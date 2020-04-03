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


import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb
import struct

from binary_helpers import determine_number_of_pages_in_header
from binary_helpers import determine_if_file_sp_or_ep
from binary_helpers import merge_binary_strings
#from binary_helpers import skip_bytes
from binary_helpers import read_int_from_8byte_float
from binary_helpers import read_staggered_string
from header_fields import field_reader_ep

class DatamineHeader(object):
    def __init__(self):
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
        self.dm_file_path = None
        self.precision = None
        self.n_pages_header = None
        self.embedded_filename = None #H
        self.dbname = None #H
        self.description = None #H
        self.date = None #H
        self.number_of_fields = None #H
        self.n_last_page = None #H
        self.n_last_record = None #H
        self.data_fields = None #
        self.fields = None

    def determine_precision(self):
        print("insert logic to determine if EP or SP file here based on self.dm_filename")
        self.precision = 'extended'
        if self.precision=='single':
            print('warning, single precison reader DNE')
            raise Exception
        else:
            print("reading Extended precision header")
        return

    def count_header_pages(self):
        """
        pretty sure this is dependant only on self.n_fields
        """
        num_header_pages = 1
        n_fields_past_page_1 = self.number_of_fields - 68
        if n_fields_past_page_1 > 0:
        #the number more pages you need is ceiling of n_fields/72
            n_extra_pages = np.ceil(n_fields_past_page_1/72.0)
            num_header_pages += n_extra_pages
        self.n_pages_header = int(num_header_pages)
        return

    def get_number_of_fields_per_page(self):
        """
        returns a list of number of fields on each page of header
        e.g. [68, 7]
        """
        fields_per_page = []
        if self.n_pages_header==1:
            fields_per_page.append(self.number_of_fields)
        else:
            fields_per_page.append(68)
        n_fields_remain = self.number_of_fields - 68
        while n_fields_remain > 72:
            fields_per_page.append(72)
            n_fields_remain -= 72
        if n_fields_remain > 0:
            fields_per_page.append(n_fields_remain)
        self.number_of_fields_per_page = fields_per_page
        return fields_per_page

    @property
    def bytes_per_page(self):
        if self.precision=='extended':
            return 4096
        elif self.precision=='single':
            return 2048
        else:
            print('precsion unkown')
            raise Exception

    @property
    def bytes_per_field(self):
        if self.precision=='single':
            return 28
        elif self.precision=='extended':
            return 56
        #12+16+160+4+8+8+8+8+68*56
    @property
    def static_bytes_page_1(self):
        if self.precision=='single':
            return 112
        elif self.precision=='extended':
            return 224

    def n_skip_bytes_to_read_fields(self, page_number):
        if page_number==0:
            return self.static_bytes_page_1
        else:
            return 0

    def read_fields_from_page(self, ff, page_number):
        num_fields = self.number_of_fields_per_page[page_number]
        print("read fields may need modification for single precision")
        output = num_fields * [None]
        for i in range(num_fields):#68+1
            field = field_reader_ep(ff)
            output[i] = field
        return output

    def read(self):
        if self.precision=='extended':
            self.read_extended_precison()

    def read_ep_header_sans_fields(self):
        """
        fname: 1-4, x, 9-12, x
        dbname:17-20, x, 25-28, x
        desc: 33-36, x, ...

        """
        dm_file = self.dm_file_path
        f = open(dm_file, 'rb')
        fname = read_staggered_string(f, 16, 4, keep_first=True)
        print('1. fname={} ok'.format(fname))
        dbname = read_staggered_string(f, 16, 4, keep_first=True)
        print('2. dbname={} ok'.format(dbname))
        description = read_staggered_string(f, 160, 4, keep_first=True)
        print('3. description={} ok'.format(description))
        date = read_int_from_8byte_float(f)
        print("4. date {}".format(date))
        n_fields = read_int_from_8byte_float(f)
        print('5. nfields {}'.format(n_fields));
        n_last_page = read_int_from_8byte_float(f)
        print('6. nlast page {}'.format(n_last_page))
        n_last_record = read_int_from_8byte_float(f)
        print('7. nlast record {}'.format(n_last_record));
        f.close()
        self.embedded_filename = fname
        self.number_of_fields = int(n_fields)
        self.n_last_page = int(n_last_page)
        self.n_last_record = int(n_last_record)
        return

    def read_extended_precison(self):
        """
        """
        self.read_ep_header_sans_fields()
        self.count_header_pages()
        self.get_number_of_fields_per_page()
        print("header has {} pages".format(self.n_pages_header))

        fields = []
        for i_page in range(self.n_pages_header):
            if i_page==0:
                n_skip_bytes = self.static_bytes_page_1
            else:
                n_skip_bytes = i_page * self.bytes_per_page
            f = open(self.dm_file_path, 'rb')
            f.read(n_skip_bytes)
            new_fields = self.read_fields_from_page(f, i_page)
            fields += new_fields
            f.close()
        self.data_fields = fields
        return

    def cast_fields_to_df(self):
        default_values = [x.default_value for x in self.data_fields]
        field_names = [x.name for x in self.data_fields]
        stored_words = [x.stored_word for x in self.data_fields]
        word_numbers = [x.word_number for x in self.data_fields]
        types = [x.type for x in self.data_fields]

        data_dict = {}
        data_dict['default_values'] = default_values
        data_dict['field_name'] = field_names
        data_dict['stored_word'] = stored_words
        data_dict['word_number'] = word_numbers
        data_dict['type'] = types
        df = pd.DataFrame(data=data_dict)
        return df

def read_header(dm_file, file_type='extended_precision'):
    """
    warning: this only works for EP files, need a SP reader as well

    """
    header = DatamineHeader()
    header.dm_file_path = dm_file
    header.determine_precision()
    header.read()
    return header





def main():
    """
    """
    read_header()
    print("finito {}".format(datetime.datetime.now()))

if __name__ == "__main__":
    main()

