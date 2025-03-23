# -*- coding: utf-8 -*-
import arcpy, os
from arcpy import env
from arcpy.sa import *
import arcpy.mapping
import arcpy.mapping as mapping
from glob import glob as glb
arcpy.env.overwriteOutput = True
T_mxd = u"F:\\论文写作\\欣雨学姐\\出图\\数据\\防风固沙\\模版k.mxd"
T_tif = u"F:\\论文写作\\欣雨学姐\\出图\\数据\\固碳"
out_png = u"F:\\论文写作\\欣雨学姐\\出图\\图\\固碳"

flst = glb(T_tif + os.sep + '*.tif')
year = [2000,2005,2010,2015,2020]
k = 0
mxd = arcpy.mapping.MapDocument(T_mxd)
#for i in year:
    #fname = T_tif + os.sep + str(i) + ".tif"
for j in flst:

    mxd = arcpy.mapping.MapDocument(T_mxd)  # 打开模型
    for df in mapping.ListDataFrames(mxd):
        lys = mapping.ListLayers(mxd, "", df)
        for ly in lys:
            if u'2000' in ly.name:
                ly.replaceDataSource(T_tif, "RASTER_WORKSPACE", os.path.basename(fname)) # 替换数据

    elm = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT")
    save_png = out_png + os.sep + os.path.basename(j).split('.tif')[0]+ ".png"
    arcpy.mapping.ExportToPNG(mxd, save_png, resolution=600)
    k += 1
    print(k)

del mxd



# for i in year:
#     j = T_tif + os.sep + 'cnpp_Qt_'+ str(i) +'.tif'
#     #mxd = arcpy.mapping.MapDocument(T_mxd)  # 打开地图文档
#
#     # 替换栅格数据
#     for df in mapping.ListDataFrames(mxd):
#         lys = mapping.ListLayers(mxd, "", df)
#         print(lys)
#         for ly in lys:
#             if os.path.basename(j).split('2000')[0] in ly.name:  # 根据文件名替换数据
#                 print(j)  # 打印替换的栅格数据路径，确认是否替换正确
#                 ly.replaceDataSource(T_tif, "RASTER_WORKSPACE", os.path.basename(j))
                # 尝试强制刷新图层
                #arcpy.mapping.UpdateLayer(df, ly, ly)