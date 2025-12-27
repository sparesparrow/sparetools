cmake_minimum_required(VERSION 3.20)

# Set C++ standard before project()
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Check if we're using Conan toolchain
if(EXISTS "${CMAKE_TOOLCHAIN_FILE}")
    message(STATUS "Using Conan toolchain: ${CMAKE_TOOLCHAIN_FILE}")
endif()

project(GamepadMapper VERSION 1.0.0 LANGUAGES CXX)

# Add Conan-generated files to paths
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_BINARY_DIR}")

# Options for backend selection
option(WITH_X11 "Enable X11 backend" ON)
option(WITH_WAYLAND "Enable Wayland backend" ON)
option(WITH_KDE "Enable KDE backend" ON)
option(WITH_SDL2 "Enable SDL2 backend" ON)
option(WITH_UINPUT "Enable UInput backend" ON)
option(WITH_MCP "Enable MCP server" ON)
option(WITH_BLUETOOTH "Enable Bluetooth HID device support" ON)
option(WITH_CLIPBOARD "Enable clipboard monitoring" ON)

# Find required packages
find_package(PkgConfig REQUIRED)

# Include Conan dependencies
include(${CMAKE_BINARY_DIR}/conandeps_legacy.cmake OPTIONAL)

# Find nlohmann_json from Conan
find_package(nlohmann_json REQUIRED)

# Find libcurl for network operations
find_package(CURL REQUIRED)

# Backend-specific package detection
if(WITH_X11)
    pkg_check_modules(X11 REQUIRED x11 xtst)
endif()

if(WITH_WAYLAND)
    pkg_check_modules(WAYLAND REQUIRED wayland-client wayland-protocols)
endif()

if(WITH_SDL2)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(SDL2 REQUIRED sdl2)
endif()

if(WITH_BLUETOOTH)
    # Find Bluetooth development libraries
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(BLUEZ bluez)
    if(NOT BLUEZ_FOUND)
        # Fallback: try to find libbluetooth directly
        find_library(BLUEZ_LIBRARIES bluetooth)
        if(BLUEZ_LIBRARIES)
            set(BLUEZ_FOUND TRUE)
            set(BLUEZ_LIBRARIES ${BLUEZ_LIBRARIES})
            set(BLUEZ_INCLUDE_DIRS "")
        endif()
    endif()

    if(NOT BLUEZ_FOUND)
        message(WARNING "Bluetooth libraries not found. Bluetooth support will be disabled.")
        set(WITH_BLUETOOTH OFF)
    endif()
endif()

if(WITH_CLIPBOARD)
    # Find GTK for clipboard support
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(GTK gtk+-3.0)
    if(NOT GTK_FOUND)
        message(WARNING "GTK libraries not found. Clipboard support will be disabled.")
        set(WITH_CLIPBOARD OFF)
    endif()
endif()

# Include directories
include_directories(include)
include_directories(${CMAKE_BINARY_DIR}/include)  # For generated headers

if(WITH_MCP)
    # TinyMCP is included as external dependency
    add_subdirectory(external/TinyMCP EXCLUDE_FROM_ALL)
    # Add TinyMCP include directory
    include_directories(external/TinyMCP/Source)
    # Add TinyMCP's bundled jsoncpp include directory
    include_directories(external/TinyMCP/Source/External/jsoncpp/include)
endif()

# Add Conan include directories
if(EXISTS "${CMAKE_BINARY_DIR}/conandeps_legacy.cmake")
    include(${CMAKE_BINARY_DIR}/conandeps_legacy.cmake)
endif()

# Add nlohmann_json include directory explicitly
include_directories(/home/sparrow/.conan2/p/nlohm1bed1ddc0a2fa/p/include)

# Source files
set(CORE_SOURCES
    src/gamepad_mapper.cpp
    src/controller_manager.cpp
)

# Add clipboard monitor if enabled
if(WITH_CLIPBOARD)
    list(APPEND CORE_SOURCES src/clipboard_monitor.cpp)
endif()

# Add voice alerts system
list(APPEND CORE_SOURCES src/voice_alerts.cpp)

