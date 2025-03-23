# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 20:39:54 2023

@author: 31961
"""

# import pandas as pd
# import glob
import rasterio,os
import numpy as np


# s
with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\数据\坡度.tif") as slope:
    slope1 = slope.read()
    nodata = slope.nodata
    slope1[slope1 ==nodata]= np.nan
    profile = slope.profile

rd = np.radians(slope1)
t = np.tan(rd) * 100
t1 = t.copy()
t1[t<9] = 10.8 * np.sin(rd[t<9]) + 0.03
t1[t>=18] = 21.91 * np.sin(rd[t>=18]) - 0.96
t1[(t >= 9) & (t < 18)] = 16.8 * np.sin(rd[(t >= 9) & (t < 18)]) - 0.5

s_path = r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\土壤因子\s1.tif"
s1 = rasterio.open(s_path, 'w', **profile)
s1.write(t1)
s1.close()


# l
with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\数据\DEM.tif") as dem:
    dem1 = dem.read()
    nodata = dem.nodata
    dem1[dem1==nodata]= np.nan
t_0 = np.sin(t)
B = (np.sin(t) / 0.089) / (3.0 * np.power(np.sin(t),0.8) + 0.56)
m = B/(1+B)
pc = dem1 / np.sin(t)
pc[t_0==0] = 0
l = np.power((pc/22.13),m)
l[t_0 == 0] = 1


l_path = r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\土壤因子\l1.tif"
l1 = rasterio.open(l_path, 'w', **profile)
l1.write(l)
l1.close()



# c
if not os.path.exists(r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\土壤因子\c1"):
    os.mkdir(r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\土壤因子\c1")
for year in range(2000,2021,5):
    
    fvc_path = r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\FVC" + os.sep + 'FVC' + f'{year}' + '.tif'
    
    with rasterio.open(fvc_path) as fvc:
        fvc1 = fvc.read()
        nodata = fvc.nodata
        fvc1[fvc1 ==nodata] = np.nan
        profile = fvc.profile
        
    c = fvc1.copy()
    c[fvc1<=0.1] = 1
    c[(fvc1>0.1)&(fvc1<=0.783)] = 0.6508 - 0.3436 * np.log10(fvc1[(fvc1>0.1)&(fvc1<=0.783)])
    c[(fvc1>0.783)] = 0
    
    c_path = r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\土壤因子\c1" + os.sep + 'c1_' + f'FVC{year}' + '.tif'
    c1 = rasterio.open(c_path, 'w', **profile)
    c1.write(c)
    c1.close()


# p
with rasterio.open(r"F:\论文写作\欣雨学姐\数据\Data\土地利用\2018\out\2018.tif") as lu:
    lu1 = lu.read().astype(float)
    nodata = lu.nodata
    lu1[lu1 == nodata] = np.nan

p = lu1.copy()
p[(lu1>= 21) & (lu1 <= 33)] = 0.9
p[(lu1>= 51) & (lu1 <= 67)] = 1
p[((lu1>= 41) & (lu1 <= 46)) | (lu1==64)] = 0
p[(lu1<= 12) & (slope1==0)] = 0.2
p[(lu1<= 12) & ((slope1>0) & (slope1<=10))] = 0.5
p[(lu1<= 12) & ((slope1>10) & (slope1<=25))] = 0.6
p[(lu1<= 12) & ((slope1>25) & (slope1<=45))] = 0.8
p[(lu1<= 12) & (slope1>45)] = 1

p_path = r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\土壤因子\p1.tif"
p1 = rasterio.open(p_path, 'w', **profile)
p1.write(p)
p1.close()



with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\土壤因子\R.tif") as R:
    R1 = R.read()
    nodata = R.nodata
    R1[R1 == nodata] = np.nan
with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\土壤因子\K.tif") as k:
    k1 = k.read()
    nodata = k.nodata
    k1[k1 == nodata] = np.nan

for year in range(2000,2021,5):
    
    c_path = r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\土壤因子\c1" + os.sep + 'c1_' + f'FVC{year}' + '.tif'
    
    with rasterio.open(c_path) as c2:
        c3 = c2.read()
        
    Qsr = R1 * k1 * l * t1 * (1 - c3 * p)
    Qsr_path = r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\土壤保持" + os.sep + f'土壤保持{year}' + '.tif'
    Qsr1 = rasterio.open(Qsr_path, 'w', **profile)
    Qsr1.write(Qsr)
    Qsr1.close()
























