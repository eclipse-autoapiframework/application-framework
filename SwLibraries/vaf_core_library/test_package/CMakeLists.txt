cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(vafcpp CONFIG REQUIRED)
find_package(Threads)

add_executable(example src/example.cpp)
target_link_libraries(example vafcpp::vaf_core)
