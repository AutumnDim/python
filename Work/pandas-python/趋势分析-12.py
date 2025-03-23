# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 19:44:43 2024

@author: hqm
"""
import rasterio 
import pandas as pd
from glob import glob as glb
import scipy.stats as st
import time
import numpy as np
data = np.arange(2000,2016,1)
start = time.time()
import os
path =  r"D:\厚德学习\Pandas__Python\python_work\12 趋势和显著性\MAT/"       
#路径结尾用 / 或者 \\ ，因为\有转义的含义，\' 会把 ' 转义从而与 ‘’ 不匹配
file =r"t2000.tif"
with rasterio.open(path + file) as scr:
    windows = [window for ij,window in scr.block_windows()] #一个栅格默认读取30个窗口
    profile = scr.profile
    nodata = scr.nodata
files = ['slope.tif','P_value.tif']
Data = []
for i in files:
    scr1 = rasterio.open("D:\厚德学习\Pandas__Python\python_work\12 趋势和显著性\my输出/" + i,'w',**profile )
    Data.append(scr1)
    
"""
np.empty创建空的多维数组，
np.empty((2, k, u)为三维数组，
表示2个二维数组,每个二维数组有k个一维数组,一维数组长度为u
dtype 指定输出数组的数值类型
"""
def fun (data1):  #data1 为计算显著性水平的三维数组
    k = data1.shape[1]
    u = data1.shape[2]
    O = np.empty((2, k, u),dtype='float32')
    for x in range(0,k):
        for y in range(0,u):
            y_data = data1[:,x,y]
            if len(y_data[y_data ==nodata]) > 0:   
            #y_data[y_data ==nodata] 检测nodata,如果这些值的长度大于 0（即存在缺失值）,说明该位置的数据有问题
                O[:,x,y] = np.nan
            else:
                x_data = data #自变量为年份  
                slope, intercept, r_value, p_value, std_err = st.linregress(x_data, y_data)
                # 线性拟合，可以返回斜率，截距，r 值，p 值，标准误差
                O[0:,k,u] =slope
                O[1:,k,u] = P_value
    return O
    
    
for win in windows:
    tif = r"D:\厚德学习\Pandas__Python\python_work\12 趋势和显著性\MAT"
    de = []
    for year in range(2000,2016):
        tif_path = tif + os.sep + str(year) + '*.tif'
        with raster.open(tif_path) as scr1:
            array = src1.read(window=win)[0] #读取第一个波段
        de.append(array)
    datak = np.array(de)
    datau = fun(datak)
    Data[0].write(datau[0], 1, window=win)  #栅格文件为只有一个波段的三维数组，所以写入的也必须是一个三维数组，此处指定波段即可
    Data[1].write(datau[1], 1, window=win)
Data[0].close()       #写入后关闭文件
Data[1].close()
end = time.time()
print(end - start)    
            
































































'''
import pandas as pd 
import numpy as np
import os 
import multiprocessing
import scipy.stats as st#提供了广泛的统计分布、检验和函数。常用于统计分析和数据处理
from multiprocessing import Pool #Pool 可以分配输入数据到多个进程中并行处理
from osgeo import gdal #用于读取、写入和处理地理空间数据（如栅格数据、矢量数据等）
data = np.arange(2000,2016,1)
def fun (data_1):
    y_data = data_1                             #因变量
    x_data = data                               #自变量
    y_data = y_data.reshape(-1, 1)              #1列多行
    slope, intercept, r_value, p_value, std_err = st.linregress(x_data, y_data)
    #线性回归分析   斜率、截距、相关系数（r值）、p值以及标准误差
    return slope,p_value
if __name__ == '__main__':   #确保某些代码只在脚本被直接运行时执行，而不是在被作为模块导入时执行
    tif = r"D:\厚德学习\Pandas__Python\python_work\12 趋势和显著性\MAT\t2000.tif"
    scr = gdal.Open(tif)
    width = scr.RasterXSize
    height = scr.RasterYSize
    band = scr.RasterCount
    band1 = scr.GetRasterBand(1)
    datatype = band1.DataType
    data1 = np.full((16,width*height), 1.0)#有16个tif
    for y in range(2000,2016):
        path = r"D:\厚德学习\Pandas__Python\python_work\12 趋势和显著性\MAT"
        tifs = path + os.sep + 't' + str(y) + '.tif'
        rs = gdal.Open(tifs)
        data = rs.ReadAsArray() #将栅格波段中的数据读入数组
        data = data.flatten()  # 将栅格数据展平成一维数组
        data1[y - 2000] = data
    data1 = pd.DataFrame(data1).T #行列翻转
    data1 = data1.values  #dataframe转化为数组
    cores = multiprocessing.cpu_count()#获取CPU的核心数  通过获取 CPU 核心数来分配进程的数量，确保你的程序能够充分利用硬件资源
    pool = Pool(cores) #开启线程池
    data2 = pool.map(fun,data1)
    data2 = pd.DataFrame(data2)
    data2 = data2.values
    data3 = data2[:,0]  
    data4 = data2[:,1]
    data3 = data3.reshape(width,height)
    data4 = data4,reshape(width,height)
    var = ['MAT趋势.tif','MAT显著水平.tif']  
    datas = [data3,data4]
    for i in range(0,2):
        driver = gdal.GetDriverByName('GTiff') #写入
        out_scr = driver.Create(
        r"D:\厚德学习\Pandas__Python\python_work\12 趋势和显著性\my输出\趋势和P_值/" + var[i],                   # 保存的路径
        scr.RasterXSize,                                     # 获取栅格矩阵的列数
        scr.RasterYSize,                                     # 获取栅格矩阵的行数
        scr.RasterCount,                                     # 获取栅格矩阵的波段数
        datatype)
        out_scr.SetProjection(scr.GetProjection())                # 投影信息
        out_scr.SetGeoTransform(scr.GetGeoTransform())
        for k in range(1, ds.RasterCount + 1):                  # 循环逐波段写入
            out_band = out_scr.GetRasterBand(k)
            out_band.WriteArray(datas[i])                           # 写入数据 (why)
        out_scr.FlushCache()  #(刷新缓存)
        del out_scr #删除 
        
'''        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        