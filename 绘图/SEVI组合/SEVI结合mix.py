# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 09:46:13 2025

@author: hqm
"""
import geopandas as gpd
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams,font_manager

sns.set_theme(style="white", palette=None)
font_path = r"C:/WINDOWS/Fonts/SIMSUN.TTC"  # 替换为你的中文字体路径
font_prop = font_manager.FontProperties(fname=font_path)
# 设置绘图主题
sns.set_theme(style="white", palette=None)
config = {
    "font.family": "Times New Roman",
#    "font.size": 15,
    "font.serif": ["Times New Roman"],
    "mathtext.fontset": 'stix',
    'axes.unicode_minus': False
}
rcParams.update(config)

# 读取数据
path = r"F:/生态脆弱性/数据/sevi组合/sevi组合/条形.xlsx"
path1 = r"F:/生态脆弱性/数据/sevi组合/sevi组合/SEVI.xlsx"
coord_path = r"F:/生态脆弱性/数据/sevi组合/sevi组合/区域坐标.xlsx"
pathk = r"F:/生态脆弱性/数据/sevi组合/sevi组合/密度.xlsx"

dfk = pd.read_excel(pathk)
df = pd.read_excel(path).round(2)
df1 = pd.read_excel(path1).round(2)
coord_df = pd.read_excel(coord_path)

# 地图数据
map_fig = gpd.read_file(r"F:/生态脆弱性/数据/sevi组合/sevi组合/区域面积.shp")

# 定义柱状图函数
def map_bar3(height, x_pos, y_pos, adjust, ax_width, ax_height, main_ax):
    x = np.arange(1, len(height) + 1)
    ax_bar = main_ax.inset_axes([x_pos - adjust, y_pos - adjust, ax_width, ax_height],
                                transform=main_ax.transData)
    ax_bar.bar(x, height, width=1, ec="k", lw=.3, color=colors[:len(height)])
    ax_bar.set_facecolor("none")
    ax_bar.grid(False)
    ax_bar.tick_params(which="both", labelleft=False, left=False, bottom=False, labelbottom=False)
    for spine in ["left", "top", "right"]:
        ax_bar.spines[spine].set_visible(False)
    return ax_bar

# 定义颜色
#colors = ["#9AC9DB", "#F8AC8C", "#BEB8DC"]
colors = ["#9AC9DB", "#F8AC8C", "#BEB8DC","#8ECFC9","#FEA3A2"]
years = [2001, 2010, 2022]
heights = df1[years].values.tolist()
coordinates = coord_df[['x', 'y']].values  # 提取坐标

# 创建布局
fig = plt.figure(figsize=(12, 12), dpi=100)
grid = plt.GridSpec(4, 4, hspace=0.4, wspace=0.4)

# 主图（地图和柱状图）
ax_main = fig.add_subplot(grid[1:, :3])
map_fig.plot("country", legend=False, ec="k", lw=.5, color='#E7EFFA', alpha=.8, ax=ax_main)

# 设置主图范围
x_min, x_max = 114.3, 118.2  # 经度范围
y_min, y_max = 27.3, 30.6  # 纬度范围
ax_main.set_xlim(x_min, x_max)
ax_main.set_ylim(y_min, y_max)

ax_main.tick_params(axis='both', which='major', labelsize=17, direction='in')
# 绘制柱状图
for (x, y), height in zip(coordinates, heights):
    adjust = 0.05
    map_bar = map_bar3(height, x_pos=x, y_pos=y, adjust=adjust, ax_width=0.2, ax_height=0.1, main_ax=ax_main)

# # 设置图例
# labels = ["2001", "2010", "2022","2001-2010","2010-2022"]
# handles = [plt.Rectangle((0, 0), 0.6, 2, color=color) for color in colors]
# legend1 = ax_main.legend(handles, labels, loc='upper right', fontsize=15, title_fontsize=15)
# legend1.get_frame().set_edgecolor('black')
# legend1.get_frame().set_linewidth(0.5)



import matplotlib.lines as mlines

# 设置颜色
colors = ["#9AC9DB", "#F8AC8C", "#BEB8DC","#8ECFC9","#FEA3A2"] 
labels = ["2001", "2010", "2022", "2001-2010", "2010-2022"]
handles = [plt.Rectangle((0, 0), 0.6, 2, color=color) for color in colors[:3]]
line_handles = [mlines.Line2D([0], [0], color=color, lw=2) for color in colors[3:]]
handles.extend(line_handles)#合并
legend1 = ax_main.legend(handles, labels, loc='upper right', fontsize=17, title_fontsize=15)
legend1.get_frame().set_edgecolor('black')
legend1.get_frame().set_linewidth(0.5)
for line_handle in line_handles:
    line_handle.set_markersize(6)  # 可以调整线条的样式，比如设置markersize


# 设置主图轴标签
ax_main.set_xlabel("Longitude", fontsize=20)
ax_main.set_ylabel("Latitude", fontsize=20)
ax_main.xaxis.set_label_coords(0.5, -0.05)  
ax_main.yaxis.set_label_coords(-0.1, 0.52) 
plt.text(-0.08, 0.52,'经度' , fontsize=20, fontproperties=font_prop ,
         ha='center', va='center', rotation='vertical', transform=plt.gca().transAxes)
plt.text(0.5, -0.1,'纬度' , fontsize=20, fontproperties=font_prop ,
         ha='center', va='center',  transform=plt.gca().transAxes)
# 上方密度图（基于经度的分布）
ax_top = fig.add_subplot(grid[0, :3])
sns.kdeplot(
    x=dfk["x"], 
    weights=dfk["2001-2010"].abs(), 
    label="2001-2010", 
    color="#8ECFC9", 
    linewidth=2, 
    ax=ax_top,
    fill=False
)
sns.kdeplot(
    x=dfk["x"], 
    weights=dfk["2010-2022"].abs(), 
    label="2010-2022", 
    color="#FEA3A2", 
    linewidth=2, 
    ax=ax_top,
    fill=False
)
# ax_top.tick_params(axis="x", bottom=False, labelbottom=False)  # 隐藏 x 轴
# ax_top.set_ylabel("Density")
# ax_top.legend(fontsize=15, loc="upper right", handlelength=0.5,bbox_to_anchor=(1.2, 0.86))


# 右侧密度图（基于纬度的分布）
ax_right = fig.add_subplot(grid[1:, 3])
sns.kdeplot(
    y=dfk["y"], 
    weights=dfk["2001-2010"].abs(), 
    label="2001-2010", 
    color="#8ECFC9", 
    linewidth=2, 
    ax=ax_right,
    fill=False
)
sns.kdeplot(
    y=dfk["y"], 
    weights=dfk["2010-2022"].abs(), 
    label="2010-2022", 
    color="#FEA3A2", 
    linewidth=2, 
    ax=ax_right,
    fill=False
)
# ax_right.tick_params(axis="y", left=False, labelleft=False)  # 隐藏 y 轴
# ax_right.set_xlabel("Density")
# ax_right.legend(fontsize=10, loc="upper right")

ax_right.set_position([0.8535, 0.11, 0.1, 0.75])
ax_top.set_position([0.117, 0.861, 0.735, 0.1]) 
ax_main.set_position([0.11, 0.11, 0.75, 0.75]) 
# 移除坐标轴标注、刻度和标签
ax_top.set_xticks([])
ax_top.set_yticks([])
ax_top.set_xlabel("")
ax_top.set_ylabel("")
ax_top.spines['top'].set_visible(False)  # 隐藏边框
ax_top.spines['right'].set_visible(False)  
ax_top.spines['left'].set_visible(False)  
ax_top.spines['bottom'].set_visible(False)  
ax_right.set_xticks([])
ax_right.set_yticks([])
ax_right.set_xlabel("")
ax_right.set_ylabel("")
ax_right.spines['top'].set_visible(False)
ax_right.spines['right'].set_visible(False)
ax_right.spines['left'].set_visible(False)
ax_right.spines['bottom'].set_visible(False)
# 调整布局
plt.savefig(r"F:\生态脆弱性\出图\SEVI组合\密度.PDF", dpi=300)
plt.tight_layout()
plt.show()




