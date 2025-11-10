import re
import os
import math
import datetime
import glob as gb
import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import font_manager
from matplotlib.ticker import MultipleLocator

font_path = 'C:/Windows/Fonts/simhei.ttf'  # 根据操作系统找到合适的字体路径
prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = prop.get_name()  # 使用找到的中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def tendency_chart_accuracy():
    """
    贝叶斯分类交叉验证准确率图
    """
    path = r"C:\降水归档\降水数据插值(国内)_气象局\3数据插值\1缺失值插值\accuracy_all.csv"
    df = pd.read_csv(path,index_col=0)
    df_mean = df.mean(axis=1)

    fig,ax = plt.subplots(figsize=(12,3),dpi=300)
    plt.plot(df_mean.index, df_mean, label='准确率', color='#FF2800', linestyle='-',
             linewidth=1, markersize=4)

    # 添加阴影区域
    plt.axvline(x=171, color='gray', linestyle='--', linewidth=0.4)
    plt.axvline(x=238, color='gray', linestyle='--', linewidth=0.4)
    plt.axvspan(171, 238, color='gray', alpha=0.1)  # 例：198到243之间的阴影区域
    ax.text(179, 0.85, 'x=171', color='gray', fontsize=10, ha='center', va='center')
    ax.text(230, 0.85, 'x=238', color='gray', fontsize=10, ha='center', va='center')

    plt.xlabel('天数',fontsize=8)
    plt.ylabel('准确率',fontsize=8)

    len=plt.legend(loc='upper left', fontsize=8,frameon=False)

    plt.ylim(0.75, 0.98)
    plt.xlim(0, 370)

    yticks = ax.get_yticks()[1:-1]
    plt.yticks(yticks, fontsize=8)
    x_ticks = range(20, 361, 30)
    x_labels = [str(i) for i in x_ticks]
    plt.xticks(ticks=x_ticks, labels=x_labels, fontsize=8)

    # 显示副刻度线
    ax.tick_params(axis="both", which="major", width=0.5, length=4)
    ax.tick_params(axis="y", which="minor", width=0.5, length=2)
    ax.yaxis.set_minor_locator(MultipleLocator(0.025))

    # 网格线和布局
    plt.grid(True, which='major', axis='y', color='#D3D3D3', linestyle=':', linewidth=0.4, alpha=0.6, dashes=[6, 4])
    plt.grid(True, which='both', axis='x', color='#D3D3D3', linestyle=':', linewidth=0.4, alpha=0.6, dashes=[6, 4])
    plt.tight_layout()

    for spine in ax.spines.values():
        spine.set_linewidth(0.5)

    # 显示图形
    # plt.show(block=True)
    plt.savefig(rf"C:\降水归档\降水数据插值(国内)_气象局\4插值效果分析\整体分析\贝叶斯分类准确度(缺失值).png", dpi=600, bbox_inches='tight')
    print('ok')
# tendency_chart_accuracy()

