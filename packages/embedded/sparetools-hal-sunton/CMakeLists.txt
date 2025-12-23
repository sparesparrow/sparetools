cmake_minimum_required(VERSION 3.16)

project(sparetools-hal-sunton VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Include directories
include_directories(include)

# Source files
set(SOURCES
    src/display.cpp
)

# Header files
set(HEADERS
    include/hal/sunton/display.h
    src/pin_mapping.h
)

# Create library
add_library(${PROJECT_NAME} ${SOURCES} ${HEADERS})

# Set library properties
set_target_properties(${PROJECT_NAME} PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
    PUBLIC_HEADER "${HEADERS}"
)

# Install library
install(TARGETS ${PROJECT_NAME}
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    PUBLIC_HEADER DESTINATION include/hal/sunton
)

# Install header files
install(DIRECTORY include/ DESTINATION include)

# Optional lvgl integration
if(WITH_LVGL)
    find_package(lvgl REQUIRED)
    target_link_libraries(${PROJECT_NAME} PUBLIC lvgl::lvgl)
    target_compile_definitions(${PROJECT_NAME} PUBLIC WITH_LVGL)
endif()

# Touch support option
if(WITH_TOUCH)
    target_compile_definitions(${PROJECT_NAME} PUBLIC WITH_TOUCH)
endif()