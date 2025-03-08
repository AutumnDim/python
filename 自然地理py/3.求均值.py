# -*- coding: utf-8 -*-
"""
Created on Thu May 23 20:12:30 2024

@author: hqm
"""
import pandas as pd
import geopandas as gpd 
import numpy as np
import os
path ="D:\数据批量\表格\IDW"
out_path = "D:\数据批量\表格\均值"
list = ['1950','1960','1980','1990','2000','2010','2020']
for k in list:
    df =pd.read_csv(path + '\\' + f'IDW_{k}_daily_.csv')
    df1 = df.iloc[:,4:-1]
    df2 = df1.mean(axis=1)
    df3 = df.iloc[:,1:4]
    df_output = pd.concat([df3,df2],axis=1)
    df_output.to_csv(out_path + '\\'+ f'{k}.csv',index=False,header=[ 'NAME', 'LATITUDE', 'LONGITUDE', 'TEMP'])
