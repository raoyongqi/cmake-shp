import geopandas as gpd
import os
import zipfile

# 加载 Shapefile
shp_data = gpd.read_file('build/shp/new/filtered.shp', encoding='GBK')

# 输出 Shapefile 的 CRS 信息
print("Shapefile CRS:", shp_data.crs)

# 指定存放 GeoJSON 文件的目录
geojson_dir = 'geojson'  # 替换为实际的目录

# 指定输出 Shapefile 的目录

# 指定压缩文件存放的目录
zip_dir = 'zip'  # 替换为实际的目录
os.makedirs(zip_dir, exist_ok=True)  # 如果输出目录不存在，创建它

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
                output_basename = geojson_file.replace('.json', '')
                shp_output_path = os.path.join(zip_dir, f"{output_basename}.shp")
                clipped_data.to_file(shp_output_path, encoding='GBK')  # 指定保存时的编码为 GBK
                print(f"{geojson_file} 裁剪后的数据已保存到 '{shp_output_path}'")

                # 打包 Shapefile 为 .zip
                zip_output_path = os.path.join(zip_dir, f"{output_basename}.zip")  # 更新为 zip 目录
                with zipfile.ZipFile(zip_output_path, 'w') as zipf:
                    for ext in ['.shp', '.shx', '.dbf', '.prj']:
                        filepath = os.path.join(zip_dir, f"{output_basename}{ext}")
                        if os.path.exists(filepath):
                            zipf.write(filepath, os.path.basename(filepath))
                
                print(f"{geojson_file} 裁剪后的 Shapefile 已打包为 '{zip_output_path}'")

                # 删除中间生成的文件
                for ext in ['.shp', '.shx', '.dbf', '.prj','.cpg']:
                    os.remove(os.path.join(zip_dir, f"{output_basename}{ext}"))
                print(f"{geojson_file} 的中间文件已删除。")
        else:
            print(f"{geojson_file} 没有重叠区域，无法进行裁剪。")
