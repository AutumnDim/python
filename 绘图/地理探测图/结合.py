# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 08:53:23 2024

@author: hqm
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.patches as patches
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import ticker, font_manager, rcParams
# 设置绘图主题
plt.style.use("ggplot")
sns.set_theme(style="white", palette=None)

font_path = r"C:/WINDOWS/Fonts/SIMSUN.TTC"  # 替换为你的中文字体路径
font_prop = font_manager.FontProperties(fname=font_path)
config = {
    "font.family": "Times New Roman",  # 使用衬线字体
    "font.size": 15,  # 字体大小
    "font.serif": ["Times New Roman"],  # Times New Roman 用于英文和数字
    "mathtext.fontset": "stix",  # 数学字体设置为 stix
    "axes.unicode_minus": False  # 解决负号显示问题
}

# 更新全局配置
rcParams.update(config)
# font_path = r"C:/WINDOWS/Fonts/SIMSUN.TTC"  
# font_prop = font_manager.FontProperties(fname=font_path)

# # 设置全局字体
# config = {
#     "font.family": font_prop.get_name(),
#     "font.size": 15,
#     "mathtext.fontset": 'stix',
#     'axes.unicode_minus': False
# }
# rcParams.update(config)
# # 设置中文字体
# plt.rcParams["font.family"] = ['serif']
# plt.rcParams["font.sans-serif"] = ["SimHei"]
# plt.rcParams["font.family"] = "sans-serif"
# plt.rcParams['axes.unicode_minus'] = False  # 解决负号无法显示的问题

# 读取和处理第一个CSV文件
df_heatmap = pd.read_csv(r"F:\生态脆弱性\数据\地理探测器自变量\qv.csv", encoding='gbk').round(2)
df_heatmap.set_index(df_heatmap.columns[0], inplace=True)
df_heatmap = df_heatmap.apply(pd.to_numeric, errors='coerce')

# 读取和处理第二个CSV文件（交互效果）
df_interactions = pd.read_csv(r"F:\生态脆弱性\数据\地理探测器自变量\effectk.csv", encoding='gbk')
df_interactions = df_interactions.replace({'Enhance, nonlinear': 1, 'Enhance, bi-': 2})
df_interactions.set_index(df_interactions.columns[0], inplace=True)



# 条形图数据
df = pd.read_csv(r"F:\生态脆弱性\数据\地理探测器自变量\Q值.csv",encoding='gbk')
df = df.drop(index=1)
df = df.drop(columns='type')
df.columns = df.iloc[1]
df = df.drop(index=2)
df = df.round(2)
df.iloc[0] = df.iloc[0].astype(float)
df_sorted = df.iloc[0].sort_values(ascending=True)
df = pd.DataFrame(df_sorted)
# 数据
factors = df.index.tolist()
values = df.iloc[:, 0].tolist()

# 设置颜色
#colors = sns.color_palette("Spectral", len(factors))
# 自定义颜色映射
colors = ["#FFEFD5", "#E6E6FA", "#ffd1df", '#F5F5F5']
cmap = ListedColormap(colors)

# 创建图表
plt.figure(figsize=(20, 8))

# 绘制左侧的条形图
plt.subplot(1, 2, 1)
bars = plt.barh(df_sorted.index, df_sorted.values, color=sns.color_palette("coolwarm", len(df_sorted)))
for bar, value in zip(bars, df_sorted.values):
    plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{value:.2f}', va='center', fontsize=15)
plt.yticks(fontsize=15)
plt.xticks(fontsize=15)
#plt.legend(['Q值'], loc='lower right', fontsize=15, frameon=True, facecolor='white', edgecolor='black')






plt.subplots_adjust(wspace=0.5) 








# 绘制右侧的热力图
plt.subplot(1, 2, 2)

# 第一个热力图层
ax = sns.heatmap(df_heatmap, annot=False, cmap="coolwarm", cbar=True, linewidths=1,
                 linecolor='black',square=True,xticklabels=2, yticklabels=2) 
