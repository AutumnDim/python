# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 16:04:00 2025

@author: hqm
"""
import pandas as pd
import numpy as np
import rasterio,os
from glob import glob as glb
path = r"F:\论文写作\欣雨学姐\数据\水源涵养\数据\实际蒸散\out"
out = r"F:\论文写作\欣雨学姐\数据\水源涵养\数据\实际蒸散\fin"
fist = glb(path + os.sep + '*.tif')
for i in fist :
    out_path = out + os.sep + os.path.basename(i)
    with rasterio.open(i) as src:
        band1 = src.read(1)
        band2= src.read(2)
        band3= src.read(3)
        nodata = src.nodata
        band1[band1 == nodata] = np.nan
        band2[band2 == nodata] = np.nan
        band3[band3 == nodata] = np.nan
        sum_data = band1 + band2 + band3
    meta = src.meta
    meta.update(dtype='float32', count=1, nodata=np.nan)
    with rasterio.open(out_path, 'w', **meta) as dest:
            dest.write(sum_data, 1)         
