# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 19:54:16 2025

@author: hqm
"""
import numpy as np
import pandas as pd
import os
import rasterio
from glob import glob as glb
def read_raster(file_path):
    with rasterio.open(file_path) as src:
        data = src.read(1).astype('float32')  # 读取第一波段
        nodata = src.nodata
        data[data == nodata] = np.nan
        data[np.isinf(data)] = np.nan
        profile = src.profile
        return data
def out_raster(out, data):
    with rasterio.open(r"F:\论文写作\欣雨学姐\计算\归一化\2000\cnpp_Qt_2000.tif") as okk:
        cnpp_data = okk.read(1)
        nodata = okk.nodata
        cnpp_data[cnpp_data == nodata] = np.nan
        meta = okk.meta
    meta.update(dtype='float32', count=1, nodata=np.nan)

    with rasterio.open(out, 'w', **meta) as dest:
            dest.write(data, 1)
#权重
def cal_w(file_paths):
    kist = []  

    # 遍历每个文件路径
    for i in file_paths:
        with rasterio.open(i) as src:
            profile = src.profile
            data = src.read(1).astype(float)
            nodata = src.nodata  
            data[data == nodata] = np.nan  
            data1 = data[~np.isnan(data)]  
            # 计算变异系数
            mean_values = np.mean(data1, axis=0)
            std_devs = np.std(data1, axis=0)
            coeff_variation = std_devs / mean_values
            name = os.path.basename(i)
            df = pd.DataFrame(coeff_variation.flatten(), columns=[name])
            kist.append(df)
    final_data = pd.concat(kist, axis=1)
    # 计算客观权重
    weights_objective = final_data / np.sum(final_data, axis=1).values[0]
    return  weights_objective
for year in range(2000,2021,5):
    path = rf"F:\论文写作\欣雨学姐\计算\归一化\社会\归一化\{year}"
    fist = glb(path + os.sep + "**.tif")
    w = cal_w(fist).T
    uist = []
    SEVI = np.zeros_like(read_raster(fist[0]))
    for i in fist:
        name = os.path.basename(i)
        data = read_raster(i)
        mask = ~np.isnan(data)
        sevi = data * w.loc[name].values[0]
        SEVI[mask] += sevi[mask]
        out = rf"F:\论文写作\欣雨学姐\计算\SEVI\SEVI{year}.tif"
        out_raster(out, SEVI)

