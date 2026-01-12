# CMakeLists.txt for SpareTools BPM Detector Consumer Package
#
# This CMakeLists.txt is designed for host-based unit testing and development.
# For ESP32 firmware building, use PlatformIO (platformio.ini).
#
# Following OMS pattern: separate build systems for different environments.

cmake_minimum_required(VERSION 3.20)
project(sparetools-bpm-detector VERSION 0.1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include Conan-generated files
include(${CMAKE_BINARY_DIR}/conan_toolchain.cmake)
include(${CMAKE_BINARY_DIR}/conandeps_legacy.cmake)

# Find required packages
find_package(sparetools-protocols REQUIRED)
find_package(GTest REQUIRED)

# Enable testing
enable_testing()

# Define source files for unit testing
# These would be platform-agnostic versions of the ESP32 code
set(TEST_SOURCES
    # Mock implementations for testing
    src/bpm_detector_mock.cpp
    src/audio_input_mock.cpp
    test/test_bpm_detector.cpp
    test/test_audio_processing.cpp
)

# Create test executable
add_executable(bpm_detector_tests ${TEST_SOURCES})

# Link dependencies
target_link_libraries(bpm_detector_tests
    PRIVATE
        sparetools-protocols::bpm
        GTest::gtest_main
)

# Include directories
target_include_directories(bpm_detector_tests
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Register tests
add_test(NAME bpm_detector_unit_tests COMMAND bpm_detector_tests)

# Install test harness scripts
install(DIRECTORY scripts/
    DESTINATION bin
    FILES_MATCHING PATTERN "*.py"
)

install(DIRECTORY tests/
    DESTINATION test
    FILES_MATCHING PATTERN "*.py"
)