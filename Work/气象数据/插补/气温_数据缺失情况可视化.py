# -*- coding: utf-8 -*-
"""
Created on Sat 2024/10/18 17:39
@Author : lyr

Analysis of missing data

"""
import re
import os
import pandas as pd
import numpy as np
import datetime
import glob as gb
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def out_date_by_day(year, day):
    """
    输入的年份/天数计算对应的日期
    """
    first_day = datetime.datetime(year, 1, 1)
    add_day = datetime.timedelta(days=day - 1)
    return datetime.datetime.strftime(first_day + add_day, "%Y-%m-%d")

def clean_data(data_all):
    """
    将无效值替换为NaN
    """
    # to_replace = [999990.0, 999999.0, 999998.0, 32766.0,-9999.0]
    data_all[(data_all < -999) | (data_all > 10000)] = np.nan          # 降水的无效值不统一
    return data_all

def acquire_prcp(path_data,df2):
    """
    获取所有年份的降水数据
    """
    paths = gb.glob(path_data)
    data_all = []

    for p in paths:
        year = re.split('[_.]', p)[-2]
        data = pd.read_csv(p,encoding_errors='ignore')
        data = data.drop(['Unnamed: 0'], axis=1).set_index('台站编号')
        data.index = data.index.astype(str)
        data = data.drop(data.columns[:3], axis=1)

        # 将天数据转换为日期数据
        f = data[data.index.isin(df2.index)]
        days = data.columns.str.extract(r'D(\d+)')[0].astype(int)
        date = pd.Series(days).apply(lambda x: out_date_by_day(int(year), x))
        f.columns = list(date)
        data_all.append(f)
    data_all = clean_data(pd.concat(data_all, axis=1))

    return data_all

if __name__ == "__main__":

    path = r"E:\所实习\气温原始数据\unique_station_TMAX_1980_2022.txt"          # 经纬度数据信息
    path_data = r"E:\所实习\气温原始数据\平均后日最高气温\TEM_max_*.txt" # 原始降水量数据
    output_path = r'E:\所实习\气温数据插值处理\1数据缺失值概况\日平均气温'

    # 获取经纬度信息并排除自动站
    df = pd.read_csv(path, index_col=0, dtype={'台站编号':str})
    df2 = df[df['台站编号'].str.startswith('5')]                        # 以5开头的是自动站点
    df2 = df2.drop_duplicates(subset=['经度', '纬度'], keep='first')    # 存在台站编号不同但是经纬度相同的值
    df2 = df2.set_index('台站编号')

    data_all = acquire_prcp(path_data,df2)
    data_all = data_all.T
    data_all.index = pd.to_datetime(data_all.index)
    full_index = pd.date_range(start="1980-01-01", end="2022-12-31", freq="D")
    data_all = data_all.reindex(full_index)                             # 填补2016年的时间序列

    ###新插入2025/5/13
    data_all1 = data_all.copy()
    data_all1[:] = np.where(data_all1.isna(), '0111111111', '1111111111')
    # data_all1.to_csv(r"E:\所实习\气温数据插值处理\2数据质量控制\日平均气温\插值前质量控制\QC_prcp_bin.csv")   # 二进制输出
    #######
    data_grouped = data_all.groupby(data_all.index.year)

    # 计算站点在各年份的缺失值
    y_nan = []
    year = []
    number = []
    for y,data in data_grouped:
        c = data.isnull().sum()
        y_nan.append(c)
        year.append(y)
        number.append(len(c[c != len(data)]))
    y_nan = pd.concat(y_nan,axis=1)
    y_nan.columns = year

    # 计算站点在所有年份的缺失值和占比
    y_nan_all = y_nan.sum(axis=1)
    percentage = (y_nan_all/len(data_all))*100
    less = len(percentage[percentage <= 80])

    percentage_info = pd.concat([df2,percentage],axis=1)
    percentage_info = percentage_info.rename(columns={0: '缺失值占比'})

    # percentage.to_csv(output_path + os.sep + '多年缺失值占比.csv')                   # 输出
    # percentage_info.to_csv(output_path + os.sep + '多年缺失值占比(带经纬度版).csv')   # 输出


    # """ 缺失值可视化 """
    #
    # # 逐年站点数量图
    # plt.figure(figsize=(24, 6))
    # plt.bar(year, number, label='站点数量', color=(0.3, 0.3, 0.3), width=0.6)  # 使用较深的灰色
    # plt.xlabel('年份', fontsize=16)
    # plt.ylabel('台站数量/个', fontsize=16)
    # # plt.title('Number of sites per year', fontsize=18)
    # plt.xticks(year, rotation=45, fontsize=12)
    # plt.yticks(fontsize=12)
    # plt.legend(fontsize=14)
    # plt.grid(False)
    # plt.tight_layout()
    # plt.show(block=True)
    # # plt.savefig(r"逐年站点数量图.png", dpi=300, bbox_inches='tight')
    #
    # # 缺失值占比图
    # plt.figure(figsize=(24, 8))
    # plt.plot(percentage.index, percentage.values, label= '缺失值百分比', color='#2ca02c', linestyle='-', linewidth=1,
    #          markersize=4)
    # plt.axhline(y=80, color='red', linestyle='--', linewidth=1)
    # plt.plot([], [], ' ', label=f'小于80%的站点个数: {less}')
    # plt.plot([], [], ' ', label=f'总站点个数: {len(percentage)}')
    # plt.xlabel('台站编号',fontsize=16)
    # plt.ylabel('百分比(%)',fontsize=16)
    # # plt.title(f'The proportion of missing values',fontsize=16)
    # plt.xticks(ticks=range(0, len(percentage.index), 180), labels=percentage.index[::180], fontsize=12, rotation=45)
    # plt.yticks(fontsize=12)
    # plt.legend(fontsize=14)
    # plt.grid(False)
    # plt.tight_layout()
    # plt.show(block=True)
    # # plt.savefig(r"缺失值占比图.png", dpi=300, bbox_inches='tight')

































