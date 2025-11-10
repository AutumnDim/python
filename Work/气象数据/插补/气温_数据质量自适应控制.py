# -*- coding: utf-8 -*-
"""
Created on Sat 2024/12/9 11:13
@Author : lyr


"""
import qa.qa_prcp1 as qa
import QW_bayesi_QA as QA
import hanshu
import gc
import os
import prcp_QA
import numpy as np
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from db.station_data import station_data,TMAX_FLAG,PRCP_FLAG,TMIN_FLAG,TAVG
from concurrent.futures import ProcessPoolExecutor, as_completed
from db.station_data import LON, LAT, STN_ID, YEAR, DATE, MONTH, TMIN, TMAX, PRCP, YMD, DAY, YDAY

YMD = u'年月日'
DATE = u'日期'
YDAY = u'年日'
YEAR = u'年'
MONTH = u'月'
DAY = u'日'

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

def output_file(output_path, result_all, accuracy_all, r2_all, fail_station, name=None):

    file_path = os.path.join(output_path, name)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    else:
        pass

    result_all.to_csv(file_path + os.sep + f'prcp_all({len(fail_station)}).csv')
    accuracy_all.to_csv(file_path + os.sep + f'accuracy_all({len(fail_station)}).csv')
    r2_all.to_csv(file_path + os.sep + f'r2_all({len(fail_station)}).csv')

    return file_path

def process_station(task):
    name, data_prcp, data_qa, df2, prcp, tavg, value = task
    print(name)
    df_qa = data_qa[name]

    # 筛选附近的七个站点数据
    dist = QA.distance(name, df2)

    # 获取目标站点和附近7个站点的降水数据
    df, target, feature = QA.acquire_inter_data(data_prcp, dist, prcp, df_qa, name, value)

    # 进行贝叶斯分类预测
    grouped_all, accuracies = QA.Naive_Bayes(df, target, feature)
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
    r2 = QA.validate_kriging(grouped_all, target, xi, yi, x1, y1, elevation1)
    r2 = pd.DataFrame({f'{target}': [r2]})

    # 进行泛克里金插值
    result = QA.interpolate_values(grouped_all, target, xi, yi, x1, y1, elevation1)

    return result, accuracies, r2, name

def Common_interpolation(prcp, data_qa, df2, prcp_id, value, days, tavg):

    result_all = pd.DataFrame()
    accuracy_all = pd.DataFrame()
    r2_all = pd.DataFrame()

    tasks = [(name, data_prcp, data_qa, df2, prcp, tavg, value) for name, data_prcp in prcp_id.items()]
    DEBUG1 = False
    if DEBUG1:
        results = []
        for t in tqdm(tasks, total=len(tasks), desc='Processing station (Single Thread)'):
            results.append(process_station(t))
    else:
        with ProcessPoolExecutor() as executor:
            results = list(tqdm(executor.map(process_station, tasks),
                              total=len(tasks), desc='Processing station (Multi Process)'))

    for result, accuracies, r2, name in results:
        print(f'{name} is ok')

        if tavg is None:
            pass
        else:
            tavg2 = tavg[name]

        result1 = result[name]
        flags_prcp = np.ones(result1.size)

        for v in value:
            position = v.find('0')
            if position == 6:
                # 获取站点及其对应值的条件阈值
                b = qa.qa_frequent(result1, days, flags_prcp)
                b1 = pd.DataFrame(b).drop_duplicates()
                if not b1.empty:
                    b2 = b1.set_index("date")

                    # 将插值结果限制在阈值内
                    for d in b2.index:
                        if result.loc[d, :][0] >= b2.loc[d, b2.columns[-1]]:
                            per1 = b2.loc[d, b2.columns[-2]]
                            per2 = b2.loc[d, b2.columns[-1]]
                            result.loc[d, :] = np.random.uniform(per1, per2)
            elif position == 7:
                result = qa.qa_gap(result1, days, flags_prcp)
            elif position == 8:
                result = qa.qa_clim_outlier(result1, tavg2, days, flags_prcp)

        result_all = pd.concat([result_all, result], axis=1)
        accuracy_all = pd.concat([accuracy_all, accuracies], axis=1)
        r2_all = pd.concat([r2_all, r2], axis=1)

    return result_all, accuracy_all, r2_all

