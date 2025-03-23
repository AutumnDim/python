# -*- coding: utf-8 -*-
"""
Created on Mon May 13 21:22:03 2024

@author: hqm
"""
# occupation
import pandas as pd
users = pd.read_csv(r'D:\厚德学习\Pandas__Python\pandas_exercises-master\03_Grouping\Occupation_02',sep='|',index_col='user_id')
users.head()
users.groupby('occupation').age.mean()


# gender_to_numeric 函数
def gender_to_numeric(gender):
    """
    将性别转换为数值表示
    :param gender: 性别，可以是 'Male' 或 'Female'
    :return: 数值表示，可能是 0 或 1
    """
    if gender == 'Male':
        return 1
    elif gender == 'Female':
        return 0
#    else:
#       return None  # 处理异常情况，比如输入既不是 'Male' 也不是 'Female'
users['gender_n'] = users['gender'].apply(gender_to_numeric)
k = users.groupby('occupation').gender_n.sum / users.occupation.value_counts() * 100
k.sort_values(ascending = False)


users.groupby('occupation').age.agg(['min','max'])

'''
df.agg() 是 Pandas DataFrame 对象的一个方法，
用于在 DataFrame 上应用一个或多个聚合函数。
它可以接受一个函数、一个函数列表或一个函数字典作为参数
以便对整个 DataFrame 或特定的列进行聚合计算。
下面是 df.agg() 方法的基本用法：
df.agg(func, axis=0) 
其中，参数含义如下：
• func：可以是一个函数、一个函数列表或一个函数字典。如果是函数，则会对整个 DataFrame 应用该函数；如果是函数列表，则会对每个列应用列表中的每个函数；如果是函数字典，则会对每个列应用字典中对应的函数。
• axis：指定应用函数的轴。默认为 0，表示沿着列进行操作；如果设置为 1，则沿着行进行操作。
下面是一些示例用法：
# 对整个 DataFrame 应用一个函数 
df.agg('mean') 

# 对每列应用多个函数 
df.agg(['mean', 'std']) 

# 对每列应用不同的函数 
df.agg({'A': 'sum', 'B': 'max'}) 

# 对每行应用一个函数
 df.agg('mean', axis=1)
 
'''

users.groupby(['occupation','gender']).age.mean()
gender_ocup = users.groupby(['occupation','gender']).agg({'age':'count'})
occup_count = users.groupby('occupation').agg('count')
occup_gender = gender_ocup.div(occup_count,level = "occupation") * 100
occup_gender.loc[: , 'gender']
# occup_count1 = users.sort_values('occupation').reset_index(drop=True)

# 重置索引
# df_reset = df.reset_index()
# div() 函数
# result = div(10, 2)
# print(result)  # 输出为 5







































