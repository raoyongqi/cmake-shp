import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
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

# 创建绘图对象，2个子图横向排列，减少两张图之间的距离
fig, (ax_map, ax_legend) = plt.subplots(nrows=1, ncols=2, figsize=(24, 12), subplot_kw={'projection': albers_proj}, gridspec_kw={'wspace': 0.1})

# 转换 Shapefile 数据的坐标系到自定义投影坐标系
if gdf_shp.crs != albers_proj:
    gdf_shp = gdf_shp.to_crs(albers_proj)
if gdf_geojson.crs != albers_proj:
    gdf_geojson = gdf_geojson.to_crs(albers_proj)

# 绘制转换后的 GeoJSON 数据
gdf_geojson.plot(ax=ax_map, edgecolor='black', facecolor='white', alpha=0.5, label='GeoJSON Data')

# 获取第14列的唯一值
unique_values = gdf_shp.iloc[:, 13].unique()  # 这里假设第14列的索引为13

# 创建中文到英文的映射字典
label_mapping = {
    None: '', 
    'None': 'Other grassland',
}

# 创建一个颜色映射
cmap = plt.get_cmap('viridis', len(unique_values))  # 使用viridis colormap
print(unique_values)

# 为每个多边形绘制不同的颜色
for i, value in enumerate(unique_values):
    # 根据条件过滤出当前值的数据
    subset = gdf_shp[gdf_shp.iloc[:, 13] == value]
    # 绘制当前值的数据，设置颜色
    subset.plot(ax=ax_map, edgecolor='none', facecolor=cmap(i / len(unique_values)), linewidth=2, alpha=0.5)

# 添加标题
ax_map.set_title('Shapefile Data Colored by Unique Values in Column 14')

# 设置坐标轴标签
ax_map.set_xlabel('Easting (meters)')
ax_map.set_ylabel('Northing (meters)')

# 添加经纬度网格线
gridlines = ax_map.gridlines(draw_labels=True, color='gray', linestyle='--', alpha=0.5)
gridlines.xlabel_style = {'size': 10}
gridlines.ylabel_style = {'size': 10}
# 隐藏右边和上边的网格线标签
gridlines.top_labels = False
gridlines.right_labels = False

# 创建图例并设置位置和字体大小
legend_patches = [
    mpatches.Patch(color=cmap(i / len(unique_values)), label=label_mapping.get(str(value), str(value))) 
    for i, value in enumerate(unique_values)
]

# 在第二个子图中添加图例
ax_legend.axis('off')  # 隐藏第二个子图的坐标轴
ax_legend.legend(handles=legend_patches, title='Column 14 Values', loc='center', fontsize=20, title_fontsize=18, borderpad=1, handletextpad=1.5)

# 保存图形到文件
output_file_path = 'pic/shapefile_overlay_cartopy_combined.png'
plt.savefig(output_file_path, dpi=300, bbox_inches='tight')

# 显示图形
plt.show()
