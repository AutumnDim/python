# -*- coding: utf-8 -*-
"""
Created on Sat 2024/8/24 9:43
@Author : lyr
将2017-2022年的降水数据格式
"""
import os.path
import pandas as pd
import datetime
import numpy as np
import glob as gb
from collections import defaultdict
from tqdm import tqdm
import os
import re

""" 分要素文件夹 """

# path = r'E:\stations\分要素1980-2016\*\*.txt'
# output_path = r'E:\stations_new'
# files = gb.glob(path)
# # files = ["E:\stations\分要素1980-2016\平均相对湿度\Average_relative_humidity_2015.txt"]
# for file in tqdm(files, total=len(files), desc="Processing years"):
#     folder_name = file.split('\\')[-2]
#     file_name = file.split('\\')[-1]
#     print(file_name)
#     if file_name == 'readme.txt':
#         continue
#     else:
#         split = re.split(r'[._]',file_name)
#         # var_name = split[0]
#         year = split[-2]
#         df_tmax = pd.read_csv(file, sep=' ', header=1,low_memory=False)
#         # 重命名列为 Pandas 期望的名称
#         df_tmax.rename(columns={'Year': 'year', 'Mon': 'month', 'Day': 'day'}, inplace=True)
#         df_tmax['DATE'] = pd.to_datetime(df_tmax[['year', 'month', 'day']])
#         df_tmax['yearofday'] = df_tmax['DATE'].dt.dayofyear
#         df_tmax.drop(columns=['DATE','year', 'month','day'], inplace=True)   #获取每年第几天的数据
#         #获取台站的一些基础信息
#         df_infor = df_tmax[['Station_ID_C', 'Lat', 'Lon', 'Alti']]
#         df_infor = df_infor.drop_duplicates(subset='Station_ID_C')
#         df_infor = df_infor.dropna(subset=['Station_ID_C'])
#
#         df = df_tmax.iloc[:,[0,1,-2,-1]]
#         df = df.dropna(thresh=df.shape[1] - 3 + 1)    ##df中如果有一行只有第一列有值，其余都为nan，删去这一行
#
#         df1 = df.set_index(['Station_Name', 'Station_ID_C','yearofday'])
#         # duplicates = df1.index[df1.index.duplicated()]
#         startswith_str = df1.columns[0][0]    #获取变量值列的第一个字母
#         df2 = df1.unstack(level='yearofday')
#         df2 = df2.reset_index()
#         #将多层索引平面化
#         df2.columns = ['_'.join(map(str, col)) if isinstance(col, tuple) else col for col in df2.columns]
#         #找到站台号对应的经纬度
#         for index,sta in df_infor.iterrows():
#             col = np.where(df2.iloc[:, 1] == sta[0])[0]
#             df2.loc[col,['Lat', 'Lon', 'Alti']] = [sta[1],sta[2],sta[3]]
#         # print('ok')
#         # 将列移动到前面
#         lat_lon_alti = df2[['Lat', 'Lon', 'Alti']]
#         df2.drop(['Lat', 'Lon', 'Alti'], axis=1, inplace=True)
#         df2.insert(2,  'Lon', lat_lon_alti['Lon'])
#         df2.insert(3, 'Lat', lat_lon_alti['Lat'])
#         df2.insert(4,'Alti', lat_lon_alti['Alti'])
#         # 创建一个新列名列表
#
#         new_columns = []
#         for column in df2.columns:
#             if column.startswith(startswith_str):
#                 split_day = column.split("_")[-1]
#                 new_name = 'D' + str(split_day)
#             else:
#                 new_name = column  # 如果列名不以'T'开头，则保持原样
#             new_columns.append(new_name)
#         new_columns[:5] = ['台站名', '台站编号', '经度', '纬度', '海拔']
#         # 使用新列名列表来重命名df2的列
#         df2.columns = new_columns
#         df_base = df2.iloc[:,:5]
#         df_all = df2.drop(columns='台站名')
#         #输出文件
#         base_folder = output_path + os.sep + 'base_data' + os.sep + folder_name
#         if os.path.exists(base_folder):
#             pass
#         else:
#             os.makedirs(base_folder)
#         df_base.to_csv(base_folder + os.sep + file_name)
#
#         data_folder = output_path + os.sep + folder_name
#         if os.path.exists(data_folder):
#             pass
#         else:
#             os.makedirs(data_folder)
#         df_all.to_csv(data_folder + os.sep + file_name)
# print('ok')

""" 全国气象台站数据2017文件夹 """

# path = r'E:\stations\全国气象台站数据2017\*\*.txt'
# output_path = r'E:\单年'
# files = gb.glob(path)
# data_dict = {}
# for file in tqdm(files, total=len(files), desc="Processing years"):
#     folder_name = file.split('\\')[-2]
#     file_name = file.split('\\')[-1]
#     if file_name == 'readme.txt':
#         continue
#     else:
#         split = re.split(r'[._]',file_name)
#         # var_name = split[0]
#         year = split[-3]
#         df_tmax = pd.read_csv(file, sep=' ', header=1,low_memory=False)
#         # 重命名列为 Pandas 期望的名称
#         df_tmax.rename(columns={'Year': 'year', 'Mon': 'month', 'Day': 'day'}, inplace=True)
#         df_tmax['DATE'] = pd.to_datetime(df_tmax[['year', 'month', 'day']])
#         df_tmax['yearofday'] = df_tmax['DATE'].dt.dayofyear
#         df_tmax.drop(columns=['DATE','year', 'month','day'], inplace=True)   #获取每年第几天的数据
#
#         # 将数据存储在字典中
#         if year not in data_dict:
#             data_dict[year] = {}
#         if folder_name not in data_dict[year]:
#             data_dict[year][folder_name] = []
#
#         # 添加到列表中
#         data_dict[year][folder_name].append(df_tmax)

