import json
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from shapely.geometry import shape
from matplotlib.patches import Wedge, Rectangle, Patch
import geopandas as gpd
# 从本地读取 GeoJSON 文件
with open('内蒙古自治区.json', 'r') as file:
    geojson_data = json.load(file)

# 计算 global_max_pl_value 函数
def calculate_global_max_pl_value(capitals):
    max_value = 0
    for capital in capitals:
        pl_values = list(capital['PL'].values())
        max_value = max(max_value, *pl_values)  # 更新最大值
    return max_value

# 创建绘图函数

# 设置等面积投影
equal_area_crs = ccrs.AlbersEqualArea(
    central_longitude=105,
    central_latitude=35,
    standard_parallels=(25, 47)
)
fig = plt.figure(figsize=(12, 6))

# 创建子图
ax = fig.add_subplot(1, 1, 1, projection=equal_area_crs)
ax.set_extent([95.0, 126.0, 35.8, 54.0], crs=ccrs.PlateCarree())
# 读取 Shapefile 数据
shp_file_path = 'shp/内蒙古自治区.shp'
gdf_shp = gpd.read_file(shp_file_path, encoding='GBK')
# 定义 Albers 投影坐标系

# 转换坐标系到自定义投影
if gdf_shp.crs != equal_area_crs:
    gdf_shp = gdf_shp.to_crs(equal_area_crs)
# 保存图像
# 保存图像
import matplotlib.patches as mpatches
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# 创建一个值到颜色的映射，指定每个分类的颜色 (原始饱和色)
original_color_mapping = {
    '草甸': 'purple',   # 紫色
    '草原': 'blue',     # 蓝色
    '草丛': 'yellow'    # 黄色
}
unique_values = gdf_shp.iloc[:, 10].unique()  # 这里假设第14列的索引为13

# 减少颜色的饱和度，返回不饱和的颜色
def desaturate_color(color, factor=0.5):
    # 将 RGB 颜色转换为 HSV
    hsv = mcolors.rgb_to_hsv(mcolors.to_rgb(color))
    # 减少饱和度
    hsv[1] *= factor
    # 将 HSV 转回 RGB
    return mcolors.hsv_to_rgb(hsv)

# 创建不饱和的颜色映射
desaturated_color_mapping = {key: desaturate_color(value, 0.5) for key, value in original_color_mapping.items()}

# 如果存在未映射的值，可以使用一个默认颜色
default_color = desaturate_color('gray', 0.5)

# 绘制多边形并根据分类设置不饱和颜色
for value in unique_values:
    # 根据条件过滤出当前值的数据
    subset = gdf_shp[gdf_shp.iloc[:, 10] == value]
    
    # 获取当前值的颜色（不饱和色），如果没有指定，则使用默认颜色
    facecolor = desaturated_color_mapping.get(str(value), default_color)
    
    # 绘制当前值的数据，设置不饱和颜色
    subset.plot(ax=ax, edgecolor='none', facecolor=facecolor, linewidth=2, alpha=0.5)

# 添加标题
plt.title('Shapefile Data Colored by Unique Values in Column 10 (Desaturated Colors)')

# 映射中文值到英文值的字典
label_mapping = {
    '草甸': 'Meadow',
    '草原': 'Grassland',
    '草丛': 'Shrubland'
}
# 创建图例并设置位置和字体大小
# 创建图例，按指定顺序显示英文标签
legend_patches = [
    mpatches.Patch(color=desaturated_color_mapping.get(key, default_color), label=label_mapping[key]) 
    for key in label_mapping.keys()
]

plt.legend(handles=legend_patches, title='Column 10 Values', loc='lower right', fontsize=10, title_fontsize=10, borderpad=1, handletextpad=1.5)


for feature in geojson_data['features']:
    if feature['geometry']['type'] == 'Polygon':
        polygon = shape(feature['geometry'])  # 创建 shapely 多边形对象
        ax.add_geometries([polygon], crs=ccrs.PlateCarree(), facecolor='none', edgecolor='gray', linewidth=2)
