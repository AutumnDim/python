# -*- coding: utf-8 -*-
"""
Created on Sat 2023/6/19 19:42
@Author : wly
"""

import os, sys, re, time, warnings, inspect, pathlib, math
from functools import partial
from typing import overload
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor
import threading
from tqdm import tqdm
from itertools import chain

import pandas as pd
import numpy as np

import geopandas as gpd

import rasterio
import rasterio.mask
from rasterio import features
from rasterio.transform import Affine
from rasterio.transform import from_origin
from rasterio.windows import Window
from rasterio.warp import calculate_default_transform
from rasterio.enums import Resampling
from rasterio.warp import reproject as _reproject

import mycode.codes as cd
import mycode.tempSet as tp
from mycode.decorator import unrepe
from mycode._Class import raster,false






def create_raster(**kwargs):
    memfile = rasterio.MemoryFile()
    return memfile.open(**kwargs)


def build_overviews(raster_in, level=4, how=Resampling.nearest):
    factors = [2**(i+1) for i in range(int(level))]
    
    with rasterio.open(raster_in, 'r+') as dataset:
        # 使用最近邻重采样方法构建概视图
        dataset.build_overviews(factors, how)
        # 设置概视图的压缩选项（可选）
        dataset.update_tags(ns='rio_overview', compress='lzw')

def get_RasterAttr(raster_in, *args, ds={}, **kwargs):
    """
    获得栅格数据属性

    raster_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py))
        栅格数据或栅格地址
    *args: 所需属性或函数（类中存在的，输入属性名、函数名即可）
    ds: (dict)
        传递操作所需变量,可将全局变量(globals()先赋予一个变量，直接将globals()填入参数可能会报错)输入，
        默认额外可用变量为函数此文件及mycode.code文件的全局变量


    **kwargs: 字典值获得对应属性所需操作，可为表达式，默认参数以字典形式写在“//ks//”之后，在ds中输入相应变量可替代默认参数
            非自身类函数调用时及自身在dic、kwargs中定义的属性调用时，src不可省略。
            必须使用src代表源数据。

            合并属性返回类型为list. e.g.'raster_size': ('height', 'width') -> [900, 600]
            如需特定属性请用函数. e.g. 'raster_size': r"(src.height, src.width)" or r"pd.Serise([src.height, src.width])"
   （dic中有部分，按需求添加，可直接修改dic,效果一致,getattrs中ds参数是为传递操作所需变量,如在dic中添加ds需考虑修改函数参数名及系列变动）

    ---------------------------------
    return:
        args对应属性值列表


    """

    ## 输入变量优先级高
    # now = globals()
    # now.update(ds)
    # ds = now

    # 此文件变量优先级高
    ds.update(globals())
    
    # 定义一些栅格属性
    dic = {'raster_size': r"(src.height, src.width)",
           'cell_size': r"(src.xsize, src.ysize)",
           # 'dtype':r"src.dtypes[0]",
           'bends': 'count', 
           'xsize': r'transform[0]', 
           'ysize': r'abs(src.transform[4])',
           'Bounds': r'[float(f"{i:f}") for i in src.bounds]',
           'values': r'src.read().astype(dtype)//ks//{"dtype":np.float64}',
           'arr': r'src.values',
           'df': r'pd.DataFrame(src.values.reshape(-1, 1))',
           # 'shape_b': r"(src.count, src.height, src.width)"
           'shape_b': ('count', 'height', 'width')
           }
    _getattrs = partial(cd.getattrs, **dic)
    
    
    src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in

    return _getattrs(src, *args, ds=ds, **kwargs)


def add_attrs_raster(src, ds={}, **kwargs):
    """
    向栅格数据中添加属性

    src:栅格数据
    ds:表达式所需变量
    kwargs:属性：对应表达式（"//ks//后为默认参数，在ds中输入相应变量可替代默认参数"）

    """
    dic = {'raster_size': r"(src.height, src.width)",
           'cell_size': r"(src.xsize, src.ysize)",
           'bends': 'count', 
           'xsize': r'transform[0]',
           'ysize': r'abs(src.transform[4])',
           'Bounds': r'[float(f"{i:f}") for i in src.bounds]',
           'values': r'src.read().astype(dtype)//ks//{"dtype":np.float64}',
           'arr': r'src.values.reshape(-1, 1)',
           'df': r'pd.DataFrame(src.values.reshape(-1, 1))',
           #'shape_b': r"(src.count, src.height, src.width)"
           'shape_b': ('count', 'height', 'width')
           }

    dic.update(kwargs)

    data = globals()
    data.update(ds)
    ds = data

    cd.add_attrs(src, run=True, ds=ds, **dic)



def check(src_in=None, dst_in=None,
          src_attrs=None, dst_attrs=None,
          args=None, need=None,
          printf=False, Raise = None,
          w_len=65):
    '''
    检验栅格数据是否统一
    (空间参考、范围、栅格行列数)
    (Bounds为bounds精确到小数点后六位)

    Parameters
    ----------
    输入两栅格
    
    need : 完全自定义比较属性
    args : 添加其他需要比较的属性
    
    src_in : raster
        比较数据之一
    dst_in : raster
        比较数据之一
        
    src_attrs : raster_attrs
        比较的属性集之一
    
    dst_attrs : raster_attrs
        比较的属性集之一
    printf : bool
        是否打印比较对象的不同属性值
    w_len : int
        规范打印的最大宽度
    Raise : class or str
        输入一个错误或警告类。或填入'e'、'w',等于Exception、Warning
        产生一个错误或警告

    Returns
    -------
    judge : bool
        比较的属性是否一致
    diffe : list
        不一致属性的列表
    

    '''
    
    if need:
        attrnames = need
    else:
        args = args or ()
        attrnames = ['crs', 'Bounds', 'raster_size'] + [i for i in args if not(i in ['crs', 'Bounds', 'raster_size'])]
    if src_attrs:
        if "Bounds" in attrnames:
            src_attrs = list(src_attrs) if not isinstance(src_attrs, list) else src_attrs
            for i in range(len(attrnames)):
                if attrnames[i] == "Bounds":
                    src_attrs[i] = [float(f"{n:f}") for n in src_attrs[i]]
    elif src_in:
        src_attrs = get_RasterAttr(src_in, attrnames)

    if dst_attrs:
        if "Bounds" in attrnames:
            dst_attrs = list(dst_attrs) if not isinstance(dst_attrs, list) else dst_attrs
            for i in range(len(attrnames)):
                if attrnames[i] == "Bounds":
                    dst_attrs[i] = [float(f"{n:f}") for n in dst_attrs[i]]
    elif dst_in:
        dst_attrs = get_RasterAttr(dst_in, attrnames)
    else:
        raise Exception('dst_in,dst_attrs必须输入其中一个')
    
    
    diffe = [attrnames[i] for i in range(len(attrnames)) if src_attrs[i] != dst_attrs[i]]
    
    if printf or Raise:
        # 规范打印
        if diffe == []:
            if printf:
                print('栅格属性一致')
            return True, []
        message = '以下属性不一致\n'
        for i in range(len(attrnames)):
            if attrnames[i] in diffe:
                message += (f'\n{"-"*w_len}\
                            \n{("<"+attrnames[i]+">"):-^{w_len}}\
                            \n--->src : {cd.wlen(src_attrs[i],w_len,10)}\
                            \n-\
                            \n--->dst : {cd.wlen(dst_attrs[i],w_len,10)}\n')
                          
        # if message == '以下属性不一致\n':
        #     judge = True if diffe == [] else False
        #     return judge,diffe
        
        if Raise in ('w','e'):
            Raise = Exception if Raise == 'e' else Warning
            
        if Raise is None:
            print(message)
        elif issubclass(Raise, Warning) :
            warnings.warn(message,category=Raise)
        elif issubclass(Raise, Exception):
            raise Raise(message)
        else:
            print(message)
        
            
        
    judge = True if diffe == [] else False
    
    return judge,diffe
    


def check_all(*rasters,args=None, need=None):
    '''
    比较栅格集的属性是否一致
    默认比较是否统一(空间参考、范围、栅格行列数)

    Parameters
    ----------
    *rasters : 
        栅格集
    need : 完全自定义比较属性
    args : 在空间参考、范围、栅格行列数基础上添加其他需要比较的属性
    Returns
    -------
    bool
        返回bool值，表示是否一致

    '''
    # 获得首个栅格元素作为目标值
    dst = cd.get_first(rasters,e_class=str)
    
    def compare(rasters):
        '''将rasters中的每个元素都于首个元素dst比较'''
        if cd.isiterable(rasters) & ~isinstance(rasters, str):
            [compare(x) for x in rasters]
        else:
            if rasters == dst:
                return True
            
            judge,diffe = check(rasters,dst,args=args, need=need)
            if judge:
                return True
            else:
                raise false  # 以false错误退出函数
        # 前面正常运行则全部相等
        return True
            
    try:
        return compare(rasters)
    except false:  # 捕捉false
        return False
    except Exception as e:
        raise e
    



# def checks(*rasters,
#            args=None, need=None,
#            printf=False, Raise = None,
#            w_len=60):
#     if check_all(*rasters,args=None, need=None):
#         return True, []
#     else:
        

# rasterio.DatasetReadertransform

class shp_loc:
    def __init__(self, shp, dtype=float,ex=0,t=0):
        self.shp = shp
        self.bounds = self.get_shp_bounds(dtype=dtype,ex=ex)
        self.xyslice = self.get_xy_slice(t)


    def get_shp_bounds(self, dtype, ex=0):
        bounds = self.shp.bounds
        return bounds.apply(lambda x:
                                   min(x) - ex
                               if x.name[:3] == 'min' 
                               else 
                                   max(x) + ex,
                               axis=0).astype(dtype)

    def get_xy_slice(self,t):
        minx, miny, maxx, maxy = self.bounds
        if t:
            lon, lat = slice(minx, maxx), slice(maxy,miny)
        else:
            lon, lat = slice(minx, maxx), slice(miny, maxy)
        return lon, lat
    

        
        