# 获取该年份的字典
# folders = data_dict['2017']
# # 遍历每个 folder_name 和 DataFrames
# for folder_name, data_frames in folders.items():
#     df_all = pd.DataFrame()
#     for df in data_frames:
#         # 对每个 DataFrame 执行操作
#         df_all = pd.concat([df_all,df])
#
#     #获取台站的一些基础信息
#     df_infor = df_all[['Station_ID_C', 'Lat', 'Lon', 'Alti']]
#     df_infor = df_infor.drop_duplicates(subset='Station_ID_C')
#     df_infor = df_infor.dropna(subset=['Station_ID_C'])
#
#     df = df_all.iloc[:,[0,1,-2,-1]]
#     df = df.dropna(thresh=df.shape[1] - 3 + 1)    ##df中如果有一行只有第一列有值，其余都为nan，删去这一行（解决台站名称和数据换行的情况）
#     df1 = df.set_index(['Station_Name', 'Station_ID_C', 'yearofday'])
#     # duplicates = df1.index[df1.index.duplicated()]      #找到索引相同的数据
#     # duplicate_data = df1.loc[duplicates]                # 筛选所有重复的行
#     df1 = df1[~df1.index.duplicated(keep='first')]     #保留重复的第一个数据（原始数据出现了两个相同的日期）
#     startswith_str = df1.columns[0][0]                  #获取变量值列的第一个字母
#     df2 = df1.unstack(level='yearofday')
#     df2 = df2.reset_index()
#     #将多层索引平面化
#     df2.columns = ['_'.join(map(str, col)) if isinstance(col, tuple) else col for col in df2.columns]
#     #找到站台号对应的经纬度
#     df2.rename(columns={'Station_ID_C_': 'Station_ID_C'}, inplace=True)
#     df2 = df2.merge(df_infor[['Station_ID_C', 'Lat', 'Lon', 'Alti']], on='Station_ID_C', how='left')
#     # 将列移动到前面
#     lat_lon_alti = df2[['Lat', 'Lon', 'Alti']]
#     df2.drop(['Lat', 'Lon', 'Alti'], axis=1, inplace=True)
#     df2.insert(2,  'Lon', lat_lon_alti['Lon'])
#     df2.insert(3, 'Lat', lat_lon_alti['Lat'])
#     df2.insert(4,'Alti', lat_lon_alti['Alti'])
#     # 创建一个新列名列表
#
#     new_columns = []
#     for column in df2.columns:
#         if column.startswith(startswith_str):
#             split_day = column.split("_")[-1]
#             new_name = 'D' + str(split_day)
#         else:
#             new_name = column  # 如果列名不以'T'开头，则保持原样
#         new_columns.append(new_name)
#     new_columns[:5] = ['台站名', '台站编号', '经度', '纬度', '海拔']
#     # 使用新列名列表来重命名df2的列
#     df2.columns = new_columns
#     df_base = df2.iloc[:,:5]
#     df_all = df2.drop(columns='台站名')
#     output_name = df1.columns[0] + '_2017.txt'
#     #输出文件
#     base_folder = output_path + os.sep + 'base_data' + os.sep + folder_name
#     if os.path.exists(base_folder):
#         pass
#     else:
#         os.makedirs(base_folder)
#     df_base.to_csv(base_folder + os.sep + output_name)
#
#     data_folder = output_path + os.sep + folder_name
#     if os.path.exists(data_folder):
#         pass
#     else:
#         os.makedirs(data_folder)
#     df_all.to_csv(data_folder + os.sep + output_name)
#     print(folder_name)

""" 2017剩下半个月 """

