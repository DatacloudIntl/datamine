#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 11:55:31 2020

@author: ianpatterson
Example of converting a dm file dump to a block model file
assume you have created h5 files by running:
python read_dm_file.py borcddmod150220.dm --save_data=True --data_format=h5
"""

from __future__ import absolute_import, division, print_function


import datetime
#import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb
import itertools


print('Starting at:', datetime.datetime.now())
data_df = pd.read_hdf('borcddmod150220_data.h5')
header_df = pd.read_csv('borcddmod150220_header.csv')
NX = int(header_df[header_df.field_name=='NX'].iloc[0].default_value)
NY = int(header_df[header_df.field_name=='NY'].iloc[0].default_value)
NZ = int(header_df[header_df.field_name=='NZ'].iloc[0].default_value)
XMORIG = header_df[header_df.field_name=='XMORIG'].iloc[0].default_value
YMORIG = header_df[header_df.field_name=='YMORIG'].iloc[0].default_value
ZMORIG = header_df[header_df.field_name=='ZMORIG'].iloc[0].default_value
XINC = header_df[header_df.field_name=='XINC'].iloc[0].default_value
YINC = header_df[header_df.field_name=='YINC'].iloc[0].default_value
ZINC = header_df[header_df.field_name=='ZINC'].iloc[0].default_value


gridsteps = np.array([x for x in itertools.product(np.arange(NX),
                                              np.arange(NY), np.arange(NZ))])
#gridsteps = np.array([x for x in itertools.product(np.arange(200),
#                                              np.arange(92), np.arange(43))])
print('Finished loading the csv at:', datetime.datetime.now())
"""Making the grid"""
print("the NX, NY, NZ values are taken from the header")
#pdb.set_trace()
xyz_increments = np.array([XINC, YINC, ZINC])
#xyz_increments = np.array([60, 60, 30])
origin = np.array([XMORIG, YMORIG, ZMORIG]) + xyz_increments/2.0
#origin = np.array([(530735+30), (973690+30), (-795+15)])
#pdb.set_trace()
grid = origin + gridsteps * xyz_increments
griddf = pd.DataFrame(data=grid, columns = ['X_UTMZ4N_m', 'Y_UTMZ4N_m', 'Z_m'])
griddf['IJK'] = np.arange(len(griddf))


"""Merging the grid onto the dataframe"""
df = data_df.merge(griddf)
df['DIST'] = ((df.XC - df.X_UTMZ4N_m)**2 + (df.YC - df.Y_UTMZ4N_m)**2 +
  (df.ZC - df.Z_m)**2) **0.5

"""Sorting"""
"""THIS IS NOT HOW THE PROPRIATARY SOFTWARE DOES THE SORTING!!!"""

"""I've spent some time trying to figure it out, but I'm a bit stumped.
It doesn't seem to just take the first closest DIST value and it also doesn't
have some other simple pattern. I've been looking at some of the 256s to see
some pattern but no luck for me. Perhaps you'll have some insight."""

#@note: re Ians comment above, it was because he was sorting wit XC, YC, ZC,
#after commenting out in below line all is right
df = df.sort_values(['IJK', 'DIST'])#, 'XC', 'YC', 'ZC'])
df = df.drop_duplicates(['IJK'], keep = 'first')

"""Merging back on to the grid"""
df = griddf.merge(df, on = ['IJK', 'X_UTMZ4N_m','Y_UTMZ4N_m', 'Z_m'],
                  how = 'left')

"""Finish making this look like the propriatary software's csv"""
df = df.sort_values(['Y_UTMZ4N_m', 'X_UTMZ4N_m', 'Z_m'])
df['ID'] = np.arange(len(griddf))
print(df.shape)
print(df.head)
df.to_csv('Ians_dataframe.csv') #Feel free to rename this!
print('You are done!', datetime.datetime.now())
