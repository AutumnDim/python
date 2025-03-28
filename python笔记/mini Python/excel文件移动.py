# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 19:22:23 2025

@author: hqm
"""

import pandas as pd
import os
from glob import glob as glb

# 设置路径
path = r"F:\work\水文资料\数据后\鄱阳湖区站点水文数据"

# 获取所有的 "逐日平均流量表.xlsx" 文件
fist = glb(path + "*/*逐日平均流量表.xlsx")

# 创建一个 Excel 文件，将所有数据写入该文件
with pd.ExcelWriter(path + os.sep + '合并后的流量表.xlsx', engine='xlsxwriter') as writer:
    for i in fist:
        # 获取文件名并提取工作表名称
        name = os.path.basename(i).split('站')[0][4:]

        # 读取 Excel 文件中的数据
        df = pd.read_excel(i)

        # 将数据写入新的 Excel 文件，并以 name 为工作表的名字
        df.to_excel(writer, sheet_name=name, index=False)

print("所有文件已成功写入合并后的 Excel 文件！")