# def conversion(df_var):
#     df_var.rename(columns={'Year': 'year', 'Mon': 'month', 'Day': 'day'}, inplace=True)
#     df_var['DATE'] = pd.to_datetime(df_var[['year', 'month', 'day']])
#     df_var['yearofday'] = df_var['DATE'].dt.dayofyear
#     df_var.drop(columns=['DATE', '时间', 'year', 'month', 'day'], inplace=True)  # 获取每年第几天的数据
#
#     df = df_var.dropna(thresh=df_var.shape[1] - 3 + 1)    ##df中如果有一行只有第一列有值，其余都为nan，删去这一行（解决台站名称和数据换行的情况）
#     df1 = df.set_index(['Station_Name', 'Station_ID_C', 'yearofday'])
#     df1 = df1[~df1.index.duplicated(keep='first')]     #保留重复的第一个数据（原始数据出现了两个相同的日期）
#     startswith_str = df1.columns[0][0]  # 获取变量值列的第一个字母
#     output_name = df1.columns[0] + '_2017.txt'
#     df2 = df1.unstack(level='yearofday')
#     df2 = df2.reset_index()
#     #将多层索引平面化
#     df2.columns = ['_'.join(map(str, col)) if isinstance(col, tuple) else col for col in df2.columns]
#
#     new_columns = []
#     for column in df2.columns:
#         if column.startswith(startswith_str):
#             split_day = column.split("_")[-1]
#             new_name = 'D' + str(split_day)
#         else:
#             new_name = column  # 如果列名不以'T'开头，则保持原样
#         new_columns.append(new_name)
#     new_columns[:2] = ['台站名', '台站编号']
#     # 使用新列名列表来重命名df2的列
#     df2.columns = new_columns
#     df_base = df2.iloc[:,:2]   #基础数据
#     df_all = df2.drop(columns='台站名')  #最后输出数据完整数据
#     return df_base,df_all,output_name
#
# def output(base,var,name,file_name):
#     # base.to_csv(output_path + os.sep + 'base1' + os.sep + file_name + '_' + name)
#     var.to_csv(output_path + os.sep + file_name + '_' + name)
# path = r'E:\stations\全国气象台站数据2017\*.txt'
# output_path = r'E:\单年'
# files = gb.glob(path)
# for file in files:
#     file_name = os.path.splitext(file)[0].split('\\')[-1]
#     df = pd.read_csv(file,sep=' ')
#     df = df.iloc[:,:11]
#     df.columns = ['Station_ID_C','时间','Year','Mon','Day','Station_Name','TEM_Max','TEM_Min','RHU_Avg','PRE_Time','SSH']
#     sta = df.pop('Station_Name')
#     df.insert(0,'Station_Name',sta)
#     tmax = df.iloc[:,:7]
#     tmin = df.iloc[:,[0,1,2,3,4,5,-4]]
#     RHU = df.iloc[:,[0,1,2,3,4,5,-3]]
#     pre = df.iloc[:,[0,1,2,3,4,5,-2]]
#     SSH = df.iloc[:,[0,1,2,3,4,5,-1]]
#
#     tmax_base,df_tmax,tmax_name = conversion(tmax)
#     tmin_base,df_tmin,tmin_name = conversion(tmin)
#     RHU_base,df_RHU,RHU_name = conversion(RHU)
#     pre_base,df_pre,pre_name = conversion(pre)
#     SSH_base,df_SSH,SSH_name = conversion(SSH)
#
#     output(tmax_base,df_tmax,tmax_name,file_name)
#     output(tmin_base,df_tmin,tmin_name,file_name)
#     output(RHU_base,df_RHU,RHU_name,file_name)
#     output(pre_base,df_pre,pre_name,file_name)
#     output(SSH_base,df_SSH,SSH_name,file_name)

""" 合并数据(2017年所有) """

# path = r'E:\单年\*.txt'
# path_6 = "E:\单年\*\*.txt"
# output_path = r'E:\2017-2020'
# files=gb.glob(path)
# files_6 = gb.glob(path_6)
# # 按变量名分组文件路径
# grouped_files = defaultdict(list)
# for p in files:
#     # 提取变量名（假设变量名在文件路径中的下划线之间）
#     variable = p.split('_')[-2]  # 倒数第二个元素是变量名
#     grouped_files[variable].append(p)
# # 打印分组后的文件路径
# for variable, paths in grouped_files.items():
#     print(f"{variable}:")
#     df_all = pd.DataFrame()
#     for path in paths:
#         df = pd.read_csv(path,index_col=0)
#         df_all = pd.concat([df_all,df])
#         df_all['台站编号'] = df_all['台站编号'].astype(str)
#     for f6 in files_6:
#         folder_name = f6.split('\\')
#         if folder_name[-1] == 'WIN_S_2mi_Avg_2017.txt':
#             continue
#         if variable in f6:
#             df6 = pd.read_csv(f6,index_col=0)
#             df6['台站编号'] = df6['台站编号'].astype(str)
#             df6 = df6.merge(df_all,on = '台站编号',how='left')
#             #填补缺失的列
#             df6.columns = df6.columns.str.replace(r'^(D\d+)\.0$', r'\1', regex=True)
#             existing_columns = df6.columns
#             day = int(existing_columns[-1].split('D')[-1])
#             required_columns = [f'D{i}' for i in range(1, day+1)]
#             missing_columns = [col for col in required_columns if col not in existing_columns]
#             for col in missing_columns:
#                 position = required_columns.index(col)+4
#                 df6.insert(position,col,np.nan)
#             folder = output_path + os.sep + folder_name[2]
#             if os.path.exists(folder):
#                 pass
#             else:
#                 os.makedirs(folder)
#             df6.to_csv(folder + os.sep + folder_name[-1])
#             print(folder_name[2])

""" 全国气象台站2018 """

