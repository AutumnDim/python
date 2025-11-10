"""
ghcnd 数据处理
"""
import os
import re
import calendar
import datetime
import shutil
import glob as gb
import numpy as np
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool, Manager

def out_date_by_day(year, day):
    '''
    根据输入的年份和天数计算对应的日期
    '''
    first_day = datetime.datetime(year, 1, 1)
    add_day = datetime.timedelta(days=day - 1)
    return datetime.datetime.strftime(first_day + add_day, "%Y-%m-%d")


"""" 1，在原始ghcnd数据中提取ghcnd全部站点信息  """
# base_info_all = []
# for year in range(1980,2021):
#     path = rf"C:\任务\实习\atm\data\station\Station_data\PRCP1\PRCP_{year}.csv"
#     df = pd.read_csv(path,index_col=0)
#
#     # 提取全部站点信息
#     base_info = df.iloc[:,:4]
#     base_info_all.append(base_info)
#
# base_info_all = pd.concat(base_info_all)
# base_info_all = base_info_all.drop_duplicates(subset=['台站编号'], keep='first')
# base_info_all = base_info_all.drop_duplicates(subset=['经度','纬度'], keep='first')  # 剔除重复值
#
# # 全部站点信息数据输出
# # base_info_all.to_csv(r"C:\任务\实习\atm\data\station\Station_data\unique_stations_ghcnd(1980-2020).csv")
#
# # 剔除中国站点信息
# base_info_foreign = base_info_all[~base_info_all['台站编号'].str.startswith('CH')]
# base_info_foreign.to_csv(r"C:\任务\实习\atm\data\station\Station_data\shp\unique_stations_foreign(1980-2020).csv")

# # 获取国外站点数据
# for year in range(1980,2021):
#     path = rf"C:\任务\实习\atm\data\station\Station_data\PRCP1\PRCP_{year}.csv"
#
#     df1 = pd.read_csv(path,index_col=0)
#
#     stations = base_info_foreign['台站编号']
#     df3 = df1[df1['台站编号'].isin(stations)]
#
#     # 国外站点数据输出
#     df3.to_csv(rf'C:\任务\实习\atm\data\station\Station_data\PRCP(foreign)\PRCP_{year}.csv')

""" 2，查看国外站点数据缺失情况，缺失值低于60%的站点剔除，不参与插补 """
# GHCND = pd.DataFrame()
# for y in range(1980, 2023):
#     path_GHCND = rf'C:\任务\实习\atm\data\station\Station_data\PRCP(foreign)\PRCP_{y}.csv'
#     df_ghcnd = pd.read_csv(path_GHCND, dtype={'台站编号': str})
#     df_ghcnd.drop('Unnamed: 0', axis=1, inplace=True)
#     print(len(df_ghcnd))
#
#     df_ghcnd = df_ghcnd.set_index('台站编号')
#     df_ghcnd = df_ghcnd.iloc[:, 3:]
#
#     data_col = df_ghcnd.columns
#     days = data_col.map(lambda x: int(re.search(r'D(\d+)', x).group(1)) if re.search(r'D(\d+)', x) else None)
#     date = pd.Series(days).apply(lambda x: out_date_by_day(int(y), x))
#     df_ghcnd.columns = list(date)
#     GHCND = pd.concat([GHCND, df_ghcnd.T])
#     print(y)
# GHCND.index = pd.to_datetime(GHCND.index)
#
# # 筛选缺失值低于60%的站点数据
# sta_nan = GHCND.isnull().sum()
# percentiles = sta_nan/len(GHCND)*100
# percentiles.to_csv(r'C:\任务\实习\atm\data\station\Station_data\多年数据缺失情况60%_GHCND_foreign.csv')

""" 3,从ghcnd官网下载的全球dly数据筛选出指定的国外站点数据 """

# path_sta = r"C:\任务\实习\atm\data\station\Station_data\shp\unique_stations_foreign(1980-2020).csv"
# path_files = r'C:\Users\2024\Downloads\ghcnd_all.tar\ghcnd_all\ghcnd_all\*'
# output_dir = r'C:\气象数据插值(ghcnd+国内)'
#
# df_sta = pd.read_csv(path_sta, index_col=0)
# df_files = gb.glob(path_files)
#
# files = [file for file in df_files if any(stations in file for stations in df_sta['台站编号']) ]
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)
#
# for file in files:
#
#     file_name = os.path.basename(file)
#     target_file = os.path.join(output_dir, file_name)
#     shutil.copy(file, target_file)
#
# print(f"已将 {len(files)} 个文件复制到 {output_dir}")

"""" 4，从下载的数据中提取降水数据（通用：也可提取气温数据）"""

# def process_file(file):
#     data = []
#
#     # 每次处理一个文件
#     with open(file, 'r') as f:
#         lines = f.readlines()  # 一次读取所有行
#         prcp_lines = [line for line in lines if line[17:21] == 'TAVG']  # 筛选PRCP行
#
#         for line in prcp_lines:
#             station_id = line[:11].strip()
#             year = int(line[11:15].strip())
#             month = int(line[15:17].strip())
#
#             # 只处理1980年及以后的数据
#             if year >= 1980 and year <= 2022:
#                 # 获取该月的天数
#                 days_in_month = calendar.monthrange(year, month)[1]  # 返回该月的天数
#
#                 # 提取该月的降水量，步长8
#                 values = np.array([int(line[21 + i * 8:26 + i * 8].strip()) for i in range(days_in_month)])
#                 days = np.arange(1, days_in_month + 1)
#
#                 # 将 year, month, day 组合为日期字符串
#                 dates = [f"{year}-{month:02d}-{day:02d}" for day in days]
#
#                 # 组合为一列，直接添加到数据中
#                 data.extend(zip([station_id] * days_in_month, dates, values))
#
#     # 返回处理结果
#     return data
#
# def main(files):
#     manager = Manager()
#     all_data = manager.list()
#
#     with Pool(processes=None) as pool:
#
#         for result in tqdm(pool.imap(process_file, files), total=len(files), desc='Processing files'):
#             all_data.extend(result)
#
#     # 将所有结果转换为 DataFrame
#     df = pd.DataFrame(list(all_data), columns=['StationID', 'Date', 'TAVG'])
#     df_wide = df.pivot(index='StationID', columns='Date', values='TAVG')
#     return df_wide
#
# if __name__ == "__main__":
#     path_sta = r"C:\任务\实习\atm\data\station\Station_data\shp\unique_stations_foreign(1980-2020).csv"
#     path = r'C:\气象数据插值(ghcnd+国内)\dly\*'
#     output_file = r'C:\气象数据插值(ghcnd+国内)\ghcnd_tavg(1980-2022).csv'
#
#     files = gb.glob(path)
#     df_result = main(files)
#     df_result.T.to_csv(output_file)




