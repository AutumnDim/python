# -*- coding: utf-8 -*-
"""
Created on Sat 2024/9/26 13:32
@Author : lyr
"""
import os
import numpy as np
import pandas as pd
from numpy.linalg import LinAlgError
from sklearn import naive_bayes
from tqdm import tqdm
from sklearn.metrics import r2_score
from pykrige.uk import UniversalKriging
from sklearn.model_selection import LeaveOneOut
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.model_selection import train_test_split, cross_val_score
import warnings
from sklearn.metrics import mean_squared_error
from multiprocessing import Pool, Manager
warnings.filterwarnings('ignore')


def classification(x):
    """
    对降雨量进行等级划分
    无雨：0mm,小雨：0.1-9.9mm ，中雨：10.0-24.9mm，大雨：25.0-49.9mm，暴雨：50.0-99.9mm,大暴雨：50.0-99.9mm，特大暴雨：100.0-249.9mm
    """
    if pd.isna(x):  # 检查是否为 NaN
        return np.nan
    elif x < 0.1:
        x = 1        # 无雨
    elif x < 9.9:
        x = 2       # 小雨
    elif x < 24.9:
        x = 3      # 中雨
    elif x < 49.9:
        x = 4      # 大雨
    elif x < 99.9:
        x = 5      # 暴雨
    elif x < 249.9:
        x = 6      # 大暴雨
    else:
        x = 7      # 特大暴雨
    return x

def preprocess_group(group, feature):
    """
    预处理每个分组，包括填充缺失值和清理数据
    """
    group.drop('month_day', axis=1, inplace=True)
    group = group.copy()
    group[feature] = group[feature].fillna(group[feature].mean())

    first_column = group.iloc[:, 0]
    cleaned_data = group.iloc[:, 1:].dropna(axis=1)   # 填充后一列值还是nan就删除
    group = pd.concat([first_column, cleaned_data], axis=1)
    feature = feature.intersection(group.columns)

    return group, feature

def encode_features(group, feature):
    """
    对特征进行独热编码
    """
    x = group[feature]
    x_all = pd.DataFrame()
    for col, data in x.items():
        col_split = pd.get_dummies(data, prefix=col)
        x_all = pd.concat([x_all, col_split], axis=1)
    return x_all

def Naive_Bayes_classifier(group,day,feature,target,random_seed=42):
    """
    进行多项式朴素贝叶斯分类，对每个分组进行处理
    """
    np.random.seed(random_seed)
    group, feature = preprocess_group(group, feature)

    # 对降水进行分级
    group_class = group.applymap(classification)
    missing = group_class[target].isnull()  # 标记需要填补的值

    # 特征和目标数据
    df_feature = encode_features(group_class, feature).astype(int)
    df_target = group_class[target]

    # 样本
    n_sample = len(df_feature[~missing])

    if n_sample < 2:
        mean_accuracy = np.nan
        y_pre = None
        # print('样本不足,不能进行贝叶斯分类')
    else:
        # 超参数搜索调参
        estimator = naive_bayes.MultinomialNB()
        loo = LeaveOneOut()  # 留一法交叉验证
        param_grid = {'alpha': [0.1, 0.5, 1.0, 2.0]}  # 可调整的超参数
        grid_search = GridSearchCV(estimator, param_grid, cv=loo)
        grid_search.fit(df_feature[~missing], df_target[~missing])

        # 获取最优估计器和评分
        best_estimator = grid_search.best_estimator_

        # 使用留一法交叉验证评估模型
        scores = cross_val_score(best_estimator, np.array(df_feature[~missing]),
                                 np.array(df_target[~missing]), cv=loo)
        mean_accuracy = scores.mean()

        # 拟合模型
        best_estimator.fit(df_feature[~missing], df_target[~missing])

        # 对有缺失值的降水进行分级预测
        if len(df_feature[missing]) > 0:
            y_pre = best_estimator.predict(df_feature[missing])
        else:
            y_pre = None

    return mean_accuracy, y_pre, group, missing, target

def validate_kriging(grouped_all, target, xi, yi, x1, y1, elevation1):
    """
    用非缺失值验证数据精度
    """
    grouped_all1 = grouped_all.copy()
    # 去除缺失值
    grouped_all1 = grouped_all1[~grouped_all1[target].astype(str).apply(lambda x: len(x.split('.')[0]) == 4)]
    ture_valuees = grouped_all1[target]
    # 数据预测
    predicted_values = interpolate_values1(grouped_all1, target, xi, yi, x1, y1, elevation1)

    merge = pd.concat([ture_valuees, predicted_values],axis=1)
    r2 = r2_score(merge.iloc[:, 0], merge.iloc[:,1])
    return r2

