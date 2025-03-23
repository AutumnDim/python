# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 11:01:45 2025

@author: hqm
"""
import rasterio
import pandas as pd
import numpy as np
import os
from glob import glob
import mycode.arcmap as ap
from pyproj import CRS
os.chdir(r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算")
def read_tif(path,n = 1):
    if n != 1 | n != 2 | n != 3:
        print('n=1 or 2 or 3')
        return 0  #可有可无
    else:
        with rasterio.open(path) as src:
            nodata = np.float32(src.nodata)
            profile = src.profile
            profile.data['dtype'] = 'float32'
            data = src.read().astype('float32')
            shape = data.shape
            data = data.reshape(-1,1)
            #data = data.reshape(1,-1)
            data[data == nodata] = np.nan
            data = pd.DataFrame(data)
        if n == 1:
            return data
        elif n == 2:
            return data,profile
        elif n == 3:
            return data,profile,shape

def out(a,path,shape,profile):
    result = pd.DataFrame(np.array(a).reshape(shape)[0])
    with rasterio.open(path,'w',**profile) as wr:
        wr.write(result,1)
# 坡度因子s,坡长因子l 
data_s,profile_s,shape_s = read_tif(r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\数据\坡度.tif",n=3)
data_dem = read_tif(r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\数据\DEM.tif")

# 得坡度因子s
df = data_s.copy()
df[data_s[0] < 5] = 10.8 * np.sin(np.radians(df[data_s[0] < 5])) + 0.03
df[data_s[0] >= 10] = 21.91 * np.sin(np.radians(df[data_s[0] >= 10])) - 0.96
df[(data_s[0] >= 5) & (data_s[0] < 10)] = 16.8 * np.sin(np.radians(df[(data_s[0] >= 5) & (data_s[0] < 10)])) - 0.5


# 得坡长因子l
pc = data_dem / np.sin(np.radians(data_s))
b = (np.sin(np.radians(data_s)) / 0.089) / (3.0 * np.power(np.sin(np.radians(data_s)),0.8) + 0.56)
m = b / (1 + b)
l_all = np.power((pc/22.13),m)

path_s = '土壤因子\s1.tif'   
path_l = '土壤因子\l1.tif'
out(df,path_s,shape_s,profile_s)  # s 坡度因子
out(l_all,path_l,shape_s,profile_s)   # l 坡长因子



# 植被覆盖和管理因子c
if not os.path.exists(r'土壤因子\c1'):
    os.mkdir(r'土壤因子\c1')
for fd in glob(r'F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\FVC\*.tif'):
    print(fd)
    y = fd.split(os.sep)[-1].split('.')[0]
    data_c,profile_c,shape_c = read_tif(fd,n=3)
    
    df = data_c.copy()
    df[data_c <= 0.1] = 1.0
    df[(data_c > 0.1) & (data_c < 0.783)] = 0.6508 - 0.3436 * np.log10((df[(data_c > 0.1) & (data_c < 0.7830)]))
    df[data_c > 0.783] = 0
    
    path_c = f'土壤因子\c1\c1_{y}.tif'
    out(df,path_c,shape_c,profile_c)

# 水土保持措施因子p
data_lu,profile_lu,shape_lu = read_tif(r"F:\论文写作\欣雨学姐\数据\Data\土地利用\2018\out\2018.tif",n=3)
data_s = read_tif(r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\数据\DEM.tif")

c1 = (data_lu[0] <= 12.0)
c2 = (((data_lu[0] >= 21.0) & (data_lu[0] <= 24.0)) | ((data_lu[0] >= 31.0) & (data_lu[0] <= 33.0))) # 林地、草地
c3 = (((data_lu[0] >= 41.0) & (data_lu[0] <= 46.0)) | (data_lu[0] == 64.0)) # 水域
c4 = (((data_lu[0] >= 51.0) & (data_lu[0] <= 53.0)) | ((data_lu[0] >= 61.0) & (data_lu[0] <= 67.0))) # 裸地

dd = data_s.copy()
dd[c2] = 0.9
dd[c3] = 0
dd[c4] = 1.0
dd[(c1 & (data_s[0] == 0.0))] = 0.2
dd[(c1 & ((data_s[0] > 0.0) & (data_s[0] <= 10.0)))] = 0.5
dd[(c1 & ((data_s[0] > 10.0) & (data_s[0] <= 25.0)))] = 0.6
dd[(c1 & ((data_s[0] > 25.0) & (data_s[0] <= 45.0)))] = 0.8
dd[(c1 & (data_s[0] > 45.0))] = 1.0
dd[(data_lu[0].isna())] = np.nan

path_p = r'土壤因子\p1.tif'
out(dd,path_p,shape_lu,profile_lu)