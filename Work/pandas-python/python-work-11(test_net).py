# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 22:07:27 2024

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
path = r"C:\Users\hqm\Documents\WeChat Files\wxid_235yshiz2ylm22\FileStorage\File\2024-07\test_vr6.nc"
out_path = r"D:\厚德学习\Pandas__Python\python_work\11 nc-tif\tif\test_net"
data = nc.Dataset(path)
nc_info = data.variables
ws = data.variables['ws']
lon = data.variables['lon'][:]
lat = data.variables['lat'][:]
time = data.variables['time']
ws_arr = np.asarray(data.variables['ws'])
lonmin, lonmax,latmin, latmax = [lon.min(),lon.max(),lat.min(),lat.max()]
l_lat = len(lat)
l_lon = len(lon)
lon_ce = (lonmax - lonmin)/(l_lon-1)
lat_ce = (latmax - latmin)/(l_lat-1)
# 创建tif文件
out_file = out_path + os.sep + 'ws.tif'
driver = gdal.GetDriverByName('GTiff')
arr = ws_arr[0, :, :]
out_tif = driver.Create(out_file, l_lon, l_lat, 1, gdal.GDT_Float32)
geotransform = (lonmin, lon_ce, 0, latmin, 0, lat_ce)
out_tif.SetGeoTransform(geotransform)
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)
out_tif.SetProjection(srs.ExportToWkt())
arr[arr[:, :] < 0] = 999999
out_tif.GetRasterBand(1).WriteArray(arr)
#out_tif.GetRasterBand(1).SetNoDataValue(999999)
out_tif.FlushCache()
del out_tif
print("转tif成功")
