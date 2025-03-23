# -*- coding: utf-8 -*-
"""
Created on Sat May 25 21:01:41 2024

@author: hqm
"""
import rasterio
import numpy as np
import os
import pandas as pd

def func(path):
    with rasterio.open(path) as src:# 打开栅格文件，使用上下文管理器with，在退出with缩进时自动关闭文件
        nodata = np.float64(src.nodata) 
        
        #这里使用 numpy 中的 float64 类型来确保获取的无效值与后续处理中的数据类型一致。
        #因为 nodata 可能是浮点数或整数，使用 np.float64() 函数可以确保无效值被正确地转换为 float64 类型的值，
        #以便后续在栅格数据中进行处理和替换 无效值
        
        profile = src.profile  # 栅格元信息
        '''
        栅格文件元数据（profile）字段
        driver: 文件格式驱动，比如 GTiff 表示 GeoTIFF 格式。
        dtype: 数据类型，比如 uint8, int16, float32 等。
        nodata: 无效值标识，比如 None 或特定的数值。
        width: 栅格的宽度（像素数）。
        height: 栅格的高度（像素数）。
        count: 波段数。
        crs: 坐标参考系统（Coordinate Reference System），通常是一个 EPSG 代码或 WKT 字符串。
        transform: 仿射变换参数，用于将栅格坐标转换为地理坐标。
        compress: 压缩类型，比如 lzw, jpeg 等（可选）。
        interleave: 数据交错类型，比如 pixel, band（可选）
        '''
        
        profile.data['dtype'] = 'float64'  # 更新数据类型 ,该数据类型未改变，只是再后续计算的过程中将结果变为float64
        #数据类型更新为 float64 的主要原因是为了在处理栅格数据时确保数值的精度和处理的灵活性。
        profile.data['nodata'] = np.nan  # 更新无效值
        
        data = src.read().astype('float64')  # 读取栅格矩阵，将数据类型变为float64
        shape = data.shape  # 矩阵形状（波段，行，列）
        data = data.reshape(-1,1)  # 变为一列
        data[data == nodata] = np.nan  # 无效值替换为np.nan
        data = pd.DataFrame(data)  # 转为df，方便再后续的数据进行计算和合并
    return data,profile,shape  # 输出

def out(out_path, data, profile, shape):
    """
        操作函数
        ---------
        （与read对应）

        生成栅格文件

    """

    data = np.array(data).reshape(shape)
    bend = shape[0]
    with rasterio.open(out_path, 'w', **profile) as src:
        
        for i in range(bend):  # 将矩阵输出至各个波段，其实src.write(data)就行
            src.write(data[i], i + 1)  # 二维，将计算出的年均值写入并还原形状
        # src.write(data)  # 三维



dir_pre = r"D:\厚德学习\Pandas__Python\python_work\17 rasterio\降水_月"
pre_dir = r"D:\厚德学习\Pandas__Python\python_work\17 rasterio\年"

# pre_{y}_01.tif
for y in range(2001,2018):
    df_mean = pd.DataFrame()
    for m in range(1,13):
        
        path_pre = dir_pre + '\\pre_%d_%.2d.tif'%(y,m)
        
        dfn,profile,shape = func(path_pre)
        
        df_mean = pd.concat([df_mean,dfn],axis=1)
        
    df_y = df_mean.agg('mean',axis=1)
    pre_path = pre_dir + f'\\{y}.tif' 
    out(pre_path,df_y,profile,shape)
    print(y,shape)
















































































