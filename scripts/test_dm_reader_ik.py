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
from helper_functions import dm_csv
from helper_functions import manu_csv

SAVE_CSV = False


df = create_df_from_npy_array_book()

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