def Make_space_map():
    """
    制作评价指标的空间图
    """
    # 读取中国的GeoJSON边界数据
    china = gpd.read_file(r"C:\降水归档\降水数据插值(国内)_气象局\1数据缺失值概况\2024最新行政区划\sheng.shp")
    line = gpd.read_file(r"C:\降水归档\降水数据插值(国内)_气象局\1数据缺失值概况\2024最新行政区划\shiduanxian.shp")
    data = pd.read_csv(r"C:\降水归档\降水数据插值(国内)_气象局\3数据插值\1缺失值插值\r2_all(带经纬度版).csv")
    data1 = pd.read_csv(r"C:\降水归档\降水数据插值(国内)_气象局\3数据插值\1缺失值插值\r2_all(仅南沙群岛).csv")

    # 检查 CRD 是否一致，转换 CRS 如果不一致
    if china.crs != line.crs:
        line = line.to_crs(china.crs)
        print('CRS mismatch. CRS converted.')

    # name = ['均方根误差(RMSE)','均值绝对误差(MAE)','相关系数(r)','决定系数 ($R^2$)','GHCND缺失比例']
    # number = ['a', 'b', 'c', 'd','e']
    # 泛克里金交叉验证制图使用下面
    data = data.rename(columns={'0': '泛克里金插值交叉验证结果'})
    data1 = data1.rename(columns={'0': '泛克里金插值交叉验证结果'})
    name = ['R2']
    number = [' ']  #TODO

    for d,n,num in zip(data.columns[4:],name,number):

        ############## 创建主图 ###################
        fig, ax = plt.subplots(figsize=(10, 10), dpi=300)
        ax.set_facecolor('#F5F5F5')
        ax.text(0.05, 0.95, f'{num}', transform=ax.transAxes, fontsize=16, verticalalignment='top',
                horizontalalignment='left', weight='bold')

        # 绘制中国地图边界
        china.plot(ax=ax, color='#F8F8F8', edgecolor='black',linewidth=0.2)

        # 设置地图边界和标签
        ax.set_xlim(73, 135.5)  # 经纬度范围
        ax.set_ylim(18, 54)

        # 获取当前的刻度
        x_ticks = ax.get_xticks()[1:-1]
        y_ticks = np.arange(20,60,10)

        # 设置自定义标签
        x_labels = [f'{int(x)}°E' if x > 0 else f'{abs(int(x))}°W' for x in x_ticks]
        y_labels = [f'{int(y)}°N' if y > 0 else f'{abs(int(y))}°S' for y in y_ticks]

        # 设置新的刻度标签
        ax.set_xticks(x_ticks)   #重新设置坐标轴上刻度的位置
        ax.set_yticks(y_ticks)
        ax.set_xticklabels(x_labels)   # 将自定义的标签设计为实际的刻度标签
        ax.set_yticklabels(y_labels)

        # 设置字体大小
        ax.tick_params(axis='x', labelsize=9)
        ax.tick_params(axis='y', labelsize=9, labelrotation=90)

        # 设置总图的边框大小
        for spine in ax.spines.values():
            spine.set_linewidth(1)

        ############# 创建子图绘制南海区域 ##############
        ax_child = fig.add_axes([0.66, 0.255, 0.10, 0.2])
        ax_child.set_facecolor('#F5F5F5')

        # 绘制中国地图边界
        china.plot(ax=ax_child, color='#F8F8F8', edgecolor='black',linewidth=0.2)

        # 绘制十段线，使用更粗的边界
        line.plot(ax=ax_child, color='black', linewidth=0.5)

        # 设置子图的经纬度范围，确保它包含十段线
        ax_child.set_xlim(106.5, 125.5)
        ax_child.set_ylim(4, 26)

        ax_child.set_xticks([])  # 去掉x轴的刻度
        ax_child.set_yticks([])

        for spine in ax_child.spines.values():
            spine.set_linewidth(0.5)

        ############# 在图中添加数据 ##############
        # 主图
        # 使用散点图来表示热力点
        mmax = data[d].max()
        mmin = data[d].min()
        numbers = np.linspace(mmin, mmax, num=10, endpoint=True).round(1)
        norm = mcolors.BoundaryNorm(boundaries=numbers, ncolors=256)
        sc = ax.scatter(
            data['经度'], data['纬度'],
            c=data[d], cmap='RdYlBu', s=4, alpha=0.7,edgecolors='black', linewidths=0.15,norm=norm
        )

        # 添加颜色条
        cbar = plt.colorbar(sc, ax=ax, orientation='vertical',pad=0.02,extend='both',shrink=0.55,)
        cbar.set_label(n, fontsize=9)
        cbar.ax.tick_params(labelsize=9)  # 设置颜色条的刻度标签字体大小

        # 子图
        # 使用散点图来表示热力点
        sc_child = ax_child.scatter(
            data1['经度'], data1['纬度'],
            c=data1[d], cmap='RdYlBu', s=4, alpha=0.7, norm=norm,
            edgecolors='black', linewidths=0.15)

        # 显示图形
        # plt.show(block=True)
        # plt.savefig(rf"C:\降水归档\降水数据插值(国内)_气象局\4插值效果分析\整体分析\{d}(python[日]).png",
        # dpi=600,bbox_inches='tight')
        plt.savefig(rf"C:\降水归档\降水数据插值(国内)_气象局\4插值效果分析\整体分析\{d}.png", dpi=600,bbox_inches='tight')       # 交叉验证制图
        plt.clf()
        print(d)
# Make_space_map()

def tendency_chart_r2():
    """
    泛克里金插值交叉验证R2图
    """
    path = r"C:\降水归档\降水数据插值(国内)_气象局\3数据插值\1缺失值插值\r2_all.csv"
    df = pd.read_csv(path,index_col=0).T
    df_mean = df.mean(axis=1)
    overall_mean = df_mean.mean()

    fig,ax = plt.subplots(figsize=(12,4),dpi=300)
    plt.plot(df_mean.index, df_mean, label=f'$R^2$/平均$R^2$ = {overall_mean:.2f}',
             color='orangered', linestyle='-', linewidth=0.4, markersize=4)

    # ax.axhline(y=0, color='grey', linestyle='-', linewidth=0.8,alpha=0.4)

    plt.xlabel('台站编号',fontsize=8)
    plt.ylabel('决定系数 ($R^2$)',fontsize=8)

    plt.ylim(-0.9, 1.1)
    plt.xlim(-5,2465)

    plt.xticks(np.arange(0, len(df_mean)+1,100 ),rotation=45)

    plt.legend(loc='upper left', fontsize=8,frameon=False)

    # 网格线和布局
    plt.grid(True, which='major', axis='y', color='#D3D3D3', linestyle=':', linewidth=0.3, alpha=0.6, dashes=[6, 4])
    plt.grid(True, which='both', axis='x', color='#D3D3D3', linestyle=':', linewidth=0.3, alpha=0.6, dashes=[6, 4])
    plt.tight_layout()

    for spine in ax.spines.values():
        spine.set_linewidth(0.5)

    # 显示图形
    # plt.show(block=True)
    plt.savefig(rf"C:\降水归档\降水数据插值(国内)_气象局\4插值效果分析\整体分析\交叉验证结果.png", dpi=600, bbox_inches='tight')
    print('ok')
tendency_chart_r2()