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
import struct
#BYTES_PER_PAGE = 4096

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
    merged_string = merged_string.strip()
    return merged_string

def read_int_from_8byte_float(f):
    qq = f.read(8);
    output = struct.unpack('<d',qq)[0]
    output = int(output)
    return output

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

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


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

