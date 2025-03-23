# -*- coding: utf-8 -*-
"""
Created on Sun May 12 17:02:36 2024

@author: hqm
"""
import pandas as pd
import numpy as np
ur1 =  https://github.com/justmarkham
chipo = pd.read_csv(ur1)
chipo.head(10)
chipo.shape()
chipo.info()
chipo.shape[1]
chipo.columns
chipo.index

chipo.groupby('item_name')
c = chipo.sum()
c = c.short_value('quantity',ascending=False)
c.head(1)

c = chipo.quantity.sum()
print(c)

chipo.item_price.btype

chipo = chipo(lambda x: float(x[1:-1]))



import pandas as pd
k = pd.read_csv('Downloads/Pandas__Python/pandas_exercises-master/02_Filtering_&_Sorting/Euro12_02.csv',)
euro12 = k
euro12 = euro12.Goal
euro12 = euro12.shape[0]
euro12 = euro12.info()
euro12 = euro12[['Team','YellowCard','RedCard',''] ]
euro12 = euro12.short_value(['Red Cards','Yellow'],ascending=False)

euro12 = euro12.groupby('Team')['Yellow'].mean()
# 筛选奖牌大于6枚的
euro12 = euro12[euro12['Goals']>6]
# 以G为开头
euro12 = euro12[euro12['Team'].str.startswith('G')]
# 读取前7列
euro12.iloc[:,0:7]
# 除最后三列之后的所有列
euro12.iloc[:,:-3]
# 
euro12.loc[euro12['Team'].isin(['England','Italy','Russia']),['Team','Shooting Accuracy']]
euro12.loc[euro12.Team.isin(['England','Italy','Russia']),['Team','Shooting Accuracy']]



# groupby

import pandas as pd
drinks = pd.read_csv(r'C:\Users\hqm\Desktop\u.user',sep='|')
drinks.head()
drinks.groupby('continent').beer_serving.mean()
drinks.groupby('continent').wine_servings.describe()
drinks.groupby('continent').mean()
drinks.groupby('continent').median()
drinks.groupby('cintinent').spirit_stats.agg(['mean','min','max'])


import pandas as pd
users = pd.read_csv(r'D:\厚德学习\Pandas__Python\pandas_exercises-master\03_Grouping\Occupation_02',sep='|',index_col=user_id)
users.head()
users.groupby('occupation').age.mean()

























































































