# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 11:21:02 2024

@author: hqm
"""
import pandas as pd 
import numpy as np
import os,time
from netCDF4 import Dataset
from glob import glob as glb
from osgeo import osr
from netCDF4 import date2num ,num2date, Dataset
import netCDF4 as nc
from osgeo import gdal
path = r"D:\use\Downloads\Pandas__Python\python_work\11 nc-tif\pet_2001.nc"
out_path = r"D:\厚德学习\Pandas__Python\python_work\11 nc-tif\tif\etp_net"
data = nc.Dataset(path)
nc_info = data.variables
etp = data.variables['etp']
lon = data.variables['lon'][:]
lat = data.variables['lat'][:]
time = data.variables['time']
etp_arr = np.asarray(data.variables['etp'])
etp_arr = etp_arr * 0.1
lonmin, lonmax,latmin, latmax = [lon.min(),lon.max(),lat.min(),lat.max()]
l_lat = len(lat)
l_lon = len(lon)
lon_ce = (lonmax - lonmin)/(l_lon-1)
lat_ce = (latmax - latmin)/(l_lat-1)
for i in range(0,12):
    out_file = out_path + os.sep + 'etp_2001_' + str(i) + '_01.tif'
    driver = gdal.GetDriverByName('GTiff')
    arr = etp_arr[i, :, :]
    out_tif = driver.Create(out_file, l_lon, l_lat, 1, gdal.GDT_Float32)
    geotransform = (lonmin, lon_ce, 0, latmin, 0, lat_ce)
    out_tif.SetGeoTransform(geotransform)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    out_tif.SetProjection(srs.ExportToWkt())
    arr[arr[:, :] < 0] = np.nan
    out_tif.GetRasterBand(1).WriteArray(arr)
    #out_tif.GetRasterBand(1).SetNoDataValue(-32768)
    out_tif.FlushCache()
    del out_tif
print("转tif成功")