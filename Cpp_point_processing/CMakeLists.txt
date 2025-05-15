cmake_minimum_required(VERSION 3.10)

project(EPnPProject)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(${CMAKE_SOURCE_DIR})
include_directories(${CMAKE_SOURCE_DIR}/Eigen)

# Add executable
add_executable(EPnPMain main.cpp find_marker_points.cpp PoseUtil.cpp)

# Apply /bigobj for MSVC
if (MSVC)
    target_compile_options(EPnPMain PRIVATE /bigobj)
endif()
