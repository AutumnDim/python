# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 16:28:09 2023

@author: 30971
"""

import glob,os
import cv2
import rasterio
import numpy as np

path = r'H:\夜间灯光\data'
files = glob.glob(path + os.sep + '*.tif')
outpath = r'H:\夜间灯光\Sobel 梯度'


for tif in files:
    basename = os.path.basename(tif)
    name = basename.split('.')[0]
    with rasterio.open(tif) as src:
        nodata = src.nodata
        profile = src.profile
        data = src.read()
        data[(data == nodata) | (data < 5)] = np.nan
        data = data.reshape(5536,6856)
    # cv2.Sobel(src,ddepth,dx,dy,ksize)
    # src:输入图像；ddepth:输入图像深度（理解为数据类型）
    # dx,dy:求x/y方向上的一阶导数
    # ksize:SObel算子的大小，必须是1、3、5、7，默认3，一般很少用，就是形成3*3（5*5）的卷积核
    sobel_x = cv2.Sobel(data, cv2.CV_64F, 1, 0, ksize=5)
    sobel_y = cv2.Sobel(data, cv2.CV_64F, 0, 1, ksize=5)
    edges_sobel = np.hypot(sobel_x, sobel_y)
    # edges_sobel *= 255.0 / np.max(edges_sobel)
    
    
    with rasterio.open(outpath + os.sep + str(name) + '.tif','w',**profile) as wr:
        wr.write(edges_sobel,1)
        # break