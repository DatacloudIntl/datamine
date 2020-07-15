Files uploaded 20200408 (kk):
borcddmod150220_data_csv.zip: A zipped version of the data dump from the parent file borcddmod150220.dm

borcddmod150220_data_h5.zip: a zipped version of the same data table in pandas dataframe h5 dump for rapid load

borcddmod150220_header.csv: ascii dump of the header fields information

Ians_dataframe_csv.zip: this is a "snap to first closest" version of the 
dm file dump, where the master grid described by XMORIG, YMORIG, ZMORIG,
NX, NY, NZ, XINC, YINC, ZINC default values from the header of the dm file
are used to make a grid, and then for each grid cell the "first closest"
observation within that cell from the dm is associated.
This file should be almost identical to the one from geoscience analyst.
Exceptions include some rounding off w.r.t. sig figs performed by analyst
And some ignoring of small values by analyst:
e.g. 
The CRECAU column in Manu's dataframe seems to disregard all values of 0.01, the most common value.  Presumably this is below some threshold of interest.  The unique values in the dm file are (with rounding):
[ 0.01 ,  0.1, 50.5, 48. , 56.4, 51.3, 43.1] ... 
but in  Manu's file they are 
[ 0.0 ,  0.1, 50.5, 48. , 56.4, 51.3, 43.1]
So his software is treating 0.01 as 0.0.  Thats fine, as far as a gold percentage it may as well be zero, just an observation.