def QA_1(df2, prcp, data_qa):

    """
    1、缺失值
    （方法：利用此套数据源附近7个站点的数据插值）
    步骤：插值前质量判断——缺失值插值——插值后质量判断
    """

    # 获取未通过质量判断的站点
    value_1 = ['0111111111']
    condition_1 = (data_qa == value_1[0])
    fail_station = condition_1.sum()[condition_1.sum() > 0].index
    prcp_id = prcp.loc[:, fail_station]
    prcp = prcp.T

    result_all, accuracy_all, r2_all = Common_interpolation(prcp, data_qa, df2, prcp_id, value_1, None, None)

    file_path1 = output_file(output_path, result_all, accuracy_all, r2_all, fail_station, '1缺失值插值')

    # 替换插值后的数据
    prcp.loc[:, result_all.columns] = result_all
    prcp.to_csv(file_path1 + os.sep + 'prcp_all.csv')
    print('缺失值检查完成')
    return prcp

def QA_2(df2, prcp, data_qa, path_era5):

    """
    2/3/4、不同年份之间的重复值/不同年份之间相同月份的重复值
    （原因：附近站点数据全部缺失，用多年平均值填充，值相同使得插值结果相同
    方法：由于附近站点的数据缺失真值，引入era5数据作为特征）
    """

    # 获取era5数据
    # era5 = QA.acquire_prcp(path_era5, 'era5')
    # era5.columns = pd.to_datetime(era5.columns)
    # era5[era5 == -0.0] = 0.0
    # era5 = era5[era5.index.isin(prcp.columns)]

    # 获取未通过质量判断的站点
    value = ['1011111111', '1110111111','1101111111']
    condition_1 = ((data_qa == value[0]) | (data_qa == value[1]) | (data_qa == value[2]))  # 插值后的质量判断
    fail_station = condition_1.sum()[condition_1.sum() > 0].index
    prcp_id = prcp.loc[:, fail_station]

    result_all, accuracy_all, r2_all = Common_interpolation(data_qa, df2, prcp_id, value, None, None)  #

    # 数据输出
    file_path2 = output_file(output_path, result_all, accuracy_all, r2_all, fail_station, '2重复值插值')

    # 全部站点插值后的数据
    prcp.loc[:, result_all.columns] = result_all
    prcp.to_csv(file_path2 + os.sep + 'prcp_all.csv')
    print('重复值检查完成')
    return prcp

def QA_5(df2, prcp, data_qa):

    """
    5,不可能的值/6,20个以上的连续值
    （方法：利用此套数据源附近7个站点的数据插值,因为插值结果限制在降水分级范围内，所以首次插值后一定会消除掉）
    """

    # 获取插值后的质量判断和降水数据
    # path1 = r"D:\实习\test1\重复值插值\prcp_all.csv"
    # prcp = pd.read_csv(path1)

    # 获取未通过质量判断的站点
    value_5 = '1111011111'
    value_6 = '1111101111'
    value = [value_5, value_6]
    condition_1 = ((data_qa == value_5) | (data_qa == value_6))
    fail_station = condition_1.sum()[condition_1.sum() > 0].index
    prcp_id = prcp.loc[:, fail_station]
    prcp = prcp.T

    result_all, accuracy_all, r2_all = Common_interpolation(prcp, data_qa, df2, prcp_id, value, None, None)

    file_path3 = output_file(output_path, result_all, accuracy_all, r2_all, fail_station, '3超记录插值')

    # 替换插值后的数据
    prcp = prcp.T
    prcp.loc[:, result_all.columns] = result_all
    prcp.to_csv(file_path3 + os.sep + 'prcp_all.csv')
    print('超记录检查完成')
    return prcp

