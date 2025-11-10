# -*- coding: utf-8 -*-
"""
Created on Mon Sep  1 10:07:04 2025

@author: hqm
"""
# import pandas as pd
# import numpy as np
# import rasterio ,os
# from glob import glob as glb
# # #path = r'F:\work\地理所\地上生物量\输出\2023\AGB'
# # fist = glb(r'F:\work\地理所\地上生物量\输出\2023\AGB\*.tif')
# # for i in fist:
# #     with rasterio.open(i) as :
# import rasterio

# fp = r"F:\work\地理所\地上生物量\输出\2023\AGB\grid1_Season1.tif"

# with rasterio.open(fp) as ds:
#     print("波段数:", ds.count)
#     print("波段名字列表:", ds.descriptions)

#     for i, desc in enumerate(ds.descriptions, start=1):
#         print(f"Band {i} 名字:", desc if desc else f"band_{i}")
        
        











'''23-25年 7-8月数据'''

# import os
# import numpy as np
# import rasterio
# from rasterio.transform import Affine
# from glob import glob as glb
# files = sorted(glb(r'F:\work\地理所\地上生物量\输出\2024\AGB\7-8\*.tif'))
# for y in 
# for i in files:
# with rasterio.open(r"F:\work\地理所\地上生物量\输出\2023\AGB\mean_by_bandname_scaled.tif") as ds0:
#     data = ds0.read(2)



import os
import numpy as np
import rasterio
from glob import glob as glb

# ========= 配置 =========
in_glob = r"E:\地上生物量\地上生物量\输出\2024\2024\2408\*.tif"
out_dir = r"E:\地上生物量\地上生物量\输出\2024\2024\2408\out"
os.makedirs(out_dir, exist_ok=True)

scale_cols = ['CAI', 'CRI',  'NDII','NDVI', 'RGR', 'RVI',  'SATVI', 'SAVI', 'VARI']  # 需要缩放的波段
nodata_out = np.nan
dtype_out = 'float32'

# ========= 收集文件 =========
files = sorted(glb(in_glob))
if not files:
    raise RuntimeError(f'未找到输入影像: {in_glob}')
print(f'共 {len(files)} 个输入影像')

# ========= 获取基准信息 & 波段名 =========
with rasterio.open(files[0]) as s0:
    height, width = s0.height, s0.width
    transform, crs = s0.transform, s0.crs

# 收集每个文件的波段名
bandnames_per_file = []
for f in files:
    with rasterio.open(f) as s:
        assert s.crs == crs and s.transform == transform
        assert s.width == width and s.height == height
        desc = list(s.descriptions) if s.descriptions else [f'B{i}' for i in range(1, s.count+1)]
        desc = [d if d else f'B{i+1}' for i,d in enumerate(desc)]
        bandnames_per_file.append(desc)

# 取共同波段名
common_names = set(bandnames_per_file[0])
for desc in bandnames_per_file[1:]:
    common_names &= set(desc)
common_names = sorted(common_names)
print("共同波段名:", common_names)

# 文件中 bandname -> index 映射
name2idx_list = []
for desc in bandnames_per_file:
    name2idx_list.append({d: i+1 for i,d in enumerate(desc)})

# ========= 函数 =========
def read_band_as_float(s, band_idx):
    arr = s.read(band_idx, out_dtype='float32')
    m = s.read_masks(band_idx)
    arr = np.where(m==0, np.nan, arr)
    if s.nodata is not None:
        arr = np.where(np.isclose(arr, s.nodata), np.nan, arr)
    return arr

# ========= 按波段平均并逐一写出 =========
for name in common_names:
    stack_list = []
    for f, name2idx in zip(files, name2idx_list):
        idx = name2idx[name]
        with rasterio.open(f) as s:
            arr = read_band_as_float(s, idx)
            stack_list.append(arr)
    stack = np.stack(stack_list, axis=0)
    mean_ = np.nanmean(stack, axis=0).astype('float32')
    mean_[np.isnan(mean_)] = nodata_out

    # ⚡ 指定波段做缩放
    if name in scale_cols:
        mean_ = mean_ / 10000.0

    # 输出单波段 GeoTIFF
    out_path = os.path.join(out_dir, f"{name}.tif")
    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 1,
        "crs": crs,
        "transform": transform,
        "dtype": dtype_out,
        "nodata": nodata_out,
        "compress": "deflate"
    }
    with rasterio.open(out_path, 'w', **profile) as dst:
        dst.write(mean_, 1)
        dst.set_band_description(1, name)

    print(f"写出波段 {name} → {out_path}")

