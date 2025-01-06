# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 20:24:58 2024

@author: hqm
"""
import rasterio
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import matplotlib.pyplot as plt
import matplotlib.colors as cor
import numpy as np
import seaborn as sns
from matplotlib.patches import Patch
import matplotlib.patches as mpatches
import geopandas as gpd
from shapely import affinity
from matplotlib import font_manager, rcParams
from mpl_toolkits.mplot3d import Axes3D  # 用于绘制3D图形
import shapely
import frykit.plot as fplt
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as pyplot 
# 设置绘图主题
sns.set_theme(style="white", palette=None)
font_path = r"C:/WINDOWS/Fonts/SIMSUN.TTC"  # 替换为你的中文字体路径
font_prop = FontProperties(fname=font_path)

# config = {
#     "font.family": "Times New Roman",  # 衬线字体族
#     "font.size": 20,  # 相当于小四大小
#     "font.serif": ["Times New Roman"],  # 设置serif字体族的字体列表，按优先级排序
#     "mathtext.fontset": 'stix',  # matplotlib渲染数学字体时使用的字体，和Times New Roman差别不大
#     'axes.unicode_minus': False  # 处理负号，即-号
# }

path = r"F:\生态脆弱性\数据\MK中值 k\MK中值\趋势\趋势分析k.tif"
shp_path = r"F:\生态脆弱性\数据\MK中值 k\MK中值\pr\区域面积\区域面积pr.shp"
shp = r"F:\生态脆弱性\数据\MK中值 k\MK中值\pr\区域面积\区域面积融合.shp"
ColorTable = {
    2: (255,255,0, 255),    #  显著增加
    1: (119, 0, 1, 255),    #  不显著增加
    0: (162, 207, 254, 255),#  稳定不变
   -1: (10, 255, 2, 255),   #  显著减少
   -2: (219, 112, 147, 255) #  不显著减少
}

# 设置中文字体
plt.rcParams["font.sans-serif"] = ["Times New Roman"]
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams['axes.unicode_minus'] = False

# 打开数据集并读取数据
with rasterio.open(path) as dataset:
    band = dataset.read(1)
    nodata = dataset.nodata
    band = band.astype(float)
    
    band[band == nodata] = np.nan
    profile = dataset.profile
    transform = dataset.transform

# 初始化色彩映射表
CMapV = [(r/255, g/255, b/255, a/255) for r, g, b, a in ColorTable.values()]
CMap = cor.ListedColormap(CMapV)
ColorName = ['显著增加', '不显著增加', '稳定不变', '显著减少', '不显著减少']
Columns = profile['width']
Rows = profile['height']
GEOT = transform
ExtentData = [GEOT[2], GEOT[2] + GEOT[0] * Columns, GEOT[5] + GEOT[4] * Rows, GEOT[5]]
# 检查 ExtentData 是否有效
if any(np.isnan(ExtentData)) or any(np.isinf(ExtentData)):
    raise ValueError("ExtentData contains NaN or Inf values.")
# 缩放参数设置
scale_factor = 1  # 地图和shapefile放大比例

ExtentData_scaled = [
    ExtentData[0] - (ExtentData[1] - ExtentData[0]) * (scale_factor - 1) / 2,
    ExtentData[1] + (ExtentData[1] - ExtentData[0]) * (scale_factor - 1) / 2,
    ExtentData[2] - (ExtentData[3] - ExtentData[2]) * (scale_factor - 1) / 2,
    ExtentData[3] + (ExtentData[3] - (ExtentData[2])) * (scale_factor - 1) / 2
]

# 读取Shp
def add_shp(shp_file, scale_factor=1, shift_x=-0, shift_y=0):    #后两个为shp调整x y位置
    gdf = gpd.read_file(shp_file)

    # 计算整体几何的中心点
    total_bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    center_x = (total_bounds[0] + total_bounds[2]) / 2 
    center_y = (total_bounds[1] + total_bounds[3]) / 2 
    
    # 使用整体中心点进行缩放
    scaled_geometries = gdf.geometry.apply(
        lambda geom: shapely.affinity.scale(geom, xfact=scale_factor, yfact=scale_factor, origin=(center_x, center_y)))
    gdf['geometry'] = scaled_geometries
    
    # 使用 Shapely 的 translate 函数来平移几何
    translated_geometries = gdf.geometry.apply(
        lambda geom: shapely.affinity.translate(geom, xoff=shift_x, yoff=shift_y))
    gdf['geometry'] = translated_geometries
    return gdf

gdf = add_shp(shp_path)    
gdf1 = add_shp(shp)
# 设置线条粗细
line_width =0.2  # 设置线条粗细

DataCRS = ccrs.PlateCarree()
# 构造特定的阴影图层的 URL
class Hillshade(cimgt.GoogleWTS):
    def _image_url(self, tile):
        x, y, z = tile
        return f"https://server.arcgisonline.com/ArcGIS/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}"

# 创建画布
fig = plt.figure(figsize=(4, 4), dpi=300)

# 左边子图：绘制栅格图和shapefile
ax1 = fig.add_subplot(111, projection=ccrs.AlbersEqualArea(central_longitude=90, standard_parallels=(25.0, 25.0)))
ax1.set_extent(ExtentData_scaled, crs=DataCRS)

hillshade_img = Hillshade()
ax1.add_image(hillshade_img, 8)

# 绘制栅格数据
im = ax1.imshow(band, transform=DataCRS, cmap=CMap, extent=ExtentData_scaled, zorder=2, interpolation='none',
               vmin=-2, vmax=2)

# 绘制缩放后的Shapefile图层，设置线条粗细
gdf.plot(ax=ax1, edgecolor='gray', linewidth=line_width, facecolor='none', transform=ccrs.PlateCarree(), zorder=3)
gdf1.plot(ax=ax1, edgecolor='black', linewidth=line_width, facecolor='none', transform=ccrs.PlateCarree(), zorder=3)

# 绘制格网线
gl = ax1.gridlines(draw_labels=True, dms=False, x_inline=False, y_inline=False, linestyle=(0, (10, 10)),
                  linewidth=0.2, color='gray', rotate_labels=False, xlabel_style={'fontsize': 7.5}, ylabel_style={'fontsize': 7.5})
# 关闭顶部和右边的标签
# gl.top_labels = False
# gl.right_labels = False
# # 关闭上方和右侧的刻度线
ax1.tick_params(top=True, right=False)

# # 添加指北针
# def add_north(ax, labelsize=10, loc_x=0.07, loc_y=0.98, width=0.03, height=0.08, pad=0.14):
#     minx, maxx = ax.get_xlim()
#     miny, maxy = ax.get_ylim()
#     ylen = maxy - miny
#     xlen = maxx - minx
#     left = [minx + xlen*(loc_x - width*.5), miny + ylen*(loc_y - pad)]
#     right = [minx + xlen*(loc_x + width*.5), miny + ylen*(loc_y - pad)]
#     top = [minx + xlen*loc_x, miny + ylen*(loc_y - pad + height)]
#     center = [minx + xlen*loc_x, left[1] + (top[1] - left[1])*.4]
#     triangle = mpatches.Polygon([left, top, right, center], color='k')
#     ax.text(s='N', x=minx + xlen*loc_x, y=miny + ylen*(loc_y - pad + height), fontsize=labelsize,
#             horizontalalignment='center', verticalalignment='bottom')
#     ax.add_patch(triangle)
# add_north(ax1)
#fplt.add_compass(ax1, 0.1, 0.81, size=20)
# 添加比例尺
def draw_the_scale(ax, text, length=0.5, height=0.01, lw=0.00):
    # 设置比例尺的黑白部分比例，只有两个部分，黑色和白色各占一半
    black_white_ratio = [0.5, 0.5]  # 黑白各一半
    y = 0.02  # 比例尺的y位置
    x = 0.05  # 比例尺的x位置

    # 绘制整体矩形框
    ax.add_patch(plt.Rectangle((x, y), length, height, transform=ax.transAxes, color='black'))

    # 绘制比例尺的黑白条段
    position = x
    for i in range(2):  # 只有两个部分
        # 在矩形框内绘制黑白条段
        color = 'black' if i == 0 else 'white'  # 第一个部分为黑色，第二个部分为白色
        ax.add_patch(plt.Rectangle((position, y), black_white_ratio[i] * length, 0.015, transform=ax.transAxes, color=color, lw=lw))
        position += black_white_ratio[i] * length

    # 添加比例尺上的文字
    ax.text(x , y + 0.024, '0', transform=ax.transAxes, fontsize=7.5, ha='center',family="Times New Roman")
    ax.text(x + length , y + 0.024, text, transform=ax.transAxes, fontsize=7.5, ha='center',family="Times New Roman")
    ax.text(x + 0.5 * length + 0.0, y + 0.024, '50', transform=ax.transAxes, fontsize=7.5, ha='center',family="Times New Roman")
    ax.text(x+0.29, y-0.002 , 'KM', transform=ax.transAxes, fontsize=7.5, ha='center',family="Times New Roman")
draw_the_scale(ax1, '100', length=0.24, height=0.015) 
# 添加图例
legend_elements = [Patch(facecolor=CMapV[i], edgecolor='k', label=ColorName[i]) for i in range(len(ColorName))]
font_prop = FontProperties(fname=font_path,size=6)
legend = ax1.legend(
    handles=legend_elements,
    loc='lower left',                                   
    #bbox_to_anchor=(0.01, 0.78, 1.4, 1),
    bbox_to_anchor=(0.74, -0.0009, 1.4, 1),
    ncol=1,                         
    frameon=True,                   
    labelspacing=0.34,               # 条目间距
    prop=font_prop,
   handlelength=2                
)
title_font = FontProperties(size=7, weight='bold', fname=font_path)
legend.set_title('分类', prop=title_font )
#frame = legend.get_frame()
#frame.set_linewidth(0.1)  # 设置边框线宽度
#frame.set_edgecolor("black")  # 设置边框颜色
#frame.set_alpha(1)  # 设置图例背景透明度

# 计算每个类别的百分比
with rasterio.open(path) as src:
    profile = src.profile  
    data = src.read(1)
    nodata = src.nodata
    a = np.sum(data == 2)
    b = np.sum(data == 1)
    c = np.sum(data == 0)
    d = np.sum(data == -1)
    e = np.sum(data == -2)

total = a + b + c + d + e
sizes = [100 * a / total, 100 * b / total, 100 * c / total, 100 * d / total, 100 * e / total]
colors = ['#FFFF00', '#770001', '#a2cffe', '#0aff02', '#DB7093']

# 定义缩放因子，单独缩小 'c' 的高度
scale_factor = 0.0001
c_scale_factor = 0.00005  # 'c' 部分的缩放比例

# 计算高度，单独调整 'c' 对应的高度
heights = [size * scale_factor if i != 2 else size * c_scale_factor for i, size in enumerate(sizes)]

# 根据数值大小对扇形排序，以便先绘制较大的，最后绘制较小的
sorted_indices = np.argsort(sizes)[::-1]  # 降序排列索引
# 右图
#ax2 = fig.add_axes([0.587, 0.113, 0.2, 0.2], projection='3d')
# 主图宽高比
main_width = 8
main_height = 5

# 子图比例（相对于主图）
sub_scale = 0.221

# 计算子图的宽高
sub_width = main_width * sub_scale 
sub_height = main_height * sub_scale

# 计算相对宽高
relative_width = sub_width / main_width +0.02
relative_height = sub_height / main_height 

# 设置子图的位置和大小
ax2 = fig.add_axes([0.12, 0.656, relative_width, relative_height], projection='3d')

angles = np.cumsum([0] + [sizes[i] for i in sorted_indices]) * 360 / sum(sizes)

# 绘制每个扇形
for i in range(len(sizes)):
    idx = sorted_indices[i]
    theta1, theta2 = np.radians(angles[i]), np.radians(angles[i + 1])
    r = np.linspace(0, 1, 30)
    p = np.linspace(theta1, theta2, 30)
    R, P = np.meshgrid(r, p)
    X, Y = R * np.cos(P), R * np.sin(P)

    # 堆叠形成完整的扇形体
    for k in range(30):
        z_low = heights[idx] * (k / 30)
        z_high = heights[idx] * ((k + 1) / 30)
        Z = np.full_like(X, z_high)

        # 绘制饼图扇形部分，并在外围添加白色边界线
        edge_color = 'white' if k == 29 else 'none'
        ax2.plot_surface(X, Y, Z, color=colors[idx], edgecolor=edge_color, linewidth=0.03, alpha=0.9)

    # 添加标签
    mid_angle = (theta1 + theta2) / 2
    if idx == 2:
        label_x = np.cos(mid_angle) * 2.8  # 偏移量
        label_y = np.sin(mid_angle) * 1.9
    
    if idx == 0:
        label_x = np.cos(mid_angle) * 1.5  #非显著
        label_y = np.sin(mid_angle) * 1.5 
       
    else:
        label_x = np.cos(mid_angle) * 1.68  
        label_y = np.sin(mid_angle) * 1.9  

    ax2.text(label_x, label_y, heights[idx] / 2,
             f'{sizes[idx]:.2f}%', color='black', ha='center', fontsize=5)

#饼状图的高度设置
u = np.linspace(0, 1 * np.pi, 100)
x_border = np.cos(u)
y_border = np.sin(u)
z_border = np.full_like(x_border, 0.01)
ax2.plot(x_border, y_border, z_border, color='white', linewidth=4)

# 设置视角
ax2.view_init(40, -40)
ax2.set_axis_off()
plt.savefig(r"F:\生态脆弱性\出图\MK中值\中值k.png", dpi=600)
# 显示图表
plt.show()
