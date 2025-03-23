# -*- coding: utf-8 -*-
"""
Created on Sat May 18 10:50:15 2024

@author: hqm
"""
import pandas as pd 
k = pd.read_csv(r"D:\厚德学习\Pandas__Python\python_work\1 读取txt\v11002_qinghai.txt", sep='\s+' )
out_path = r"D:\厚德学习\Pandas__Python\python_work\1 读取txt\v11002_qinghai.csv"
m = k.replace(32765,0)
m1 = m.iloc[:,4:].mean(axis = 1).to_frame(name='mean')
m2 = m.iloc[:,:3]
m3 = pd.concat([m2,m1],axis = 1)
m3.to_csv(out_path, index=True,header=True)

