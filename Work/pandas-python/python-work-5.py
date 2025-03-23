# -*- coding: utf-8 -*-
"""
Created on Fri May 31 19:48:40 2024

@author: hqm
"""
import pandas as pd
import numpy as np
import os
from pathlib import Path
path = r"D:\厚德学习\Pandas__Python\python_work\5 整合\气象数据"
out_path = r"D:\厚德学习\Pandas__Python\python_work\5 整合\数据"
ou_ph = r"D:\厚德学习\Pandas__Python\python_work\5 整合\输出"
p = Path(path)
vrs = ['Maxi T','Mini T', 'P','RH','S','WS']
f = pd.read_csv(r"D:\厚德学习\Pandas__Python\python_work\5 整合\气象数据\225-232\Maxi T 225-232.txt",encoding="GBK").iloc[:,0:4]
for i in vrs:
    for (iroot , idirs ,ifiles) in os.walk(path):
        list = sorted(idirs,key=lambda x:int(x.replace("-","")))
        for k in list:
            files = path + os.sep + k + os.sep + i +' ' + k + '.txt'
            data = pd.read_csv(files,encoding="GBK").iloc[:,4]
            f[k] = data
        f.to_csv(out_path + os.sep + f'{i}.txt',sep = '\t')
        print(i)
            
        
        
    
    
    
    
    
    
    
    
    
    
    
    # for file_name in p.rglob('*'):
    #     for file in file_name.rglob('*'):
            
    #         k = file_name.stem
    #         u = file.stem
    #         fn = path + os.sep + k + os.sep + u +'.txt'
    #         data = pd.read_csv(fn,encoding="GBK").iloc[:,4]
    #         f[k] = data
    #     p = f.columns[4:].tolist()
    #     list = sorted(p,key=lambda x:int(x.replace("-","")))
        
    #     f.to_csv(ou_ph + os.sep + f'{i}.txt',sep='\t')
    #     print(i)
            
            
        
        
    

# file_list = []
# file_dict = {}
# for iroot ,idirs,ifiles in os.walk(path):
    
#     content = file.read()