def interpolate_values(grouped_all,target,xi,yi,x1,y1,elevation1):
    """
    使用泛克里金插值填补缺失值
    """
    np.random.seed(42)
    class_standard = [[2002, 0.1, 9.9], [2003, 9.9, 24.9], [2004, 24.9, 49.9],
                      [2005, 49.9, 1828.8], [2006, 99.9, 249.9], [2007, 249.9, 1828.8], [np.nan, 0, 1828.8]]  # 182.88为降水的不可能值 ,

    # 进行泛克里金插值
    for c in class_standard:

        if pd.isna(c[0]):
            group_class = grouped_all[grouped_all[target].isna()]
        else:
            group_class = grouped_all[grouped_all[target] == c[0]]

        if len(group_class) > 0:

            for loc, row in group_class.iterrows():

                # 将有雨的天气用泛克里金插值
                z1 = np.array(row[1:])
                merge = pd.DataFrame({'x': x1, 'y': y1, 'z': z1, 'elevation': elevation1}).dropna()
                x = np.array(merge['x'])
                y = np.array(merge['y'])
                z = np.array(merge['z'])
                elevation = np.array(merge['elevation'])

                # 判断是否所有的降水值都为 0
                if np.all(z == 0):
                    zi = 0  # 赋值为 0

                elif len(z) <= 2:
                    zi = z.mean()
                else:
                    if np.all(z == z[0]):
                        z = z + np.random.uniform(0, 0.01, size=z.shape)
                    try:
                        uk = UniversalKriging(
                            x, y, z,
                            variogram_model='linear',
                            drift_terms=['regional_linear'],  # 添加海拔作为趋势项
                            external_drift=elevation.reshape(-1, 1)  # 将海拔数据传递为外部漂移
                        )

                        # 进行插值预测
                        zi, ss = uk.execute('points', xi, yi)  # zi插值预测值，ss插值点的方差

                        # if zi < c[1]:
                        #     zi = c[1] + np.random.uniform(0, 1)

                    except (LinAlgError, ValueError) as e:
                        print(f"插值失败，位置: {loc}, 错误信息: {e}")
                        # 打印出 x, y, z 和 elevation 的值
                        print(f"x: {x}, y: {y}, z: {z}, elevation: {elevation}")

                group_class = group_class.copy()
                group_class.loc[loc, target] = zi
            group_class.loc[:, target] = np.where(group_class[target] < c[1],
                                                  c[1]+np.random.uniform(0, 1, size=group_class[target].shape), group_class[target])
            group_class.loc[:, target] = np.where(group_class[target] > c[2],
                                                  c[2]-np.random.uniform(0, 1, size=group_class[target].shape), group_class[target])
            grouped_all.loc[group_class.index, target] = group_class[target]

        else:
            continue
    result = pd.DataFrame(grouped_all.sort_index().iloc[:,0])

    return result

def interpolate_values1(grouped_all,target,xi,yi,x1,y1,elevation1):
    """
    验证泛克里金插值的精度
    """
    np.random.seed(42)
    class_standard = [[2, 0.1, 9.9], [3, 9.9, 24.9],
                      [4, 24.9, 49.9], [5, 49.9, 1828.8], [6, 99.9, 249.9], [7, 249.9, 1828.8]]  # 182.88为降水的不可能值 ,

    grouped_all[target] = grouped_all[target].apply(lambda x: classification(x))
    grouped_all[target][grouped_all[target] == 1] = 0

    # 进行泛克里金插值
    for c in class_standard:

        group_class = grouped_all[grouped_all[target] == c[0]]

        if len(group_class) > 0:

            for loc, row in group_class.iterrows():

                # 将有雨的天气用泛克里金插值
                z1 = np.array(row[1:])
                merge = pd.DataFrame({'x': x1, 'y': y1, 'z': z1, 'elevation': elevation1}).dropna()
                x = np.array(merge['x'])
                y = np.array(merge['y'])
                z = np.array(merge['z'])
                elevation = np.array(merge['elevation'])

                # 判断是否所有的降水值都为 0
                if np.all(z == 0):
                    zi = 0  # 赋值为 0

                elif len(z) <= 2:
                    zi = z.mean()
                else:
                    if np.all(z == z[0]):
                        z = z + np.random.uniform(0, 0.01, size=z.shape)
                    try:
                        uk = UniversalKriging(
                            x, y, z,
                            variogram_model='linear',
                            drift_terms=['regional_linear'],  # 添加海拔作为趋势项
                            external_drift=elevation.reshape(-1, 1)  # 将海拔数据传递为外部漂移
                        )

                        # 进行插值预测
                        zi, ss = uk.execute('points', xi, yi)  # zi插值预测值，ss插值点的方差

                    except (LinAlgError, ValueError) as e:
                        print(f"插值失败，位置: {loc}, 错误信息: {e}")
                        # 打印出 x, y, z 和 elevation 的值
                        print(f"x: {x}, y: {y}, z: {z}, elevation: {elevation}")

                group_class = group_class.copy()
                group_class.loc[loc, target] = zi
            group_class.loc[:, target] = np.where(group_class[target] < c[1],
                                                  c[1]+np.random.uniform(0, 1, size=group_class[target].shape), group_class[target])
            group_class.loc[:, target] = np.where(group_class[target] > c[2],
                                                  c[2]-np.random.uniform(0, 1, size=group_class[target].shape), group_class[target])
            grouped_all.loc[group_class.index, target] = group_class[target]

        else:
            continue
    result = pd.DataFrame(grouped_all.sort_index().iloc[:,0])

    return result

def Output_annually(result_all, df2,output_path):

    """ 输出分年结果 """

    grouped = result_all.groupby(result_all.index.year)
    for year, group in grouped:
        dayofyear = group.index.dayofyear
        group = group.T
        group.columns = [f'D{day}' for day in dayofyear]
        group = pd.concat([df2, group], axis=1)
        group = group.reset_index()
        group = group.rename(columns={'index': '台站编号'})

        output_path_year = os.path.join(output_path, 'prcp_data')
        if not os.path.exists(output_path_year):
            os.makedirs(output_path_year)
        else:
            pass
        return output_path,group
        # group.to_csv(output_path_year + os.sep + f'prcp_{year}')      # 保存结果
        print(year)
