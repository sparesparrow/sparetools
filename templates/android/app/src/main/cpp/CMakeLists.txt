cmake_minimum_required(VERSION 3.18.1)

project("{{project_name}}-native")

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Conan dependencies
find_package(sparetools-openssl REQUIRED)
find_package(sparetools-base REQUIRED)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# Source files
add_library(native-lib SHARED
    native-lib.cpp
)

# Link libraries
target_link_libraries(native-lib
    sparetools-openssl::sparetools-openssl
    sparetools-base::sparetools-base
    android
    log
)

# Compiler options
target_compile_options(native-lib PRIVATE
    -Wall
    -Wextra
    -Wpedantic
    -fexceptions
    -frtti
)

# Build tests if available
if(BUILD_TESTING)
    enable_testing()

    add_executable(native-tests
        test/native-lib-test.cpp
    )

    target_link_libraries(native-tests
        native-lib
        gtest_main
    )

    add_test(NAME native-tests COMMAND native-tests)
endif()