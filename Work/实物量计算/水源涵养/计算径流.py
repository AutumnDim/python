# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 17:36:00 2025

@author: hqm
"""
# import rasterio
import numpy as np
import os
import pandas as pd
from funcs import read, out, three_sigma



# 获取类型对应径流系数字典
dic = {}

path_code = r"F:\论文写作\欣雨学姐\计算\实物量计算\水源涵养\数据\类型对应径流因子.xlsx" # 表格
df_code = pd.read_excel(path_code)
for i in range(len(df_code)):
    dic[df_code['code'][i]] = df_code['系数'][i]

for y in range(2000,2021,5):
    y = str(y)
    # code转系数（coef）
    path_land = rf"F:\论文写作\欣雨学姐\计算\实物量计算\水源涵养\数据\土地利用\土地利用{y}.tif"  # 土地利用
    df_land = read(path_land)
    df_coef = df_land.copy()
    for i in df_land[0].unique():
        if i in dic:
            df_coef[df_land == i] = dic[i]
        
        elif np.isnan(i):
            df_coef[df_land.isna()] = np.nan
        else:
            df_coef[df_land == i] = np.nan
    
    
    
    # 计算R及输出
    dir_pre =  rf"F:\论文写作\欣雨学姐\计算\实物量计算\水源涵养\数据\降水\out\SUM_{y}.tif"
    R_dir = r"F:\论文写作\欣雨学姐\计算\实物量计算\水源涵养\计算\径流"
    R_path = os.path.join(R_dir, f'径流{y}.tif')
    df_pre,pro,shape = read(dir_pre,3)
    df_pre = three_sigma(df_pre)
    df = df_pre*df_coef
    out(R_path, df, pro)
    
    # if i == 2001:
    #     df_all = df
    # else:
    #     df_all = pd.concat([df_all,df],axis=1)
    
    
    
# print (i)
    

# '''
# 平均径流
# '''



# dfx = df_all.agg(np.nanmean,axis=1)





# R_path = r'D:/水源涵养/平均/径流_deal2.tif'
# ap.out(R_path,dfx,pro)
    