# Add Bluetooth stubs when Bluetooth is disabled
if(NOT WITH_BLUETOOTH)
    list(APPEND CORE_SOURCES src/bluetooth_stubs.cpp)
endif()

set(BACKEND_SOURCES)

# Add backend sources conditionally
if(WITH_X11)
    list(APPEND BACKEND_SOURCES src/input_backends/x11_simulator.cpp)
endif()

if(WITH_WAYLAND)
    list(APPEND BACKEND_SOURCES src/input_backends/wayland_simulator.cpp)
endif()

if(WITH_KDE)
    list(APPEND BACKEND_SOURCES src/input_backends/kde_simulator.cpp)
endif()

if(WITH_SDL2)
    list(APPEND BACKEND_SOURCES src/input_backends/sdl2_simulator.cpp)
endif()

if(WITH_UINPUT)
    list(APPEND BACKEND_SOURCES src/input_backends/uinput_simulator.cpp)
endif()

if(WITH_MCP)
    list(APPEND CORE_SOURCES src/gamepad_server.cpp)
endif()

# Create main library
add_library(gamepad_mapper ${CORE_SOURCES} ${BACKEND_SOURCES})

# Set compile definitions based on enabled backends
if(WITH_X11)
    target_compile_definitions(gamepad_mapper PRIVATE WITH_X11)
endif()

if(WITH_WAYLAND)
    target_compile_definitions(gamepad_mapper PRIVATE WITH_WAYLAND)
endif()

if(WITH_KDE)
    target_compile_definitions(gamepad_mapper PRIVATE WITH_KDE)
endif()

if(WITH_SDL2)
    target_compile_definitions(gamepad_mapper PRIVATE WITH_SDL2)
endif()

if(WITH_UINPUT)
    target_compile_definitions(gamepad_mapper PRIVATE WITH_UINPUT)
endif()

if(WITH_MCP)
    target_compile_definitions(gamepad_mapper PRIVATE WITH_MCP)
endif()

if(WITH_BLUETOOTH)
    target_compile_definitions(gamepad_mapper PRIVATE WITH_BLUETOOTH=1)
else()
    target_compile_definitions(gamepad_mapper PRIVATE WITH_BLUETOOTH=0)
endif()

if(WITH_CLIPBOARD)
    target_compile_definitions(gamepad_mapper PRIVATE WITH_CLIPBOARD)
endif()

# Link libraries
target_link_libraries(gamepad_mapper PRIVATE nlohmann_json::nlohmann_json CURL::libcurl)

# Ensure include directories are properly set
target_include_directories(gamepad_mapper PRIVATE 
    $<TARGET_PROPERTY:nlohmann_json::nlohmann_json,INTERFACE_INCLUDE_DIRECTORIES>
)

# Backend-specific linking
if(WITH_X11)
    target_include_directories(gamepad_mapper PRIVATE ${X11_INCLUDE_DIRS})
    target_link_libraries(gamepad_mapper PRIVATE ${X11_LIBRARIES})
endif()

if(WITH_WAYLAND)
    target_include_directories(gamepad_mapper PRIVATE ${WAYLAND_INCLUDE_DIRS})
    target_link_libraries(gamepad_mapper PRIVATE ${WAYLAND_LIBRARIES})
endif()

if(WITH_SDL2)
    target_include_directories(gamepad_mapper PRIVATE ${SDL2_INCLUDE_DIRS})
    target_link_libraries(gamepad_mapper PRIVATE ${SDL2_LIBRARIES})
endif()

if(WITH_BLUETOOTH)
    target_include_directories(gamepad_mapper PRIVATE ${BLUEZ_INCLUDE_DIRS})
    target_link_libraries(gamepad_mapper PRIVATE ${BLUEZ_LIBRARIES})
endif()

if(WITH_CLIPBOARD)
    target_include_directories(gamepad_mapper PRIVATE ${GTK_INCLUDE_DIRS})
    target_link_libraries(gamepad_mapper PRIVATE ${GTK_LIBRARIES})
endif()

# Voice alerts system (uses espeak)
find_program(ESPEAK_EXECUTABLE espeak)
if(ESPEAK_EXECUTABLE)
    message(STATUS "Found espeak: ${ESPEAK_EXECUTABLE}")
    target_compile_definitions(gamepad_mapper PRIVATE WITH_VOICE_ALERTS)
