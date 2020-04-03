#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 14:53:13 2020

@author: ianpatterson and kkappler
This needs to be modified in general to handle short and long format dm files,
or so called SP and EP formats.
ToDo:
"""

from __future__ import absolute_import, division, print_function


#import datetime
#import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb
import struct
#import chardet
#from collections import defaultdict
from binary_helpers import determine_number_of_pages_in_header
from binary_helpers import skip_pages
from header import read_header

#can get this programatically now;
HEADER_FIELDS_NOT_IN_TABLE = ['XMORIG', 'YMORIG', 'ZMORIG', 'NX', 'NY', 'NZ']




def page_to_array(ff):
    """
    ToDo: parameterize 483, 8, 7x69, 232
    """
    arrayed_page = np.full(483,np.nan)
    for i in np.arange(483):
        qq = ff.read(8)
        numerical = struct.unpack('<d',qq)[0]
        arrayed_page[i] = numerical
    arrayed_page = arrayed_page.reshape(7,69)
    ff.read(232)
    #print(arrayed_page)
    return arrayed_page

def combine_pages(n_pages, n_fields, records_per_page, ff, n_skip=0):
    """
    232361 pages total
    7: this is the number of records per page.  It is listed
    as the number of records on the last page in the web documentation.
    In our example this was true for all data pages, but we need to check it
    n_fields: this is the number of data fields per record, it was 69 in the example file
    """
    print("warning -  total number of records needs validataion")
    total_number_of_records = records_per_page*n_pages
    output_shape = (total_number_of_records, n_fields)
    print("warning -  total number of records needs validataion")
    big_array = np.full(output_shape, np.nan)
    skip_pages(n_skip, ff)
    for i in np.arange(n_pages - n_skip):
        if np.mod(i,100) == 0:
            print(i)
        output = page_to_array(ff)
        #output should be a 7x69 numpy array
        big_array[i*records_per_page:(i+1)*records_per_page,:] = output
    return big_array



def read_data_book_from_dm_file(header, dm_file):
    n_header_pages = determine_number_of_pages_in_header(dm_file)
    n_pages_data = header.n_last_page - n_header_pages
    records_per_page = print(header.n_last_record)
    pdb.set_trace()
    #n_data_pages= 232361
    f = open(dm_file, 'rb')
    skip_pages(n_header_pages, f)
    records_per_page = 7
    n_fields = header.number_of_fields
    book = combine_pages(n_data_pages, n_fields, records_per_page, f)
    #book = combine_pages(23, f) #Small version for testing
    f.close()
    return book

def cast_book_to_dataframe(book, header):
    field_names = [x.name for x in header.data_fields]
    #real_field_names = field_names[0:17] + field_names[23:75]
    real_field_names = [x for x in field_names if x not in HEADER_FIELDS_NOT_IN_TABLE]

    data_dict = {}
    for i in range(69):
        key = real_field_names[i]
        value = book[:,i]
        data_dict[key] = value

    ###Possibly check for default values to avoid scanning in to csv###
    df = pd.DataFrame.from_dict(data_dict)
    return df

def create_df_from_npy_array_book(dm_file):
    """
    read dm_file (from original dm or stashed npy array)
    """
    #<READ DM AND DUMP TO NPY>
    header = read_header(dm_file)
    df = header.cast_fields_to_df()
    pdb.set_trace()

    try:
        book = np.load(dm_npy_file)
        raise(Exception)
    except:
        book = read_data_book_from_dm_file(header, dm_file)
        np.save(dm_npy_file, book)
    #</READ DM AND DUMP TO NPY>
    df = cast_book_to_dataframe(book, header)
    return df

