# -*- coding: utf-8 -*-
"""
Created on Sat 2024/10/14 19:47
@Author : lyr
"""
import re
import os
import pandas as pd
import numpy as np
import seaborn as sns
import datetime
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error, mean_absolute_error

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def calculate_stats(y_true, y_pred):
    """
    计算结果评估指数
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    correlation = y_true.corr(y_pred)
    r2 = r2_score(y_true, y_pred)

    return rmse, mae, correlation, r2

def out_date_by_day(year, day):
    '''
    根据输入的年份和天数计算对应的日期
    '''
    first_day = datetime.datetime(year, 1, 1)
    add_day = datetime.timedelta(days=day - 1)
    return datetime.datetime.strftime(first_day + add_day, "%Y-%m-%d")

def conditional_sum(x):
    return pd.Series({
        col: x[col].sum() if np.all(~x[col].isna()) else None for col in x.columns
    })

def safe_sum(group):
    if group.isnull().values.any():
        group1 = pd.DataFrame(np.nan, index=[0], columns=group.columns)
    else:
        group1 = pd.DataFrame(group.sum()).T
    return group1

def compute_metrics(col):
    if f'{col}' in GHCND.columns:
        GHCND_year = GHCND[f'{col}'].groupby(GHCND.index.year).apply(
            lambda x: x.sum() if not x.isna().any() else None
        )
        GHCND_8d = GHCND[f'{col}'].resample('8D').apply(
            lambda x: x.sum() if not x.isna().any() else None
        )

        merge_year = pd.concat([data_year[col], GHCND_year], axis=1)
        merge_8d = pd.concat([data_8d[col], GHCND_8d], axis=1)
        merge_d = pd.concat([df_data[col], GHCND[f'{col}']], axis=1)

        GHCND_year_nan = (merge_year[f'{col}'].isnull().sum() / len(merge_year) * 100).round(2)
        GHCND_8d_nan = (merge_8d[f'{col}'].isnull().sum() / len(merge_8d) * 100).round(2)
        GHCND_nan = (merge_d[f'{col}'].isnull().sum() / len(merge_d) * 100).round(2)

        merge_year = merge_year.dropna()
        merge_8d = merge_8d.dropna()
        merge_d = merge_d.dropna()

        # 计算统计指标
        rmse_y, mae_y, correlation_y, r2_y = calculate_stats(merge_year[f'{col}'], merge_year[col])
        rmse_8d, mae_8d, correlation_8d, r2_8d = calculate_stats(merge_8d[f'{col}'], merge_8d[col])
        rmse_d, mae_d, correlation_d, r2_d = calculate_stats(merge_d[f'{col}'], merge_d[col])

        evaluate_year = pd.DataFrame({'RMSE': rmse_y, 'MAE': mae_y, 'r': correlation_y, 'R方': r2_y, 'GHCND_nan_percent': GHCND_year_nan}, index=[col]).round(2)
        evaluate_8d = pd.DataFrame({'RMSE': rmse_8d, 'MAE': mae_8d, 'r': correlation_8d, 'R方': r2_8d, 'GHCND_nan_percent': GHCND_8d_nan}, index=[col]).round(2)
        evaluate_d = pd.DataFrame({'RMSE': rmse_d, 'MAE': mae_d, 'r': correlation_d, 'R方': r2_d, 'GHCND_nan_percent': GHCND_nan}, index=[col]).round(2)

        return evaluate_year, evaluate_8d, evaluate_d
    return None, None, None

def visual_trend(merge_year,merge_8d,merge_d,df_acr,col):
    """
    可视化趋势图
    """
    merge_8d.index = pd.to_datetime(merge_8d.index).strftime('%Y-%m-%d')
    merge_d.index = pd.to_datetime(merge_d.index).strftime('%Y-%m-%d')

    # # 365天准确率可视化
    # plt.figure(figsize=(16, 9))
    # plt.title("朴素贝叶斯分类")
    # plt.plot(range(1, len(df_acr) + 1), df_acr, label='准确率')
    # plt.xlabel('天数')
    # plt.ylabel('准确率')
    # plt.legend()
    # plt.show(block=True)
    # plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\西藏改则\准确率(未通过检验).png", dpi=300, bbox_inches='tight')
    # plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\准确率.png", dpi=300)

    sns.set(style="whitegrid")
    # 年尺度
    plt.figure(figsize=(12, 6))
    plt.plot(merge_year.index, merge_year.iloc[:,0], label=merge_year.columns[0], color='#2ca02c', linestyle='-')
    plt.plot(merge_year.index, merge_year.iloc[:,1],  label=merge_year.columns[1],color='#7f7f6f', linestyle='-')
    plt.xlabel('Year')
    plt.ylabel('Precipitation(mm)')
    plt.title(f'Total annual precipitation of {col}')
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.show(block=True)
    # plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\西藏改则\趋势图(四种数据).png", dpi=300, bbox_inches='tight')

    # 8天尺度
    plt.figure(figsize=(20, 6))
    plt.plot(merge_8d.index, merge_8d.iloc[:,0], label=merge_8d.columns[0], color='#2ca02c', linestyle='-', linewidth=1,
             markersize=4)
    plt.plot(merge_8d.index, merge_8d.iloc[:,1], label=merge_8d.columns[1], color='#ff7f0e', linestyle='-', linewidth=1)
    plt.xlabel('8D')
    plt.ylabel('Precipitation(mm)')
    plt.title(f'Total 8D precipitation of {col}')
    plt.xticks(ticks=range(0, len(merge_8d.index), 32), labels=merge_8d.index[::32], fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.show(block=True)
    # plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\GPM卫星数据插值\趋势-8D-ghcnd.png", dpi=300, bbox_inches='tight')

    # 天尺度
    plt.figure(figsize=(20, 6))
    plt.plot(merge_d.index, merge_d.iloc[:,0], label=merge_d.columns[0], color='#2ca02c', linestyle='-', linewidth=1,
             markersize=4)
    plt.plot(merge_d.index, merge_d.iloc[:,1], label=merge_d.columns[1], color='#ff7f0e', linestyle='-', linewidth=1)
    plt.xlabel('D')
    plt.ylabel('Precipitation(mm)')
    plt.title(f'Total D precipitation of {col}')
    plt.xticks(ticks=range(0, len(merge_d.index), 180), labels=merge_d.index[::180], fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    plt.show(block=True)
    # plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\GPM卫星数据插值\趋势-8D-ghcnd.png", dpi=300, bbox_inches='tight')

def visual_scatter(merge_year, merge_8d, merge_d):
    """
    可视化散点图
    """
    # 年尺度
    rmse1, mae1, correlation1, r21 = calculate_stats(merge_year.iloc[:,1], merge_year.iloc[:,0])
    slope, intercept = np.polyfit(merge_year.iloc[:,1], merge_year.iloc[:,0], 1)  # 一阶多项式拟合，即线性拟合
    trend_line = slope * merge_year.iloc[:,1] + intercept
    plt.figure(figsize=(10, 6))
    plt.scatter(merge_year.iloc[:,1], merge_year.iloc[:,0], color='#1f77b4', alpha=0.6)  # 深蓝色
    plt.plot(merge_year.iloc[:,1], trend_line, color='#7f7f7f')  # 深红色
    plt.text(0.05, 0.95, f'R² = {r21:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.90, f'R = {correlation1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.85, f'MAE = {mae1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.80, f'RMSE = {rmse1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.title('Comparison between the prcp and GHCND')
    plt.xlabel('GHCND(mm)')
    plt.ylabel('prcp(mm)')
    plt.grid(False)
    plt.show(block=True)
    # plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\西藏改则\散点图(对比GHCND).png", dpi=300, bbox_inches='tight')

    # 8天尺度
    rmse2, mae2, correlation2, r22 = calculate_stats(merge_8d.iloc[:,1], merge_8d.iloc[:,0])
    slope, intercept = np.polyfit(merge_8d.iloc[:,1], merge_8d.iloc[:,0], 1)  # 一阶多项式拟合，即线性拟合
    trend_line = slope * merge_8d.iloc[:,1] + intercept
    plt.figure(figsize=(10, 6))
    plt.scatter(merge_8d.iloc[:,1], merge_8d.iloc[:,0], color='#1f77b4', alpha=0.6)  # 深蓝色
    plt.plot(merge_8d.iloc[:,1], trend_line, color='#7f7f7f')  # 深红色
    plt.text(0.05, 0.95, f'R² = {r22:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.90, f'R = {correlation2:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.85, f'MAE = {mae2:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.80, f'RMSE = {rmse2:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.title('Comparison between the prcp and ghcnd_prcp_8d')
    plt.xlabel('ghcnd_prcp_8d(mm)')
    plt.ylabel('prcp(mm)')
    plt.grid(False)
    plt.show(block=True)
    # plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\GPM卫星数据插值\散点-8D-ghcnd.png", dpi=300, bbox_inches='tight')

    # 天尺度
    rmse3, mae3, correlation3, r23 = calculate_stats(merge_d.iloc[:,1], merge_d.iloc[:,0])
    slope, intercept = np.polyfit(merge_d.iloc[:,1], merge_d.iloc[:,0], 1)  # 一阶多项式拟合，即线性拟合
    trend_line = slope * merge_d.iloc[:,1] + intercept
    plt.figure(figsize=(10, 6))
    plt.scatter(merge_d.iloc[:,1], merge_d.iloc[:,0], color='#1f77b4', alpha=0.6)  # 深蓝色
    plt.plot(merge_d.iloc[:,1], trend_line, color='#7f7f7f')  # 深红色
    plt.text(0.05, 0.95, f'R² = {r23:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.90, f'R = {correlation3:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.85, f'MAE = {mae3:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.80, f'RMSE = {rmse3:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.title('Comparison between the prcp and ghcnd_prcp_d')
    plt.xlabel('ghcnd_prcp_d(mm)')
    plt.ylabel('prcp(mm)')
    plt.grid(False)
    plt.show(block=True)
    # plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\GPM卫星数据插值\散点-8D-ghcnd.png", dpi=300, bbox_inches='tight')


if __name__ == '__main__':

    path_data =r"C:\气象数据插值\3数据插值\1缺失值插值\prcp_all.csv"
    path_acr = r"C:\气象数据插值\3数据插值\1缺失值插值\accuracy_all.csv"
    output_path = r"C:\气象数据插值\4插值效果分析\era5_compare"

    df_data = pd.read_csv(path_data,index_col=0)
    df_data.index = pd.to_datetime(df_data.index)

    df_acr = pd.read_csv(path_acr,index_col=0)

    # 计算年和8天总和
    data_year = df_data.groupby(df_data.index.year).sum().round(2)
    data_month = df_data.resample('ME').sum().round(2)
    data_8d = df_data.resample('8D').sum().round(2)

    # # 获取GHCND数据
    # GHCND = pd.DataFrame()
    # for y in range(1980,2021):
    #     path_GHCND = rf"C:\任务\实习\atm\data\station\Station_data\PRCP1\PRCP_{y}.csv"
    #     df_ghcnd = pd.read_csv(path_GHCND, dtype={'台站编号': str})
    #     df_ghcnd.drop('Unnamed: 0',axis=1,inplace=True)
    #
    #     df_ghcnd = df_ghcnd.set_index('台站编号')
    #     df_ghcnd = df_ghcnd[df_ghcnd.index.isin([f'CH0000{station}' for station in df_data.columns])]
    #     df_ghcnd = df_ghcnd.iloc[:,3:]
    #
    #     data_col = df_ghcnd.columns
    #     days = data_col.map(lambda x: int(re.search(r'D(\d+)', x).group(1)) if re.search(r'D(\d+)', x) else None)
    #     date = pd.Series(days).apply(lambda x: out_date_by_day(int(y), x))
    #     df_ghcnd.columns = list(date)
    #     GHCND = pd.concat([GHCND, df_ghcnd.T])
    #     print(y)
    # GHCND.index = pd.to_datetime(GHCND.index)
    # GHCND.columns = [col.replace('CH0000', '') for col in GHCND.columns]
    # print('ok')

    # # 获取CPC数据
    # GHCND = pd.DataFrame()
    # for y in range(1980,2021):
    #     path_GHCND = rf"C:\CPC\CPC_extract_tif\PRCP_{y}.csv"
    #     df_ghcnd = pd.read_csv(path_GHCND, index_col=0)
    #     col = df_ghcnd.columns[df_ghcnd.columns.isin(df_data.columns)]
    #     df_ghcnd = df_ghcnd[col]
    #     df_ghcnd[(df_ghcnd > 10000) | (df_ghcnd < 0)] = np.nan
    #     # df_ghcnd.index = [i for i in range(1,len(df_ghcnd.index)+1)]
    #     # date = pd.Series(df_ghcnd.index).apply(lambda x: out_date_by_day(int(y), x))
    #     # df_ghcnd.index = list(date)
    #     GHCND = pd.concat([GHCND, df_ghcnd])
    #     print(y)
    # GHCND.index = pd.to_datetime(GHCND.index)
    # print('ok')

    # 获取era5数据
    GHCND = pd.DataFrame()
    for y in range(1980,2021):
        path_GHCND = rf"C:\ERA5\PRCP\PRCP_{y}.csv"
        df_ghcnd = pd.read_csv(path_GHCND, index_col=0)
        col = df_ghcnd.columns[df_ghcnd.columns.isin(df_data.columns)]
        df_ghcnd = df_ghcnd[col]
        df_ghcnd[(df_ghcnd > 10000) | (df_ghcnd < 0)] = np.nan
        df_ghcnd.index = [i for i in range(1,len(df_ghcnd.index)+1)]
        date = pd.Series(df_ghcnd.index).apply(lambda x: out_date_by_day(int(y), x))
        df_ghcnd.index = list(date)
        GHCND = pd.concat([GHCND, df_ghcnd])
        print(y)
    GHCND.index = pd.to_datetime(GHCND.index)
    print('ok')

    # 计算评价指标
    incomparable = []
    all_year = pd.DataFrame()
    all_month = pd.DataFrame()
    all_8d = pd.DataFrame()
    all_d = pd.DataFrame()
    month_change_ghcnd = pd.DataFrame()
    # data_year = data_year.iloc[:,411:412]
    for col in tqdm(data_year.columns,total=len(data_year.columns), desc='Processing stations'):

        if col in GHCND.columns and GHCND[col].notna().any():
            # 所有年份一起的对比
            GHCND_year = GHCND[f'{col}'].groupby(GHCND.index.year).apply( lambda x: x.sum() if not x.isna().any() else np.nan)
            GHCND_month = GHCND[f'{col}'].resample('ME').apply(lambda x: x.sum() if not x.isna().any() else np.nan)
            GHCND_8d = GHCND[f'{col}'].resample('8D').apply( lambda x: x.sum() if not x.isna().any() else np.nan)

            merge_year = pd.concat([data_year[col],GHCND_year],axis=1)
            merge_month = pd.concat([data_month[col], GHCND_month], axis=1)
            merge_8d = pd.concat([data_8d[col],GHCND_8d], axis=1)
            merge_d = pd.concat([df_data[col], GHCND[col]], axis=1)

            GHCND_year_nan = (merge_year.iloc[:,1:].isnull().sum()/len(merge_year)*100).round(2)
            GHCND_month_nan = (merge_month.iloc[:,1:].isnull().sum()/len(merge_month)*100).round(2)
            GHCND_8d_nan = (merge_8d.iloc[:,1:].isnull().sum()/len(merge_8d)*100).round(2)
            GHCND_nan = (merge_d.iloc[:,1:].isnull().sum()/len(merge_d)*100).round(2)

            # 可视化趋势
            # visual_trend(merge_year,merge_8d,merge_d,df_acr[col],col)

            merge_year = merge_year.dropna()
            merge_month = merge_month.dropna()
            merge_8d = merge_8d.dropna()
            merge_d = merge_d.dropna()

            # # 分年份的对比
            # merge_d_y = merge_d.groupby(merge_d.index.year).apply(
            #     lambda x: calculate_stats(x[f'{col}'], x[col])
            # )
            # merge_d_y_df = pd.DataFrame(merge_d_y.tolist(), columns=['RMSE', 'MAE', 'r', 'R2'],
            #                              index=merge_d_y.index)
            # merge_8d_y = merge_8d.groupby(merge_8d.index.year).apply(
            #     lambda x: calculate_stats(x[f'{col}'], x[col])
            # )
            # merge_8d_y_df = pd.DataFrame(merge_8d_y.tolist(), columns=['RMSE', 'MAE', 'r', 'R2'],
            #                              index=merge_8d_y.index)

            # ghcnd所有站点的月数据
            # month_change_ghcnd = pd.concat([month_change_ghcnd,GHCND_month],axis=1)

            #可视化散点
            # visual_scatter(merge_year, merge_8d, merge_d)

            if not merge_year.empty:
                rmse_y, mae_y, correlation_y, r2_y = calculate_stats(merge_year.iloc[:, 1], merge_year.iloc[:, 0])
                evaluate_year = pd.DataFrame({'RMSE': rmse_y, 'MAE': mae_y, 'r': correlation_y, 'R方': r2_y,
                                              'GHCND_nan_percent': GHCND_year_nan}, index=[col]).round(2)
                all_year = pd.concat([all_year, evaluate_year])

            if not merge_month.empty:
                rmse_month, mae_month, correlation_month, r2_month = calculate_stats(merge_month.iloc[:, 1],
                                                                                     merge_month.iloc[:, 0])
                evaluate_month = pd.DataFrame(
                    {'RMSE': rmse_month, 'MAE': mae_month, 'r': correlation_month, 'R方': r2_month,
                     'GHCND_nan_percent': GHCND_month_nan}, index=[col]).round(2)
                all_month = pd.concat([all_month, evaluate_month])

            if not merge_8d.empty:
                rmse_8d, mae_8d, correlation_8d, r2_8d = calculate_stats(merge_8d.iloc[:, 1], merge_8d.iloc[:, 0])
                evaluate_8d = pd.DataFrame({'RMSE': rmse_8d, 'MAE': mae_8d, 'r': correlation_8d, 'R方': r2_8d,
                                            'GHCND_nan_percent': GHCND_8d_nan}, index=[col]).round(2)
                all_8d = pd.concat([all_8d, evaluate_8d])

            if not merge_d.empty:
                rmse_d, mae_d, correlation_d, r2_d = calculate_stats(merge_d.iloc[:, 1], merge_d.iloc[:, 0])
                evaluate_d = pd.DataFrame(
                    {'RMSE': rmse_d, 'MAE': mae_d, 'r': correlation_d, 'R方': r2_d, 'GHCND_nan_percent': GHCND_nan},
                    index=[col]).round(2)
                all_d = pd.concat([all_d, evaluate_d])

            # # 每年结果
            # merge_8d_y_df.to_csv(output_path + os.sep + rf'evaluate_8d_yearly\{col}_8d.csv')
            # merge_d_y_df.to_csv(output_path + os.sep + rf'evaluate_d_yearly\{col}_d.csv')
        else:
            incomparable.append(col)


    # 筛选出R方小于0.8的站点
    low_r2_year = all_year[all_year['R方'] < 0.8]
    low_r2_month = all_month[all_month['R方'] < 0.8]
    low_r2_8d = all_8d[all_8d['R方'] < 0.8]
    low_r2_d = all_d[all_d['R方'] < 0.8]

    # 输出结果
    low_r2_year.to_csv(output_path + os.sep + 'low_r2_year.csv')
    low_r2_month.to_csv(output_path + os.sep + 'low_r2_month.csv')
    low_r2_8d.to_csv(output_path + os.sep + 'low_r2_8d.csv')
    low_r2_d.to_csv(output_path + os.sep + 'low_r2_d.csv')

    # 输出不能比较的值
    incomparable = pd.DataFrame(incomparable)
    incomparable.to_csv(output_path + os.sep + 'incomparable_sta.csv')

    # 多年结果
    all_year.to_csv(output_path + os.sep + 'evaluate_year.csv')
    all_month.to_csv(output_path + os.sep + 'evaluate_month.csv')
    all_8d.to_csv(output_path + os.sep + 'evaluate_8d.csv')
    all_d.to_csv(output_path + os.sep + 'evaluate_d.csv')

    # # GHCND和插补数据全部站点月数据结果
    # data_month.to_csv(output_path + os.sep + 'month_change.csv')
    # month_change_ghcnd.to_csv(output_path + os.sep + 'month_change_ghcnd.csv')
    print('ok')






























