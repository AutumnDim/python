# -*- coding: utf-8 -*-
"""

Created on Sat 2024/9/4 9:44
@Author : lyr

add()：                      为2022年添加对应的海拔
extract()：                  获取所有年份台站的并集，并获取对应的经纬度和海拔信息
extract_feature()：          提取与拉萨站相关的特征(平均气温、最低温度等)，用于随机森林输入特征
extract_caculate()：         计算与拉萨站相关的特征(附近站点，与附近站点的方向角，起伏度，坡度，距离)，用于随机森林输入特征
acquire_data()：             从多年原始降水量数据中获取拉萨站40年的原始数据
drawing()：                  era5数据和通过质量评价的降水数据的年总量对比
distance()：                 筛选出附近站点数据
QC_prcp()：                  提取质量判断数据并转换为2进制
extract_GHCND()：            提取GHCND数据
acquire_lon_lat()：          为通过插值后的站点数据匹配经纬度
prcp_month_change()：        插补结果的多年月际变化图
type_prcp():                降水年型判断(枯水年，丰水年)
convert_unit():             转换温度单位(乘以0.1)
Anusplin_Fillna_Format():   数据转为Anusplin空间插值的插补缺失值模式格式

"""

import re
import os
import math
import datetime
import glob as gb
import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import font_manager
from sklearn.metrics import r2_score
from matplotlib.ticker import MultipleLocator
from sklearn.metrics import mean_squared_error, mean_absolute_error

font_path = 'C:/Windows/Fonts/simhei.ttf'  # 根据操作系统找到合适的字体路径
prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = prop.get_name()  # 使用找到的中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def out_date_by_day(year, day):
    '''
    根据输入的年份和天数计算对应的日期
    '''
    first_day = datetime.datetime(year, 1, 1)
    add_day = datetime.timedelta(days=day - 1)
    return datetime.datetime.strftime(first_day + add_day, "%Y-%m-%d")
