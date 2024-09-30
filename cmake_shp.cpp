#include <iostream>
#include <string>
#include <gdal.h>
#include <ogrsf_frmts.h>
#include <filesystem> // 用于检查和创建目录

namespace fs = std::filesystem; // 命名空间简化


int main() {
    // 设置 PROJ 搜索路径
    std::string path = "C:/Users/r/Desktop/cmake/cmake_shp/build/vcpkg_installed/x64-windows/share/proj";
    const char* proj_path[] = { path.c_str(), nullptr };
    OSRSetPROJSearchPaths(proj_path);

    // 初始化 GDAL
    GDALAllRegister();
    const char* outputDir = "shp/new";
    if (!fs::exists(outputDir)) {
        if (!fs::create_directories(outputDir)) {
            std::cerr << "无法创建目录: " << outputDir << std::endl;
            return 1;
        }
    }
    // 打开 Shapefile
    const char* shpFilePath = "C:/Users/r/Desktop/go-shp/shp/vegetation_china.shp";
    GDALDataset* poDS = (GDALDataset*)GDALOpenEx(shpFilePath, GDAL_OF_VECTOR, NULL, NULL, NULL);
    if (poDS == NULL) {
        std::cerr << "无法打开 Shapefile: " << shpFilePath << std::endl;
        return 1;
    }

    // 获取图层
    OGRLayer* poLayer = poDS->GetLayer(0);
    if (poLayer == NULL) {
        std::cerr << "无法获取图层" << std::endl;
        GDALClose(poDS);
        return 1;
    }

    // 创建新的 Shapefile 和图层
    GDALDriver* poDriver = GetGDALDriverManager()->GetDriverByName("ESRI Shapefile");
    GDALDataset* newShpDS = poDriver->Create("shp/new/filtered.shp", 0, 0, 0, GDT_Unknown, NULL);
    if (newShpDS == NULL) {
        std::cerr << "无法创建新的 Shapefile" << std::endl;
        GDALClose(poDS);
        return 1;
    }

    OGRLayer* newLayer = newShpDS->CreateLayer("filtered", NULL, wkbPolygon, NULL);
    if (newLayer == NULL) {
        std::cerr << "无法创建新的图层" << std::endl;
        GDALClose(poDS);
        GDALClose(newShpDS);
        return 1;
    }

    // 复制字段结构
    OGRFeatureDefn* poFDefn = poLayer->GetLayerDefn();
    for (int i = 0; i < poFDefn->GetFieldCount(); i++) {
        OGRFieldDefn* poFieldDefn = poFDefn->GetFieldDefn(i);
        std::string fieldName = poFieldDefn->GetNameRef();

        // 替换中文字段名为英文名
        if (fieldName == "植被群系和") fieldName = "Vegetation_Type";
        else if (fieldName == "植被型编号") fieldName = "Vegetation_ID";
        else if (fieldName == "植被型") fieldName = "Vegetation_Type_Name";
        else if (fieldName == "植被型组编") fieldName = "Vegetation_Group_Code";
        else if (fieldName == "植被型组") fieldName = "Vegetation_Group";
        else if (fieldName == "植被大类") fieldName = "Vegetation_Category";

        OGRFieldDefn newFieldDefn(fieldName.c_str(), poFieldDefn->GetType());
        newLayer->CreateField(&newFieldDefn);
    }

    // 遍历图层中的每个要素
    OGRFeature* poFeature;
    poLayer->ResetReading();
    int count = 0;

    while ((poFeature = poLayer->GetNextFeature()) != NULL) {
        OGRGeometry* poGeometry = poFeature->GetGeometryRef();
        if (poGeometry != NULL && wkbFlatten(poGeometry->getGeometryType()) == wkbPolygon) {
            // 创建新要素并设置几何形状和属性
            OGRFeature* newFeature = OGRFeature::CreateFeature(newLayer->GetLayerDefn());
            newFeature->SetGeometry(poGeometry);

            // 设置字段值
            for (int i = 0; i < poFDefn->GetFieldCount(); i++) {
                // 确保字段存在再访问
                if (poFeature->IsFieldSet(i)) {
                    newFeature->SetField(i, poFeature->GetFieldAsString(i));
                }
            }

            newLayer->CreateFeature(newFeature);
            OGRFeature::DestroyFeature(newFeature);
            count++;
        }

        OGRFeature::DestroyFeature(poFeature);
    }

    // 关闭 Shapefile
    GDALClose(poDS);
    GDALClose(newShpDS);

    std::cout << "过滤并写入了 " << count << " 个要素" << std::endl;
    return 0;
}
