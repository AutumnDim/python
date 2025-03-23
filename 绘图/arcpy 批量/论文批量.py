# -*- coding: utf-8 -*-

import arcpy, os
from arcpy import env
from arcpy.sa import *
import arcpy.mapping
import arcpy.mapping as mapping
from glob import glob as glb

arcpy.env.overwriteOutput = True
T_mxd = u"F:\\mode.mxd"
T_tif = u"F:\\论文写作\\欣雨学姐\\出图\\数据\\土壤保持"
out_png = u"F:\\论文写作\\欣雨学姐\\出图\\图\\多年图\\土壤保持"

#flst = glb(T_tif + os.sep + '*.tif')

k = 0

for i in [2000, 2005, 2010, 2015, 2020]:
    mxd = arcpy.mapping.MapDocument(T_mxd)
    path_name = 'Qsr_' + str(i)+ '.tif'
    j = T_tif + os.sep + path_name
    # 替换图层数据源
    for df in arcpy.mapping.ListDataFrames(mxd):
        for ly in arcpy.mapping.ListLayers(mxd, "", df):
            if 'Qsr_'in ly.name:
                ly.replaceDataSource(T_tif, "RASTER_WORKSPACE", path_name)
                arcpy.mapping.UpdateLayer(df, ly, ly)


    arcpy.management.CalculateStatistics(j)

    # 获取当前栅格数据的最小值和最大值
    min_value = arcpy.GetRasterProperties_management(j, "MINIMUM")
    max_value = arcpy.GetRasterProperties_management(j, "MAXIMUM")
    min_value = round(float(min_value.getOutput(0)), 3)  # 保留两位小数
    max_value = round(float(max_value.getOutput(0)), 4)  # 保留两位小数

    # 更新图层的符号系统（确保符号渲染基于最小值和最大值）
    for df in mapping.ListDataFrames(mxd):
        lys = mapping.ListLayers(mxd, "", df)
        for ly in lys:
            if os.path.basename(j) in ly.name:  # 根据文件名获取正确的栅格图层
                if ly.isRasterLayer:  # 确保图层是 RasterLayer 类型
                    # 检查是否支持 symbology
                    if hasattr(ly, "symbology"):
                        ly.symbology.renderer.classBreakValues = [min_value, max_value]

    # 更新图例元素的文本（例如“High”和“Low”）
    elm = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")
    for element in elm:
        if "High" in element.text:  # 如果文本包含
            element.text = "高:{}".format(max_value)
        elif "Low" in element.text:  # 如果文本包含
            element.text = "低:{}".format(min_value)

    # 导出为 PNG 文件
    save_png = out_png + os.sep + os.path.basename(j)[:-4] + ".png"  # 设置输出文件名
    arcpy.mapping.ExportToPNG(mxd, save_png, resolution=600)

    k += 1
    print(k)
    # 释放资源
    del mxd

