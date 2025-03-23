# -*- coding: utf-8 -*-
import arcpy, os
from arcpy import env
from arcpy.sa import *
import arcpy.mapping
import arcpy.mapping as mapping
from glob import glob as glb

arcpy.env.overwriteOutput = True
T_mxd = u"F:\\论文写作\\欣雨学姐\\出图\\数据\\防风固沙\\模版.mxd"
T_tif = u"F:\\论文写作\\欣雨学姐\\出图\\数据\\防风固沙"
out_png = u"F:\\论文写作\\欣雨学姐\\出图\\图\\防风固沙"

flst = glb(T_tif + os.sep + '*.tif')
year = [2000, 2005, 2010, 2015, 2020]
k = 0
mxd = arcpy.mapping.MapDocument(T_mxd)

for j in flst:
    mxd = arcpy.mapping.MapDocument(T_mxd)  # 打开地图文档

    # 替换栅格数据
    for df in mapping.ListDataFrames(mxd):
        lys = mapping.ListLayers(mxd, "", df)
        for ly in lys:
            if os.path.basename(j) in ly.name:  # 根据文件名替换数据
                ly.replaceDataSource(T_tif, "RASTER_WORKSPACE", os.path.basename(j))

    # 计算栅格数据的统计信息（如果没有的话）
    arcpy.management.CalculateStatistics(j)

    # 获取当前栅格数据的最小值和最大值
    min_value = arcpy.GetRasterProperties_management(j, "MINIMUM")
    max_value = arcpy.GetRasterProperties_management(j, "MAXIMUM")

    # 直接获取最小值和最大值并保留两位小数
    min_value = round(float(min_value.getOutput(0)), 2)  # 保留两位小数
    max_value = round(float(max_value.getOutput(0)), 2)  # 保留两位小数

    # 更新图层的符号系统（确保符号渲染基于最小值和最大值）
    for df in mapping.ListDataFrames(mxd):
        lys = mapping.ListLayers(mxd, "", df)
        for ly in lys:
            if os.path.basename(j) in ly.name:  # 根据文件名获取正确的栅格图层
                if ly.isRasterLayer:  # 确保图层是 RasterLayer 类型
                    # 检查图层的符号类型
                    if ly.symbologyType == "CLASSIFIED":
                        # 获取分类渲染器并设置分类区间
                        symbology = ly.symbology
                        classification = symbology.classBreakValues
                        classification[0] = min_value
                        classification[-1] = max_value
                        ly.symbology = symbology  # 更新图层符号

    # 更新图例元素的文本（例如“low”和“high”）
    elm = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")
    for element in elm:
        if "high"  in element.text:  # 如果文本包含 "low"
            element.text = "High:{}".format(max_value)
    # 导出为 PNG 文件
    save_png = out_png + os.sep + os.path.basename(j)[:-4] + ".png"  # 设置输出文件名
    arcpy.mapping.ExportToPNG(mxd, save_png, resolution=600)

    k += 1
    #print("已导出第 {} 张地图：{}".format(k, save_png))

# 释放资源
del mxd





