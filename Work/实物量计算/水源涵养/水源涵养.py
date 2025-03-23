# -*- coding: utf-8 -*-
"""
Created on Wed May 17 20:51:43 2023

@author: wly
"""


import os
from funcs import read, out

dir_pre = r"F:\论文写作\欣雨学姐\计算\实物量计算\水源涵养\数据\降水\out"
dir_r = r"F:\论文写作\欣雨学姐\计算\实物量计算\水源涵养\计算\径流"
dir_pet = r"F:\论文写作\欣雨学姐\计算\实物量计算\水源涵养\数据\实际蒸散"

qwr_dir = r"F:\论文写作\欣雨学姐\计算\实物量计算\水源涵养\计算\水源涵养"


for i in range(2000,2021,5):
    path_pre = dir_pre + os.sep + f'SUM_{i}.tif'
    path_r = dir_r + os.sep + f'径流{i}.tif'
    path_eva = dir_pet + os.sep + f'实际蒸散{i}.tif'
    
    qwr_path = qwr_dir + os.sep + f'水源涵养{i}.tif'
    
    
    df_pre, pro, shape = read(path_pre,3)
    df_r = read(path_r)
    df_eva = read(path_eva)


    df = (df_pre - df_eva - df_r)*10  # 乘10转换为立方米每公顷
    df[df<0] = 0
    
    out(qwr_path, df, pro)
    print(i)


















# qwr_path = r'D:\水源涵养\水源涵养\qwr.tif'


































































