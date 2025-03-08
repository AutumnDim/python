# -*- coding: utf-8 -*-

import arcpy
import os
from arcpy import env
from arcpy.sa import *

# 设置工作空间
arcpy.env.overwriteOutput = True
arcpy.env.workspace = u"D:\\数据批量\\表格"
path = u"D:\\数据批量\\表格\\均值"
out_path = u'D:\\数据批量\\表格\\tif'
shp_path = u"D:\\桌面\\2021年全国行政区划+1940-2020年全球范围气象站点的逐日平均气温数据\\2021年全国行政区划\\省.shp"

files = os.listdir(path)
for file in files:
    if file.endswith('.csv'):
        file_name = os.path.splitext(file)[0]
        new_file_path = os.path.join(path, file)
        out_layer = file_name
        # 设置输出图层路径
        out_workspace = os.path.join(u"D:\\数据批量\\表格\\shp", file_name + ".shp")

        # 设置输出栅格路径
        outVarRaster = os.path.join(u"D:\\数据批量\\表格\\kgtif", "Kg" + file_name + ".tif")

        # Process: Make XY Event Layer
        arcpy.MakeXYEventLayer_management(new_file_path, "LONGITUDE", "LATITUDE", out_layer, arcpy.SpatialReference(4326), "")

        # Process: Feature Class
        arcpy.CopyFeatures_management(out_layer, out_workspace)

        # process: Kriging
        outKrig = Kriging(out_workspace, "TEMP", "Spherical 0.198906", 0.05, "VARIABLE 12", "")
        outKrig.save(outVarRaster)

        # process: Extract by mask
        #out_mask = os.path.join(u"D:\\数据批量\\tif", file_name + ".tif")
        #inRaster = outVarRaster
        #inMaskData = shp_path
        #arcpy.CheckOutExtension("Spatial")
        #outExtractByMask = ExtractByMask(outVarRaster, shp_path)
        #outExtractByMask.save(out_mask)
        out_mask = os.path.join(out_path, file_name + ".tif")
        arcpy.CheckOutExtension("Spatial")
        arcpy.gp.ExtractByMask_sa(outVarRaster, shp_path, out_mask)



