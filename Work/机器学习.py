# -*- coding: utf-8 -*-
"""
Created on Mon Sep  1 18:48:28 2025

@author: 中科院地理所
"""

import numpy as np
import pandas as pd
import rasterio
import shap
from tqdm import tqdm
import glob, os
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import optuna


# def func(path):
#     with rasterio.open(path) as src:
#         name = os.path.splitext(os.path.basename(path))[0]
#         nodata = np.float32(src.nodata)    # 获取无效值
#         profile = src.profile
#         profile.data['dtype'] = 'float32'    # 转换数据类型，float32为8为小数，若担心精度，可改为64
#         profile.data['nodata'] = np.nan
        
#         data = src.read().astype('float32')  # 读取栅格矩阵
#         data = data.reshape(-1,1)    # 重塑形状为一列多行
#         data[data == nodata] = np.nan
#         data = pd.DataFrame(data, columns=[name])    # 转成Dataframe
#         # data = data.sample(n=300_0000, random_state=42)
#     return data
# for year in range(2000,2020,5):
# # 读取数据
# dt = pd.DataFrame()    #定义空数组存储数据
# path = glob.glob(r"F:\论文写作\欣雨学姐\机器学习\数据\数据\自变量\2000\fin\*.tif")    # 两个应变量都读进去了，要去掉一个
# for tif in tqdm(path):
#     df = func(tif)
#     dt = pd.concat([dt, df], axis=1)  # 合并 DataFrame
# dt = dt.dropna(how='any')

# x = dt.drop(['EVI'], axis=1)    # 用因变量的标签索引
# y = dt['EVI']
# path = r"F:\work\地理所\生态风险\data\TEST1\2256.csv"
# datak = pd.read_csv(path, encoding='gbk')
#k = 112
path = r"E:\地上生物量\提取特征\特征值.csv"
datak = pd.read_csv(path, encoding='gbk')
datak = datak.dropna(how='any')
# 2. 划分特征和目标变量 - 修正y的形状
y = datak.iloc[:, 0].values  # 特征变量
x = datak.iloc[:, 1:].values
#x = datak[['TAVG', 'PRCP', 'DEM_QTP']].values# 目标变量，确保是一维数组
# del df, dt, path, tif    # 清除无用变量释放内存
# 划分训练集和测试集
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=24)
# 定义目标函数
def objective(trial):
    params = {
        # 最大树深度，3-10是常见范围，但我们扩展到15以探索更深的树。较深的树可能导致过拟合，而较浅的树可能欠拟合。
        'max_depth': trial.suggest_int('max_depth', 3, 6),
        # 学习率，使用对数均匀分布，覆盖很小到适中的学习率。较小的学习率通常需要更多的树。
        'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.1, log=True),
        # 树的数量，从较小的值开始，但允许更多的树以适应小学习率。通常，更多的树会提高性能，但也会增加计算时间。
        'n_estimators': trial.suggest_int('n_estimators', 100, 200),
        # 最小子节点权重和，从1开始，上限设为20以允许更严格的修剪。较大的值可以防止过拟合，但可能导致欠拟合。
        'min_child_weight': trial.suggest_int('min_child_weight', 3, 10),
        # 样本采样比例，保持在0.5到1之间，这是常见的有效范围。小于1的值可以防止过拟合，但太小可能导致欠拟合。
        'subsample': trial.suggest_float('subsample', 0.6, 0.9),
        # 特征采样比例，同样保持在0.5到1之间。类似于subsample，但是针对特征而不是样本。
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        # 添加gamma参数来控制树的进一步分裂所需的最小损失减少
        'gamma': trial.suggest_float('gamma', 0.1, 1.0, log=True),
        # 控制模型复杂程度的权重值的 L1 正则项参数，参数值越大，模型越不容易过拟合。
        'reg_alpha': trial.suggest_float('reg_alpha', 0.5, 5.0, log=True),
        # 控制模型复杂度的权重值的L2正则化项参数，参数越大，模型越不容易过拟合。
        'reg_lambda': trial.suggest_float('reg_lambda', 0.5, 5.0, log=True),
    }
    
    model = XGBRegressor(**params, random_state=42)
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f'r2的值是{r2}')
    return mse


