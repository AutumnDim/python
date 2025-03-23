# -*- coding: utf-8 -*-
"""
Created on Sun Mar  2 15:17:53 2025

@author: hqm
"""
import rasterio,os
import pandas as pd
import numpy as np
from glob import glob as glb
path = r"F:\论文写作\欣雨学姐\计算\归一化\社会\新建文件夹\out"
out = r"F:\论文写作\欣雨学姐\计算\归一化\社会\新建文件夹\归一化"
fist = glb(path + os.sep + '**.tif')
for i in fist:
    with rasterio.open(i) as src:
        data = src.read(1).astype('float32')
        profile = src.profile
        nodata = src.nodata 
        data[data==nodata]= np.nan
        data[np.isinf(data)] = np.nan
        #data = np.isfinite(data)  # 确保数据中无效值不参与归一化计算
        X_min = np.nanmin(data)  
        X_max = np.nanmax(data)  
        positive_normalized_data = (data - X_min) / (X_max - X_min)  # 正向标准化
        negative_normalized_data = (X_max - data) / (X_max - X_min)  # 负向标准化
        profile.update(dtype=rasterio.float32)
        output = os.path.join(out, os.path.basename(i))
        with rasterio.open(output, 'w', **profile) as dst:
            dst.write(positive_normalized_data, 1)  # 写入第一波段


# #统计数据归一化
# import os
# import pandas as pd
# import numpy as np
# path = r"F:\论文写作\欣雨学姐\数据\最终数据\矢量\县_汇总.xlsx"
# years = [2000,2005,2010,2015,2020]
# k  = {}
# for year in years:
#     name = str(year)
#     de = pd.read_excel(path,sheet_name=name)
#     #归一化
#     df = de[['CITY','农业依赖度','经济适应能力']]
#     df['农业依赖度'] = df['农业依赖度']/df['农业依赖度'].sum() 
#     df['经济适应能力'] = df['经济适应能力'] /df['经济适应能力'].sum()
#     k[year] = df
# output_path = r"F:\论文写作\欣雨学姐\计算\生态系统计算\归一化数据.xlsx"
# with pd.ExcelWriter(output_path) as writer:
#     for year in years:
#         k[year].to_excel(writer, sheet_name=str(year), index=True)