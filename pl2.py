import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib as mpl
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd

# 读取 Shapefile 数据
shp_file_path = 'build/shp/new/filtered.shp'
gdf_shp = gpd.read_file(shp_file_path, encoding='GBK')

# 设置 Pandas 显示选项
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.max_colwidth', None)  # 显示完整列宽

geojson_file_path = '中华人民共和国.json'
gdf_geojson = gpd.read_file(geojson_file_path)

# 定义 Albers 投影坐标系
albers_proj = ccrs.AlbersEqualArea(
    central_longitude=105,
    central_latitude=35,
    standard_parallels=(25, 47)
)

# 创建绘图对象
fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={'projection': albers_proj})

# 转换 Shapefile 数据的坐标系到自定义投影坐标系
if gdf_shp.crs != albers_proj:
    gdf_shp = gdf_shp.to_crs(albers_proj)
if gdf_geojson.crs != albers_proj:
    gdf_geojson = gdf_geojson.to_crs(albers_proj)
# 绘制转换后的 GeoJSON 数据
gdf_geojson.plot(ax=ax, edgecolor='black', facecolor='white', alpha=0.5, label='GeoJSON Data')


# 获取第10列的唯一值
unique_values = gdf_shp.iloc[:, 10].unique()  # 这里假设第10列的索引为10

# 创建中文到英文的映射字典
label_mapping = {
    '草甸': 'Meadow',
    '草原': 'Grassland',
    '草丛': 'Shrubland'
}

# 创建一个颜色映射
cmap = plt.get_cmap('viridis', len(unique_values))  # 使用viridis colormap
print(unique_values)

# 为每个多边形绘制不同的颜色
for i, value in enumerate(unique_values):
    # 根据条件过滤出当前值的数据
    subset = gdf_shp[gdf_shp.iloc[:, 10] == value]
    # 绘制当前值的数据，设置颜色
    subset.plot(ax=ax, edgecolor='none', facecolor=cmap(i / len(unique_values)), linewidth=2, alpha=0.5)

# 添加标题
plt.title('Shapefile Data Colored by Unique Values in Column 10')

# 创建图例并设置位置和字体大小
legend_patches = [
    mpatches.Patch(color=cmap(i / len(unique_values)), label=label_mapping.get(str(value), str(value))) 
    for i, value in enumerate(unique_values)
]
plt.legend(handles=legend_patches, title='Column 10 Values', loc='lower left',fontsize=20, title_fontsize=20, borderpad=1, handletextpad=1.5)


# 设置坐标轴标签
ax.set_xlabel('Easting (meters)')
ax.set_ylabel('Northing (meters)')

# 添加经纬度网格线
gridlines = ax.gridlines(draw_labels=True, color='gray', linestyle='--', alpha=0.5)
gridlines.xlabel_style = {'size': 10}
gridlines.ylabel_style = {'size': 10}
# 隐藏右边和上边的网格线标签
gridlines.top_labels = False
gridlines.right_labels = False

# 保存图形到文件
output_file_path = 'pic/shapefile_overlay_cartopy.png'
plt.savefig(output_file_path, dpi=300, bbox_inches='tight')

# 显示图形
plt.show()
