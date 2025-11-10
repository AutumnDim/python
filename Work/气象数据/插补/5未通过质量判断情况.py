"""
查找未通过质量判断的数量，单点质量状况举例及数据可视化
"""
import pandas as pd
import numpy as np
import glob as gb
import datetime
import re
import utils.util_dates as utld
from datetime import datetime as dt
import matplotlib.pyplot as plt
from datetime import  timedelta
from matplotlib.ticker import AutoMinorLocator
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


YMD = u'年月日'
DATE = u'日期'
YDAY = u'年日'
YEAR = u'年'
MONTH =  u'月'
DAY = u'日'

PRCP_MIN_VALUE = 0.0
# World Record Daily Prcp (cm)
PRCP_MAX_VALUE = 1828.8

#Constants for spatial collaboration checks
MAX_SPATIAL_COLLAB_THRES = 269.24
MAX_SPATIAL_COLLAB_THRES_MM = MAX_SPATIAL_COLLAB_THRES*10.0
NGH_RADIUS = 75.0
ANOMALY_CUTOFF = 10.0
MIN_DAYS_MTH_WINDOW = 40
MIN_NGHS = 3
MAX_NGHS = 7

STREAK_LEN = 20
GAP_THRES = 300.0 #mm

MONTHS = np.arange(1,13)
DATES_366 = utld.get_date_array(dt(1980,1,1),dt(1980,12,31))
MIN_PERCENTILE_VALUES = 20

def structure_date(days_all):
    """
    days_all:格式化的时间信息
    """
    # 创建 DataFrame，直接提取日期的年、月、日信息
    df = pd.DataFrame({
        DATE: days_all,
        YEAR: [date.year for date in days_all],
        MONTH: [date.month for date in days_all],
        DAY: [date.day for date in days_all],
        YMD: [f"{date.year}-{date.month}-{date.day}" for date in days_all],
        YDAY: [date.dayofyear for date in days_all]
    })

    return df

def qa_clim_outlier(prcp, tavg, days, flags_prcp,target_date):
    '''
    Checks for prcp outliers based on relation to 29-day climate norm 95th percentile
    Must have 20 nonzero values in the 29-day period of record for the check to run
    '''

    dates = list(map(lambda x: x[0], days))
    dates1 = list(map(lambda x: x[-1], days))

    if target_date in dates:
        target_index = dates.index(target_date)
        print(f"目标日期 {target_date} 的索引为: {target_index}")
    else:
        print(f"目标日期 {target_date} 未找到")

    pctiles, vals_rng = build_percentiles(prcp, dates, DATES_366,target_date)

    date_objs = np.array(dates)
    ydays = np.array(dates1)
    prcp = np.array(prcp)
    tavg = np.array(tavg)

    prcp_nonzero = prcp[[target_index]]

    for x in np.arange(prcp_nonzero.size):
        day_num = ydays[target_index]-1

        # check that a val and norm exists
        if not_nan(pctiles[day_num, 4]):

            if not_nan(tavg[target_index]) and tavg[target_index] < 0.0:  # 根据气温设置阈值
                m = 5.0
            else:
                m = 9.0

            percentile_95 = m * pctiles[day_num, 4]

    return percentile_95, vals_rng, m

def build_percentiles1(vals, days, yr_days):
    mth_days = utld.get_md_array(days[DATE])

    # Build 29-day percentiles for every day in yr_days
    day_nums = np.arange(yr_days.size)
    # Columns: 30th,50th,70th,90th,95th
    percentiles = np.ones([yr_days.size, 5]) * np.nan

    for x in day_nums:
        date = yr_days[x]
        srt_date = date - utld.TWO_WEEKS
        end_date = date + utld.TWO_WEEKS
        date_range = utld.get_date_array(srt_date, end_date)
        mth_days_range = utld.get_md_array(date_range)

        date_mask = np.in1d(mth_days, mth_days_range)  # 检查 mth_days 中的每个元素是否存在于 mth_days_range 中，并返回一个布尔数组
        vals_rng = vals[np.logical_and(np.logical_and(not_nan(vals), vals > 0), date_mask)]

        if vals_rng.size >= MIN_PERCENTILE_VALUES:
            percentiles[x, :] = [np.percentile(vals_rng, 30), np.percentile(vals_rng, 50), np.percentile(vals_rng, 70),
                                 np.percentile(vals_rng, 90), np.percentile(vals_rng, 95)]

    return percentiles

