# -*- coding: utf-8 -*-
"""
Created on Sun May  5 14:27:46 2024

@author: hqm
"""
'''
# 从列表 数组 字典构建series
import pandas as pd 
import numpy as np
mylist = list('abcdefghijklmnopqrsthuvwxyz')
myarr = np.arange(26)
mydict = dict(zip(mylist,myarr))
ser1 = pd.Series(mylist)
ser2 = pd.Series(myarr)
ser3 = pd.Series(mydict)
print(ser3.head())




# 使series的索引列转化为dataframe的列
import pandas as pd
import numpy as np
mylist = list ('abcdefg')
myarr = np.arange(7)
mydict = dict(zip(mylist,myarr))
ser = pd.Series(mydict)
# series 转换为dataframe
df = ser.to_frame()
# 索引列转换为dataframe的列
df.reset_index(inplace=True)
print(df.head())




# 创建DataFrame

import pandas as pd 

data = {'Site':['Google','Runoob','Wiki'],'Age':[10,12,13]}
df = pd.DataFrame(data)
print(df)



# ndarrays构建DataFrame
import numpy as np
import pandas as pd
ndarray_data = np.array([
    ['Google',10],
    ['Runoob',12],
    ['Wiki',13]
])
df = pd.DataFrame(ndarray_data,columns=['Site','Age'])
print(df)



import pandas as pd 
data = [{'a':1,'b':2},{'a':5,'b':9,'c':6}]
df = pd.DataFrame(data)
print(df)




# 从列表的列表创建
import pandas as pd
df = pd.DataFrame([[1,2,3],[4,5,6],[7,8,9]],
                  columns=['Column1','Column2','Column3'])
print(df)



# 从字典创建
import pandas as pd
df = pd.DataFrame({'Column1':[1,2,3],'Column2':[4,5,6]})
print(df)




# 从Numpy数组创建
import pandas as pd
import numpy as np
df = pd.DataFrame(np.array([[1,2,3],[4,5,6],[7,8,9]]))
print(df)




# 从Series创建DataFrame

import pandas as pd
s1 = pd.Series(['Alice','Bob','Charlie'])
s2 = pd.Series([22,33,44])
s3 = pd.Series(['new york','la','china'])
df = pd.DataFrame({'name':s1,'age':s2,'city':s3})
print(df)




# 修改DataFrame
import pandas as pd
df =['Column1'] = [10, 11, 12]
df['NewColumn'] = [100, 111, 222]
df.loc[3] = [13, 14, 15, 16]

'''

# CSV












































































































































































































































































































































































































































































































































































































