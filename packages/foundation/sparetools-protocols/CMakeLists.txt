cmake_minimum_required(VERSION 3.25)
project(sparetools-protocols VERSION 1.0.0 LANGUAGES CXX)

# Find FlatBuffers
find_package(FlatBuffers REQUIRED)

# Set output directories for generated code
set(GENERATED_DIR ${CMAKE_BINARY_DIR}/generated)

# Create output directories
file(MAKE_DIRECTORY ${GENERATED_DIR})

# Define schema groups for organized code generation
set(COMMON_SCHEMAS
    ${CMAKE_SOURCE_DIR}/schemas/common/common.fbs
)

set(IOT_SCHEMAS
    ${CMAKE_SOURCE_DIR}/schemas/iot/BPM.fbs
    ${CMAKE_SOURCE_DIR}/schemas/iot/VEHICLE.fbs
    ${CMAKE_SOURCE_DIR}/schemas/iot/bpm_protocol.fbs
)

set(MEDICAL_SCHEMAS
    ${CMAKE_SOURCE_DIR}/schemas/medical/MIA.fbs
)

set(MCP_SCHEMAS
    ${CMAKE_SOURCE_DIR}/schemas/mcp/MCP.fbs
)

set(EMBEDDED_SCHEMAS
    # Temporarily disabled - need schema fixes
    # ${CMAKE_SOURCE_DIR}/schemas/embedded/hardware.fbs
    # ${CMAKE_SOURCE_DIR}/schemas/embedded/audio.fbs
    # ${CMAKE_SOURCE_DIR}/schemas/embedded/rf.fbs
    # ${CMAKE_SOURCE_DIR}/schemas/embedded/obd.fbs
    # ${CMAKE_SOURCE_DIR}/schemas/embedded/nucleus_protocol.fbs
)

# Function to generate FlatBuffers code for a schema group
function(generate_flatbuffers_code SCHEMA_GROUP_NAME SCHEMA_FILES OUTPUT_SUBDIR)
    set(OUTPUT_DIR ${GENERATED_DIR}/${OUTPUT_SUBDIR})
    file(MAKE_DIRECTORY ${OUTPUT_DIR})

    set(GENERATED_HEADERS)

    foreach(SCHEMA_FILE ${SCHEMA_FILES})
        get_filename_component(SCHEMA_NAME ${SCHEMA_FILE} NAME_WE)
        set(GENERATED_HEADER ${OUTPUT_DIR}/${SCHEMA_NAME}_generated.h)

        add_custom_command(
            OUTPUT ${GENERATED_HEADER}
            COMMAND ${FLATBUFFERS_FLATC_EXECUTABLE}
                --cpp
                --scoped-enums
                --gen-mutable
                --gen-object-api
                -I ${CMAKE_SOURCE_DIR}/schemas/common
                -o ${OUTPUT_DIR}
                ${SCHEMA_FILE}
            DEPENDS ${SCHEMA_FILE}
            COMMENT "Generating C++ header for ${SCHEMA_NAME}.fbs"
        )

        list(APPEND GENERATED_HEADERS ${GENERATED_HEADER})
    endforeach()

    # Create a custom target for this schema group
    add_custom_target(${SCHEMA_GROUP_NAME}_codegen ALL
        DEPENDS ${GENERATED_HEADERS}
    )

    # Set parent scope variables for installation
    set(${SCHEMA_GROUP_NAME}_HEADERS ${GENERATED_HEADERS} PARENT_SCOPE)
    set(${SCHEMA_GROUP_NAME}_OUTPUT_DIR ${OUTPUT_DIR} PARENT_SCOPE)
endfunction()

# Generate code for each schema group
generate_flatbuffers_code(common "${COMMON_SCHEMAS}" "common")
generate_flatbuffers_code(iot "${IOT_SCHEMAS}" "iot")
generate_flatbuffers_code(medical "${MEDICAL_SCHEMAS}" "medical")
generate_flatbuffers_code(mcp "${MCP_SCHEMAS}" "mcp")
generate_flatbuffers_code(embedded "${EMBEDDED_SCHEMAS}" "embedded")

# Optional: Generate Python bindings for cross-platform testing
option(GENERATE_PYTHON_BINDINGS "Generate Python bindings for schemas" ON)

if(GENERATE_PYTHON_BINDINGS)
    set(PYTHON_DIR ${GENERATED_DIR}/python)
    file(MAKE_DIRECTORY ${PYTHON_DIR})

    # Combine all schemas for Python generation
    set(ALL_SCHEMAS ${COMMON_SCHEMAS} ${IOT_SCHEMAS} ${MEDICAL_SCHEMAS} ${MCP_SCHEMAS} ${EMBEDDED_SCHEMAS})

    set(PYTHON_BINDINGS)
    foreach(SCHEMA_FILE ${ALL_SCHEMAS})
        get_filename_component(SCHEMA_NAME ${SCHEMA_FILE} NAME_WE)
        set(PYTHON_BINDING ${PYTHON_DIR}/${SCHEMA_NAME}_generated.py)

        add_custom_command(
            OUTPUT ${PYTHON_BINDING}
            COMMAND ${FLATBUFFERS_FLATC_EXECUTABLE}
                --python
                -I ${CMAKE_SOURCE_DIR}/schemas/common
                -o ${PYTHON_DIR}
                ${SCHEMA_FILE}
            DEPENDS ${SCHEMA_FILE}
            COMMENT "Generating Python binding for ${SCHEMA_NAME}.fbs"
        )

        list(APPEND PYTHON_BINDINGS ${PYTHON_BINDING})
    endforeach()

    add_custom_target(python_bindings ALL
        DEPENDS ${PYTHON_BINDINGS}
    )
endif()

# Create master codegen target
add_custom_target(codegen ALL
    DEPENDS
        common_codegen
        iot_codegen
        medical_codegen
        mcp_codegen
        embedded_codegen
)

if(GENERATE_PYTHON_BINDINGS)
    add_dependencies(codegen python_bindings)
endif()

# Installation rules for headers
install(DIRECTORY ${GENERATED_DIR}/
    DESTINATION include/sparetools-protocols
    FILES_MATCHING PATTERN "*.h"
)

if(GENERATE_PYTHON_BINDINGS)
    install(DIRECTORY ${GENERATED_DIR}/python/
        DESTINATION python/sparetools_protocols
        FILES_MATCHING PATTERN "*.py"
    )
endif()

# Installation rules for schemas
install(DIRECTORY ${CMAKE_SOURCE_DIR}/schemas/
    DESTINATION schemas/sparetools-protocols
    FILES_MATCHING PATTERN "*.fbs"
)