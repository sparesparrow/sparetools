cmake_minimum_required(VERSION 3.16)
project(mcpserver-cpp VERSION 2.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find dependencies
find_package(sparetools-openssl REQUIRED)

# Source files
set(SOURCES
    src/mcp_server.cpp
    src/json_rpc.cpp
    src/tool_registry.cpp
    src/resource_manager.cpp
)

set(HEADERS
    include/mcp_server.hpp
    include/json_rpc.hpp
    include/tool_registry.hpp
    include/resource_manager.hpp
)

# Create library
add_library(mcpserver ${SOURCES} ${HEADERS})

# Include directories
target_include_directories(mcpserver
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        src
)

# Link dependencies
target_link_libraries(mcpserver
    PUBLIC
        sparetools-openssl::sparetools-openssl
)

# Compiler options
if(MSVC)
    target_compile_options(mcpserver PRIVATE /W4)
else()
    target_compile_options(mcpserver PRIVATE -Wall -Wextra -Wpedantic)
endif()

# Install
install(TARGETS mcpserver
    EXPORT McpServerTargets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(FILES ${HEADERS} DESTINATION include)

install(EXPORT McpServerTargets
    FILE McpServerTargets.cmake
    NAMESPACE McpServer::
    DESTINATION lib/cmake/McpServer
)