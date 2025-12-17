cmake_minimum_required(VERSION 3.15)
project({{project_name}}TestPackage LANGUAGES CXX)

find_package({{class_name}} REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE {{class_name}}::{{class_name}})