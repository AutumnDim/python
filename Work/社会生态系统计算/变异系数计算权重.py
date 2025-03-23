# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 15:15:37 2025

@author: hqm
"""
import ahpy 
import numpy as np 
import rasterio 
import os
import pandas as pd
from glob import glob as glb
for year in range(2000,2021,5):
    
    path = rf"F:\论文写作\欣雨学姐\计算\归一化\社会\{year}"
    
    fist = glb(path + os.sep + "**.tif")
    kist = []
    SEVI = 0
    for i in fist :
        #out = os.path.join(out_path, os.path.basename(i))
        with rasterio.open(i) as src: #读取
            profile = src.profile
            data = src.read(1).astype(float)
            nodata = src.nodata # 数据无效值
            data[data==nodata]= np.nan
            data1 = data[~np.isnan(data)]
            # 计算变异系数
            mean_values = np.mean(data1, axis=0)
            std_devs = np.std(data1, axis=0)
            coeff_variation = (std_devs / mean_values) 
            name = os.path.basename(i)
            df = pd.DataFrame(coeff_variation.flatten(), columns=[name])
            kist.append(df)
            final_data = pd.concat(kist, axis=1)
            # 计算客观权重
    weights_objective = final_data / np.sum(final_data, axis=1).values[0]
    #result_df = pd.DataFrame({ 'Weight':  weights_objective}, index=final_data.columns)
    #evi = data * result_df.loc[name, 'Weight']
    #SEVI+=evi
    #out = rf"F:\论文写作\欣雨学姐\计算\SEVI\SEVI{year}.tif"
    #out_raster(out, EVI)
    
    
    out_path = r"F:\论文写作\欣雨学姐\计算\权重\社会"
    out = os.path.join(out_path, f"{year}.xlsx")
    weights_objective.T.to_excel(out , sheet_name=str(year), index=True)
    # out_excel = r"F:\论文写作\欣雨学姐\计算\权重\社会\权重.xlsx"
    # if not os.path.exists(out_excel):
    #     with pd.ExcelWriter(out_excel, engine='openpyxl') as writer:
    #         weights_objective.to_excel(writer, sheet_name=str(year), index=True)
    # else:
    #     # 文件已存在，用 'a' 模式追加写入
    #     with pd.ExcelWriter(out_excel, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
    #         weights_objective.to_excel(writer, sheet_name=str(year), index=True)
