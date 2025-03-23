# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 19:10:18 2025

@author: hqm
"""
import pandas as pd
import glob
import rasterio
import numpy as np


#with rasterio.open(r'D:\22w\007那曲\防风固沙\data_u\土壤剖面编_0\土壤剖面编0.tif') as soil_profile:
#    soil_profile1 = soil_profile.read()
with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\数据\out\DEM.tif") as elev:
    elev1 = elev.read()
    profile = elev.profile
with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\数据\out\积雪.tif") as snow:
    snow1 = snow.read()
    nodata = snow.nodata
    snow1[snow1 == nodata] = np.nan
with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\数据\out\沙.tif") as sand:
    sand1 = sand.read()
    nodata = sand.nodata
    sand1[sand1 == nodata] = np.nan
with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\数据\out\粘土.tif") as clay:
    clay1 = clay.read()
    nodata = clay.nodata
    clay1[clay1 == nodata] = np.nan
with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\数据\out\土壤含水.tif") as swc:
    swc1 = swc.read()
    nodata = swc.nodata
    swc1[swc1 == nodata] = np.nan
with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\数据\out\ormc.tif") as som:
    som1 = som.read()
    nodata = som.nodata
    som1[som1 == nodata] = np.nan
with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\数据\out\碳酸钙.tif") as CaCO3:
    CaCO31 = CaCO3.read()
    nodata = CaCO3.nodata
    CaCO31[CaCO31 == nodata] = np.nan
# with rasterio.open(r'D:\22w\007那曲\防风固沙\data_u\地表粗糙度\rough.tif') as rough:
#     K = rough.read()
       

with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\数据\out\坡度.tif")as rough1:
    K1 = rough1.read()
    nodata = rough1.nodata
    K1[K1 == nodata] = np.nan
    K2 = np.cos(K1 * 3.1415926 / 180.0)
K_path = r"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\计算\因子\K.tif"
KK1 = rasterio.open(K_path, 'w', **profile)
KK1.write(K2)
KK1.close()

# slope_length = elev1 / K2


clay_w = clay1.copy()
clay_w[clay_w==0] = np.nan
sat = (0.332-7.251e-4*sand1 + 0.1276*np.log10(clay_w)) * 100.0
sand2 = sand1 * sand1
clay2 = clay_w * clay_w
soilalpha = np.exp(-4.396 - 0.0715*clay_w - 4.88e-4*sand2 - 4.285e-5*sand2*clay_w)
soilbeta = -3.140 - 0.00222*clay2 - 3.484e-5*sand2*clay_w
soilalpha[soilalpha==0] = np.nan
soilbeta[soilbeta==0] = np.nan
wp = np.power((15.0/(soilalpha)),(1.0/(soilbeta))) * 100.0
SW = (sat - swc1) / (sat - wp)
#len(SW[~np.isnan(SW)])

SD = 1-snow1 / 25.4
SD[snow1>25.4] = 0

silt1 = 100.0 - sand1 - clay_w
silt1[silt1<0] = 0.0
EF = (29.09 + 0.31 * sand1 + 0.17 * silt1 + 0.33 * (sand1 / clay_w) - 2.59 * som1 - 0.95 * CaCO31) /100.0
EF[EF<0] = 0
EF_path = r"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\计算\因子\EF.tif"
EF1 = rasterio.open(EF_path, 'w', **profile)
EF1.write(EF)
EF1.close()

SCF = 1.0 / (1.0 + 0.0066 * np.power(clay1, 2.0) + 0.021 * np.power(som1, 2.0))
SCF_path = r"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\计算\因子\SCF.tif"
SCF1 = rasterio.open(SCF_path, 'w', **profile)
SCF1.write(SCF)
SCF1.close()

with rasterio.open(r"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\数据\out\风速.tif") as wind:
    wind1 = wind.read()
    nodata = wind.nodata
    wind1 [wind1 == nodata] = np.nan
    
for year in range(2000,2021,5):
    # with rasterio.open(f'D:\\22w\\007那曲\\防风固沙\\data_u\\10m风速\\{year}.tif') as wind:
    #     wind1 = wind.read()
    
    with rasterio.open(rf"F:\\论文写作\\欣雨学姐\\计算\\实物量计算\\防风固沙\\数据\\气温\\tmp_{year}.tif") as tem:
        tem1 = tem.read()
        nodata = tem.nodata
        tem1[tem1 == nodata] = np.nan
    with rasterio.open(rf"F:\\论文写作\\欣雨学姐\\计算\\实物量计算\\防风固沙\\数据\\NDVI\\NDVI{year}.tif") as ndvi:
        ndvi1 = ndvi.read()
        nodata = ndvi.nodata
        ndvi1[ndvi1 == nodata] = np.nan
    
    # WF
    rou_air = 348 * ( (1.013-0.1183*(elev1/1000)+0.0048*(elev1/1000)*(elev1/1000))/(tem1+273.15) )
    
    # wind 单位为 1m/s  to 0.1m/s
    u2 = 0.72 * wind1 * 10
    WE = u2 * (u2 - 2.6877) * (u2 - 2.6877) * rou_air / 9.32
    WE[u2<=2.6877] = 0#???
    
    WF = WE*SW*SD 
    WF[WF<0] = 0
    #print(f'WF_{year}：', np.nanmean(WF))
    
    WF_path = rf"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\计算\因子\WF\WF_{year}.tif"
    WF1 = rasterio.open(WF_path, 'w', **profile)
    WF1.write(WF)
    WF1.close()
    
    ndvi1[ndvi1<0] = np.nan#???
    C = np.exp(-5.614 * np.power(ndvi1, 0.7366))
    C_path = rf"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\计算\因子\C\C_{year}.tif"
    C1 = rasterio.open(C_path, 'w', **profile)
    C1.write(C)
    C1.close()
    #C[C<=0] = np.nan
    

    

    # 防风固沙量
    a = WF*EF*SCF*K2
    a[a<0] = 0
    Qsf = 0.1699*np.power(a,1.3711)*(1-np.power(C,1.3711))
    #Qsf[soil_profile1==1] = 0.0
    
    
    print(f'Qsf_{year}：', np.nanmean(Qsf))
    
    out_path = rf"F:\论文写作\欣雨学姐\计算\实物量计算\防风固沙\计算\防风固沙\Qsf_{year}.tif"
    src1 = rasterio.open(out_path, 'w', **profile)
    
    src1.write(Qsf)
    
    src1.close()
    # break

