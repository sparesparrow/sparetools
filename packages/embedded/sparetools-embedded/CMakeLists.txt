cmake_minimum_required(VERSION 3.15)
project(sparetools-embedded VERSION 1.0.0 LANGUAGES C CXX)

# Create the embedded utilities library
add_library(sparetools-embedded
    src/ring_buffer.c
    src/timer.c
    src/display.cpp
)

# Include directories
target_include_directories(sparetools-embedded
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# Set C standard
set_target_properties(sparetools-embedded PROPERTIES
    C_STANDARD 99
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
)

# Set CXX standard
set_target_properties(sparetools-embedded PROPERTIES
    CXX_STANDARD 11
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)

# Installation
install(TARGETS sparetools-embedded
    EXPORT sparetools-embedded-targets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(DIRECTORY include/
    DESTINATION include
    FILES_MATCHING PATTERN "*.h" PATTERN "*.hpp"
)

install(EXPORT sparetools-embedded-targets
    FILE sparetools-embedded-targets.cmake
    NAMESPACE sparetools-embedded::
    DESTINATION lib/cmake/sparetools-embedded
)