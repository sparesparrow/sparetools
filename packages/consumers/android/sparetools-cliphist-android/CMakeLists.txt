cmake_minimum_required(VERSION 3.18.1)

project("cliphist")

# SQLCipher native library
add_library(sqlcipher SHARED IMPORTED)
set_target_properties(sqlcipher PROPERTIES IMPORTED_LOCATION
    ${CMAKE_SOURCE_DIR}/../sqlcipher/libs/${ANDROID_ABI}/libsqlcipher.so)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/src/main/cpp)

# Native library for ClipHist
add_library(cliphist_native SHARED
    src/main/cpp/native-lib.cpp)

# Link libraries
target_link_libraries(cliphist_native
    sqlcipher
    android
    log)