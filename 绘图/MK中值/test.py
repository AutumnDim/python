# -*- coding: utf-8 -*-
"""
Created on Sun Sep  8 11:45:37 2024

@author: A1827
"""
from pathlib import Path
import pandas as pd
import numpy as np
import rasterio
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling
import geopandas as gpd
import frykit.plot as fplt
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.ticker import FuncFormatter, PercentFormatter
import matplotlib
from matplotlib import rcParams
config = {
    "font.family": 'serif', # 衬线字体
    "font.size": 12, # 相当于小四大小
    "font.serif": ['SimSun'], # 宋体
    "mathtext.fontset": 'stix', # matplotlib渲染数学字体时使用的字体，和Times New Roman差别不大
    'axes.unicode_minus': False # 处理负号，即-号
}
rcParams.update(config)

# 创建图形
fig = plt.figure(figsize=(10, 18))

# 使用 subplot2grid 来设置子图布局
ax1 = plt.subplot2grid((3, 2), (0, 0))  # 第0行第0列
ax2 = plt.subplot2grid((3, 2), (0, 1))  # 第0行第1列
ax3 = plt.subplot2grid((3, 2), (1, 0))  # 第1行第0列
ax4 = plt.subplot2grid((3, 2), (1, 1))  # 第1行第1列
ax5 = plt.subplot2grid((3, 2), (2, 0), colspan=2)  # 第2行，跨越两列
axs = [ax1,ax2,ax3,ax4,ax5]

gdf = gpd.read_file(r"F:\生态脆弱性\数据\MK中值\MK中值\data\区域面积.shp")
gdf1 = gpd.read_file(r"F:\生态脆弱性\数据\MK中值\MK中值\data\区域面积融合.shp")

# 定义文件路径
directory = Path(r"F:\生态脆弱性\数据\MK中值\MK中值")
filenames = ['2001_2008','2008_2016','2016_2022','2001_2022']
file_paths = [directory / (filename+"趋势分析.tif") for filename in filenames]
list2 = []
bar_color = ["#4474C4","#589CD6","#6FAE45","#FFC101","#EF7E33"]
txt = ['(a) 2001-2008','(b) 2008-2016','(c) 2016-2022','(d) 2001-2022']
cmap = matplotlib.colors.ListedColormap(bar_color).reversed()
for i, file in enumerate(file_paths):
    with rasterio.open(file) as src:
        profile = src.profile
        dst_crs = 'EPSG:4326'
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height,
            'nodata': src.nodata
        })
        # Reproject the raster data to WGS84
        memfile = rasterio.io.MemoryFile()
        with memfile.open(**kwargs) as dst:
            reproject(
                source=rasterio.band(src, 1),
                destination=rasterio.band(dst, 1),
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest)
            data = src.read(1)
            # 绘制栅格
            show((dst, 1), ax=axs[i], cmap=cmap, vmin=-2, vmax=2)
        # Close the in-memory file
        memfile.close()
    # 绘制矢量
    # gdf.plot(ax=axs[i], edgecolor='gray', facecolor='none', linewidth=1)
    # gdf1.plot(ax=axs[i], edgecolor='black', facecolor='none', linewidth=1)
    # axs[i].axis('off')
    
    def degree_formatter(x, pos):
        return f'{x:.2f}°'

    axs[i].xaxis.set_major_formatter(FuncFormatter(degree_formatter))
    axs[i].yaxis.set_major_formatter(FuncFormatter(degree_formatter))
    
    # 计算类别
    a = np.sum(data == 2)
    b = np.sum(data == 1)
    c = np.sum(data == 0)
    d = np.sum(data == -1)
    e = np.sum(data == -2)
    list1 = [a,b,c,d,e]
    list2.append(list1)


labels = [4,3,2,1]
# labels = [1,2,3,4]
bar_label = ["显著增加",'不显著增加','稳定不变','显著减少','不显著减少']
width = .3
df = pd.DataFrame(list2,columns=bar_label)
# 计算每组柱子的总和
sums = df.sum(axis=1)
# 将left_y元素都初始化为0
left_y = np.zeros(len(labels))
# 循环读取数据并进行可视化绘制
for j, color, label in zip(df, bar_color, bar_label):
    data = df[j]
    y = data/sums
    axs[4].barh(labels, y, color=color, label=label, left=left_y, ec='k')
    left_y = y + left_y

# 设置轴
axs[4].tick_params(which='major',direction='in',length=3,width=1.,bottom=False)
for spine in ["top","bottom","right"]:
    axs[4].spines[spine].set_visible(False)
axs[4].spines['left'].set_linewidth(2)

# 设置刻度label
axs[4].set_yticks([1, 2, 3, 4])
# 为这些刻度添加自定义标签
axs[4].set_yticklabels(["d","c","b","a"])

# 设置百分比形式
axs[4].xaxis.set_major_formatter(PercentFormatter(xmax=1))
axs[4].legend(ncol=5,frameon=False,loc='lower center',
          bbox_to_anchor=(0.5, -0.2))
# 添加label
for c in axs[4].containers:
    axs[4].bar_label(c, label_type='center',size=13,
                 labels=[str(round(i*100,1)) for i in c.datavalues],
                 color="w",fontweight="bold")
    
plt.tight_layout()
# plt.savefig(r'C:\Users\A1827\Desktop\生态脆弱性\MK中值\mk趋势图.png', dpi=300)
plt.show()