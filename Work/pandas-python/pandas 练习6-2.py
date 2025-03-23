# -*- coding: utf-8 -*-
"""
Created on Sat May 18 09:07:14 2024

@author: hqm
"""
import pandas as pd
import datetime
data = pd.read_csv(r"D:\厚德学习\Pandas__Python\pandas_exercises-master\06_Stats\Wind_Stats\wind.data", sep= '\s+', parse_dates=[[0,1,2]])
data.head()
# sep = "\s+"：这指定了CSV文件中的分隔符为任意空白字符（一个或多个空格）。

# parse_dates = [[0,1,2]]：这将CSV文件的前三列（索引为0, 1, 2）组合并解析为一个单一的日期时间列。
#parse_dates [[col1,col2]]以时间格式-------read_csv
    # parse_dates=True : 尝试解析index为日期格式；
    # parse_dates=[0,1,2,3,4] : 尝试解析0，1，2，3，4列为时间格式；
    # parse_dates=[[’考试日期’,‘考试时间’]] :传入多列名，尝试将其解析并且拼接起来,parse_dates[[0,1,2]]也有同样的效果；
    # parse_dates={’考试安排时间’:[‘考试日期’,‘考试时间’]}，将会尝试解析日期和时间拼接起来，并将列名重置为‘考试安排时间’；
    # 注意：重置后列名不能和原列名重复
#https://blog.csdn.net/qq_34292369/article/details/114026626


def fix_century(x):
    year = x.year - 100 if x.year > 1989 else x.year
    return datetime.date(year, x.month, x.day)
data['Yr_Mo_Dy'] = data['Yr_Mo_Dy'].apply(fix_century)
data.head()

data['Yr_Mo_Dy'] = pd.to_datetime(data['Yr_Mo_Dy'])
k = data.set_index('Yr_Mo_Dy')
k.head()




# 计算一列中有多少空值
data.isnull().sum()


data.shape[0] - data.isnul






# data.sum().sum()：计算数据框中所有数值的总和。
# data.sum()沿每列求和，返回一个包含每列总和的Series，然后再调用一次.sum()对这些列总和求和，得到所有数值的总和。
# data.notna().sum().sum()：计算数据框中所有非缺失值的数量。
# data.notna()生成一个布尔数据框，其中True表示非缺失值，False表示缺失值。然后，sum()沿每列求和，返回每列中非缺失值的数量。再对这些列的非缺失值数量求和，得到数据框中所有非缺失值的总数量。


data.sum().sum() / data.notna().sum().sum()
data.describe(percentiles=[]) # 百分比



day_stats = pd.DataFrame()
day_stats['min'] = data.min(axis = 1)
day_stats['max'] = data.max(axis = 1)
day_stats['mean'] = data.mean(axis = 1)
day_stats['std'] = data.std(axis = 1)

day_stats.head()

data.groupby(data.index.to_period('M')).mean()
data.groupby(data.index.to_period('W')).mean()# 将索引转换为按周分组的周期

k = data.resample('W').agg(['min','max','mean','std'])
k.loc[k.index[1:53],'RPT':'MAL'].head(10)









































