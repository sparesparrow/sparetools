cmake_minimum_required(VERSION 3.16)
project(voice_control_fsm VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Boost (specifically SML)
find_package(Boost 1.83.0 REQUIRED)

# Create the voice control FSM library
add_library(voice_control_fsm
    src/voice_control_fsm.cpp
)

target_include_directories(voice_control_fsm
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${Boost_INCLUDE_DIRS}
)

target_link_libraries(voice_control_fsm
    PUBLIC
        Boost::boost
)

# Install the library and headers
install(TARGETS voice_control_fsm
    EXPORT voice_control_fsm-targets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(DIRECTORY include/
    DESTINATION include
    FILES_MATCHING PATTERN "*.hpp" PATTERN "*.h"
)

install(EXPORT voice_control_fsm-targets
    FILE voice_control_fsm-config.cmake
    NAMESPACE voice_control_fsm::
    DESTINATION lib/cmake/voice_control_fsm
)