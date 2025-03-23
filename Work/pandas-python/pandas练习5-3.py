# -*- coding: utf-8 -*-
"""
Created on Fri May 17 20:34:24 2024

@author: hqm
"""
import pandas as pd
import numpy as np
s1 = pd.Series(np.random.randint(1, high=5, size=100, dtype='l'))
s2 = pd.Series(np.random.randint(1, high=4, size=100, dtype='l'))
s3 = pd.Series(np.random.randint(10000, high=30001, size=100, dtype='l'))
k = pd.concat([s1,s2,s3], axis=1)
k.head()



#df.rename(index、columns、axis = mapper,inplace = 1)。mapper(映射关系)：函数或字典
#默认为行index、columns、axis，inplace原地(更改)
k.rename(column = {0: 'bedrs',1: 'bathrs',2: 'price_sqr_meter'},inplace=True)
k.head()
m = pd.concat([s1,s2,s3],axis=0)
#Series.to_frame(name=None)
m1 = m.to_frame()
type(m1)

len(m1)
# 计算列的长度


m1.reset_index(drop=True,inplace=True)

# reset_index()函数会重新设置DataFrame的索引，如果设置了drop=True，则会丢弃原来的索引，生成一个新的默认整数索引。
# drop=True表示丢弃原来的索引列，如果为False，则会保留原来的索引列。
# inplace=True表示在原DataFrame上进行修改，如果为False，则会返回一个新的DataFrame，不修改原来的DataFrame。