# path = r'E:\stations\全国气象台站数据2018\*TEM_MIn*.txt'
# output_path = r'E:\2017-2020'
# files = gb.glob(path)
# # 按变量名分组文件路径
# grouped_files = defaultdict(list)
# for p in files:
#     # 提取变量名（假设变量名在文件路径中的下划线之间）
#     variable = p.split('\\')[-1].split('_')[0]
#     grouped_files[variable].append(p)
# # 打印分组后的文件路径
# for variable, paths in grouped_files.items():
#     print(f"{variable}:")
#     folder_name = [os.path.split(name)[-1] for name in paths][0]
#     df_all = pd.DataFrame()
#     for path in paths:
#         print(path)
#         df = pd.read_csv(path,header=1)   #,delim_whitespace=True
#
#         # 将行首的全角空格删除
#         df.iloc[:, 0] = df.iloc[:, 0].str.replace(r'^\u3000', '', regex=True)
#         #删除行首的多余空格，仅保留一个空格
#         df.iloc[:, 0] = df.iloc[:, 0].str.replace(r'^\s', '', regex=True)
#         # 将数据按空格拆分成多个列
#         df_split = df.iloc[:, 0].str.split(r' ', expand=True)
#         #筛选出没有站名只有站点但顶格的数据
#         d = df_split[df_split.iloc[:, 5] != '2018']
#         if not d.empty:
#             d.loc[:, d.columns[1:]] = d.iloc[:, :-1].values
#             for index,values in d.iterrows():
#                 df_split.loc[index] = values
#
#         # 确保列名称正确
#         columns_name = df.columns[0].split(' ')
#         df_split.columns = columns_name
#         df_split = df_split.set_index('Station_ID_C', drop=False)
#
#         # 筛选不是以字母开头的行
#         df_filter = df_split[~df_split.index.str.match(r'^[a-zA-Z]')]
#         df_filter.index = [i for i in range(0, len(df_filter))]
#         # 合并数据
#         df_all = pd.concat([df_all, df_filter])
#
#     # 重命名列为 Pandas 期望的名称
#     df_all.rename(columns={'Year': 'year', 'Mon': 'month', 'Day': 'day'}, inplace=True)
#     df_all['DATE'] = pd.to_datetime(df_all[['year', 'month', 'day']])
#     df_all['yearofday'] = df_all['DATE'].dt.dayofyear
#     df_all.drop(columns=['DATE','year', 'month','day'], inplace=True)   #获取每年第几天的数据
#
#     df_infor = df_all[['Station_ID_C', 'Lat', 'Lon', 'Alti']]
#     df_infor = df_infor.drop_duplicates(subset='Station_ID_C')
#     df_infor = df_infor.dropna(subset=['Station_ID_C'])
#
#     df_var = df_all.iloc[:,[0,1,-2,-1]]
#     df_var = df_var.dropna(thresh=df_var.shape[1] - 3 + 1)    ##df中如果有一行只有第一列有值，其余都为nan，删去这一行
#
#     df1 = df_var.set_index(['Station_Name', 'Station_ID_C','yearofday'])
#     df1 = df1[~df1.index.duplicated(keep='first')]     #保留重复的第一个数据（原始数据出现了两个相同的日期）
#     startswith_str = df1.columns[0][0]    #获取变量值列的第一个字母
#     df2 = df1.unstack(level='yearofday')
#     df2 = df2.reset_index()
#     #将多层索引平面化
#     df2.columns = ['_'.join(map(str, col)) if isinstance(col, tuple) else col for col in df2.columns]
#     #找到站台号对应的经纬度
#     df2.rename(columns={'Station_ID_C_': 'Station_ID_C'}, inplace=True)
#     df2 = df2.merge(df_infor[['Station_ID_C', 'Lat', 'Lon', 'Alti']], on='Station_ID_C', how='left')
#
#     # 将列移动到前面
#     lat_lon_alti = df2[['Lat', 'Lon', 'Alti']]
#     df2.drop(['Lat', 'Lon', 'Alti'], axis=1, inplace=True)
#     df2.insert(2,  'Lon', lat_lon_alti['Lon'])
#     df2.insert(3, 'Lat', lat_lon_alti['Lat'])
#     df2.insert(4,'Alti', lat_lon_alti['Alti'])
#     # 创建一个新列名列表
#
#     new_columns = []
#     for column in df2.columns:
#         if column.startswith(startswith_str):
#             split_day = column.split("_")[-1]
#             new_name = 'D' + str(split_day)
#         else:
#             new_name = column  # 如果列名不以'T'开头，则保持原样
#         new_columns.append(new_name)
#     new_columns[:5] = ['台站名', '台站编号', '经度', '纬度', '海拔']
#     # 使用新列名列表来重命名df2的列
#     df2.columns = new_columns
#     df_base = df2.iloc[:,:5]
#     df_end = df2.drop(columns='台站名')
#     #输出文件
#     base_folder = output_path + os.sep + 'base_data'
#     if os.path.exists(base_folder):
#         pass
#     else:
#         os.makedirs(base_folder)
#     df_base.to_csv(base_folder + os.sep + folder_name)
#     df_end.to_csv(output_path + os.sep + folder_name)
#     print(output_path + os.sep + folder_name)

""" 全国气象台站2019 """

