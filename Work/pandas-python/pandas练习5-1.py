# -*- coding: utf-8 -*-
"""
Created on Fri May 17 18:16:47 2024

@author: hqm
"""
import pandas as pd 
import numpy as np
cars1 = pd.read_csv(r"D:\厚德学习\Pandas__Python\pandas_exercises-master\05_Merge\Auto_MPG\cars1.csv")
cars2 = pd.read_csv(r"D:\厚德学习\Pandas__Python\pandas_exercises-master\05_Merge\Auto_MPG\cars2.csv")
cars1.head()
cars2.head()

print(cars1.head())
print(cars2.head())

cars1 = cars1.loc[:, "mpg":"car"]
cars1.head()

print(cars1.shape)
print(cars2.shape)



#df连接
#df = df1.append(df2)--------ignore_index：默认值为False，如果为True则不使用index标签
#cars = cars1.append(cars2)
cars = pd.concat([cars1,cars2],ignore_index=True)
# 这段代码按行（默认行为）连接cars1和cars2，并重新索引结果DataFrame。
# 如果你需要按列连接它们，可以指定axis=1：
cars3 =pd.concat([cars1,cars2],axis=1)


#生成随机数组
#numpy.random.randint(low, high=None, size=None, dtype='l')
    # low: int
    # 生成的数值最低要大于等于low。
    #（hign = None时，生成的数值要在[0, low)区间内）

    # high: int (可选)
    # 如果使用这个值，则生成的数值在[low, high)区间。

    # size: int or tuple of ints(可选)
    # 输出随机数的尺寸，比如size = (m * n* k)则输出同规模即m * n* k个随机数。默认是None的，仅仅返回满足要求的单一随机数。

    # dtype: dtype(可选)：
    # 想要输出的格式。如int64、int等等


owners = np.random.randint(15000, high=73001, size=60, dtype='l')
cars['owners'] = owners
cars.tail()




































