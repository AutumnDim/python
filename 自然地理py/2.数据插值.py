# -*- coding: utf-8 -*-
"""
Created on Sun May 19 09:05:21 2024

@author: hqm
"""




import pandas as pd
import geopandas as gpd
import numpy as np
import os
from scipy.spatial import cKDTree as KDTree
class Invdisttree:
    
    def __init__( self, X, z, leafsize=10, stat=0 ):   # 有参构造函数 
        # assert 检查条件，不符合就终止程序
        assert len(X) == len(z), "len(X) %d != len(z) %d" % (len(X), len(z))
        self.tree = KDTree( X, leafsize=leafsize )  # build the tree
        self.z = z
        self.stat = stat
        self.wn = 0
        self.wsum = None

    def __call__( self, q, nnear=6, eps=0, p=1, weights=None ):  # 使对象可调用
        # 每个插值点的最邻近
        q = np.asarray(q)   # 相当于复制一个相同的可变的数据
        qdim = q.ndim       # ndim返回的是数组的维度
        if qdim == 1:
            q = np.array([q])
        if self.wsum is None:
            self.wsum = np.zeros(nnear)   #创建元素全为 0 的数组

        self.distances, self.ix = self.tree.query( q, k=nnear, eps=eps )
        interpol = np.zeros( (len(self.distances),) + np.shape(self.z[0]) )
        jinterpol = 0
        for dist, ix in zip(self.distances, self.ix):
            if nnear == 1:
                wz = self.z[ix]
            elif dist[0] < 1e-10:
                wz = self.z[ix[0]]
            else:  # weight z s by 1/dist --
                w = 1 / dist**p
                if weights is not None:
                    w *= weights[ix]  # >= 0
                w /= np.sum(w)
                wz = np.dot(w, self.z[ix])    # 向量点积
                if self.stat:
                    self.wn += 1
                    self.wsum += w
            interpol[jinterpol] = wz
            jinterpol += 1
        return interpol if qdim > 1  else interpol[0]
os.chdir(r"D:\数据批量\表格")
out_path = "D:\数据批量\表格\IDW"
list = ['1950','1960','1980','1990','2000','2010','2020']
for k in list:
    df =pd.read_csv(f'TEMP_{k}_daily_.csv')
    for i in range(5, df.shape[1]):
        df1 = df[['2', '3', f'{i}']][~df[f'{i}'].isna()]
        known = df1[['2', '3']].values
        z = df1[f'{i}'].values
        ask = df[['2', '3']][df[f'{i}'].isna()].values
        invdisttree = Invdisttree(known, z, leafsize=5, stat=1)
        interpol = invdisttree(ask, nnear=20, eps=0.1, p=1)
        df[f'{i}'][df[f'{i}'].isna()] = interpol
    df.to_csv(out_path + '\\' + f'IDW_{k}_daily_.csv',index=False, float_format='%.1f')














    # 赋值
# df2 = df.reset_index()
# df2 = df2.set_index(['0', '经度', '纬度', '高程'])
# df2.to_csv('IDW_2016.txt', float_format='%.1f')
















































in_path = r"D:\自然\TEMP_1950_daily.dbf"
out_path = r"D:\插值\TEMP_1980_daily.csv"
df = gpd.read_file(in_path)
a = 9999.9
df[df==a] = np.nan
df.columns = range(len(df.columns))
df.to_csv(out_path,index=False)
