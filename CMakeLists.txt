# CMakeList.txt: cmake_shp 的 CMake 项目，在此处包括源代码并定义
# 项目特定的逻辑。
#
cmake_minimum_required (VERSION 3.8)

# 如果支持，请为 MSVC 编译器启用热重载。
if (POLICY CMP0141)
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()

project ("cmake_shp")

find_package(fmt CONFIG REQUIRED)

# 将源代码添加到此项目的可执行文件。
add_executable (cmake_shp "cmake_shp.cpp" "cmake_shp.h")

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET cmake_shp PROPERTY CXX_STANDARD 20)
endif()

# TODO: 如有需要，请添加测试并安装目标。


target_link_libraries(cmake_shp PRIVATE fmt::fmt)
find_package(GDAL REQUIRED)
if(GDAL_FOUND)
    target_include_directories(${PROJECT_NAME} PRIVATE ${GDAL_INCLUDE_DIR})
    target_link_libraries(cmake_shp PRIVATE GDAL::GDAL)

else(GDAL_FOUND)
    message( FATAL_ERROR "GDAL library not found" )
endif(GDAL_FOUND)