# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 22:28:37 2025

@author: hqm
"""
import pandas as pd
import glob
import rasterio
import numpy as np
import os
# import mycode.arcmap as ap
from collections import Counter

#根据土地利用情况，给森林，灌丛，草地，湿地赋值
with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\固碳量\数据\土地利用\土地利用2020.tif") as lu:
    
    print("栅格文件的元数据：", lu.meta)
    lu1 = lu.read(1).astype(float)
    nodata = lu.nodata
    lu1[lu1 == nodata] = np.nan
    profile = lu.profile
    print("栅格数据的形状：", lu1.shape)
    print("栅格数据的类型：", lu1.dtype)
    print("栅格数据的值：", np.unique(lu1, return_counts=True))
    
# 检查栅格数据是否全为 0
if np.all(lu1 == 0):
    print("栅格数据全为 0")
else:
    print("栅格数据包含非 0 的值")
    
a = lu1.astype(float)

# NEP 和 NPP 的转换系数α取值如表 C.4
a[(lu1== 1) | (lu1 == 5)| (lu1 == 6)| (lu1 == 7)| (lu1 == 8)] = np.nan
a[lu1 == 2] = 0.215    #森林
a[lu1== 3] = 0.087   #灌丛
a[lu1== 4] = 0.262  #草地
a[lu1== 9] = 0.302  #湿地


# -----------------------------------------------------------------------------
# 输出a
profile.update(dtype=rasterio.float32, count=1)

a_path = r"F:\论文写作\欣雨学姐\计算\实物量计算\固碳量\计算\因子\a2.tif"
with rasterio.open(a_path, 'w', **profile) as dst:
    dst.write(a.astype(rasterio.float32), 1)

# 验证输出文件是否正确写入
with rasterio.open(a_path) as src:
    data = src.read(1)
    print("输出栅格数据的唯一值：", np.unique(data, return_counts=True))
#------------------------------------------------------------------------------

#最后，计算陆地生态系统Qtco2（净生态系统生产力法）
path = r"F:\论文写作\欣雨学姐\计算\实物量计算\固碳量\数据\NPP\CNPP\out"
# path1 = r'D:\a工作2024\zmz_那曲\碳固定\lucc\a.tif'
output_dir = r"F:\论文写作\欣雨学姐\计算\实物量计算\固碳量\计算\固碳"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

npps = glob.glob(path+os.sep+'*.tif')
for year in range(2000,2021,5):
    npp_files = [f for f in npps if str(year) in os.path.basename(f)]
   
    if not npp_files:
        print(f"未找到 {year} 年的NPP文件")
        continue
   
    # 确保只找到一个文件
    if len(npp_files) > 1:
        print(f"找到多个 {year} 年的NPP文件： {npp_files}")
        continue
   
    npp_file = npp_files[0]
    with rasterio.open(npp_file) as npp_profile:
            npp = npp_profile.read(1) 
            nodata = npp_profile.nodata
            npp[npp == nodata] = np.nan
            profile = npp_profile.profile
            # no_data_value = npp_profile.nodata
    
            # # 将无效值替换为 NaN
            # if no_data_value is not None:
            #     npp = np.where(npp == no_data_value, np.nan, npp)
            
    # with rasterio.open(path1) as a_profile:
            # a = a_profile.read(1)  
            
    Qt =  a* (44/12)*npp*(72/162)

    # 将NaN替换为no_data_value
    # if no_data_value is not None:
        # Qt = np.where(np.isnan(Qt), no_data_value, Qt)

    # profile.update(dtype=rasterio.float32, count=1, nodata=no_data_value)

    # 输出栅格文件的路径
    output_path = os.path.join(output_dir, f'cnpp_Qt_{year}.tif')

    # 写入新的栅格数据
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(Qt.astype(rasterio.float32), 1)
        
    print(f"{year} 年的NPP文件处理完成，结果已保存至 {output_path}")

# def top_three_frequent_numbers(arr):
     
#       arr1 = arr[~np.isnan(arr)]
#       # 将numpy数组中的每个元素转换为元组
#       arr_tuples = [tuple(item) if isinstance(item, np.ndarray) else item for item in arr1]
#       # 统计每个数出现的次数
#       count = Counter(arr_tuples)
#       # 找出出现次数最多的三个数
#       top_three = count.most_common(5)
#       # 返回结果
#       return [num for num, freq in top_three]               
# result = top_three_frequent_numbers(a)
# print(result)            
  