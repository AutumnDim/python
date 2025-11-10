# -*- coding: utf-8 -*-
"""
Created on Sat 2024/10/14 17:45
@Author : lyr
"""

import pandas as pd
import numpy as np
import datetime
import glob as gb
import re
import os
from tqdm import tqdm
from multiprocessing import Pool
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import hanshu


def grt_circle_dist(lon1, lat1, lon2, lat2):
    """
    获取大圆距离(两地最短球面距离)

    参数
    ----------
    lon1 : float
        起始点的经度
    lat1 : float
        起始点的纬度
    lon2 : array_like
        终点的经度数组
    lat2 : array_like
        终点的纬度数组

    返回值
    -------
    distance : numpy.ndarray
        起点与每个终点之间的大圆距离

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    R = 6371.0
    distance = R * c
    return distance

def acquire_GHCND(path_GHCND,year=None):

    """ 获取GHCND的降水数据 """

    df_ghcnd = pd.read_csv(path_GHCND, dtype={'台站编号': str},index_col=0).set_index('台站编号').iloc[:, 3:]
    data_col = df_ghcnd.columns
    days = data_col.map(lambda x: int(re.search(r'D(\d+)', x).group(1)) if re.search(r'D(\d+)', x) else None)
    date = pd.Series(days).apply(lambda x: out_date_by_day(int(year), x))
    df_ghcnd.columns = list(pd.to_datetime(date))
    df_ghcnd = df_ghcnd.T
    return df_ghcnd

def out_date_by_day(year, day):

    """ 根据输入的年份和天数计算对应的日期 """

    first_day = datetime.datetime(year, 1, 1)
    add_day = datetime.timedelta(days=day - 1)
    return datetime.datetime.strftime(first_day + add_day, "%Y-%m-%d")

def clean_data(data_all):
    """
    将特定值替换为NaN
    """
    # to_replace = [999990.0, 999999.0, 999998.0, 32766.0,-9999.0,999805.0]
    data_all[(data_all > 10000) | (data_all < 0)] = np.nan
    return data_all

def distance(station,df2):

    """筛选出附近站点数据 """

    target = df2.loc[station]
    # 目标站点经纬度
    lon1, lat1 = target['经度'], target['纬度']
    # 距离计算
    distances = grt_circle_dist(lon1, lat1, df2['经度'], df2['纬度'])
    # 获取最近的7个站点
    dist = df2.iloc[np.argsort(distances)[:8]]

    return dist

def acquire_prcp(path_data, df2):

    """ 获取所有年份的降水信息 """

    paths = gb.glob(path_data)
    data_all = []

    for p in paths:
        year = re.split('[_.]', p)[-2]
        data = pd.read_csv(p)
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

def acquire_inter_data(df_qa, dist, prcp_id,value):

    """ 返回标签和特征数据 """

    # 将站点数据组成特征值
    sta_data = prcp_id.loc[dist.index].T

    # 加入质量信息
    df = pd.concat([df_qa, sta_data], axis=1)
    df.columns.values[0] = '质量信息'

    # 将未通过质量判断的值赋值为nan
    # df['dayofyear'] = df.index.dayofyear
    df['month_day'] = df.index.strftime('%m-%d')
    df['质量信息'] = df['质量信息'].apply(lambda x: np.nan if any(v in x for v in value) else x)
    df.loc[df['质量信息'].isnull(), df.columns[1]] = np.nan
    df.drop('质量信息', axis=1, inplace=True)

    # 获取目标和特征
    feature = df.columns[1:-1]  # 特征 1980-2022年1-364/365天的降水量？
    target = df.columns[0]  # 目标 质量信息？
    return df, target, feature

def process_group(group_data):

    day, group, feature, target = group_data
    mean_accuracy, y_pre, group1, missing, target_col = hanshu.Naive_Bayes_classifier(group, day, feature, target,
                                                                               random_seed=42)
    if y_pre is None:
        return group1, mean_accuracy
    else:
        y_pre1 = np.where(y_pre == 1, 0, y_pre + 2000)
        group1.loc[missing, target_col] = y_pre1
        return group1, mean_accuracy

def Naive_Bayes(df, target, feature):
    # 按照天数分组处理数据
    grouped = df.groupby('month_day')

    # 创建要传递给进程的参数
    group_data = [(day, group, feature, target) for day, group in grouped]

    DEBUG = True
    if DEBUG:
        results = []
        for group_args in tqdm(group_data, total=len(group_data), desc='Processing Days (Single Thread)'):
            results.append(process_group(group_args))
    else:
        with ProcessPoolExecutor() as executor:
            results = list(tqdm(executor.map(process_group, group_data), total=len(group_data), desc='Processing Days'))

    grouped_all1, accuracies1 = zip(*results)  # 解压返回结果
    grouped_all1 = pd.concat(grouped_all1)

    # 将站点名的排序变为原始的排序
    grouped_all1 = grouped_all1.reindex(columns=df.columns[:-1])
    return grouped_all1, list(accuracies1)

def process_station(task):

    """ 处理每个站点 """

    name, prcp_id, df_qa, df2, data_all, value_1 = task
    print(name)
    df_qa_station = df_qa[name]

    # 筛选附近的七个站点数据
    dist = distance(name, df2)

    # 获取目标站点和附近7个站点的降水数据
    df, target, feature = acquire_inter_data(df_qa_station, dist, data_all, value_1)

    # 进行贝叶斯分类预测
    grouped_all, accuracies = Naive_Bayes(df, target, feature)
    accuracies = pd.DataFrame({f'{target}': accuracies})

    # 需要插值站点的经纬度
    target_points = df2.loc[target]
    xi = np.array(target_points["经度"])
    yi = np.array(target_points["纬度"])

    # 附近站点的经纬度
    ngh_points = df2.loc[[i for i in list(feature)]]
    x1 = np.array(ngh_points["经度"])
    y1 = np.array(ngh_points["纬度"])
    elevation1 = np.array(ngh_points['海拔'])

    # 验证插值精度
    r2 = hanshu.validate_kriging(grouped_all, target, xi, yi, x1, y1, elevation1)
    r2 = pd.DataFrame({f'{target}': [r2]})

    # 进行泛克里金插值
    result = hanshu.interpolate_values(grouped_all, target, xi, yi, x1, y1, elevation1)

    return result, accuracies, r2

def main():
    path = r"C:\降水归档\降水数据插值(国内)_气象局\0降水数据\格式整理数据\unique_station_1980_2022.txt"                  # 经纬度数据
    path_qa = r"C:\降水归档\降水数据插值(国内)_气象局\2数据质量控制\插值前质量判断\QC_prcp_bin.csv"                     # 质量判断数据
    path_data = r"C:\降水归档\降水数据插值(国内)_气象局\0降水数据\格式整理数据\降水量\precipitation_time_2020_*.txt"   # 原始降水量数据
    path_nan = r"C:\降水归档\降水数据插值(国内)_气象局\1数据缺失值概况\多年缺失值占比.csv"                           # 缺失值占比数据
    path_GHCND16 = r"C:\降水归档\降水数据插值(国外)_GHCND\0原始数据\PRCP1\PRCP_2016.csv"                        # GHCND数据
    path_GHCND17 = r"C:\降水归档\降水数据插值(国外)_GHCND\0原始数据\PRCP1\PRCP_2017.csv"                    # GHCND数据
    output_path = r"C:\降水归档\降水数据插值(国内)_气象局\3数据插值\1缺失值插值"
    value_1 = ['0111111111']             # 未通过缺失值的质量判断

    # 获取缺失值\经纬度信息
    df_nan = pd.read_csv(path_nan, index_col=0)
    df = pd.read_csv(path, index_col=0, dtype={'台站编号':str})

    if len(str(df_nan.index[0])) == 11 :
        nan = df_nan[df_nan < 60].dropna().index.astype(str)
    else:
        nan = df_nan[df_nan < 80].dropna().index.astype(str)
        df = df[df['台站编号'].str.startswith('5')]

        # 获取GHCND数据
        df_ghcnd16 = acquire_GHCND(path_GHCND16, 2016)
        df_ghcnd17 = acquire_GHCND(path_GHCND17, 2017)
        df_ghcnd = pd.concat([df_ghcnd16, df_ghcnd17])

    df = df.drop_duplicates(subset=['经度', '纬度'], keep='first')
    df2 = df.set_index('台站编号')
    df2 = df2[df2.index.isin(nan)]

    # 获取质量信息数据
    data_qa = pd.read_csv(path_qa, dtype=str, index_col=0)
    data_qa.index = pd.to_datetime(data_qa.index)

    # 获取降水数据
    data_all = acquire_prcp(path_data, df2)
    data_all = data_all.T
    data_all.index = pd.to_datetime(data_all.index)

    # 填充不足的时间序列
    date_range = pd.date_range(start=data_all.index[0], end=data_all.index[-1], freq='D')
    data_all = data_all.reindex(date_range)

    # 替换2016/2017年的数据
    matching_columns = df_ghcnd.columns.intersection([f'CH0000{station}' for station in data_all.columns])
    fliter = (((df_ghcnd.index >= '2016-06-01') & (df_ghcnd.index < '2017-01-01'))
              | ((df_ghcnd.index >= '2017-06-10') & (df_ghcnd.index < '2017-07-01')))
    df_update = df_ghcnd[fliter][matching_columns]
    df_update.columns = df_update.columns.str.replace('CH0000', '', regex=False)
    data_all.update(df_update, overwrite=False)

    # 获取未通过质量判断的站点(缺失值)
    condition_1 = (data_qa == value_1[0])
    fail_station = condition_1.sum()[condition_1.sum() > 0].index
    prcp_id = data_all.loc[:, fail_station].iloc[:,:1]
    data_all = data_all.T

    # 初始化结果数据框
    result_all = pd.DataFrame()
    accuracy_all = pd.DataFrame()
    r2_all = pd.DataFrame()

    tasks = [(name, prcp_id, data_qa, df2, data_all, value_1)for name in prcp_id.columns]
    # DEBUG1为False 且 DEBUG为True时运行的效果最佳
    DEBUG1 = True
    if DEBUG1:
        results = []
        for t in tqdm(tasks, total=len(tasks), desc='Processing station (Single Thread)'):
            results.append(process_station(t))
    else:
        with ProcessPoolExecutor() as executor:
            results = list(tqdm(executor.map(process_station, tasks),
                                total=len(tasks), desc='Processing station (Multi Process)'))

    # 处理多进程结果
    for result, accuracies, r2 in results:
        result_all = pd.concat([result_all, result], axis=1)
        accuracy_all = pd.concat([accuracy_all, accuracies], axis=1)
        r2_all = pd.concat([r2_all, r2], axis=1)

    # result_all只是缺失值站点的结果，后续输出的降水数据需要加上除缺失值的站点结果

    # 保存结果
    # result_all.to_csv(output_path + os.sep + 'prcp_all.csv')
    # accuracy_all.to_csv(output_path + os.sep + 'accuracy_all.csv')
    # r2_all.to_csv(output_path + os.sep + 'r2_all.csv')

    # 分年输出结果
    hanshu.Output_annually(result_all,df2,output_path)

if __name__ == "__main__":
    # multiprocessing.set_start_method("spawn")
    main()
