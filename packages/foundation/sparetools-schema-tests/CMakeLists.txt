cmake_minimum_required(VERSION 3.25)
project(sparetools-schema-tests VERSION 1.0.0 LANGUAGES CXX)

# Find required packages
find_package(sparetools-protocols REQUIRED)
find_package(GTest REQUIRED)
find_package(FlatBuffers REQUIRED)

# Enable testing
enable_testing()

# Create test executable
add_executable(schema_tests src/main.cpp)

# Link dependencies
target_link_libraries(schema_tests
    PRIVATE
        sparetools-protocols::common
        sparetools-protocols::iot
        sparetools-protocols::mcp
        GTest::gtest_main
        flatbuffers::flatbuffers
)

# Set C++ standard
target_compile_features(schema_tests PRIVATE cxx_std_17)

# Include directories
target_include_directories(schema_tests
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Add test to CTest
add_test(
    NAME schema_compatibility_tests
    COMMAND schema_tests
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
)

# Python test integration
find_package(Python3 COMPONENTS Interpreter)

if(Python3_FOUND)
    add_test(
        NAME python_schema_tests
        COMMAND Python3::Interpreter ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_schema_compatibility.py
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    )
endif()

# Install test executable
install(TARGETS schema_tests
    RUNTIME DESTINATION bin
    COMPONENT tests
)

# Install Python tests
install(DIRECTORY tests/
    DESTINATION tests
    FILES_MATCHING PATTERN "*.py"
)

# Install schema fixtures
install(DIRECTORY schema_fixtures/
    DESTINATION fixtures
    FILES_MATCHING PATTERN "*.fbs" PATTERN "*.json"
)