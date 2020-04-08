#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 10:55:25 2020

@author: kkappler

ToDo: add ability to save as npy, npy structured array (when dtypes are mixed),
use netcdf for xarray type dumps.

Add CLI using argparse package.

"""

from __future__ import absolute_import, division, print_function


import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb

#from datamine_util import read_header
from datamine_util import read_dm_file
from datamine_util import DatamineFile

HOME = os.path.expanduser("~/")
mine_dir = os.path.join(HOME, '.cache/datacloud/first_quantum_minerals/cobre_panama')
SAVE_CSV = False
MASS_TEST = True
TEST = 'block_model'
#TEST = 'PYTR'
def set_paths():

#<SET PATHS>
    if TEST == 'block_model':
        data_dir = os.path.join(mine_dir, 'Model')
        dm_base = 'borcddmod150220.dm'
        dm_file = os.path.join(data_dir, dm_base)
        return dm_file
    elif TEST == 'PYTR':
        data_dir = os.path.join(mine_dir, 'Wireframes')
        dm_base = 'PYTR.dm'
    else:
        pass
    #dm_base = 'ANDpt.dm'
    #dm_base = 'ANDtr.dm'
    dm_file = os.path.join(data_dir, dm_base)
    return dm_file

def read_header(dm_file_path):
    datamine_file_object = DatamineFile(dm_file_path=dm_file_path)
    datamine_file_object.read_header()

def test_file_io(dm_file_path):
    datamine_file_object = DatamineFile(dm_file_path=dm_file_path)#read_dm_file(dm_file)#, num_pages=2)
    datamine_file_object.read_file()
    datamine_file_object.save_header()
    datamine_file_object.save_data()

#dm_file_path = set_paths()
#test_file_io(dm_file_path)

def mass_test():
    """
    """
    #if MASS_TEST:
    data_dir = os.path.join(mine_dir, 'Wireframes')
    #dm_file = os.path.join(data_dir, 'ANDpt.dm')
    dm_files = os.listdir(data_dir)
    for dm_base in dm_files:
        dm_file_path = os.path.join(data_dir, dm_base)
        test_file_io(dm_file_path)
    return

#def create_df_from_npy_array_book(dm_file):
#    """
#    read dm_file (from original dm or stashed npy array)
#    """
#    #<READ DM AND DUMP TO NPY>
#    header = read_header(dm_file)
#    df = header.cast_fields_to_df()
#    pdb.set_trace()
#
#    try:
#        book = np.load(dm_npy_file)
#        raise(Exception)
#    except:
#        book = read_data_book_from_dm_file(header, dm_file)
#        np.save(dm_npy_file, book)
#    #</READ DM AND DUMP TO NPY>
#    df = cast_book_to_dataframe(book, header)
#    return df

def main():
    """
    """
    mass_test()
    print("finito {}".format(datetime.datetime.now()))

if __name__ == "__main__":
    main()

