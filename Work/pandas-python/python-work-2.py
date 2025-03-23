# -*- coding: utf-8 -*-
"""
Created on Sat May 18 15:36:10 2024

@author: hqm
"""
# import pandas as pd
# import geopandas as gpd
# import numpy as np
# import os
# path_in = r"F:\厚德学习\Pandas__Python\python_work\2 批量读取\abstract"
# # files = os.listdir(path)
# path_out =  r"F:\厚德学习\Pandas__Python\python_work\2 批量读取\k"
# for y in range(1980,1990):
#     fn_in = path_in + os.sep + f'PRCP_{y}.txt'
#     fn_out = path_out + os.sep + f'PRCP_{y}.txt'
#     df = pd.read_csv(fn_in, header=None)
#     df_replace = df.replace(50136, np.nan)
# dfx = df[df[0] == name]
# df_g = df.groupby([0])
#for i in df_g:
#    dfn = i[1]
#    pass
#    df_replace.to_csv(fn_out, sep='\t')
    
import pandas as pd
import numpy as np
from glob import glob as glb
import os
k = []
path = r"F:\厚德学习\Pandas__Python\python_work\2 批量读取\abstract"
fist = glb(path + '*\*.txt')
for i in fist:
    data = pd.read_csv(i)
    data1 = data.replace(50246,np.nan)
    k.append(data1)
    

data_all = []
path = r"F:\厚德学习\Pandas__Python\python_work\2 批量读取\abstract"
#os.chdir(path)
for root,dirs,files in os.walk(path ):
    print(files)
for i in files:
    file_path = os.path.join(path, i)
    datai =pd.read_csv(file_path)
    new_datai = datai.replace(50136,np.nan)
    data_all.append(new_datai)    
    



# for file in files :
#     if file.endswith('.txt'):
#         new_file_path = os.path.join(path,file)
#         k = pd.read_table(new_file_path,delimiter=',',header=None)
#         n = k.replace(999990,'nan')
#         # a = 999990
#         # k[k==a] = np.nan
#         output_file_name = os.path.splitext(file)[0] +'.csv'
#         output_file_path = os.path.join(path,output_file_name)
#         n.to_csv(output_file_path,index=True,header=True)
    






























    