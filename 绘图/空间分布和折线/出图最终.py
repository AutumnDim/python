# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 20:42:14 2025

@author: hqm
"""
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import rasterio
import geopandas as gpd
import matplotlib.ticker as ticker
from matplotlib.patches import FancyArrowPatch
from matplotlib import cm
from matplotlib.colors import Normalize
from matplotlib.collections import LineCollection  # 导入LineCollection，用于绘制线段
from matplotlib import colorbar
import seaborn as sns
from matplotlib import ticker, font_manager, rcParams
from matplotlib.ticker import MultipleLocator
from matplotlib.colors import ListedColormap
from matplotlib.ticker import MaxNLocator, MultipleLocator
# 设置字体配置
config = {
    "font.family": "Times New Roman",  # 使用衬线字体
    "font.size": 15,  # 字体大小
    "font.serif": ["Times New Roman"],  # Times New Roman 用于英文和数字
    "mathtext.fontset": "stix",  # 数学字体设置为 stix
    "axes.unicode_minus": False  # 解决负号显示问题
}
rcParams.update(config)

# 定义颜色映射函数
def color_map(data, cmap):
    """将数值映射为颜色"""
    dmin, dmax = np.nanmin(data), np.nanmax(data)  # 获取数据的最小值和最大值
    cmo = plt.cm.get_cmap(cmap)  # 获取指定的颜色映射（colormap）
    cs, k = list(), 256/cmo.N  # 创建一个空列表，用于存储颜色

    for i in range(cmo.N):
        c = cmo(i)  # 获取每个颜色值
        for j in range(int(i*k), int((i+1)*k)):  # 将每个颜色细分为更小的步骤
            cs.append(c)  # 添加颜色到列表
    cs = np.array(cs)
    data = np.uint8(255*(data-dmin)/(dmax-dmin))  # 将数据标准化为0-255范围
    
    return cs[data]  # 返回标准化后的颜色数组


raster_path = r"F:\work\出图\K500.tif"  
with rasterio.open(raster_path) as src:
    data = src.read(1).astype('float') 
    nodata = src.nodata  
    data[data == nodata] = np.nan  
    left, bottom, right, top = src.bounds  # 获取栅格的边界（左、下、右、上）
    extent = [left, right, bottom, top]  # 设置栅格的显示范围


shp_path = r'F:\学长数据\地图数据\中国矢量及边界\全国矢量数据\province.shp'  
sea_path = r"F:\work\出图\沿海.shp"  
gdf = gpd.read_file(shp_path)  
sea_gdf = gpd.read_file(sea_path) 


lat_values = np.linspace(bottom, top, data.shape[0])


ones_count_per_row = []
for row in range(data.shape[0]):
    row_data = data[row, :] 
    ones_count = np.sum(row_data == 1)
    ones_count_per_row.append(ones_count)
ones_count_per_row = np.array(ones_count_per_row).astype('float64')  


fig = plt.figure(figsize=(8, 6))

# 创建左侧的地图（ax1）
ax1 = fig.add_subplot(121, projection=ccrs.PlateCarree())
ax1.set_extent([105, 127, 15, 45], crs=ccrs.PlateCarree())  

deep_blue_cmap = ListedColormap(['#0000FF', '#0000FF'])
img = ax1.imshow(
    data,
    extent=extent,
    cmap=deep_blue_cmap,  # 使用蓝色渐变色显示栅格数据
    transform=ccrs.PlateCarree(),
    origin='upper',
    zorder=500,
    vmax=0.001  
)

# 绘制中国省界和海岸线
gdf.plot(ax=ax1, edgecolor='gray', facecolor='gray', linewidth=0.5, zorder=2, alpha=0.15, transform=ccrs.PlateCarree())
sea_gdf.plot(ax=ax1, edgecolor='gray', facecolor='gray', linewidth=0.1, zorder=3, alpha=0.2, transform=ccrs.PlateCarree())

# 绘制海岸线
ax1.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.8, edgecolor='gray', zorder=2)
mask = np.where(~np.isnan(data), 1, 0)

# 绘制自定义网格线
gl = ax1.gridlines(
    crs=ccrs.PlateCarree(),
    draw_labels=True,
    linewidth=0.8,
    color='gray',
    alpha=0.5,
    linestyle='--',
    zorder=1
)
gl.top_labels = gl.right_labels = False  # 去掉上方和右侧的标签
gl.xformatter = LONGITUDE_FORMATTER  # 经度格式化
gl.yformatter = LATITUDE_FORMATTER  # 纬度格式化
gl.xlocator = ticker.MultipleLocator(10)  # 经度显示整十数
gl.ylocator = ticker.MultipleLocator(10)  # 纬度显示整十数

# 添加颜色条
cbar = plt.colorbar(img, ax=ax1, orientation='horizontal', shrink=0.001, pad=0.05)
ax1.spines['left'].set_position(('outward', 150))  # 左框向外延伸
ax1.spines['bottom'].set_position(('outward', 10))  # 下框向外延伸
ax1.tick_params(axis='x', which='both', direction='out', length=8, width=1, colors='black')  # 设置X轴刻度线
ax1.tick_params(axis='y', which='both', direction='out', length=8, width=1, colors='black')  # 设置Y轴刻度线
cbar.set_ticks([])  # 去除颜色条的刻度
ax1.tick_params(direction='out')  # 设置刻度线方向

# 添加文本标签
fig.text(0.04, 0.5, 'Latitude (deg)', ha='center', fontsize=15, color='black', rotation=90)  # 纬度标签
fig.text(0.28, 0.19, 'Longitude (deg)', ha='center', fontsize=15, color='black')  # 经度标签
fig.text(0.51, 0.19, 'Pixels', ha='center', fontsize=15, color='black')  # 栅格数据标签

# 创建副图（ax2）
ax2 = fig.add_axes([0.45, 0.263, 0.145, 0.61])  # 设置副图的位置

# 计算
def average_every_five_rows(values, group_size=1):
    n_groups = len(values) // group_size
    reshaped_values = values[:n_groups * group_size].reshape(-1, group_size)
    return reshaped_values.sum(axis=1)

# 计算并绘制副图
x = lat_values
y = ones_count_per_row 

x = average_every_five_rows(x)*100
y = average_every_five_rows(y)*100

ps = np.stack((y,x), axis=1)
segments = np.stack((ps[:-1], ps[1:]), axis=1)

def average_every_five_rows(data):
    reshaped_data = data[:(len(data) // 5) * 5].reshape(-1, 5, data.shape[1])
    return reshaped_data.mean(axis=1)

average_values = average_every_five_rows(segments)
# 使用颜色映射绘制线段
#cmap = ListedColormap(['#b1d1fc','#a2cffe','#9ecae1', '#75bbfd','#0ba8ee','#0384dd','#0366c2','#193a6a'])

cmap = 'brg'  # 使用Blues颜色映射
colors = color_map(np.cos(x)[:-1], cmap)  # 基于纬度计算颜色
colors = color_map(y[:-1], cmap)  # 基于像素数计算颜色

line_segments = LineCollection(segments, colors=colors, linewidths=0.5, linestyles='solid', cmap=cmap)  # 创建线段集合

# 绘制副图
ax2.set_ylim(np.min(x)-0.1, np.max(x)+0.01)  # 设置X轴范围
ax2.set_xlim(np.min(y)-0.1, np.max(y)+0.01)  # 设置Y轴范围
ax2.yaxis.set_major_locator(MultipleLocator(1))
ax2.add_collection(line_segments)  # 添加线段集合
#cb = fig.colorbar(line_segments, cmap='Blues', ax=ax2)  # 添加颜色条
#ax2.plot(y, x, color='#778899', linewidth=0.5, linestyle='-', zorder=0)  # 黑色线条，确保覆盖线段图

ax2.grid(False)  # 关闭副图网格线

# 去除副图的上框和右框
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_visible(False)

# 设置左框和下框位置，并添加箭头
ax2.spines['bottom'].set_position(('outward', 1))  # 下框向外延伸
ax2.spines['left'].set_position(('outward', 1))  # 左框向外延伸
ax2.spines['bottom'].set_position(('outward', 0.1))  # 刻度上移

# 添加箭头
arrowprops = dict(facecolor='gray', edgecolor='gray', width=0.01, headwidth=5, headlength=8)
ax2.annotate('', xy=(1, 0), xytext=(0, 0), xycoords='axes fraction', textcoords='axes fraction', arrowprops=arrowprops, zorder=10)
ax2.annotate('', xy=(0, 1), xytext=(0, 0), xycoords='axes fraction', textcoords='axes fraction', arrowprops=arrowprops, zorder=10)

# 设置X轴标签的位置
ax2.xaxis.set_label_coords(0.5, -0.08)
ax2.yaxis.set_visible(False)  # 隐藏Y轴
# 添加颜色条（图例）
fig.subplots_adjust(right=0.8)  # 调整布局，留出空间给颜色条
cbar_ax = fig.add_axes([0.2, 0.135, 0.32, 0.03])  # 设置颜色条的位置
norm = Normalize(vmin=np.min(y), vmax=np.max(y))  # 设置颜色条的数值范围
sm = cm.ScalarMappable(cmap=cmap, norm=norm)  # 创建颜色映射对象
sm.set_array([])  # 设置空数组，表示不使用数据
fig.colorbar(sm, cax=cbar_ax,orientation='horizontal')
#cbar.locator = MaxNLocator(integer=True, prune='both', nbins=2)
#cbar.set_ticks(np.arange(np.min(y), np.max(y)+1, 100))
plt.show()  # 显示图形