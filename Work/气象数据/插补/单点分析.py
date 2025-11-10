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
from sklearn.metrics import r2_score
from matplotlib.ticker import MultipleLocator
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sympy.abc import alpha

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def calculate_stats(y_true, y_pred):
    """
    计算结果评估指数
    """
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    correlation = y_true.corr(y_pred)
    r2 = r2_score(y_true, y_pred)

    return rmse, mae, correlation, r2
def read_data(path, station, year,name=None):
    df = pd.read_csv(path, index_col=0)
    df.index = pd.to_datetime(df.index)
    df.columns = [i[-5:] for i in df.columns]

    prcp = df[station.values()]
    prcp = prcp.resample('ME').sum()
    prcp.columns = [name]

    groups = prcp.groupby(prcp.index.year)
    df_prcp1 = groups.get_group(year)

    return df_prcp1

def tendency():
    """
    单点趋势图
    """

    path_true = r'C:\降水归档\降水数据插值(国内)_气象局\4插值效果分析\单点分析'          # 数据产品的路径
    path_pre = r"C:\降水归档\降水数据插值(国内)_气象局\3数据插值\7空间一致性插值\prcp_all1.csv"   # 插值结果的路径



    stations = [{'改则':'55248'},{'南康':'57792'},{'汇川':'57503'},{'霍林郭勒':'50924'}]    # 选取的站点
    vars = ['CPC','ERA5','MSWEP','GHCND']                                                # 对比的降水产品
    cols1 = ['#CC88B0','#E2C8D8','#DBE0ED','#87B5B2','#F4CEB4']
    cols2 = ['#EEC79F','#F1DFA4','#9DD0C7','#A6CDE4','#E2C8D8']     # 颜色
    colors = {2009: cols1, 2012: cols2}
    year = [2009,2012]          # 枯水年和丰水年

    for color,y in zip(year,colors.keys()):
        color1 = colors[color]

        figs, axes = plt.subplots(2, 2, figsize=(10, 8))
        axes = axes.flatten()
        for a,station in enumerate(stations):

            df_pre= read_data(path_pre,station, y,'INITIAL')
            for var in vars:
                path_true1 = gb.glob(os.path.join(path_true,fr'{var}\*_D.csv'))[0]
                df_true1= read_data(path_true1,station, y, var)

                df_pre = pd.concat([df_pre,df_true1],axis=1)
                print(var)
            df_pre.index = [i+1 for i in range(len(df_pre))]         # 获取插补数据
    
            # 趋势图
            fig, ax = plt.subplots(figsize=(10, 2))
            for i, col in enumerate(df_pre.columns):
                ax.plot(df_pre.index, df_pre[col], color=color1[i], linestyle='-', linewidth=1.5, markersize=1, label=col)

            plt.xlabel('月份',fontsize=10,labelpad=2)
            plt.ylabel('降水量(mm)',fontsize=10,labelpad=2)
            plt.text(0.98, 0.93, f'{list(station.keys())[0]}', transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
                     horizontalalignment='right', color='black')

            # 调整标签和轴的间距以及标签间的间距
            plt.xticks(ticks=range(1, 13), labels=[str(i) for i in range(1, 13)])
            plt.xlim(0.8,12.2)

            # 网格线和布局
            plt.grid(True, which='major', axis='y', color='#D3D3D3', linestyle=':', linewidth=0.3, alpha=0.6, dashes=[6, 4])
            plt.grid(True, which='both', axis='x', color='#D3D3D3', linestyle=':', linewidth=0.3, alpha=0.6, dashes=[6, 4])

            # 图例
            plt.legend(
                loc='upper left',  # 图例放在左上角
                fontsize=9,
                frameon=False,
                ncol=3,  # 设置图例为两列
                bbox_to_anchor=(0, 1),  # 图例位置的锚点
                columnspacing=1.0,  # 列之间的间距
                handletextpad=0.5  # 图例中图形和文本之间的间距
            )

            for spine in ax.spines.values():
                spine.set_linewidth(0.3)

            plt.tight_layout()
            # plt.show(block=True)
            path_png = path_true + os.sep + '趋势图'
            if not os.path.exists(path_png):
                os.makedirs(path_png)
            else:
                pass
            plt.savefig(path_png + os.sep + f"{list(station.keys())[0]}_{y}趋势图.png", dpi=600, bbox_inches='tight')
    
            # 散点图
            ax1 = axes[a]
            for c, col in zip(color1,df_pre.columns[1:]):
                ax1.scatter(df_pre[df_pre.columns[0]], df_pre[col], alpha=0.9,
                            label=f'{col} ($R^2$={r2_score(df_pre[col], df_pre[df_pre.columns[0]]):.2f})',
                            color=c, marker='o')
    
            # 添加x=y线段
            min_val = min(df_pre[df_pre.columns[0]].min(), df_pre[df_pre.columns[1:]].min().min())
            max_val = max(df_pre[df_pre.columns[0]].max(), df_pre[df_pre.columns[1:]].max().max())
            ax1.plot([min_val, max_val], [min_val, max_val], color='black', linestyle='--', linewidth=1,alpha=0.6)
    
            ax1.set_title(f'{list(station.keys())[0]}')
            ax1.set_xlabel('插补降水(mm)')
            ax1.set_ylabel('实际降水(mm)')
            ax1.grid(True, which='major', axis='y', color='#D3D3D3', linestyle=':', linewidth=0.3, alpha=1, dashes=[6, 4])
            ax1.grid(True, which='both', axis='x', color='#D3D3D3', linestyle=':', linewidth=0.3, alpha=1, dashes=[6, 4])
            ax1.legend(fontsize=9)
            ax1.grid(True)
        plt.tight_layout()
        # plt.show(block=True)
        path_png1 = path_true + os.sep + '散点图'
        if not os.path.exists(path_png1):
            os.makedirs(path_png1)
        else:
            pass
        plt.savefig(path_png1 + os.sep + f"{y}散点图.png", dpi=600, bbox_inches='tight')
    print(y)
# tendency()
