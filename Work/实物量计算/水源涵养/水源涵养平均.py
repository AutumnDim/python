# -*- coding: utf-8 -*-
"""
Created on Tue May 23 10:36:43 2023

@author: wly
"""


import mycode.arcmap as ap
import pandas as pd
import os


dir_qwr = r'D:\水源涵养\水源涵养\年平均'
qwr_path = r'D:\水源涵养\水源涵养\总平均\qwr.tif'


n = 0
for i in range(2001,2022):
    
    n += 1
    path_qwr = os.path.join(dir_qwr, f'{i}.tif')
    
    if n == 1:
        df_all,meat,shape = ap.read(path_qwr,3)
    else:
        dfn = ap.read(path_qwr)
        df_all = pd.concat([df_all,dfn],axis=1)

df = df_all.agg('mean',axis=1)






ap.out(qwr_path, df, shape, meat)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    




































