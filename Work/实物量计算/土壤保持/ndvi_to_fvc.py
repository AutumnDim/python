# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 15:13:37 2023

@author: 31961
"""

 
import rasterio,os
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt

for year in range(2000,2021,5):
    
    #ndvi_path = r"F:\论文写作\欣雨学姐\数据\土壤保持\数据\NDVI\out" + os.sep + 'NDVI' + f'{year}' + '.tif'
    ndvi_path = rf"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\数据\NDVI\NDVI{year}.tif"
    with rasterio.open(ndvi_path) as ndvi:
        ndvi1 = ndvi.read()
        nodata = ndvi.nodata
        ndvi1[ndvi1==nodata]= np.nan
        profile = ndvi.profile
        
    soi = np.nanpercentile(ndvi1,5)
    veg = np.nanpercentile(ndvi1,95)
    
    fvc = (ndvi1 - soi) / (veg - soi) 
    # np.nanpercentile(fvc,95)
    # # plt.hist(fvc[0],100)
    # a = fvc[~np.isnan(fvc)]
    # b = fvc[fvc>100]
    # # len(b)/len(a)
    fvc_path = r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\计算\FVC" + os.sep + 'FVC' + f'{year}' + '.tif'
    fvc1 = rasterio.open(fvc_path, 'w', **profile)
    fvc1.write(fvc)
    fvc1.close()
    


# a = np.array([[[10, 7, 4], [3, 2, np.nan]]])
# print (np.nanpercentile(a, 50)) 






