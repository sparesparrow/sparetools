cmake_minimum_required(VERSION 3.20)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Check if we're using Conan toolchain
if(EXISTS "${CMAKE_TOOLCHAIN_FILE}")
    message(STATUS "Using Conan toolchain: ${CMAKE_TOOLCHAIN_FILE}")
endif()

project(InputBackends VERSION 1.0.0 LANGUAGES CXX)

# Add Conan-generated files to paths
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_BINARY_DIR}")

# Options for backend selection
option(WITH_X11 "Enable X11 backend" ON)
option(WITH_WAYLAND "Enable Wayland backend" ON)
option(WITH_KDE "Enable KDE backend" ON)
option(WITH_SDL2 "Enable SDL2 backend" ON)
option(WITH_UINPUT "Enable UInput backend" ON)

# Find required packages
find_package(PkgConfig REQUIRED)

# Backend-specific package detection
if(WITH_X11)
    pkg_check_modules(X11 REQUIRED x11 xtst)
endif()

if(WITH_WAYLAND)
    pkg_check_modules(WAYLAND REQUIRED wayland-client wayland-protocols)
endif()

if(WITH_SDL2)
    pkg_check_modules(SDL2 REQUIRED sdl2)
endif()

# Include directories
include_directories(include)
include_directories(${CMAKE_BINARY_DIR}/include)

# Core source files
set(CORE_SOURCES
    src/input_backend_manager.cpp
)

# Add backend sources conditionally
set(BACKEND_SOURCES)

if(WITH_X11)
    list(APPEND BACKEND_SOURCES src/backends/x11_simulator.cpp)
endif()

if(WITH_WAYLAND)
    list(APPEND BACKEND_SOURCES src/backends/wayland_simulator.cpp)
endif()

if(WITH_KDE)
    list(APPEND BACKEND_SOURCES src/backends/kde_simulator.cpp)
endif()

if(WITH_SDL2)
    list(APPEND BACKEND_SOURCES src/backends/sdl2_simulator.cpp)
endif()

if(WITH_UINPUT)
    list(APPEND BACKEND_SOURCES src/backends/uinput_simulator.cpp)
endif()

# Create library
add_library(input_backends ${CORE_SOURCES} ${BACKEND_SOURCES})

# Set compile definitions based on enabled backends
if(WITH_X11)
    target_compile_definitions(input_backends PRIVATE WITH_X11)
endif()

if(WITH_WAYLAND)
    target_compile_definitions(input_backends PRIVATE WITH_WAYLAND)
endif()

if(WITH_KDE)
    target_compile_definitions(input_backends PRIVATE WITH_KDE)
endif()

if(WITH_SDL2)
    target_compile_definitions(input_backends PRIVATE WITH_SDL2)
endif()

if(WITH_UINPUT)
    target_compile_definitions(input_backends PRIVATE WITH_UINPUT)
endif()

# Link libraries based on backends
if(WITH_X11)
    target_include_directories(input_backends PRIVATE ${X11_INCLUDE_DIRS})
    target_link_libraries(input_backends PRIVATE ${X11_LIBRARIES})
endif()

if(WITH_WAYLAND)
    target_include_directories(input_backends PRIVATE ${WAYLAND_INCLUDE_DIRS})
    target_link_libraries(input_backends PRIVATE ${WAYLAND_LIBRARIES})
endif()

if(WITH_SDL2)
    target_include_directories(input_backends PRIVATE ${SDL2_INCLUDE_DIRS})
    target_link_libraries(input_backends PRIVATE ${SDL2_LIBRARIES})
endif()

# Set include directories for the library
target_include_directories(input_backends
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# System libraries
if(UNIX AND NOT APPLE)
    target_link_libraries(input_backends PRIVATE pthread)
endif()

# Install targets
install(TARGETS input_backends
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