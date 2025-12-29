cmake_minimum_required(VERSION 3.16)
project(sparetools-bpm-schemas VERSION 2.0.0 LANGUAGES CXX)

# Find FlatBuffers
find_package(FlatBuffers REQUIRED)

# Set output directories
set(GENERATED_CPP_DIR ${CMAKE_BINARY_DIR}/generated/cpp)
set(GENERATED_PYTHON_DIR ${CMAKE_BINARY_DIR}/generated/python)

# Create output directories
file(MAKE_DIRECTORY ${GENERATED_CPP_DIR})
file(MAKE_DIRECTORY ${GENERATED_PYTHON_DIR})

# Generate C++ headers from FlatBuffers schema
add_custom_command(
    OUTPUT ${GENERATED_CPP_DIR}/bpm_protocol_generated.h
    COMMAND ${FLATBUFFERS_FLATC_EXECUTABLE}
        --cpp
        --gen-mutable
        --gen-object-api
        -o ${GENERATED_CPP_DIR}
        ${CMAKE_SOURCE_DIR}/schemas/bpm_protocol.fbs
    DEPENDS ${CMAKE_SOURCE_DIR}/schemas/bpm_protocol.fbs
    COMMENT "Generating C++ headers from FlatBuffers schema"
)

# Generate Python bindings from FlatBuffers schema
add_custom_command(
    OUTPUT ${GENERATED_PYTHON_DIR}/bpm_protocol_generated.py
    COMMAND ${FLATBUFFERS_FLATC_EXECUTABLE}
        --python
        -o ${GENERATED_PYTHON_DIR}
        ${CMAKE_SOURCE_DIR}/schemas/bpm_protocol.fbs
    DEPENDS ${CMAKE_SOURCE_DIR}/schemas/bpm_protocol.fbs
    COMMENT "Generating Python bindings from FlatBuffers schema"
)

# Custom target to generate all code
add_custom_target(generate_code ALL
    DEPENDS
        ${GENERATED_CPP_DIR}/bpm_protocol_generated.h
        ${GENERATED_PYTHON_DIR}/bpm_protocol_generated.py
)


