# -*- coding: utf-8 -*-
"""
Created on Fri May 17 20:56:28 2024

@author: hqm
"""
import pandas as pd
baby_name = pd.read_csv(r"D:\代码存放\pandas_exercises-master\06_Stats\US_Baby_Names\US_Baby_Names_right.csv")
baby_name.info()
baby_name.head()

del baby_name['Unnamed: 0']
del baby_name['Id']
baby_name.head()


#  *元组，**字典
def dels(df,*args):
    
    for arg in args:
        del df[arg]
    
    return(df)

dels(baby_name,*['Unnamed: 0','Id'])



# pandas 计数函数value_counts()
#value_counts(normalize=False, sort=True, ascending=False, bins=None, dropna=True)
    # normalize : boolean, default False　默认false，如为true，则以百分比的形式显示
    # sort : boolean, default True　默认为true,会对结果进行排序
    # ascending : boolean, default False　默认降序排序
    # bins : integer, 格式(bins=1),意义不是执行计算，而是把它们分成半开放的数据集合，只适用于数字数据
    # dropna : boolean, default True　默认删除na值
#https://blog.csdn.net/Late_whale/article/details/103317396


# Python中的count()函数是一种非常常用的方法，用于统计某个元素在列表、元组或字符串中出现的次数。
# count = numbers.count([1, 2])
# count = text.count('Python')


baby_name['Gender'].value_counts()
del baby_name['Year']
name = baby_name.groupby('Name').sum()
name.head()
name.shape
name.sort_values('Count',ascending = 0).head()
# 出现名字次数最多的
name.Count.idxmax()
# or
# name[name.Count == name.Count.max()]

name.Count.idxmin()


# 有多少个名字出现最少
len(name[name.Count == name.Count.min()])
# len 返回行数
name[name.Count == name.Count.median()]
name.Count.std()
name.describe()

