def bounds_to_point(left,bottom,right,top):
    return [[left,top],[left,bottom],[right,bottom],[right,top],[left,top]]

def copy_raster(raster_in, out_path,update_stats=False):
    src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in
    out_ds(ds=src,out_path=out_path,update_stats=update_stats)
    


def check_flip(src, n=1):
    bounds = src.bounds
    if bounds[1] > bounds[3]:
        bounds = [bounds[0],bounds[3],bounds[2],bounds[1]]
        src_arr = np.flip(src.read(),axis=1) 
    else:
        src_arr = src.read()
    if n == 1:
        return src_arr
    elif n == 2:
        return src_arr, bounds

   

def _return(out_path=None,get_ds=True,arr=None,profile=None,ds=None):
    '''
    返回函数

    Parameters
    ----------
    输入ds或输入arr和profile
    
    Returns
    -------
    if out_path:生成栅格文件，返回out_path
    elif get_ds:返回栅格数据(io.DatasetWriter)
    else:返回重采样后的栅格矩阵（array）和 profile

    '''
    
    if ds:
        ds = rasterio.open(ds) if isinstance(ds, (str,pathlib.Path)) else ds
        profile = ds.profile
        arr = ds.read()
    if not any((profile,arr)):
        raise Exception('请输入ds或输入arr和profile')
    
    if out_path:
        out(out_path=out_path,data=arr, profile=profile)
        return out_path
        
    elif get_ds:
        shape = (profile['count'], profile['height'], profile['width'])
        if arr.shape != shape:
            arr = np.array(arr).reshape(shape)
        ds = create_raster(**profile)
        ds.write(arr)
        return ds
    else:
        return arr,profile




def window(raster_in,
           shape=None, size=None,
           step=None,
           get_dict_id_win=False , get_dict_id_self_win=False,
           get_self_wins=False,
           initial_offset=None,
           Tqbm=False):
    '''
    Parameters
    ----------
    raster_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py))
        栅格数据或栅格地址
    shape : tuple
          (height,width)
        分割为 height*width个窗口, 未除尽的并入末端窗口
    size : int、float or tuple
          (ysize,xsize)
        窗口的尺寸大小，多余的会生成独立的小窗口不会并入前一个窗口
        
    step : tuple or int
          (ystep,xstep)
        生成滑动窗口
        为滑动步进
        shape、size参数都可以与之配合使用，这里的shape代表了窗口的尺寸为总长、宽除以shape的向下取整。
        e.g.
        src.shape = (20,20)
        shape:(3,3) == size:(6,6)
        末端窗口按正常步进滑动，如有超出会剔除多余部分
        如填int类型，ystep = xstep = step;
        如tuple中存在None,则相应的维度取消滑动，或者说滑动步进等于窗口尺寸。
        e.g.
        3 -> (3,3)
        (3,None) -> (3,xsize)
        (None,3) -> (ysize,3)
    get_self_wins : bool
        如使用滑动窗口是否返回去覆盖后的自身窗口
        
    initial_offset : tuple
                    (initial_offset_x, initial_offset_y)
        初始偏移量,默认为(0,0)

    Returns
    -------
    windows : TYPE
        窗口集
    inxs : TYPE
        对应窗口在栅格中的位置索引

    '''

    assert shape or size, '请填入shape or size'
    assert not (shape and size), 'shape 与 size只填其中一个'

    
    src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in
    
    if size:
        if isinstance(size, (int ,float)):
            xsize = size
            ysize = size
        else:
            ysize, xsize = size
        xend = src.width % xsize or xsize
        yend = src.height % ysize or ysize
        
        
        s0 = int(np.ceil(src.height / ysize))
        s1 = int(np.ceil(src.width / xsize))
        shape = (s0, s1)
        
    else:
        xsize, xend0 = divmod(src.width, shape[1])
        ysize, yend0 = divmod(src.height, shape[0])
        xend = xsize + xend0
        yend = ysize + yend0
    
    
    # 生成滑动窗口
    if step:
        
        # 获取x、y 步进
        if isinstance(step, int):
            xstep = step
            ystep = step
        else:
            xstep = step[1] or xsize
            ystep = step[0] or ysize
        # 步进过大，存在缝隙
        if xstep > xsize:
            warnings.warn('步进大于窗口尺寸：xstep > xsize')
        if ystep > ysize:
            warnings.warn('步进大于窗口尺寸：ystep > ysize')
        
        # 计算窗口数
        s00, yend0 = divmod(src.height - ysize, ystep)
        s10, xend0 = divmod(src.width - xsize, xstep)
        
        s0 = int(s00+1 if yend0 == 0 else s00+2)
        s1 = int(s10+1 if yend0 == 0 else s10+2)
        shape = (s0, s1)
        
        # 末端窗口修减
        yend = ysize - (ystep - (yend0 or ystep))
        xend = xsize - (xstep - (xend0 or xstep))

    else:
        # 规范变量
        xstep = None
        ystep = None
    
    initial_offset_x, initial_offset_y = initial_offset or (0,0)  # 初始偏移量
    
    # 返回值变量
    inxs = []  # 窗口位置索引

    windows = []
    if get_self_wins:
        self_windows = []
    

    if Tqbm:
        pbar = tqdm(total=shape[0]*shape[1], desc='生成窗口')

    y_off = initial_offset_y  # y初始坐标
    for y_inx,ax0 in enumerate(range(shape[0])):
        
        x_off = initial_offset_x
        height = yend if ax0 == (shape[0] - 1) else ysize 
        if height == 0:
            continue
        if get_self_wins:
            self_height = yend if ax0 == (shape[0] - 1) else ystep
            
        for x_inx,ax1 in enumerate(range(shape[1])):

            width = xend if ax1 == (shape[1] - 1) else xsize
            if width == 0:
                continue
            if get_self_wins:
                self_width = xend if ax1 == (shape[1] - 1) else xstep
            
            windows.append(Window(x_off, y_off, width, height))
            if get_self_wins:
                self_windows.append(Window(x_off, y_off, self_width, self_height))
            

            inxs.append((y_inx,x_inx))
            
            x_off += xstep or width
            if Tqbm:
                pbar.update(1)

        
        y_off += ystep or height
    if Tqbm:
        pbar.close()

    return (windows, inxs) if not get_self_wins else (windows, inxs, self_windows)





def read(raster_in:raster,
         n=1, tran=True, get_df=True,

         nan=np.nan, dtype=np.float32):
    """
    

    Parameters
    ----------
    raster_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py))
        栅格数据或栅格地址
    n : 1 or 2 or 3, optional.
        返回几个值. The default is 1.
    tran : bool, optional.
        是否变为单列. The default is True.
    get_df : bool, optional.
        是否变为DataFrame，The default is True.
    nan : optional
        无效值设置.The default is np.nan.
    dtype : 数据类型（class），optional
        矩阵值的格式. The default is np.float64.

    Returns
    -------
    
        栅格矩阵（单列or原型）；profile;shape

    """
    

    assert n in (1,2,3), 'n = 1 or 2 or 3'

    src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in
    arr = src.read()#.astype(dtype)
    if src.nodata is None:
        nodata = None
    else:
        nodata = type(arr[0,0,0])(src.nodata)
    # nodata = dtype(src.nodata)
    shape = arr.shape
    profile = src.profile

    # 变形，无效值处理
    df = pd.DataFrame(arr.reshape(-1, 1))

    df.replace(nodata, nan, inplace=True)
    
    # 是否保留变形，是否变为df
    if tran:
        data = df if get_df else np.array(df)

    else:
        data = (pd.DataFrame(np.array(df).reshape(shape)[0]) # 返回不变形df
                if (shape[0] == 1) & bool(get_df)            # 如果是单波段栅格且get_df
                else np.array(df).reshape(shape))            # 否则返回array
    # 返回
    return (data, profile, shape)[:n] if n != 1 else data 

def read_win(raster_in, n=3, nan=np.nan, dtype=np.float64, win=None):
    """

    获得形变矩阵

    """

    src = rasterio.open(raster_in)  # 打开栅格文件（打开的文件在用完后一定关闭，src.close()，不过在函数内部定义的在退出函数后会自动关闭）
    arr = src.read(window=win).astype(dtype)  # 读取栅格矩阵，并进行类型转换
    nodata = dtype(src.nodata)  # 获取栅格无效值，这里类型转换是因为无效值的种类有可能和矩阵不同
    shape = arr.shape  # 获取行列数
    profile = src.profile  # 获取栅格属性信息
    profile.update({'dtype': dtype,
                    'nodate': nan})  # 更新栅格属性用于输出

    # 变形，无效值处理
    data = pd.Series(arr.reshape(-1))  # 降维且转df
    data.replace(nodata, nan, inplace=True)  # 替换无效值

    # return df, profile, shape
    return (data, profile, shape)[:n] if n != 1 else data  # 返回变量

def out(out_path, data, profile, update_stats=False, **kwargs):
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
        if update_stats:
            # src.update_stats()  # raserio >= 1.4.0
            for i in range(1,profile['count']+1):
                src.statistics(i)


def out_ds(ds, out_path,update_stats=False):
    """
    输出栅格数据

    Parameters
    ----------
    ds : 
        栅格数据
    out_path : str
        输出地址

    Returns
    -------
    无

    """

    arr = ds.read()
    profile = ds.profile
    with rasterio.open(out_path, 'w', **profile) as src:
        src.write(arr)
        if update_stats:
            # src.update_stats()  # raserio >= 1.4.0
            for i in range(1,profile['count']+1):
                src.statistics(i)


