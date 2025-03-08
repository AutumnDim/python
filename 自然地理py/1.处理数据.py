# -*- coding: utf-8 -*-
"""
Created on Wed May 22 23:46:37 2024

@author: hqm
"""
# -*- coding: utf-8 -*-

import pandas as pd
import geopandas as gpd 
import numpy as np
import os
path ="D:\数据批量\数据"
out_path = "D:\数据批量\表格"
files = os.listdir(path)
for file in files:
    if file.endswith('.dbf'):
        new_file_path = os.path.join(path,file)
        df = gpd.read_file(new_file_path)
        a = 9999.9
        df[df==a] = np.nan
        nun_count = df.isnull().apply(sum,axis=1)
        df1 = pd.concat([df,nun_count],axis=1) #索引添加
        df2 = df1.dropna(thresh=292)
        df3 = df2.drop(['statement',0],axis=1)
        df3.columns=range(len(df3.columns))
        output_name = os.path.splitext(file)[0] + '_.csv'
        output_path = os.path.join(out_path,output_name)
        # output_name = out_path + '.csv'
        df3.to_csv(output_path,index=False)
