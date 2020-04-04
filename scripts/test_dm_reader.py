#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 10:55:25 2020

@author: kkappler

"""

from __future__ import absolute_import, division, print_function


import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb

from datamine_util import read_header
from datamine_util import read_dm_file
from datamine_util import DatamineFile

SAVE_CSV = False
MASS_TEST = True

#<SET PATHS>
home = os.path.expanduser("~/")
mine_dir = os.path.join(home, '.cache/datacloud/first_quantum_minerals/cobre_panama')
data_dir = os.path.join(mine_dir, 'Model')
dm_base = 'borcddmod150220.dm'
#data_dir = os.path.join(mine_dir, 'Wireframes')
#dm_base = 'PYTR.dm'
#dm_base = 'ANDpt.dm'
#dm_base = 'ANDtr.dm'
dm_file = os.path.join(data_dir, dm_base)
##datamine_file_object = read_header(dm_file)
datamine_file_object = read_dm_file(dm_file)#, num_pages=2)
df = datamine_file_object.cast_fields_to_df()
df.to_csv(dm_base.replace('_header.dm', '.csv'))
df = datamine_file_object.cast_data_to_df()
df = datamine_file_object.cast_fields_to_df()
df.to_csv(dm_base.replace('_data.dm', '.csv'))


def mass_test():
    """
    """
    #if MASS_TEST:
    data_dir = os.path.join(mine_dir, 'Wireframes')
    #dm_file = os.path.join(data_dir, 'ANDpt.dm')
    dm_files = os.listdir(data_dir)
    for dm_base in dm_files:
        dm_file = os.path.join(data_dir, dm_base)
        datamine_file_object = DatamineFile(dm_file_path=dm_file)
        #datamine_file_object.read_header()
        datamine_file_object = read_dm_file(dm_file)#, num_pages=2)
        df = datamine_file_object.cast_data_to_df()
        df.describe()
#        pdb.set_trace()
        print('\n\n\n\n\n')
#        #pdb.set_trace()
#        header = read_header(dm_file)
#        df = header.cast_fields_to_df()
#        df.to_csv(dm_base.replace('.dm', '.csv'))
    #pdb.set_trace()
    return

def main():
    """
    """
    mass_test()
    print("finito {}".format(datetime.datetime.now()))

if __name__ == "__main__":
    main()
