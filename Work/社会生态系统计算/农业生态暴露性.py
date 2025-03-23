# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 15:44:26 2025

@author: hqm
"""
import rasterio,os
import pandas as pd
import numpy as np
from glob import glob as glb
def read_raster(file_path):
    with rasterio.open(file_path) as src:
        data = src.read(1).astype('float32')  # 读取第一波段
        nodata = src.nodata
        data[data == nodata] = np.nan
        profile = src.profile
        return data
def out_raster(out, data):
    with rasterio.open(r"F:\论文写作\欣雨学姐\计算\归一化\2000\cnpp_Qt_2000.tif") as okk:
        cnpp_data = okk.read(1)  # 读取第一波段
        nodata = okk.nodata
        cnpp_data[cnpp_data == nodata] = np.nan
        meta = okk.meta
    meta.update(dtype='float32', count=1, nodata=np.nan)

    with rasterio.open(out, 'w', **meta) as dest:
            dest.write(data, 1)    
for year in range(2000,2021,5):
    EVI_path = rf"F:\论文写作\欣雨学姐\计算\EVI\EVI{year}.tif"
    ny_path = rf"F:\论文写作\欣雨学姐\计算\生态系统计算\农业产值占比\out\农业产值占比{year}.tif"
    out = rf"F:\论文写作\欣雨学姐\计算\归一化\社会\农业生态敏感\农业生态敏感{year}.tif"
    EVI = read_raster(EVI_path)
    ny = read_raster(ny_path)
    far_sen = EVI * ny
    X_min = np.nanmin(far_sen)  
    X_max = np.nanmax(far_sen)  
    #positive_normalized_data = (far_sen - X_min) / (X_max - X_min)  # 正向标准化
    negative_normalized_data = (X_max - far_sen) / (X_max - X_min)  # 负向标准化
    out_raster(out, negative_normalized_data )
    