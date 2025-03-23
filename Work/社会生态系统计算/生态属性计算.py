# -*- coding: utf-8 -*-
"""
Created on Sat Mar  1 10:28:38 2025

@author: hqm
"""
import pandas as pd
import numpy as np
import rasterio,os
from glob import glob as glb

def read_raster(file_path):
    with rasterio.open(file_path) as src:
        data = src.read(1).astype('float32')  # 读取第一波段
        nodata = src.nodata
        data[data == nodata] = np.nan
        profile = src.profile
        return data
def out_raster(out, data):
    # data_out = rasterio.open(out, 'w', **profile)
    # data_out.write(data)
    # data_out.close()

    with rasterio.open(out, 'w', **meta) as dest:
            dest.write(data, 1)
        
for year in range(2000,2021,5):
    #生态暴露性---------------------------------------------------------------------------------- 
    #NPP 生产力损失（潜在 NPP - 实际 NPP）
    cnpp = rf"F:\论文写作\欣雨学姐\计算\实物量计算\固碳量\数据\NPP\CNPP\out\CNPP_{year}.tif"
    rnpp = rf"F:\论文写作\欣雨学姐\计算\实物量计算\固碳量\数据\NPP\RNPP\out\RNPP_{year}.tif"
    with rasterio.open(cnpp) as okk:
        cnpp_data = okk.read(1)  # 读取第一波段
        nodata = okk.nodata
        cnpp_data[cnpp_data == nodata] = np.nan
        meta = okk.meta
    meta.update(dtype='float32', count=1, nodata=np.nan)
    rnpp_data = read_raster(rnpp)
    npp_loss = cnpp_data - rnpp_data 
    npp_loss_out = rf"F:\\论文写作\\欣雨学姐\\计算\\生态系统计算\\生态暴露性\\NPP生产力损失\\npp生产力损失{year}.tif"
    out_raster(npp_loss_out, npp_loss)
    #风蚀暴露度（风速或防风固沙指数倒数)
    # Qsf =rf"F:\论文写作\欣雨学姐\数据\实物量计算\防风固沙\计算\防风固沙\Qsf_{year}.tif" 
    # Qsf_data = read_raster(Qsf)
    # expose = 1 / Qsf_data
    # expose_out = rf"F:\论文写作\欣雨学姐\数据\生态系统计算\生态暴露性\风蚀暴露度\风蚀暴露{year}.tif" 
    # out_raster(expose_out, expose)
    
    #水源涵养缺口(年降水量 - 实际蒸散发)
    pre = rf"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\数据\降水\SUM_{year}.tif"
    zs = rf"F:\论文写作\欣雨学姐\计算\实物量计算\水源涵养\数据\实际蒸散\实际蒸散{year}.tif"
    pre_data = read_raster(pre)
    zs_data = read_raster(zs)
    water_loss = pre_data - zs_data
    water_loss_out = rf"F:\论文写作\欣雨学姐\计算\生态系统计算\生态暴露性\水源涵养缺口\水源缺口{year}.tif"
    out_raster(water_loss_out, water_loss)
    # 生态敏感性-------------------------------------------------------------------------------------
    #NPP 敏感指数（实际 NPP / 潜在 NPP）
    npp_sen =  rnpp_data/cnpp_data
    npp_sen_out =rf"F:\\论文写作\\欣雨学姐\\计算\\生态系统计算\\生态敏感性\\NPP敏感指数\\npp敏感{year}.tif"
    out_raster(npp_sen_out, npp_sen)
    #土壤敏感性（坡度 × 土壤有机碳）
    slope = r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\数据\坡度.tif"
    sand_c = r"F:\论文写作\欣雨学姐\计算\实物量计算\土壤保持\数据\土壤数据\out\有机碳.tif"
    slope_data = read_raster(slope)
    sand_c_data = read_raster(sand_c)
    sand_sen  = slope_data * sand_c_data
    sand_sen_out = rf"F:\论文写作\欣雨学姐\计算\生态系统计算\生态敏感性\土壤敏感\土壤敏感{year}.tif"
    out_raster(sand_sen_out, sand_sen)
    #气候敏感性（年降水量/年平均气温）
    tem = rf"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\数据\气温\tmp_{year}.tif"
    tem_data = read_raster(tem)
    wea_sen = pre_data/tem_data
    wea_sen_out = rf"F:\论文写作\欣雨学姐\计算\生态系统计算\生态敏感性\气候敏感性\气候敏感{year}.tif"
    out_raster(wea_sen_out, wea_sen)
    #生态适应能力-------------------------------------------------------------------------------------
   
    
   
    
   
    
   
    