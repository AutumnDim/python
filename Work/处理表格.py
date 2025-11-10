# -*- coding: utf-8 -*-
"""
Created on Sat Aug 30 09:17:21 2025

@author: hqm
"""
'''表一'''
import pandas as pd
import numpy as np
import os

path = r"F:\work\地理所\地上生物量\青海湖-生物量+经纬度.xlsx"
df = pd.read_excel(path, engine='openpyxl')
grouped_df = df.groupby(['经度', '纬度'])[['AGB（g/m2)']].mean().reset_index()
grouped_df['年份'] = 2024
grouped_df.to_csv(r"F:\work\地理所\地上生物量\采样点数据\one.csv")


'''表二'''
import pandas as pd
import numpy as np
import os
path = r"F:\work\地理所\地上生物量\青海湖科考生物量数据.xlsx"
df1 = pd.read_excel(path,sheet_name='样地信息').iloc[:,:3]
df2 = pd.read_excel(path,sheet_name='地上生物量')
grouped_df = df2.groupby(['样地编号'])[['干重（g/m2）']].mean().reset_index()
dk = pd.concat([df1, grouped_df[['干重（g/m2）']]], axis=1)
dk['年份'] = np.where(dk['样地编号'].between(1, 38), 2023, 2024)
dk.to_csv(r"F:\work\地理所\地上生物量\采样点数据\two.csv")

'''补充表三'''
import pandas as pd
import numpy as np
import os
path = r"F:\work\地理所\地上生物量\data.xlsx"
df = pd.read_excel(path)
lon_min, lon_max = 99, 101
lat_min, lat_max = 35, 38

df_filtered = df[
    (df['longitude'].between(lon_min, lon_max)) &
    (df['latitude'].between(lat_min, lat_max))
]
df_filtered.to_csv(r"F:\work\地理所\地上生物量\采样点数据\three.csv")









