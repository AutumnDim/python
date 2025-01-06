# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 20:05:10 2024

@author: hqm
"""
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Rectangle, Ellipse
import numpy as np
from matplotlib import font_manager, rcParams
from matplotlib.ticker import MultipleLocator
from matplotlib.font_manager import FontProperties
font_path = r"C:/WINDOWS/Fonts/TIMES.TTF"
font_prop = font_manager.FontProperties(fname=font_path)
# 配置全局字体
config = {
    "font.family": "Times New Roman",  # 设置衬线字体
    "font.serif": ["Times New Roman"],  # 设置为宋体
    "font.size": 15,  # 设置字体大小
    "axes.unicode_minus": False,  # 处理负号
}
rcParams.update(config)
def plot_combined_model_custom_layout():
    G = nx.DiGraph()
    # 添加路径系数的边（潜变量之间）
    edges = [
        ("social", "wetland", -0.0925),
        ("soil", "topographic",  0.1614),
        ("social", "meteorological", 0.3205),
        ("meteorological", "topographic",  -0.7854),
        ("social", "topographic", -0.0568),
        ("topographic", "wetland", -0.3802),
        ("soil", "wetland", -0.6054),
        ("soil", "meteorological", -0.1022),
        ("meteorological", "wetland", -0.2295)
    ]
    
    # soil潜变量及其观测变量
    soil_loadings = [
        ("soil", "sand_content", 0.8785),
        ("soil", "soil_pH", 0.9473),
        ("soil", "soil_bulk_density", 0.8716),
        ("soil", "clay_content", 0.9401),
        ("soil", "carbon_content", 0.4661),
        ("soil", "water_content", 0.951)
    ]
    
    # social潜变量及其观测变量
    social_loadings = [
        ("social", "population_density", 0.5356),
        ("social", "city_station", -0.8956),
        ("social", "night_lights", 0.6169)
    ]
    
    # meteorological潜变量及其观测变量
    meteorological_loadings = [
        ("meteorological", "tmp", 1)
    ]
    
    # topographic潜变量及其观测变量
    topographic_loadings = [
        ("topographic", "slope", 0.9035),
        ("topographic", "dem", 0.9179),
        ("topographic", "landform_type", 0.9002)
    ]
    
    # wetland_area潜变量及其观测变量
    wetland_area_loadings = [
        ("wetland", "wetland_area", 1.0000)
    ]

    # 添加所有的负荷关系
    loadings = soil_loadings + social_loadings + meteorological_loadings + topographic_loadings + wetland_area_loadings

    # 在图中添加路径系数边
    for edge in edges:
        G.add_edge(edge[0], edge[1], weight=edge[2])

    # 在图中添加负荷系数边
    for edge in loadings:
        G.add_edge(edge[0], edge[1], weight=edge[2])
    
    # 自定义每个节点的位置
    pos = {
        "social": (9.5, 4.2),
        "topographic": (4.5, 4),
        "soil": (4.5, 10),
        "meteorological": (9.5, 10),
        "wetland": (7, 7),
        
        # soil的观测变量
        "sand_content": (2, 14),
        "soil_pH": (4, 14),
        "soil_bulk_density": (1.5, 12),
        "clay_content": (1.5, 10),
        "carbon_content": (1.5, 7.8),
        "water_content": (6, 14),
        
        # social的观测变量
        "population_density": (12.5, 5),
        "city_station": (11, 1),
        "night_lights": (12.5, 2.5),
        
        # meteorological的观测变量
        "tmp": (12.5, 11),

        # topographic的观测变量
        "slope": (3.5, 1),
        "dem": (1.5, 2.5),
        "landform_type": (1.5, 5),
        
        # wetland_area的观测变量
        "wetland_area": (7.5, 1)
    }
    
    plt.figure(figsize=(13, 9), facecolor='white')  # 增加图形大小，设置背景颜色为白色
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)  # 调整边距

    # 获取潜变量和观测变量
    latent_vars = ["social", "topographic", "soil", "meteorological", "wetland"]
    observed_vars = list(set(G.nodes()) - set(latent_vars))


    # 绘制潜变量（椭圆）和观测变量（矩形）
    ax = plt.gca()
    
    # AVE值
    ave_dict = {
        'soil':0.74,
        'social':0.49,
        'meteorological':1.00,
        'topographic':0.82,
        'wetland':1.00
    }
    
    # 获取椭圆边界的交点（潜变量）
    def get_edge_ellipse_intersection(start, ellipse_width, ellipse_height, end):
        # 根据潜变量和观测变量的坐标，计算线条从椭圆的边界开始的坐标
        x_start, y_start = start
        x_end, y_end = end
        dx = x_end - x_start
        dy = y_end - y_start
        scale = (ellipse_width / 4) / max(abs(dx), abs(dy))
        return x_start + dx * scale, y_start + dy * scale
    
    # 获取矩形边界的交点（观测变量）
    def get_edge_rectangle_intersection(start, rect_width, rect_height, end):
        x_start, y_start = start
        x_end, y_end = end
        dx = x_end - x_start
        dy = y_end - y_start
        scale = (rect_width / 4) / max(abs(dx), abs(dy))
        return x_start + dx * scale, y_start + dy * scale
    # 定义每个观测变量到潜变量的线长度
    edge_lengths = {
        # soil的观测变量
        "sand_content": 1,
        "soil_pH": 10,
        "soil_bulk_density": 1,
        "clay_content": 3.0,
        "carbon_content": 2.5,
        "water_content": 4.0,
    
        # social的观测变量
        "population_density": 4.5,
        "city_station": 3.5,
        "night_lights": 3.0,
    
        # meteorological的观测变量
        "tmp": 5.5,
    
        # topographic的观测变量
        "slope": 3.5,
        "dem": 3.0,
        "landform_type": 2.8,
    
        # wetland_area的观测变量
        "wetland_area": 2
    }
    
    # 绘制路径系数
    if edges:
        path_colors = ['red' if weight > 0 else 'blue' for _, _, weight in edges]
        path_widths = [abs(weight) * 3 for _, _, weight in edges]  # 根据系数调整线的粗细
        
        for (idx, (u, v, d)) in enumerate(edges):
            x_start, y_start = pos[u]
            x_end, y_end = pos[v]
            length_factor = edge_lengths.get(v, 1)
            
            # 获取当前边的颜色
            edge_color = path_colors[idx]
            edge_width = path_widths[idx]
            edge_margins = [(20, 50),(110, 36),(115, 36),(110, 35),(10, 45),(110,36),(110, 50),(110, 45),(11, 36)]
            min_source_margin, min_target_margin = edge_margins[idx]
            # 绘制边并设置箭头
            nx.draw_networkx_edges(
                G, pos,
                edgelist=[(u, v)],
                edge_color=edge_color,  # 使用单一颜色，确保箭头颜色一致
                width=edge_width,
                connectionstyle="arc3,rad=0.32",
                arrows=True,
                arrowsize=20,
                ax=plt.gca(),
                arrowstyle="-|>",  # 箭头样式
                min_source_margin=min_source_margin,
                min_target_margin=min_target_margin
            )
            
            # 计算边的中点坐标
            x_middle = (x_start + x_end) / 2
            y_middle = (y_start + y_end) / 2
            
            # 如果起点或终点是潜变量或观测变量，调整线的起止点
            if u in latent_vars:
                x_start, y_start = get_edge_ellipse_intersection((x_start, y_start), 2, 2, (x_end, y_end))
            if v in observed_vars:
                x_end, y_end = get_edge_rectangle_intersection((x_start, y_start), 1.5, 0.8, (x_end, y_end))
            
            # 定义偏移量
            offset_dict = {
                ("social", "wetland"): (0.35, -0),
                ("soil", "topographic"): (-0.2, 1.2),
                ("social", "meteorological"): (0.15, -1.2),
                ("meteorological", "topographic"): (0.6, 2.7),
                ("social", "topographic"): (1.2, 0.7),
                ("topographic", "wetland"): (0.2, -1.2),
                ("soil", "wetland"): (-0.4, 0),
                ("soil", "meteorological"): (-1.2, -0.8),
                ("meteorological", "wetland"): (-0.1, 0.5)
            }


    
            # 获取当前边的偏移量
            x_offset, y_offset = offset_dict.get((u, v), (0, 0.2))
            x_offset *= length_factor
            y_offset *= length_factor
            # 在调整后的位置绘制标签
            ax.text(x_middle + x_offset, y_middle + y_offset, f'{d:.2f}', fontsize=15,  ha='center', va='center')

        # 绘制路径边，并确保箭头正确显示
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=path_colors, 
                                 width=path_widths, ax=ax, arrows=True, 
                                 arrowsize=20, connectionstyle="arc3,rad=0.32")
    
    # 绘制负荷系数
    if loadings:
        for u, v, d in loadings:
            # 获取起点和终点的坐标
            x_start, y_start = pos[u]
            x_end, y_end = pos[v]
    
            # 如果起点是潜变量节点，则将线条起点调整到椭圆的边缘
            if u in latent_vars:
                x_start, y_start = get_edge_ellipse_intersection((x_start, y_start), 2, 3, (x_end, y_end))
    
            # 设置边的颜色和宽度
            loading_colors = ['red' if weight > 0 else 'blue' for _, _, weight in loadings]
            loading_widths = [abs(weight) * 3 for _, _, weight in loadings]
        # 合并所有潜变量及其观测变量
            loadings = [
                # soil 潜变量及其观测变量
                ("soil", "sand_content", 0.8785),
                ("soil", "soil_pH", 0.9473),
                ("soil", "soil_bulk_density", 0.8716),
                ("soil", "clay_content", 0.9401),
                ("soil", "carbon_content", 0.4661),
                ("soil", "water_content", 0.951),
            
                # social 潜变量及其观测变量
                ("social", "population_density", 0.5356),
                ("social", "city_station", -0.8956),
                ("social", "night_lights", 0.6169),
            
                # meteorological 潜变量及其观测变量
                ("meteorological", "tmp", 1),
            
                # topographic 潜变量及其观测变量
                ("topographic", "slope", 0.9035),
                ("topographic", "dem", 0.9179),
                ("topographic", "landform_type", 0.9002),
            
                # wetland_area 潜变量及其观测变量
                ("wetland", "wetland_area", 1.0000)
            ]
            
            # 定义每条边的 min_source_margin 和 min_target_margin 参数
            edge_margins = [
                (20, 42), (11, 15), (115, 58), (110, 25), (1, 14), (110, 12),  # soil
                (1000,20), (1000, 30), (1100, 41),                                 # social
                (1000, 17),                                                     # meteorological
                (1000, 12), (1000, 15), (1000, 45),                               # topographic
                (1000, 15)                                                      # wetland_area
            ]
            
            # 为每条边设置颜色和宽度
            path_colors = ['red' if weight > 0 else 'blue' for _, _, weight in loadings]
            path_widths = [abs(weight) * 3 for _, _, weight in loadings]  # 根据系数调整线的粗细
            
            # 绘制边
            for idx, (u, v, weight) in enumerate(loadings):
                # 获取起点和终点的位置
                x_start, y_start = pos[u]
                x_end, y_end = pos[v]
            
                # 获取当前边的颜色和宽度
                edge_color = path_colors[idx]
                edge_width = path_widths[idx]
            
                # 获取当前边的 min_source_margin 和 min_target_margin 参数
                min_source_margin, min_target_margin = edge_margins[idx]
            
                # 绘制边并设置箭头
                nx.draw_networkx_edges(
                    G, pos,
                    edgelist=[(u, v)],
                    edge_color=edge_color,  # 使用单一颜色，确保箭头颜色一致
                    width=edge_width,
                    connectionstyle="arc3,rad=0.32",
                    arrows=True,
                    arrowsize=20,
                    ax=plt.gca(),
                    arrowstyle="-|>",  # 箭头样式
                    min_source_margin=min_source_margin,
                    min_target_margin=min_target_margin
                )

        # 绘制负荷边
        nx.draw_networkx_edges(G, pos, edgelist=loadings, edge_color=loading_colors, 
                                 width=loading_widths, ax=ax, arrows=True, 
                                 arrowsize=15, connectionstyle="arc3,rad=0.32",node_size=10) #,node_size=1000

        # 添加负荷系数的标签
        # 偏移量字典（用来调整标签位置）
        loadings_offset_dict = {
            ("soil", "sand_content"): (0.45, -0.2),
            ("soil", "soil_pH"): (0.1, -0.2),
            ("soil", "soil_bulk_density"): (0.5, 0),
            ("soil", "clay_content"): (0.2, 0.3),
            ("soil", "carbon_content"): (0.2, 0.5),
            ("soil", "water_content"): (0.05, -0.5),
            ("social", "population_density"): (-0.1, -0.6),
            ("social", "city_station"): (-0.1, -0.2),
            ("social", "night_lights"): (-0.35, -0.4),
            ("meteorological", "tmp"): (-0.1, -0.65),
            ("topographic", "slope"): (0., 0.2),
            ("topographic", "dem"): (0.1, 0.6),
            ("topographic", "landform_type"): (0.4, 0.3),
            ("wetland", "wetland_area"): (-0.3, 1)
        }
        
        
        # 创建一个无向图
        G = nx.Graph()
        
        # 添加边
        for loadings_list in [soil_loadings, social_loadings, meteorological_loadings, topographic_loadings, wetland_area_loadings]:
            for u, v, _ in loadings_list:
                G.add_edge(u, v)
        # 为每条边添加标签并应用偏移量
        labels1 = {(u, v): f"{d:.2f}" for u, v, d in soil_loadings + social_loadings + meteorological_loadings + topographic_loadings + wetland_area_loadings}

        # 设置字体属性
        font_properties = FontProperties(family='Times New Roman', size=15)
        
        # 手动添加边标签并应用偏移量
        for u, v, d in soil_loadings + social_loadings + meteorological_loadings + topographic_loadings + wetland_area_loadings:
            label = f"{d:.2f}"
            
            # 获取偏移量
            x_offset, y_offset = loadings_offset_dict.get((u, v), (0, 0))
            
            # 获取边的中点位置
            x_start, y_start = pos[u]
            x_end, y_end = pos[v]
            
            # 计算边的中点位置并添加偏移量
            x_middle = (x_start + x_end) / 2 + x_offset
            y_middle = (y_start + y_end) / 2 + y_offset
            
            # 在中点位置添加标签
            ax.text(x_middle, y_middle, label, fontsize=15, ha='center', va='center', 
                    fontfamily=font_properties.get_name())

    # 绘制潜变量（椭圆）并添加AVE值
    for node in latent_vars:
        x, y = pos[node]
        ellipse = Ellipse((x, y), width=1.8, height=2, edgecolor='orange', facecolor='peachpuff', lw=2)
        ax.add_patch(ellipse)
        # 在潜变量中心绘制节点名称
        ax.text(x, y + 0.1, node, ha='center', va='center', fontsize=15)
        # 在潜变量下方绘制AVE值
        ax.text(x, y - 0.4, f"AVE={ave_dict[node]:.2f}", ha='center', va='center', fontsize=15, color='green')
    
    # 绘制观测变量（矩形）
    for node in observed_vars:
        x, y = pos[node]
        rect = Rectangle((x - 0.75, y - 0.375), width=1.5, height=0.75, edgecolor='none', facecolor='none', lw=2)
        ax.add_patch(rect)
        ax.text(x, y, node, ha='center', va='center', fontsize=15,
                    bbox=dict(facecolor='lightblue', edgecolor='blue', boxstyle='round,pad=0.3'))
    # 在右下角绘制GOF
    ax.text(12.5, 14, f"GOF = 0.554", fontsize=15, color='black', ha='center')
    ax.text(12.5, 13.5, f"R² = 0.501", fontsize=15, color='black', ha='center')
    plt.show()

# 调用函数绘图
plot_combined_model_custom_layout()
plt.savefig(r"F:\生态脆弱性\出图\结构方程模型\结构方程模型.png", dpi=300)