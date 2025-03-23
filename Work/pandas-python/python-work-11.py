# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 21:10:31 2024

@author: hqm
"""
import pandas as pd
import numpy as np
import xarray as xr
import os
from osgeo import osr
from osgeo import gdal
path = r"D:\use\Downloads\Pandas__Python\python_work\11 nc-tif\pet_2001.nc"
out_path = r"D:\厚德学习\Pandas__Python\python_work\11 nc-tif\tif\etp_xarray"
ds = xr.open_dataset(path)
time = ds['time'].values
# f = pd.DataFrame(time)
etp= np.asarray(ds.etp)
etp_arr = etp*0.1
lonmin,lonmax,latmin,latmax = [ds.lon.min(),ds.lon.max(),ds.lat.min(),ds.lat.max()]
l_lon = len(ds.lon)
l_lat = len(ds.lat)
lon_ce = (lonmax - lonmin)/(l_lon - 1)
lat_ce = (latmax - latmin)/(l_lat - 1)
for i in range(1,13):
    out_file = out_path + os.sep + 'etp_2001_' + str(i) + '_01.tif'
    driver = gdal.GetDriverByName('GTiff')
    arr = etp_arr[i-1, :, :]
    out_tif = driver.Create(out_file, l_lon, l_lat, 1, gdal.GDT_Float32)
    geotransform = (lonmin, lon_ce, 0, latmin, 0, lat_ce)
    out_tif.SetGeoTransform(geotransform)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    out_tif.SetProjection(srs.ExportToWkt())
    # arr[arr[:, :] < 0] = np.nan
    out_tif.GetRasterBand(1).WriteArray(arr)
    #out_tif.GetRasterBand(1).SetNoDataValue(-32768)
    out_tif.FlushCache()
    del out_tif
print("转tif成功")
