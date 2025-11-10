import pandas as pd
import glob as gb
from tqdm import tqdm
import geopandas as gpd
import matplotlib.pyplot as plt
from rasterio.plot import show
from datetime import timedelta
import numpy as np
import datetime
from sklearn.metrics import r2_score
import rasterio
import os
import re
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

def out_date_by_day(year, day):
    '''
    根据输入的年份和天数计算对应的日期
    '''
    first_day = datetime.datetime(year, 1, 1)
    add_day = datetime.timedelta(days=day - 1)
    return datetime.datetime.strftime(first_day + add_day, "%Y-%m-%d")

""" CERN台站数据提取(每八天的数据) """

# output_path = r'C:\气象数据插值(国内+国外)\空间插值效果分析'
#
# base_info_all = []
# df_all = []
# years = range(1998,2021)
# for year in years:
#     path = rf"C:\任务\实习\atm\data\CERN\CERN_new\PRCP\PRCP_{year}.csv"
#     df = pd.read_csv(path,index_col = 0)
#
#     # 经纬度信息
#     base_info = df.iloc[:,:4]
#     base_info_all.append(base_info)
#
#     # 数据信息
#     df2 = df.iloc[:,5:]
#     days = []
#     for day in df2.columns:
#         days.append(out_date_by_day(year,int(day[1:])))
#     df2.columns = days
#     df2.index = base_info['sss000']
#     df_all.append(df2.T)
#
#     print(year)
# base_info_all = pd.concat(base_info_all)
# df_all = pd.concat(df_all)
#
# base_info_all = base_info_all.drop_duplicates(subset=['sss000'],keep='first')
# base_info_all = base_info_all.drop_duplicates(subset=[' longitude', ' latitude'],keep='first')
#
# base_info_all.to_csv(output_path + os.sep + f'unique_stations_cern_{min(years)}_{max(years)}.csv')
#
# df_all.index = pd.to_datetime(df_all.index)
# # 计算降水8天的总和
# df_all1 = df_all.resample('8D').sum()
# df_all1[df_all.isna().resample('8D').sum() > 0] = np.nan
# df_all1.to_csv(output_path + os.sep + f'prcp_{min(years)}_{max(years)}_8D.csv')

""" CPC/GPM等(8天数据) """

# output_path = r'C:\降水归档\降水数据插值(国内+国外)\空间插值效果分析\MSWEP'
# if not os.path.exists(output_path):
#     os.makedirs(output_path)
# else:
#     pass
#
# df_all = []
# years = range(1980,2021)
# for y in years:
#     path_cpc = rf"C:\MSWEP\MSWEP\PRCP_{y}.csv"
#     df_cpc = pd.read_csv(path_cpc,index_col = 0)
#     df_cpc=df_cpc.dropna(axis=1,how='all')
# #     df_cpc = df_cpc*24
#
#     days = []
#     if df_cpc.index[0] == 0:
#         df_cpc.index = [i+1 for i in df_cpc.index]
#     for day in df_cpc.index:
#         days.append(out_date_by_day(y,int(day)))
#     df_cpc.index = days
#     df_cpc.index = pd.to_datetime(df_cpc.index)
#
#     df_cpc[(df_cpc < 0) | (df_cpc > 10000)] = np.nan
#     df_cpc[df_cpc == -0.0] = 0.0
#
#     # 计算降水8天的总和
#     cpc = df_cpc.resample('8D').sum()
#     cpc[df_cpc.isna().resample('8D').sum() > 0] = np.nan
#     df_all.append(cpc)
#     print(y)
# df_all = pd.concat(df_all)
# df_all.to_csv(output_path + os.sep + f'prcp_{min(years)}_{max(years)}_8D.csv')

""" 空间数据提取 """

# path_shp = r"F:\lyr\数据缺失值站比(带经纬度版_80%)_prj1.shp"
# path_tif = r'D:\LIN\prj_PRCP_1980002.flt.tif'
# output_path = r'F:\lyr\prcp_spatial'
#
# shapefile_data = gpd.read_file(path_shp)
# dataset1 = rasterio.open(path_tif)
#
# tif_crs = dataset1.crs
# shapefile_data = shapefile_data.to_crs(tif_crs)         # 统一坐标系统
# x_y = list(zip(shapefile_data.geometry.x, shapefile_data.geometry.y))   # 获取x,y值
# points = list(zip(shapefile_data['经度'],shapefile_data['纬度']))        # 获取经纬度坐标
#
# # 可视化
# # fig, ax = plt.subplots(figsize=(10, 10))
# # shapefile_data.plot(ax=ax, color='orangered', edgecolor='black', alpha=0.5,markersize=2)
# # show(dataset1, ax=ax, cmap='viridis')
# # ax.set_title('Shapefile and Raster Layer')
# # plt.show(block=True)
#
# for y in range(1980, 2023):
#     files = gb.glob(rf"D:\LIN\prj_PRCP_{y}*.tif")
#     len(files)
#     data_all = []
#     for p in tqdm(files, total=len(files), desc='processing station'):
#         data = []
#         date = re.split(r'[_.\\]', p)[-3][4:]
#
#         dataset = rasterio.open(p)
#         sample_data = dataset.sample(x_y)       # 批量获取值
#         for point, value in zip(points, sample_data):
#             data.append({
#                 '经度': point[0],
#                 '纬度': point[1],
#                 f'{date}': value[0]
#             })
#
#         df_value = pd.DataFrame(data)
#         data_all.append(df_value)
#
#     final_df = pd.concat(data_all, ignore_index=True)
#     final_df1 = final_df.copy()
#     final_df1 = final_df1.groupby(['经度', '纬度'], as_index=False).agg('first')
#
#     final_df1[final_df1 == -9999.0] = np.nan
#     final_df1.loc[:, final_df1.columns[2:]] = final_df1.loc[:, final_df1.columns[2:]].clip(lower=0)
#
#     print('ok')
#
#     final_df1 = final_df1.merge(shapefile_data, on=['经度', '纬度'], how='left')
#     final_df1 = final_df1.drop(['经度', '纬度'], axis=1).iloc[:,:-3]
#     final_df1 = final_df1.set_index(final_df1.columns[-1])
#     final_df1.to_csv(output_path + os.sep + f'PRCP_{y}.csv')
# print('done')