import matplotlib.ticker as mticker

gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, color="black")
gl.top_labels = False  # 关闭顶部经度标签
gl.right_labels = False  # 关闭右侧纬度标签gl.top_labels = False  # 关闭顶部经度标签
gl.right_labels = False  # 关闭右侧纬度标签
gl.xlocator = mticker.FixedLocator([100, 110, 120])  # 设置经度刻度
gl.ylocator = mticker.FixedLocator([40, 45, 50])  # 设置纬度刻度
gl.rotate_labels = False  # 不旋转标签
gl.xlines = False
gl.ylines = False
# 设置刻度标签的样式
gl.xlabel_style = {'rotation': 0}  # X轴刻度标签横向
gl.ylabel_style = {'rotation': 90}  # Y轴刻度标签竖向

# 设置标题
ax.set_title('neimeng site', fontsize=14)

def add_scale_bar(ax, location, length=0.1):
    # 绘制比例尺
    scale_bar = Rectangle(location, length, 0.005, color='black', transform=ax.transAxes)
    ax.add_patch(scale_bar)
    ax.text(location[0] + length / 2, location[1] + 0.02, '100 km', ha='center', va='bottom', transform=ax.transAxes)

add_scale_bar(ax, location=(0.05, 0.05), length=0.1)

inset_border = Rectangle(
    (0.16, 0.42),  # left and bottom position of the inset (matching the inset position)
    0.3,  # width of the inset
    0.5,  # height of the inset
    linewidth=2,
    edgecolor='black',
    facecolor='none',
    transform=fig.transFigure  # Use figure coordinates for the rectangle
)

# 在主图中添加边框
ax.add_patch(inset_border)


from matplotlib.patches import FancyArrowPatch
from geo_northarrow import add_north_arrow

add_north_arrow(ax, scale=0.5, xlim_pos=0.925, ylim_pos=0.9, color='#000', text_scaler=2, text_yT=-1.25)

# 从本地读取中国的 GeoJSON 文件
with open('中华人民共和国.json', 'r', encoding='utf-8') as file:  # 确保使用正确的中国地图文件名
    china_data = json.load(file)
# 添加中国地图的插图，定义插图的轴和投影
fig.subplots_adjust(left=0)  # 设置左边距为0

ax_china_inset = fig.add_axes([0.20, 0.42, 0.3, 0.5], projection=equal_area_crs)  # [left, bottom, width, height]
ax_china_inset.set_extent([80.0, 126.0, 0, 58.0], crs=ccrs.PlateCarree())

# 绘制中国所有几何形状


# 存储内蒙古的几何数据
inner_mongolia_geom = None

# 遍历中国数据的所有几何形状
for feature in china_data['features']:
    geom = shape(feature['geometry'])
    
    # 检查 feature 的属性，判断是否为内蒙古
    if '内蒙古自治区' in feature['properties']['name']:  # 假设属性中有 name 或类似的字段
        inner_mongolia_geom = geom  # 保存内蒙古的几何数据
    if  feature['properties']['name'] == '':  # 假设属性中有 name 或类似的字段
        ax_china_inset.add_geometries([geom], crs=ccrs.PlateCarree(), facecolor='none', edgecolor='black', linewidth=2)
    else:
        # 先绘制其他区域
        ax_china_inset.add_geometries([geom], crs=ccrs.PlateCarree(), facecolor='none', edgecolor='gray', linewidth=2)


# 最后绘制内蒙古的几何数据
if inner_mongolia_geom:
    ax_china_inset.add_geometries([inner_mongolia_geom], crs=ccrs.PlateCarree(), facecolor='none', edgecolor='red', linewidth=2)

ax_china_inset.axis('off')


add_scale_bar(ax_china_inset, location=(0.05, 0.05), length=0.1)

plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

plt.subplots_adjust(wspace=0, hspace=0)
# 保存图像
plt.savefig("data/neimeng.png")
plt.show()
