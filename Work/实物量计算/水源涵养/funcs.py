# -*- coding: utf-8 -*-
"""
Created on Thu Jun 27 19:40:55 2024

@author: wly
"""

import rasterio
import numpy as np
import os
import pandas as pd
import warnings

def read(path, n=1, out_shape=None, dtype='float32', nan=np.nan):
    with rasterio.open(path) as src:# 打开栅格文件，使用上下文管理器with，在退出with缩进时自动关闭文件
        nodata = np.float64(src.nodata)  # 无效值
        profile = src.profile  # 栅格元信息
        profile.data['dtype'] = dtype  # 更新数据类型
        profile.data['nodata'] = nan  # 更新无效值
        

        data = src.read(out_shape=out_shape).astype(dtype)  # 读取栅格矩阵
        shape = data.shape  # 矩阵形状

        
        data = data.reshape(-1,1)  # 变为一列
        data[data == nodata] = nan  # 无效值替换为np.nan
        data = pd.DataFrame(data)  # 转为df
    return (data, profile, shape)[:n] if n != 1 else data   # 输出

def out(out_path, data, profile, **kwargs):
    """
    
    输出函数，
    可配合形变矩阵
    


    """
    profile.update(kwargs)
    shape = (profile['count'], profile['height'], profile['width'])
    
    if data.shape != shape:
        data = np.array(data).reshape(shape)

    with rasterio.open(out_path, 'w', **profile) as src:
        src.write(data)


def three_sigma(array,areas=None) -> np.array:
    '''
    三倍标准差剔除离散值

    Parameters
    ----------
    array : array_like
        可正常转为数组的元素
        需要操作的数组
    areas : TYPE, optional
        分区数组列表，每个元素需于数组形状相同，
        每个元素中的有效值（None、np.nan、False为无效值）为一个区域.
        （如不同的时间或地区分区剔除，不受其他区域影响）
        None则不分区，（默认值）
        The default is None.

    Returns
    -------
    arr : np.array
        剔除离散值后的数组

    '''
    
    arr = np.array(array).astype('float64')
    
    if areas is None:
        mean = np.nanmean(arr)
        std = np.nanstd(arr)
        arr[(arr < mean - 3 * std) | (arr > mean + 3 * std)] = np.nan
        
    else:
        for area in areas:

            warnings.filterwarnings('ignore',category=RuntimeWarning)
            area = np.array(area)
            arrx = np.where((np.isnan(area)|(area==False)|(area==None)),np.nan,arr)
            mean = np.nanmean(arrx)
            std = np.nanstd(arrx)
            arr[(arrx < mean - 3 * std) | (arrx > mean + 3 * std)] = np.nan
        warnings.filterwarnings('default')

    return arr
