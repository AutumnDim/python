# -*- coding: utf-8 -*-
"""
Created on Wed May 15 14:11:35 2024

@author: hqm
"""
import pandas as pd 
import numpy as np
crime = pd.read_csv(r'D:\厚德学习\Pandas__Python\pandas_exercises-master\04_Apply\US_Crime_Rates\US_Crime_Rates_1960_2014.csv')
crime.head()
crime.info()
crime.Year = pd.to_datetime(crime.Year,format='%Y')
crime.info
# pandas.to_datetime(arg, errors='raise', dayfirst=False, yearfirst=False, utc=None, format=None, exact=True, unit=None, infer_datetime_format=False, origin='unix', cache=True)
    # errors：参数raise时，表示传入数据格式不符合是会报错；ignore时，表示忽略报错返回原数据；coerce用NaT时间空值代替。
    # dayfirst:表示传入数据的前两位数为天。如‘030820’——》2020-03-08.
    # yearfirst:表示传入数据的前两位数为年份。如‘030820’——》2003-08-20.
    # format：自定义输出格式，如“%Y-%m-%d”.
    # unit：可以为['D', 'h' ,'m', 'ms' ,'s', 'ns']
    # infer_datetime_format:加速计算
    # origin：自定义开始时间，默认为1990-01-01
    
    
crime = crime.set_index('Year',drop=True)
# 将'Year'列设置为索引，并删除原来的'Year'列
crime.head()

del crime['Total']
crime.head()




# Uses resample to sum each decade
crimes = crime.resample('10AS').sum()

# Uses resample to get the max value only for the "Population" column
population = crime['Population'].resample('10AS').max()

# Updating the "Population" column
crimes['Population'] = population

crimes

#根据时间聚合采样resample
# resample，重新采样，是对原样本重新处理的一个方法，
# 是一个对常规时间序列数据重新采样和频率转换的便捷的方法。重新取样时间序列数据。
# 按年代分组并求和（注意不对Population列求和，而是求平均值）
# decade_groups = crime.resample('10AS').agg({
#   'Crime Rate': 'sum',
  #  'Population': 'mean'  # 或者其他适当的聚合方式
  
  # 按年代分组并求和（注意不对Population列求和，而是求平均值）
# decade_groups = crime.resample('10AS').agg({
#     'Crime Rate': 'sum',
 #   'Population': 'mean'  # 或者其他适当的聚合方式
# })
  





crime.idxmax(0)
# idxmax() 是 pandas 中的一个函数，
# 用于找出指定轴上最大值的第一个出现位置的索引（行标签）。
# 当你调用 idxmax(0) 时，它会返回每一列最大值所在的索引标签。 
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
