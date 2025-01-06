# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 15:59:53 2024

@author: hqm
"""
import pandas as pd
import matplotlib.pyplot as plt
from pysankey2 import Sankey
import os
from matplotlib import font_manager, rcParams
import seaborn as sns
# 设置绘图主题
sns.set_theme(style="white", palette=None)



font_path = r"C:/WINDOWS/Fonts/SIMSUN.TTC"  # 替换为你的中文字体路径
font_prop = font_manager.FontProperties(fname=font_path)
config = {
    "font.family": font_prop.get_name(),  # 衬线字体族
    "font.size": 15,  # 相当于小四大小
    "font.serif": ["Times New Roman", "SimSun"],  # 设置serif字体族的字体列表，按优先级排序
    "mathtext.fontset": 'stix',  # matplotlib渲染数学字体时使用的字体，和Times New Roman差别不大
    'axes.unicode_minus': False  # 处理负号，即-号
}
rcParams.update(config)
# 文件路径
path = "F:\生态脆弱性\数据\桑基图数据\桑基图数据\EVI_levels.csv"
out = r"F:\生态脆弱性\出图\桑基图"

# 读取数据
df = pd.read_csv(path)

# 定义颜色字典
colorDict = {
    'I': '#fe828c',  
    'II': '#ffb16d',  
    'III': '#fcf679',  
    'IV': '#c1c6fc',  
    'V':  '#abd0f1'
}
# 定义顺序
order = ['V', 'IV', 'III', 'II', 'I']

# 将数据转换为类别并排序
df['2001'] = pd.Categorical(df['2001'], categories=order, ordered=True)
df['2010'] = pd.Categorical(df['2010'], categories=order, ordered=True)
df['2022'] = pd.Categorical(df['2022'], categories=order, ordered=True)
df = df.sort_values(by=['2001', '2010', '2022'])

# 绘制桑基图
sky1 = Sankey(df, colorMode="global", stripColor='left', colorDict=colorDict)
fig, ax = sky1.plot(figSize=(10, 8), fontSize=15, boxWidth=.9, text_kws={"family": "Times New Roman"})
# 添加标签
years = ['2001', '2010', '2022']
x_positions = [0.5, 11.3, 22.2]  # 调整x轴位置以增加间隔,三个数字代表每个柱子的位置
y_position = -3  # 调整y轴位置，使标签在图表下方
for i, year in enumerate(years):
    ax.text(x_positions[i], y_position, year, ha='center', va='top', fontsize=15, weight='bold', family='Times New Roman')
plt.text(0.5, -0.01, 'Years', 
         fontsize=18, 
         family="Times New Roman", 
         ha='center', va='center', 
         transform=plt.gca().transAxes)  # 基于轴坐标添加英文标签
plt.text(0.56, -0.008, '年份', 
         fontsize=18, 
         fontproperties=font_prop, 
         ha='center', va='center', 
         transform=plt.gca().transAxes)  # 基于轴坐标添加中文标签
plt.subplots_adjust(bottom=0.5)  # 调整图形底部的边距，增大bottom值以增加图形底部空间
plt.tight_layout()
fig.savefig(os.path.join(out, '桑基图k.png'), bbox_inches='tight', dpi=300)
