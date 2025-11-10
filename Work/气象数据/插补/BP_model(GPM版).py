# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 11:02:28 2024

@author: 25153
"""

import re
import os
import torch
import datetime
import glob as gb
import pandas as pd
import numpy as np
from tqdm import tqdm
import torch.nn as nn  
import torch.optim as optim
from datetime import timedelta
import torch.utils.data as Data
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime as dt
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error

def calculate_stats(y_true, y_pred):

    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    correlation = y_true.corr(y_pred)
    r2 = r2_score(y_true, y_pred)

    return rmse, mae, correlation, r2

def day_drawing(feature_all,feature_all_ghcnd,feature_8d,feature_year):
    # 对比GPM的天尺度
    plt.figure(figsize=(20, 6))
    plt.plot(feature_all.index, feature_all['prcp'], label='prcp', nameor='#2ca02c', linestyle='-', linewidth=1,
             markersize=4)
    plt.plot(feature_all.index, feature_all['gpm_prcp_d'], label='gpm_prcp_d', nameor='#7f7f6f', linestyle='-', linewidth=1,
             markersize=4)
    plt.xlabel('day')
    plt.ylabel('Precipitation(mm)')
    plt.title('Total day precipitation of gaize')
    plt.xticks(ticks=range(0, len(feature_all.index), 180,), labels=feature_all.index[::180], fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    # plt.show(block=True)
    plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\GPM卫星数据插值\人工神经网络\趋势-天-gpm2.png", dpi=300, bbox_inches='tight')

    rmse1, mae1, correlation1, r21 = calculate_stats(feature_all['gpm_prcp_d'], feature_all['prcp'])
    slope, intercept = np.polyfit(feature_all['gpm_prcp_d'], feature_all['prcp'], 1)  # 一阶多项式拟合，即线性拟合
    trend_line = slope * feature_all['gpm_prcp_d'] + intercept
    plt.figure(figsize=(10, 6))
    plt.scatter(feature_all['gpm_prcp_d'], feature_all['prcp'], nameor='#1f77b4', alpha=0.6)  # 深蓝色
    plt.plot(feature_all['gpm_prcp_d'], trend_line, nameor='#7f7f7f')  # 深红色
    plt.text(0.05, 0.95, f'R² = {r21:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.90, f'R = {correlation1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.85, f'MAE = {mae1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.80, f'RMSE = {rmse1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.title('Comparison between the prcp and gpm_prcp_d')
    plt.xlabel('gpm_prcp_d(mm)')
    plt.ylabel('prcp(mm)')
    plt.grid(False)
    # plt.show(block=True)
    plt.savefig(r"E:\实习\atm\降水的贝叶斯分类\GPM卫星数据插值\人工神经网络\散点-天-gpm2.png", dpi=300, bbox_inches='tight')


    # 对比GHCND的天尺度
    feature_all_ghcnd.columns = ['prcp','gpm_prcp_d','gpm_prcp_mon','gpm_prcp_year','ghcnd_prcp_d']
    plt.figure(figsize=(20, 6))
    plt.plot(feature_all_ghcnd.index, feature_all_ghcnd['prcp'], label='prcp', nameor='#2ca02c', linestyle='-', linewidth=2,
             markersize=4)
    plt.plot(feature_all_ghcnd.index, feature_all_ghcnd['gpm_prcp_d'], label='gpm_prcp_d', nameor='#7f7f6f', linestyle='-', linewidth=1,
             markersize=4)
    plt.plot(feature_all_ghcnd.index, feature_all_ghcnd['ghcnd_prcp_d'],  label='GHCND',nameor='#ff7f0e', linestyle='-', linewidth=1)
    plt.xlabel('day')
    plt.ylabel('Precipitation(mm)')
    plt.title('Total day precipitation of gaize')
    plt.xticks(ticks=range(0, len(feature_all_ghcnd.index), 180,), labels=feature_all_ghcnd.index[::180], fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    # plt.show(block=True)
    plt.savefig(r"E:\实习\atm\降水的贝叶斯分类\GPM卫星数据插值\人工神经网络\趋势-天-ghcnd2.png", dpi=300, bbox_inches='tight')

    feature_all_ghcnd = feature_all_ghcnd.dropna()
    rmse1, mae1, correlation1, r21 = calculate_stats(feature_all_ghcnd['ghcnd_prcp_d'], feature_all_ghcnd['prcp'])
    slope, intercept = np.polyfit(feature_all_ghcnd['ghcnd_prcp_d'], feature_all_ghcnd['prcp'], 1)  # 一阶多项式拟合，即线性拟合
    trend_line = slope * feature_all_ghcnd['ghcnd_prcp_d'] + intercept
    plt.figure(figsize=(10, 6))
    plt.scatter(feature_all_ghcnd['ghcnd_prcp_d'], feature_all_ghcnd['prcp'], nameor='#1f77b4', alpha=0.6)  # 深蓝色
    plt.plot(feature_all_ghcnd['ghcnd_prcp_d'], trend_line, nameor='#7f7f7f')  # 深红色
    plt.text(0.05, 0.95, f'R² = {r21:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.90, f'R = {correlation1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.85, f'MAE = {mae1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.80, f'RMSE = {rmse1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.title('Comparison between the prcp and ghcnd_prcp_d')
    plt.xlabel('ghcnd_prcp_d(mm)')
    plt.ylabel('prcp(mm)')
    plt.grid(False)
    # plt.show(block=True)
    plt.savefig(r"E:\实习\atm\降水的贝叶斯分类\GPM卫星数据插值\人工神经网络\散点-天-ghcnd2.png", dpi=300, bbox_inches='tight')

    # 对比GHCND的8d尺度
    feature_8d.columns = ['prcp','ghcnd_prcp_8d']
    plt.figure(figsize=(20, 6))
    plt.plot(feature_8d.index, feature_8d['prcp'], label='prcp', nameor='#2ca02c', linestyle='-', linewidth=2,
             markersize=4)
    plt.plot(feature_8d.index, feature_8d['ghcnd_prcp_8d'],  label='GHCND',nameor='#ff7f0e', linestyle='-', linewidth=2)
    plt.xlabel('8D')
    plt.ylabel('Precipitation(mm)')
    plt.title('Total 8D precipitation of gaize')
    plt.xticks(ticks=range(0, len(feature_8d.index), 32,), labels=feature_8d.index[::32], fontsize=10, rotation=45)
    plt.yticks(fontsize=10)
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    # plt.show(block=True)
    plt.savefig(r"E:\实习\atm\降水的贝叶斯分类\GPM卫星数据插值\人工神经网络\趋势-天(8D)-ghcnd2.png", dpi=300, bbox_inches='tight')

    feature_8d = feature_8d.dropna()
    rmse1, mae1, correlation1, r21 = calculate_stats(feature_8d['ghcnd_prcp_8d'], feature_8d['prcp'])
    slope, intercept = np.polyfit(feature_8d['ghcnd_prcp_8d'], feature_8d['prcp'], 1)  # 一阶多项式拟合，即线性拟合
    trend_line = slope * feature_8d['ghcnd_prcp_8d'] + intercept
    plt.figure(figsize=(10, 6))
    plt.scatter(feature_8d['ghcnd_prcp_8d'], feature_8d['prcp'], nameor='#1f77b4', alpha=0.6)  # 深蓝色
    plt.plot(feature_8d['ghcnd_prcp_8d'], trend_line, nameor='#7f7f7f')  # 深红色
    plt.text(0.05, 0.95, f'R² = {r21:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.90, f'R = {correlation1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.85, f'MAE = {mae1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.80, f'RMSE = {rmse1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.title('Comparison between the prcp and ghcnd_prcp_8d')
    plt.xlabel('ghcnd_prcp_8d(mm)')
    plt.ylabel('prcp(mm)')
    plt.grid(False)
    # plt.show(block=True)
    plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\GPM卫星数据插值\人工神经网络\散点-天(8D)-ghcnd2.png", dpi=300, bbox_inches='tight')

    # 对比GHCND的年尺度
    feature_year.columns = ['prcp','ghcnd_prcp_year']

    plt.figure(figsize=(12, 4))
    plt.plot(feature_year.index, feature_year['prcp'], label='prcp', nameor='#2ca02c', linestyle='-', linewidth=2,
             markersize=4)
    plt.plot(feature_year.index, feature_year['ghcnd_prcp_year'],  label='GHCND',nameor='#ff7f0e', linestyle='-', linewidth=2)
    plt.xlabel('Year')
    plt.ylabel('Precipitation(mm)')
    plt.yticks()
    plt.xticks(feature_year.index)
    plt.title('Total year precipitation of gaize')
    plt.legend()
    plt.grid(False)
    plt.tight_layout()
    # plt.show(block=True)
    plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\GPM卫星数据插值\人工神经网络\趋势-天(年)-ghcnd2.png", dpi=300, bbox_inches='tight')

    feature_year = feature_year.dropna()
    rmse1, mae1, correlation1, r21 = calculate_stats(feature_year['ghcnd_prcp_year'], feature_year['prcp'])
    slope, intercept = np.polyfit(feature_year['ghcnd_prcp_year'], feature_year['prcp'], 1)  # 一阶多项式拟合，即线性拟合
    trend_line = slope * feature_year['ghcnd_prcp_year'] + intercept
    plt.figure(figsize=(10, 6))
    plt.scatter(feature_year['ghcnd_prcp_year'], feature_year['prcp'], nameor='#1f77b4', alpha=0.6)  # 深蓝色
    plt.plot(feature_year['ghcnd_prcp_year'], trend_line, nameor='#7f7f7f')  # 深红色
    plt.text(0.05, 0.95, f'R² = {r21:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.90, f'R = {correlation1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.85, f'MAE = {mae1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.text(0.05, 0.80, f'RMSE = {rmse1:.2f}', transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
    plt.title('Comparison between the prcp and ghcnd_prcp_year')
    plt.xlabel('ghcnd_prcp_year(mm)')
    plt.ylabel('prcp(mm)')
    plt.grid(False)
    # plt.show(block=True)
    plt.savefig(r"D:\实习\atm\降水的贝叶斯分类\GPM卫星数据插值\人工神经网络\散点-天(年)-ghcnd2.png", dpi=300, bbox_inches='tight')

class Network(nn.Module):  
    def __init__(self, input_size):  
        super(Network, self).__init__()  
        self.fc1 = nn.Linear(input_size, 500)   # 表示输入特征后，有100维的输出，意思是第一个隐藏层有100个节点 （进行线性变换，权重会在这个过程中自动创建）、
        # print(self.fc1.weight)  # 权重矩阵
        # print(self.fc1.bias)  # 偏置向量
        self.dropout1 = nn.Dropout(0.3)   # 使隐藏层的一些节点失活，提高模型的泛化能力
        self.fc2 = nn.Linear(500, 250)
        # print(self.fc2.weight)  # 权重矩阵
        # print(self.fc2.bias)  # 偏置向量
        self.dropout2 = nn.Dropout(0.3)  
        self.fc3 = nn.Linear(250, 100)
        # print(self.fc3.weight)  # 权重矩阵
        # print(self.fc3.bias)  # 偏置向量
        self.dropout3 = nn.Dropout(0.3)  
        self.fc4 = nn.Linear(100, 1)         # 定义三个隐藏层，一个输出层

        # 定义激活函数  (三个不同的激活函数)
        self.relu = nn.ReLU()  
        self.leaky_relu = nn.LeakyReLU(negative_slope=0.01)  
        self.tanh = nn.Tanh()

    def forward(self, x):  
        x = self.tanh(self.fc1(x))  # 第一层使用 Tanh  
        x = self.dropout1(x)  
        x = self.leaky_relu(self.fc2(x))  # 第二层使用 Leaky ReLU  
        x = self.dropout2(x)  
        x = self.relu(self.fc3(x))  # 第三层使用 ReLU  
        x = self.dropout3(x)  
        x = self.fc4(x)  # 输出层  
        return x

def train_epoch(model, train_loader, optimizer, loss_func):
    model.train()  # 设置模型为训练模式
    train_loss = 0
    train_num = 0

    for batch_idx, (data, label) in enumerate(train_loader):
        optimizer.zero_grad()  # 清空梯度
        output = model(data)  # 前向传播
        loss = loss_func(output, label)  # 计算损失

        loss.backward()  # 反向传播
        optimizer.step()  # 更新参数

        train_loss += loss.item() * data.size(0)  # 累积损失
        train_num += data.size(0)  # 计数样本数量

    average_loss = train_loss / train_num
    return average_loss

def modle_BP(station, year_start, year_end, feature_data,var,output_path):
    """
    参数：
    station (int): 要查询的气象站点编号。
    year_start (int): 数据收集的起始年份。
    year_end (int): 数据收集的结束年份。
    feature (dataframe): 站点周围五个站点的数据。
    """
    # 固定随机种子
    np.random.seed(42)
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    # 读取数据并构造数据集
    d_all2 = feature_data.dropna()
    d_all2 = d_all2.loc[f'{year_start}':f'{year_end}']
    ar = np.array(d_all2)
    X_new = ar[:, :-1]  # 特征
    y_new = ar[:, -1:]  # 目标

    # 切分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X_new, y_new, test_size=0.3, random_state=20)

    # 数据标准化处理
    scale = StandardScaler()
    x_train_std = scale.fit_transform(X_train)
    x_test_std = scale.transform(X_test)

    X_train_t = torch.from_numpy(x_train_std.astype(np.float32))     # 将样本处理为张量
    y_train_t = torch.from_numpy(y_train.astype(np.float32))
    X_test_t = torch.from_numpy(x_test_std.astype(np.float32))
    y_test_t = torch.from_numpy(y_test.astype(np.float32))

    # 将训练数据处理为数据加载器
    train_data = Data.TensorDataset(X_train_t, y_train_t)     #将数据封装为适合 DataLoader 处理的格式
    train_loader = Data.DataLoader(dataset=train_data, batch_size=64, shuffle=True, num_workers=1)     # 自动将数据分批次处理

    model = Network(X_train.shape[1])
    optimizer = optim.Adam(model.parameters(), lr=0.01)     # 构建一个优化器对象来优化参数  model.parameters()返回模型中所有可训练参数的迭代器
    loss_func = nn.MSELoss()       # 损失函数
    train_loss_all = []

    best_loss = float('inf')
    model_save_path = output_path + os.sep + f'{station}_{var}_best_model.pth'

    # 使用 ProcessPoolExecutor 并行处理每个周期
    with ProcessPoolExecutor() as executor:
        futures = []
        for epoch in range(500):
            futures.append(executor.submit(train_epoch, model, train_loader, optimizer, loss_func))

        for future in tqdm(futures, total=len(futures), desc='Processing iterations'):
            average_loss = future.result()

            # 额外的评估逻辑
            with torch.no_grad():
                y_train_pred = model(X_train_t)
                rmse_train = np.sqrt(mean_squared_error(y_train_t.numpy(), y_train_pred.numpy()))

            if average_loss < best_loss:
                with torch.no_grad():
                    y_test_pred = model(X_test_t)
                    rmse_test = np.sqrt(mean_squared_error(y_test_t.numpy(), y_test_pred.numpy()))

                r_value_train = r2_score(y_train_t.numpy(), y_train_pred.numpy())
                r_value_test = r2_score(y_test_t.numpy(), y_test_pred.numpy())

                best_loss = average_loss
                torch.save(model.state_dict(), model_save_path)

    return model_save_path

def BP_model_pred(model_path, target, feature):
    ''''
    model_payh: 模型路径
    target: 该站点数据
    feature: 该站点周围五个站点的数据
    '''

    missing = target.iloc[:,-1].isnull()
    ar_2016 = np.array(feature[missing])

    model = Network(ar_2016.shape[1])
    model.load_state_dict(torch.load(model_path,map_location='cpu', weights_only=True)) #只加载权重（官方设置提高效率的办法）
    model.eval()

    # 数据标准化处理
    scale = StandardScaler()
    x_new_std_2016 = scale.fit_transform(ar_2016)
    X_new_t_2016 = torch.from_numpy(x_new_std_2016.astype(np.float32))
    with torch.no_grad():
        ar_2016_pred = model(X_new_t_2016)
    arr = ar_2016_pred.numpy()
    arr = arr.flatten()  # 转换为一维数组

    target.loc[missing,target.columns[-1]] = arr

    return target

def filter_years(df, start_year=2001, end_year=2023):
    """
    筛选数据
    """
    df['year'] = df.index.year
    filtered = df[df['year'].isin(range(start_year, end_year))]
    return filtered.drop('year', axis=1)

def out_date_by_day(year, day):
    '''
    根据输入的年份和天数计算对应的日期
    '''
    first_day = datetime.datetime(year, 1, 1)
    add_day = datetime.timedelta(days=day - 1)
    return datetime.datetime.strftime(first_day + add_day, "%Y-%m-%d")

def clean_data(data_all):
    """
    将特定值替换为NaN
    """
    to_replace = [999990.0, 999999.0, 999998.0, 32766.0]
    return data_all.replace(to_replace, np.nan)

def acquire_data(sta,paths_data):
    """
    获取站点40年的原始数据
    """
    paths = gb.glob(paths_data)
    feature = pd.DataFrame()
    data_all = pd.DataFrame()

    for p in paths:
        year = re.split('[_.]',p)[-2]
        data = pd.read_csv(p)
        data = data.drop(['Unnamed: 0'],axis=1)
        data = data.set_index('台站编号')
        data.index = data.index.astype(str)

        if sta in data.index or f"{sta}.0" in data.index:
            # 选择包含指定台站编号的行
            sta_data = data.loc[[index for index in data.index if index in [sta, f"{sta}.0"]]]
            sta_data = sta_data.iloc[0,:]
            sta_data1 = pd.DataFrame(sta_data[3:])

            # 将天数据转换为日期数据
            days = data.columns[3:].str.extract(r'D(\d+)')[0].astype(int)
            date = pd.Series(days).apply(lambda x: out_date_by_day(int(year), x))
            sta_data1.index = list(date)
            data_all = pd.concat([data_all, sta_data1])
        else:
            pass

    feature = pd.concat([feature, clean_data(data_all)], axis=1)

    return feature

def merge_feature(df_day, df_mon, df_year, sta, name,scale=None):
    """
    合并标签的特征
    """
    if scale == '8d' or scale == 'day':
        df_day['month'] = np.nan
        for time in df_mon.index:
            year, month = map(int, time.split('-'))
            h = df_day[(df_day.index.year == year) & (df_day.index.month == month)]
            df_day.loc[h.index, 'month'] = df_mon.loc[time].values[0]

        for y in df_year.index:
            h1 = df_day[df_day.index.year == y]
            df_day.loc[h1.index, 'year'] = df_year.loc[y].values[0]
        df_day.index = pd.to_datetime(df_day.index).strftime('%Y-%m-%d')

        feature_all = pd.concat([df_day, sta], axis=1)
        d = int(df_day.index[1][-1]) - 1
        feature_all.columns = [f'gpm_prcp_{d}d', 'gpm_prcp_mon', 'gpm_prcp_year', name]

        return feature_all
    else:
        for i in range(1, len(df_year) + 1):
            year_str = f'20{i:02d}'
            h = df_mon[df_mon.index.str.startswith(year_str)]
            df_mon.loc[h.index, 'year'] = df_year.loc[int(year_str)][0]

        feature_all = pd.concat([df_mon, sta], axis=1)
        feature_all.columns = ['gpm_prcp_mon', 'gpm_prcp_year', 'prcp']

        return feature_all

if __name__ == '__main__':

    path_data = r"F:\气象数据\stations_new\降水量\precipitation_time_2020_*.txt"  # 原始降水量数据
    path_sta = r"F:\实习\整理\low_r2_8d.csv"       # R方低于0.8的数据
    path_qa = r"F:\实习\atm\降水批量质量判断\QC_prcp_bin.csv"  # 质量判断数据
    output_path = r"F:\实习\整理\人工神经网络"          # 数据输出路径

    start_year,end_year = 2001,2023
    var = 'prcp'

    # 获取台站和质量判断数据
    sta = pd.read_csv(path_sta,dtype=str).set_index('Unnamed: 0')
    QA = pd.read_csv(path_qa, dtype=str).set_index('Unnamed: 0')
    QA.index = pd.to_datetime(QA.index)
    QA = filter_years(QA)

    # 获取GHCND数据
    GHCND = pd.DataFrame()
    for y in range(2001, 2021):
        path_GHCND = rf"F:\实习\atm\data\station\Station_data\PRCP1\PRCP_{y}.csv"
        df_ghcnd = pd.read_csv(path_GHCND, dtype={'台站编号': str})
        df_ghcnd.drop('Unnamed: 0', axis=1, inplace=True)

        df_ghcnd = df_ghcnd.set_index('台站编号')
        df_ghcnd = df_ghcnd[df_ghcnd.index.isin([f'CH0000{station}' for station in sta.index])]
        df_ghcnd = df_ghcnd.iloc[:, 3:]

        data_name = df_ghcnd.columns
        days = data_name.map(lambda x: int(re.search(r'D(\d+)', x).group(1)) if re.search(r'D(\d+)', x) else None)
        date = pd.Series(days).apply(lambda x: out_date_by_day(int(y), x))
        df_ghcnd.columns = list(date)
        GHCND = pd.concat([GHCND, df_ghcnd.T])
        print(y)
    GHCND.index = pd.to_datetime(GHCND.index)

    all_year = pd.DataFrame()
    all_8d = pd.DataFrame()
    all_d = pd.DataFrame()

    for name in tqdm(sta.index,total=len(sta.index),desc='Procession stations'):
        # 获取多年降水数据
        prcp = acquire_data(name, path_data)
        prcp.index = pd.to_datetime(prcp.index)
        prcp = filter_years(prcp)

        # 未通过质量判断的也赋值为nan
        QA_name = QA[name].rename('质量信息')
        prcp1 = pd.concat([QA_name, prcp], axis=1)
        prcp1['质量信息'] = prcp1['质量信息'].apply(lambda x: np.nan if '0' in x else x)
        prcp1.loc[prcp1['质量信息'].isnull(), prcp1.columns[1]] = np.nan
        prcp1.drop('质量信息', axis=1, inplace=True)

        # 标签数据的年、月、8天和日汇总
        sta_day = prcp1.copy()
        sta_day.index = pd.to_datetime(sta_day.index).strftime('%Y-%m-%d')

        # 获取GPM数据
        df_all = pd.concat(
            [pd.read_csv(rf"F:\GPM_2001\GPM_{y}.csv")[name].rename(lambda x: f'{y}-{x + 1}') for y in range(start_year, end_year)]
        )
        df_all.index = pd.date_range(start=f'{start_year}-01-01', periods=len(df_all), freq='D')

        # 特征数据的年、月、8天和日汇总
        df_year = pd.DataFrame(df_all.groupby(df_all.index.year).sum())
        df_mon = pd.DataFrame(df_all.resample('ME').sum())
        df_mon.index = pd.to_datetime(df_mon.index).strftime('%Y-%m')
        df_8d = pd.DataFrame(df_all.resample('8D').sum())
        df_day = pd.DataFrame(df_all.resample('D').sum())

        # 标签和特征数据准备
        # feature_all = merge_feature(df_day,df_mon, df_year,sta_mon,'month')
        # feature_all = merge_feature(df_8d, df_mon, df_year,sta_8d,'8d')
        feature_data = merge_feature(df_day,df_mon,df_year,sta_day,name,'day')
        
        # 模型拟合
        model_path = modle_BP(name,start_year,end_year,feature_data,var,output_path)   # 进行多进程处理

        target = pd.DataFrame(feature_data.iloc[:,-1])
        feature = feature_data.iloc[:,:-1]
        # 模型预测
        reg_day = BP_model_pred(model_path, target, feature)
        reg_day.index = pd.to_datetime(reg_day.index)

        # 预测数据的日，8天，年数据汇总
        reg_year = pd.DataFrame(reg_day[name])
        reg_year = reg_year.groupby(pd.to_datetime(reg_year.index).year).sum()
        reg_8d = pd.DataFrame(reg_day[name])
        reg_8d = reg_8d.resample('8D').sum()
        reg_8d.index = pd.to_datetime(reg_8d.index).strftime('%Y-%m-%d')
        reg_8d.index = pd.to_datetime(reg_8d.index)

        GHCND_year = GHCND[f'CH0000{name}'].groupby(GHCND.index.year).apply(
            lambda x: x.sum() if not x.isna().any() else None)
        GHCND_8d = GHCND[f'CH0000{name}'].resample('8D').apply(lambda x: x.sum() if not x.isna().any() else None)

        merge_year = pd.concat([reg_year[name], GHCND_year], axis=1)
        merge_8d = pd.concat([reg_8d[name], GHCND_8d], axis=1)
        merge_d = pd.concat([reg_day[name], GHCND[f'CH0000{name}']], axis=1)

        GHCND_year_nan = (merge_year[f'CH0000{name}'].isnull().sum() / len(merge_year) * 100).round(2)
        GHCND_8d_nan = (merge_8d[f'CH0000{name}'].isnull().sum() / len(merge_8d) * 100).round(2)
        GHCND_nan = (merge_d[f'CH0000{name}'].isnull().sum() / len(merge_d) * 100).round(2)

        merge_year = merge_year.dropna()
        merge_8d = merge_8d.dropna()
        merge_d = merge_d.dropna()

        rmse_y, mae_y, correlation_y, r2_y = calculate_stats(merge_year[f'CH0000{name}'], merge_year[name])
        rmse_8d, mae_8d, correlation_8d, r2_8d = calculate_stats(merge_8d[f'CH0000{name}'], merge_8d[name])
        rmse_d, mae_d, correlation_d, r2_d = calculate_stats(merge_d[f'CH0000{name}'], merge_d[name])

        evaluate_year = pd.DataFrame(
            {'RMSE': rmse_y, 'MAE': mae_y, 'r': correlation_y, 'R方': r2_y, 'GHCND_nan_percent': GHCND_year_nan},
            index=[name]).round(2)
        evaluate_8d = pd.DataFrame(
            {'RMSE': rmse_8d, 'MAE': mae_8d, 'r': correlation_8d, 'R方': r2_8d, 'GHCND_nan_percent': GHCND_8d_nan},
            index=[name]).round(2)
        evaluate_d = pd.DataFrame(
            {'RMSE': rmse_d, 'MAE': mae_d, 'r': correlation_d, 'R方': r2_d, 'GHCND_nan_percent': GHCND_nan},
            index=[name]).round(2)

        all_year = pd.concat([all_year, evaluate_year])
        all_8d = pd.concat([all_8d, evaluate_8d])
        all_d = pd.concat([all_d, evaluate_d])

    all_year.to_csv(output_path + os.sep + 'evaluate_year.csv')
    all_8d.to_csv(output_path + os.sep + 'evaluate_8d.csv')
    all_d.to_csv(output_path + os.sep + 'evaluate_d.csv')

    # day_drawing(feature_all,feature_all_ghcnd,feature_8d,feature_year)