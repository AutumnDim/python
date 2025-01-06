# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 22:07:15 2024

@author: hqm
"""
import pandas as pd
import numpy as np 
path = r"F:\学长数据\元彬学长\our\表\intk.csv"
k = pd.read_csv(path)
df = pd.DataFrame(k)
df = df.iloc[:,1:]
df = df.pivot(index='var1', columns='var2', values='qv12')
index = df.isna().sum(axis = 1).sort_values(ascending=True)
columns = df.isna().sum(axis = 0).sort_values(ascending=False)
sorted_df = df.loc[index.index, columns.index]