def renan(raster_in, dst_in=None, nan=np.nan, dtype=np.float32, get_ds=True, out_path=None):
    '''
    替换无效值
    
    dst_in的dtype可能是字符串，不是可调用类对象，如果该类在numpy中没有的话会报错（不知道float对应哪个这里转成np.float64了）
    
    Parameters
    ----------
    raster_in : TYPE
        DESCRIPTION.
    dst_in : TYPE, optional
        DESCRIPTION. The default is None.
    nan : TYPE, optional
        DESCRIPTION. The default is np.nan.
    dtype : TYPE, optional
        DESCRIPTION. The default is np.float32.
    get_ds : TYPE, optional
        DESCRIPTION. The default is True.
    out_path : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    
    # src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in
    
    
    nan,dtype = get_RasterAttr(dst_in,'nodata','dtype',**{'dtype':r'profile["dtype"]'}) if dst_in else nan,dtype

    arr, profile = read(raster_in=raster_in,n=2,tran=False, get_df=False,nan=nan,dtype=dtype)
    
    return _return(out_path=out_path, get_ds=get_ds, arr=arr, profile=profile)







def merge():...





def resampling(raster_in, out_path =None, get_ds=True,
               re_shape=None, re_scale=None, re_size=None,size=False, how='mode', printf=False):
    """
    栅格重采样



    Parameters
    ----------
    raster_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py))
        输入栅格数据或栅格地址
    out_path : str, optional
        输出地址. The default is None.
    get_ds : TYPE, optional
        返回裁剪后的栅格数据(io.DatasetWriter). The default is True.
    
    
    
    ----------
    重采样类型三选一，都不输入则原样返回
    
    re_shape:形状重采样(tuple)
    (height, width) or (count, height, width)

    re_size:大小重采样(tuple or number)
    (xsize,ysize) or size

    re_scale:倍数重采样(number)
    scale = 目标边长大小/源数据边长大小


    how:(str or int) , optional.
    重采样方式，The default is mode.

    (部分)
    mode:众数，6;
    nearest:临近值，0;
    bilinear:双线性，1;
    cubic_spline:三次卷积，3。
    ...其余见rasterio.enums.Resampling

    printf : 任意值,optional.
        如果发生重采样，则会打印原形状及输入的printf值。The default is False.

    Returns
    -------
    if out_path:生成栅格文件，不返回
    elif get_ds:返回栅格数据(io.DatasetWriter)
    else:返回重采样后的栅格矩阵（array）和 profile

    """
    if isinstance(raster_in, (list,tuple)):
        
        if out_path is None:
            out_path = [None for i in range(len(raster_in))]
        if len(out_path) != len(raster_in):
            raise Exception('输入栅格与输出路径数量不一致')
        return [resampling(raster_in=_src,out_path=_out_path, get_ds=get_ds,
                           re_shape=re_shape, re_scale=re_scale, re_size=re_size,
                           how=how,printf=printf
                           ) for _src,_out_path in zip(raster_in,out_path)]
    
    def update():  # <<<<<<<<<更新函数
        
        if shape != out_shape:

            if not (printf is False):
                print(f'{printf}的原形状为{shape}')

            transform = rasterio.transform.from_bounds(*bounds, height=out_shape[1], width=out_shape[2])

            profile.data.update({'height': out_shape[1], 'width': out_shape[2], 'transform': transform})
            nonlocal how
            how = how if isinstance(how, int) else getattr(Resampling, 'nearest')
            data = src.read(out_shape=out_shape, resampling=how)
        else:
            data = src.read()

        return data

    src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in
    
    # 取出所需参数
    nodata, profile, count, height, width, bounds= get_RasterAttr(src, *(
        'nodata', 'profile', 'count', 'height', 'width', 'bounds'))
    west, south, east, north = bounds
    shape = (count, height, width)

    if re_shape:
        if not(2 <= len(re_shape) <= 3):
            mis = 'resampling:\n当前函数接收re_shape=%s\n请输入二维("height", "width")或三维("count", "height", "width")形状' % str(re_shape)
            raise Exception(mis)
        
        re_shape = list(re_shape)
        re_shape = [count] + re_shape[-2:]

        out_shape = re_shape

        # 更新
        data = update()
        shape = out_shape


    elif re_size:

        if (type(re_size) == int) | (type(re_size) == float):
            xsize = re_size
            ysize = re_size
        else:
            xsize, ysize = re_size
        
        
        
        
        
        out_shape = (count, round((north - south) / ysize), round((east - west) / xsize))
        if size:
            transform = rasterio.transform.from_origin(west, north, xsize, ysize)
            height, width = out_shape[1:]
            
            left, bottom, right, top = west, north-ysize*height, west+xsize*width, north
            
            
            profile.data.update({'height': height, 'width': width, 'transform': transform})
            
            y_off,x_off = src.index(left, top)
            y_end, x_end = src.index(right, bottom)
            width, height = x_end-x_off, y_end-y_off
            win = Window(x_off, y_off,width, height)
            how = how if isinstance(how, int) else getattr(Resampling, 'nearest')
            data = src.read(window=win,out_shape=out_shape, resampling=how,boundless=True,fill_value=nodata)

        else:
            # 更新
            data = update()
        shape = out_shape
        # 更新
        # data = update()
        shape = out_shape



    elif re_scale:
        scale = re_scale
        out_shape = (count, int(height / scale), int(width / scale))

        # 更新
        data = update()
        shape = out_shape
    else:
        data = src.read()
        
        
    if out_path:
        with rasterio.open(out_path, 'w', **profile) as ds:
            ds.write(data)
    elif get_ds:
        ds = create_raster(**profile)
        ds.write(data)
        return ds
    else:
        return data, profile



# @unrepe(src='raster_in',attrs=['crs'],dst='dst_in',dst_attrs=['crs'],moni_args=('run_how','resolution','shape'),return_and_dict=(_return,{'ds':'raster_in'},{}))
def reproject(raster_in, dst_in=None,
              out_path=None, get_ds=True,
              crs=None,
              how='mode',
              dst_nodata='src',
              run_how=None,
              resolution=None, shape=(None, None, None),**kwargs):
    """
    栅格重投影

    Parameters
    ----------
    raster_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py))
        输入栅格数据或栅格地址
    dst_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py)), optional
        目标投影的栅格数据或栅格地址
    out_path : str, optional
        输出地址. The default is None.
    get_ds : io.DatasetWriter, optional
        返回裁剪后的栅格数据(io.DatasetWriter). The default is True.

    crs : crs.CRS, optional
        目标投影. The default is None.
        
    
    run_how : 
        作用与how相同，但优先级更高，且不会被unrepe装饰器当作重复操作（被unrepe监视，只要不是默认值，函数正常运行）
    how:(str or int) , optional.
    重采样方式，The default is mode.

    (部分)
    mode:众数，6;
    nearest:临近值，0;
    bilinear:双线性，1;
    cubic_spline:三次卷积，3。
    ...其余见rasterio.enums.Resampling
    
    ------------------------------------------------------
    resolution : TYPE, optional
        输出栅格分辨率单位为目标坐标单位. The default is None.
    shape : TYPE, optional
        输出栅格形状. The default is (None, None, None).
        
        ------<resolution与shape不能一起使用>
        
        
   
    Raises
    ------
        dst_in 和 crs 必须输入其中一个
    
    Returns
    -------
    if out_path:生成栅格文件，不返回
    elif get_ds:返回栅格数据(io.DatasetWriter)
    else:返回重投影后的栅格矩阵（array）和 profile

    """
    # 批量处理，递归
    if isinstance(raster_in, (list,tuple)):
        
        if out_path is None:
            out_path = [None for i in range(len(raster_in))]
        if len(out_path) != len(raster_in):
            raise Exception('输入栅格与输出路径数量不一致')
        return [reproject(raster_in=_src,dst_in=dst_in,
                          out_path=_out_path, get_ds=get_ds,
                          crs=crs,
                          how=how,
                          resolution=resolution, shape=shape) for _src,_out_path in zip(raster_in,out_path)]
    

    # 输入数据整理
    src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in
    if dst_nodata == 'src':
        dst_nodata = src.nodata
    run = False
    if crs:
        if crs == 'src':
            crs = src.crs
            run = True
        
        pass
    elif dst_in:
        crs = get_RasterAttr(dst_in, 'crs')
    else:
        raise Exception("dst_in 和 crs 必须输入其中一个")
    
    # 如果输入栅格与目标投影一致则直接返回
    if src.crs == crs and not run:
        _return(out_path=out_path, get_ds=get_ds, ds=src)
    
    profile = src.profile
    if len(shape) == 2:  # 保证shape是三维的
        shape = [src.count] + list(shape)
    
    
    
    dst_transform, dst_width, dst_height = calculate_default_transform(src.crs, crs, src.width, src.height, *src.bounds,
                                                                       resolution=resolution, dst_width=shape[2],
                                                                       dst_height=shape[1])

    profile.update({'crs': crs, 'transform': dst_transform, 'width': dst_width, 'height': dst_height,'nodata':dst_nodata})
    if run_how:
        how = run_how
    how = how if isinstance(how, int) else getattr(Resampling, how)

    lst = []
    for i in range(1, src.count + 1):
        if 'int8' in str(profile['dtype']):
            # int8时,dst_nodata输入负数无效
            arrn = src.read(i).astype(np.int16)
            dst_array = np.empty((dst_height, dst_width), dtype=np.int16)
        else:
            arrn = src.read(i)
            dst_array = np.empty((dst_height, dst_width), dtype=profile['dtype'])
        _reproject(  
            # 源文件参数
            source=arrn,
            src_crs=src.crs,
            src_nodata=src.nodata,
            src_transform=src.transform,
            # 目标文件参数
            destination=dst_array,
            dst_transform=dst_transform,
            dst_crs=crs,
            dst_nodata=dst_nodata,
            # 其它配置
            resampling=how,
            num_threads=2)
        if 'int8' in str(profile['dtype']):
            dst_array = dst_array.astype(np.int8)
        lst.append(dst_array)
    dst_arr = np.array(lst)
    profile.update(kwargs)
    if out_path:
        with rasterio.open(out_path, 'w', **profile) as ds:
            ds.write(dst_arr)
        return out_path
    elif get_ds:
        ds = create_raster(**profile)
        ds.write(dst_arr)
        return ds
    else:
        return dst_arr, profile

def extract(raster_in, dst_in,
            out_path=None, get_ds=True):
    """

    栅格按栅格掩膜提取
    (对掩膜栅格有效值位置栅格值进行提取)


    Parameters
    ----------
    raster_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py))
        输入栅格数据或栅格地址
    dst_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py)), optional
        掩膜的栅格数据或栅格地址
    out_path : str, optional
        输出地址. The default is None.
    get_ds : bool, optional
        返回提取后的栅格数据(io.DatasetWriter). The default is True.


    Raises
    ------
    Exception
        二者的'crs'、 'raster_size'、 'Bounds'需统一,可先调用unify函数统一栅格数据
        或使用mask函数



    Returns
    -------
    if out_path:生成栅格文件，不返回
    elif get_ds:返回提取后的栅格数据(io.DatasetWriter)
    else:返回提取后的栅格矩阵（array）和 profile


    """

    src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in
    dst = rasterio.open(dst_in) if issubclass(type(dst_in), (str,pathlib.PurePath)) else dst_in
    # attrnames = ('crs', 'raster_size', 'Bounds')

    # src_attrs = get_RasterAttr(src, attrnames)
    # dst_attrs = get_RasterAttr(dst, attrnames)
    
    judge,dif = check(src_in=src, dst_in=dst)

    if not judge:
        
        mis = '\nextract 无法正确提取:\n'
        for i in dif:
            mis += f'\n    \"{i}\" 不一致'
        mis += '\n\n----<请统一以上属性>'
        raise Exception(mis)

    # 获得有效值掩膜
    mask_arr = dst.dataset_mask()
    # mask_arr[np.isnan(dst.read(1))] = 0

    if len(mask_arr.shape) == 3:
        mask_arr = mask_arr.max(axis=0)

    mask_arr = np.array([mask_arr for i in range(src.count)])

    # 按掩膜提取
    profile = src.profile
    nodata = src.nodata
    
    # uint格式，None无法输出
    if ('uint' in str(profile['dtype'])) & (nodata == None) :
        profile.update({'dtype':np.float32,'nodata': np.nan})
        nodata = np.nan
    arr = src.read()
    arr = np.where(mask_arr == 0, nodata, arr)

    

    if out_path:
        with rasterio.open(out_path, 'w', **profile) as ds:
            ds.write(arr)
    elif get_ds:
        ds = create_raster(**profile)
        ds.write(arr)
        return ds
    else:
        return arr, profile


@unrepe(src='raster_in',attrs=['Bounds'],dst='dst_in',dst_attrs=['bounds'],moni_kwargs={'Extract':(0,False,None,(),{})},return_and_dict=(_return,{'ds':'raster_in'},{}))
def clip(raster_in,
         dst_in=None, bounds=None,
         inner=False,
         Extract=False, mask=False,
         out_path=None, get_ds=True):
    """
    栅格按范围裁剪
    (须保证投影一致)
    (可按栅格有效值位置掩膜提取)
    
    

    Parameters
    ----------
    raster_in : (str or io.DatasetReader or io.DatasetWriter...)
        输入栅格数据或栅格地址
    dst_in : (str or io.DatasetReader or io.DatasetWriter...), optional
        目标范围的栅格数据或栅格地址
    bounds : tuple, optional
        目标范围(左，下，右，上)
    
    Extract : bool.optional
        调用extract函数
        是否对目标dst_in有效值位置的数据进行提取
        (类似矢量按周长边界裁剪栅格，dst_in必填且为栅格). The default is False.
    
    out_path : str, optional
        输出地址. The default is None.
    get_ds : bool, optional
        返回裁剪后的栅格数据(io.DatasetWriter). The default is True.

    Raises
    ------
       1. dst_in 和 bounds必须输入其中一个
       2. 如使用dst_in, dst_in 和 raster_in空间参考(crs)须一致.
       2. 使用extract，dst_in必填且为栅格
        

    Returns
    -------
    if out_path:生成栅格文件，不返回
    elif get_ds:返回栅格数据(io.DatasetWriter)
    else:返回裁剪后的栅格矩阵（array）和 profile

    """

    
    # 批量处理，递归
    if isinstance(raster_in, (list,tuple)):
        if out_path is None:
            out_path = [None for i in range(len(raster_in))]
        if len(out_path) != len(raster_in):
            raise Exception('输入栅格与输出路径数量不一致')
        return [clip(raster_in=_src,
                     dst_in=dst_in, bounds=bounds,
                     inner=inner,
                     Extract=Extract, mask=mask,
                     out_path=_out_path, get_ds=get_ds) for _src,_out_path in zip(raster_in,out_path)]
    
 
    src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in

    if dst_in:

        bounds, crs = get_RasterAttr(dst_in, 'bounds', 'crs')
        if crs != src.crs:
            mis = '\nclip:\n \"crs\"不一致'
            raise Exception(mis)

    elif bounds:
        pass
    else:
        mis = "\nclip:\n\n    \"dst_in\"和\"bounds\"必须输入其中一个"
        raise Exception(mis)
    
    if [float(f"{i:f}") for i in src.bounds] == [float(f"{i:f}") for i in bounds]:
        _return(out_path=out_path, get_ds=get_ds,ds=src)
    
    
    
    
    xsize, ysize, bounds_src, profile, nodata = get_RasterAttr(src, 'xsize', 'ysize', 'bounds', 'profile', 'nodata')
    
    
    # 有些数据集是上下翻转的
    if bounds[1] > bounds[3]:
        bounds = [bounds[0],bounds[3],bounds[2],bounds[1]]
        
        
    if bounds_src[1] > bounds_src[3]:
        bounds_src = [bounds_src[0],bounds_src[3],bounds_src[2],bounds_src[1]]
        src_arr = np.flip(src.read(),axis=1)

    else:
        src_arr = src.read()

    
    # 判断是否有交集
    inter = (max(bounds[0], bounds_src[0]),  # west
             max(bounds[1], bounds_src[1]),  # south
             min(bounds[2], bounds_src[2]),  # east
             min(bounds[3], bounds_src[3]))  # north

    if (inter[2] <= inter[0]) | (inter[3] <= inter[1]):
        # print('输入范围与栅格不重叠')
        if inner:
            Exception('\nclip: 输入范围与栅格不重叠')
        else:
            warnings.warn('\nclip: 输入范围与栅格不重叠')
        
    
    
    # uint格式，None无法输出
    if ('uint' in str(profile['dtype'])) & (nodata == None) :
         profile.update({'dtype':np.float32,'nodata': np.nan})
         nodata = np.nan

    if inner:
        # 取相交范围
        # src_arr = src.read()
        a = int((inter[0] - bounds_src[0]) / xsize)
        b = int((bounds_src[3] - inter[1]) / ysize)
        c = int((inter[2] - bounds_src[0]) / xsize)
        d = int((bounds_src[3] - inter[3]) / ysize)
        
        # dst_arr = src_arr[:, d:b, a:c]

        if mask:
            dst_arr = np.full(src_arr.shape, nodata, object)
            dst_arr[:, d:b, a:c] = src_arr[:, d:b, a:c]
            dst_height = src_arr.shape[1]
            dst_width = src_arr.shape[2]
            dst_bounds = bounds_src
        else:
            dst_arr = src_arr[:, d:b, a:c]
            dst_height = b - d
            dst_width = c - a
            dst_bounds = inter
        
    
    else:
        # 取目标范围
        
        # 填充范围
        # 并集
        union = (min(bounds[0], bounds_src[0]),  # west
                 min(bounds[1], bounds_src[1]),  # south
                 max(bounds[2], bounds_src[2]),  # east
                 max(bounds[3], bounds_src[3]))  # north
    
        union_shape = (src.count, int((union[3] - union[1]) / ysize) + 1, int((union[2] - union[0]) / xsize) + 1)
        union_arr = np.full(union_shape, nodata, object)
    
        # 填入源数据栅格值
        # src_arr = src.read()
    
        a = int((bounds_src[0] - union[0]) / xsize)
        d = int((union[3] - bounds_src[3]) / ysize)
        union_arr[:, d:d + src.height, a:a + src.width] = src_arr
    
        # clip,提取输入范围内的值
        a = int((bounds[0] - union[0]) / xsize)
        b = int((union[3] - bounds[1]) / ysize)
        c = int((bounds[2] - union[0]) / xsize)
        d = int((union[3] - bounds[3]) / ysize)
    

        if mask:
            dst_arr = np.full(union_shape, nodata, object)
            dst_arr[:, d:b, a:c] = union_arr[:, d:b, a:c]
            dst_height = union_arr.shape[1]
            dst_width = union_arr.shape[2]
            dst_bounds = union
        else:
            dst_arr = union_arr[:, d:b, a:c]
            dst_height = b - d
            dst_width = c - a
            dst_bounds = bounds

        
    
    
    dst_transform = rasterio.transform.from_bounds(*dst_bounds, dst_width, dst_height)

    profile.update({'height': dst_height,
                    'width': dst_width,
                    'transform': dst_transform})

    if Extract:
        if dst_in is None:
            raise Exception('\nclip:\n    使用extract，dst_in必填且为栅格')

        # 如果栅格大小不同,重采样
        src_shape = (dst_height, dst_width)
        dst_shape = get_RasterAttr(dst_in, 'raster_size')

        if src_shape != dst_shape:
            dst = resampling(raster_in=dst_in, re_shape=src_shape)
        else:
            dst = dst_in

        ds = create_raster(**profile)
        ds.write(dst_arr)

        return extract(raster_in=ds, dst_in=dst, out_path=out_path, get_ds=get_ds)

    if out_path:
        with rasterio.open(out_path, 'w', **profile) as ds:
            ds.write(dst_arr)
    elif get_ds:
        ds = create_raster(**profile)
        ds.write(dst_arr)
        return ds
    else:
        return dst_arr, profile



def zonal(raster_in, dst_in, stats, areas=None, dic=None, index='area',get_ds=None):
    '''
    分区统计
    栅格统计栅格
    分区栅格应为整型栅格

    Parameters
    ----------
    raster_in : TYPE
        输入栅格
    dst_in : TYPE
        分区数据栅格
    stats : 
       统计类型。基于df.agg(stats) .e.g. 'mean' or ['mean','sum','max']...
    
    areas : 
        需要统计的分区，为None时都统计，默认都统计
    
    dic : dict
        分区数据栅格各值对应属性
    
    index : list,str
    设置表格的索引,e.g. "name"、['name','count']
    如为 None 则为默认索引（0-n）
    默认分区值（如dic中有对应属性则为对应属性值）为索引
    
    get_table、get_ds:
        获得表格、获得栅格数据（DatasetWriter）
        默认只获得表格，可以任意获得
    
    Raises
    ------
    Exception
        二者的'crs'、 'raster_size'、 'Bounds'需统一,可先调用unify函数统一栅格数据
        或使用zonal_u函数

    Returns
    -------
    所需统计值的dataframe，与统计stats对应的栅格数据（数量、意义）

    '''
    


    
    assert isinstance(stats, (list,tuple)) , '请保证stats是一个list或tuple'
    src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in
    dst = rasterio.open(dst_in) if issubclass(type(dst_in), (str,pathlib.PurePath)) else dst_in
    
    
    judge,dif = check(src_in=src, dst_in=dst)

    if not judge:
        
        mis = '\nextract 无法正确提取:\n'
        for i in dif:
            mis += f'\n    \"{i}\" 不一致'
        mis += '\n\n----<请统一以上属性>'
        raise Exception(mis)
    
    # stats = [stats] if isinstance(stats, str) else stats
    
    
    df_src = read(raster_in=src, n=1)
    df_dst = read(raster_in=dst, n=1)
    
    
    df_return = pd.DataFrame()
    
    areas = areas or list(df_dst[0].unique())
    
    if len(areas) >= 1000:
        warnings.warn('\n分区数为%d,分区栅格可能为浮点型栅格'%len(areas))

    
    dic = dic or {}
    
    for area in areas:

        # virtual = df_src[df_dst[0].isin([area])]  # isin()解决np.nan不被 == 检索问题 ,但慢很多还是改用了条件判断
        if area == None:
            virtual = df_src[df_dst==area]
        elif np.isnan(area):  # 不支持None,所以分了三段
            virtual = df_src[df_dst[0].isna()]
        else:
            virtual = df_src[df_dst==area]
            
        stats_values = virtual.agg(stats,axis=0)
        stats_values.columns = [area]
        df_return = pd.concat([df_return,stats_values],axis=1)
    

    df_return = df_return.T
    if len(df_return.columns) == 1:
        stat_names = [stat if isinstance(stat, str) else stat.__name__ for stat in stats]
        df_return.loc[:,stat_names] = np.nan
    # df_return.set_index('area',inplace=True)
    
    results = []
    
    
    
    if get_ds:
        profile = src.profile
        profile['nodata'] = np.nan
        get_ds = get_ds if isinstance(get_ds, (list,tuple)) else list(df_return.columns)
        shape = (profile['count'], profile['height'], profile['width'])
        for idx in get_ds:
            df_ds = df_src*np.nan  # 初始化等长df
            dfn = df_return[idx]
            for i in areas:
                df_ds[df_dst[0] == i] = dfn.loc[i]
            arr = np.array(df_ds).reshape(shape)
            ds = create_raster(**profile)
            ds.write(arr)
            results.append(ds)
    

    df_return.reset_index().rename(columns={"index":"area"})
    
    if index:
        df_return.set_index(keys=index,drop=True,inplace=True)
    
    results.insert(0, df_return)
    

    return results if len(results) != 1 else results[0]
            


def three_sigma(raster_in,dst_in=None,out_path=None, get_ds=True):
    '''
    三倍标准差剔除离散值

    Parameters
    ----------
    raster_in : TYPE
        DESCRIPTION.
    dst_in : TYPE
        DESCRIPTION.
    out_path : TYPE, optional
        DESCRIPTION. The default is None.
    get_ds : TYPE, optional
        DESCRIPTION. The default is True.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    if out_path:生成栅格文件，不返回
    elif get_ds:返回栅格数据(io.DatasetWriter)
    else:返回重投影后的栅格矩阵（array）和 profile

    '''
    
    src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in
    
    if dst_in is None:
        df_src,profile = read(src,2)
        df_src = cd.three_sigma(df_src)
    
    else:
        dst = rasterio.open(dst_in) if issubclass(type(dst_in), (str,pathlib.PurePath)) else dst_in
        
        
        judge,dif = check(src_in=src, dst_in=dst)
    
        if not judge:
            
            mis = '\nextract 无法正确提取:\n'
            for i in dif:
                mis += f'\n    \"{i}\" 不一致'
            mis += '\n\n----<请统一以上属性>'
            raise Exception(mis)

        
        df_src,profile = read(src,2)
        df_dst = read(dst)
        
        areas = list(df_dst[0].unique())
        if len(areas) >= 1000:
            warnings.warn('\n分区数为%d,分区栅格可能为浮点型栅格'%len(areas))
        
        for area in areas:
            # areax = df_dst[(df_dst==area)]
            areax = (df_dst==area)
            df_src = cd.three_sigma(df_src,[areax])
            
            
            
            # df_x = df_src[df_dst==area]
            # mean = df_x[0].mean()
            # std = df_x[0].std()
            
            # df_src[(df_x[0] < mean - 3 * std) | (df_x[0] > mean + 3 * std)] = np.nan
    
    return _return(out_path, get_ds, arr=df_src, profile=profile)






def interval(raster_in,
             Min=0, Max=1, nodata=np.nan, dtype='float64', drop=True,
             dst_in=None,out_path=None, get_ds=True):
    src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in
    
    if dst_in is None:
        df_src,profile = read(src,2)
        df_src = cd.three_sigma(df_src)
    
    else:
        dst = rasterio.open(dst_in) if issubclass(type(dst_in), (str,pathlib.PurePath)) else dst_in
        
        
        judge,dif = check(src_in=src, dst_in=dst)
    
        if not judge:
            
            mis = '\nextract 无法正确提取:\n'
            for i in dif:
                mis += f'\n    \"{i}\" 不一致'
            mis += '\n\n----<请统一以上属性>'
            raise Exception(mis)

        
        df_src,profile = read(src,2)
        df_dst = read(dst)
        
        areas = list(df_dst[0].unique())
        if len(areas) >= 1000:
            warnings.warn('\n分区数为%d,分区栅格可能为浮点型栅格'%len(areas))
        
        for area in areas:
            # areax = df_dst[(df_dst==area)]
            areax = (df_dst==area)
            df_src = cd.three_sigma(df_src,[areax])
    return _return(out_path, get_ds, arr=df_src, profile=profile)












@unrepe(src='raster_in',attrs=['crs','Bounds','raster_size'],dst='dst_in',moni_args=['run_how'],moni_kwargs={'Extract':(0,False,None,(),{},'')},return_and_dict=(_return,{'ds':'raster_in'},{}))
def unify(raster_in, dst_in,
          out_path=None, get_ds=True,
          Extract=False, how='mode',run_how=None,
          **kwargs):
    """
    统一栅格数据
    (空间参考、范围、行列数)
    
    范围的误差在小数点后9位左右(绝大多数时候用bounds也不会报错)，
    因此检查统一函数check比较的范围Bounds为bounds精确到小数点后六位。
    如有问题可用check中printf参数查看

    Parameters
    ----------
    raster_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py))
        输入栅格数据或栅格地址
    dst_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py)), optional
        目标投影的栅格数据或栅格地址
    out_path : str, optional
        输出地址. The default is None.
    get_ds : io.DatasetWriter, optional
        返回统一后的栅格数据(io.DatasetWriter). The default is True.
    Extract : bool, optional
        是否按有效值位置提取. The default is False
    
    run_how : 
        作用与how相同，但优先级更高，且不会被unrepe装饰器当作重复操作（被unrepe监视，只要不是默认值，函数正常运行）
    how:(str or int) , optional.
    重采样方式，The default is mode.

    (部分)
    mode:众数，6;
    nearest:临近值，0;
    bilinear:双线性，1;
    cubic_spline:三次卷积，3。
    ...其余见rasterio.enums.Resampling
    


    **kwargs:
        接收调用函数(reproject、clip、resampling)的其他参数.
        e.g. printf(resampling中：如果发生重采样，则会打印原形状及printf值。The default is False.)

    Returns
    -------
    if out_path:生成栅格文件，不返回
    elif get_ds:返回栅格数据(io.DatasetWriter)
    else:返回重采样后的栅格矩阵（array）和 profile

    """
    
    
    
    # 是否按有效值位置提取
    if Extract:
        ds = unify(raster_in=raster_in, dst_in=dst_in, how=how, Extract=False, out_path=None, get_ds=True, **kwargs)
        kwargs_extract = {}  # 设置默认参数
        kwargs_extract.update({k: v for k, v in kwargs.items() if k in inspect.getfullargspec(extract)[0]}) #接收其他参数 
        
        return extract(raster_in=ds, dst_in=dst_in,out_path=out_path,get_ds=get_ds,**kwargs_extract)

    # 获得栅格变量
    src = rasterio.open(raster_in) if issubclass(type(raster_in), (str,pathlib.PurePath)) else raster_in
    dst = rasterio.open(dst_in) if issubclass(type(dst_in), (str,pathlib.PurePath)) else dst_in
    

    # 检查哪些属性需要统一
    judge,dif = check(src_in=src, dst_in=dst)
    if judge:
        return _return(out_path=out_path,get_ds=get_ds,ds=src)
    elif 'crs' in dif:
        run = 3
    elif 'Bounds' in dif:
        run = 2
    elif 'raster_size' in dif:
        run = 1
    else:
        raise Exception('有问题')
        

    
    shape = dst.shape
    
    
    ds = raster_in
    # 重投影（空间参考）
    if run == 3:
        kwargs_reproject = {}  # 设置默认参数
        kwargs_reproject.update({k: v for k, v in kwargs.items()
                                 if k in inspect.getfullargspec(reproject)[0] + inspect.getfullargspec(reproject)[4]})  #接收其他参数 
        ds = reproject(raster_in=ds, dst_in=dst, how=how, **kwargs_reproject)
    # 裁剪（范围）
    
    if run >= 2:
        kwargs_clip = {}  # 设置默认参数
        kwargs_clip.update({k: v for k, v in kwargs.items()
                            if k in inspect.getfullargspec(clip)[0] + inspect.getfullargspec(clip)[4]}) #接收其他参数 
        ds = clip(raster_in=ds, dst_in=dst,**kwargs_clip)
    # 重采样（行列数）
    if ds.shape[-2:] == dst.shape[-2:]:
        return _return(out_path=out_path, get_ds=get_ds, ds=ds)
    kwargs_resapilg = {}  # 设置默认参数
    kwargs_resapilg.update({k: v for k, v in kwargs.items()
                            if k in inspect.getfullargspec(resampling)[0] + inspect.getfullargspec(resampling)[4]})  #接收其他参数 
    return resampling(raster_in=ds, out_path=out_path,how=how, get_ds=get_ds, re_shape=shape, re_size=None, re_scale=None, **kwargs_resapilg)



def unify_wins(raster_in, dst_in,
              out_path=None, get_ds=True,
              Extract=False, how='mode',run_how=None,
              **kwargs):
    pass





def polygon_to_raster(shp,raster,pixel,field,
                      crs=None,dtype='float32',nodata=-9999):
    '''
    矢量转栅格
    :param shp: 输入矢量全路径，字符串，无默认值
    :param raster: 输出栅格全路径，字符串，无默认值
    :param pixel: 像元大小，与矢量坐标系相关
    :param field: 栅格像元值字段
    :param Code: 输出坐标系代码，默认为4326
    :return: None
    '''

    # 判断字段是否存在
    if crs:
        shapefile = gpd.read_file(shp).to_crs(crs)
    else:
        shapefile = gpd.read_file(shp)
        crs = shapefile.crs
    if not field in shapefile.columns:
        raise Exception ('输出字段不存在')
    shapefile[field] = shapefile[field].astype(dtype)

    bound = shapefile.bounds
    width = int((bound.get('maxx').max()-bound.get('minx').min())/pixel)
    height = int((bound.get('maxy').max()-bound.get('miny').min())/pixel)
    transform = Affine(pixel, 0.0, bound.get('minx').min(),
           0.0, -pixel, bound.get('maxy').max())

    meta = {'driver': 'GTiff',
            'dtype': dtype,
            'nodata': nodata,
            'width': width,
            'height': height,
            'count': 1,
            'crs': crs,
            'transform': transform}

    with rasterio.open(raster, 'w+', **meta) as out:
        out_arr = out.read(1)
        shapes = ((geom,value) for geom, value in zip(shapefile.get('geometry'), shapefile.get(field)))
        burned = features.rasterize(shapes=shapes, fill=nodata, out=out_arr, transform=out.transform)
        out.write_band(1, burned)
        out.statistics(1, clear_cache=True)





"""
以下函数包含统一空间参考

如须多次使用同一目标栅格dst_in，建议先手动使用reproject统一，减少reproject函数的调用
手动统一后可以不去寻找原函数，函数会跳过以统一栅格


"""



def clip_u(raster_in,
           dst_in=None,bounds=None,
           inner=False,
           Extract=False,mask=False,
           out_path=None, get_ds=True,**kwargs):
    '''
    栅格裁剪
    按范围裁剪。
    可提取。
    含临时统一投影操作。
    

    Parameters
    ----------
    raster_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py))
       输入栅格数据或栅格地址
    dst_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py)), optional
       目标范围的栅格数据或栅格地址
    bounds : tuple, optional
       目标范围(左，下，右，上)
      
    inner : 是否取交集，默认False
    
    Extract : bool.optional
       调用extract函数
       是否对原栅格处于掩膜栅格有效值位置的值进行提取
       (类似矢量按周长边界裁剪栅格，dst_in必填且为栅格). The default is False.
    
    mask : 是否保留并集
    
    out_path : str, optional
       输出地址. The default is None.
    get_ds : bool, optional
       返回裁剪后的栅格数据(io.DatasetWriter). The default is True.
      
    Raises
    ------
       1. "dst_in"和"bounds"必须输入其中一个
       2. 使用extract，dst_in必填且为栅格
       
       
    Returns
    -------
    if out_path:生成栅格文件，不返回
    elif get_ds:返回栅格数据(io.DatasetWriter)
    else:返回裁剪后的栅格矩阵（array）和 profile
    



    '''


    # 按范围裁剪，无须统一
    if bounds:
        return clip(raster_in=raster_in, bounds=bounds, out_path=out_path, get_ds=get_ds,mask=mask, inner=inner)
    
    # 检查参数
    if not dst_in:
        excs = "\nclip:\n\n    \"dst_in\"和\"bounds\"必须输入其中一个"
        raise Exception(excs)
    
    # 保证空间参考统一
    src_crs = get_RasterAttr(raster_in,'crs')
    dst_crs = get_RasterAttr(dst_in,'crs')
    
    if src_crs != dst_crs:
        ds = reproject(dst_in,raster_in)
    else:
        ds = dst_in
    
    # 调用clip函数
    return clip(raster_in=raster_in, dst_in=ds,inner=inner,mask=mask, Extract=Extract, out_path=out_path, get_ds=get_ds) 




def mask(raster_in,
         dst_in=None,bounds=None,
         Extract=False,Clip=True,
         out_path=None, get_ds=True,**kwargs):
    """
    栅格按栅格掩膜提取,
    对原栅格处于掩膜栅格有效值位置的值进行提取，也可对范围提取
    支持不同空间参考
    

    --------------------------

    raster_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py))
        输入栅格数据或栅格地址
        
    dst_in : (str or io.DatasetReader or io.DatasetWriter...(in io.py)), optional
        掩膜的栅格数据或栅格地址
    bounds : tuple, optional
        目标范围(左，下，右，上),bounds与dst_in填其中一个，bounds优先级更高
    
    
    Extract : bool.optional
        调用extract函数
        是否对目标dst_in有效值位置的数据进行提取
        (类似矢量按周长边界裁剪栅格，dst_in必填且为栅格). The default is False.
        
    Clip : bool,optional
        是否裁剪. The default is True.
    out_path : str, optional
        输出地址. The default is None.
    get_ds : bool, optional
        返回提取后的栅格数据(io.DatasetWriter). The default is True.

    
    Raises
    ------
       1. "dst_in"和"bounds"必须输入其中一个
       2. 使用extract，dst_in必填且为栅格
       3. 须保证范围与输入栅格有重叠
      
       
    Returns
    ------------------
    if out_path:生成栅格文件，不返回
    elif get_ds:返回提取后栅格数据(io.DatasetWriter)
    else:返回提取后的栅格矩阵（array）和 profile

    """
    

    
    return clip_u(raster_in=raster_in,
                  dst_in=dst_in,bounds=bounds,
                  inner=True,
                  Extract=Extract,mask=not(Clip),
                  out_path=out_path, get_ds=get_ds,**kwargs)

       
"""
以下函数内部调用unify统一函数，支持不同空间参考、范围、行列数栅格之间的操作
不更改原栅格，将目标栅格向原栅格转换，以下函数都是如此

如须多次使用同一目标栅格dst_in，建议先手动使用unify统一，减少unify函数的调用，
手动统一后可以不去寻找原函数，函数会跳过以统一栅格


"""

def zonal_u(raster_in, dst_in, stats, areas=[], dic=None, index='area',get_ds=None,**kwargs):
    '''
    分区统计
    含临时统一操作
    分区栅格应为整型栅格
    
    Parameters
    ----------
    raster_in : TYPE
        输入栅格
    dst_in : TYPE
        分区数据栅格
    stats : list or tuple
       统计类型。基于df.agg(stats). e.g. ['mean'] or ['mean','sum','max']...
    
    dic : dict
        分区数据栅格各值对应属性，默认为值本身
    **kwargs : TYPE
       unify可填入的其他参数

    Returns
    -------
    dataframe
        所需统计值的dataframe

    '''
    
    ds = unify(raster_in = dst_in, dst_in = raster_in, out_path=None,get_ds=True, **kwargs)
    return zonal(raster_in=raster_in,dst_in=ds, stats=stats,area=areas,dic=dic,index=index,get_ds=get_ds)
       
 

'''
其他