def QA_7(df2, prcp, data_qa):

    """
    7,不是必须连续的频繁相同的值
    （方法：利用此套数据源附近7个站点的数据插值，插值结果限制次百分比和百分比位数之间的随机值）
    """

    np.random.random(42)
    # 获取未通过质量判断的站点
    value_7 = ['1111110111']
    condition_1 = (data_qa == value_7[0])
    fail_station = condition_1.sum()[condition_1.sum() > 0].index
    prcp_id = prcp.loc[:, fail_station]
    prcp = prcp.T

    # prcp_id = prcp1.loc[:, fail_station]  # 制图

    days = structure_date(prcp_id.index)
    days.index = prcp_id.index

    result_all, accuracy_all, r2_all = Common_interpolation(prcp, data_qa, df2, prcp_id, value_7, days, None)

    file_path4 = output_file(output_path, result_all, accuracy_all, r2_all, fail_station, '4频率插值')

    # 替换插值后的数据
    prcp = prcp.T
    prcp.loc[:, result_all.columns] = result_all
    prcp.to_csv(file_path4 + os.sep + 'prcp_all.csv')
    print('频率检查完成')
    return prcp

def QA_8(df2, prcp, data_qa):

    """
    8,频率分布中尾部与异常值分离
    （方法：利用此套数据源附近7个站点的数据插值，插值结果限制为低于百分位数阈值的随机值）
    """

    # 获取未通过质量判断的站点
    value_8 = ['1111111011']
    condition_1 = (data_qa == value_8[0])
    fail_station = condition_1.sum()[condition_1.sum() > 0].index
    prcp_id = prcp.loc[:, fail_station]
    prcp = prcp.T

    days = structure_date(prcp_id.index)
    days.index = prcp_id.index

    result_all, accuracy_all, r2_all = Common_interpolation(prcp, data_qa, df2, prcp_id, value_8, days, None)

    file_path5 = output_file(output_path, result_all, accuracy_all, r2_all, fail_station, '5间隙插值')

    # 替换插值后的数据
    prcp = prcp.T
    prcp.loc[:, result_all.columns] = result_all
    prcp.to_csv(file_path5 + os.sep + 'prcp_all.csv')
    print('间隙检查完成')
    return prcp

def QA_9(df2, prcp, data_qa,path_prcp):

    """
    9,气候异常值检测
    （方法：利用此套数据源附近7个站点的数据插值，插值结果限制为第90百分位和第95百分位数计算阈值间的随机值）
    """

    # 获取插值后的质量判断和降水数据
    tavg1 = QA.acquire_prcp(path_prcp, 'tavg')
    # 筛选站点并填充时间序列
    tavg1 = tavg1[tavg1.index.isin(prcp.columns)]  # 筛选
    tavg1 = tavg1.T
    tavg1.index = pd.to_datetime(tavg1.index)
    tavg1 = pd.concat([prcp.iloc[:, 0], tavg1],axis=1).iloc[:, 1:]  # 填充时间序列
    sta = set(prcp.columns) - set(tavg1.columns)
    tavg1[list(sta)] = np.nan                     # 填充站点

    # 获取未通过质量判断的站点
    value_9 = ['1111111101']
    condition_1 = (data_qa == value_9[0])
    fail_station = condition_1.sum()[condition_1.sum() > 0].index
    prcp_id = prcp.loc[:, fail_station]
    tavg1 = tavg1.loc[:, fail_station]
    prcp = prcp.T

    days = structure_date(prcp_id.index)
    days.index = prcp_id.index

    result_all, accuracy_all, r2_all = Common_interpolation(prcp, data_qa, df2, prcp_id, value_9, days, tavg1)

    file_path6 = output_file(output_path, result_all, accuracy_all, r2_all, fail_station, '6气候异常值插值')

    # 替换插值后的数据
    prcp = prcp.T
    prcp.loc[:, result_all.columns] = result_all
    prcp.to_csv(file_path6 + os.sep + 'prcp_all.csv')
    print('气候异常值检查完成')
    return prcp

