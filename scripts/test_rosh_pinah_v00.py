# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 11:47:58 2020

@author: kkappler

Test of usage of dm code on rosh pinah block model:

    Block model file uploaded by Manu to sharepoint, link here
    https://datacloudinternational.sharepoint.com/:f:/r/sites/ClientProjects/Shared%20Documents/Trevali-RoshPinah/1_OriginalClientData/16_Models?csf=1&web=1&e=JId45W

    I placed the blockmodel locally at ~/.cache/datacloud/trevali/rosh_pinah/rp_bm_final_wf3.dm')

    The blockmodel x,y,z, values are in a recentered coordinate system.
    The origin of the data in the DM file is <0, 0, 0>, but in the
    mine-coordinate system it is <X0 : 22074.0, Y0 : 659553.0, Z0 : -525.0>
    Which are <Easting, Northing, Elevation>

    The rotation is described as:
    ANGLE1 : 55.0
    ANGLE2 : 0.0
    ANGLE3 : 0.0
    ROTAXIS1 : 3.0
    ROTAXIS2 : 0.0
    ROTAXIS3 : 0.0
    I take this to be a single rotation about the z-axis of 55 degrees.

    Thus to "right it" we would rotate by -55 degrees.

    from scipy.spatial.transform import Rotation as R


class SimpleRotationXYZ(object):
    def __init__(self, axis, angle, degrees=True):
        self.axis = axis
        self.angle=angle
        self.degrees = degrees
        self.matrix = None
        self._calc_rotation_matrix()

    def _calc_rotation_matrix(self):
        r_x = R.from_euler(self.axis, self.angle, degrees=self.degrees)
        R_x = r_x.as_dcm()
        self.matrix = R_x

    def apply_rotation(self, vector):
        rotated_vector = self.matrix.dot(vector)
        return rotated_vector
"""

from __future__ import absolute_import, division, print_function


import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb

from scipy.spatial.transform import Rotation
from dc_mwd.mine_data_cache_paths import MineDataCachePaths
from dc_mwd.logging_util import init_logging

from datamine_util import DatamineFile

logger = init_logging(__name__)
HOME = os.path.expanduser("~/")
#MINE_DATA_CACHE_PATH = MineDataCachePaths('trevali', 'rosh_pinah')
data_folder = os.path.join(HOME, '.cache', 'datacloud', 'trevali', 'rosh_pinah')
dm_file_path = os.path.join(data_folder, 'rp_bm_final_wf3.dm')
#datamine_file_object = DatamineFile(dm_file_path=dm_file_path)
#datamine_file_object.read_file()#num_pages=5
#datamine_file_object.save_header()
#datamine_file_object.save_data(data_format='hdf')

def my_function():
    """
    """
    datamine_file_object = DatamineFile(dm_file_path=dm_file_path)
    #pdb.set_trace()
#    datamine_file_object.read_file(num_pages=100, pages_per_message=1000)#num_pages=5
    datamine_file_object.read_file(pages_per_message=1000)
    r_x = Rotation.from_euler('z', -55, degrees=True).as_dcm()
    datamine_file_object.save_header()
    datamine_file_object.save_data(data_format='csv')
    datamine_file_object.rotate_coordinates(r_x)
    #pdb.set_trace()
#    datamine_file_object.save_data(data_format='h5')
    datamine_file_object.save_data(filename='rotated.csv', data_format='csv')
    pdb.set_trace()
    pass

def main():
    """
    """
    my_function()
    print("finito {}".format(datetime.datetime.now()))

if __name__ == "__main__":
    main()
