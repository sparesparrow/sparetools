cmake_minimum_required(VERSION 3.20)
project(WiFiSensing VERSION 1.0.0 LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find Conan dependencies
find_package(Eigen3 REQUIRED)
find_package(Boost REQUIRED COMPONENTS system filesystem)
find_package(FFTW3 REQUIRED)
find_package(OpenCV REQUIRED)
find_package(HDF5 REQUIRED)
find_package(yaml-cpp REQUIRED)

# Optional Qt GUI
find_package(Qt6 QUIET COMPONENTS Widgets Charts DataVisualization)
if(Qt6_FOUND)
    set(QT_AVAILABLE TRUE)
endif()

# Include directories
include_directories(include)
include_directories(${CMAKE_BINARY_DIR})

# Core library
add_library(wifi_sensing_core
    src/core/motion_detector.cpp
    src/core/csi_processor.cpp
    src/core/signal_analyzer.cpp
    include/wifi_sensing/core/motion_detector.hpp
    include/wifi_sensing/core/csi_processor.hpp
    include/wifi_sensing/core/signal_analyzer.hpp
)

target_link_libraries(wifi_sensing_core
    PUBLIC
        Eigen3::Eigen3
        Boost::system
        Boost::filesystem
        FFTW3::fftw3
        OpenCV::core
        OpenCV::imgproc
        HDF5::HDF5
        yaml-cpp::yaml-cpp
)

target_include_directories(wifi_sensing_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# CSI processing library
add_library(csi_processor
    src/analysis/csi_analyzer.cpp
    src/analysis/activity_classifier.cpp
    include/wifi_sensing/analysis/csi_analyzer.hpp
    include/wifi_sensing/analysis/activity_classifier.hpp
)

target_link_libraries(csi_processor
    PUBLIC
        wifi_sensing_core
        Eigen3::Eigen3
        Boost::system
)

# Signal analysis library
add_library(signal_analyzer
    src/analysis/signal_processor.cpp
    src/analysis/frequency_analyzer.cpp
    include/wifi_sensing/analysis/signal_processor.hpp
    include/wifi_sensing/analysis/frequency_analyzer.hpp
)

target_link_libraries(signal_analyzer
    PUBLIC
        wifi_sensing_core
        FFTW3::fftw3
        Eigen3::Eigen3
)

# CLI executable
add_executable(wifi_sensing_cli
    src/tools/wifi_scanner.cpp
    src/tools/csi_collector.cpp
    src/main.cpp
)

target_link_libraries(wifi_sensing_cli
    PRIVATE
        wifi_sensing_core
        csi_processor
        signal_analyzer
)

# CSI analyzer executable
add_executable(csi_analyzer
    src/tools/csi_analyzer_main.cpp
)

target_link_libraries(csi_analyzer
    PRIVATE
        csi_processor
        signal_analyzer
)

# GUI application (if Qt is available)
if(QT_AVAILABLE AND BUILD_GUI)
    add_executable(wifi_sensing_gui
        src/visualization/main_window.cpp
        src/visualization/csi_plotter.cpp
        src/visualization/signal_visualizer.cpp
    )

    target_link_libraries(wifi_sensing_gui
        PRIVATE
            wifi_sensing_core
            csi_processor
            signal_analyzer
            Qt6::Widgets
            Qt6::Charts
            Qt6::DataVisualization
    )
endif()

# Python bindings (optional)
option(BUILD_PYTHON_BINDINGS "Build Python bindings" OFF)
if(BUILD_PYTHON_BINDINGS)
    find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
    find_package(pybind11 REQUIRED)

    pybind11_add_module(wifi_sensing_py
        src/python_bindings/core_bindings.cpp
        src/python_bindings/analysis_bindings.cpp
    )

    target_link_libraries(wifi_sensing_py
        PRIVATE
            wifi_sensing_core
            csi_processor
            signal_analyzer
    )
endif()

# Tests
enable_testing()

add_executable(test_core tests/test_motion_detector.cpp)
target_link_libraries(test_core PRIVATE wifi_sensing_core)
add_test(NAME test_core COMMAND test_core)

add_executable(test_csi tests/test_csi_processor.cpp)
target_link_libraries(test_csi PRIVATE csi_processor)
add_test(NAME test_csi COMMAND test_csi)

add_executable(test_signal tests/test_signal_analyzer.cpp)
target_link_libraries(test_signal PRIVATE signal_analyzer)
add_test(NAME test_signal COMMAND test_signal)

# Installation
install(TARGETS wifi_sensing_core csi_processor signal_analyzer
    EXPORT WiFiSensingTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(TARGETS wifi_sensing_cli csi_analyzer
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/
    DESTINATION include
    FILES_MATCHING PATTERN "*.hpp" PATTERN "*.h"
)

install(EXPORT WiFiSensingTargets
    FILE WiFiSensingTargets.cmake
    NAMESPACE WiFiSensing::
    DESTINATION lib/cmake/WiFiSensing
)

include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/WiFiSensingConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/WiFiSensingConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/WiFiSensingConfig.cmake"
    INSTALL_DESTINATION lib/cmake/WiFiSensing
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/WiFiSensingConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/WiFiSensingConfigVersion.cmake"
    DESTINATION lib/cmake/WiFiSensing
)

# Build options
option(BUILD_SHARED_LIBS "Build shared libraries" ON)
option(BUILD_GUI "Build GUI applications" OFF)
option(BUILD_PYTHON_BINDINGS "Build Python bindings" OFF)
option(BUILD_TESTS "Build tests" ON)

if(BUILD_TESTS)
    enable_testing()
endif()