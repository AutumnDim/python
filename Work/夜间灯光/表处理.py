# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 20:35:15 2024

@author: hqm
"""
import pandas as pd 
import numpy as np 
path1 = r"F:\夜间灯光\数据\Elvidge_DMSP_intercalib_coef.csv"
path2 = r"F:\夜间灯光\数据\卫星数据.csv"
out1 = r"F:\夜间灯光\表\WXk.csv"
out2 = r"F:\夜间灯光\表\合并.csv"
data1 = pd.read_csv(path1)
data2 = pd.read_csv(path2, encoding='utf-8')
data1.index = data1['satellite'] + data1['year'].astype(str)
data2.index = data2['卫星'] + data2['年份'].astype(str)
data1 = data1.iloc[:,2:5]
data2 = data2.iloc[:,2:5]
data = pd.merge(data1, data2, left_index=True, right_index=True, how='inner')
data2.to_csv(out1, index=True, encoding='utf-8')
data.to_csv(out2, index=True, encoding='utf-8')


