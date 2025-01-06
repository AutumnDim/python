# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 21:39:46 2024

@author: hqm
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import font_manager, rcParams
from matplotlib.ticker import MultipleLocator
# 指定中文字体路径
font_path = r"C:/WINDOWS/Fonts/SIMSUN.TTC"  # 确保路径正确
font_prop = font_manager.FontProperties(fname=font_path)  # 中文字体宋体

config = {
    "font.family": "serif",  # 使用衬线字体
    "font.size": 15,  # 字体大小
    "font.serif": ["Times New Roman"],  # Times New Roman 用于英文和数字
    "mathtext.fontset": "stix",  # 数学字体设置为 stix
    "axes.unicode_minus": False  # 解决负号显示问题
}

# 更新全局配置
rcParams.update(config)

# 在绘图时动态指定中文字体为宋体
import matplotlib.pyplot as plt

plt.rcParams['axes.unicode_minus'] = False  # 解决负号问题


df = pd.read_csv(r"F:\生态脆弱性\代码\上下图.csv")
df['Year'] = df['Year'].astype(int)
df.set_index('Year', inplace=True)
df = df/1000000

# 创建子图
fig, axs = plt.subplots(2, 1, figsize=(10, 14))

colors=["#4474C4", "#6FAE45", '#b7e1a1', "#e6daa6"]
labels = ['PWT', 'SWP', 'MSH', 'FFT']
for select,color in zip(labels,colors):
    axs[0].plot(df.index,df[select].values,color=color,lw=8,label=select)
    axs[0].grid(which="major",ls="--",lw=.8,zorder=0)

#axs[0].set_ylabel('Wetland Area/(km²)\n', fontsize=18)
#axs[0].set_ylabel('湿地面积', fontsize=18, fontproperties=font_prop)
axs[0].text(-0.1, 0.5, '湿地面积', fontsize=18, fontproperties=font_prop,
            ha='center', va='center', rotation='vertical', transform=axs[0].transAxes)

axs[0].text(-0.13, 0.5, 'Wetland Area/(km²)', fontsize=18, family="Times New Roman",
            ha='center', va='center', rotation='vertical', transform=axs[0].transAxes)
axs[0].tick_params(direction='out', length=6, width=1.2)
plt.xticks(np.arange(2001, 2020, 5), rotation=45, fontsize=15)
plt.yticks(fontsize=15)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tick_params(axis='x', direction='out', length=6, width=1)   # 设置刻度线朝外、长度、宽度
# 上图 堆叠图
axs[1].stackplot(df.index, df['PWT'] / df['Total Area'] * 100, df['SWP'] / df['Total Area'] * 100,
                  df['MSH'] / df['Total Area'] * 100, df['FFT'] / df['Total Area'] * 100,
                  labels=['Permanent water','Swamp','Marsh','Flooded flat','Total area'], colors=colors,
                  edgecolor='none')
axs[1].text(-0.1, 0.5, '百分比', fontsize=18, fontproperties=font_prop,
            ha='center', va='center', rotation='vertical', transform=axs[1].transAxes)
axs[1].text(0.2, -0.21, '常年水域', fontsize=15, fontproperties=font_prop,
            ha='center', va='center',  transform=axs[1].transAxes)
axs[1].text(0.465, -0.21, '沼泽', fontsize=15, fontproperties=font_prop,
            ha='center', va='center',  transform=axs[1].transAxes)
axs[1].text(0.66, -0.21, '草本湿地', fontsize=15, fontproperties=font_prop,
            ha='center', va='center',  transform=axs[1].transAxes)
axs[1].text(0.878, -0.21, '淹水滩涂', fontsize=15, fontproperties=font_prop,
            ha='center', va='center',  transform=axs[1].transAxes)
axs[1].text(-0.13, 0.5, 'Percentage/(%)', fontsize=18, family="Times New Roman",
            ha='center', va='center', rotation='vertical', transform=axs[1].transAxes)
#axs[1].set_ylabel('Percentage/(%)', fontsize=18)
axs[1].set_xlim(2001, 2022)
axs[1].set_ylim(0, 100)
axs[1].xaxis.set_major_locator(ticker.MultipleLocator(2))
axs[1].tick_params(direction='out', length=6, width=1.2)

