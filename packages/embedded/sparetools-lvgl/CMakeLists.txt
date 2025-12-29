cmake_minimum_required(VERSION 3.16)

project(lvgl VERSION 8.3.11 LANGUAGES C CXX)

# Set C standard
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# LVGL source files
file(GLOB LVGL_SOURCES
    "src/*.c"
    "src/core/*.c"
    "src/draw/*.c"
    "src/draw/sw/*.c"
    "src/font/*.c"
    "src/hal/*.c"
    "src/misc/*.c"
    "src/widgets/*.c"
    "src/extra/*.c"
    "src/extra/layouts/*.c"
    "src/extra/layouts/flex/*.c"
    "src/extra/layouts/grid/*.c"
    "src/extra/themes/*.c"
    "src/extra/themes/basic/*.c"
    "src/extra/widgets/*.c"
    "src/extra/widgets/animimg/*.c"
    "src/extra/widgets/calendar/*.c"
    "src/extra/widgets/chart/*.c"
    "src/extra/widgets/colorwheel/*.c"
    "src/extra/widgets/imgbtn/*.c"
    "src/extra/widgets/keyboard/*.c"
    "src/extra/widgets/led/*.c"
    "src/extra/widgets/list/*.c"
    "src/extra/widgets/menu/*.c"
    "src/extra/widgets/meter/*.c"
    "src/extra/widgets/msgbox/*.c"
    "src/extra/widgets/span/*.c"
    "src/extra/widgets/spinbox/*.c"
    "src/extra/widgets/spinner/*.c"
    "src/extra/widgets/tabview/*.c"
    "src/extra/widgets/tileview/*.c"
    "src/extra/widgets/win/*.c"
)

# Create LVGL library
add_library(lvgl ${LVGL_SOURCES})

# Define LV_CONF_INCLUDE_SIMPLE to use #include "lv_conf.h"
target_compile_definitions(lvgl PUBLIC LV_CONF_INCLUDE_SIMPLE)

# Include directories
target_include_directories(lvgl
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# Compiler options for embedded systems
if(CMAKE_SYSTEM_NAME STREQUAL "Generic" OR CMAKE_SYSTEM_NAME MATCHES ".*RTOS.*")
    target_compile_options(lvgl PRIVATE
        -Wno-unused-parameter
        -Wno-missing-field-initializers
        -Wno-unused-function
        -Wno-unused-variable
    )
endif()

# Install library
install(TARGETS lvgl
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

# Install headers
install(DIRECTORY src/
    DESTINATION include/lvgl
    FILES_MATCHING PATTERN "*.h"
)

# Version information
set_target_properties(lvgl PROPERTIES
    VERSION 8.3.11
    SOVERSION 8
)