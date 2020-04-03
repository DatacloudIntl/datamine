#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 14:53:13 2020

@author: kkappler
This needs to be modified in general to handle short and long format dm files,
or so called SP and EP formats.
"""

from __future__ import absolute_import, division, print_function


import pdb
import struct

from binary_helpers import read_staggered_string

class DatamineDataField(object):
    """
    container for a header element representing a column of data in dm file
    """
    def __init__(self):
        self.name = None
        self.type = None
        self.stored_word = None
        self.word_number = None
        self.default_value = None




def field_reader_ep(ff):
    """
    reads the 56 byte info about a data field, parses, and stores as an
    object of class
    20200402: made change to tipo (type) reader, was choking on binary noise in file,
    need only pull N or A from first 4 bytes, so no need to read as 8
    """
    field_name = read_staggered_string(ff, 16, 4, keep_first=True)

    tipo = read_staggered_string(ff, 4, 4, keep_first=True)
    ff.read(4)
    stored_word = ff.read(8);
    stored_word = struct.unpack('<d',stored_word)[0]
    #print('stored_word', stored_word)

    word_number = ff.read(8);#skip
    word_number = struct.unpack('<d',word_number)[0]
    #print('word_number ', word_number)

    ff.read(8);#skip

    #<default_value>
    default_value = ff.read(8);
    default_value = struct.unpack('<d',default_value)[0]
    #print('default_value', default_value)
    #</default_value>

    field = DatamineDataField()
    field.name = field_name
    field.stored_word = stored_word
    field.default_value = default_value
    field.type = tipo
    field.word_number = word_number
    if word_number != 1:
        print("WARNING! Weve never seen a word number not == 1")

    return field

