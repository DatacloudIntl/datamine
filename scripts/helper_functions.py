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

#can get this programatically now;
HEADER_FIELDS_NOT_IN_TABLE = ['XMORIG', 'YMORIG', 'ZMORIG', 'NX', 'NY', 'NZ']


def fix_non_unique_field_names(data_fields):
    """
    add _1, _2, _3 to field names
    receiving a list of strings;
    Want to get number and position of all duplicate occurrences
    Lets use dataframe.values_count
    """
    field_names = [x.name for x in data_fields]
    tmp_dict = {}
    tmp_dict['field_names'] = field_names
    df = pd.DataFrame(data=tmp_dict)
    value_counts = df.values_count()
    offending_labels = value_counts[value_counts>1]
    if len(offending_labels)==0:
        return
    else:
        print('dammit')




    pdb.set_trace()

    pass




