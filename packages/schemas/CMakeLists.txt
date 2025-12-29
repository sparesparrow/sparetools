cmake_minimum_required(VERSION 3.16)
project(sparesparrow-protocols)

# Find FlatBuffers
find_package(FlatBuffers REQUIRED)

# Set FlatBuffers compiler
set(FLATBUFFERS_FLATC_EXECUTABLE flatc)

# List of schema files
set(SCHEMA_FILES
    BPM.fbs
    MIA.fbs
    MCP.fbs
    common.fbs
)

# Generate C++ headers for each schema
foreach(SCHEMA_FILE ${SCHEMA_FILES})
    get_filename_component(SCHEMA_NAME ${SCHEMA_FILE} NAME_WE)
    set(GENERATED_HEADER "${SCHEMA_NAME}_generated.h")

    add_custom_command(
        OUTPUT ${GENERATED_HEADER}
        COMMAND ${FLATBUFFERS_FLATC_EXECUTABLE}
        ARGS --cpp --scoped-enums ${SCHEMA_FILE}
        DEPENDS ${SCHEMA_FILE}
        COMMENT "Generating C++ header for ${SCHEMA_FILE}"
    )

    list(APPEND GENERATED_HEADERS ${GENERATED_HEADER})
endforeach()

# Create a custom target for all generated headers
add_custom_target(generate_schemas ALL DEPENDS ${GENERATED_HEADERS})

# Install headers
install(FILES ${GENERATED_HEADERS}
        DESTINATION include/sparesparrow/protocols)

# Install original schemas
install(FILES ${SCHEMA_FILES}
        DESTINATION share/sparesparrow/protocols/schemas)