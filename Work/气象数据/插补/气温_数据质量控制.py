# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:13:02 2024
@author: 25153

Data quality control
"""

import gc
import os
import warnings
import numpy as np
import qa1.qa_temp as qa
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from datetime import timedelta
import utils.util_dates as utld
from db2.station_data import station_data,TMAX_FLAG,PRCP_FLAG,TMIN_FLAG,TAVG
from concurrent.futures import ProcessPoolExecutor, as_completed
from db2.station_data import LON, LAT, STN_ID, YEAR, DATE, MONTH, TMIN, TMAX, PRCP, YMD, DAY, YDAY
warnings.filterwarnings("ignore")

QA_OK = 1
QA_MISSING = 2
QA_NAUGHT = 3
DUP = 25
QA_DUP_YEAR = 4
QA_DUP_MONTH = 5
QA_DUP_YEAR_MONTH = 6
QA_DUP_WITHIN_MONTH = 7
QA_IMPOSS_VALUE = 8
QA_STREAK = 9
QA_GAP = 10
QA_INTERNAL_INCONSIST = 11
QA_LAGRANGE_INCONSIST = 12
QA_SPIKE_DIP = 13
QA_MEGA_INCONSIST = 14
QA_CLIM_OUTLIER = 15
QA_SPATIAL_REGRESS = 16
QA_SPATIAL_CORROB = 17
QA_MEGA_INCONSIST = 18
# QA_OK = 1
# QA_MISSING = '缺失值'
# QA_NAUGHT = '错误的0值'
# DUP = 25
# QA_DUP_YEAR = '年份之间的重复值'
# QA_DUP_MONTH = '不同年份之间相同月份的重复值'
# QA_DUP_YEAR_MONTH = '同一年中不同月份的重复值'
# QA_DUP_WITHIN_MONTH = '一个月内日最高气温与日最低气温相等天数超过十天'
# QA_IMPOSS_VALUE = '超过世界记录范围的值'
# QA_STREAK = '20个以上的连续值'
# QA_GAP = '频率分布中尾部与其余值异常分离'
# QA_INTERNAL_INCONSIST = '同一观测日或相邻观测日内部不一致'
# QA_LAGRANGE_INCONSIST = '最高气温与最暖的最低气温相差超过40度'
# QA_SPIKE_DIP = '相邻几天内的异常波动'
# QA_MEGA_INCONSIST = '日最低气温高于最热最高气温或最高气温低于最冷最低气温'
# QA_CLIM_OUTLIER = 15
# QA_SPATIAL_REGRESS = '观测点与相邻站点显著不同(空间回归)'
# QA_SPATIAL_CORROB = '未被任何相邻值证实'
# QA_MEGA_INCONSIST = '日最低气温高于最热最高气温或最高气温低于最冷最低气温'

#World records for daily Tmax and Tmin in degrees C
TMAX_RECORD = 57.7
TMIN_RECORD = -89.4

#Constants for spatial regression/collab checks
NGH_RADIUS = 75.0
NGH_CORR = 0.8
NGH_RESID_CUTOFF = 8.0
NGH_RESID_STD_CUTOFF = 4.0
ANOMALY_CUTOFF = 10.0
MIN_DAYS_MTH_WINDOW = 40
MIN_NGHS = 3
MAX_NGHS = 7
NGH_STNS_ID = "NGH_STNS_ID"
NGH_STNS_MASK_OVERLAP = "NGH_STNS_MASK_OVERLAP"
NGH_STNS_WGHTS = "NGH_STNS_WGHTS"
NGH_STNS_MODEL = "NGH_STNS_MODEL"
NGH_STNS_OBS = "NGH_STNS_OBS"

#Constants for building Tmin/Tmax normals
MONTHS = np.arange(1, 13)
#改1:
DATES_366 = utld.get_date_array(datetime(2004, 1, 1), datetime(2004, 12, 31))
# DATES_366 = np.array(pd.date_range(datetime(2004, 1, 1), datetime(2004, 12, 31)))
DATES_365 = utld.get_date_array(datetime(2003, 1, 1), datetime(2003, 12, 31))
# DATES_365 = np.array(pd.date_range(datetime(2003, 1, 1), datetime(2003, 12, 31)))
MIN_NORM_VALUES = 100


def yd_neg1(year, day_of_year):
    """
    将年份和一年中的天数转换为月份和日期
    """
    date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
    return [date.month, date.day]

def csvtolist(df2, tmax_path, tmin_path, prcp_path, tavg_path, year):
    """
    将所用数据处理成可用形式

    df2: dataframe 筛选后的经纬度数据
    tmax_path : str 最高温数据路径
    tmin_path : str 最低温数据路径
    prcp_path : str 降水数据路径
    year : int 数据年份

    return
    lis : 列表 返回一个可以直接作为station_data类第一个参数的列表
    列表内容格式：(台站编号, 经度, 纬度, 年, 月, 日,降水量, 平均气温,datetime(int(year), int(m), int(d)))
    """

    # 数据预处理
    lis = []
    tmax = pd.read_csv(tmax_path, dtype={'台站编号': str}, index_col=1).iloc[:, 4:]
    tmin = pd.read_csv(tmin_path, dtype={'台站编号': str}, index_col=1).iloc[:, 4:]

    tmax.columns = tmax.columns.str.replace('D', '')
    tmin.columns = tmin.columns.str.replace('D', '')

    if len(tmax.columns) != len(tmin.columns):

        tmin_last_col = int(tmin.columns[-1].split('.')[0])
        tmax_last_col = int(tmax.columns[-1].split('.')[0])

        if tmax_last_col > tmin_last_col:

            missing_columns = [f'{day}' for day in range(tmin_last_col + 1, tmax_last_col + 1)]
            for col in missing_columns:
                tmin[col] = np.nan
        elif tmax_last_col < tmin_last_col:

            missing_columns = [f'{day}' for day in range(tmin_last_col + 1, tmax_last_col + 1)]
            for col in missing_columns:
                tmax[col] = np.nan
        else:
            print(f'{year} is no change')                   # 填充不足的日期

    day = tmax.columns
    list1 = [f'{mon}_{days}' for mon, days in map(lambda d: yd_neg1(year, int(float(d))), day)]

    tmax.columns = list1
    tmin.columns = list1                                    # 日期转换

    # 筛选符合条件的台站数据
    tmax = pd.concat([df2, tmax], axis=1, join='inner')

    tmin = tmin[tmin.index.isin(tmax.index)]
    tmin = pd.concat([df2, tmin], axis=1, join='inner')
    sta = set(tmax.index) - set(tmin.index)
    info = tmax.iloc[:, :3][tmax.index.isin(sta)]
    tmin = pd.concat([tmin, info])                         # 填充不足的站点(tavg)

    # 获取年份及其对应数据值
    station = tmax.index
    for s in station:
        tmax_ax1 = tmax.loc[s]
        tmin_ax1 = tmin.loc[s]
        head_col = tmax_ax1[:2]

        for md in tmax_ax1.index[3:]:
            m, d = md.split('_')
            lis.append((s, head_col[1], head_col[0], year, int(m), int(d),
                        tmin_ax1[md], tmax_ax1[md], datetime(int(year), int(m), int(d))))

    return lis

def read(year):

    # 输入数据
    tmax_path = rf"E:\所实习\气温原始数据\平均后日最高气温\TEM_max_{year}.txt"
    tmin_path = rf"E:\所实习\气温原始数据\平均后日最低气温\TEM_min_{year}.txt"
    prcp_path = rf"C:\降水归档\降水数据插值(国内)_气象局\0降水数据\格式整理数据\降水量\precipitation_time_2020_{year}.txt" # 降水量数据
    tavg_path = rf"C:\降水归档\降水数据插值(国内)_气象局\0降水数据\格式整理数据\平均气温\TEM_Tavg_{year}.txt"               # 平均气温数据
    nan_min = r"E:\所实习\气温数据插值处理\1数据缺失值概况\日平均最低温度\多年缺失值占比.csv"                                  # 缺失值数据
    nan_max = r"E:\所实习\气温数据插值处理\1数据缺失值概况\日平均最高温度\多年缺失值占比.csv"                                  # 缺失值数据
    path_max = r"E:\所实习\气温原始数据\unique_station_TMAX_1980_2022.txt"                    # 经纬度数据
    path_min = r"E:\所实习\气温原始数据\unique_station_TMIN_1980_2022.txt"

    # 筛选符合条件的站点
    nan_min1 = pd.read_csv(nan_min, index_col=0)
    nan_max1 = pd.read_csv(nan_max, index_col=0)   #缺失值占比

    df_max = pd.read_csv(path_max, index_col=0, dtype={'台站编号':str}).set_index('台站编号')
    df_min = pd.read_csv(path_min, index_col=0, dtype={'台站编号':str}).set_index('台站编号')
    common_sta = pd.concat([df_max, df_min],axis=1, join='inner').iloc[:,:3]                #筛选出共有的台站

    if len(str(nan_min1.index[0])) == 11 :                   # 11为国外站点，5为国内站点
        nan_min1 = nan_min1[nan_min1 < 60].dropna().index.astype(str)
        nan_max1 = nan_max1[nan_max1 < 60].dropna().index.astype(str)
        common_index = nan_min1.intersection(nan_max1)
    else:
        nan_min1 = nan_min1[nan_min1 < 80].dropna().index.astype(str)
        nan_max1 = nan_max1[nan_max1 < 80].dropna().index.astype(str)
        common_index = nan_min1.intersection(nan_max1)

    df2 = common_sta.loc[common_index]

    return csvtolist(df2, tmax_path, tmin_path, prcp_path, tavg_path, year)

def output(all_df,output_path,max_len, name=None):
    """
    :param all_df: 所有年份质量控制码结果
    :param name: 变量名
    :return: 多年共同站点的质量控制最终结果
    """
    datetime_index = pd.to_datetime(all_df.index, format="%Y-%m-%d")
    all_df.index = datetime_index

    df_bin = all_df.applymap(lambda x: bin(x)[2:].zfill(max_len))
    df_bin.to_csv(output_path + os.sep + f"QC_{name}_bin.csv")   # 二进制输出
    all_df.to_csv(output_path + os.sep + f"QC_{name}_all.csv")   # 十进制输出

    groupby = all_df.groupby(all_df.index.year)
    for year, group in groupby:

        print(f"Year: {year}")
        df_bin_year = group.T

        file_path = os.path.join(output_path, name)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        else:
            pass
        df_bin_year.to_csv(file_path + os.sep + f"{name}_{year}.csv")

    return df_bin

def main():

    spatial_min = {'缺失值':0,'错误的0值':0,'年份之间的重复值':0,'不同年份之间相同月份的重复值':0,
                    '同一年中不同月份的重复值':0,'一个月内日最高气温与日最低气温相等天数超过十天':0,'超过世界记录范围的值':0,
                    '20个以上的连续值':0,'频率分布中尾部与其余值异常分离':0,'同一观测日或相邻观测日内部不一致':0,
                    '最高气温与最暖的最低气温相差超过40度':0,'相邻几天内的异常波动':0,'日最低气温高于最热最高气温或最高气温低于最冷最低气温':0,
                    '观测点与相邻站点显著不同(空间回归)':0,'未被任何相邻值证实':0,'z值大于6个标准差':0}
    spatial_max = {'缺失值':0,'错误的0值':0,'年份之间的重复值':0,'不同年份之间相同月份的重复值':0,
                    '同一年中不同月份的重复值':0,'一个月内日最高气温与日最低气温相等天数超过十天':0,'超过世界记录范围的值':0,
                    '20个以上的连续值':0,'频率分布中尾部与其余值异常分离':0,'同一观测日或相邻观测日内部不一致':0,
                    '最高气温与最暖的最低气温相差超过40度':0,'相邻几天内的异常波动':0,'日最低气温高于最热最高气温或最高气温低于最冷最低气温':0,
                    '观测点与相邻站点显著不同(空间回归)':0,'未被任何相邻值证实':0,'z值大于6个标准差':0}

    output_path_tmin = rf"E:\所实习\气温数据插值处理\2数据质量控制\日平均最低温度\插值前质量控制"
    output_path_tmax = rf"E:\所实习\气温数据插值处理\2数据质量控制\日平均最高温度\插值前质量控制"

    years = range(1980, 2023)
    list2 = []

    DEBUG = False

    if DEBUG:
        for year in years:
            li = read(year)
            list2.extend(li)
    else:

        with ProcessPoolExecutor() as executor:
            future_to_year = {executor.submit(read, year): year for year in years}  # read函数中输入路径

            for future in tqdm(as_completed(future_to_year), total=len(future_to_year), desc="Processing years"):
                year = future_to_year[future]
                try:
                    li = future.result()
                    list2.extend(li)
                    del li
                    gc.collect()
                except Exception as e:
                    print(f"Error processing year {year}: {e}")
                    import traceback
                    traceback.print_exc()

    stn_da = station_data(list2, datetime(min(years), 1, 1), datetime(max(years), 12, 31))
    del list2
    gc.collect()
    print('ok')
    stns = np.unique(stn_da.load_stns())
    stations = set(stns[STN_ID])
    # stations = ['54853']
    tmin_all = pd.DataFrame()
    tmax_all = pd.DataFrame()

    # 数据质量判断
    days = stn_da.days
    days1 = stn_da.days1
    for s in tqdm(stations, desc="Processing stations"):

        stn = stns[stns[STN_ID] == s][0]    # 返回台站，纬度，经度数据
        stn_obs = stn_da.load_all_stn_obs(np.array(s), set_flagged_nan=False)  # 返回最小、最大气温、降水、平均气温

        df_tmin,df_tmax = qa.checks_qa(stn, stn_da, stn_obs[TMIN], stn_obs[TMAX], days, days1, spatial_min)  # 质量判断
        tmin_qa, tmax_qa,tmin_max_len,tmax_max_len = qa.Convert_to_decimal(df_tmin,df_tmax)
        tmin_all[s] = tmin_qa.iloc[:, -1]           # 更新数据
        tmax_all[s] = tmax_qa.iloc[:, -1]           # 更新数据

    tmin_bin = output(tmin_all, output_path_tmin,tmin_max_len, "tmin")
    tmax_bin = output(tmax_all, output_path_tmax, tmax_max_len,"tmax")


    """ 未通过质量判断的情况 """

    condition_prcp = ['缺失值','错误的0值','年份之间的重复值','不同年份之间相同月份的重复值',
                    '同一年中不同月份的重复值','一个月内日最高气温与日最低气温相等天数超过十天','超过世界记录范围的值',
                    '20个以上的连续值','频率分布中尾部与其余值异常分离','同一观测日或相邻观测日内部不一致',
                    '最高气温与最暖的最低气温相差超过40度','相邻几天内的异常波动','日最低气温高于最热最高气温或最高气温低于最冷最低气温',
                    '观测点与相邻站点显著不同(空间回归)','未被任何相邻值证实','z值大于6个标准差']
    var = ['tmin', 'tmax']
    bin_data = {
        "tmin": tmin_bin,
        "tmax": tmax_bin
    }

    # Store the output paths in a dictionary for easy access
    output_paths = {
        "tmin": output_path_tmin,
        "tmax": output_path_tmax
    }

    for v in var:
        current_bin = bin_data[v]  # 获取 tmin_bin 或 tmax_bin
        unique_value = np.unique(current_bin.astype(str).values)

        df_error = pd.DataFrame()
        for value in unique_value:
            if str(0) in value:
                position = value.find('0')
                print(f"判断条件为:{condition_prcp[position]}")
                condition = current_bin[current_bin == value]
                number_sta = condition.count()
                number_all = number_sta.sum()
                print({f'{condition_prcp[position]}': number_all})
                df_error[condition_prcp[position]] = [number_all]

        # 计算未通过判断的数量和百分比
        count_all = df_error.sum(axis=1).values[0]
        percentage = count_all / current_bin.size * 100

        df_error['未通过判断的总数量'] = [count_all]
        df_error['未通过判断的数量占比'] = [percentage]

        print(v)
        print(f'未通过判断的总数量为{count_all}')
        print(f'未通过判断的数量占比为{percentage}%')

        output_dir = output_paths[v]
        os.makedirs(output_dir, exist_ok=True)
        df_error.to_excel(os.path.join(output_dir, '未通过质量判断情况.xlsx'))

    print("质量控制完成！\n")

if __name__ == '__main__':
    main()








