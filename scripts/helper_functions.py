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
from datamine_util import read_header

#can get this programatically now;
HEADER_FIELDS_NOT_IN_TABLE = ['XMORIG', 'YMORIG', 'ZMORIG', 'NX', 'NY', 'NZ']


def fix_non_unique_field_names():
    pass



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

