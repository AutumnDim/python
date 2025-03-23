# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 18:52:15 2024

@author: hqm
"""
import pandas as pd 
import numpy as np 
import rasterio 
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
dmsp_path = r"C:\Users\hqm\Downloads\dsmp校正.tif"
npp_path = r"C:\Users\hqm\Downloads\zhnpp.tif"
X = rasterio.open(npp_path).read(1).flatten()  
Y = rasterio.open(dmsp_path).read(1).flatten()  

# 删除无效值
valid_mask = (X > 0) & (Y > 0)  # 保留正值
X_clean = X[valid_mask].reshape(-1, 1)
Y_clean = Y[valid_mask].reshape(-1, 1)

log_X = np.log(X_clean)
log_Y = np.log(Y_clean)

# 使用线性回归模型拟合
model = LinearRegression().fit(log_X, log_Y)

# 获取回归系数
A_log = model.intercept_[0]  # ln(A)
B = model.coef_[0][0]  # 斜率 B
A = np.exp(A_log)  # A的真实值
