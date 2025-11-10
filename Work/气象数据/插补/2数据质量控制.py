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
import qa.qa_prcp as qa
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from datetime import timedelta
import utils.util_dates as utld
from db.station_data import station_data,TMAX_FLAG,PRCP_FLAG,TMIN_FLAG,TAVG
from concurrent.futures import ProcessPoolExecutor, as_completed
from db.station_data import LON, LAT, STN_ID, YEAR, DATE, MONTH, TMIN, TMAX, PRCP, YMD, DAY, YDAY
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

def csvtolist(df2,tmax_path,tmin_path,prcp_path,tavg_path,year):
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
    prcp = pd.read_csv(prcp_path, dtype={'台站编号': str}, index_col=1).iloc[:, 4:]
    tavg = pd.read_csv(tavg_path, dtype={'台站编号': str}, index_col=1).iloc[:, 4:]

    prcp.columns = prcp.columns.str.replace('D', '')
    tavg.columns = tavg.columns.str.replace('D', '')

    if len(tavg.columns) != len(prcp.columns):

        tavg_last_col = int(tavg.columns[-1].split('.')[0])
        prcp_last_col = int(prcp.columns[-1].split('.')[0])

        if prcp_last_col > tavg_last_col:

            missing_columns = [f'{day}' for day in range(tavg_last_col + 1, prcp_last_col + 1)]
            for col in missing_columns:
                tavg[col] = np.nan
        elif prcp_last_col < tavg_last_col:

            missing_columns = [f'{day}' for day in range(tavg_last_col + 1, prcp_last_col + 1)]
            for col in missing_columns:
                prcp[col] = np.nan
        else:
            print(f'{year} is no change')                   # 填充不足的日期

    day = prcp.columns
    list1 = [f'{mon}_{days}' for mon, days in map(lambda d: yd_neg1(year, int(float(d))), day)]

    prcp.columns = list1
    tavg.columns = list1                                    # 日期转换

    # 筛选符合条件的台站数据
    prcp = pd.concat([df2, prcp], axis=1, join='inner')

    tavg = tavg[tavg.index.isin(prcp.index)]
    tavg = pd.concat([df2, tavg], axis=1, join='inner')
    sta = set(prcp.index) - set(tavg.index)
    info = prcp.iloc[:, :3][prcp.index.isin(sta)]
    tavg = pd.concat([tavg, info])                         # 填充不足的站点(tavg)

    # 获取年份及其对应数据值
    station = prcp.index
    for s in station:
        prcp_ax1 = prcp.loc[s]
        tavg_ax1 = tavg.loc[s]
        head_col = prcp_ax1[:2]

        for md in prcp_ax1.index[3:]:
            m, d = md.split('_')
            lis.append((s, head_col[1], head_col[0], year, int(m), int(d),
                        prcp_ax1[md], tavg_ax1[md], datetime(int(year), int(m), int(d))))

    return lis

def read(year):

    # 输入数据
    tmax_path = rf"C:\降水归档\降水数据插值(国内)_气象局\0降水数据\格式整理数据\降水量\precipitation_time_2020_{year}.txt"
    tmin_path = rf"C:\降水归档\降水数据插值(国内)_气象局\0降水数据\格式整理数据\降水量\precipitation_time_2020_{year}.txt"
    prcp_path = rf"C:\降水归档\降水数据插值(国内)_气象局\0降水数据\格式整理数据\降水量\precipitation_time_2020_{year}.txt" # 降水量数据
    tavg_path = rf"C:\降水归档\降水数据插值(国内)_气象局\0降水数据\格式整理数据\平均气温\TEM_Tavg_{year}.txt"               # 平均气温数据
    nan_path = r"C:\降水归档\降水数据插值(国内)_气象局\1数据缺失值概况\多年缺失值占比.csv"                                  # 缺失值数据
    path = r"C:\降水归档\降水数据插值(国内)_气象局\0降水数据\格式整理数据\unique_station_1980_2022.txt"                    # 经纬度数据

    # 筛选符合条件的站点
    nan = pd.read_csv(nan_path, index_col=0)
    df = pd.read_csv(path, index_col=0, dtype={'台站编号':str})

    if len(str(nan.index[0])) == 11 :                   # 11为国外站点，5为国内站点
        nan = nan[nan < 60].dropna().index.astype(str)
    else:
        nan = nan[nan < 80].dropna().index.astype(str)
        df = df[df['台站编号'].str.startswith('5')]

    df = df.drop_duplicates(subset=['经度', '纬度'], keep='first')  # 去除重复站点和自动站点
    df2 = df.set_index('台站编号')
    df2 = df2[df2.index.isin(nan)]

    return csvtolist(df2, tmax_path, tmin_path, prcp_path, tavg_path, year)

