# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 19:09:57 2025

@author: hqm
"""
import pandas as pd
import numpy as np

# 读取表格数据
df = pd.read_csv(r"C:\Users\hqm\Desktop\工作簿1.csv", index_col=0)

# 创建全零矩阵容器
inverted_matrix = pd.DataFrame(np.zeros_like(df, dtype=df.values.dtype),
                              index=df.index,
                              columns=df.columns)
# 矩阵倒置操作（优化边界条件）
n = len(df)
for i in range(n):
    inverted_matrix.iloc[i, i] = df.iloc[i, i]  # 对角线不变
    for j in range(i+1, n):
        # 确保不超出列范围（处理非方阵情况）
        if j < df.shape[1]:
            inverted_matrix.iloc[j, i] = df.iloc[i, j]
            inverted_matrix.iloc[i, j] = df.iloc[j, i]

