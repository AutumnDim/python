library(raster)
library("GD")

base_file <- "C:/Users/A1827/Desktop/生态脆弱性/地理探测器/自变量"
tif_file_path <- list.files(base_file, pattern=".tif$", full.names=TRUE, ignore.case=TRUE)
# 将全部栅格图像的数据放入同一个变量中
factor_stack <- stack(tif_file_path)

tif_file_all_matrix <- getValues(factor_stack)
tif_matrix <- na.omit(tif_file_all_matrix)
data_frame <- as.data.frame(tif_matrix)
# 导出为csv
# write.csv(data_frame,'data1.csv',row.names=FALSE)

# 离散化方式 ("equal","natural","quantile","geometric","sd")
discmethod <- c("equal","natural","quantile","geometric","sd")
# 分类数量
discitv <- c(5:8)
my_gd <- gdm(wetland_area ~ carbon_content+city_station+clay_content+dem+dryness+
                          landform_type+night_lights+population_density+
                          pre+sand_content+slope+soil_bulk_density+soil_pH+
                          tmp+water_content,
                        continuous_variable = c('carbon_content',
                                                'city_station',
                                                'clay_content',
                                                'dem',
                                                'dryness',
                                                'landform_type',
                                                'night_lights',
                                                'population_density',
                                                'pre',
                                                'sand_content',
                                                'slope',
                                                'soil_bulk_density',
                                                'soil_pH',
                                                'tmp',
                                                'water_content'),
                        data = data_frame,
                        discmethod = discmethod,
                        discitv = discitv)
# plot(my_gd)
