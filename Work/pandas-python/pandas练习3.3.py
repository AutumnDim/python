# -*- coding: utf-8 -*-
"""
Created on Tue May 14 19:06:35 2024

@author: hqm
"""
import pandas as pd 
raw_data = {'regiment': ['Nighthawks', 'Nighthawks', 'Nighthawks', 'Nighthawks', 'Dragoons', 'Dragoons', 'Dragoons', 'Dragoons', 'Scouts', 'Scouts', 'Scouts', 'Scouts'], 
        'company': ['1st', '1st', '2nd', '2nd', '1st', '1st', '2nd', '2nd','1st', '1st', '2nd', '2nd'], 
        'name': ['Miller', 'Jacobson', 'Ali', 'Milner', 'Cooze', 'Jacon', 'Ryaner', 'Sone', 'Sloan', 'Piger', 'Riani', 'Ali'], 
        'preTestScore': [4, 24, 31, 2, 3, 4, 24, 31, 2, 3, 2, 3],
        'postTestScore': [25, 94, 57, 62, 70, 25, 94, 57, 62, 70, 62, 70]}



# 通过字典创建DataFrame
# pandas.DataFrame(data=None, index=None, columns=None, dtype=None, copy=False)
regiment = pd.DateFrame(raw_data,columns = raw_data.keys())

regiment[regiment['regiment'] == 'Nighthawks'].groupby.('regiment').mean



# df.describe()	显示数据的基本统计信息，包括均值、方差、最大值、最小值等；
regiment.groupby('company').describe()
regiment.groupby('company').preTestScore.mean()



# 根据列 'A' 进行分组
# grouped = df.groupby('A')
# 根据列 'A' 和 'B' 进行分组
# grouped = df.groupby(['A', 'B'])
regiment.groupby(['regiment','company']).preTestScore.mean()


regiment.groupby(['regiment','company']).preTestScore.ment().unstack()
regiment.groupby(['regiment','company']).preTestScore.ment().reset_index()
# unstack() 是 Pandas 中的一个函数，用于将具有多层索引的 Series 或 DataFrame 转换为具有更少维度的表格形式。
# 具体来说，它将一个多层级的索引的 DataFrame 中的其中一个层级转换为列。
# unstack() 还可以指定要转换的索引级别的位置，默认是转换最内层的索引。
# 可以通过传递级别的位置或名称来指定要转换的索引级别。


# 使用 unstack() 指定要转换的索引级别的位置
# unstacked_df = df.unstack(level=0)  # 将 'group' 级别转换为列
# 使用 unstack() 指定要转换的索引级别的名称
# unstacked_df = df.unstack(level='group')  # 将 'group' 级别转换为列



regiment.groupby(['regiment','company']).mean()
# size() 是 Pandas 中的一个函数，用于返回一个 Series，其中包含每个分组的元素数量。
# 它通常与 groupby() 结合使用，用于计算每个分组的大小或数量。
regiment.groupby(['regiment','company']).size()
# 遍历一个组，并打印名字和整个数据
for name, group in regiment.groupby('regiment'):
    print(name)
    print(group)








































