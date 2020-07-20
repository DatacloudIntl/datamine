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
#from dc_mwd.mine_data_cache_paths import MineDataCachePaths
#from dc_mwd.logging_util import init_logging

from datamine_util import DatamineFile

#logger = init_logging(__name__)
HOME = os.path.expanduser("~/")
#MINE_DATA_CACHE_PATH = MineDataCachePaths('trevali', 'rosh_pinah')
data_folder = os.path.join(HOME, '.cache', 'datacloud', 'trevali', 'rosh_pinah')
dm_file_path = os.path.join(data_folder, 'rp_bm_final_wf3.dm')
h5_file_path = os.path.join(data_folder, 'rp_bm_final_wf3_data.h5')

def greet_the_datamine_file():
    """
    read file,
    save a copy
    rotate csys and save rotated,

    ..:ToDo: add offset correction to Mine Csys <X0, Y0, Z0>

    #note to Ian: Added datamine_file_object._data_df
    """
    #<TO BE MADE INPUT VARS>
    num_pages = None
    SAVE_ORIGINAL_TO_CSV = False
    SAVE_ORIGINAL_TO_H5 = False
    SAVE_5X5X5_TO_CSV = True
    #</TO BE MADE INPUT VARS>
    datamine_file_object = DatamineFile(dm_file_path=dm_file_path)
    X0 = 22074.0
    Y0 = 659553.0
    Z0 = -525.0
    ANGLE1 = 55.0
    ROTAXIS1 = 3; rot_axis = 'xyz'[ROTAXIS1-1]
    r_x = Rotation.from_euler(rot_axis, -ANGLE1, degrees=True).as_dcm()
#    datamine_file_object.read_file(num_pages=100, pages_per_message=1000)#num_pages=5
    print('Reading file')
    print('For quick Test / debug run set num_pages=100')
    datamine_file_object.read_file(pages_per_message=1000, num_pages=num_pages)

    print('Saving Header')
    datamine_file_object.save_header()
    if SAVE_ORIGINAL_TO_CSV:
        print('Saving csv')
        datamine_file_object.save_data(data_format='csv')
    if SAVE_ORIGINAL_TO_H5:
        print('Saving h5')
        datamine_file_object.save_data(data_format='h5')
#    outfile = datamine_file_object.default_output_data_filename
#    outfile = outfile.replace('.csv', '_estimation_grid.csv')
#    datamine_file_object.save_data(filename=outfile, data_format='csv')



    print('Rotating coordinates')
    rotated_coords_array = datamine_file_object.rotate_coordinates(r_x, write_to_df=False)

    if SAVE_5X5X5_TO_CSV:
        df = datamine_file_object.data_df
        print('adding geographic coordinates')
        df['easting'] = rotated_coords_array[:,0] + X0
        df['northing'] = rotated_coords_array[:,1] + Y0
        df['elevation'] = rotated_coords_array[:,2] + Z0

        print('Saving 5x5x5')
        df5x5x5 = df[df.VOL==125]
        outfile = datamine_file_object.default_output_data_filename
        outfile = outfile.replace('.csv', '_with_mine_coordinates_5x5x5.csv')
        df5x5x5 .to_csv(outfile)

        plt.plot(df5x5x5.XC, df5x5x5.YC, 'rx', label='estimation_grid')
        plt.plot(df5x5x5.easting-X0, df5x5x5.northing-Y0, 'bo', label='mine coordinates')
        plt.xlim([-100, 2000])
        plt.xlabel("Translated Easting")
        plt.ylabel("Translated Northing")
        plt.plot(0,0,'g+', markersize=25, markeredgewidth=5, label='origin')
        plt.legend();plt.show()

    pdb.set_trace()
    print('done20200717')

    pass

def test_read_h5():
    from ians_helper_functions import round_xyz_increments
    from ians_helper_functions import add_blocks_column

    datamine_file_object = DatamineFile(dm_file_path=dm_file_path)
    datamine_file_object.read_header(verbose=True)
    df = pd.read_hdf(h5_file_path)
    datamine_file_object._data_df = df
    pdb.set_trace()
    df = round_xyz_increments(df)
    df = add_blocks_column(df)
    cell_size_counts = df['BLOCK'].value_counts()
    str_cell_size_counts = cell_size_counts.index.astype('str')
    tmp = str_cell_size_counts
    volumes = [ int(tmp[i][0]) * int(tmp[i][1]) * int(tmp[i][2]) for i in range(125)]
    vc_dict = {'volume':volumes, 'id':cell_size_counts.index, 'count':cell_size_counts.values}
    vc_info_df = pd.DataFrame(data=vc_dict)
    vc_info_df.to_csv('block_size_info.csv')
    pdb.set_trace()
    datamine_file_object._data_df = df
    ijk_counts = df['IJK'].value_counts()
    plt.hist(ijk_counts, 100);
    plt.xlabel('rows with common IJK');
    plt.ylabel('Number of Occurences');
    plt.title('Rosh Pinah 2020 blockmodel DM IJK value counts')
    plt.show()
    print('fast read ok')
    #datamine_file_object.save_data(filename='20200715_with_blocks.csv', data_format='csv')
    pdb.set_trace()
    datamine_file_object.save_data(filename='20200715_with_blocks.csv', data_format='csv')
    print('ok')

def main():
    """
    """
    #test_read_h5()
    greet_the_datamine_file()
    print("finito {}".format(datetime.datetime.now()))

if __name__ == "__main__":
    main()
