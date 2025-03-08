# -*- coding: utf-8 -*-
import arcpy, os
from arcpy import env
from arcpy.sa import *
import arcpy.mapping
import arcpy.mapping as mapping
from glob import glob as glb
arcpy.env.overwriteOutput = True
T_mxd = u"F:\论文写作\欣雨学姐\出图\数据\防风固沙\防风固沙.mxd"
T_tif = u"F:\论文写作\欣雨学姐\出图\数据\防风固沙"
out_png = u"D:\\数据批量\\表格\\图片"

flst = glb(T_tif + os.sep + '*.tif')
year = [2000,2005,2010,2015,2020]
k = 0
mxd = arcpy.mapping.MapDocument(T_mxd)
for i in list:
    fname = T_tif + os.sep + str(i) + ".tif"
# for j in flst:

    mxd = arcpy.mapping.MapDocument(T_mxd)  # 打开模型
    for df in mapping.ListDataFrames(mxd):
        lys = mapping.ListLayers(mxd, "", df)
        for ly in lys:
            if u'1960' in ly.name:
                ly.replaceDataSource(T_tif, "RASTER_WORKSPACE", os.path.basename(fname)) # 替换数据

    elm = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")
    elm[0].text = i + u"年平均气温"
    save_png = out_png + os.sep + i
    arcpy.mapping.ExportToPNG(mxd, save_png, resolution=600)
    k += 1
    print(k)

del mxd
