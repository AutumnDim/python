# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 17:20:17 2024

@author: hqm
"""
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import linregress
from matplotlib import font_manager, rcParams
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
rcParams['axes.unicode_minus'] = True
df = pd.read_csv(r"D:\微信文件\WeChat Files\wxid_235yshiz2ylm22\FileStorage\File\2024-09\折线(3).csv",header=None)
vals = df[1]/1000000

# 计算平均湿地面积
average_area = np.mean(vals)
years = np.arange(2001, 2023, 1)
# 绘制图形
plt.figure(figsize=(10, 6))
# 绘制湿地面积变化曲线
plt.plot(years, vals,  color="black",linewidth=3)
# 在每个年份节点添加数据点
plt.scatter(years, vals, color="black", s=80, zorder=5)  # zorder参数用于将散点置于折线之上
# 绘制平均湿地面积虚线
plt.axhline(y=average_area, color="b", linestyle='--',linewidth=2)
plt.text(2016.5, average_area - 10,  
         f"average_area={average_area:.2f}", color='b',fontsize=15,fontstyle='italic',family="Times New Roman")
# # 添加背景阴影以标识特定时间段
# plt.axvspan(2002, 2005, color='yellow', alpha=0.3)
# plt.axvspan(2015, 2017, color='yellow', alpha=0.3)

# 添加两条竖虚线
plt.axvline(x=2008, color='#978a84', linestyle='--',linewidth=2)
plt.axvline(x=2016, color='#978a84', linestyle='--',linewidth=2)


# 使用sns.regplot添加2001-2008年趋势线
slope1, intercept1, r_value1, p_value1, std_err1 = linregress(years[:8], vals[:8])
sns.regplot(x=years[:8], y=vals[:8], scatter=False, color='#fe4b03', ci=95, 
            line_kws={'label': f"2001-2008斜率={round(slope1, 2)}", 'linewidth': 3})

# 在趋势线附近添加斜率、R²、p值
y_2004 = slope1 * 2004 + intercept1  
plt.text(2004+0.5, y_2004 + 7, f"Slope={slope1:.2f}\n R²={r_value1**2:.2f}\n p={p_value1:.4f}", color='#fe4b03',fontsize=15,fontstyle='italic',family="Times New Roman")

# 使用sns.regplot添加2008-2016年趋势线
slope2, intercept2, r_value2, p_value2, std_err2 = linregress(years[7:16], vals[7:16])
sns.regplot(x=years[7:16], y=vals[7:16], scatter=False, color='#069af3', ci=95,
            line_kws={'label': f"2008-2016斜率={round(slope1, 2)}", 'linewidth': 3})
y_2011 = slope2 * 2012 + intercept2 
plt.text(2012, y_2011 - 45 , f"Slope={slope2:.2f}\n R²={r_value2**2:.2f}\n p={p_value2:.4f}", color='#069af3',fontsize=15,fontstyle='italic',family="Times New Roman")

# 设置 X 轴刻度和网格线
plt.xticks(np.arange(2001, 2023, 1), rotation=45, fontsize=15,family="Times New Roman")
plt.yticks(fontsize=15,family="Times New Roman")
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tick_params(axis='x', direction='out', length=6)   # 设置刻度线朝外、长度、宽度

# 调整X轴刻度线位置与对齐
plt.gca().xaxis.set_tick_params(pad=3)  # 设置标签与刻度线的距离
plt.gca().xaxis.set_ticks_position('bottom')  # 确保刻度线位于底部
# 添加坐标轴标签和图表标题
# plt.xlabel('Years\n年份',fontsize=18)
# plt.ylabel('Wetland Area (km²)\n湿地面积',fontsize=18 )
# x轴标签
plt.text(0.45, -0.16, 'Years', 
         fontsize=18, 
         family="Times New Roman", 
         ha='center', va='center', 
         transform=plt.gca().transAxes)  # 基于轴坐标添加英文标签
plt.text(0.52, -0.16, '年份', 
         fontsize=18, 
         fontproperties=font_prop, 
         ha='center', va='center', 
         transform=plt.gca().transAxes)  # 基于轴坐标添加中文标签

# # y轴标签
# plt.text(-0.14, 0.5, 'Wetland Area/(km²)', 
#          fontsize=18, 
#          family="Times New Roman", 
#          ha='center', va='center', 
#          rotation='vertical', 
#          transform=plt.gca().transAxes)  # 基于轴坐标添加英文标签
# plt.text(-0.10, 0.5, '湿地面积', 
#          fontsize=18, 
#          fontproperties=font_prop, 
#          ha='center', va='center', 
#          rotation='vertical', 
#          transform=plt.gca().transAxes)  # 基于轴坐标添加中文标签
# 修改 y 轴标签的坐标位置
plt.ylabel('Wetland Area/(km²)', fontsize=18,family="Times New Roman", labelpad=30)
plt.text(-0.1, 0.5,'湿地面积' , fontsize=18, fontproperties=font_prop ,
         ha='center', va='center', rotation='vertical', transform=plt.gca().transAxes)

# 禁用自动y轴标签
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x)}"))

# 移除Y轴顶部的1
plt.gca().tick_params(axis='y', which='both', left=True, right=False, labelleft=True)

# 禁用 y 轴刻度线测试
plt.tick_params(axis='y', which='both', left=False)  # 测试是否是刻度线问题

plt.tight_layout()

# 显示图表并保存图像
#plt.savefig(r"F:\生态脆弱性\出图\折线图\折线图.png", dpi=300)
plt.show()
