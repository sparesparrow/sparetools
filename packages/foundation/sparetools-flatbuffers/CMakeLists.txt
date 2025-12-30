cmake_minimum_required(VERSION 3.25)
project(sparetools-flatbuffers VERSION 24.3.25 LANGUAGES CXX)

# This CMakeLists.txt is primarily for building FlatBuffers from source
# if the Conan package is not available. The main purpose of this package
# is to provide the flatc compiler tool.

# Find or build FlatBuffers
find_package(FlatBuffers QUIET)

if(NOT FlatBuffers_FOUND)
    message(STATUS "FlatBuffers not found, building from source...")

    # Download and build FlatBuffers
    include(FetchContent)
    FetchContent_Declare(
        flatbuffers
        URL https://github.com/google/flatbuffers/archive/refs/tags/v24.3.25.tar.gz
        URL_HASH SHA256=1b6cff1d0e1a6e66dde2c8ef72b5abfb6a6e2bd9b7e24f170ba4dbdb6e2a1fbcfb
    )
    FetchContent_MakeAvailable(flatbuffers)

    # Build flatc compiler
    add_subdirectory(${flatbuffers_SOURCE_DIR} ${flatbuffers_BINARY_DIR})
else()
    message(STATUS "Using system FlatBuffers")
endif()

# Installation - primarily for flatc binary
if(TARGET flatc)
    install(TARGETS flatc
        RUNTIME DESTINATION bin
        COMPONENT tools)
endif()