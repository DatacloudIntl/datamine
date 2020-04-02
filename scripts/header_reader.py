#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 11:40:17 2020

@author: kkappler
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
from binary_helpers import skip_bytes
from header_fields import field_reader

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
        self.dm_filename = None
        self.precision = None
        self.n_pages_header = None
        self.embedded_filename = None
        self.dbname = None
        self.description = None
        self.date = None
        self.number_of_fields = None
        self.n_last_page = None
        self.n_last_record = None
        self.data_fields = None

    def determine_if_file_sp_or_ep(self):
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
        self.n_pages_header = num_header_pages
        return num_header_pages


    @property
    def bytes_per_field(self):
        if self.precision=='single':
            return 28
        elif self.precision=='extended':
            return 56
        #12+16+160+4+8+8+8+8+68*56

def divide_chunks(string, n):
    # looping till length l
    for i in range(0, len(string), n):
        yield string[i:i + n]

def drop_staggered(string_list, keep_first=True):
    if keep_first:
        output = string_list[0::2]
    else:
        output = string_list[1::2]
    return output

def read_staggered_string(f, n_read, n_chunk, keep_first=True):
    """
    """
    string = f.read(n_read)
    string = string.decode('utf-8')
    chunk_generator = divide_chunks(string, 4)
    chunked_string = list(chunk_generator)
    if keep_first:
        keepers = chunked_string[0::2]
    else:
        keepers = chunked_string[1::2]
    merged_string = ''.join(keepers)
    return merged_string


def read_header(dm_file, file_type='extended_precision'):
    """
    ::ToDo:: fname is not being correctly parsed
    warning: this only works for EP files, need a SP reader as well

    """
    header = DatamineHeader()
    header.dm_filename = dm_file
    header.determine_if_file_sp_or_ep()
    if header.precision == 'extended':
        header = read_header_ep(dm_file)
    else:
        print('warning, single precison reader DNE')
        raise Exception
    return header

def read_int_from_8byte_float(f):
    qq = f.read(8);
    output = struct.unpack('<d',qq)[0]
    output = int(output)
    return output

def read_ep_header_sans_fields(dm_file):
    """
    fname: 1-4, x, 9-12, x
    dbname:17-20, x, 25-28, x
    desc: 33-36

    """
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
    header = DatamineHeader()
    header.embedded_filename = fname
    header.number_of_fields = int(n_fields)
    header.n_last_page = int(n_last_page)
    header.n_last_record = int(n_last_record)
    return header

def read_header_ep(dm_file):
    """
    12 (4, skip4, 4): for filename
    Several things we would need to know,
    we iterate over 69 fields, but 75 are given.  We know that six of these
    are not part of the table, but we figured that out by dumping data and
    looking at its repititions, not by interogating the header
    need to deduce NUM_DATA_FIELDS from the file

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
    NUM_HEADER_PAGES = 2
    NUM_DATA_FIELDS = [68, 7]
    header = read_ep_header_sans_fields(dm_file)
    header.count_header_pages()
    print('d')
    print(header.count_header_pages)
    pdb.set_trace()
    f = open(dm_file, 'rb')
    f = skip_bytes(f, 224)
    #12+16+160+4+8+8+8+8+68*56
    #=224 + 68*56
    #<FIELD READER>
    fields = []
    for i in range(1,69):#68+1
        print(i)
        field = field_reader(f)
        fields.append(field)
        print('\n')#end i',i)
    print(i, i*56)
    qq = f.read(32)
    qq = f.read(32)
    for i in range(1,8):#7+1
        print(i)
        field = field_reader(f)
        fields.append(field)
        print('\n')#end i',i)
#    field_names = [x.name for x in fields]
#    sw = [x.stored_word for x in fields]
#    wn = [x.word_number for x in fields]
#    types = [x.type for x in fields]
    f.close()
    header.data_fields = fields
    return header
    pass

def my_function():
    """
    """
    pass

def main():
    """
    """
    my_function()
    print("finito {}".format(datetime.datetime.now()))

if __name__ == "__main__":
    main()