# 使用 fig.legend 创建共享图例
plt.legend(loc='lower center', bbox_to_anchor=(0.5, -0.23), ncol=5, frameon=False,fontsize=15)




# 设置 X 轴刻度和网格线
for ax in axs:
    ax.tick_params(axis='x', direction='out', length=5, width=1)  # 设置刻度线朝外
    ax.grid(axis='y', linestyle='--', alpha=0.6)  # 仅设置 Y 轴网格线

# 分别为上下图设置 X 轴刻度
axs[0].set_xticks(np.arange(2001, 2023, 5))  # 上图设置为5年间隔
axs[1].set_xticks(np.arange(2001, 2023, 1))  # 下图设置为1年间隔
axs[0].tick_params(axis='x', labelrotation=0, labelsize=15)  # 上图 X 轴不旋转
axs[1].tick_params(axis='x', labelrotation=40, labelsize=15)  # 下图 X 轴旋转45°

# 如果需要对 Y 轴分别设置：
axs[0].tick_params(axis='y', labelrotation=0, labelsize=15)  # 上图 Y 轴不旋转
axs[1].tick_params(axis='y', labelrotation=40, labelsize=15)  # 下图 Y 轴旋转40°
axs[0].xaxis.set_major_locator(MultipleLocator(5))  # 上图：每5年一个刻度
axs[1].xaxis.set_major_locator(MultipleLocator(1))  # 下图：每1年一个刻度
# 设置 X 轴刻度标签旋转及字体
for ax in axs:
    #ax.tick_params(axis='x', labelrotation=0, labelsize=15)  # X 轴标签旋转和字体大小
    #ax.tick_params(axis='y',labelrotation=40, labelsize=15)  # Y 轴字体大小
    ax.xaxis.set_tick_params(pad=2)  # 调整标签与刻度线的距离
    ax.xaxis.set_ticks_position('bottom')  # 确保刻度线位于底部

# 调整子图间距以适配共享图例
#fig.subplots_adjust(hspace=0.1)

# 调整布局
plt.tight_layout(rect=[0, 0, 1, 0.95])  # 留出图例位置的空间
plt.subplots_adjust(hspace=0.1) 
# 可选保存图像
plt.savefig(r"F:\生态脆弱性\出图\上下分层图\上下分层图.pdf", dpi=300, bbox_inches='tight')

# 显示图表
plt.show()







# # 下图 
# selected_years = [2001, 2008, 2016, 2022]
# selected_data = df.loc[selected_years, df.columns]
# area_changes = selected_data.diff().dropna()
# area_changes.index = ['2001-2008', '2008-2016', '2016-2022']

# bar_width = 0.15
# index = np.arange(len(area_changes))
# bars1 = axs[1].bar(index - 1.5 * bar_width, area_changes['PWT'], width=bar_width, label='Permanent water',
#                    color='#1f77b4', edgecolor="black")
# bars2 = axs[1].bar(index - 0.5 * bar_width, area_changes['SWP'], width=bar_width, label='Swamp',
#                    color='#009337', edgecolor="black")
# bars3 = axs[1].bar(index + 0.5 * bar_width, area_changes['MSH'], width=bar_width, label='Marsh',
#                    color='#9dcf8e', edgecolor="black")
# bars4 = axs[1].bar(index + 1.5 * bar_width, area_changes['FFT'], width=bar_width, label='Flooded flat',
#                    color='#f1e2c2', edgecolor="black")
# bars5 = axs[1].bar(index + 2.5 * bar_width, area_changes['Total Area'], width=bar_width, label='Total area',
#                    color='#fec615', edgecolor="black")
# axs[1].set_ylabel('Wetland Area Change (km²)', fontsize=12)
# axs[1].set_xticks(index)
# axs[1].set_xticklabels(['2001-2008', '2008-2016', '2016-2022'])
# axs[1].axhline(0, color='black', linewidth=0.8)
# axs[1].tick_params(direction='in')