'''
import xarray as xr
# def nc_to_tif(ds_nc,
#               vr=None,
#               arr_vr=None,
#               out_ph=None,
#               loc_names=None,
#               crs='EPSG:4326',
#               dtype='float32',
#               nodata=None):
#     '''
#     nc转tif
#     # (数据维度及排序为(time,lat,lon),或（lat,lon)可用)
#     仅限维度为二[lat,lon] --- [height, width]
#     或维度大小为三[*, lat,lon] --- [count, height, width] 第三个维度将设为栅格波段维度
#     *维度顺序不限将自动排序

#     Parameters
#     ----------
#     ds_nc : xr.Dataset,xr.DataArray
#         nc数据
#     vr : str
#         提取的变量
#     arr_vr : array
#         变量矩阵
#     out_ph : str
#         输出位置
#     loc_names : dict, optional
#         lon,lat的对应变量名,默认为lon,lat
        
#         eg. {'lon':'longitude', 'lat':'latitude'}
        
#     crs : str, dict, or CRS; optional
#         空间参考. The default is 'EPSG:4326'.
#     dtype :  str or numpy dtype, optional
#         数据类型. The default is 'float32'.
#     nodata : int, float, or nan; optional
#         无效值.

#     Returns
#     -------
#     if out_ph is None :
#         return arr_vr, profile
#     else:
#         output tif and return out_ph