""" 空间数据评价分析 """

def calculate_stats(y_true, y_pred):
    """
    计算结果评估指数
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    correlation = y_true.corr(y_pred)
    r2 = r2_score(y_true, y_pred)

    return rmse, mae, correlation, r2

def read(var):
    path_cpc = gb.glob(rf"C:\降水归档\降水数据插值(国内+国外)\空间插值效果分析\{var}(8天数据)\*8D.csv")[0] #(8天数据)
    df_cpc = pd.read_csv(path_cpc,index_col=0)
    df_cpc.index = pd.to_datetime(df_cpc.index)
    grouped = df_cpc.groupby(df_cpc.index.year)
    return grouped

output_path = r'C:\降水归档\降水数据插值(国内+国外)\空间插值效果分析\result'

# vars = ['CPC','ERA5','MSWEP','YANGKUN','origin']
# vars = ['origin']
# for var in vars:
#
#     # 输出文件夹
#     output_path_file = output_path + os.sep + f'{var}'
#     if not os.path.exists(output_path_file):
#         os.makedirs(output_path_file)
#     else:
#         pass
#
#     grouped = read(var)             # 输入对比的产品数据
#     df_all_year = pd.DataFrame()
#     years = []
#     for y,group in tqdm(grouped, total=len(grouped), desc='processing year'):
#
#         years.append(y)
#         path_inter = rf"C:\降水归档\降水数据插值(国内+国外)\空间插值效果分析\插值提取(8天数据)\prcp_spatial\PRCP_{y}.csv"
#         df_inter = pd.read_csv(path_inter,index_col=0).T
#         df_inter.columns = df_inter.columns.astype(str)
#
#         # 转换行索引日期
#         start_date = pd.to_datetime(f'{y}-01-01')
#         dates = [start_date + timedelta(days=(int(n) - 1) * 8) for n in df_inter.index]
#         df_inter.index = dates
#
#         df_all = pd.DataFrame()
#         for col in df_inter.columns:
#             if col in group.columns:
#
#                 # 剔除缺失值
#                 merge = pd.concat([df_inter[col],group[col]],axis=1).dropna(axis=0)
#
#                 # 评价指标计算
#                 if not merge.empty:
#                     rmse, mae, correlation, r2 = calculate_stats(merge.iloc[:,1],merge.iloc[:,0])
#
#                     result_df = pd.DataFrame({
#                         'RMSE': [rmse],
#                         'MAE': [mae],
#                         'Correlation': [correlation],
#                         'R2': [r2]
#                     })
#                     result_df.index = [col]
#                     df_all = pd.concat([df_all, result_df])
#
#         df_all_year = pd.concat([df_all_year,df_all.mean()],axis=1)
#         df_all.to_csv(output_path_file + os.sep + f'compare_{y}.csv')
#
#     df_all_year.columns = years
#     df_all_year.to_csv(output_path + os.sep + rf'{var}_R2_mean.csv')
#     print(f'{var} is ok' )
# print('处理完成')


""" 提取单个站点分析结果 """
# vars = ['CPC','ERA5','MSWEP','YANGKUN','origin']
# df_all = pd.DataFrame()
# for var in vars:
#     paths = gb.glob(rf"C:\降水归档\降水数据插值(国内+国外)\空间插值效果分析\result\{var}\compare_*.csv")
#     df_year = pd.DataFrame(columns=[f'R2_{var}'])
#     for path in paths:
#         year = re.split(r'[_.]',path)[-2]
#         df = pd.read_csv(path,index_col=0)
#         value = df.loc[55248,'R2']
#         df_year.loc[year,f'R2_{var}'] = value
#     df_all = pd.concat([df_all,df_year],axis=1)
# df_all.to_excel(r'C:\降水归档\降水数据插值(国内+国外)\空间插值效果分析\result\R方_改则.xlsx')








