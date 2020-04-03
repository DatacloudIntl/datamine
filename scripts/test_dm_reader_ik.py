#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 10:55:25 2020

@author: kkappler
wc -l *dm
4042718 borcddmod150220.dm
looks like 7 records per page in the dm file



"""

from __future__ import absolute_import, division, print_function


import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb

from helper_functions import create_df_from_npy_array_book
from datamine_util import read_header
from datamine_util import read_data#(dm_file, file_type='extended_precision')
#from helper_functions import dm_csv
#from helper_functions import manu_csv

SAVE_CSV = False
MASS_TEST = False

#<SET PATHS>
home = os.path.expanduser("~/")
#mine_dir = os.path.join(home, 'Documents/ian/cobre_panama')
mine_dir = os.path.join(home, '.cache/datacloud/first_quantum_minerals/cobre_panama')
data_dir = os.path.join(mine_dir, 'Model')
dm_base = 'borcddmod150220.dm'
data_dir = os.path.join(mine_dir, 'Wireframes')
dm_base = 'ANDpt.dm'
dm_file = os.path.join(data_dir, dm_base)
#datamine_file_object = read_header(dm_file)
datamine_file = DatamineFile(dm_file_path=dm_file)
datamine_file.read_header()
datamine_file_object = read_data(dm_file, file_type='extended_precision')

df = datamine_file_object.cast_fields_to_df()
df.to_csv(dm_base.replace('.dm', '.csv'))
pdb.set_trace()
#<Testwf>
if MASS_TEST:
    data_dir = os.path.join(mine_dir, 'Wireframes')
    #dm_file = os.path.join(data_dir, 'ANDpt.dm')
    dm_files = os.listdir(data_dir)
    #pdb.set_trace()
    for dm_base in dm_files:
        dm_file = os.path.join(data_dir, dm_base)
        #pdb.set_trace()
        header = read_header(dm_file)
        df = header.cast_fields_to_df()
        df.to_csv(dm_base.replace('.dm', '.csv'))
    pdb.set_trace()

#</Testwf>


manu_dir = os.path.join(mine_dir, 'ClientBM')
dm_npy_file = os.path.join(data_dir, 'book.npy')
dm_csv = os.path.join(data_dir, 'borcddmod150220.csv')
manu_csv = os.path.join(manu_dir, 'borcddmod150220.csv')
#from dc_mwd.mine_data_cache_paths import MineDataCachePaths
#MINE_DATA_CACHE_PATH = MineDataCachePaths('first_quantum_minerals', 'cobre_panama')
#</SET PATHS>


df = create_df_from_npy_array_book(dm_file)

if SAVE_CSV:
    df.to_csv(dm_csv, index=False)

#load mans's dataframe:
pdb.set_trace()
manu_df = pd.read_csv(manu_csv)
qq = manu_df.sort_values(by=['X_UTMZ4N_m', 'Y_UTMZ4N_m', 'Z_m'])#, ignore_index=True)
ijk = np.arange(len(manu_df))
qq['ijk'] = ijk
#qq.reset_index(inplace=True)
qq.set_index('ijk', inplace=True)
print('ok, i think we are set, now lets compare some ijk...')
print('find row_ids where ijk unique in dmdf')

#print(data_frame)
#pdb.set_trace()
#qq=data_frame.ZC.unique()
#qq.sort()
#plt.plot(qq, 'b*');plt.show()
#pdb.set_trace()


print('whatsitlooklike?')

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

