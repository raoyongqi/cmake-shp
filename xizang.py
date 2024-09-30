import json
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
from shapely.geometry import shape

# 读取中国地图数据
with open('中华人民共和国.json', 'r', encoding='utf-8') as file:
    china_data = json.load(file)

# 读取 Shapefile 数据
shp_file_path = 'shp/xizang.shp'
gdf_shp = gpd.read_file(shp_file_path, encoding='GBK')

# 读取 GeoJSON 数据
geojson_file_path = '西藏自治区.json'
gdf_geojson = gpd.read_file(geojson_file_path)

# 定义 Albers 投影坐标系
albers_proj = ccrs.AlbersEqualArea(
    central_longitude=105,
    central_latitude=35,
    standard_parallels=(25, 47)
)

# 创建绘图对象，3个子图横向排列
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(36, 12), subplot_kw={'projection': albers_proj}, gridspec_kw={'wspace': 0.1})

# 设置左边距
fig.subplots_adjust(left=0.1)

# 绘制中国所有几何形状
ax_china_inset = axes[0]  # 插图轴
ax_china_inset.set_extent([80.0, 126.0, 0, 56.0], crs=ccrs.PlateCarree())

# 绘制中国地图的几何形状
# 遍历中国数据的所有几何形状
for feature in china_data['features']:
    geom = shape(feature['geometry'])
    
    # 检查 feature 的属性，判断是否为内蒙古
    if '西藏自治区' in feature['properties']['name']:  # 假设属性中有 name 或类似的字段
        inner_mongolia_geom = geom  # 保存内蒙古的几何数据
    if  feature['properties']['name'] is '':  # 假设属性中有 name 或类似的字段
        ax_china_inset.add_geometries([geom], crs=ccrs.PlateCarree(), facecolor='none', edgecolor='black', linewidth=2)
    else:
        # 先绘制其他区域
        ax_china_inset.add_geometries([geom], crs=ccrs.PlateCarree(), facecolor='none', edgecolor='gray', linewidth=2)
        # print(feature['properties']['name'])
if inner_mongolia_geom:
    ax_china_inset.add_geometries([inner_mongolia_geom], crs=ccrs.PlateCarree(), facecolor='none', edgecolor='red', linewidth=2)




ax_china_inset.set_title('china')
ax_china_inset.axis('off')  # 隐藏坐标轴

# 绘制转换后的 GeoJSON 数据
ax_map = axes[1]  # 主图轴


# 转换坐标系到自定义投影
if gdf_shp.crs != albers_proj:
    gdf_shp = gdf_shp.to_crs(albers_proj)
if gdf_geojson.crs != albers_proj:
    gdf_geojson = gdf_geojson.to_crs(albers_proj)

# 获取第14列的唯一值
unique_values = gdf_shp.iloc[:, 13].unique()  # 这里假设第14列的索引为13

# 创建中文到英文的映射字典
label_mapping = {
    None: '', 
    'None': 'Other grassland',
}

# 创建一个颜色映射
cmap = plt.get_cmap('viridis', len(unique_values))  # 使用viridis colormap

# 为每个多边形绘制不同的颜色
for i, value in enumerate(unique_values):
    subset = gdf_shp[gdf_shp.iloc[:, 13] == value]
    subset.plot(ax=ax_map, edgecolor='none', facecolor=cmap(i / len(unique_values)), linewidth=2, alpha=0.5)
gdf_geojson.plot(ax=ax_map, edgecolor='black', facecolor='none', alpha=1, label='GeoJSON Data')
# 添加标题和坐标轴标签
ax_map.set_title('Shapefile Data Colored by Unique Values in Column 14')
ax_map.set_xlabel('Easting (meters)')
ax_map.set_ylabel('Northing (meters)')

# 添加经纬度网格线
gridlines = ax_map.gridlines(draw_labels=True, color='gray', linestyle='--', alpha=0.5)
gridlines.xlabel_style = {'size': 10}
gridlines.ylabel_style = {'size': 10}
gridlines.top_labels = False
gridlines.right_labels = False

# 创建图例并设置位置和字体大小
ax_legend = axes[2]  # 图例轴
ax_legend.axis('off')  # 隐藏坐标轴
legend_patches = [
    mpatches.Patch(color=cmap(i / len(unique_values)), label=label_mapping.get(str(value), str(value))) 
    for i, value in enumerate(unique_values)
]
ax_legend.legend(handles=legend_patches, title='Column 14 Values', loc='center', fontsize=20, title_fontsize=18, borderpad=1, handletextpad=1.5)

# 保存图形到文件
output_file_path = 'pic/shapefile_overlay_cartopy_combined.png'
plt.savefig(output_file_path, dpi=300, bbox_inches='tight')

# 显示图形
plt.show()