def QA_10(df2, prcp, data_qa):

    """
    10,未被任何相邻值证实
    （方法：利用此套数据源附近7个站点的数据插值，插值结果限制为低于百分位数阈值的随机值）
    """
    # 获取未通过质量判断的站点
    value_10 = ['1111111110']
    condition_1 = (data_qa == value_10[0])
    fail_station = condition_1.sum()[condition_1.sum() > 0].index
    prcp_id = prcp.loc[:, fail_station]
    prcp = prcp.T

    result_all, accuracy_all, r2_all = Common_interpolation(prcp, data_qa, df2, prcp_id, value_10, None, None)

    file_path7 = output_file(output_path, result_all, accuracy_all, r2_all, fail_station, '7空间一致性插值')

    # 替换插值后的数据
    output_path_file = file_path7 + os.sep + 'prcp_all.csv'
    prcp = prcp.T
    prcp.loc[:, result_all.columns] = result_all
    prcp.to_csv(output_path_file)
    print('空间一致性检查完成')
    return file_path7, prcp_id.columns, prcp

if __name__ in '__main__':

    np.random.random(42)

    # condition_prcp = ['缺失值','不同年份之间的重复值', '同一年中不同月份的重复值', '不同年份之间相同月份的重复值', '不可能的值',
    #                   '20个或以上连续的值', '不是必须连续的频繁出现的值', '频率分布中尾部与其余值异常分离', '20个以下的非零值',
    #                   '未被任何相邻值证实']

    path_era5 = r"C:\ERA5\PRCP\PRCP_*.csv"                  # era5降水数据
    path_prcp = r"E:\所实习\气温数据插值处理\3缺失值插值\平均日最高气温\prcp_data\prcp_*.csv"      # 插值后的降水数据
    path = r"E:\所实习\气温数据插值处理\2数据质量控制\日平均最高温度\插值后质量控制\QC_prcp_bin.csv"          # 插值后的质量判断
    path_nan = r"E:\所实习\气温数据插值处理\1数据缺失值概况\日平均最高温度\多年缺失值占比.csv"           # 缺失值占比数据
    path_lon = r"E:\所实习\气温原始数据\unique_station_TMAX_1980_2022.txt"  # 经纬度数据
    path_tavg = r"C:\降水归档\降水数据插值(国内)_气象局\0降水数据\格式整理数据\平均气温\TAVG_*.csv"            # 平均气温数据
    output_path = r"C:\降水归档\降水数据插值(国内)_气象局\3数据插值"                               # 数据输出路径

    # 筛选符合条件的站点
    df_nan = pd.read_csv(path_nan, index_col=0)
    df = pd.read_csv(path_lon, index_col=0, dtype={'台站编号':str})

    if len(str(df_nan.index[0])) == 11 :
        nan = df_nan[df_nan < 60].dropna().index.astype(str)
    else:
        nan = df_nan[df_nan < 80].dropna().index.astype(str)
        df = df[df['台站编号'].str.startswith('5')]

    df = df.drop_duplicates(subset=['经度', '纬度'], keep='first')
    df2 = df.set_index('台站编号')
    df2 = df2[df2.index.isin(nan)]

    # 获取降水数据
    prcp = QA.acquire_prcp(path_prcp, 'prcp')
    prcp = prcp.T
    prcp.index = pd.to_datetime(prcp.index)

    # 获取质量判断数据
    data_qa = pd.read_csv(path, dtype=str, index_col=0)  # 插值后的质量判断
    data_qa.index = pd.to_datetime(data_qa.index)

    "测试:添加其他质量控制"
    # # 定义要替换的目标值和替换模式
    # target_value = "1111111111"
    # replacement_patterns = [
    #     "1011111111", "1101111111", "1110111111",
    #     "1111011111", "1111101111", "1111110111",
    #     "1111111110", "1111111101", "1111111011"
    # ]
    #
    # # 找出所有值为"1111111111"的位置
    # mask = data_qa.apply(lambda x: x == target_value)
    # eligible_positions = np.argwhere(mask.values)
    #
    # # 确保有足够的位置进行替换
    # total_replacements_needed = len(replacement_patterns) * 10
    # if len(eligible_positions) < total_replacements_needed:
    #     raise ValueError(
    #         f"Not enough '{target_value}' values in data. Need at least {total_replacements_needed}, found {len(eligible_positions)}")
    #
    # # 随机选择位置
    # np.random.shuffle(eligible_positions)
    # selected_positions = eligible_positions[:total_replacements_needed]
    #
    # # 分配替换模式
    # for i, pattern in enumerate(replacement_patterns):
    #     start_idx = i * 10
    #     end_idx = (i + 1) * 10
    #     positions_for_pattern = selected_positions[start_idx:end_idx]
    #
    #     for pos in positions_for_pattern:
    #         row_idx, col_idx = pos
    #         data_qa.iloc[row_idx, col_idx] = pattern
    # data_qa.to_csv(r"E:\所实习\气温数据插值处理\2数据质量控制\日平均最高温度\插值后质量控制\QC_prcp_bin.csv")

    """
    不同判断条件的自适应策略（判断条件为顺序质量控制）
    """

    # prcp = QA_1(df2, prcp, data_qa)               # 缺失值检查（缺失值插补完成再质量判断后进行下一步的检查，这个不需要调用）

    prcp = QA_2(df2, prcp, data_qa, path_era5)    # 重复值检查

    prcp = QA_5(df2, prcp, data_qa)               # 超世界记录检查 连续值检查

    prcp = QA_7(df2, prcp, data_qa)               # 频率检查

    prcp = QA_8(df2, prcp, data_qa)               # 间隙检查

    prcp = QA_9(df2, prcp, data_qa, path_tavg)    # 气候异常值检查

    output_path_end, stations, prcp = QA_10(df2, prcp, data_qa)          # 空间一致性检查
    print(stations)

    # 限制在范围之内
    # input_path_file = output_path + os.sep + os.sep + r'\7空间一致性插值\prcp_all.csv'
    hanshu.Output_annually(prcp,df2,output_path_end)        # 转换为每年的格式
    tavg_path = os.path.split(path_tavg)[0]

    years = range(1980, 2023)
    list2 = []

    with ProcessPoolExecutor() as executor:
        future_to_year = {
            executor.submit(prcp_QA.read, year, output_path_end, tavg_path, df2): year for year in years
        }

        for future in tqdm(as_completed(future_to_year), total=len(future_to_year), desc="Processing years"):
            year = future_to_year[future]

            try:
                li = future.result()
                list2.extend(li)

            except Exception as e:
                print(f"Error processing year {year}: {e}")
                import traceback
                traceback.print_exc()

            del li
            gc.collect()

    stn_da = station_data(list2, datetime(min(years), 1, 1), datetime(max(years), 12, 31))
    del list2
    gc.collect()
    print('ok')
    stns = np.unique(stn_da.load_stns())

    days = stn_da.days
    for s in tqdm(stations,desc="Processing stations"):
        stn = stns[stns[STN_ID] == s][0]
        stn_obs = stn_da.load_all_stn_obs(np.array(s),set_flagged_nan=False)   #返回最小、最大气温、降水、平均气温
        df_prcp = qa.checks_qa(stn, stn_da, stn_obs[PRCP], stn_obs[TAVG], days)
        print(df_prcp)
        prcp[s] = df_prcp
    prcp.to_csv(output_path + os.sep + '7空间一致性插值/prcp_all1.csv')

    # 输出分年结果
    output_path1 = os.path.join(output_path, '8最终结果')
    if not os.path.exists(output_path1):
        os.makedirs(output_path1)
    else:
        pass

    hanshu.Output_annually(prcp,df2,output_path1)

    print("ok")
