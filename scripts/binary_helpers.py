#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 11:43:20 2020

@author: kkappler
"""

from __future__ import absolute_import, division, print_function


import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb

#BYTES_PER_PAGE = 4096
def skip_pages(n, ff, bytes_per_page=4096):
    for i in range(n):
        ff.read(bytes_per_page)


def skip_bytes(f, n_bytes):
    f.read(n_bytes)
    return f

def merge_binary_strings(in_bytes):
    qq = [x.decode('utf-8') for x in in_bytes]
    qq = [x for x in qq if x!=' ']
    qq = ''.join(qq)
    return qq


def determine_if_file_sp_or_ep(dm_file):
    print("insert logic to determine if EP or SP file here")
    file_type = 'extended_precision'
    if file_type=='single_precision':
        print('warning, single precison reader DNE')
    else:
        print("reading Extended precision header")
    return file_type


def determine_number_of_pages_in_header(dm_file):
    print("warning, we dont have a method for counting pages in header vs rest of file")
    print("insert method here for doing this")
    return 2

def determine_number_of_records_per_page(df_file):
    """
    we are given the number of records on the last page, but
    I see no guarantee that the last page is complete.  So we should
    read the last page, and the one before it and make sure they
    both have the same number of records before assuming the
    number of records on the last page is true for all
    """
    print("read last page and second last page and compare # records")
    return 7



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

