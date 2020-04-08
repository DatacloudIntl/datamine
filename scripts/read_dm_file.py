# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 12:45:25 2020

@author: kkappler

Command line interface for Datamine (.dm) file reader.

First version supports only header dump to terminal, and csv dump to file.

1. Dump header to screen
2. Dump to csv

ToDo Lower priority if there is time:
3. Low priority items, netcdf, h5, xarray

"""

from __future__ import absolute_import, division, print_function

import argparse
import datetime
import pdb

from binary_helpers import str2bool
from datamine_util import DatamineFile

def read_header(dm_file_path):
    datamine_file_object = DatamineFile(dm_file_path=dm_file_path)
    datamine_file_object.read_header()
    return datamine_file_object

def read_data(dm_file_path):
    """
    Note: Header is read automatically (necesarily) before data read.
    """
    datamine_file_object = DatamineFile(dm_file_path=dm_file_path)#read_dm_file(dm_file)#, num_pages=2)
    datamine_file_object.read_file()
#    datamine_file_object.save_header()
#    datamine_file_object.save_data()
    return datamine_file_object


def my_function():
    """
    """
    pass

def main(args):
    """
    Example usages:
        python dm_read.py -if='cpybopt.dm'

    If you want to send the header fields to a csv file:
        python dm_read.py -if='cpybopt.dm' --save_header=True
        will save the header to cpybopt_header.csv
        python dm_read.py -if='cpybopt.dm' --header_filename=foo.csv
        will save the header to foo.csv

    Does not currently provide a method for dumping data to terminal.  Instead
    write data csv and then inspect csv file.

    """
    save_header = args.save_header
    header_filename = args.header_filename
    save_data = args.save_data
    out_file_path = args.output_file
    verbose = str2bool(args.verbose)
    dm_file_path = args.input_file

    #<Allow save_header/data to be implied by a passed output filename>
    if header_filename is not None:
        save_header = True

    if args.output_file is not None:
        save_data = True
    #</Allow save_header/data to be implied by a passed output filename>

    #<Sanity Check>
    print("Reading file {}".format(dm_file_path))
    if dm_file_path[-3:] != '.dm':
        print("warning: Input File {} does not have a .dm extension".format(dm_file_path))
    #</Sanity Check>

    dm_obj = DatamineFile(dm_file_path)

    #<Set output filenames to default or given values>
    if save_header:
        if header_filename is None:
            header_filename = dm_obj.default_output_header_filename
            print("No Output Header File Specified, Writing to {}".format(header_filename))
    if save_data:
        if out_file_path is None:
            out_file_path = dm_obj.default_output_data_filename
            print("No Output Data File Specified, Writing to {}".format(out_file_path))
    #</Set output filenames to default or given values>

    #clunky but works
    if verbose:
        dm_obj.read_header(verbose=True)
    else:
        dm_obj.read_header(verbose=False)

    if save_header:
        dm_obj.save_header(filename=header_filename)

    if save_data:
        dm_obj.read_file(verbose=False)
        dm_obj.save_data(filename=out_file_path)
    print("finito {}".format(datetime.datetime.now()))


if __name__ == "__main__":
    example_text = """example:

        To print dmfile header to terminal:
            python read_dm_file.py cpybopt.dm

        To save header to default csv file:
            python dm_read.py cpybopt.dm --save_header=True
                saves header to cpybopt_header.csv
            python dm_read.py cpybopt.dm --header_file=foo.csv
                saves header to foo.csv

        To save data to default csv file:
            python dm_read.py cpybopt.dm --save_data=True
                saves header to cpybopt_data.csv
            python dm_read.py cpybopt.dm --output_file=foo.csv
                or
            python dm_read.py cpybopt.dm -of=foo.csv
                will save the data to foo.csv

        by specifying an output data_file header_file the save_data, save_header
        arguments are interpretted as True
        """
    description_string = "DM (Datamine) file interface -  Copyright (c) 2020 DataCloud"
    argparser = argparse.ArgumentParser(description=description_string,
                                        epilog=example_text,
                                        formatter_class=argparse.RawDescriptionHelpFormatter)

    argparser.add_argument('input_file', help="path to the dm file")

    argparser.add_argument('-v', '--verbose', help="print header info to terminal", default=True)
    argparser.add_argument('-of', '--output_file', help="path to the output csv file",
                           default=None)
    argparser.add_argument('--save_header', help="save header fields as a csv", default=True)
    argparser.add_argument('--header_filename', help="filename for header data", default=None)
    argparser.add_argument('--save_data', help="save tabular data as a csv", default=False)

    args = argparser.parse_args()

    main(args)