# 定义计算评估模型性能的函数
def evaluate_model(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    rrmse = (rmse/np.mean(y_true))*100
    return mse, rmse, mae, r2, mape, rrmse

# 使用 optuna 进行超参数优化
study = optuna.create_study(direction='minimize')
study.optimize(objective, n_trials=100)
# 输出最优超参数
print('-'*60)
print("Best parameters:", study.best_params)
print('Best trial number:', study.best_trial.number)

# 使用最优超参数训练模型
#his_params = study.trials_dataframe()
best_params = study.best_params
best_model = XGBRegressor(**best_params, random_state=42)
best_model.fit(x_train, y_train)

# 预测和评估模型 
train_pred = best_model.predict(x_train)
test_pred = best_model.predict(x_test)
train_mse, train_rmse, train_mae, train_r2, train_mape, train_rrmse = evaluate_model(y_train, train_pred)
test_mse, test_rmse, test_mae, test_r2, test_mape, test_rrmse = evaluate_model(y_test, test_pred)
print("-"*60)
print('评估训练数据集：train_mse:{:.3f} train_rmse:{:.3f} train_mae:{:.3f} train_r2:{:.3f} train_mape:{:.3f} train_rrmse:{:.3f}'.format(train_mse, train_rmse, train_mae, train_r2, train_mape, train_rrmse))
print('评估测试数据集：test_mse:{:.3f} test_rmse:{:.3f} test_mae:{:.3f} test_r2:{:.3f} test_mape:{:.3f} test_rrmse:{:.3f}'.format(test_mse, test_rmse, test_mae, test_r2, test_mape, test_rrmse))




# # ==========用最优参数训练模型 ==========
# best_params = study.best_params
# best_model = XGBRegressor(**best_params, random_state=42)
# best_model.fit(x_train, y_train)

# # ==========训练和测试评估 ==========
# train_pred = best_model.predict(x_train)
# test_pred = best_model.predict(x_test)
# train_mse, train_rmse, train_mae, train_r2, train_mape, train_rrmse = evaluate_model(y_train, train_pred)
# test_mse, test_rmse, test_mae, test_r2, test_mape, test_rrmse = evaluate_model(y_test, test_pred)
# print("-" * 60)
# print(f'评估训练数据集：train_mse:{train_mse:.3f} train_rmse:{train_rmse:.3f} train_mae:{train_mae:.3f} train_r2:{train_r2:.3f} train_mape:{train_mape:.3f} train_rrmse:{train_rrmse:.3f}')
# print(f'评估测试数据集：test_mse:{test_mse:.3f} test_rmse:{test_rmse:.3f} test_mae:{test_mae:.3f} test_r2:{test_r2:.3f} test_mape:{test_mape:.3f} test_rrmse:{test_rrmse:.3f}')
















# import numpy as np
# import rasterio
# import glob, os

# # 假设 best_model 已经训练好并可直接调用
# # from xgboost import XGBRegressor
# # best_model = XGBRegressor(**your_params)
# # best_model.fit(x_train, y_train)

# # 1️⃣ 指定待预测的环境变量栅格路径（顺序一定要和训练时对应）
# tif_dir = r"F:\work\地理所\生态风险\data\TEST1\data\变量\mask"
# # 举例：训练时特征为 ['TAVG.tif','PRCP.tif','DEM_QTP.tif']
# tif_list = ['TAVG.tif', 'PRCP.tif', 'DEM_QTP.tif']
# tif_files = [os.path.join(tif_dir, fn) for fn in tif_list]

# # 2️⃣ 读取并展成列向量
# feature_arrays = []
# for path in tif_files:
#     with rasterio.open(path) as src:
#         arr = src.read(1).astype(np.float32)
#         nod = src.nodata
#         # 用 NaN 标记无效
#         if nod is not None:
#             arr[arr == nod] = np.nan
#         feature_arrays.append(arr.ravel())
#         # 保存空间信息用于重塑与写出
#         if 'profile' not in locals():
#             profile = src.profile.copy()
#             height, width = src.height, src.width

# # 检查
# print("加载波段：", tif_list)
# print("每波段像元数：", feature_arrays[0].shape)

# # 3️⃣ 拼成 [像元数, 特征数] 的矩阵
# X_full = np.stack(feature_arrays, axis=1)  # shape = (height*width, n_features)

# # 4️⃣ 过滤含 NaN 的像元
# nan_mask = np.any(np.isnan(X_full), axis=1)
# X_valid = X_full[~nan_mask]
# print(f"总像元：{X_full.shape[0]}, 有效像元：{X_valid.shape[0]}")

# # 5️⃣ 模型预测
# y_pred = np.full(X_full.shape[0], np.nan, dtype=np.float32)
# y_pred[~nan_mask] = best_model.predict(X_valid)

# # 6️⃣ 重塑回栅格并保存
# pred_raster = y_pred.reshape((height, width))

# # 更新 profile：单波段，nodata 用 -9999
# new_nodata = -9999
# pred_raster[pred_raster < 0] = np.nan
# profile.update({
#     'count': 1,
#     'dtype': 'float32',
#     'nodata': new_nodata,
#     'compress': 'lzw'
# })

# # 把 nan 转成 nodata 值
# pred_to_save = np.where(np.isnan(pred_raster), new_nodata, pred_raster)

# out_dir = r"F:\work\地理所\生态风险\data\TEST1\data\变量\预测"
# os.makedirs(out_dir, exist_ok=True)
# out_path = os.path.join(out_dir, f"预测{k}.tif")

# with rasterio.open(out_path, 'w', **profile) as dst:
#     dst.write(pred_to_save, 1)

# print("✅ 预测完成，输出：", out_path)


# plt.tight_layout()
# plt.show()