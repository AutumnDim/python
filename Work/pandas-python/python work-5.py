# -*- coding: utf-8 -*-
"""
Created on Mon May 20 17:11:16 2024

@author: hqm
"""
import pandas as pd 
import os



in_path = r"D:\厚德学习\Pandas__Python\python_work\5 整合\气象数据"
out_path = r"D:\厚德学习\Pandas__Python\python_work\5 整合\RH数据"

start = 1
# 
vrs = ['Maxi T','Mini T', 'P','RH','S','WS']
for vr in vrs:
    df_all = pd.DataFrame() #建立空的dataframe
    # ls_df = []
    for start in range(1, 366, 8):
        end = start + 7 if start != 361 else 366
        D = f'{start}-{end}'
        fn_in = in_path + os.sep + f"{D}"
        # fn_in
        fn = os.listdir(fn_in)
        
        for file in fn :
            if vr in file:
                file_path = os.path.join(fn_in, file)
                df = pd.read_csv(file_path,index_col=0, encoding="GBK")
                df2 = df.iloc[:,4:5]
                df2.columns = [D]
                # ls_df.append(df2)
                dfx = pd.concat([df_all,df2],axis = 1)
                df_all = dfx
                
    # df_all = pd.concat(df.iloc[:,0:3],ls_df,axis=1)
    df_all = pd.concat([df.iloc[:,0:3],df_all],axis=1)
    df_all.to_csv(out_path + os.sep + f'{vr}.txt',sep='\t')
    print(vr)
            
            
































        
        