# def deal_data(var1, var_name1):
#     df_var1 = var1.reset_index()
#
#     df_var1 = df_var1.merge(df_infor[['Station_ID_C', 'Lat', 'Lon', 'Alti']], on='Station_ID_C', how='left')
#
#     # 将列移动到前面
#     lat_lon_alti = df_var1[['Lat', 'Lon', 'Alti']]
#     df_var1.drop(['Lat', 'Lon', 'Alti'], axis=1, inplace=True)
#     df_var1.insert(1, 'Lon', lat_lon_alti['Lon'])
#     df_var1.insert(2, 'Lat', lat_lon_alti['Lat'])
#     df_var1.insert(3, 'Alti', lat_lon_alti['Alti'])
#
#     # 创建一个新列名列表
#     new_columns = []
#     for column in df_var1.columns:
#         if re.match(r'^\d', str(column)):
#             new_name = 'D' + str(column)
#         else:
#             new_name = column  # 如果列名不以'T'开头，则保持原样
#         new_columns.append(new_name)
#     new_columns[:4] = ['台站编号', '经度', '纬度', '海拔']
#     df_var1.columns = new_columns       # 使用新列名列表来重命名df2的列
#
#     # 输出数据
#     base_folder = output_path + os.sep + '2019' + os.sep + f'{variable}'
#     if os.path.exists(base_folder):
#         pass
#     else:
#         os.makedirs(base_folder)
#     df_var1.to_csv(base_folder + os.sep + f'{var_name1}.csv')
#
#     return print(base_folder + os.sep + f'{var_name1}.csv')
#
# output_path = r'E:\2017-2020'
# path = rf'E:\stations\全国气象台站数据2019\*WIN*'
# paths = gb.glob(path)
# grouped_files = defaultdict(list)
# for p in paths:
#     # 提取变量名（假设变量名在文件路径中的下划线之间）
#     variable = p.split('\\')[-1].split('-')[1]
#     grouped_files[variable].append(p)
#
# # 打印分组后的文件路径
# for variable, files in grouped_files.items():
#     print(f"{variable}:")
#     folder_name = [os.path.split(name)[-1] for name in files][0]
#     df_all = pd.DataFrame()
#     for f in files:
#         df = pd.read_csv(f,delim_whitespace=True,header=None)   #,delim_whitespace=True
#
#         df_index1 = df.iloc[0, :]
#         # 检查是否包含英文字符
#         contains_english = df_index1.apply(lambda x: bool(re.search(r'[a-zA-Z]', str(x))))
#         if contains_english.all():
#             print("包含数据介绍的列名")
#         else:
#             print('不包含数据介绍的列名')
#             if variable == 'EVP':
#                 df.columns = ['Station_ID_C','Lat','Lon','Alti','year','month','day','EVP_min','EVP_max','EVP_min_flag','EVP_max_flag']
#             if variable == 'GST':
#                 df.columns = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'GST_0cm_avg','GST_0cm_max',
#                               'GST_0cm_min', 'GST_0cm_avg_flag', 'GST_0cm_max_flag', 'GST_0cm_min_flag']
#             if variable == 'PRE':
#                 df.columns = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'PRE_Time_2008','PRE_Time_0820',
#                               'PRE_Time_2020', 'PRE_Time_2008_flag', 'PRE_Time_0820_flag', 'PRE_Time_2020_flag']
#             if variable == 'PRS':
#                 df.columns = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'PRS_Avg', 'PRS_Max',
#                               'PRS_Min', 'PRS_Avg_flag','PRS_Max_flag', 'PRS_Min_flag']
#             if variable == 'TEM':
#                 df.columns = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'TEM_Avg', 'TEM_Max',
#                               'TEM_Min', 'TEM_Avg_flag', 'TEM_Max_flag','TEM_Min_flag']
#             if variable == 'SSD':
#                 df.columns = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'SSH','SSH_flag']
#             elif variable == 'RHU':    #########
#                 df.columns = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'RHU_Avg','RHU_Min','RHU_Avg_flag','RHU_Min_flag']
#                 df['Lat'] = (df['Lat'] / 100).round(2)
#                 df['Lon'] = (df['Lon'] / 100).round(2)
#                 df['Alti'] = (df['Alti'] / 10).round(1)
#             elif variable == 'WIN':   #####
#                 df.columns = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'WIN_S_10mi_Avg', 'WIN_S_Max',
#                               'WIN_D_S_Max', 'WIN_S_Inst_Max', 'WIN_D_INST_Max','WIN_S_10mi_Avg_flag', 'WIN_S_Max_flag',
#                               'WIN_D_S_Max_flag', 'WIN_S_Inst_Max_flag', 'WIN_D_INST_Max_flag']
#                 df['Lat'] = (df['Lat'] / 100).round(2)
#                 df['Lon'] = (df['Lon'] / 100).round(2)
#                 df['Alti'] = (df['Alti'] / 10).round(1)
#                 df['WIN_S_10mi_Avg'] = (df['WIN_S_10mi_Avg'] / 10).round(1)
#                 df['WIN_S_Max'] = (df['WIN_S_Max'] / 10).round(1)
#                 df['WIN_S_Inst_Max'] = (df['WIN_S_Inst_Max'] / 10).round(1)
#
#             #修正数据
#             else:
#                 df['Lat'] = (df['Lat'] / 100).round(2)
#                 df['Lon'] = (df['Lon'] / 100).round(2)
#                 df['Alti'] =( df['Alti']/10).round(1)
#                 col_len = len(df.columns[7:])/2
#                 for var in df.columns[7:int(-col_len)]:
#                     for index,value in enumerate(df[var]):
#                         if value == 32766:
#                             df.loc[index, var] = value
#                         else:
#                             df.loc[index, var] = value/10
#
#
#
#             df_all = pd.concat([df_all,df])
#
#     #获取一年中的天数据
#     df_all['DATE'] = pd.to_datetime(df_all[['year', 'month', 'day']])
#     df_all['yearofday'] = df_all['DATE'].dt.dayofyear
#     df_all.drop(columns=['DATE', 'year', 'month', 'day'], inplace=True)
#
#     #获取台站号的唯一值
#     df_infor = df_all[['Station_ID_C', 'Lat', 'Lon', 'Alti']]
#     df_infor = df_infor.drop_duplicates(subset='Station_ID_C')
#     df_infor = df_infor.dropna(subset=['Station_ID_C'])
#
#     df_var = df_all.iloc[:, [0] + list(range(4, df_all.shape[1]))]
#     df1 = df_var.set_index(['Station_ID_C','yearofday'])
#     df2 = df1.unstack(level='yearofday')    #转换成需要的格式
#     for col in df1.columns:
#         var1 = df2[col]
#         deal_data(var1,col)
#     print(f'{variable} is ok')

