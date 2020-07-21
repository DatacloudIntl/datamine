#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 11:55:31 2020

@author: kkappler
Based on some of Ian's functions;
1. Load Manu's DF
2. Load Ian's DF
3. Confirm orders are identical (x,y,z) subtracts to zero
4. Assign IJK
5. difference row-by-row
6. identify first row with a significant sum-difference
7. Dig those IJK out of ians "pre-droped" df
"""

from __future__ import absolute_import, division, print_function


import datetime
#import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb
import itertools

#from helper_functions import create_df_from_npy_array_book

SAVE_CSV = False

#dm = create_df_from_npy_array_book()
#print('Finished loading the csv at:', datetime.datetime.now())
def make_grid_with_ijk(NX, NY, NZ, XINC, YINC, ZINC, XMORIG, YMORIG, ZMORIG):
    """
    Making the master grid with cell centers in the master grid
    """
    print('making IJK master grid')
    gridsteps = np.array([x for x in itertools.product(np.arange(NX),
                                              np.arange(NY), np.arange(NZ))])
    xyz = np.array([XINC, YINC, ZINC])
    origin = np.array([(XMORIG+XINC/2.), (YMORIG+YINC/2.), (ZMORIG+ZINC/2.)])
    grid = origin + gridsteps * xyz
    grid_df = pd.DataFrame(data=grid, columns = ['xc_ijk', 'yc_ijk', 'zc_ijk'])
    #grid_df = pd.DataFrame(data=grid, columns = ['X_UTMZ4N_m', 'Y_UTMZ4N_m', 'Z_m'])
    grid_df['IJK'] = np.arange(len(grid_df))
    return grid_df

#
#"""Merging the grid onto the dataframe"""
#df = dm.merge(grid_df)
#df2 = dm.merge(grid_df, on=['IJK'])
#df['DIST'] = ((df.XC - df.X_UTMZ4N_m)**2 + (df.YC - df.Y_UTMZ4N_m)**2 +
#  (df.ZC - df.Z_m)**2) **0.5
#pdb.set_trace()
#print("how do we know that after the merge, the subdf associated with a \
#      fixed ijk retains the ordering that it did in the original dataframe?")
#print("we know that some ijk have a bunch (eg 256) rows .. are they ordered same?")
#
#"""Sorting"""
#"""THIS IS NOT HOW THE PROPRIATARY SOFTWARE DOES THE SORTING!!!"""
#
#"""I've spent some time trying to figure it out, but I'm a bit stumped.
#It doesn't seem to just take the first closest DIST value and it also doesn't
#have some other simple pattern. I've been looking at some of the 256s to see
#some pattern but no luck for me. Perhaps you'll have some insight."""
#
#df = df.sort_values(['IJK', 'DIST'])#, 'XC', 'YC', 'ZC'])
#df = df.drop_duplicates(['IJK'], keep = 'first')
#
#"""Merging back on to the grid"""
#df = grid_df.merge(df, on = ['IJK', 'X_UTMZ4N_m','Y_UTMZ4N_m', 'Z_m'],
#                  how = 'left')
#
#"""Finish making this look like the propriatary software's csv"""
#df = df.sort_values(['Y_UTMZ4N_m', 'X_UTMZ4N_m', 'Z_m'])
#df['ID'] = np.arange(len(grid_df))
#print(df.shape)
#print(df.head)
#if SAVE_CSV:
#    df.to_csv('Ians_dataframe.csv') #Feel free to rename this!
##pdb.set_trace()
#common_columns = df.columns[4:-2]
#common_columns = common_columns[0:10].append(common_columns[16:])
##pdb.set_trace()
##common_ijk = common_columns.append(['IJK'])
##pdb.set_trace()
#from helper_functions import manu_csv
#manu_df = pd.read_csv(manu_csv)
#manu_df = manu_df.sort_values(by=['X_UTMZ4N_m', 'Y_UTMZ4N_m', 'Z_m'])#, ignore_index=True)
#manu_df['IJK'] = np.arange(len(manu_df))
#manu_df.dropna(axis='rows', inplace=True)
#manu_df.to_csv('manu_106050.csv', index=False)
#pdb.set_trace()
#
#manu_df = manu_df.sort_values(by=['X_UTMZ4N_m', 'Y_UTMZ4N_m', 'Z_m'])#, ignore_index=True)
##ijk = np.arange(len(manu_df))
#manu_df['IJK'] = np.arange(len(manu_df))
#manu_df.dropna(axis='rows', inplace=True)
#ddf = df.dropna(axis='rows')
#ijk_all = manu_df.IJK.to_list()
#for ijk in ijk_all:
#    manu = manu_df[manu_df.IJK==ijk]
#    ian = ddf[ddf.IJK==ijk]
#    print(len(ian), len(manu))
#    #manu = manu[common_columns]
#    #ian = ian[common_columns]
#    pdb.set_trace()
#    print('ijk')
##qq.set_index('ijk', inplace=True)
#mdf = manu_df[common_columns]
##mdf.dropna(axis='rows', inplace=True)
#ddf = df[common_columns]
#ddf.dropna(axis='rows', inplace=True)
#pdb.set_trace()
##cols = manu_df.column
#i=0
#col = common_columns[i]
#qq=~(manu_df[cols] - df[cols]).isna()
#print(sum((manu_df[cols[i]] - df[cols[i]])[qq]))
#
#print('You are done!', datetime.datetime.now())