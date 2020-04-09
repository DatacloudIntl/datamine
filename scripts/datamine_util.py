#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 11:40:17 2020

@author: kkappler

        There are a maximum of 68 data fields on page 1 (56Bytes per field),
        after 224 byte preamble.  THere are 32 empty bytes hanging out after the
        68th field before you get to the last 32 bytes of header page
        which are security information, no longer used

        Need to know:
            1. NUmber of pages in header
            2. NUmber of fields per header page

        The method to read the "non-field metadata" is basically a parser on the first
        224 bytes.
        The field metadata are obtained on page 1 by skipping 224 bytes, and then
        reading chunks of 56.
        the metadata on pages 2 and beyond are obtained by skipping to the page, and
        reading 56-byte chunks

"""

from __future__ import absolute_import, division, print_function

import copy
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb
import struct

#from binary_helpers import merge_binary_strings
#from binary_helpers import skip_bytes
from binary_helpers import read_int_from_8byte_float
from binary_helpers import read_staggered_string
from header_fields import field_reader_ep
from helper_functions import fix_non_unique_field_names

class DatamineFile(object):
    def __init__(self, dm_file_path=None, precision=None):
        """
        self.n_last_record: Number of last logical data record within the last page
        Some bookkeeping it is pointless to code:
            EP has 224bytes before fields begin, and last 32 are not used, thus
            256 bytes unavailable for data_fields on page 1.
            (4096bytes_per_page-256used)/56perfield = 68.57
            So Max Fields on Page 1 of EP is 68
            Max Fields on any subsequent page is (4096-32)/56 = 72.57
            So Max Fields on Page > 2 of EP is 72

        """
        self.dm_file_path = dm_file_path
        self.data_dict = None

        #<Header>
        self.embedded_filename = None #H
        self.dbname = None #H
        self.description = None #H
        self.date = None #H
        self.number_of_fields = None #H
        self.n_last_page = None #H
        self.n_last_record = None #H
        self.data_fields = None #
        #</Header>

        #<Derived>
        self.precision = precision
        self._bytes_per_page = None
        self._usable_bytes_per_page = None
        self._static_bytes_page_1 = None
        self._num_pages_header = None
        self._num_pages_data = None
        self._num_data_records = None
        self._num_fields_per_page = None
        self._constant_fields = None
        self._tabular_fields = None
        self._merged_tabular_fields = None
        self._num_rows_per_data_page = None
        self._bytes_per_word = None
        self.words_per_column = None #list to handle multi-word fields
        #</Derived>

    def determine_precision(self):
        """
        this can be done programatically by reading the description
        as SP and as EP.  If the EP description contains binary, then
        it is SP
        The logic has not been tested since we do not have SP files yet
        """
        if self.precision is None:
            f=open(self.dm_file_path, 'rb')
            f.seek(32)
            qq = f.read(160)#text field with description, will contain binary in SP case
            f.close()
            try:
                qq.decode('UTF-8')
                self.precision = 'extended'
            except UnicodeDecodeError:
                self.precision = 'single'
        if self.precision=='single':
            self._bytes_per_page = 2048
            self._usable_bytes_per_page = 2032
            self._bytes_per_header_field = 28
            self._static_bytes_page_1 = 112
            self._bytes_per_word = 4
            print('warning, single precison reader NEVER TESTED\
                  as there were no example files.  It likely wont work!')
        elif self.precision=='extended':
            self._bytes_per_page = 4096
            self._usable_bytes_per_page = 4064
            self._bytes_per_header_field = 56
            self._static_bytes_page_1 = 224
            self._bytes_per_word = 8
        return

    @property
    def num_pages_header(self):
        """
        pretty sure this is dependant only on self.n_fields
        The number more pages you need is ceiling of n_fields/72
        68 is a baked in property of page 1, it has max 68 fields
        """
        if self._num_pages_header is None:
            num_pages_header = 1
            n_fields_past_page_1 = self.number_of_fields - 68
            if n_fields_past_page_1 > 0:
                n_extra_pages = np.ceil(n_fields_past_page_1/72.0)
                num_pages_header += n_extra_pages
            self._num_pages_header = int(num_pages_header)
        return self._num_pages_header

    @property
    def num_fields_per_page(self):
        """
        returns a list of number of fields on each page of header
        e.g. [68, 7]
        68 and 72 are baked in numbers of the format.
        68 fields max on page 1, and 72 on every header page thereafter
        """
        if self._num_fields_per_page is None:
            fields_per_page = []
            if self.num_pages_header==1:
                fields_per_page.append(self.number_of_fields)
            else:
                fields_per_page.append(68)
            n_fields_remain = self.number_of_fields - 68
            while n_fields_remain > 72:
                fields_per_page.append(72)
                n_fields_remain -= 72
            if n_fields_remain > 0:
                fields_per_page.append(n_fields_remain)
            self._num_fields_per_page = fields_per_page
        return self._num_fields_per_page

    @property
    def bytes_per_page(self):
        return self._bytes_per_page

    @property
    def usable_bytes_per_page(self):
        return self._usable_bytes_per_page

    @property
    def static_bytes_page_1(self):
        return self._static_bytes_page_1

    @property
    def constant_fields(self):
        if self._constant_fields is None:
            constant_fields = [x for x in self.data_fields if x.stored_word==0]
            self._constant_fields = constant_fields
        return self._constant_fields

    @property
    def tabular_fields(self):
        if self._tabular_fields is None:
            tabular_fields = [x for x in self.data_fields if x.stored_word!=0]
            self._tabular_fields = tabular_fields
        return self._tabular_fields

    @property
    def merged_tabular_fields(self):
        return self._merged_tabular_fields

    @property
    def bytes_per_word(self):
        return self._bytes_per_word

    @property
    def num_rows_per_data_page(self):
        if self._num_rows_per_data_page is None:
            num_fields_per_row = len(self.tabular_fields)
            bytes_per_row = num_fields_per_row * self.bytes_per_word
            rows_per_page = 1.0 * self.usable_bytes_per_page / bytes_per_row
            self._num_rows_per_data_page = int(rows_per_page)
        return self._num_rows_per_data_page

    @property
    def num_pages_data(self):
        if self._num_pages_data is None:
            total_pages = self.n_last_page
            n_pages_data = total_pages - self.num_pages_header
            self._num_pages_data = n_pages_data
        return self._num_pages_data

    @property
    def num_data_records(self):
        if self._num_data_records is None:
            num_full_data_pages = self.num_pages_data - 1
            total_rows = num_full_data_pages * self.num_rows_per_data_page + self.n_last_record
            self._num_data_records = total_rows
        return self._num_data_records

    def read_fields_from_page(self, ff, page_number):
        """
        print("Read fields may need modification for single precision")
        """
        num_fields = self.num_fields_per_page[page_number]
        output = num_fields * [None]
        for i in range(num_fields):#68+1
            #pdb.set_trace()
            field = field_reader_ep(ff)
            output[i] = field
        return output

    def read_header(self, verbose=True):
        if verbose:
            print("Reading {}".format(self.dm_file_path))
        self.determine_precision()
        if self.precision=='extended':
            self.read_extended_precison_header(verbose=verbose)
        elif self.precision=='single':
            print("No single precision header reader exists yet")
            raise Exception

    def read_ep_header_sans_fields(self, verbose=True):
        """
        fname: 1-4, x, 9-12, x
        dbname:17-20, x, 25-28, x
        desc: 33-36, x, ...

        """
        dm_file = self.dm_file_path
        f = open(dm_file, 'rb')
        fname = read_staggered_string(f, 16, 4, keep_first=True)
        dbname = read_staggered_string(f, 16, 4, keep_first=True)
        description = read_staggered_string(f, 160, 4, keep_first=True)
        date = read_int_from_8byte_float(f)
        n_fields = read_int_from_8byte_float(f)
        n_last_page = read_int_from_8byte_float(f)
        n_last_record = read_int_from_8byte_float(f)
        f.close()

        self.embedded_filename = fname
        self.dbname = dbname
        self.description = description
        self.date = date
        self.number_of_fields = int(n_fields)
        self.n_last_page = int(n_last_page)
        self.n_last_record = int(n_last_record)

        if verbose:
            print('1. fname={}'.format(fname))
            print('2. dbname={}'.format(dbname))
            print('3. description={}'.format(description))
            print("4. date={}".format(date))
            print('5. nfields={}'.format(n_fields))
            print('6. nlast page={}'.format(n_last_page))
            print('7. nlast record={}\n'.format(n_last_record))
            print("header has {} pages\n".format(self.num_pages_header))
        return

    def check_for_foolishness(self):
        """
        a place to put some debugging notes and issues
        """
        #NON UNIQUE FIELDS
        field_names = [x.name for x in self.data_fields]
        if len(field_names) != len(set(field_names)):
            print("NON UNIQUE FIELDS DETECTED")
        return

    def merge_tabular_fields(self):
        """
        have observed repeated field names, with incrementing word_number
        Making the assumption that these only occur in string or "A" type fields
        and that they are sequentially stored in the row
        This method generates a _merged_tabular_fields, which is tabular
        fields with duplicates removed, and max_word attribute increased
        proportionally.
        """
        tabular_field_names = [x.name for x in self.tabular_fields]
        tmp_dict = {}
        tmp_dict['field_names'] = tabular_field_names
        df = pd.DataFrame(data=tmp_dict)
        value_counts = df['field_names'].value_counts()
        for field in self.tabular_fields:
            field.max_words = value_counts[field.name]
        #drop multiple occurences by comparing name with the name before it?
        merged_tabular_fields = [self.tabular_fields[0],]
        for i in range(len(self.tabular_fields)-1):
            if self.tabular_fields[i+1].name != self.tabular_fields[i].name:
                merged_tabular_fields.append(self.tabular_fields[i+1])
        self._merged_tabular_fields = merged_tabular_fields
        self.words_per_column = [x.max_words for x in merged_tabular_fields]
        return

    def read_extended_precison_header(self, verbose=True):
        """
        """
        self.read_ep_header_sans_fields(verbose=verbose)
        fields = []
        for i_page in range(self.num_pages_header):
            if i_page==0:
                n_skip_bytes = self.static_bytes_page_1#224
            else:
                n_skip_bytes = i_page * self.bytes_per_page
            f = open(self.dm_file_path, 'rb')
            f.read(n_skip_bytes)
            new_fields = self.read_fields_from_page(f, i_page)
            fields += new_fields
            f.close()
        self.data_fields = fields
        self.constant_fields #init
        self.tabular_fields #init
        self.check_for_foolishness()
        self.merge_tabular_fields()
        if verbose:
            print("CONSTANT FIELDS")
            if len(self.constant_fields)==0:
                print('None')
            for field in self.constant_fields:
                out_text = '{} : {}'.format(field.name, field.default_value)
                print(out_text)
            print('\n')
            print("TABULAR FIELDS")
            for field in self.tabular_fields:
                out_text = '{} : {}'.format(field.name, field.default_value)
                print(out_text)
        return

    def cast_fields_to_df(self, field_type=None):
        """
        supports writing of constant, variable (tabular), or all (default)
        """
        if field_type is None:
            fields = self.data_fields
        elif field_type == 'constant':
            fields = self.constant_fields
        elif field_type == 'tabular':
            fields = self.tabular_fields
        elif field_type == 'merged':
            fields = self.merged_tabular_fields

        default_values = [x.default_value for x in fields]
        field_names = [x.name for x in fields]
        stored_words = [x.stored_word for x in fields]
        word_numbers = [x.word_number for x in fields]
        types = [x.type for x in fields]

        data_dict = {}
        data_dict['default_value'] = default_values
        data_dict['field_name'] = field_names
        data_dict['stored_word'] = stored_words
        data_dict['word_number'] = word_numbers
        data_dict['type'] = types
        df = pd.DataFrame(data=data_dict)
        return df

    def cast_data_to_df(self):
        df = pd.DataFrame(data=self.data_dict)
        return df

    def initialize_data_dict_for_readin(self, n_rows):
        """
        """
#        print("modify this to use compressed tabular fields")
        data_dict = {}
        for field in self.merged_tabular_fields:
            if field.type =='N':
                data_dict[field.name] = np.full(n_rows, np.nan)
            elif field.type =='A':
                n_bytes = self.bytes_per_word * field.max_words
                data_dict[field.name] = np.chararray(n_rows,
                         itemsize=n_bytes, unicode=True)
            else:
                print("UNEXPECTED DTYPE ENCOUNTERED {}".format(field.type))
                pdb.set_trace()
        return data_dict

    def data_page_to_dict(self, page_num, n_rows):
        """
        This was originally done with all numeric values, using a numpy array
        We could use structured arrays, but for now will use individual arrays
        keyed by columns name

        ToDo: parameterize 483, 8, 7x69, 232
        This is admittedly slow.  It can be sped up if needed but the idea
        is that we will only read dm files once and save to another format
        """
        #pdb.set_trace()
        n_cols = len(self.merged_tabular_fields)
        data_dict = self.initialize_data_dict_for_readin(n_rows)
        types = [x.type for x in self.merged_tabular_fields]
        names = [x.name for x in self.merged_tabular_fields]
        f = open(self.dm_file_path, 'rb')
        f.seek(page_num * self.bytes_per_page)
        for i_row in range(n_rows):
            for i_col in range(n_cols):
                name = names[i_col]
                if types[i_col] == 'N':#numerical
                    qq = f.read(self.bytes_per_word)
                    value = struct.unpack('<d',qq)[0]
                    data_dict[name][i_row] = value
                else: #alpha
                    #print("NEED A BYTESPERCOLUMN")
                    n_bytes = self.bytes_per_word * self.words_per_column[i_col]
                    #print(n_bytes, name)
                    qq = f.read(n_bytes)
                    value = qq.decode('utf-8')
                data_dict[name][i_row] = value
        f.close()
        return data_dict

    def read_file(self, num_pages=None, verbose=True):
        """
        """
        #<read header if not already done>
        #this could be cleaner with a self._header_read_complete attr
        if self.data_fields is None:
            self.read_header(verbose=True)
        else:
            pass
        #</read header if not already done>

        n_rows_big = self.num_data_records
        book_dict = self.initialize_data_dict_for_readin(n_rows_big)
        last_page = False
        if num_pages is None:
            num_pages = self.num_pages_data
        for i_page in range(num_pages):
            if np.mod(i_page, 100)==0:
                print('reading page {} of {}'.format(i_page, num_pages))
            page_num = i_page + self.num_pages_header
            n_rows = self.num_rows_per_data_page
            if page_num == self.n_last_page - 1:
                last_page=True
                n_rows = self.n_last_record
            page_dict = self.data_page_to_dict(page_num, n_rows)
    #        print(i_page, page_num, datamine_file.n_last_page,i_page*n_rows,(i_page+1)*n_rows)
            if last_page:
                assign_page_to_book(page_dict, book_dict, i_page, n_rows, last_page=True)
            else:
                assign_page_to_book(page_dict, book_dict, i_page, n_rows)
        self.data_dict = book_dict
        return

    @property
    def default_output_header_filename(self):
        filename = self.dm_file_path.replace('.dm', '_header.csv')
        return filename

    @property
    def default_output_data_filename(self):
        filename = self.dm_file_path.replace('.dm', '_data.csv')
        return filename

    def save_header(self, filename=None):
        if filename is None:
            filename = self.default_output_header_filename
        df = self.cast_fields_to_df()
        print("Saving header info to: {}".format(filename))
        df.to_csv(filename)

    def save_data(self, filename=None, data_format='csv'):
        if filename is None:
            filename = self.default_output_data_filename
        df = self.cast_data_to_df()
        print(data_format, filename)
        if data_format=='csv':
            print("Saving data info to: {}".format(filename))
            df.to_csv(filename)
        elif data_format=='h5':
            filename = filename.replace('.csv', '.h5')
            print("Saving data info to: {}".format(filename))
            df.to_hdf(filename, key='df', mode='w')
        #elif filetype=='npy':
        #    pdb.set_trace()
        #    print('ss')

def read_header(dm_file, file_type='extended_precision'):
    """
    warning: this only works for EP files, need a SP reader as well

    """
    datamine_file = DatamineFile()
    datamine_file.dm_file_path = dm_file
    datamine_file.determine_precision()
    datamine_file.read_header()
    return datamine_file

def assign_page_to_book(page, book, i_page, n_rows, last_page=False):
    """
    I find it interesting that I do not need to return book.  The change is
    made on the input book, but the book outside this function is modified
    ... it feels fortranic.
    """
    if last_page:
        for k in page.keys():
            book[k][-n_rows:] = page[k]
    else:
        for k in page.keys():
            book[k][i_page*n_rows:(i_page+1)*n_rows] = page[k]
    return


def read_dm_file(dm_file, num_pages=None):
    """
    """
    datamine_file = DatamineFile()
    datamine_file.dm_file_path = dm_file
    datamine_file.read_header()
    n_rows_big = datamine_file.num_data_records
    book_dict = datamine_file.initialize_data_dict_for_readin(n_rows_big)
    last_page = False
    if num_pages is None:
        num_pages = datamine_file.num_pages_data
    for i_page in range(num_pages):
        if np.mod(i_page, 100)==0:
            print('reading page {} of {}'.format(i_page, num_pages))
        page_num = i_page + datamine_file.num_pages_header
        n_rows = datamine_file.num_rows_per_data_page
        if page_num == datamine_file.n_last_page - 1:
            last_page=True
            n_rows = datamine_file.n_last_record
        page_dict = datamine_file.data_page_to_dict(page_num, n_rows)
#        print(i_page, page_num, datamine_file.n_last_page,i_page*n_rows,(i_page+1)*n_rows)
        if last_page:
            assign_page_to_book(page_dict, book_dict, i_page, n_rows, last_page=True)
        else:
            assign_page_to_book(page_dict, book_dict, i_page, n_rows)
    datamine_file.data_dict = book_dict
    return datamine_file


def main():
    """
    """
    print("finito {}".format(datetime.datetime.now()))

if __name__ == "__main__":
    main()