def output(all_df,output_path, name=None):
    """
    :param all_df: 所有年份质量控制码结果
    :param name: 变量名
    :return: 多年共同站点的质量控制最终结果
    """
    datetime_index = pd.to_datetime(all_df.index, format="%Y-%m-%d")
    all_df.index = datetime_index

    df_bin = all_df.applymap(lambda x: bin(x)[2:].zfill(10))
    # df_bin.to_csv(output_path + os.sep + "QC_prcp_bin.csv")   # 二进制输出
    # all_df.to_csv(output_path + os.sep + "QC_prcp_all.csv")   # 十进制输出

    groupby = all_df.groupby(all_df.index.year)
    for year, group in groupby:

        print(f"Year: {year}")
        df_bin_year = group.T

        file_path = os.path.join(output_path, name)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        else:
            pass
        # df_bin_year.to_csv(file_path + os.sep + f"{name}_{year}.csv")

    return df_bin

def main():

    spatial_prcp = {'缺失值': 0, '频率分布中尾部与其余值异常分离': 0,
                    '不可能的值': 0, '不同年份之间的重复值': 0, '同一年中不同月份的重复值': 0,
                    '20个以下的非零值': 0, '不同年份之间相同月份的重复值': 0, '未被任何相邻值证实': 0}

    output_path = r"C:\降水归档\降水数据插值(国内)_气象局\2数据质量控制\插值前质量判断"

    years = range(1980, 1981)
    list2 = []

    DEBUG = True

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
    # stations = ['55591']
    prcp_all = pd.DataFrame()

    # 数据质量判断
    days = stn_da.days
    days1 = stn_da.days1
    for s in tqdm(stations, desc="Processing stations"):

        stn = stns[stns[STN_ID] == s][0]    # 返回台站，纬度，经度数据
        stn_obs = stn_da.load_all_stn_obs(np.array(s), set_flagged_nan=False)  # 返回最小、最大气温、降水、平均气温

        df_prcp = qa.checks_qa(stn, stn_da, stn_obs[PRCP], stn_obs[TAVG], days, days1, spatial_prcp)  # 质量判断
        prcp_qa = qa.Convert_to_decimal(df_prcp)
        prcp_all[s] = prcp_qa.iloc[:, -1]           # 更新数据

    df_bin = output(prcp_all, output_path, "prcp")


    """ 未通过质量判断的情况 """

    condition_prcp = ['缺失值检查','不同年份之间的重复值','同一年中不同月份的重复值','不同年份之间相同月份的重复值','超世界记录检查',
                      '条纹检查','频率检查','间隙检查','气候异常值检查',
                        '空间一致性检查']
    unique_value = np.unique(df_bin.astype(str).values)
    df_error = pd.DataFrame()
    for value in unique_value:
        if str(0) in value:
            position = value.find('0')
            print(f"判断条件为:{condition_prcp[position]}")
            condition = df_bin[df_bin == value]
            number_sta = condition.count()
            number_all  = number_sta.sum()
            print({f'{condition_prcp[position]}':number_all})
            df_error[condition_prcp[position]] = [number_all]
    # 未通过判断的数量
    count_all = 0
    for l in df_error.columns:
        count_all += df_error[l].values[0]
    percentage = count_all/(df_bin.shape[0]*df_bin.shape[1])*100
    df_error['未通过判断的总数量'] = [count_all]
    df_error['未通过判断的数量占比'] = [percentage]

    print(f'未通过判断的总数量为{count_all}')
    print(f'未通过判断的数量占比为{percentage}')

    df_error.to_excel(output_path + os.sep +f'未通过质量判断情况.xlsx')

    print("质量控制完成！")

if __name__ == '__main__':
    main()








