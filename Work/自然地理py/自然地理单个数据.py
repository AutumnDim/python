# -*- coding: utf-8 -*-
"""
Created on Sun May  5 21:18:21 2024

@author: hqm

"""
import geopandas as gpd 
import pandas as pd 
import numpy as np
df = gpd.read_file(r"D:\自然\TEMP_2020_daily.shp")
arr = df.values
arr1 = arr[:,6:-1]
arr1[arr1>100] = np.nan 
arr2 = np.nanmean(arr1,axis=1)
arr3 = arr[:,0:5]
arr2_up = arr2.reshape(-1,1)
arr4 = np.concatenate((arr3,arr2_up),axis=1)
df_output = pd.DataFrame(arr4)
df_output.to_excel(r"D:\自然\TEMP_2020_TEMP.xlsx",index=False,header=['STATION','NAME','LATITUDE','LONGITUDE','ELEVATION','TEMP'])