#     '''
    
#     # 计算transform
#     if loc_names is None:
#         loc_names = {}
    
#     lon_name = loc_names.get('lon', 'lon')
#     lat_name = loc_names.get('lat', 'lat')
    
#     dims = list(ds_nc.dims) if vr is None else list(ds_nc[vr].dims)
#     assert {lat_name,lon_name}.issubset(set(dims)) , '未找到代表lat、lon的维度，尝试重新定义loc_names参数'
    
#     assert len(dims) <= 3, 'dims长度超限，仅接受代表维度[lat, lon]或[band, lat, lon]'
        
    
#     # 维度排序
#     loc = [lat_name, lon_name]
#     if len(dims) == 3:
#         new_dims = [i for i in dims if i not in loc] + loc
#     else:
#         new_dims = loc
#     if dims != new_dims:
#         ds_nc = ds_nc.transpose(*new_dims)
    
    
#     # 获取经纬度序列
#     lon = ds_nc[lon_name].data
#     lat = ds_nc[lat_name].data
    
#     # 获取分辨率
#     res_lon = abs(lon[1] - lon[0])
#     res_lat = abs(lat[1] - lat[0])
    
#     # 计算栅格transform
#     transform = from_origin(west=lon.min()-res_lon/2,
#                             north=lat.max()+res_lat/2,
#                             xsize=res_lon, ysize=res_lat)
    
    
#     # 获取数据矩阵
#     if arr_vr is None:
#         if isinstance(ds_nc, xr.DataArray):
#             arr_vr = ds_nc.data
#         else:
#             arr_vr = ds_nc[vr].data
    
