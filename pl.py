import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd

# 读取 GeoJSON 数据
geojson_file_path = '中华人民共和国.json'
gdf_geojson = gpd.read_file(geojson_file_path)

# 读取 Shapefile 数据
shp_file_path = 'build/shp/new/filtered.shp'
gdf_shp = gpd.read_file(shp_file_path, encoding='GBK')

# 检查 GeoDataFrame 是否为空
if gdf_shp.empty:
    print("Shapefile GeoDataFrame is empty.")
else:
    # 设置 Pandas 显示选项
    pd.set_option('display.max_columns', None)  # 显示所有列
    pd.set_option('display.max_colwidth', None)  # 显示完整列宽

    # 打印 GeoDataFrame 信息
    print(gdf_shp.info())

    # 打印 GeoDataFrame 的前几行
    print(gdf_shp.head())

    # # 打印所有列的名称
    print("Columns in gdf_shp:", gdf_shp.columns.tolist())
