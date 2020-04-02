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
        if self.precision=='single':
            print('no support for SP')
            raise Exception
        elif self.precision=='extended':
            print('ok')

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
#    """
#    """
#    pass
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

def read_ep_header_sans_fields(dm_file):
    """
    """
    f = open(dm_file, 'rb')
#    tmp = f.read(12)
#    tmp = divide_chunks(tmp, 4)
#    tmp=list(tmp)
#    ''.join(tmp)
#    pdb.set_trace()
    name_1 = f.read(4);#name1
    name_1 = struct.unpack('cccc',name_1)
    name_1 = merge_binary_strings(name_1)
    f = skip_bytes(f, 4)
    name_2 = f.read(4);#name2
    name_2 = struct.unpack('cccc',name_2)
    name_2 = merge_binary_strings(name_2)
    fname = '{}{}'.format(name_1, name_2)
    #</embedded filename>

    #<embedded database name>
    print('dbname no longer in use, skipping')
    qq = f.read(16);print('2. dbname');print(qq);print('\n')
    #</embedded database name>

    #<description>
    description = f.read(160);print('3. description');
    #can pull out ever
    print(description);print('\n');

    #</description>

    qq = f.read(4);#skip
    qq = f.read(8);print('4. date');print(qq);
    date = struct.unpack('<d',qq)[0]
    print(date)
    print('\n');

    n_fields = f.read(8);
    n_fields = struct.unpack('<d',n_fields)[0]
    print('5. nfields {}'.format(n_fields));

    qq = f.read(8);
    n_last_page = struct.unpack('<d',qq)[0]
    print('6. nlast page {}\n'.format(n_last_page))

    qq = f.read(8);
    n_last_record = struct.unpack('<d',qq)[0]
    print('7. nlast record {}\n'.format(n_last_record));
    f.close()
    #12+16+160+4+8+8+8+8+68*56
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