""" 全国气象数据2020 """

# def deal_data(var1, var_name1):
#     df_var1 = var1.reset_index()
#
#     df_var1 = df_var1.merge(df_infor[['Station_ID_C', 'Lat', 'Lon', 'Alti']], on='Station_ID_C', how='left')
#
#     # 将列移动到前面
#     lat_lon_alti = df_var1[['Lat', 'Lon', 'Alti']]
#     df_var1.drop(['Lat', 'Lon', 'Alti'], axis=1, inplace=True)
#     df_var1.insert(1, 'Lon', lat_lon_alti['Lon'])
#     df_var1.insert(2, 'Lat', lat_lon_alti['Lat'])
#     df_var1.insert(3, 'Alti', lat_lon_alti['Alti'])
#
#     # 创建一个新列名列表
#     new_columns = []
#     for column in df_var1.columns:
#         if re.match(r'^\d', str(column)):
#             new_name = 'D' + str(column)
#         else:
#             new_name = column  # 如果列名不以'T'开头，则保持原样
#         new_columns.append(new_name)
#     new_columns[:4] = ['台站编号', '经度', '纬度', '海拔']
#     df_var1.columns = new_columns       # 使用新列名列表来重命名df2的列
#
#     # 输出数据
#     base_folder = output_path + os.sep + '2020' + os.sep + f'{variable}'
#     if os.path.exists(base_folder):
#         pass
#     else:
#         os.makedirs(base_folder)
#     df_var1.to_csv(base_folder + os.sep + f'{var_name1}.csv')
#
#     return print(base_folder + os.sep + f'{var_name1}.csv')
#
# output_path = r'E:\2017-2020'
# path = rf'E:\stations\全国气象台站数据2020\*PRE*'
# paths = gb.glob(path)
# grouped_files = defaultdict(list)
# for p in paths:
#     # 提取变量名（假设变量名在文件路径中的下划线之间）
#     variable = p.split('\\')[-1].split('-')[1]
#     grouped_files[variable].append(p)
#
# # 打印分组后的文件路径
# for variable, files in grouped_files.items():
#     print(f"{variable}:")
#     folder_name = [os.path.split(name)[-1] for name in files][0]
#     df_all = pd.DataFrame()
#     count = 0
#     for f in files:
#         count += 1
#         if count <= 3:   #3月份后数据包含数据介绍的列名
#             df = pd.read_csv(f,delim_whitespace=True,header=None)   #,delim_whitespace=True
#             print('不包含数据介绍的列名')
#         else:
#             df=pd.read_csv(f,delim_whitespace=True,header=None,skiprows=1)
#             print('包含数据介绍的列名')
#         len1 = len(df.columns[7:])
#         if variable == 'EVP':
#             list1 = ['Station_ID_C','Lat','Lon','Alti','year','month','day','EVP_min','EVP_max','EVP_min_flag','EVP_max_flag']
#             if len(df.columns) != len(list1):
#                 df.columns = list1[:int(-len1)]
#             else:
#                 df.columns = list1
#         if variable == 'GST':
#             list1 = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'GST_0cm_avg','GST_0cm_max',
#                           'GST_0cm_min', 'GST_0cm_avg_flag', 'GST_0cm_max_flag', 'GST_0cm_min_flag']
#             if len(df.columns) != len(list1):
#                 df.columns = list1[:int(-len1)]
#             else:
#                 df.columns = list1
#         if variable == 'PRE':
#             list1 = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'PRE_Time_2008','PRE_Time_0820',
#                           'PRE_Time_2020', 'PRE_Time_2008_flag', 'PRE_Time_0820_flag', 'PRE_Time_2020_flag']
#             if len(df.columns) != len(list1):
#                 df.columns = list1[:int(-len1)]
#             else:
#                 df.columns = list1
#         if variable == 'PRS':
#             list1 = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'PRS_Avg', 'PRS_Max',
#                           'PRS_Min', 'PRS_Avg_flag','PRS_Max_flag', 'PRS_Min_flag']
#             if len(df.columns) != len(list1):
#                 df.columns = list1[:int(-len1)]
#             else:
#                 df.columns = list1
#         if variable == 'TEM':
#             list1 = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'TEM_Avg', 'TEM_Max',
#                           'TEM_Min', 'TEM_Avg_flag', 'TEM_Max_flag','TEM_Min_flag']
#             if len(df.columns) != len(list1):
#                 df_c = df[df.isna().any(axis=1)]
#                 for index, arr in df_c.iterrows():
#                     # print(index)
#                     nan_count = arr.isna().sum()
#                     split_arr = len(str(arr[6]).split('.')[0])
#                     if split_arr > 2:
#                         if nan_count == 1:
#                             arr[6] = str(arr[6]).split('.')[0][:-6]
#                             arr[9] = arr[8]
#                             arr[8] = arr[7]
#                             arr[7] = 999999
#                         elif nan_count == 2:
#                             if split_arr >10:
#                                 arr[6] = str(arr[6]).split('.')[0][:-12]
#                                 arr[7] = arr[8] = 999999
#                             else:
#                                 arr[6] = str(arr[6]).split('.')[0][:-6]
#                                 arr[7] = arr[9] = 999999
#                                 arr[8] = str(arr[8]).rsplit('.',1)[0][:-6]
#                         elif nan_count == 3:
#                             arr[6] = str(arr[6]).split('.')[0][:-18]
#                             arr[7] = arr[8]=arr[9]=999999
#                     else:
#                         if nan_count == 1:
#                             split_7 = len(str(arr[7]).split('.')[0])
#                             if split_7 > 6:
#                                 arr[7] = str(arr[7]).split('.')[0][:-12]
#                                 arr[8] = arr[9] = 999999
#                             else:
#                                 arr[8] = arr[9] = 999999
#                     df.loc[index] = arr
#                 df.fillna(999999, inplace=True)
#                 df.columns = list1[:int(-len1)]
#             else:
#                 df.columns = list1
#         if variable == 'SSD':
#             list1 = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'SSH','SSH_flag']
#             if len(df.columns) != len(list1):
#                 df.columns = list1[:int(-len1)]
#             else:
#                 df.columns = list1
#         elif variable == 'RHU':    #########
#             list1 = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'RHU_Avg','RHU_Min','RHU_Avg_flag','RHU_Min_flag']
#             if len(df.columns) != len(list1):
#                 df_c = df[df.isna().any(axis=1)]
#                 for index, arr in df_c.iterrows():
#                     nan_count = arr.isna().sum()
#                     split_arr = len(str(arr[6]).split('.')[0])
#                     if split_arr > 2:
#                         if nan_count == 1:
#                             arr[6] = str(arr[6]).split('.')[0][:-6]
#                             arr[8] = arr[7]
#                             arr[7] = 999999
#                         elif nan_count == 2:
#                             arr[6] = str(arr[6]).split('.')[0][:-12]
#                             arr[7] = 999999
#                             arr[8] = 999999
#                     else:
#                         if nan_count == 1:
#                             split_7 = len(str(arr[7]).split('.')[0])
#                             if split_7 > 6:
#                                 arr[7] = str(arr[7]).split('.')[0][:-6]
#                             else:
#                                 pass
#                             arr[8] = 999999
#                         elif nan_count == 2:
#                             arr[7] = 999999
#                             arr[8] = 999999
#                     df.loc[index] = arr
#                 df.fillna(999999, inplace=True)
#                 df.columns = list1[:int(-len1)]
#             else:
#                 df.columns = list1
#                 df['Lat'] = (df['Lat'] / 100).round(2)
#                 df['Lon'] = (df['Lon'] / 100).round(2)
#                 df['Alti'] = (df['Alti'] / 10).round(1)
#         elif variable == 'WIN':    #####
#             list1 = ['Station_ID_C', 'Lat', 'Lon', 'Alti', 'year', 'month', 'day', 'WIN_S_10mi_Avg', 'WIN_S_Max',
#                           'WIN_D_S_Max', 'WIN_S_Inst_Max', 'WIN_D_INST_Max','WIN_S_10mi_Avg_flag', 'WIN_S_Max_flag',
#                           'WIN_D_S_Max_flag', 'WIN_S_Inst_Max_flag', 'WIN_D_INST_Max_flag']
#             if len(df.columns) != len(list1):
#                 df_c = df[df.isna().any(axis=1)]
#                 for index, arr in df_c.iterrows():
#                     # print(index)
#                     nan_count = arr.isna().sum()
#                     split_arr8 = len(str(arr[8]).split('.')[0])
#                     split_arr9 = len(str(arr[9]).split('.')[0])
#                     if nan_count == 2:
#                         if split_arr8 == split_arr9 ==12:
#                             arr[8]=arr[9]=arr[10]=arr[11]=999999
#                         elif split_arr8 < 4 and split_arr9 < 4:
#                             arr[10]=arr[11]=999999
#                     elif nan_count == 1:
#                         if split_arr8 == 12:
#                             arr[11] = arr[10]
#                             arr[10] = arr[9]
#                             arr[9] = 999999
#                             arr[8] = 999999
#                         else:
#                             arr[11] = 999999
#                 df.fillna(999999, inplace=True)
#                 df.columns = list1[:int(-len1)]
#             else:
#                 df.columns = list1
#                 df['Lat'] = (df['Lat'] / 100).round(2)
#                 df['Lon'] = (df['Lon'] / 100).round(2)
#                 df['Alti'] = (df['Alti'] / 10).round(1)
#                 df['WIN_S_10mi_Avg'] = (df['WIN_S_10mi_Avg'] / 10).round(1)
#                 df['WIN_S_Max'] = (df['WIN_S_Max'] / 10).round(1)
#                 df['WIN_S_Inst_Max'] = (df['WIN_S_Inst_Max'] / 10).round(1)
#
#             #修正数据
#         else:
#             col_len = len(df.columns[7:]) / 2
#             if count <= 3:
#                 df['Lat'] = (df['Lat'] / 100).round(2)
#                 df['Lon'] = (df['Lon'] / 100).round(2)
#                 df['Alti'] =( df['Alti']/10).round(1)
#                 for var in df.columns[7:int(-col_len)]:   #对变量中的无效值不进行计算
#                     for index,value in enumerate(df[var]):
#                         if value == 32766:
#                             df.loc[index, var] = value
#                         else:
#                             df.loc[index, var] = value/10
#             else:
#                 pass
#         df_all = pd.concat([df_all,df])
#
#     #获取一年中的天数据
#     df_all['DATE'] = pd.to_datetime(df_all[['year', 'month', 'day']])
#     df_all['yearofday'] = df_all['DATE'].dt.dayofyear
#     df_all.drop(columns=['DATE', 'year', 'month', 'day'], inplace=True)
#
#     #获取台站号的唯一值
#     df_infor = df_all[['Station_ID_C', 'Lat', 'Lon', 'Alti']]
#     df_infor = df_infor.drop_duplicates(subset='Station_ID_C')
#     df_infor = df_infor.dropna(subset=['Station_ID_C'])
#
#     df_var = df_all.iloc[:, [0] + list(range(4, df_all.shape[1]))]
#     df1 = df_var.set_index(['Station_ID_C','yearofday'])
#     df2 = df1.unstack(level='yearofday')    #转换成需要的格式
#     for col in df1.columns:
#         var1 = df2[col]
#         deal_data(var1,col)
#     print(f'{variable} is ok')

