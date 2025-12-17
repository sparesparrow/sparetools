# Test configuration
find_package(GTest REQUIRED)

# Test executable
add_executable(${PROJECT_NAME}_tests
    test_{{project_name}}.cpp
)

target_link_libraries(${PROJECT_NAME}_tests
    PRIVATE
        ${PROJECT_NAME}
        GTest::gtest_main
)

# Register tests
include(GoogleTest)
gtest_discover_tests(${PROJECT_NAME}_tests)