ax.figure.axes[-1].tick_params(labelsize=30)
cbar = ax.collections[0].colorbar
cbar.set_ticks([0.2, 0.4, 0.6])
cbar.set_ticklabels([ 0.2, 0.4, 0.6])
ax.figure.axes[-1].tick_params(labelsize=15)
cbar.ax.set_aspect(19)  
# 添加矩形和文本
for y in range(df_heatmap.shape[1]):
    for x in range(df_heatmap.shape[0]):
        value = df_heatmap.iloc[x, y]
        if pd.isna(value):
            continue
        rect = patches.Rectangle((x, y), 1, 1, fill=False, edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)
        plt.text(x + 0.5, y + 0.5, f"{value:.2f}", ha='center', va='center', fontsize=15, color="black")

# 第二个热力图层（交互效果）
ax0 = sns.heatmap(df_interactions, annot=False, cmap=cmap, cbar=False, linewidths=1, linecolor='black')
for o in range(df_interactions.shape[0]):
    for k in range(df_interactions.shape[1]):
        value2 = df_interactions.iloc[o, k]
        if pd.isna(value2):
            continue
        color1 = cmap(value2 / 5)
        rectangle = patches.Rectangle((o, k), 1, 1, facecolor=color1, edgecolor='black')
        ax0.add_patch(rectangle)

# 第三个热力图层，使用纯白色背景
ax1 = sns.heatmap(df_heatmap, annot=False, cmap=sns.color_palette(['white']), cbar=False, linewidths=1, linecolor='black')
norm = plt.Normalize(df_heatmap.min().min(), df_heatmap.max().max())

# 添加圆形和文本
for y in range(df_heatmap.shape[1]):
    for x in range(df_heatmap.shape[0]):
        value1 = df_heatmap.iloc[y, x]
        if pd.isna(value1):
            continue
        rect = patches.Rectangle((x, y), 1, 1, fill=False, edgecolor='black', linewidth=0.8)
        ax1.add_patch(rect)
        color = plt.cm.coolwarm(norm(value1))
        radius = norm(value1) * 0.4
        circle = patches.Circle((x + 0.5, y + 0.5), radius, facecolor=color, edgecolor='black')
        ax1.add_patch(circle)



# 添加变量名称

variables =['X5','X14','X8','X10','X3','X12', 'X15', 'X13', 'X2', 'X9', 'X11','X7','X6','X1','X4']

def split_text(var, n=5):
    return '\n'.join([var[i:i+n] for i in range(0, len(var), n)])

for i, var in enumerate(variables):
    text = split_text(var)
    plt.text(i+0.5, i+0.52, text, ha='center', va='center', fontsize=15)
# 隐藏坐标轴刻度
ax1.set_xlabel('')
ax1.set_ylabel('')
ax1.set_xticks([])
ax1.set_yticks([])
ax.set_xticks([])
ax.set_yticks([])
# # 自定义图例
fig = plt.gcf()
fig.subplots_adjust(bottom=0.3)  # 调整图表底部的间距
legend_ax = plt.gcf().add_axes([0.55, 0.05, 0.8, 0.05])
legend_ax.axis('off')
legend_labels = ['NonlinearEnhancement', 'bi-Enhance']
legend_patches = [patches.Patch(color=colors[i], label=legend_labels[i]) for i in range(len(legend_labels))]
legend_ax.legend(handles=legend_patches, loc='center', bbox_to_anchor=(0.23, -0.1), ncol=5, frameon=False,fontsize=15)
plt.text(0.18, -0.65, '双因子增强', fontsize=15, fontproperties=font_prop,
         ha='center', va='center', transform=plt.gca().transAxes)
plt.text(0.348, -0.65, '非线性增强', fontsize=15, fontproperties=font_prop,
         ha='center', va='center',  transform=plt.gca().transAxes)

#plt.savefig(r"F:\生态脆弱性\出图\地理探测器\结合图.png", dpi=300)
plt.tight_layout()
plt.show()

