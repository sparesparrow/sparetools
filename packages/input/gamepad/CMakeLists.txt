cmake_minimum_required(VERSION 3.20)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Check if we're using Conan toolchain
if(EXISTS "${CMAKE_TOOLCHAIN_FILE}")
    message(STATUS "Using Conan toolchain: ${CMAKE_TOOLCHAIN_FILE}")
endif()

project(GamepadCore VERSION 1.0.0 LANGUAGES CXX)

# Add Conan-generated files to paths
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_BINARY_DIR}")

# Find required packages
find_package(nlohmann_json REQUIRED)

# Include directories
include_directories(include)
include_directories(${CMAKE_BINARY_DIR}/include)

# Source files
set(CORE_SOURCES
    src/gamepad_mapper.cpp
    src/controller_manager.cpp
    src/multi_controller_manager.cpp
)

# Create library
add_library(gamepad_core ${CORE_SOURCES})

# Link libraries
target_link_libraries(gamepad_core PRIVATE nlohmann_json::nlohmann_json)

# Set include directories for the library
target_include_directories(gamepad_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# Install targets
install(TARGETS gamepad_core
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(DIRECTORY include/ DESTINATION include)

# Testing (optional)
option(BUILD_TESTS "Build tests" OFF)
if(BUILD_TESTS)
    enable_testing()
    find_package(GTest REQUIRED)
    add_subdirectory(tests)
endif()

# Documentation
find_package(Doxygen)
if(DOXYGEN_FOUND)
    set(DOXYGEN_INPUT_DIR ${CMAKE_CURRENT_SOURCE_DIR})
    set(DOXYGEN_OUTPUT_DIR ${CMAKE_CURRENT_BINARY_DIR}/docs)
    configure_file(${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile @ONLY)
    add_custom_target(docs
        COMMAND ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Generating API documentation with Doxygen"
    )
endif()