print("全部完成 ✅")






'''特征提取'''

# import pandas as pd
# import numpy as np
# kist = []

# path1 = r"F:\work\地理所\地上生物量\采样点数据\特征提取\points_timeseries_all_bands2021.csv"
# df1 = pd.read_csv(path1)
# df1['date_str'] = pd.to_datetime(df1['date_str'], format='%Y/%m/%d')
# df1_a = df1[(df1['date_str'].dt.year == 2020) & (df1['date_str'].dt.month == 8)]

# grouped1 = df1_a.groupby(['Abovegroun'])[[ 'Blue', 'CAI', 'CRI', 'Green', 'NDII','NDVI', 'NIR', 'QA', 'RGR', 'RVI', 'Red', 'SATVI', 
#     'SAVI', 'SWIR1','SWIR2', 'VARI']].mean().reset_index()

# scale_cols = ['CAI', 'CRI',  'NDII','NDVI', 'RGR', 'RVI',  'SATVI', 'SAVI', 'VARI']  # [ndvi, rvi, cri, rgr, ndii, satvi, cai, savi, vari]
# grouped1[scale_cols] = grouped1[scale_cols] / 10000
# grouped1.rename(columns={'Abovegroun': 'AGB'}, inplace=True)  # 统一列名
# kist.append(grouped1)

# path2 = r"F:\work\地理所\地上生物量\采样点数据\特征提取\points_timeseries_all_bands2024.csv"
# df2 = pd.read_csv(path2)

# grouped2 = df2.groupby(['AGB（g_m2'])[[ 
#     'Blue', 'CAI', 'CRI', 'Green', 'NDII','NDVI', 
#     'NIR', 'QA', 'RGR', 'RVI', 'Red', 'SATVI', 
#     'SAVI', 'SWIR1','SWIR2', 'VARI'
# ]].mean().reset_index()

# grouped2[scale_cols] = grouped2[scale_cols] / 10000
# grouped2.rename(columns={'AGB（g_m2': 'AGB'}, inplace=True)  # 统一列名
# kist.append(grouped2)

# path3 = r"F:\work\地理所\地上生物量\采样点数据\特征提取\points_timeseries_all_bands2023.csv"
# df3 = pd.read_csv(path3)

# grouped3 = df3.groupby(['干重（g'])[[ 
#     'Blue', 'CAI', 'CRI', 'Green', 'NDII','NDVI', 
#     'NIR', 'QA', 'RGR', 'RVI', 'Red', 'SATVI', 
#     'SAVI', 'SWIR1','SWIR2', 'VARI'
# ]].mean().reset_index()

# grouped3[scale_cols] = grouped3[scale_cols] / 10000
# grouped3.rename(columns={'干重（g': 'AGB'}, inplace=True)  # 统一列名
# kist.append(grouped3)

# final_df = pd.concat(kist, ignore_index=True)

# out_csv = r"F:\work\地理所\地上生物量\采样点数据\特征提取\AGB.csv"
# final_df.to_csv(out_csv, index=False, encoding="utf-8-sig")




'''预测结果可视化'''

import pandas as pd 
import numpy as np 
import rasterio
path = r"E:\地上生物量\地上生物量\7,8\2508.tif"
# with rasterio.open(path) as res:
#     data = res.read
#     k = data.mean()
with rasterio.open(path) as res:
    data = res.read()
    # 获取nodata值
    nodata = res.nodata
    
    if nodata is not None:
        # 将nodata值替换为NaN，然后计算平均值
        data = data.astype(np.float32)
        data[data == nodata] = np.nan
        mean_value = np.nanmean(data)
        print(f"去除nodata后的平均值: {mean_value}")
    else:
        mean_value = data.mean()
        print(f"平均值: {mean_value}")







import matplotlib.pyplot as plt
import numpy as np
# 数据
years = [2023, 2024, 2025]
values = [107.02558135986328, 96.67459869384766, 105.56409454345703]

# 创建折线图
plt.figure(figsize=(8, 5))
plt.plot(years, values, marker='o', linestyle='-', linewidth=2, markersize=6, color='blue')

# 设置标题和标签
plt.title('地上生物量8月变化 (2023-2025)')
plt.xlabel('年份')
plt.ylabel('地上生物量 (g/m2)')  # 添加单位

plt.xticks(years)

# 添加数据标签
for i, value in enumerate(values):
    plt.text(years[i], value + 0.8, f'{value:.2f}', ha='center', va='bottom')

# 添加网格
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()


