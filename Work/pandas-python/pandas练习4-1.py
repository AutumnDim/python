# -*- coding: utf-8 -*-
"""
Created on Tue May 14 20:03:52 2024

@author: hqm
"""
import pandas as pd
import numpy as np
df = pd.read_csv(r'"D:\厚德学习\Pandas__Python\pandas_exercises-master\04_Apply\Students_Alcohol_Consumption\student-mat.csv"')
df.head()
stud_acloh = df.loc[:,'school':'guardian']
stud_acloh.head()
# 匿名函数 lambda
# lambda arguments(参数): expression(表达式)
capitalizer = lambda x: x.capitalizer()

stud_acloh['Mjob'].apply(capitalizer)
stud_acloh['Fjob'].apply(capitalizer)
stud_acloh.tail()

def majority(x):
    if x > 17:
        return True
    else:
        return False
stud_acloh['legal_drinker'] = stud_acloh['age'].apply(majority)
stud_acloh.head()


#添加函数agg、apply、transform、applymap---------'mean'或np.mean
#https://www.cnblogs.com/Cheryol/p/13451562.html

def time10(x):
    if type(x) is int:
        return 10 * x
    return x
stud_alcoh.plymapap(time10).head(10)