#     # 统一为三维(count, height, width), 并获取shape
#     if arr_vr.ndim == 2:
#         arr_vr = np.array([arr_vr])
#     count, height, width = arr_vr.shape
    
#     # 检查经纬度方向, 保证lat递减, lon递增
#     if lat[1] > lat[0]:
#         arr_vr = np.flip(arr_vr,axis=1) 
#     if lon[1] < lon[0]:
#         arr_vr = np.flip(arr_vr,axis=2) 
    
#     # 定义profile
#     profile = {
#         "driver": "GTiff",
#         "dtype": dtype,
#         "width": width,
#         "height": height,
#         "count": count,
#         "crs": crs,
#         "transform": transform,
#         "nodata": nodata
#     }
    
#     if out_ph is None:
#         return arr_vr, profile
#     else:
#         # 输出
#         with rasterio.open(out_ph, 'w', **profile) as dst:
#             dst.write(arr_vr)
#         return out_ph



def nc_to_tif(ds_nc,
              vr=None,
              arr_vr=None,
              out_ph=None,
              loc_names=None,
              crs='EPSG:4326',
              dtype='float32',
              nodata=None):
    '''
    nc转tif
    仅限维度为二[lat,lon] --- [height, width]
    或维度大小为三[*, lat,lon] --- [count, height, width] 第三个维度将设为栅格波段维度
    *维度顺序不限将自动排序

    Parameters
    ----------
    ds_nc : xr.Dataset,xr.DataArray
        nc变量
    vr : str
        提取的变量
    arr_vr : array  * 还需完善,使用此参数维度顺序暂时不自动排序
        变量矩阵, 提前计算所得通过此函数输出为tif, 如其dims不与ds_nc.dims相同，请输入与之dims相同的vr参数
    out_ph : str
        输出位置
    loc_names : dict, optional
        lon,lat的对应变量名,默认为lon,lat
        
        eg. {'lon':'longitude', 'lat':'latitude'}
        
    crs : str, dict, or CRS; optional
        空间参考. The default is 'EPSG:4326'.
    dtype :  str or numpy dtype, optional
        数据类型. The default is 'float32'.
    nodata : int, float, or nan; optional
        数据无效值.

    Returns
    -------
    if out_ph is None :
        return arr_vr, profile
    else:
        output tif and return out_ph

    '''
    
    # 计算transform
    if loc_names is None:
        loc_names = {}
    
    lon_name = loc_names.get('lon', 'lon')
    lat_name = loc_names.get('lat', 'lat')
    
    # dims判断
    dims = list(ds_nc.dims) if vr is None else list(ds_nc[vr].dims)
    assert {lat_name,lon_name}.issubset(set(dims)) , '未找到代表lat、lon的维度，尝试重新定义loc_names参数'
    assert len(dims) <= 3, 'dims长度超限,期望长度2或3，得到%d。仅接受代表维度[lat, lon]或[band, lat, lon]'%len(dims)
        
    
    # 维度排序
    loc = [lat_name, lon_name]
    if len(dims) == 3:
        new_dims = [i for i in dims if i not in loc] + loc
    else:
        new_dims = loc
    if dims != new_dims:
        ds_nc = ds_nc.transpose(*new_dims)
    
    # 获取经纬度序列
    lon = ds_nc[lon_name].data
    lat = ds_nc[lat_name].data
    
    # 获取分辨率
    res_lon = abs(lon[1] - lon[0])
    res_lat = abs(lat[1] - lat[0])
    
    # 计算栅格transform
    transform = from_origin(west=lon.min()-res_lon/2,
                            north=lat.max()+res_lat/2,
                            xsize=res_lon, ysize=res_lat)
    
    
    # 获取数据矩阵
    if arr_vr is None:
        if isinstance(ds_nc, xr.DataArray):
            arr_vr = ds_nc.data
        else:
            arr_vr = ds_nc[vr].data
    
    # 统一为三维(count, height, width), 并获取shape
    if arr_vr.ndim == 2:
        arr_vr = np.array([arr_vr])
    count, height, width = arr_vr.shape
    
    # 检查经纬度方向, 保证lat递减, lon递增
    if lat[1] > lat[0]:
        arr_vr = np.flip(arr_vr,axis=1) 
    if lon[1] < lon[0]:
        arr_vr = np.flip(arr_vr,axis=2) 
    
    # 定义profile
    profile = {
        "driver": "GTiff",
        "dtype": dtype,
        "width": width,
        "height": height,
        "count": count,
        "crs": crs,
        "transform": transform,
        "nodata": nodata
    }
    
    if out_ph is None:
        return arr_vr, profile
    else:
        # 输出
        with rasterio.open(out_ph, 'w', **profile) as dst:
            dst.write(arr_vr)
        return out_ph
