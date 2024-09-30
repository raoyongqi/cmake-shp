#include <iostream>
#include <string>
#include <gdal.h>
#include <ogrsf_frmts.h>
#include <filesystem> // 用于检查和创建目录

namespace fs = std::filesystem; // 命名空间简化
#include <iostream>
#include <string>
#include <algorithm> // 用于 std::find_if_not
#include <cctype>    // 用于 std::isspace
#include "cpl_string.h" // Include necessary GDAL header

#include <filesystem>
#include <iostream>
#include <string>
#include <algorithm> // 用于 std::find_if_not
#include <cctype>    // 用于 std::isspace
#include <string>

static std::string trim(const std::string& str) {
    size_t start = 0;
    size_t end = str.size() - 1;

    while (start < str.size() && (str[start] == ' ' || str[start] == '\t' ||
        str[start] == '\n' || str[start] == '\r' ||
        str[start] == '\f' || str[start] == '\v')) {
        ++start;
    }

    if (start == str.size()) {
        return "";
    }

    while (end > start && (str[end] == ' ' || str[end] == '\t' ||
        str[end] == '\n' || str[end] == '\r' ||
        str[end] == '\f' || str[end] == '\v')) {
        --end;
    }

    return str.substr(start, end - start + 1);
}

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

//OGRFeatureDefn* poFDefn = poLayer->GetLayerDefn();
//for (int i = 0; i < poFDefn->GetFieldCount(); i++) {
//    OGRFieldDefn* poFieldDefn = poFDefn->GetFieldDefn(i);
//    std::string fieldName = poFieldDefn->GetNameRef();
//
//    // Create new field definition with original name
//    OGRFieldDefn newFieldDefn(fieldName.c_str(), poFieldDefn->GetType());
//    newFieldDefn.SetWidth(poFieldDefn->GetWidth());  // Set width to original width
//
//    newLayer->CreateField(&newFieldDefn);
//}
    const char* newFieldNames[] = {
        "AREA", "PERIMETER", "VEGETATION", "VEGETATI_1", "VEGE_ID",
        "Vegetation Community", "Vegetation Type Number", "Vegetation Type", "Vegetation Type Group Number",
        "Vegetation Type Group", "Major Vegetation Category", "VEGETATI_2", "VEGETATI_3",
        "VEGETATI_4", "VEGETATI_5", "geometry"
    };
const int numFields = sizeof(newFieldNames) / sizeof(newFieldNames[0]);

// Create new fields in the new layer
for (int i = 0; i < numFields; i++) {
    OGRFieldDefn newFieldDefn(newFieldNames[i], OFTString);
    if (newLayer->CreateField(&newFieldDefn) != OGRERR_NONE) {
        std::cerr << "Error creating field: " << newFieldNames[i] << std::endl;
    }
}

// 遍历图层中的每个要素
OGRFeature* poFeature;
poLayer->ResetReading();
int count = 0;



while ((poFeature = poLayer->GetNextFeature()) != NULL) {
    OGRGeometry* poGeometry = poFeature->GetGeometryRef();
    if (poGeometry != nullptr && wkbFlatten(poGeometry->getGeometryType()) == wkbPolygon) {
        std::string fieldValue = poFeature->GetFieldAsString(10); // 假设是第10个字段
        const char* utf8FieldValue = CPLRecode(fieldValue.c_str(), "GBK", "UTF-8");
        fieldValue = trim(utf8FieldValue);
        OGRFeature* newFeature = OGRFeature::CreateFeature(newLayer->GetLayerDefn());
        if (fieldValue == "草甸" || fieldValue == "草原" || fieldValue == "草丛") {
            //            // 创建新要素并设置几何形状和属性
            OGRFeature* newFeature = OGRFeature::CreateFeature(newLayer->GetLayerDefn());
            newFeature->SetGeometry(poGeometry);
            for (int i = 0; i < numFields; i++) {
                std::string originalFieldValue = poFeature->GetFieldAsString(i);
                const char* utf8FieldValue = CPLRecode(originalFieldValue.c_str(), "Windows-1252", "UTF-8");

                // 确保转换成功
                newFeature->SetField(i, utf8FieldValue); // Set the UTF-8 field value
            }
        
        if (newLayer->CreateFeature(newFeature) != OGRERR_NONE) {
            std::cerr << "Error creating feature in new layer." << std::endl;
        }
            OGRFeature::DestroyFeature(newFeature); // Clean up
        }
        count++;
    }

    
    OGRFeature::DestroyFeature(poFeature); // Clean up original feature
}

    OGRFeature::DestroyFeature(poFeature);
    // 关闭 Shapefile
    GDALClose(poDS);
    GDALClose(newShpDS);

    std::cout << "过滤并写入了 " << count << " 个要素" << std::endl;
    return 0;
}
