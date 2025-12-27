# Gamepad Mapper Tests CMakeLists.txt

# Find GTest
find_package(GTest REQUIRED)

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/include)
include_directories(${CMAKE_BINARY_DIR}/include)

# Test sources
set(TEST_SOURCES
    test_gamepad_mapper.cpp
    test_controller_manager.cpp
)

# Create test executable
add_executable(gamepad_mapper_tests ${TEST_SOURCES})

# Link libraries
target_link_libraries(gamepad_mapper_tests
    PRIVATE
    gamepad_mapper
    GTest::gtest_main
)

# Add test
add_test(NAME gamepad_mapper_unit_tests COMMAND gamepad_mapper_tests)