# src = raster_in if type(raster_in) in (i[1] for i in inspect.getmembers(rasterio.io)) else rasterio.open(raster_in)
# dst = dst_in if type(dst_in) in (i[1] for i in inspect.getmembers(rasterio.io)) else rasterio.open(dst_in)


def get_geometry(ph_shp, crs=None):
    shp = gpd.read_file(ph_shp) if crs is None else gpd.read_file(ph_shp).to_crs(crs)
    return shp.geometry



def rio_mask(dataset, shapes,
             nodata=None,dtype=None,
             crop=True,all_touched=False,filled=True,
             **kwgs):
    """
    使用矢量形状对栅格数据进行掩膜操作，并返回掩膜后的数组和更新后的元信息。

    Parameters
    ----------
    dataset : rasterio.io.DatasetReader
        将应用掩膜的栅格数据集
    shapes : iterable
        矢量形状列表，用于掩膜操作。
    crop : bool, optional
        是否裁剪到矢量范围，默认为 True。
    nodata : int or float, optional
        无效值。如果未提供，则使用输入栅格的 nodata 值；如果栅格没有 nodata 值，则默认为 0。
    dtype : data-type, optional
        默认情况下，数据类型是从输入数据推断出来的
    all_touched : bool, optional
        如果为 True，则掩膜操作中会填充所有被形状边界触碰的像素；否则只填充形状内部的像素。
    filled : bool, optional
        如果为 True，则掩膜外填充为 nodata；否则返回 fill_value 为 nodata 的掩膜数组。
        nodata 无法转换为 dataset 的 dtype 时可设置 dtype 参数，否则会报错。
    **kwgs : dict
        其他关键字参数，传递给 `rasterio.mask.mask`。

    Returns
    -------
    arr : numpy.ndarray
        掩膜处理后的数组。
    profile : dict
        更新后的数据集元信息（profile）。
    """
    # crs = src_in.crs
    
    # shp = gpd.read_file(ph_shp).to_crs(crs)
    # shapes = shp.geometry
    
    # `profile`获取
    profile = dataset.profile.copy()
    
    # `nodata`获取
    if nodata is None:
        nodata = 0 if dataset.nodata is None else dataset.nodata
    
    # 运行`rasterio.mask.mask`, 关闭filled(改为由后续代码自定义控制)
    arr, tf = rasterio.mask.mask(dataset, shapes,
                                 crop=crop,nodata=nodata,
                                 all_touched=all_touched,
                                 filled=False,
                                 **kwgs)
    
    # 更新`arr`的类型
    if dtype is not None:
        arr = arr.astype(dtype)
    
    # 检查无效值能否储存在`arr`中
    dtype = arr.dtype
    try:
        fill_value = np.asarray(nodata, dtype=dtype)
    except (OverflowError, ValueError) as e:
        # Raise TypeError instead of OverflowError or ValueError.
        # OverflowError is seldom used, and the real problem here is
        # that the passed fill_value is not compatible with the ndtype.
        err_msg = "Cannot convert nodata %s to dtype %s"
        raise TypeError(err_msg % (fill_value, dtype)) from e
    
    # 填充设置
    if filled:
        arr = arr.filled(nodata)
    else:
        arr.fill_value = nodata
    
    
    # 更新`profile`
    profile.update({
                'dtype': arr.dtype,
                'nodata':nodata,
                "height": arr.shape[1],
                "width": arr.shape[2],
                "transform": tf})
    return arr, profile
        


