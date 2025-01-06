library(plspm)

# 读取数据
df <- read.csv("C:/Users/A1827/Desktop/生态脆弱性/结构方程模型/data.csv")
df_matrix <- na.omit(df)
data_frame <- as.data.frame(df_matrix)

# 定义路径矩阵
soil=c(0, 0, 0, 0, 0)  # soil受 social, topographic 的影响
social=c(0, 0, 0, 0, 0)  # social受 topographic 的影响
meteorological=c(1, 1, 0, 0, 0)  # meteorological 受 social, topographic 的影响
topographic=c(1, 1, 1, 0, 0)  # topographic 受 social, social 的影响
wetland_area=c(1, 1, 1, 1, 0) # wetland_area 受所有潜变量影响

foot_path=rbind(soil, social, meteorological, topographic, wetland_area)
colnames(foot_path)=c("soil", "social", "meteorological", "topographic", "wetland_area")
innerplot(foot_path)

foot_blocks=list(
  # soil潜在变量
  soil <- c("sand_content", "soil_pH", "soil_bulk_density", "clay_content", "carbon_content", "water_content"),  
  # social潜在变量
  social <- c("population_density", "city_station", "night_lights"),
  # meteorological潜在变量
  meteorological <- c('tmp'), # 'pre' "dryness"
  # topographic潜在变量
  topographic <- c("slope", "dem", "landform_type"),
  # wetland_area潜在变量（假设没有直接的观察变量，或者是一个被解释的因变量）
  wetland_area <- c("wetland_area"))
foot_mod=rep("A",5)

foot_pls=plspm(data_frame,foot_path,foot_blocks, scheme="path", modes=foot_mod)
summary(foot_pls)

#查看路径系数的参数估计值，以及相关的统计信息
foot_pls$path_coefs
foot_pls$inner_model

#查看因果关系的路径图，详情 ?innerplot
innerplot(foot_pls, colpos = 'red', colneg = 'blue', show.values = TRUE, lcol = 'gray', box.lwd = 0)

#查看作为外源潜变量和内源潜变量的状态
foot_pls$inner_summary

#查看变量间的影响状态
foot_pls$effects

#查看观测变量和潜变量关系，可通过 outerplot() 画图展示类似路径图的结构，详情 ?outerplot
foot_pls$outer_model
outerplot(foot_pls, what = 'loadings', arr.width = 0.1, colpos = 'red', colneg = 'blue', show.values = TRUE, lcol = 'gray')
outerplot(foot_pls, what = 'weights', arr.width = 0.1, colpos = 'red', colneg = 'blue', show.values = TRUE, lcol = 'gray')

#goodness-of-fit 值可以帮助评估模型优度
foot_pls$gof

#查看潜变量得分，可以理解为标准化后的潜变量的值
foot_pls$scores

#输出潜变量的值
#latent <- data.frame(foot_pls$scores)
#latent <- cbind(foot_pls$site, latent)
#write.csv(latent, 'latent.csv')