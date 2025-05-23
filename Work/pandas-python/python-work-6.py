# -*- coding: utf-8 -*-
"""
Created on Thu May 30 10:11:32 2024

@author: hqm
"""
import pandas as pd
import os
import glob
from glob import glob as glb
in_path = r"D:\厚德学习\Pandas__Python\python_work\6 数据分组\数据"
out_path =r"D:\\厚德学习\\Pandas__Python\\python_work\\6 数据分组\结果"
f = pd.read_csv(r"D:\厚德学习\Pandas__Python\python_work\6 数据分组\2015\1\Maxi T 1-15.txt",encoding="GBK").iloc[:,:4]
vrs = ['Maxi T','Mini T', 'P','RH','S','WS']
for y in range(2015,2021):
    for i in vrs:
        out_ph = out_path + os.sep + i
        if not os.path.exists(out_ph):
            os.makedirs(out_ph)
        else:
            pass
            #out_file = out_ph + os.sep + str(y) +'.txt'
        
        for m in range (1,13):
            files = glb (in_path + os.sep +str(y) + os.sep +str(m) + os.sep + i +'*.txt')
            try:
                f[str(m) +'a'] = pd.read_csv(files[0],encoding="GBK").iloc[:,5]
            except IndexError:
                continue
            try:
                f[str(m) +'b'] = pd.read_csv(files[1],encoding="GBK").iloc[:,5]
            except IndexError:
                    continue
            
            out_file = os.path.join(out_ph, f'{y}.txt')
            f.to_csv(out_file, sep=',', index=False)
        #f.to_csv(out_file,sep = ',')
            
