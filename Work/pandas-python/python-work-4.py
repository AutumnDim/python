# -*- coding: utf-8 -*-
"""
Created on Sat May 18 20:29:34 2024

@author: hqm
"""
import pandas as pd
import re
def dms_to_decimal(dms_str):    #将度分秒转化为十进制的函数
    parts = re.split('[°\'"]+', dms_str)    
    # re.split 是 Python 正则表达式库 re 中的一个函数，用于根据正则表达式模式拆分字符串。它类似于字符串方法 str.split，但更强大，因为它允许使用正则表达式定义拆分规则
    # re.split('[°\'"]+', dms_str): 使用正则表达式模式 '[°\'"]+' 拆分字符串 dms_str。
    # []：表示字符类，匹配括号内的任意一个字符。
    # °：匹配度符号。
    # '：匹配分符号。
    # "：匹配秒符号。
    # +：匹配前面的字符一次或多次。
    # 这将根据度（°）、分（'）和秒（"）符号拆分字符串。例如，字符串 "39°55'56.72\"" 将被拆分为 ['39', '55', '56.72']。
    degrees = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])
    decimal = degrees + (minutes / 60) + (seconds / 3600)
    return decimal
data = pd.read_excel(r"F:\厚德学习\Pandas__Python\python_work\4 经纬度转为十进制\气象局生态站地理坐标(1)(数据已修改) - 副本.xls", header=1)
data['经度'] = data['经度'].apply(dms_to_decimal)
data['纬度'] = data['纬度'].apply(dms_to_decimal)
data.to_csv(r"F:\厚德学习\Pandas__Python\python_work\4 经纬度转为十进制\k.csv",index=False)