def build_percentiles(vals, dates, yr_days,target_date):

    mth_days = utld.get_md_array(dates)

    # Build 29-day percentiles for every day in yr_days
    day_nums = np.arange(yr_days.size)
    # Columns: 30th,50th,70th,90th,95th
    percentiles = np.ones([yr_days.size, 5]) * np.nan

    for x in day_nums:
        date = yr_days[x]
        srt_date = date - utld.TWO_WEEKS
        end_date = date + utld.TWO_WEEKS
        date_range = utld.get_date_array(srt_date, end_date)
        mth_days_range = utld.get_md_array(date_range)

        date_mask = np.in1d(mth_days, mth_days_range)  # 检查 mth_days 中的每个元素是否存在于 mth_days_range 中，并返回一个布尔数组
        vals_rng = vals[np.logical_and(np.logical_and(not_nan(vals), vals > 0), date_mask)]


        if vals_rng.size >= MIN_PERCENTILE_VALUES:
            percentiles[x, :] = [np.percentile(vals_rng, 30), np.percentile(vals_rng, 50), np.percentile(vals_rng, 70),
                                 np.percentile(vals_rng, 90), np.percentile(vals_rng, 95)]

        if target_date.strftime('%m-%d') == date.strftime('%m-%d'):
            vals_rng_to_return = vals_rng

    if vals_rng_to_return is not None:
        return percentiles, vals_rng_to_return
    else:
        return percentiles, None

def clean_data(data_all):
    """
    将特定值替换为NaN
    """
    # to_replace = [999990.0, 999999.0, 999998.0, 32766.0,-9999.0]
    data_all[(data_all > 10000) | (data_all < 0)] = np.nan
    return data_all

def out_date_by_day(year, day):
    '''
    根据输入的年份和天数计算对应的日期
    '''
    first_day = datetime.datetime(year, 1, 1)
    add_day = datetime.timedelta(days=day - 1)
    return datetime.datetime.strftime(first_day + add_day, "%Y-%m-%d")

def acquire_prcp(path_data):
    # 获取所有年份的降水信息
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
    return data_all.T

def not_nan(vals):
    vals = np.float64(vals)
    return np.logical_not(np.isnan(vals))

def acquire_data(path_all,df_all):
    """
    获取降水和平均气温数据,筛选和质量判断后相同的站点并统一列顺序
    """
    data = acquire_prcp(path_all)
    data = pd.concat([data, df_all.iloc[:, 0]], axis=1)
    data = data.iloc[:, :-1]
    merge = pd.concat([df_all.iloc[:1, :], data])
    data = merge.iloc[1:, :]
    return data

