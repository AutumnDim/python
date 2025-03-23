# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 16:39:11 2024

@author: wly
"""
import os, sys, rasterio
import pandas as pd
import numpy as np
import mycode.arcmap as ap
from mycode.rio_wrap import unify, clip, reproject
from os.path import join
# from mycode.rio_wrap.core.clip1 import _clip
# from mycode.rio_wrap.core.unify1 import unify
from mycode.rio_wrap.core.clip import clip_array


os.chdir(r'F:\PyCharm\pythonProject1\代码\mycode\测试文件')





ph_src = r'F:/PyCharm/pythonProject1/代码/mycode/测试文件/源数据/110_40_1_5_5.tif'

ph_dst = r'F:/PyCharm/pythonProject1/代码/mycode/测试文件/源数据/111.3_38.6_1_5_5.tif'

ph_src = r'F:/PyCharm/pythonProject1/代码/mycode/测试文件/源数据/1990-5km-tiff.tif'

ph_dst = r'F:/PyCharm/pythonProject1/代码/mycode/测试文件/源数据/eva_2.tif'


out_dir = r'F:\PyCharm\pythonProject1\代码\mycode\测试文件\rio_wrap\2412'

out_ph = join(out_dir, 'unify1_dtype_0.tif')




with rasterio.open(ph_src) as src:
    
    arr = src.read(masked=True)
    src_bounds = src.bounds
    src_nodata = src.nodata
    src_crs = src.crs


with rasterio.open(ph_dst) as dst:
    
    arr_dst = dst.read(masked=True)
    dst_bounds = dst.bounds
    dst_nodata = dst.nodata
    dst_crs = dst.crs


# arr.mask = False

from rasterio.crs import CRS


def eq_crs(crs1, crs2):
    return CRS.from_user_input(crs1) == CRS.from_user_input(crs2)


out_arr, tr = clip_array(arr,arr_dst,
                         src_bounds=src_bounds,src_nodata=src_nodata,src_crs=src_crs,
                         dst_bounds=dst_bounds,dst_nodata=dst_nodata,dst_crs=dst_crs,
                         mode='round', crop=0)


























# unify(ph_src,dst_in=ph_dst,out_path=out_ph,nodata=np.nan,dtype='float32',Double_operation=0)

# _clip(ph_src, ph_dst, out_ph,mode='rio',crop=0)


# arr_crop = np.asarray([1,0,0])

# arr = np.ma.masked_equal([1,2,3],2)



# arr.mask = np.where(arr_crop==0, True, arr.mask)
# arr.data












# src = rasterio.open(ph_src)
# src.count
# unify(ph_src, ph_dst, out_ph,nodata=255,Double_operation=True,how=6)

# mode='touch'
# mode='rio'
# # mode = 'round'
# out_ph = join(out_dir, 'clip2.tif')
# clip(ph_src, ph_dst, out_ph,mode=mode,crop=0,nodata=1,dtype=np.int32)

# with rasterio.open(out_ph) as src:
#     arr = src.read()
#     profile = src.profile

