def calculate_angle(lat1, lon1, lat2, lon2):
    # 将纬度和经度从度数转换为弧度
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # 计算经度差
    d_lon = lon2 - lon1

    # 计算方向角公式
    x = math.sin(d_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(d_lon)

    # 计算初始方位角（弧度）
    initial_angle = math.atan2(x, y)

    # 将结果从弧度转换为角度
    initial_angle = math.degrees(initial_angle)

    # 确保方位角是0-360度之间
    angle = (initial_angle + 360) % 360
    return angle
def DISTANCE( r,  lat1,  lon1,  lat2,  lon2):
    '''
    :param r: 地球半径
    :param lat1: 目标点的纬度
    :param lon1: 目标点的经度
    :param lat2: 网格点的纬度
    :param lon2: 网格点的经度
    :return: 大圆距离
    '''
    # 将度数转变为弧度
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # 计算球面上两点的余弦值
    temp = math.sin(lat1)*math.sin(lat2)+math.cos(lat1)*math.cos(lat2)*math.cos(lon1-lon2)
    # 限制余弦值的范围在[-1, 1]之间
    temp = min(1.0, max(-1.0, temp))
    # 计算两点之间的弧度距离
    rad_dif = math.acos(temp)
    # 计算实际距离
    dist = r*rad_dif
    return dist
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

def add():
    """
    为2022年台站数据添加对应的海拔
    """
    for year in range(2022,2023):
        path = fr'E:\stations_new\日最低气温\TEM_Min_{year}.txt'
        file_name = path.split('\\')[-1]
        df = pd.read_csv(path,index_col=0)
        df.insert(3,'海拔',np.nan)
        print(len(df))
        df.to_csv(path)
        print('ok')
# add()

def extract():
    """
    获取所有年份台站的并集（只包括经纬度和海拔信息）
    """
    base_info = pd.DataFrame()
    for year in range(1980,2023):
        path1 = fr"E:\所实习\气温原始数据\平均气温\TEM_Tavg_{year}.txt"
        ddf = pd.read_csv(path1)
        ddf = ddf.iloc[:,1:]
        info = ddf.iloc[:,:4]
        base_info = pd.concat([base_info, info], ignore_index=True)
        print(year)
    unique_stations = base_info.drop_duplicates(subset=['台站编号'])
    unique_stations.to_csv(r'E:\所实习\气温原始数据\unique_station_TAVG_1980_2022.txt')
    print('ok')
# extract()

def extract_feature():
    """
    提取拉萨站与降水相关的特征要素，形成随机森林中可以用到的数据
    """
    path_prcp = r"E:\data_prcp.csv"         #降水数据  3648.9
    # sta = ['55595','55594','55590','55593','55589','55499','55691','55586','55598','55493']
    var = ['平均气温','日最高气温','日最低气温','平均相对湿度','日照时数']
    df1 = pd.DataFrame()
    for v in var:
        df_all = pd.DataFrame()
        path = gb.glob(rf'E:\stations_new\{v}\*.txt') # 其他特征数据
        for p in path:
            year = re.split(r'[\\_.]',p)[-2]
            file = pd.read_csv(p,dtype={'台站编号':str})
            df = file.iloc[:,1:]
            data_sta = df[df['台站编号']==((str(55591.0)).split('.')[0])]
            data_base = data_sta.iloc[:,:4]
            data = data_sta.iloc[:,4:]
            data.index = [0]
            # 将天数据转换为日期数据
            data_col = data.columns
            days = data_col.map(lambda x: int(re.search(r'D(\d+)', x).group(1)) if re.search(r'D(\d+)', x) else None)
            date = pd.Series(days).apply(lambda x: out_date_by_day(int(year), x))
            data.columns = list(date)
            df_all = pd.concat([df_all,data],axis=1)
            print(year)
        df_all.index = [v]
        df1 = pd.concat([df1,df_all])
    df1=df1.T
    arr = pd.read_csv(path_prcp)
    arr = arr.set_index('Unnamed: 0')
    arr.columns = ['降水量']
    merge = pd.concat([df1,arr],axis=1)
    merge.insert(0, '海拔', 3648.9)

    merge[merge == 999990.0] = np.nan
    merge[merge == 999999.0] = np.nan
    merge[merge == 999998.0] = np.nan
    merge.to_csv(r"E:\prcp_relative.csv")
    print('ok')
# extract_feature()

def extract_caculate():
    """
    计算拉萨站和邻近站点与降水有关的特征数据
    :return:
    """
    R_earth = 6371.0  # 地球半径
    # sta = ['55591','55595','55594','55590','55593','55589','55499','55691','55586','55598','55493']

    path = r"/atm/降水的贝叶斯分类/西藏改则/ngb_sta_7.csv"
    ngb = pd.read_csv(path).set_index('台站编号')
    sta = ngb.index

    #计算方向角
    path_lon = r"D:\GPM_2001\unique_station_1980_2022.txt"
    df_lon = pd.read_csv(path_lon)
    df_lon = df_lon.set_index('Unnamed: 0')
    data = df_lon[df_lon['台站编号'].isin(sta)].set_index('台站编号')
    data = pd.concat([ngb,data],axis=1).drop('0',axis=1)
    target = data.loc[data.index[0]]
    near = data.drop(data.index[0])

    df_angle = pd.DataFrame()
    df_dis = pd.DataFrame()
    lon1 = target['经度']
    lat1 = target['纬度']
    for index,row in near.iterrows():
        lon2 = row['经度']
        lat2 = row['纬度']
        # 计算两个站点的方向角
        angle = calculate_angle(lat1, lon1, lat2, lon2)
        # 计算两个站点的距离
        distance = DISTANCE(R_earth,lat1, lon1, lat2, lon2)
        df_angle[index] = [angle]
        df_dis[index] = [distance]
    df_angle.columns = [f'{i}_angle' for i in df_angle.columns]
    df_dis.columns = [f'{i}_dis' for i in df_dis.columns]

    # 计算起伏度
    mean = data['海拔'].mean()
    RDLS = pd.DataFrame(data['海拔'] - mean)
    RDLS.index = [f'{i}_elev' for i in RDLS.index]
    RDLS_df = RDLS.T

    # 计算坡度
    h = RDLS_df#.drop(f'{data.index[0]}_elev',axis=1)
    h.columns = [i.split('_')[0] for i in h.columns]
    df_dis.columns = [i.split('_')[0] for i in df_dis.columns]
    df_slope = pd.concat([h,df_dis])
    slope_radians = np.arctan(abs(df_slope.iloc[0,:]) / df_slope.iloc[1,:])
    slope_degrees = np.degrees(slope_radians)
    slope_degrees = pd.DataFrame(slope_degrees).T
    slope_degrees.columns = [f'{i}_slope' for i in slope_degrees.columns]
    df_dis.columns = [f'{i}_dis' for i in df_dis.columns]

    # 合并邻近站点数据
    df_all = pd.DataFrame()
    for s in sta:
        path = rf"D:\实习\atm\降水的贝叶斯分类\西藏改则\data_prcp_{s}.csv"
        df = pd.read_csv(path)
        df = df.set_index('Unnamed: 0')
        df_all = pd.concat([df_all,df],axis=1)

    # 获取 df_all 的行数
    num_rows = df_all.shape[0]

    # 扩展的行数，使其与 df_all 相同
    RDLS_expanded = pd.concat([RDLS_df] * num_rows, ignore_index=True)
    df_angle_expanded = pd.concat([df_angle] * num_rows, ignore_index=True)
    slope_degrees_expanded = pd.concat([slope_degrees] * num_rows, ignore_index=True)
    df_dis_expanded = pd.concat([df_dis] * num_rows, ignore_index=True)
    RDLS_expanded.index = df_all.index
    df_angle_expanded.index = df_all.index
    slope_degrees_expanded.index = df_all.index
    df_dis_expanded.index = df_all.index


    df_all = pd.concat([df_all, RDLS_expanded,df_angle_expanded,df_dis_expanded,slope_degrees_expanded], axis=1)
    # c=[ '55595', '55594', '55590',  '55499', '55691','55586',
    #     '55594_elev', '55691_elev', '55586_elev','55590_elev', '55595_elev', '55499_elev',
    #     '55594_angle', '55691_angle','55586_angle', '55590_angle', '55595_angle', '55499_angle',
    #     '55594_dis', '55691_dis','55586_dis', '55590_dis', '55595_dis', '55499_dis',
    #     '55594_slope', '55691_slope','55586_slope', '55590_slope', '55595_slope', '55499_slope']
    # merge = df_all.drop(c,axis=1)
    merge = df_all
    merge[merge == 999990.0] = np.nan
    merge[merge == 999999.0] = np.nan
    merge[merge == 999998.0] = np.nan
    merge[merge == 32766.0] = np.nan
    merge = merge.round(3)
    merge.index = pd.to_datetime(merge.index)

    # 加一个质量信息
    paths = r"D:\实习\atm\降水的贝叶斯分类\西藏改则\QC_pre2_55248.csv"
    QA = pd.read_csv(paths,dtype={'质量信息':str}).set_index('Unnamed: 0')
    QA = QA['质量信息']
    QA.index = pd.to_datetime(QA.index)
    merge1 = pd.concat([QA,merge],axis=1)

    merge1.to_csv(r"D:\实习\atm\降水的贝叶斯分类\西藏改则\feature.csv")
    print('ok')
# extract_caculate()

def acquire_data():
    """
    获取拉萨站点40年的原始数据
    :return:
    """
    paths_data = r"E:\气象数据\stations_new\降水量\precipitation_time_2020_*.txt"
    path = r'/atm/降水的贝叶斯分类/西藏狮泉河/ngb_sta_7.csv'
    ngb = pd.read_csv(path).set_index('台站编号')
    sta = ngb.index
    paths = gb.glob(paths_data)

    for station in sta:
        station = str(station)
        data_all = pd.DataFrame()

        for p in paths:
            split_path = re.split('[_.]',p)
            year = split_path[-2]
            data = pd.read_csv(p)
            data = data.drop(['Unnamed: 0'],axis=1)
            data = data.set_index('台站编号')
            data.index = data.index.astype(str)

            if station in data.index or f"{station}.0" in data.index:
                # 选择包含指定台站编号的行
                sta_data = data.loc[[index for index in data.index if index in [station, f"{station}.0"]]]
                sta_data = sta_data.iloc[0,:]
                sta_data1 = pd.DataFrame(sta_data[3:])

                # 将天数据转换为日期数据
                data_col = data.columns[3:]
                days = data_col.map(lambda x: int(re.search(r'D(\d+)', x).group(1)) if re.search(r'D(\d+)', x) else None)
                date = pd.Series(days).apply(lambda x: out_date_by_day(int(year), x))
                sta_data1.index = list(date)
                data_all = pd.concat([data_all, sta_data1])
            else:
                print(f'{station} not in {year}')
        print(station)
        data_all.to_csv(rf'D:\实习\atm\降水的贝叶斯分类\西藏狮泉河\data_prcp_{int(station)}.csv')
# acquire_data()

def drawing():
    """
    era5数据和通过质量评价的降水数据的年总量对比
    """
    path_LAS = r"/atm/降水的贝叶斯分类/西藏改则/inter_prcp(未通过).csv"
    df_las = pd.read_csv(path_LAS)
    df_las.index = pd.to_datetime(df_las['Unnamed: 0']).dt.year
    df_las.drop('Unnamed: 0',axis=1,inplace=True)
    las = df_las.groupby(df_las.index).sum().round(1)

    correct_prcp = pd.read_excel(r"C:\Users\21202\Desktop\拉萨年降水总量1980-2022.xlsx",header=None)
    correct_prcp = correct_prcp.set_index(0)

    era5 = pd.DataFrame()
    GHCND = pd.DataFrame()
    for y in range(1980,2021):
        path_era5 = rf"D:\实习\atm\data\out\interpolation\PRCP\PRCP_{y}.xlsx"
        path_GHCND=rf"D:\实习\atm\data\station\Station_data\PRCP\PRCP_{y}.xlsx"
        df_era5 = pd.read_excel(path_era5).iloc[:,1:].sum().round(1)
        df_ghcnd = pd.read_excel(path_GHCND,dtype={'台站编号':str})
        df_ghcnd=df_ghcnd.set_index('台站编号')
        df_ghcnd=df_ghcnd[df_ghcnd.index =='CH000055248']
        if len(df_ghcnd) > 0:
            nan = df_ghcnd.iloc[:,3:].isnull().sum(axis=1)
            df_ghcnd_sum = df_ghcnd.iloc[:,3:].sum(axis=1).round(1)
            print(nan)
            print(df_ghcnd_sum)
        else:
            df_ghcnd_sum = np.nan
            print("索引 'CH000055248' 不存在。请检查索引。")
        era5[y] = df_era5
        GHCND[y] = df_ghcnd_sum
        print(y)
    era5=era5.T
    GHCND = GHCND.T
    merge = pd.concat([las,era5,correct_prcp,GHCND],axis=1)
    merge.columns = ['original','era5','yearbooks','GHCND']
    merge.to_csv(r'D:\实习\atm\降水的贝叶斯分类\西藏改则\comparision_data.csv')

    merge = pd.read_csv(r'/atm/降水的贝叶斯分类/西藏改则/comparision_data.csv').set_index('Unnamed: 0')

    def calculate_stats(y_true, y_pred):

        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        correlation = y_true.corr(y_pred)
        r2 = r2_score(y_true, y_pred)

        return rmse, mae, correlation, r2

    sns.set(style="whitegrid")

    # 趋势图
    plt.figure(figsize=(12, 6))
    plt.plot(merge.index, merge['original'], label='original', color='#2ca02c', linestyle='-', linewidth=2,marker='o', markersize=4)
    # plt.plot(merge.index, merge['era5'],  label='era5', color='#1f77b4', linestyle='-', linewidth=2,marker='o', markersize=4)
    # plt.plot(merge.index, merge['yearbooks'],  label='yearbooks',color='#ff7f0e', linestyle='-', linewidth=2,marker='o', markersize=4)
    plt.plot(merge.index, merge['GHCND'],  label='GHCND',color='#7f7f6f', linestyle='-', linewidth=2,marker='o', markersize=4)
    plt.xlabel('Year')
    plt.ylabel('Precipitation(mm)')
    plt.title('Total annual precipitation of gaize')
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    # plt.show(block=True)
    plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\西藏改则\趋势图(四种数据).png", dpi=300, bbox_inches='tight')

    # 绘制散点图
    # merge1 = merge.iloc[:,:2]
    # merge1 = merge1.dropna()
    # rmse, mae, correlation, r2 = calculate_stats(merge1['era5'], merge1['original'])
    # slope, intercept = np.polyfit(merge1['era5'], merge1['original'], 1)  # 一阶多项式拟合，即线性拟合
    # trend_line = slope * merge1['era5'] + intercept
    # plt.figure(figsize=(10, 6))
    # plt.scatter(merge1['era5'], merge1['original'], color='#1f77b4', alpha=0.6)  # 深蓝色
    # plt.plot(merge1['era5'], trend_line, color='#7f7f7f')  # 深红色
    # plt.text(0.05, 0.95, f'R² = {r2:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    # plt.text(0.05, 0.90, f'R = {correlation:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    # plt.text(0.05, 0.85, f'MAE = {mae:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    # plt.text(0.05, 0.80, f'RMSE = {rmse:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    # plt.title('Comparison between the original and era5')
    # plt.xlabel('era5(mm)')
    # plt.ylabel('original(mm)')
    # plt.grid(False)
    # plt.show(block=True)
    # plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\西藏改则\散点图(对比era5).png", dpi=300, bbox_inches='tight')

    merge2 = merge.iloc[:,[0,-1]]
    merge2 = merge2.dropna()
    rmse1, mae1, correlation1, r21 = calculate_stats(merge2['GHCND'], merge2['original'])
    slope, intercept = np.polyfit(merge2['GHCND'], merge2['original'], 1)  # 一阶多项式拟合，即线性拟合
    trend_line = slope * merge2['GHCND'] + intercept
    plt.figure(figsize=(10, 6))
    plt.scatter(merge2['GHCND'], merge2['original'], color='#1f77b4', alpha=0.6)  # 深蓝色
    plt.plot(merge2['GHCND'], trend_line, color='#7f7f7f')  # 深红色
    plt.text(0.05, 0.95, f'R² = {r21:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.90, f'R = {correlation1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.85, f'MAE = {mae1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.80, f'RMSE = {rmse1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.title('Comparison between the original and GHCND')
    plt.xlabel('GHCND(mm)')
    plt.ylabel('original(mm)')
    plt.grid(False)
    # plt.show(block=True)
    plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\西藏改则\散点图(对比GHCND).png", dpi=300, bbox_inches='tight')
# drawing()

def distance():
    """
    筛选出附近站点数据
    """
    path = r"E:\气象数据\stations_new\unique_station_1980_2022.txt"
    df = pd.read_csv(path).iloc[:,1:]
    # 排除自动站
    df['台站编号'] = df['台站编号'].astype(str)
    df2 = df[df['台站编号'].str.startswith('5')]
    target = df2[df2['台站编号'] == '55228']
    # 目标站点经纬度
    lon1 = target['经度'].values[0]
    lat1 = target['纬度'].values[0]
    # 距离计算
    distance = grt_circle_dist(lon1, lat1, df2['经度'], df2['纬度'])
    dist =pd.DataFrame(distance).set_index(df2['台站编号'])
    #获取最近的7个站点
    dist = dist.sort_values(by=0)[:8]
    dist.to_csv(r'D:\实习\atm\降水的贝叶斯分类\西藏狮泉河\ngb_sta_7.csv')
    print('ok')
# distance()

def QC_prcp():
    """
    提取质量判断结果，并转换为二进制
    """
    path = r"E:\实习\atm\降水批量质量判断\QC_prcp_all.csv"
    df = pd.read_csv(path).set_index('Unnamed: 0')
    df1 = pd.DataFrame(df['55228'])
    df2 = df1.applymap(lambda x: bin(x)[2:].zfill(10))
    df2.columns = ['质量信息']
    df2.to_csv(r"D:\实习\atm\降水的贝叶斯分类\西藏狮泉河\QC_pre2_55228.csv")
    print('ok')
# QC_prcp()

def extract_GHCND():
    """
    提取GHCND数据
    """
    years=[]
    stations = '55228'
    GHCND = pd.DataFrame()
    for y in range(1980, 2021):
        path_GHCND = rf"D:\实习\atm\data\station\Station_data\PRCP\PRCP_{y}.xlsx"
        df_ghcnd = pd.read_excel(path_GHCND, dtype={'台站编号': str})
        df_ghcnd = df_ghcnd.set_index('台站编号')
        df_ghcnd = df_ghcnd[df_ghcnd.index == f'CH0000{stations}']
        GHCND = pd.concat([GHCND,df_ghcnd])
        years.append(y)
        print(y)
    GHCND = GHCND.iloc[:,3:]
    # years.remove(2008)
    GHCND.index=years
    GHCND.to_csv(r'D:\实习\atm\降水的贝叶斯分类\西藏狮泉河\GHCND_80_21.csv')
# extract_GHCND()

def acquire_lon_lat():
    """
    为通过插值后的站点数据匹配经纬度
    """
    path_day = r"C:\降水归档\降水数据插值(国内)_气象局\3数据插值\1缺失值插值\r2_all.csv"
    path_base = r"C:\降水归档\降水数据插值(国内)_气象局\0降水数据\格式整理数据\unique_station_1980_2022.txt"

    df_day = pd.read_csv(path_day,index_col=0).T
    df_day.index = df_day.index.astype(int)
    df_base = pd.read_csv(path_base,index_col=1).drop('Unnamed: 0',axis=1)

    info = df_base[df_base.index.isin(df_day.index)]

    day = pd.concat([info,df_day],axis=1)
    day1 = day.loc[[59981,59985]]
    day.to_csv(r"C:\降水归档\降水数据插值(国内)_气象局\3数据插值\1缺失值插值\r2_all(带经纬度版).csv")
    day1.to_csv(r"C:\降水归档\降水数据插值(国内)_气象局\3数据插值\1缺失值插值\r2_all(仅仅南沙群岛).csv")
    print('ok')
# acquire_lon_lat()

def convert_year():
    path = rf"C:\气象数据插值(ghcnd国外)\GHCND数据提取\ghcnd_prcp(1980-2022)_0.1.csv"
    path_base = r"C:\气象数据插值(ghcnd国外)\unique_stations_foreign(1980-2020).csv"
    output_path = r'C:\气象数据插值(ghcnd国外)\GHCND数据提取\dly_to_csv_prcp'

    df_base = pd.read_csv(path_base,dtype={'台站编号':str},index_col=1).drop('Unnamed: 0',axis=1)
    df = pd.read_csv(path,index_col=0).T
    info = df_base[df_base.index.isin(df.index)]
    df = df.T
    df.index = pd.to_datetime(df.index)
    groups = df.groupby(df.index.year)
    for year,group in groups:
        dayofyear = group.index.dayofyear
        group = group.T
        group.columns = [f'D{day}' for day in dayofyear]
        group = pd.concat([info,group],axis=1)
        group = group.reset_index()
        group = group.rename(columns={'index': '台站编号'})
        group.to_csv(output_path + os.sep + f'PRCP_{year}.csv')
        print(year)
# convert_year()

def prcp_month_change():
    """
    插补结果的多年月际变化图
    """
    path = r"C:\任务\结果(最新版2)\克里金插值\month_change.csv"
    path_g = r"C:\任务\结果(最新版2)\克里金插值\month_change_ghcnd.csv"

    df = pd.read_csv(path,index_col=0)
    df_g = pd.read_csv(path_g,index_col=0)

    df_mean = df.mean(axis=1)
    df_g_mean = df_g.mean(axis=1)

    df_mean.index = pd.to_datetime(df_mean.index)
    df_g_mean.index = pd.to_datetime(df_g_mean.index)

    merge = pd.concat([df_mean,df_g_mean],axis=1)
    merge.columns = ['插补后数据','GHCND数据']

    # 提取年月
    merge.index = merge.index.strftime('%Y-%m')

    fig, ax = plt.subplots(figsize=(12, 4), dpi=300)

    plt.plot(merge.index, merge['插补后数据'], label='插补后数据', color='orangered', linestyle='-', markersize=4)
    plt.scatter(merge.index, merge['GHCND数据'], label='GHCND数据', color='blue', s=5)

    plt.xlabel('年份')
    plt.xlim(-4,520)
    plt.ylabel('月降水量(mm)')

    xticks = merge.index[::12]
    year_labels = [tick.split('-')[0] for tick in xticks]
    ax.set_xticks(xticks)
    ax.set_xticklabels(year_labels, rotation=45)

    plt.legend()
    plt.tight_layout()

    plt.savefig(rf"C:\任务\结果(最新版2)\精度验证图片\月际变化结果.png", dpi=600, bbox_inches='tight')
    print('ok')
# prcp_month_change()

def type_prcp():
    """" 降水年型判断 """
    path = r"C:\任务\结果(最新版2)\克里金插值(单个站点)\GHCND年总降水量.xlsx"
    high_flow_year = []
    low_flow_year = []
    median_flow_year = []
    name_all = []
    df = pd.read_excel(path,index_col=0).T
    for name,sta in df.items():
        mean = sta.mean()
        std = sta.std()

        high_flow = mean + 0.33 * std
        low_flow = mean - 0.33 * std

        year_h = sta[sta > high_flow]
        year_l = sta[sta < low_flow]
        year_m = sta[(sta >= low_flow) & (sta <= high_flow)]

        high_flow_year.append(year_h)
        low_flow_year.append(year_l)
        median_flow_year.append(year_m)
        name_all.append(name)

    high_flow_year = pd.concat(high_flow_year,axis=1).sort_index()
    low_flow_year = pd.concat(low_flow_year,axis=1).sort_index()
    median_flow_year = pd.concat(median_flow_year,axis=1).sort_index()
    print('ok')
# type_prcp()

def convert_unit():
    """ 转换温度单位(乘以0.1) """
    path = rf"C:\气象数据插值(ghcnd国外)\GHCND数据提取\ghcnd_prcp(1980-2022).csv"
    df = pd.read_csv(path,index_col=0)
    df.replace(-9999, np.nan, inplace=True)
    df1 = df * 0.1
    df1.to_csv(rf"C:\气象数据插值(ghcnd国外)\GHCND数据提取\ghcnd_prcp(1980-2022)_0.1.csv")
    print('ok')
# convert_unit()

def Anusplin_Fillna_Format():
    """ 数据转为Anusplin空间插值的插补缺失值模式格式 """
    path1 = r"C:\Users\2024\OneDrive\Desktop\PRCP_1951_Filled.csv"
    df1 = pd.read_csv(path1)

    file_path = "C:\指标计算\计算指标\RHU"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    else:
        pass

    for year in range(2016,2017):
        path = rf"C:\指标计算\风速和气温代码\风速代码\插补后的特征数据\湿度\Average_relative_humidity_{year}.txt"
        df = pd.read_csv(path,index_col=0,dtype={'台站编号':str})

        for col,d in enumerate(df['台站编号']):
            d = d.split('.')[0]
            if len(d) == 5:
                df.iloc[col,0] = f'CH0000{d}'
            else:
                pass
        lon = df['经度']
        df.drop('经度',axis=1,inplace=True)
        df.insert(2,'经度',lon)

        df = df.rename(columns={'经度':'LONG','纬度':'LATI','海拔':'Elva'})
        df.insert(1,'Year',year)

        col = df.columns[1:]
        col1 = [c if not c.startswith('D') else f"D{c[1:].zfill(3)}" for c in col]
        df.columns = col1 + ['']
        df = df.set_index('Year')

        output_path=os.path.join(file_path,f"RHU_{year}_Filled.csv")
        df.to_csv(output_path)
        print(year)
# Anusplin_Fillna_Format()

""" CPC/GPM等(8天数据) """

# output_path = r'C:\降水归档\降水数据插值(国内)_气象局\4插值效果分析\单点分析\GHCND'
# if not os.path.exists(output_path):
#     os.makedirs(output_path)
# else:
#     pass
#
# df_all = []
# years = range(1980,2021)
# for y in years:
#     path_cpc = rf"C:\降水归档\降水数据插值(国外)_GHCND\0原始数据\PRCP1\PRCP_{y}.csv"
#     df_cpc = pd.read_csv(path_cpc,index_col = 0)
#     df_cpc=df_cpc.dropna(axis=1,how='all')
#
#     if len(df_cpc) > 366:
#         df_cpc = df_cpc[df_cpc['台站编号'].str.startswith('CH')].set_index('台站编号').iloc[:,3:]
#         df_cpc.columns = [i.replace('D','') for i in df_cpc.columns]
#         df_cpc.columns = [i for i in range(0,len(df_cpc.columns))]
#         df_cpc = df_cpc.T
#
#     days = []
#     if df_cpc.index[0] == 0:
#         df_cpc.index = [i+1 for i in df_cpc.index]
#         for day in df_cpc.index:
#             days.append(out_date_by_day(y, int(day)))
#         df_cpc.index = days
#     else:
#         pass
#     df_cpc.index = pd.to_datetime(df_cpc.index)
#
#     df_cpc[(df_cpc < 0) | (df_cpc > 10000)] = np.nan
#     df_cpc[df_cpc == -0.0] = 0.0
#
#     df_all.append(df_cpc)
#     print(y)
# df_all = pd.concat(df_all)
# df_all.to_csv(output_path + os.sep + f'prcp_{min(years)}_{max(years)}_D.csv')


def Output_annually(result_all, df2,output_path):

    """ 输出分年结果 """

    grouped = result_all.groupby(result_all.index.year)
    for year, group in grouped:
        dayofyear = group.index.dayofyear
        group = group.T
        group.columns = [f'D{day}' for day in dayofyear]
        group = pd.concat([df2, group], axis=1)
        group = group.reset_index()
        group = group.rename(columns={'index': '台站编号'})

        output_path_year = os.path.join(output_path, 'prcp_data')
        if not os.path.exists(output_path_year):
            os.makedirs(output_path_year)
        else:
            pass
        group.to_csv(output_path_year + os.sep + f'prcp_{year}.csv')      # 保存结果
        print(year)

# output_path = r"E:\所实习\气温数据插值处理\3缺失值插值\平均日最高气温"
# df = pd.read_csv(r"E:\所实习\气温数据插值处理\3缺失值插值\平均日最高气温\prcp_all.csv",index_col=0)
# df1 = pd.read_csv(r"E:\所实习\气温原始数据\unique_station_TMAX_1980_2022.txt",index_col=0,)
# df1 = df1.set_index("台站编号")
# df1.index = df1.index.astype(str)
# df.index = pd.to_datetime(df.index)
# grouped = df.groupby(df.index.year)
# for year, group in grouped:
#     dayofyear = group.index.dayofyear
#     group = group.T
#     group.columns = [f'D{day}' for day in dayofyear]
#     group = pd.concat([df1, group], axis=1,join='inner')
#     group = group.reset_index()
#     group = group.rename(columns={'index': '台站编号'})
#     output_path_year = os.path.join(output_path, 'prcp_data')
#     if not os.path.exists(output_path_year):
#         os.makedirs(output_path_year)
#     else:
#         pass
#     # group.to_csv(output_path_year + os.sep + f'prcp_{year}.csv')  # 保存结果
#     print(year)
# print('ok')

np.random.seed(42)
df = pd.read_csv(r"E:\所实习\气温数据插值处理\2数据质量控制\日平均最高温度\插值前质量控制\QC_prcp_bin.csv",dtype = str,index_col=0)


# 原始统计
original_full = (df == '1111111111').sum().sum()
original_half = (df == '0111111111').sum().sum()
print(f"原始统计:\n全1: {original_full}\n011...: {original_half}")

# 修改操作
mask = df == '1111111111'
rows, cols = np.where(mask)
selected = np.random.choice(len(rows), 10, replace=False)

for idx in selected:
    r, c = rows[idx], cols[idx]
    pos = np.random.randint(0, 10)
    df.iat[r, c] = df.iat[r, c][:pos] + '0' + df.iat[r, c][pos+1:]

# 精确验证
def count_single_zeros(df):
    return ((df.apply(lambda x: x.str.len() == 10)) &
            (df.apply(lambda x: x.str.count('0') == 1)) &
            (df != '0111111111')).sum().sum()

print(f"\n验证结果:")
print(f"理论应修改数量: 10")
print(f"实际全1减少量: {original_full - (df == '1111111111').sum().sum()}")
print(f"含单个0的新值数量: {count_single_zeros(df)}")

print('ok')


