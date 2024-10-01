import geopandas as gpd
import os

# 加载 Shapefile
shp_data = gpd.read_file('build/shp/new/filtered.shp', encoding='GBK')

# 输出 Shapefile 的 CRS 信息
print("Shapefile CRS:", shp_data.crs)

# 指定存放 GeoJSON 文件的目录
geojson_dir = 'geojson'  # 替换为实际的目录

# 指定输出 Shapefile 的目录
output_dir = 'shp'
# 如果输出目录不存在，创建它
os.makedirs(output_dir, exist_ok=True)

# 循环遍历 GeoJSON 文件
for geojson_file in os.listdir(geojson_dir):
    if geojson_file.endswith('.json'):
        # 加载 GeoJSON 数据
        geojson_path = os.path.join(geojson_dir, geojson_file)
        geojson_data = gpd.read_file(geojson_path)

        # 输出 GeoJSON 的 CRS 信息
        print(f"Processing {geojson_file}, CRS: {geojson_data.crs}")

        # 如果 CRS 不同，转换 GeoJSON CRS 为 Shapefile 的 CRS
        if shp_data.crs != geojson_data.crs:
            geojson_data = geojson_data.to_crs(shp_data.crs)

        # 检查是否有重叠
        if shp_data.intersects(geojson_data.unary_union).any():
            # 进行裁剪
            clipped_data = gpd.clip(shp_data, geojson_data)
            
            # 检查裁剪结果是否为空
            if clipped_data.empty:
                print(f"{geojson_file} 裁剪后的数据为空，没有找到重叠区域。")
            else:
                # 保存裁剪后的数据，使用 GeoJSON 文件名作为输出文件名
                output_path = os.path.join(output_dir, f"{geojson_file.replace('.json', '.shp')}")
                clipped_data.to_file(output_path, encoding='GBK')  # 指定保存时的编码为 GBK
                print(f"{geojson_file} 裁剪后的数据已保存到 '{output_path}'")
        else:
            print(f"{geojson_file} 没有重叠区域，无法进行裁剪。")