if __name__ in '__main__':

    condition_prcp = ['缺失值','不同年份之间的重复值','同一年中不同月份的重复值','不同年份之间相同月份的重复值','不可能的值',
                      '20个或以上连续的值','不是必须连续的频繁出现的值','频率分布中尾部与其余值异常分离','20个以下的非零值',
                        '未被任何相邻值证实']

    path = r"C:\气象数据插值(ghcnd+国内)\国外数据插值\插值前质量控制\QC_prcp_bin.csv" # 插值前的质量判断
    path1 = r"C:\气象数据插值\2数据质量控制\插值后质量判断\QC_prcp_bin.csv"  # 插值后的质量判断
    path_data = r"C:\任务\气象数据\stations_new\降水量\precipitation_time_2020_*.txt"  # 原始降水数据
    path_data1 = r"C:\气象数据插值\3数据插值\8最终结果\prcp_data\prcp_*.csv"   # 插值后降水数据(全部条件插值后）
    path_data2 = r"C:\气象数据插值\3数据插值\1缺失值插值\prcp_data\prcp_*.csv" # 插值后降水数据(缺失值插值后）
    path_lon = r"C:\任务\气象数据\stations_new\unique_station_1980_2022.txt"  # 经纬度数据
    path_nan = r"C:\任务\实习\数据缺失值概况\多年缺失值占比.csv"  # 缺失值占比数据
    path_tavg = rf"C:\任务\气象数据\stations_new\平均气温\TEM_Tavg_*.txt"

    # 获取质量判断数据
    df = pd.read_csv(path,dtype=str,index_col=0)   #插值前的质量判断
    df1 = pd.read_csv(path1,dtype=str,index_col=0)  #插值后的质量判断
    # merge1 = pd.concat([df.iloc[:1,:],df1])
    # df1 = merge1.iloc[1:,:]     #统一插值前和插值后的列

    # 获取缺失值信息
    df_nan = pd.read_csv(path_nan, index_col=0)
    df_nan = df_nan[df_nan < 80].dropna()

    # 获取经纬度信息
    df_lon = pd.read_csv(path_lon).iloc[:, 1:]
    df_lon['台站编号'] = df_lon['台站编号'].astype(str)
    df2 = df_lon[df_lon['台站编号'].str.startswith('5')]
    df2 = df2.drop_duplicates(subset=['经度', '纬度'], keep='first')
    df2 = df2.set_index('台站编号')
    df2 = df2[df2.index.isin(df_nan.index.astype(str))]

    # 获取插值前的数据
    data_all = acquire_data(path_data,df)       # 插值前的降水数据
    data_all1 = acquire_data(path_data1,df)     # 插值后降水数据(全部条件插值后）
    data_all2 = acquire_data(path_data2,df)     # 插值后降水数据(缺失值插值后）
    data_tavg = acquire_data(path_tavg,df)      # 平均气温数据

    """ 未通过质量判断的情况 """

    # unique_value = np.unique(df.values)
    # list = []
    # for value in unique_value:
    #     if str(0) in value:
    #         position = value.find('0')
    #         print(f"判断条件为:{condition_prcp[position]}")
    #         condition = df[df == value]
    #         number_sta = condition.count()
    #         number_all  = number_sta.sum()
    #         list.append({f'{condition_prcp[position]}':number_all})
    # # 未通过判断的数量
    # count_all = 0
    # for l in list:
    #     print(l)
    #     count_all += sum(l.values())
    # percentage = count_all/(df.shape[0]*df.shape[1])*100
    # print(f'未通过判断的总数量为{count_all}')
    # print(f'未通过判断的数量占比为{percentage}')

    """ 缺失值检查 """

    # value_0 = ['0111111111']
    # condition_1 = (df == value_0[0])
    # fail_station = condition_1.sum()[condition_1.sum() > 0].index
    #
    # # 插值前数据
    # prcp_id = data_all.loc[:, fail_station]
    # data = prcp_id['55248']
    # data = data[:121]
    # data.index =  pd.to_datetime(data.index).strftime('%m-%d')
    # # 插值后数据
    # prcp_id1 = data_all1.loc[:, fail_station]
    # data1 = prcp_id1['55248']
    # data1 = data1[:121]
    # data1.index =  pd.to_datetime(data1.index).strftime('%m-%d')
    #
    # # 创建并排的两个子图
    # fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    #
    # # 绘制 h2 数据
    # axes[0].plot(data,  color='#8CA3C3', linestyle='-', linewidth=2.5, markersize=4,label='插值前')
    # axes[0].set_xlabel('日期')
    # axes[0].set_ylabel('降水量(mm)')
    # axes[0].set_xticks(range(0, len(data), 10))
    # axes[0].set_xticklabels(data.index[::10])
    # axes[0].tick_params(axis='both', labelsize=10)
    # axes[0].grid(True, which='major', axis='y', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5, 5))
    # axes[0].grid(True, which='both', axis='x', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5, 5))
    # axes[0].text(0.05, 0.95, '(a)插值前', transform=axes[0].transAxes, fontsize=10, verticalalignment='top',
    #              horizontalalignment='left')
    # # axes[0].legend()
    #
    # # 绘制 h3 数据
    # axes[1].plot(data1,  color='#D2ADA8', linestyle='-', linewidth=2.5, markersize=4,label='插值后')
    # axes[1].set_xlabel('日期')
    # axes[1].set_xticks(range(0, len(data1), 10))
    # axes[1].set_xticklabels(data1.index[::10],   fontsize=9)
    # axes[1].tick_params(axis='y', left=False, labelleft=False,labelsize=9)
    # axes[1].grid(True, which='major', axis='y', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5, 5))
    # axes[1].grid(True, which='both', axis='x', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5, 5))
    # axes[1].text(0.05, 0.95, '(b)插值后', transform=axes[1].transAxes, fontsize=10, verticalalignment='top',
    #              horizontalalignment='left')
    # # axes[1].legend()
    # plt.tight_layout()
    # plt.show(block=True)
    # plt.savefig(r'C:\任务\test1\质量判断图\缺失值检查(55248_1980)',dpi=300)

    """ 重复值检查 """

    # value_1 = ['1011111111', '1110111111','1101111111']
    # condition_1_old = ((df1 == value_1[0]) | (df1 == value_1[1]) | (df1 == value_1[2]))  # 插值后的质量判断
    # data_sum_old1 = condition_1_old.sum().sum()
    # # condition_1 = (df == value_1)  # 插值后的质量判断
    # # data_sum1 = condition_1.sum().sum()
    #
    # # 筛选出为True的列(前)
    # columns_with_true1_old = condition_1_old.any(axis=0)
    # columns_with_true_names1_old  = columns_with_true1_old [columns_with_true1_old ].index.tolist()
    #
    # b1_old  = data_all2[columns_with_true_names1_old ].iloc[:,0:1]  # 获取列对应的值
    # c1_old  = condition_1_old[columns_with_true_names1_old ].iloc[:,0:1]  # 获取列对应的标记值
    # h1_old  = b1_old [c1_old ].dropna(how='all') # 获取标记对应的值
    #
    # # 选取2011与2012年的数据
    # # 插值前
    # b1_old.index = pd.to_datetime(b1_old.index)
    # b1_old = b1_old.loc['2011-11':'2012-12']
    # #插值后
    # h1 = data_all1[columns_with_true_names1_old ].iloc[:,0:1]
    # h1.index = pd.to_datetime(h1.index)
    # h1 = h1.loc['2011-11':'2012-12']
    #
    # # 创建并排的两个子图
    # fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    #
    # # 绘制 h2 数据
    # axes[0].plot(b1_old,  color='#8CA3C3', linestyle='-', linewidth=1, markersize=4,label='插值前')
    # axes[0].set_xlabel('日期')
    # axes[0].set_ylabel('降水量(mm)')
    # axes[0].tick_params(axis='y', labelsize=10)
    # axes[0].grid(True, which='major', axis='y', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5,5))
    # axes[0].grid(True, which='both', axis='x', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5,5))
    # axes[0].text(0.05, 0.95, '(a)插值前', transform=axes[0].transAxes, fontsize=10, verticalalignment='top',
    #              horizontalalignment='left')
    # # axes[0].legend()
    #
    # # 绘制 h3 数据
    # axes[1].plot(h1,  color='#D2ADA8', linestyle='-', linewidth=1, markersize=4,label='插值后')
    # axes[1].set_xlabel('日期')
    # axes[1].tick_params(axis='y', left=False, labelleft=False,labelsize=9)
    # axes[1].grid(True, which='major', axis='y', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5,5))
    # axes[1].grid(True, which='both', axis='x', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5,5))
    # axes[1].text(0.05, 0.95, '(b)插值后', transform=axes[1].transAxes, fontsize=10, verticalalignment='top',
    #              horizontalalignment='left')
    # # axes[1].legend()
    # plt.tight_layout()
    # # plt.show(block=True)
    # plt.savefig(rf"C:\任务\test1\质量判断图\重复值检查_{h1_old.columns[0]}(2011.11-2012.11).png",dpi=300)

    """ 超世界记录检查 """

    # value_4 = '1111011111'
    # condition_4 = (df == value_4)  # 插值前的质量判断
    # data_sum = condition_4.sum().sum()
    #
    # # 筛选出为True的列
    # columns_with_true4 = condition_4.any(axis=0)
    # columns_with_true_names4 = columns_with_true4[columns_with_true4].index.tolist()
    #
    # b4 = data_all[columns_with_true_names4]  # 获取列对应的值
    # c4 = condition_4[columns_with_true_names4] # 获取列对应的标记值
    #
    # h4 = b4[c4].dropna(how='all') # 获取标记对应的值  57395 2017-01-30  3059.6999
    #
    # # 插值后
    # h5 = data_all1.loc[h4.index[0],h4.columns[0]]  # 57395 2017-01-30  0.26
    # print(f"不可能的值为{h4} \n 界限值: prcp_min = {PRCP_MIN_VALUE} prcp_max = {PRCP_MAX_VALUE}")

    """ 条纹检查 """

    # value_5 = '1111101111'
    # condition_5_old = (df == value_5) # 插值前的质量判断
    # data_sum_old = condition_5_old.sum().sum()
    # # condition_5 = (df == value_5)  # 插值后的质量判断
    # # data_sum = condition_5.sum().sum()
    #
    # # 筛选出为True的列
    # columns_with_true = condition_5_old.any(axis=0)
    # columns_with_true_names = columns_with_true[columns_with_true].index.tolist()
    #
    # b = data_all[columns_with_true_names]  # 获取列对应的值
    # c = condition_5_old[columns_with_true_names] # 获取列对应的标记值
    #
    # h = b[c].dropna(how='all') # 获取标记对应的值
    # # 插值前的数据
    # h1 = b.loc[h.index[0]:h.index[-1]]
    # h1.index = pd.to_datetime(h1.index).strftime('%m-%d')
    # # 插值后的数据
    # h2 = data_all1[columns_with_true_names]
    # h3 = h2.loc[h.index[0]:h.index[-1]]
    # h3.index = pd.to_datetime(h3.index).strftime('%m-%d')
    #
    # # 创建并排的两个子图
    # fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    #
    # # 绘制 h2 数据
    # axes[0].plot(h1, color='black', linestyle='None', marker='o', markersize=2)
    # axes[0].set_xlabel('日期')
    # axes[0].set_ylabel('降水量 (mm)')
    # axes[0].set_xticks(range(0, len(h1), 6))
    # axes[0].set_xticklabels(h1.index[::6],   fontsize=9)
    # axes[0].tick_params(axis='y', labelsize=10)
    # axes[0].grid(True, which='major', axis='y', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5,5))
    # axes[0].grid(True, which='both', axis='x', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5,5))
    # # axes[1].text(0.05, 0.95, '(a)插值前', transform=axes[1].transAxes, fontsize=10, verticalalignment='top',
    # #              horizontalalignment='left')
    #
    # # 绘制 h3 数据
    # axes[1].plot(h3, color='black', linestyle='None', marker='o', markersize=2)
    # axes[1].set_xlabel('日期')
    # axes[1].set_xticks(range(0, len(h3), 6))
    # axes[1].set_xticklabels(h3.index[::6],   fontsize=10)
    # axes[1].tick_params(axis='y', left=False, labelleft=False,labelsize=10)
    # axes[1].grid(True, which='major', axis='y', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5,5))
    # axes[1].grid(True, which='both', axis='x', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5,5))
    # # axes[1].text(0.05, 0.95, '(b)插值后', transform=axes[1].transAxes, fontsize=10, verticalalignment='top',
    # #              horizontalalignment='left')
    # plt.tight_layout()
    # # plt.show(block=True)
    # plt.savefig(rf'C:\任务\test1\质量判断图\条纹检查({b.columns[0]}_2016)',dpi=300)
    # print('ok')

    """ 频率检查(被标记站点的值没有出现变化，可能是缺失值插值之后导致窗口内的百分位数发生了变化，从而标记值被取消) """

    # value_6 = '1111110111'
    # condition_6_old = (df == value_6) # 插值前的质量判断
    # data_sum_old6 = condition_6_old.sum().sum()
    # # condition_6 = (df1 == value_6)  # 插值后的质量判断
    # # data_sum6 = condition_6.sum().sum()
    #
    # # 筛选出被标记的站点
    # columns_with_true6 = condition_6_old.any(axis=0)
    # columns_with_true_names6 = columns_with_true6[columns_with_true6].index.tolist()
    #
    # b6 = data_all[columns_with_true_names6].iloc[:,0:1] # 获取列对应的值（插值前）
    # c6 = condition_6_old[columns_with_true_names6].iloc[:,0:1] # 获取列对应的标记值
    # h6 = b6[c6].dropna(how='all') # 获取标记对应的值
    #
    # h2 = data_all1[columns_with_true_names6].iloc[:, 0:1] # 获取列对应的值（插值后）
    #
    # # 获取数据的百分位数
    # days = structure_date(pd.to_datetime(b6.index))
    # days.index = pd.to_datetime(b6.index)
    # b66 = b6.iloc[:,0]
    # h22 = h2.iloc[:, 0]
    #
    # percentiles_pre = build_percentiles1(b66, days, DATES_366)[:,0]
    # percentiles_next = build_percentiles1(h22, days, DATES_366)[:,0]  # 获取第30百分位数
    # percentiles_pre = pd.DataFrame(percentiles_pre)
    # percentiles_next = pd.DataFrame(percentiles_next)
    # month_day = [(dt(1980, 1, 1) + timedelta(days=i)).strftime('%m-%d') for i in range(len(percentiles_pre))]
    # percentiles_pre.index = [str(i) for i in month_day ]
    # percentiles_next.index = [str(i) for i in month_day ]
    #
    # # 插值前的数据
    # h1 = b6.loc[h6.index[0]:h6.index[-1]]
    # h1.index = pd.to_datetime(h1.index).strftime('%m-%d')
    # merge1 = pd.concat([h1,percentiles_pre],axis=1).loc[:h1.index[-1],:]
    # # 插值后的数据
    # h3 = h2.loc[h6.index[0]:h6.index[-1]]
    # h3.index = pd.to_datetime(h3.index).strftime('%m-%d')
    # merge2 = pd.concat([h3,percentiles_next],axis=1).loc[:h3.index[-1],:]
    #
    # # 创建并排的两个子图
    # fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    #
    # # 绘制 h2 数据
    # axes[0].plot(merge1.iloc[:,0], color='black', linestyle='None', marker='o', markersize=2)
    # axes[0].plot(merge1.iloc[:,1], color='gray', linestyle='-', linewidth=1)
    # axes[0].set_xlabel('日期')
    # axes[0].set_ylabel('降水量 (mm)')
    # axes[0].set_xticks(range(0, len(h1), 10))
    # axes[0].set_xticklabels(h1.index[::10],   fontsize=9)
    # axes[0].tick_params(axis='y', labelsize=9)
    # axes[0].grid(True, which='major', axis='y', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5, 5))
    # axes[0].grid(True, which='both', axis='x', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5, 5))
    # axes[0].text(0.05, 0.95, '(a)插值前', transform=axes[0].transAxes, fontsize=10, verticalalignment='top',
    #              horizontalalignment='left')
    #
    # # 绘制 h3 数据
    # axes[1].plot(merge2.iloc[:,0], color='black', linestyle='None', marker='o', markersize=2)
    # axes[1].plot(merge2.iloc[:,1], color='gray', linestyle='-', linewidth=1)
    # axes[1].set_xlabel('日期')
    # axes[1].set_xticks(range(0, len(h3), 10))
    # axes[1].set_xticklabels(h3.index[::10],   fontsize=9)
    # axes[1].tick_params(axis='y', left=False, labelleft=False,labelsize=9)
    # axes[1].grid(True, which='major', axis='y', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5, 5))
    # axes[1].grid(True, which='both', axis='x', linestyle=':', color='#D3D3D3', linewidth=0.5,dashes=(5, 5))
    # axes[1].text(0.05, 0.95, '(b)插值后', transform=axes[1].transAxes, fontsize=10, verticalalignment='top',
    #              horizontalalignment='left')
    # plt.tight_layout()
    # # plt.show(block=True)
    # plt.savefig(rf'C:\任务\test1\质量判断图\频率检查({h6.columns[0]}(2021.1-2022.1)).png',dpi=300)
    # # print('ok')

    """ 间隙检查 """

    # value_7 = '1111111011'
    # condition_7 = (df == value_7)  # 插值前的质量判断
    # data_sum = condition_7.sum().sum()
    #
    # # 筛选出为True的列
    # columns_with_true7 = condition_7.any(axis=0)
    # columns_with_true_names7 = columns_with_true7[columns_with_true7].index.tolist()
    #
    # b7 = data_all[columns_with_true_names7].iloc[:,0:1]  # 获取列对应的值
    # c7 = condition_7[columns_with_true_names7].iloc[:,0:1]  # 获取列对应的标记值
    #
    # # 插值前的数据
    # h7 = b7[c7].dropna(how='all') # 获取标记对应的值 #插值前  54848 1999-08-12  619.7
    #
    # prcp1 = data_all[h7.columns[0]]
    # prcp1.index = pd.to_datetime(prcp1.index).month
    # prcp1_mar = prcp1.loc[8]
    # vals_rng = pd.Series(sorted(prcp1_mar[np.logical_and(not_nan(prcp1_mar), prcp1_mar > 0)]))
    #
    # # 插值后的数据
    # h2 = data_all1[columns_with_true_names7].iloc[:,0:1]
    # h3 = h2.loc[h7.index[0]:h7.index[-1]]
    # h3.index = pd.to_datetime(h3.index).strftime('%m-%d')  #插值后  54848 1999-08-12 28.313364
    #
    # prcp2 = data_all1[h7.columns[0]]
    # prcp2.index = pd.to_datetime(prcp2.index).month
    # prcp2_mar = prcp2.loc[8]
    # vals_rng2 = pd.Series(sorted(prcp2_mar[np.logical_and(not_nan(prcp2_mar), prcp2_mar > 0)]))
    # print('ok')
    #
    # # 可视化(簇状柱状图)
    # # 定义柱形图的宽度和类别
    # bar_width = 45
    # bin_edges = np.arange(0, max(vals_rng.max(), vals_rng2.max()) + 100, 100)  # 设置柱形图的分组
    # bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2  # 计算柱形图的中心位置
    # # 计算每个分组的频率
    # vals_rng_hist, _ = np.histogram(vals_rng, bins=bin_edges)
    # vals_rng2_hist, _ = np.histogram(vals_rng2, bins=bin_edges)
    # # 创建图形和坐标轴
    # fig, ax = plt.subplots(figsize=(6, 4))
    # # 绘制簇状柱形图
    # ax.bar(bin_centers - bar_width / 2, vals_rng_hist, bar_width, label='插值前', color='#C8D7EB', edgecolor='gray',alpha=0.6,)
    # ax.bar(bin_centers + bar_width / 2, vals_rng2_hist, bar_width, label='插值后', color='#FAEBC7', edgecolor='gray',alpha=0.6,)
    # # 添加标签和标题
    # ax.set_xlabel('降水(mm)')
    # ax.set_ylabel('频率')
    # ax.set_xticks(bin_centers)  # 设置x轴标签为每个分组的中心
    # ax.set_xticklabels([int(x) for x in bin_edges[:-1]])  # 以区间显示x轴标签
    # ax.arrow(630,90,0,-60,head_width=6,
    #           head_length=6,linewidth=1,color='black')
    # ax.legend()
    # # 显示图形
    # plt.tight_layout()
    # # plt.show(block=True)
    # plt.savefig(rf'C:\任务\test1\质量判断图\间隙检查({h7.columns[0]}_{h7.index[0]}).png',dpi=300)

    """ 气候异常值检验 """

    # value_8 = '1111111101'
    # condition_8_old = (df == value_8) # 插值前的质量判断
    # data_sum_old8 = condition_8_old.sum().sum()
    #
    # # 筛选出为True的列
    # columns_with_true8 = condition_8_old.any(axis=0)
    # columns_with_true_names8 = columns_with_true8[columns_with_true8].index.tolist()
    #
    # b8 = data_all[columns_with_true_names8].iloc[:,0:1]  # 获取列对应的值
    # c8 = condition_8_old[columns_with_true_names8].iloc[:,0:1] # 获取列对应的标记值
    # h8 = b8[c8].dropna(how='all') # 获取标记对应的值  58553 2013-10-07 376.0
    #
    # # 插值前数据
    # prcp = data_all[h8.columns[0]]
    # tavg = data_tavg[h8.columns[0]]
    # flags_prcp = np.ones(prcp.size)
    # target_date =dt.strptime(h8.index[0], '%Y-%m-%d')
    # days = pd.to_datetime(prcp.index)
    # days = [(timestamp,timestamp.year,timestamp.month,timestamp.day,timestamp.strftime('%Y-%m-%d'),
    #      (timestamp - pd.Timestamp(f'{timestamp.year}-01-01')).days + 1) for timestamp in days]
    # percentile_95, vals_rng, m = qa_clim_outlier(prcp, tavg, days, flags_prcp, target_date)
    #
    # # 插值后数据
    # prcp1 = data_all1[h8.columns[0]]
    # h8_1 = prcp1.loc[h8.index]    # 插值后的数据值  58553 2013-10-07 23.949286
    # flags_prcp1 = np.ones(prcp1.size)
    # target_date1 =dt.strptime(h8.index[0], '%Y-%m-%d')
    # percentile_95_1, vals_rng1, m = qa_clim_outlier(prcp1, tavg, days, flags_prcp1, target_date1)
    #
    # # 可视化(簇状柱状图)
    # # 定义柱形图的宽度和类别
    # bar_width = 20
    # bin_edges = np.arange(0, max(vals_rng.max(), vals_rng1.max()) + 50, 50)  # 设置柱形图的分组
    # bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2  # 计算柱形图的中心位置
    # # 计算每个分组的频率
    # vals_rng_hist, _ = np.histogram(vals_rng, bins=bin_edges)
    # vals_rng2_hist, _ = np.histogram(vals_rng1, bins=bin_edges)
    # # 创建图形和坐标轴
    # fig, ax = plt.subplots(figsize=(10,6))
    # # 绘制簇状柱形图
    # ax.bar(bin_centers - bar_width / 2, vals_rng_hist, bar_width, label='插值前', color='#C8D7EB', edgecolor='black',alpha=0.6,)
    # ax.bar(bin_centers + bar_width / 2, vals_rng2_hist, bar_width, label='插值后', color='#FAEBC7', edgecolor='black',alpha=0.6,)
    # # 添加标签和标题
    # ax.set_xlabel('降水(mm)')
    # ax.set_ylabel('频率')
    # ax.set_xticks(bin_centers)  # 设置x轴标签为每个分组的中心
    # ax.set_xticklabels([int(x) for x in bin_edges[:-1]])  # 以区间显示x轴标签
    # plt.text(percentile_95, 53, f'插值前阈值 = {percentile_95:.2f}mm',
    #          horizontalalignment='center', color='black')
    # ax.arrow(percentile_95,50,0,-40,head_width=3,
    #           head_length=4,linewidth=1,color='black')
    # plt.text(percentile_95_1, 53, f'插值后阈值 = {percentile_95_1:.2f}mm',
    #          horizontalalignment='right', color='black')
    # ax.arrow(percentile_95_1,50,0,-40,head_width=3,
    #           head_length=4,linewidth=1,color='black')
    # ax.legend()
    # # 显示图形
    # plt.tight_layout()
    # # plt.show(block=True)
    # plt.savefig(rf'C:\任务\test1\质量判断图\气候异常值检查({h8.columns[0]}_{h8.index[0]}).png',dpi=300)

    """ 空间一致性检查 """

    # value_9 = '1111111110'
    # condition_9_old = (df == value_9) # 插值前的质量判断
    # data_sum_old9 = condition_9_old.sum().sum()
    #
    # # 筛选出为True的列(前)
    # columns_with_true9_old = condition_9_old.any(axis=0)
    # columns_with_true_names9_old  = columns_with_true9_old [columns_with_true9_old ].index.tolist()
    #
    # b9_old  = data_all[columns_with_true_names9_old ]  # 获取列对应的值
    # c9_old  = condition_9_old[columns_with_true_names9_old ] # 获取列对应的标记值
    # h9_old  = b9_old [c9_old ].dropna(how='all') # 获取标记对应的值
    #
    # b9  = data_all1[columns_with_true_names9_old ]  # 获取列对应的值
    # h9_old  = b9 [c9_old].dropna(how='all') # 获取标记对应的值
    #
    # # 57776 1991/9/8 42.0

    print('ok')


