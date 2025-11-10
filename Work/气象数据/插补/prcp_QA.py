# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 15:13:02 2024

@author: 25153
"""

import gc
import os
import warnings
import numpy as np
import qa.qa_prcp
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from datetime import timedelta
import utils.util_dates as utld
from db.station_data import station_data,TMAX_FLAG,PRCP_FLAG,TMIN_FLAG,TAVG
from concurrent.futures import ProcessPoolExecutor, as_completed
from db.station_data import LON, LAT, STN_ID, YEAR, DATE, MONTH, TMIN, TMAX, PRCP, YMD, DAY, YDAY#,station_data,TMAX_FLAG,PRCP_FLAG,TMIN_FLAG,TAVG
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
    将所用数据处理成可用形式，获取年份和对应数据值

    参数
    ----------
    tmax_path : str
        最高温数据路径
    tmin_path : str
        最低温数据路径
    prcp_path : str
        降水数据路径
    year : int
        数据年份

    返回值
    -------
    lis : 列表
        返回一个可以直接作为station_data类第一个参数的列表

    """
    lis = []
    prcp = pd.read_csv(prcp_path,dtype={'台站编号': str},index_col=1).iloc[:,4:]
    tavg = pd.read_csv(tavg_path,dtype={'台站编号': str},index_col=1).iloc[:,4:]

    #获取数据的日期
    prcp.columns = prcp.columns.str.replace('D', '')
    tavg.columns = tavg.columns.str.replace('D', '')

    # 填充不足的日期(tavg)
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
            print(f'{year} is no change')

    day = prcp.columns

    list1 = [f'{mon}_{days}' for mon, days in map(lambda d: yd_neg1(year, int(float(d))), day)]

    prcp.columns = list1
    tavg.columns = list1

    # 筛选符合条件的台站数据
    prcp = pd.concat([df2,prcp],axis=1,join='inner')

    # 填充不足的站点(tavg)
    tavg = tavg[tavg.index.isin(prcp.index)]
    tavg = pd.concat([df2,tavg],axis=1,join='inner')
    sta = set(prcp.index) - set(tavg.index)
    info = prcp.iloc[:,:3][prcp.index.isin(sta)]
    tavg = pd.concat([tavg,info])

    station = prcp.index
    # stations = ['52941']
    for s in station:
        prcp_ax1 = prcp.loc[s]
        tavg_ax1 = tavg.loc[s]
        head_col = prcp_ax1[:2]
        #获取年份及其对应数据值
        for md in prcp_ax1.index[3:]:
            m,d= md.split('_')
            lis.append((s, head_col[1], head_col[0], year, int(m), int(d),
                        prcp_ax1[md], tavg_ax1[md],datetime(int(year), int(m), int(d))))

    return lis

def read(year,prcp_path1,tavg_path,df2):

    tmax_path = prcp_path1 + os.sep + f"prcp_{year}.csv"
    tmin_path = prcp_path1 + os.sep + f"prcp_{year}.csv"
    prcp_path = prcp_path1 + os.sep + f"prcp_{year}.csv"
    tavg_path = tavg_path + os.sep + f"TAVG_{year}.csv"

    return csvtolist(df2,tmax_path, tmin_path, prcp_path, tavg_path, year)

def output(all_df,name=None):
    """
    :param all_df: 所有年份质量控制码结果
    :param name: 变量名
    :return: 多年共同站点的质量控制最终结果
    """
    datetime_index = pd.to_datetime(all_df.index,format = "%Y-%m-%d")
    all_df.index=datetime_index
    df2 = all_df.applymap(lambda x: bin(x)[2:].zfill(10))
    df2.to_csv(rf"D:\实习\test1\插值后质量判断2\QC_prcp_bin.csv")
    all_df.to_csv(rf"D:\实习\test1\插值后质量判断2\QC_prcp_all.csv")
    groupby =all_df.groupby(all_df.index.year)
    for year, group in groupby:
        print(f"Year: {year}")
        df2 = group.T
        df2.to_csv(rf"D:\实习\test1\插值后质量判断2\{name}\{name}_{year}.csv")

def process_station1(s, stns, stn_da, qa, spatial_max, spatial_min):
    """
    s:处理的站点
    tmin_qa/tmax_qa:每个站点的处理结果
    """
    stn = stns[stns[STN_ID] == s][0]
    stn_obs = stn_da.load_all_stn_obs(np.array([stn[STN_ID]]), set_flagged_nan=False)  # 返回最小、最大气温、降水、平均气温
    df_tmin, df_tmax = qa.qa_temp.checks_qa(stn, stn_da, stn_obs[TMIN], stn_obs[TMAX], stn_da.days, stn_da.days1, spatial_max, spatial_min)  #返回质量控制结果
    tmin_qa, tmax_qa = qa.qa_temp.Convert_to_decimal(df_tmin, df_tmax)    #返回处理后的十进制质量控制码
    return s, tmin_qa.iloc[:, -1], tmax_qa.iloc[:, -1]