""" 全国气象数据2021 """

# path = r'E:\stations\全国气象台站数据2021\*.txt'
# output_path = r'E:\2017-2020'
# paths = gb.glob(path)
# for p in paths:
#     varname = re.split(r'[\\_.]',p)[-3]
#     year = re.split(r'[\\_.]',p)[-2]
#
#     df = pd.read_csv(p, sep='\t+', header=None)
#     col_len = len(df.columns[4:])
#     col_name = [f'D{i}' for i in range(1,col_len+1)]
#     base_name = ['台站编号','纬度','经度','海拔']
#     df.columns = base_name + col_name
#
#     col_lat = df.pop('纬度')
#     col_lon = df.pop('经度')
#     df.insert(1,'经度',col_lon)
#     df.insert(2,'纬度',col_lat)
#     df.iloc[:, 0] = df.iloc[:, 0].apply(lambda x: x[-5:])
#     # 将数据转换为字符串类型
#     df.iloc[:, -1] = df.iloc[:, -1].astype(str)
#
#
#     # 处理无效值
#     def clean_value(value):
#         try:
#             return float(value[:-1])  # 提取引号前的部分并转换为浮点数
#         except ValueError:
#             return np.nan
#     df.iloc[:, -1] = df.iloc[:, -1].apply(clean_value)
#
#     base_folder = output_path + os.sep + '2021'
#     if os.path.exists(base_folder):
#         pass
#     else:
#         os.makedirs(base_folder)
#     df.to_csv(base_folder + os.sep + f'{varname}_{year}.csv')
#
#     print(base_folder + os.sep + f'{varname}_{year}.csv')

