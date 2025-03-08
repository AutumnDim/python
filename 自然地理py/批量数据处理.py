# -*- coding: utf-8 -*-
"""
Created on Wed May 22 14:55:05 2024

@author: hqm
"""
# -*- coding: utf-8 -*-
# 遍历文件
import pandas as pd
import geopandas as gpd 
import numpy as np
import os
path ="D:\数据批量\表格\IDW"
out_path = "D:\数据批量\表格\均值"
files = os.listdir(path)
for file in files:
    if file.endswith('.csv'):
        new_file_path = os.path.join(path,file)
        df = gpd.read_file(new_file_path)
        df2 = df1.iloc[:,6:-1]
        df3 = df2.mean(axis=1)
        df4 = df1.iloc[:,1:5]
        df_output = pd.concat([df4,df3],axis=1)
        output_file_name = os.path.splitext(file)[0] +'.csv'
        output_file_path = os.path.join(out_path,output_file_name)
        df_output.to_csv(output_file_path,index=False,header=[ 'NAME', 'LATITUDE', 'LONGITUDE', 'ELEVATION', 'TEMP'])
