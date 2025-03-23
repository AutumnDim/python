# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 15:25:31 2025

@author: hqm
"""
import numpy as np
import pandas as pd
import rasterio,os
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

        
# 熵值
def calculate_entropy(df_normalized):
    m = df_normalized.shape[0]
    k = 1 / np.log(11)  # 常数 k
    H_j = []
    for column in df_normalized.columns:
        f_ij = df_normalized[column]  # 获取第 j 个指标
        H_j_value = -k * np.sum(f_ij * np.log(f_ij + 1e-10))  
        H_j.append(H_j_value)
    
    return np.array(H_j)

# 权重
def calculate_weights(H_j):
    H_j_sum = np.sum(1 - H_j)  
    w_j = (1 - H_j) / H_j_sum  # 计算权重
    return w_j
years = [2000,2005,2010,2015,2020]
for year in years: 
    path = rf"F:\论文写作\欣雨学姐\计算\归一化\{year}"
    if not os.path.exists(rf"F:\论文写作\欣雨学姐\计算\权重\{year}"):
        os.makedirs(rf"F:\论文写作\欣雨学姐\计算\权重\{year}")
    else:
        pass
    kist = []
    fist = glb(path + '*/*.tif')
    EVI = np.zeros_like(read_raster(fist[0]))
    for i in fist:
        name = os.path.basename(i)
        data = read_raster(i)
        df = pd.DataFrame(data.flatten(), columns=[name])
        kist.append(df)
        final_data = pd.concat(kist, axis=1)
        H_j = calculate_entropy(final_data)
        w_j = calculate_weights(H_j)
        result_df = pd.DataFrame({ 'Weight':  w_j}, index=final_data.columns)
        mask = ~np.isnan(data)
        evi = data * result_df.loc[name, 'Weight']
        EVI[mask] += evi[mask]
        out = rf"F:\论文写作\欣雨学姐\计算\EVI\EVI{year}.tif"
        out_raster(out, EVI)
        # out_excel = rf"F:\论文写作\欣雨学姐\计算\权重\权重.xlsx"
        # if not os.path.exists(out_excel):
        
        #     with pd.ExcelWriter(out_excel, engine='openpyxl') as writer:
        #         result_df.to_excel(writer, sheet_name=str(year), index=True)
        # else:
        #     # 文件已存在，用 'a' 模式追加写入
        #     with pd.ExcelWriter(out_excel, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
        #         result_df.to_excel(writer, sheet_name=str(year), index=True)
            
        
        
        
        
        
        
        
        
    # final_data = pd.concat(kist, axis=1)
    # F = final_data/final_data.sum(axis=0)
    # F_S = F.sum(axis=0)
    # K = 1 / np.log(10)
    # H =-K * F_S * (np.log(F + 1e-10))
    # W = (1-H)/np.sum(1-H)
    # for w in W.columns:
    #     out = os.path.join(rf"F:\论文写作\欣雨学姐\计算\权重\{year}",w )
    #     W_data = W[w].values.reshape((data.shape[0], data.shape[1]))
    #     out_raster(out, W_data)

    
        
        
        
    
