# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 08:41:49 2024

@author: 25153
"""

import os
import warnings
import numpy as np
from tqdm import tqdm
import pandas as pd
import dask
import dask.dataframe as dd
from dask.distributed import Client
from dask.diagnostics import ProgressBar
from datetime import datetime
from datetime import timedelta
from alive_progress import alive_bar
import utils.util_dates as utld
from concurrent.futures import ProcessPoolExecutor, as_completed
from db1.station_data import LON, LAT, STN_ID, YEAR, DATE, MONTH, TMIN, TMAX, PRCP, YMD, DAY, YDAY#,station_data,TMAX_FLAG,PRCP_FLAG,TMIN_FLAG,TAVG
from db1.station_data import station_data,TMAX_FLAG,PRCP_FLAG,TMIN_FLAG,TAVG
import qa1.qa_prcp
import qa1.qa_temp


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

def yd(year,month,day):
    """
    计算某一天是一年中的第几天

    参数
    ----------
    year : int
        年
    month : int
        月
    day : int
        日

    返回值
    -------
    int
        输入日期为一年中的第几天

    """
    if month==1:
        return day
    if month==2:
        return day+31
    l = 0
    for m in [1,3,5,7,8,10,12]:
        if month <= m:
            break
        l+=1
    if (year%4==0 and year%100!=0) or (year%400==0 and year%100==0):
        return l*31+(month-l-2)*30+29+day
    else:
        return l*31+(month-l-2)*30+28+day
    
def yd_neg1(year, day_of_year):
    """
    将年份和一年中的天数转换为月份和日期
    """
    date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
    return [date.month, date.day]

def yd_neg(year,day):
    """
    输入一个天数和年份，计算天数为几月几日

    参数
    ----------
    year : int
        天数所处年份
    day : int
        天数

    返回值
    -------
    list
        返回[月，日]列表

    """
    year = int(year)
    day = int(day)
    for m in range(1,13):
        if m in [1,3,5,7,8,10,12]:
            if day>31:
                day-=31
            else:
                return [m,day]
        elif m==2:
            if (year%4==0 and year%100!=0) or (year%400==0 and year%100==0):
                if day>29:
                    day-=29
                else:
                    return [m,day]
            else:
                if day>28:
                    day-=28
                else:
                    return [m,day]
        else:
            if day>30:
                day-=30
            else:
                return [m,day]
# 原
def csvtolist(tmax_path,tmin_path,prcp_path,tavg_path,year):
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
    # 新
    # tmax = pd.read_csv(tmax_path, dtype={"台站编号": str}).iloc[:,1:]
    # tmin = pd.read_csv(tmin_path, dtype={"台站编号": str}).iloc[:,1:]
    tmax = pd.read_csv(tmax_path).iloc[:500,1:]
    tmin = pd.read_csv(tmin_path).iloc[:500,1:]
    # prcp = pd.read_excel(prcp_path)
    # tavg = pd.read_excel(tavg_path)
    # print("read_ok")
    base_data = tmax[['台站编号','经度','纬度']]
    
    #获取数据的日期
    tmax.columns = tmax.columns.str.replace('D', '')
    tmin.columns = tmin.columns.str.replace('D', '')
    day = tmax.columns[4:]
    
    list = []
    for d in day:
        mon, days = yd_neg1(year, int(float(d)))
        list.append(f'{mon}_{days}')
    tmax.columns.values[4:] = list
    tmin.columns.values[4:] = list
    
    # 新
    station = set(tmax['台站编号']) & set(tmin['台站编号'])
    # station_id = '55591'
    # if int(station_id) in station:
    #     print(f"{station_id} 在 station 集合中")
    # else:
    #     print(f"{station_id} 不在 station 集合中")

    for s in station:
        tmax_ax1 = tmax[tmax['台站编号']==s]
        tmin_ax1 = tmin[tmin['台站编号']==s]
        head_col = tmax_ax1.iloc[0, :4]
        #获取年份及其对应数据值
        for md in tmax_ax1.columns[4:]:
            m,d= md.split('_')
            lis.append((head_col[0], head_col[2], head_col[1], year, int(m), int(d),
                        tmin_ax1[md].values[0], tmax_ax1[md].values[0],datetime(int(year), int(m), int(d))))
    return lis,station,base_data


#TODO
# ydic = {}
# # yb= {'1':3,'2':4}

def read(year):
    # tmax_path = rf"D:\数据\站点数据处理\其他气象数据\日最高气温\TEM_Max_{year}.txt"
    # tmin_path = rf"D:\数据\站点数据处理\其他气象数据\日最低气温\TEM_Min_{year}.txt"
    # 拟合后数据
    tmax_path = rf"E:\所实习\气温原始数据\平均后日最高气温\TEM_max_{year}.txt"
    tmin_path = rf"E:\所实习\气温原始数据\平均后日最低气温\TEM_min_{year}.txt"
    # tmax_path = rf"E:\气象data\气温原始数据\测试数据\日最高气温\TEM_Max_{year}.txt"
    # tmin_path = rf"E:\气象data\气温原始数据\测试数据\日最低气温\TEM_Min_{year}.txt"
    prcp_path = r""
    tavg_path = r""
    return csvtolist(tmax_path, tmin_path, prcp_path, tavg_path, year)

def yd(year, month, day):
    """计算一年中的第几天"""
    return datetime(year, month, day).timetuple().tm_yday

def create_date_array(start_date, end_date):
    """
    """
    # 定义字段名
    LON = u'经度'
    LAT = u'纬度'
    STN_ID = u'台站'
    YEAR = u'年'
    MONTH =  u'月'
    DAY = u'日'
    PRCP = u'降水量'
    TMIN = u'日最低气温'
    TMAX = u'日最高气温'
    YMD = u'年月日'
    DATE = u'日期'
    YDAY = u'年日'
    PRCP_FLAG = u'降水量标记'
    TMIN_FLAG = u'日最低气温标记'
    TMAX_FLAG = u'日最高气温标记'
    TAVG_FLAG = u'日最高气温标记'
    TAVG = u'平均气温'

    # 生成日期范围
    date_range = pd.date_range(start_date, end_date)
    
    # 准备各列数据
    dates = date_range.to_list()
    years = [d.year for d in dates]
    months = [d.month for d in dates]
    days = [d.day for d in dates]
    ymd_strings = [f'{y}-{m}-{d}' for y, m, d in zip(years, months, days)]
    ydays = [yd(y, m, d) for y, m, d in zip(years, months, days)]
    
    # 组合成结构化数组
    structured_array = np.array(
        list(zip(dates, years, months, days, ymd_strings, ydays)),
        dtype=[
            (DATE, datetime),
            (YEAR, np.uint16),
            (MONTH, np.uint8),
            (DAY, np.uint8),
            (YMD, 'U10'),
            (YDAY, np.uint16)
        ]
    )
    
    return structured_array


def output(all_df,name=None):
    """
    :param all_df: 所有年份质量控制码结果
    :param name: 变量名
    :return: 多年共同站点的质量控制最终结果
    """
    datetime_index = pd.to_datetime(all_df.index,format = "%Y-%m-%d")
    all_df.index=datetime_index
    groupby =all_df.groupby(all_df.index.year)
    for year, group in groupby:
        print(f"Year: {year}")
        df2 = group.T
        df2.to_excel(rf"E:\气象data\质量控制\十进制\{name}_{year}.xlsx")

def process_station(s, stns, stn_da, qa1, spatial_max, spatial_min):
    """
    s:处理的站点
    tmin_qa/tmax_qa:每个站点的处理结果
    """
    stn = stns[stns[STN_ID] == s][0]
    stn_obs = stn_da.load_all_stn_obs(np.array([stn[STN_ID]]), set_flagged_nan=False)  # 返回最小、最大气温、降水、平均气温
    df_tmin, df_tmax = qa1.qa_temp.checks_qa(stn, stn_da, stn_obs[TMIN], stn_obs[TMAX], stn_da.days, stn_da.days1, spatial_max, spatial_min)  #返回质量控制结果
    tmin_qa, tmax_qa = qa1.qa_temp.Convert_to_decimal(df_tmin, df_tmax)    #返回处理后的十进制质量控制码
    return s, tmin_qa.iloc[:, -1], tmax_qa.iloc[:, -1]

def date_year(year_list):
    all_dates = []

    for year in year_list:
        # 生成该年的所有日期（从 1月1日 到 12月31日）
        dates = pd.date_range(
            start=f"{year}-01-01",
            end=f"{year}-12-31",
            freq="D"  # 'D' 表示按天生成
        )
        all_dates.extend(dates)
    
    # 转换为字符串格式（可选）
    # all_dates_str = [d.strftime("%Y-%m-%d") for d in all_dates]
    all_dates_str = [f"{d.year}-{d.month}-{d.day}" for d in all_dates]
    sorted_dates = sorted(all_dates_str,key=lambda x: datetime.strptime(x, "%Y-%m-%d"))
    return sorted_dates

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
    spatial_prcp = {'缺失值':0,'频率分布中尾部与其余值异常分离':0,
                    '不可能的值':0,'不同年份之间的重复值':0,'同一年中不同月份的重复值':0,
                    '20个以下的非零值':0,'不同年份之间相同月份的重复值':0,
                    '未被任何相邻值证实':0}
    spatial_tavg = {'缺失值':0,'错误的0值':0,'年份之间的重复值':0,'不同年份之间相同月份的重复值':0,
                    '同一年中不同月份的重复值':0,'超过世界记录范围的值':0,
                    '20个以上的连续值':0,'频率分布中尾部与其余值异常分离':0,'同一观测日或相邻观测日内部不一致':0,
                    '相邻几天内的异常波动':0,'观测点与相邻站点显著不同(空间回归)':0,'未被任何相邻值证实':0,'z值大于6个标准差':0}
    years = range(1999, 2001)
    list2 = []
    common_stations = None
    stations_all = pd.DataFrame()
    # year = 1980
    # lis,station,base_data = read(year)
    with ProcessPoolExecutor(max_workers=5) as executor:
        future_to_year = {executor.submit(read, year): year for year in years}  #提交每个年份的进程任务
        # 使用tqdm显示进度条
        for future in tqdm(as_completed(future_to_year), total=len(future_to_year), desc="Processing years"):   #as_completed返回一个可迭代对象
            year = future_to_year[future]
            # 新
            try:
                li, stations,base_data = future.result()
                df = pd.DataFrame({year: list(stations)})
                stations_all = pd.concat([stations_all, df], axis=1)
                list2.extend(li)
                if common_stations is None:
                    common_stations = stations
                else:
                    common_stations &= stations  # 更新共同台站号
            except Exception as e:
                print(f"Error processing year {year}: {e}")
                import traceback
                traceback.print_exc()
    
    # stations_all = pd.read_excel(r"E:\气象data\质量控制\stations_all.xlsx")
    stn_da = station_data(list2,datetime(min(years),1,1),datetime(max(years),12,31))
    stns = stn_da.load_stns()
    stations = set(stns[STN_ID])

    df_ten_min = pd.DataFrame()
    df_ten_max = pd.DataFrame()
    df_two_min = pd.DataFrame()
    df_two_max = pd.DataFrame()
    #下面是没有进行并行计算的代码
    # stations = set(list(stations)[14:65])
    # stations = ['54841.0']
    for s in tqdm(stations,desc="Processing stations"):
        print(s)
        target_value = int(float(s))

        # 含有该站点的所有年份
        year_list = sorted([col for col in stations_all.columns if target_value in stations_all[col].values])
        # 获取日期数组
        lis = []
        for ye in year_list:
            start_date = datetime(ye, 1, 1)
            end_date = datetime(ye, 12, 31)
            date_arr = create_date_array(start_date, end_date)
            lis.append(date_arr)
        days_array = np.concatenate(lis)
        # 获取日期序列
        sorted_dates = date_year(year_list)
 
        tmin_all = pd.DataFrame()
        tmax_all = pd.DataFrame()
        stn = stns[stns[STN_ID]==s][0]
        # stn = arr_index(stns,STN_ID,'54825')
        stn_obs = stn_da.load_all_stn_obs(np.array([stn[STN_ID]]),set_flagged_nan=False)   #返回最小、最大气温、降水、平均气温
        df_tmin,df_tmax = qa1.qa_temp.checks_qa(stn,stn_da,stn_obs[TMIN],stn_obs[TMAX],days_array,stn_da.days1,spatial_max,spatial_min,sorted_dates)
        tmin_qa,tmax_qa = qa1.qa_temp.Convert_to_decimal(df_tmin,df_tmax)
        # x_tmin = stn_obs[TMIN]
        # y_tmax = stn_obs[TMAX]
        # 十进制
        tmin_all[s] = tmin_qa.iloc[:,-1]
        tmax_all[s] = tmax_qa.iloc[:,-1]
        df_ten_min = pd.concat([df_ten_min,tmin_all],axis=1)
        df_ten_max = pd.concat([df_ten_max,tmax_all],axis=1)
        
        # 二进制
        df_two_min[s] = tmin_qa.iloc[:,-2]
        df_two_max[s] = tmax_qa.iloc[:,-2]
        
    
    df_ten_min.to_excel(r"E:\气象data\质量控制\十进制\min_all.xlsx")
    df_ten_max.to_excel(r"E:\气象data\质量控制\十进制\max_all.xlsx")
    df_two_min.to_excel(r"E:\气象data\质量控制\二进制\min_all.xlsx")
    df_two_max.to_excel(r"E:\气象data\质量控制\二进制\max_all.xlsx")
    
    #原：十进制
    # df_tmin = output(tmin_all,"tmin")
    # df_tmax = output(tmax_all,"tmax")
    print("ok")
if __name__ == '__main__':  #确保主程序执行时才使用，而不是调用模块时就使用
    main()


