# -*- coding: utf-8 -*-
import arcpy
import os
from arcpy import env
from arcpy.sa import *
import arcpy.mapping
import arcpy.mapping as mapping
from glob import glob as glb
arcpy.env.overwriteOutput = True
arcpy.env.workspace = u"D:\\数据批量\\表格"
path = u"D:\\数据批量\\表格\\均值"
out_path = u'D:\\数据批量\\表格\\tif\\tifk'
shp_path = u"D:\\桌面\\2021年全国行政区划+1940-2020年全球范围气象站点的逐日平均气温数据\\2021年全国行政区划\\省.shp"
T_mxd = u"D:\出图\\1960平均气温k.mxd"
T_tif = u"D:\\数据批量\\表格\\tif"
out_png = u"D:\\数据批量\\表格\\图片\\出图"
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
        out_mask = os.path.join(out_path, file_name + ".tif")
        arcpy.CheckOutExtension("Spatial")
        arcpy.gp.ExtractByMask_sa(outVarRaster, shp_path, out_mask)

flst = glb(T_tif + os.sep + '*.tif')
k = 0
mxd = arcpy.mapping.MapDocument(T_mxd)
for j in flst:
    mxd = arcpy.mapping.MapDocument(T_mxd)
    for df in mapping.ListDataFrames(mxd):
        lys = mapping.ListLayers(mxd, "", df)
        for ly in lys:
            if u'1960' in ly.name:
                ly.replaceDataSource(T_tif, "RASTER_WORKSPACE", os.path.basename(j)) # 替换数
    elm = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")
    elm[0].text = os.path.basename(j)[:-4] + u"年平均气温"
    save_png = out_png + os.sep + os.path.basename(j)[:-4]
    arcpy.mapping.ExportToPNG(mxd, save_png, resolution=600)
    k += 1
    print(k)

del mxd

