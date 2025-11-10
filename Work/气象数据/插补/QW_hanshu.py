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
    对温度进行等级划分

    温度范围      等级编号  等级名称        描述
    ＜-40℃       1       极寒        极端低温，生命活动高风险
    -40℃ ~ -30℃  2       酷寒        金属脆化，户外活动极度危险
    -30℃ ~ -20℃  3       严寒        呼吸刺痛，需专业防寒装备
    -20℃ ~ -10℃  4       大寒        裸露皮肤可能冻伤
    -10℃ ~ 0℃    5       小寒        寒冷，需厚衣物
    0℃ ~ 10℃     6       轻寒        凉意明显，需外套
    10℃ ~ 20℃    7       微凉        凉爽舒适，适合户外活动
    20℃ ~ 26℃    8       舒适        人体最适温度（无需调节）
    26℃ ~ 30℃    9       微热        稍感闷热，需通风
    30℃ ~ 35℃    10      炎热        出汗增多，需防暑
    35℃ ~ 40℃    11      酷热        高温预警，易中暑
    ≥40℃         12      极热        极端高温，可能引发热射病
    """
    if pd.isna(x):  # 检查是否为 NaN
        return np.nan
    elif x < -40:
        return 1  # 极寒
    elif x < -30:
        return 2  # 酷寒
    elif x < -20:
        return 3  # 严寒
    elif x < -10:
        return 4  # 大寒
    elif x < 0:
        return 5  # 小寒
    elif x < 10:
        return 6  # 轻寒
    elif x < 20:
        return 7  # 微凉
    elif x < 26:
        return 8  # 舒适
    elif x < 30:
        return 9  # 微热
    elif x < 35:
        return 10  # 炎热
    elif x < 40:
        return 11  # 酷热
    else:
        return 12  # 极热

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
    class_standard =[
        [2001, -89.4, -40.0],  # 极寒
        [2002, -40.0, -30.0],  # 酷寒
        [2003, -30.0, -20.0],  # 严寒
        [2004, -20.0, -10.0],  # 大寒
        [2005, -10.0, 0.0],  # 小寒
        [2006, 0.0, 10.0],  # 轻寒
        [2007, 10.0, 20.0],  # 微凉
        [2008, 20.0, 26.0],  # 舒适
        [2009, 26.0, 30.0],  # 微热
        [2010, 30.0, 35.0],  # 炎热
        [2011, 35.0, 40.0],  # 酷热
        [2012, 40.0, 57.7]  # 极热
    ]

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
    # 气温等级分类标准
    # 格式: [等级编号, 下限温度, 上限温度]
    # 不可能值范围: -89.4℃ 到 57.7℃
    class_standard = [
        [1, -89.4, -40.0],  # 极寒
        [2, -40.0, -30.0],  # 酷寒
        [3, -30.0, -20.0],  # 严寒
        [4, -20.0, -10.0],  # 大寒
        [5, -10.0, 0.0],  # 小寒
        [6, 0.0, 10.0],  # 轻寒
        [7, 10.0, 20.0],  # 微凉
        [8, 20.0, 26.0],  # 舒适
        [9, 26.0, 30.0],  # 微热
        [10, 30.0, 35.0],  # 炎热
        [11, 35.0, 40.0],  # 酷热
        [12, 40.0, 57.7]  # 极热
    ]

    grouped_all[target] = grouped_all[target].apply(lambda x: classification(x))
    # grouped_all[target][grouped_all[target] == 1] = 0

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
        group.to_csv(output_path_year + os.sep + f'prcp_{year}.csv')      # 保存结果
        print(year)
        # return output_path,group