""" 全国气象数据2022 """

# def deal_data(var1, var_name1):
#     df_var1 = var1.reset_index()
#
#     df_var1 = df_var1.merge(df_infor[['区站号', '纬度', '经度']], on='区站号', how='left')
#
#     # 将列移动到前面
#     lat_lon_alti = df_var1[['纬度', '经度']]
#     df_var1.drop(['纬度', '经度'], axis=1, inplace=True)
#     df_var1.insert(1, '经度', lat_lon_alti['经度'])
#     df_var1.insert(2, '纬度', lat_lon_alti['纬度'])
#
#     # 创建一个新列名列表
#     new_columns = []
#     for column in df_var1.columns:
#         if re.match(r'^\d', str(column)):
#             new_name = 'D' + str(column)
#         else:
#             new_name = column  # 如果列名不以'T'开头，则保持原样
#         new_columns.append(new_name)
#     new_columns[:3] = ['台站编号', '经度', '纬度']
#     df_var1.columns = new_columns       # 使用新列名列表来重命名df2的列
#
#     # 输出数据
#     base_folder = output_path + os.sep + '2022'
#     if os.path.exists(base_folder):
#         pass
#     else:
#         os.makedirs(base_folder)
#     df_var1.to_csv(base_folder + os.sep + f'{var_name1}_2022.csv')
#
#     return print(base_folder + os.sep + f'{var_name1}_2022.csv')
#
# path = r'E:\stations\全国气象台站数据2022\*.txt'
# output_path = r'E:\2017-2020'
# paths = gb.glob(path)
# df_all = pd.DataFrame()
# for p in paths:
#     year = re.split(r'[\\]',p)[-1]
#
#     df = pd.read_csv(p, sep=',',encoding='gbk')
#     df_all = pd.concat([df_all,df])
#
# df_all.rename(columns={'年': 'year', '月': 'month', '日': 'day'}, inplace=True)
# df_all['DATE'] = pd.to_datetime(df_all[['year', 'month', 'day']])
# df_all['yearofday'] = df_all['DATE'].dt.dayofyear
# df_all.drop(columns=['站名','省名','DATE', 'year', 'month', 'day'], inplace=True)
#
# #获取台站号的唯一值
# df_infor = df_all[['区站号', '纬度', '经度']]
# df_infor = df_infor.drop_duplicates(subset='区站号')
# df_infor = df_infor.dropna(subset=['区站号'])
#
# df_var = df_all.iloc[:, [0] + list(range(3, df_all.shape[1]))]
# df1 = df_var.set_index(['区站号','yearofday'])
# df2 = df1.unstack(level='yearofday')    #转换成需要的格式
# for col in df1.columns:
#     var1 = df2[col]
#     deal_data(var1,col)



































