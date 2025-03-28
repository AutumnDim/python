# -*- coding: utf-8 -*-
"""
Created on Sun Nov 10 15:10:56 2024

@author: hqm
"""
#注意，是arcgis pro版本的arcpy!!!
import arcpy
import os

def batch_rename_rasters(workspace, name_pattern, start_num=1):
    """
    批量重命名工作空间中的栅格数据
    
    参数:
    workspace: 栅格数据所在的工作空间路径
    name_pattern: 新名称的模式,例如 "dem_{}",其中{}将被数字替换
    start_num: 起始编号,默认为1
    """
    
    # 设置工作空间
    arcpy.env.workspace = workspace
    
    # 获取工作空间中的所有栅格数据
    raster_list = arcpy.ListRasters()
    
    # 如果没有找到栅格数据,打印提示并返回
    if not raster_list:
        print(f"在 {workspace} 中没有找到栅格数据")
        return
    
    # 打印找到的栅格数据总数
    print(f"找到 {len(raster_list)} 个栅格数据")
    
    # 遍历所有栅格数据进行重命名
    for i, raster in enumerate(raster_list, start=start_num):
        try:
            # 构建新的栅格名称
            new_name = name_pattern.format(str(i).zfill(3))
            
            # 如果新名称已经存在,跳过该栅格
            if arcpy.Exists(new_name):
                print(f"警告: {new_name} 已存在,跳过 {raster}")
                continue
                
            # 重命名栅格
            arcpy.Rename_management(raster, new_name)
            print(f"已将 {raster} 重命名为 {new_name}")
            
        except arcpy.ExecuteError:
            print(f"重命名 {raster} 时发生错误: {arcpy.GetMessages()}")
        except Exception as e:
            print(f"处理 {raster} 时发生未知错误: {str(e)}")

if __name__ == "__main__":
    # 示例用法
    workspace_path = r"C:\Users\A1827\Desktop\未裁剪\干旱指数"  # 修改为你的栅格数据路径
    name_pattern = "tmp_ymax_{}"  # 修改为你想要的命名模式
    start_number = 2000  # 修改起始编号
    
    # 执行批量重命名
    batch_rename_rasters(workspace_path, name_pattern, start_number)