else()
    message(WARNING "espeak not found. Voice alerts will be disabled.")
endif()

# Audio backend support
option(WITH_ALSA "Enable ALSA audio backend" ON)
option(WITH_PULSEAUDIO "Enable PulseAudio backend" ON)

if(WITH_ALSA)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(ALSA alsa)
    if(ALSA_FOUND)
        target_include_directories(gamepad_mapper PRIVATE ${ALSA_INCLUDE_DIRS})
        target_link_libraries(gamepad_mapper PRIVATE ${ALSA_LIBRARIES})
        target_compile_definitions(gamepad_mapper PRIVATE WITH_ALSA)
        message(STATUS "ALSA audio backend enabled")
    else()
        message(WARNING "ALSA not found. ALSA backend will be disabled.")
        set(WITH_ALSA OFF)
    endif()
endif()

if(WITH_PULSEAUDIO)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(PULSEAUDIO libpulse)
    if(PULSEAUDIO_FOUND)
        target_include_directories(gamepad_mapper PRIVATE ${PULSEAUDIO_INCLUDE_DIRS})
        target_link_libraries(gamepad_mapper PRIVATE ${PULSEAUDIO_LIBRARIES})
        target_compile_definitions(gamepad_mapper PRIVATE WITH_PULSEAUDIO)
        message(STATUS "PulseAudio backend enabled")
    else()
        message(WARNING "PulseAudio not found. PulseAudio backend will be disabled.")
        set(WITH_PULSEAUDIO OFF)
    endif()
endif()

# Add audio backend source
list(APPEND CORE_SOURCES src/audio_backend.cpp)

# Add KDE Connect client source
list(APPEND CORE_SOURCES src/kde_connect_client.cpp)

if(WITH_MCP)
    target_link_libraries(gamepad_mapper PRIVATE tinymcp)
endif()

# System libraries
if(UNIX AND NOT APPLE)
    target_link_libraries(gamepad_mapper PRIVATE udev pthread)
endif()

# Create executable
add_executable(gamepad_mapper_app src/main.cpp)
target_link_libraries(gamepad_mapper_app PRIVATE gamepad_mapper)

# Create advanced executable
add_executable(advanced_gamepad_mapper src/advanced_main.cpp)
target_link_libraries(advanced_gamepad_mapper PRIVATE gamepad_mapper)

# Create MCP tool if enabled
if(WITH_MCP)
    # Python tool - just install it
    install(PROGRAMS tools/mcp_gamepad_tool.py
        DESTINATION bin
        RENAME mcp_gamepad_tool)
endif()

# Install targets
install(TARGETS gamepad_mapper gamepad_mapper_app advanced_gamepad_mapper
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(DIRECTORY include/ DESTINATION include)

# Install config files
install(DIRECTORY config/ DESTINATION share/gamepad-mapper/config)

# Generate and install pkg-config file
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/gamepad-mapper.pc.in
    ${CMAKE_CURRENT_BINARY_DIR}/gamepad-mapper.pc
    @ONLY
)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/gamepad-mapper.pc
    DESTINATION lib/pkgconfig
)

# Testing (optional)
option(BUILD_TESTS "Build tests" OFF)
if(BUILD_TESTS)
    enable_testing()
    # Try to find GTest from Conan first, fallback to system
    find_package(GTest QUIET)
    if(NOT GTest_FOUND)
        find_package(GTest REQUIRED)
    endif()
    add_subdirectory(tests)
endif()

# Documentation
find_package(Doxygen)
if(DOXYGEN_FOUND)
    set(DOXYGEN_INPUT_DIR ${CMAKE_CURRENT_SOURCE_DIR})
    set(DOXYGEN_OUTPUT_DIR ${CMAKE_CURRENT_BINARY_DIR}/docs)
    configure_file(Doxyfile.in Doxyfile @ONLY)
    add_custom_target(docs
        COMMAND ${DOXYGEN_EXECUTABLE} Doxyfile
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Generating API documentation with Doxygen"
    )
endif()