# -*- coding: utf-8 -*-
"""
Created on Fri May 17 18:54:39 2024

@author: hqm
"""
import pandas as pd
raw_data_1 = {
        'subject_id': ['1', '2', '3', '4', '5'],
        'first_name': ['Alex', 'Amy', 'Allen', 'Alice', 'Ayoung'], 
        'last_name': ['Anderson', 'Ackerman', 'Ali', 'Aoni', 'Atiches']}

raw_data_2 = {
        'subject_id': ['4', '5', '6', '7', '8'],
        'first_name': ['Billy', 'Brian', 'Bran', 'Bryce', 'Betty'], 
        'last_name': ['Bonder', 'Black', 'Balwner', 'Brice', 'Btisan']}

raw_data_3 = {
        'subject_id': ['1', '2', '3', '4', '5', '7', '8', '9', '10', '11'],
        'test_id': [51, 15, 15, 61, 16, 14, 15, 1, 61, 16]}


data1 = pd.DataFrame(raw_data_1, columns = ['subject_id', 'first_name', 'last_name'])
data2 = pd.DataFrame(raw_data_2, columns = ['subject_id', 'first_name', 'last_name'])
data3 = pd.DataFrame(raw_data_3, columns = ['subject_id','test_id'])



all_data = pd.concat([data1,data2])
all_data_col = pd.concat([data1, data2], axis = 1)

#数据连接pd.concat-----https://zhuanlan.zhihu.com/p/132593960
    # objs: 需要连接的数据，可以是多个DataFrame或者Series，它是必传参数
    # axis: 连接轴的方法，默认值为0，即按行连接，追加在行后面;值为1时追加到列后面(按列连接:axis=1)
    # join: 合并方式，其他轴上的数据是按交集(inner)还是并集(outer)进行合并
    # ignore_index: 是否保留原来的索引---- 1 新的索引
    # keys: 连接关系，使用传递的键作为最外层级别来构造层次结构索引，就是给每个表指定一个一级索引
    # names: 索引的名称，包括多层索引
    # verify_integrity: 是否检测内容重复;参数为True时，如果合并的数据与原数据包含索引相同的行，则会报错
    # copy: 如果为False，则不要深拷贝

pd.merge(all_data, data3, on ='subject_id')
pd.merge(data1, data2, on ='subject_id',how='inner')
pd.merge(data1, data2, on ='subject_id',how='outer')
#数据合并merge
#https://blog.csdn.net/Asher117/article/details/84725199
#https://blog.csdn.net/brucewong0516/article/details/82707492
#pd.merge(left, right, how='inner', on=None, left_on=None, right_on=None,
         # left_index=False, right_index=False, sort=True,
         # suffixes=('_x', '_y'), copy=True, indicator=False,
         # validate=None)
    # left: 拼接的左侧DataFrame对象
    # right: 拼接的右侧DataFrame对象
    # on: 要加入的列或索引级别名称。 必须在左侧和右侧DataFrame对象中找到。 如果未传递且left_index和right_index为False，则DataFrame中的列的交集将被推断为连接键。
    # left_on:左侧DataFrame中的列或索引级别用作键。 可以是列名，索引级名称，也可以是长度等于DataFrame长度的数组。
    # right_on: 左侧DataFrame中的列或索引级别用作键。 可以是列名，索引级名称，也可以是长度等于DataFrame长度的数组。
    # left_index: 如果为True，则使用左侧DataFrame中的索引（行标签）作为其连接键。 对于具有MultiIndex（分层）的DataFrame，级别数必须与右侧DataFrame中的连接键数相匹配。
    # right_index: 与left_index功能相似。
    # how: One of ‘left’, ‘right’, ‘outer’, ‘inner’. 默认inner。inner是取交集，outer取并集。比如left：[‘A’,‘B’,‘C’];right[’'A,‘C’,‘D’]；inner取交集的话，left中出现的A会和right中出现的买一个A进行匹配拼接，如果没有是B，在right中没有匹配到，则会丢失。'outer’取并集，出现的A会进行一一匹配，没有同时出现的会将缺失的部分添加缺失值。
    # sort: 按字典顺序通过连接键对结果DataFrame进行排序。 默认为True，设置为False将在很多情况下显着提高性能。
    # suffixes: 用于重叠列的字符串后缀元组。 默认为（‘x’，’ y’）。
    # copy: 始终从传递的DataFrame对象复制数据（默认为True），即使不需要重建索引也是如此。
    # indicator:将一列添加到名为_merge的输出DataFrame，其中包含有关每行源的信息。 _merge是分类类型，并且对于其合并键仅出现在“左”DataFrame中的观察值，取得值为left_only，对于其合并键仅出现在“右”DataFrame中的观察值为right_only，并且如果在两者中都找到观察点的合并键，则为left_only。


























