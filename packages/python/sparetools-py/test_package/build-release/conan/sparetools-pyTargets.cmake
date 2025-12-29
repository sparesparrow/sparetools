# Load the debug and release variables
file(GLOB DATA_FILES "${CMAKE_CURRENT_LIST_DIR}/sparetools-py-*-data.cmake")

foreach(f ${DATA_FILES})
    include(${f})
endforeach()

# Create the targets for all the components
foreach(_COMPONENT ${sparetools-py_COMPONENT_NAMES} )
    if(NOT TARGET ${_COMPONENT})
        add_library(${_COMPONENT} INTERFACE IMPORTED)
        message(${sparetools-py_MESSAGE_MODE} "Conan: Component target declared '${_COMPONENT}'")
    endif()
endforeach()

if(NOT TARGET sparetools-py::sparetools-py)
    add_library(sparetools-py::sparetools-py INTERFACE IMPORTED)
    message(${sparetools-py_MESSAGE_MODE} "Conan: Target declared 'sparetools-py::sparetools-py'")
endif()
# Load the debug and release library finders
file(GLOB CONFIG_FILES "${CMAKE_CURRENT_LIST_DIR}/sparetools-py-Target-*.cmake")

foreach(f ${CONFIG_FILES})
    include(${f})
endforeach()