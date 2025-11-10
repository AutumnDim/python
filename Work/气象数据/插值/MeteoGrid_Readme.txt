气象数据空间插值产品说明
jbwang@igsnrr.ac.cn(:2017-09-28&Beijing:)

1. MeteoGrid250m_08days
    是250米空间分辨率，每8天时间步长的气象插值后的栅格数据。8天时间步长，按MODIS数据合成时间，依次按日序1至8天、9至16、...、361至年最后一天，合计为每年46个时相。如下要素：
	（1）PRCP：8天总降水量，
	（2）RHU：8天平均相对湿度
	（3）SSD：8天平均日照时数
	（4）TAVG：8天平均日平均气温
	
2. MeteoGrid250m_10days
    是250米空间分辨率，每旬时间步长的气象插值后的栅格数据。旬定义为1至10、11至20、21至月末分别为上、中、下旬，合计为每年36个时相。包括如下要素：
	（1）PRCP：旬总降水量，
	（2）RHU：旬平均相对湿度
	（3）SSD：旬平均日照时数
	（4）TAVG：旬平均日平均气温
	
3. MeteoGrid11km_08days
    是1k米空间分辨率，每8天时间步长的气象插值后的栅格数据。8天时间步长，按MODIS数据合成时间，依次按日序1至8天、9至16、...、361至年最后一天，合计为每年46个时相。如下要素：
	（1）PRCP：8天总降水量，
	（2）RHU：8天平均相对湿度
	（3）SSD：8天平均日照时数
	（4）TAVG：8天平均日平均气温
4. 数据格式及处理
	（1）数据以32位浮点型二进制形式保存，具体数据信息及坐标信息可参见数据头文件。
	（2）投影信息，插值软件不能直接输出投影文件，只能复制给定投影文件为每个数据同名.prj文件：
		 神农架（按县界矩形外扩50公里）：SRTM_Shennj_250m.prj
			Projection    ALBERS
			Datum         WGS84
			Spheroid      WGS84
			Units         METERS
			Zunits        NO
			Xshift        0.0
			Yshift        0.0
			Parameters    
			  25  0  0.0 /* 1st standard parallel
			  47  0  0.0 /* 2nd standard parallel
			 105  0  0.0 /* central meridian
			   0  0  0.0 /* latitude of projection's origin
			4000000.0 /* false easting (meters)
			0.0 /* false northing (meters)

		 环江站（按县界矩形外扩50公里）：SRTM_Huanj_250m.prj
			Projection    ALBERS
			Datum         WGS84
			Spheroid      WGS84
			Units         METERS
			Zunits        NO
			Xshift        0.0
			Yshift        0.0
			Parameters    
			  25  0  0.0 /* 1st standard parallel
			  47  0  0.0 /* 2nd standard parallel
			 105  0  0.0 /* central meridian
			   0  0  0.0 /* latitude of projection's origin
			4000000.0 /* false easting (meters)
			0.0 /* false northing (meters)
		 全国（按大陆矩形外扩100公里）：SRTM_Asia_250m.prj
			Projection    ALBERS
			Datum         WGS84
			Spheroid      WGS84
			Units         METERS
			Zunits        NO
			Xshift        0.0
			Yshift        0.0
			Parameters    
			  25  0  0.0 /* 1st standard parallel
			  47  0  0.0 /* 2nd standard parallel
			 110  0  0.0 /* central meridian
			   0  0  0.0 /* latitude of projection's origin
			0.0 /* false easting (meters)
			0.0 /* false northing (meters)	 
	（3）数据及地图坐标信息
		 神农架（按县界矩形外扩50公里）：SRTM_Shennj_250m.hdr
			ncols         800
			nrows         680
			xllcorner     4410000
			yllcorner     3280000
			cellsize      250
			NODATA_value  -9999
		 环江站（按县界矩形外扩50公里）：SRTM_Huanj_250m.hdr
			ncols         800
			nrows         800
			xllcorner     4230000
			yllcorner     2530000
			cellsize      250
			NODATA_value  -9999
		 全国（按大陆矩形外扩100公里）：SRTM_Asia_250m.hdr
			ncols         8581
			nrows         5571
			xllcorner     -4250847.4505022
			yllcorner     1009302.3938841
			cellsize      1000
			NODATA_value  -9999		 
	（4）数据处理：
	     matlab环境
			 fip = fopen('data_file_name.flt','r');
			 dat = fread(fip, [ncols nrows],'float32');
			 fclose(fip);
		基于ArcGIS的Python环境
                fgrd = tpath + "grd/" + var + str0
                fflt = opath + var + str0 + ".flt"
                arcpy.FloatToRaster_conversion(fflt, fgrd)			
				