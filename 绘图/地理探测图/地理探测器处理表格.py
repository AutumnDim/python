# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 22:07:15 2024

@author: hqm
"""

import pandas as pd
import numpy as np 
path = r"F:\学长数据\元彬学长\hu\hu\int.csv"
path2 = r"F:\学长数据\元彬学长\hu\hu\p_q.csv"
data2 = pd.read_csv(path2)
Q = data2.drop(index =1).T
k = pd.read_csv(path)
df = pd.DataFrame(k)
dff = df.iloc[:,1:]
df = dff.pivot(index='var1', columns='var2', values='qv12')
dfk = dff.pivot(index='var1', columns='var2', values='interaction')
index = df.isna().sum(axis = 1).sort_values(ascending=True)
columns = df.isna().sum(axis = 0).sort_values(ascending=False)
sorted_df = df.loc[index.index, columns.index]
eff_df = dfk.loc[index.index, columns.index]
