# -*- coding: utf-8 -*-
"""
Created on Sat May 18 16:44:55 2024

@author: hqm
"""
import pandas as pd
df = pd.read_csv(r"D:\厚德学习\Pandas__Python\python_work\3 输出为excel\2000年～2019年中国各区县降水量年度数据.csv",encoding='gbk')
df1 = pd.read_excel(r"D:\厚德学习\Pandas__Python\python_work\3 输出为excel\县.xlsx")
# 过滤出与县列表一致的县
df2 = df[df['县'].isin(df1)]
# 将数据透视，使每个县为一列，年份为行
df3 = df2.pivot(index='年份', columns='县', values='降水量')
df4 = df3.sort_index(ascending=False)

