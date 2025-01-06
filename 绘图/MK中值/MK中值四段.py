# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 19:55:40 2024

@author: hqm
"""
from pathlib import Path
import pandas as pd
import numpy as np
import rasterio
from rasterio.plot import show
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import ticker, font_manager,rcParams
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LongitudeFormatter, LatitudeFormatter
from matplotlib.ticker import FuncFormatter, MaxNLocator
import frykit.plot as fplt
from scipy.stats import linregress
import seaborn as sns

# font_path = r"C:/WINDOWS/Fonts/SIMSUN.TTC" 
# font_prop = font_manager.FontProperties(fname=font_path)
font_path = r"C:/WINDOWS/Fonts/TIMES.TTF"
 
font_prop = font_manager.FontProperties(fname=font_path)

# 配置全局字体
config = {
    "font.family": "serif",  # 设置衬线字体
    "font.serif": ["SimSun"],  # 设置为宋体
    "font.size": 12,  # 设置字体大小
    "axes.unicode_minus": False,  # 处理负号
}
rcParams.update(config)


# 创建图形，调整子图间距以去除边框
fig = plt.figure(figsize=(7, 9)) 
# 使用 subplot 来设置子图布局
ax1 = plt.subplot(3, 2, 1)  # 第1行第1列
ax2 = plt.subplot(3, 2, 2)  # 第1行第2列
ax3 = plt.subplot(3, 2, 3)  # 第2行第1列
ax4 = plt.subplot(3, 2, 4)  # 第2行第2列
ax5 = plt.subplot(3, 2, (5, 6))  # 第3行，跨越两列
axs = [ax1, ax2, ax3, ax4, ax5]

# 定义文件路径、颜色、文本等信息
gdf = gpd.read_file(r"F:\生态脆弱性\数据\MK中值\MK中值\pr\区域面积\区域面积pr.shp")
gdf1 = gpd.read_file(r"F:\生态脆弱性\数据\MK中值\MK中值\pr\区域面积\区域面积融合pr.shp")
directory = Path(r"F:\生态脆弱性\数据\MK中值\MK中值\pr")
filenames = ['2001_2008', '2008_2016', '2016_2022', '2001_2022']
file_paths = [directory / (filename+"趋势分析.tif") for filename in filenames]
list2 = []
bar_color = ["#4474C4","#589CD6","#6FAE45","#FFC101","#EF7E33"]
txts = ['(a) 2001-2008','(b) 2008-2016','(c) 2016-2022','(d) 2001-2022']
cmap = matplotlib.colors.ListedColormap(bar_color).reversed()


lon_min, lon_max = 114, 118.2
lat_min, lat_max = 27, 30.5
xticks = [114,  116,  118]
yticks = [ 28.0,  29,  30]
# 定义格式化函数用于显示经纬度，带有"N"和"E"
def lon_formatter(x, pos):
    return f'{x:.1f}°E'
def lat_formatter(x, pos):
    return f'{x:.1f}°N'    
def draw_the_scale(ax, text, length=0.5, height=0.01, lw=0.00):
    # 设置比例尺的黑白部分比例，只有两个部分，黑色和白色各占一半
    black_white_ratio = [0.5, 0.5]  # 黑白各一半
    y = 0.02  # 比例尺的y位置
    x = 0.42  # 比例尺的x位置

    # 矩形框
    ax.add_patch(plt.Rectangle((x, y), length, height, transform=ax.transAxes, color='black'))

    # 绘制比例尺的黑白条段
    position = x
    for i in range(2):  # 只有两个部分
        # 在矩形框内绘制黑白条段
        color = 'black' if i == 0 else 'white'  # 第一个部分为黑色，第二个部分为白色
        ax.add_patch(plt.Rectangle((position, y), black_white_ratio[i] * length, 0.035, transform=ax.transAxes, color=color, lw=lw))
        position += black_white_ratio[i] * length

    # 添加比例尺上的文字
    ax.text(x - 0.02, y + 0.053, '0', transform=ax.transAxes, fontsize=12, ha='center',family="Times New Roman")
    ax.text(x + length , y + 0.053, text, transform=ax.transAxes, fontsize=12, ha='center',family="Times New Roman")
    ax.text(x + 0.5 * length + 0.0, y + 0.053, '50', transform=ax.transAxes, fontsize=12, ha='center',family="Times New Roman")
    ax.text(x+0.48 , y-0.01 , 'KM', transform=ax.transAxes, fontsize=11, ha='center',family="Times New Roman")
    
# 例子中的绘图部分
for i, file in enumerate(file_paths):
    with rasterio.open(file) as src:
        profile = src.profile  
        data = src.read(1)
        nodata = src.nodata
        data[data == nodata] = np.nan  # 替换无数据值
        bounds = src.bounds
        transform = src.transform
        extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
        
        # 绘制栅格数据
        axs[i].imshow(data, origin='upper', extent=extent, cmap=cmap, vmin=-2, vmax=2) 
        
        # 绘制矢量边界
        gdf.plot(ax=axs[i], edgecolor='gray', facecolor='none', linewidth=1)
        gdf1.plot(ax=axs[i], edgecolor='black', facecolor='none', linewidth=1)
        
        axs[i].axis('on')
        
        # 设置经纬网范围
        axs[i].set_xlim(lon_min, lon_max)
        axs[i].set_ylim(lat_min, lat_max)

        axs[i].set_xticks(xticks)  # 使用提供的 xticks 刻度
        axs[i].tick_params(axis='x', labelrotation=1, labelsize=12, direction='out')  
        axs[i].set_yticks(yticks)  # 使用提供的 yticks 刻度
        axs[i].tick_params(axis='y', labelrotation=0, labelsize=12, direction='out')  
        axs[i].tick_params(axis='both', direction='out', which='both', length=6, width=1, labelsize=12)

        # 调整刻度字体样式
        for label in axs[i].get_xticklabels() + axs[i].get_yticklabels():
            label.set_fontproperties(font_prop)  # 自定义字体样式  # 自定义字体样式
            
            

        # 使用 FuncFormatter 添加经度"E"和纬度"N"的刻度单位
        axs[i].xaxis.set_major_formatter(FuncFormatter(lon_formatter))
        axs[i].yaxis.set_major_formatter(FuncFormatter(lat_formatter))

     # 设置y轴刻度
        axs[i].spines['top'].set_visible(True)
        axs[i].spines['right'].set_visible(True)
        axs[i].spines['bottom'].set_visible(True)
        axs[i].spines['left'].set_visible(True)
        plt.rcParams['xtick.direction'] = 'out'
        plt.rcParams['ytick.direction'] = 'out'
        # 添加经纬网
        axs[i].tick_params(axis='both', direction='out', length=7, width=1, color='black')  # 外部刻度
        plt.draw()
        #axs[i].grid(True)  # 禁用内部网格线
       
        
        # 设置边框的线条样式
        axs[i].spines['top'].set_linewidth(1.5)
        axs[i].spines['right'].set_linewidth(1.5)
        axs[i].spines['bottom'].set_linewidth(1.5)
        axs[i].spines['left'].set_linewidth(1.5)
        # 添加指北针
        fplt.add_compass(axs[i], 0.93, 0.81, size=20)
        # 添加比例尺
        
        #scale_bar = fplt.add_scale_bar(axs[i], 0.7, 0.08, length=100)
        #scale_bar.set_xticks([0, 50, 100])
        draw_the_scale(axs[i], '100', length=0.4, height=0.035) 
        axs[i].axis('on')
        # 添加文本
        axs[i].text(0.03, 0.9, txts[i], transform=axs[i].transAxes,family="Times New Roman")
        
        # 计算类别
        a = np.sum(data == 2)
        b = np.sum(data == 1)
        c = np.sum(data == 0)
        d = np.sum(data == -1)
        e = np.sum(data == -2)
        list1 = [a, b, c, d, e]
        list2.append(list1)
# 绘制条形图
labels = [4, 3, 2, 1]
bar_label = ["显著增加",'不显著增加','稳定不变','显著减少','不显著减少']
width = .3
df = pd.DataFrame(list2, columns=bar_label)
sums = df.sum(axis=1)
left_y = np.zeros(len(labels))

for j, color, label in zip(df, bar_color, bar_label):
    data = df[j]
    y = data/sums
    axs[4].barh(labels, y, color=color, label=label, left=left_y, ec='k')
    left_y = y + left_y

# 设置轴和图例
axs[4].tick_params(which='major', direction='out', length=3, width=1., bottom=False)
for spine in ["top", "bottom", "right"]:
    axs[4].spines[spine].set_visible(False)
axs[4].spines['left'].set_linewidth(2)
axs[4].set_yticks([1, 2, 3, 4])
axs[4].set_yticklabels(["d", "c", "b", "a"],fontproperties=font_prop, fontsize=12)

axs[4].xaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
axs[4].tick_params(axis='x', labelsize=12)  # 设置字体大小
for label in axs[4].get_xticklabels():
    label.set_fontproperties(font_prop) 

for c in axs[4].containers:
    axs[4].bar_label(c, label_type='center', fontsize=12, 
                     labels=[str(round(i*100, 1)) for i in c.datavalues], 
                     color="w", fontweight="bold", fontproperties=font_prop)

axs[4].legend(ncol=5, frameon=False, loc='lower center', bbox_to_anchor=(0.48, -0.3), fontsize=12, handletextpad=0.08, labelspacing=0.5,columnspacing=0.4)


# 调整布局去除边框
plt.tight_layout()
plt.subplots_adjust()
plt.savefig(r"F:\生态脆弱性\出图\MK中值\四段k.png", dpi=300)
plt.show()