def nan_equal(arr, value):
    """
    判断数组中的值是否等于给定值（支持 NaN 值的比较）。
    
    Parameters
    ----------
    arr : numpy.ndarray
        输入数组。
    value : int, float or None
        要比较的值。
    
    Returns
    -------
    numpy.ndarray
        布尔数组，表示每个元素是否等于给定值。
    """
    arr = np.asarray(arr)
    if value is None or not np.isnan(value):
        return np.equal(arr, value)
    else:
        return np.isnan(arr)



def tif_fill_in_shp(dataset, shapes, mod_nan,
                    fill_value=0, nodata=None,
                    all_touched=False,
                    dtype=None,
                    **kwgs):

    """
    根据矢量形状（shapes）对栅格数据进行掩膜操作，并填充指定值，同时更新数据的 nodata 值。

    参数：
        dataset: rasterio.io.DatasetReader
            打开的栅格数据集，需以可写模式（r+, w, w+）打开。
        shapes: list
            矢量形状列表，用于掩膜操作。
        mod_nan: int 或 float
            中间处理时的临时 nodata 值，请使用dataset中不存在的值, 不能与 `nodata` 或 `fill_value` 相同。
        fill_value: int 或 float, 可选
            填充的值，默认为 0。
        nodata: int 或 float, 可选
            栅格数据的 nodata 值。如果未提供，则使用 `dataset.nodata`。
        all_touched: bool, 可选
            如果为 True，则掩膜操作中会填充所有被形状边界触碰的像素；否则只填充形状内部的像素。
        dtype: 数据类型, 可选
            输出数组的 dtype。如果未提供，则保持与输入数据一致。
        **kwgs: 其他关键字参数
            传递给 rio_mask 的其他参数。

    Returns:
    ------
        arr: numpy.ndarray
            掩膜处理后的数组。
        profile: dict
            更新后的数据集元信息（profile），包括 nodata 和 dtype。

    Raises
    ------
        ValueError: 如果 nodata、mod_nan 或 fill_value 存在冲突，或输入None (nodata输入None且dataset.nodata为None)。

    Note：
    ------
        - `dataset` 必须以可写模式打开。
        -.`mod_nan`请使用`dataset`中不存在的值
        - `nodata`、`mod_nan` 和 `fill_value` 必须互不相同。
        -.注意考虑`dataset`与`nodata`、`mod_nan` 和 `fill_value`的dtype兼容性
    """
    
    
    assert dataset.mode != 'r', '请使用可写模式打开数据集: r+, w, w+'
    
    
    if nodata is None:
        nodata = dataset.nodata
    
    args = {nodata, mod_nan, fill_value}
    
    if None in args:
        raise ValueError(f'监测到None值输入, nodata({nodata}), mod_nan({mod_nan}), fill_value({fill_value})')
    
    if len(args) != 3:
        raise ValueError(f'监测到输入值冲突,请保证三者互不相同\n nodata({nodata}), mod_nan({mod_nan}), fill_value({fill_value})')
    
    with tp.set_temp_attr(dataset, 'nodata', mod_nan):
        '''此处dtype兼容性暂未测试'''
        arrx, profile = rio_mask(dataset, shapes,
                                 nodata=mod_nan,all_touched=all_touched,dtype=dtype,**kwgs)
    
    # arrx: shapes外位置为mod_nan, shapes内原nodata保持不变
    
    arr = np.where(nan_equal(arrx, dataset.nodata), fill_value, arrx)  # 将`nodata`(都在`shapes`内)替换为`fill_value`
    arr = np.where(nan_equal(arrx, mod_nan), nodata, arr)  # 将`mod_nan`(都在`shapes`外, 且`shapes`外都是)替换为`nodata`
    # arr = np.where(nan_equal(arrx, mod_nan), nodata, arr)  # 将`mod_nan`(都在`shapes`外, 且`shapes`外都是)替换为`nodata`
    
    profile.update(nodata=nodata)
    
    return arr, profile




# import numpy as np

# def nan_equal(x1, x2):
#     """
#     比较两个数组或标量是否相等，支持 np.nan 的特殊处理。
#     """
#     x1, x2 = np.asarray(x1), np.asarray(x2)  # 转换为数组（如果是标量）
    
#     # 使用 np.isnan 检查 NaN 的位置
#     nan_mask = np.isnan(x1) & np.isnan(x2)
    
#     # 正常的相等比较
#     normal_equal = np.equal(x1, x2)
    
#     # 将 NaN 位置的比较结果设置为 True
#     return normal_equal | nan_mask

# x = nan_equal([1,None],1)



# def nan_equal(arr, value):
#     mode='easy'
#     arr = np.asarray(arr)
#     if mode == 'easy':
#         if value is None or not np.isnan(value):
#             return np.equal(arr, value)
#         else:
#             return np.isnan(arr)

#     else:
#         '''暂未完善, 不要使用'''
#         arr = np.asarray(arr, dtype=object)
        
#         if value is None:
#             # 如果 value 是 None，直接比较
#             return np.equal(arr, None)
#         elif isinstance(value, float) and np.isnan(value):
#             # 如果 value 是 np.nan，检查 arr 中的 NaN
#             return np.vectorize(lambda x: isinstance(x, float) and np.isnan(x))(arr)
#         else:
#             # 其他情况，直接比较
#             return np.equal(arr, value)
# import numpy as np

# def nan_equal(arr, value):
#     # Convert the input array to a NumPy array with dtype=float to handle np.nan
#     arr = np.asarray(arr, dtype=float)
#     if value is None or not np.isnan(value):
#         return np.equal(arr, value)
#     else:
#         return np.isnan(arr)




if __name__ == '__main__':
    # sys.exit(0)
    raster_in = r'F:/PyCharm/pythonProject1/arcmap/015温度/土地利用/landuse_4y/1990-5km-tiff.tif'

    dst_in = r'F:\PyCharm\pythonProject1\arcmap\007那曲市\data\eva平均\eva_2.tif'

    out_path = r'F:\PyCharm\pythonProject1\代码\mycode\测试文件\eva5_1.tif'
    
    out_path1 = r'F:\PyCharm\pythonProject1\arcmap\015温度\zonal\grand_average.xlsx'


    # x = check_all(raster_in,raster_in,dst_in)
    src = rasterio.open(raster_in)
    windows, ids, self_windows = window(r'F:\PyCharm\pythonProject1\代码\008并行分窗口\20230819\lst2000\LSTD1_2000.tif',
                                        size=200,step=1,get_self_wins=True,Tqbm=1)
    # windows1, ids1 = window(src,size=200,step=None)
    # os.chdir(r'F:/Python/pythonlx/9 tif_mean')
    # x = rasterio.band(src,1)
    # pro = src.profile
    # src.checksum(1)
    # src.lnglat()
    # src.files
    # src.overviews(1)
    # src.window_bounds()
    # src.write_transform()
    # # src.
    # nodata = src.nodata
    
    # arr = src.read()
    
    # arr == nodata
    # pro['dtype'] = 'float32'
    
    # ds = create_raster(**pro)
    
    
    # ds.profile['dtype']
    
    # ds.close()
    
    # dst = rasterio.open(r'F:\PyCharm\pythonProject1\代码\mycode\测试文件\float2.tif','w',**pro)
    # ds = renan(src)
    
    # arr = ds.read()
    
    # dst.profile
    
    
    
    
    
    # check(raster_in,dst_in=dst_in,printf=1,w_len=80)
    # df = zonal_u(raster_in=dst_in, dst_in=raster_in, stats = ['sum','max','min'])
    # src.dtypes
    # dst = unify(raster_in,dst_in)
    # ds = three_sigma(dst_in,dst)
    # out_ds(ds, out_path)
    
    
    # ws = src.read()
    # w = src.block_window(1,0,0)
    
    # list(ws)
    
    # # src.block_shapes = [(1368/2,1728/2)]
    
    # from sys import getsizeof as getsize
    # var = object()
    # print(getsize(ws))
    
    
    # s = time.time()
    # ds = unify(raster_in,dst_in=dst_in)
    # print('运行时间：%.2f'%(time.time()-s)+'s')
    # s = time.time()
    # ds1 = unify(dst_in,dst_in=ds)
    # ds1 = unify(dst_in,dst_in=ds)
    # ds1 = unify(dst_in,dst_in=ds)
    # ds1 = unify(dst_in,dst_in=ds)
    # ds1 = unify(dst_in,dst_in=ds)
    # ds1 = unify(dst_in,dst_in=ds)
    # print('运行时间：%.2f'%(time.time()-s)+'s')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    






































    





















