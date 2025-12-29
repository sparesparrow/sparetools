########## MACROS ###########################################################################
#############################################################################################

# Requires CMake > 3.15
if(${CMAKE_VERSION} VERSION_LESS "3.15")
    message(FATAL_ERROR "The 'CMakeDeps' generator only works with CMake >= 3.15")
endif()

if(sparetools-py_FIND_QUIETLY)
    set(sparetools-py_MESSAGE_MODE VERBOSE)
else()
    set(sparetools-py_MESSAGE_MODE STATUS)
endif()

include(${CMAKE_CURRENT_LIST_DIR}/cmakedeps_macros.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/sparetools-pyTargets.cmake)
include(CMakeFindDependencyMacro)

check_build_type_defined()

foreach(_DEPENDENCY ${sparetools-py_FIND_DEPENDENCY_NAMES} )
    # Check that we have not already called a find_package with the transitive dependency
    if(NOT ${_DEPENDENCY}_FOUND)
        find_dependency(${_DEPENDENCY} REQUIRED ${${_DEPENDENCY}_FIND_MODE})
    endif()
endforeach()

set(sparetools-py_VERSION_STRING "1.0.0")
set(sparetools-py_INCLUDE_DIRS ${sparetools-py_INCLUDE_DIRS_RELEASE} )
set(sparetools-py_INCLUDE_DIR ${sparetools-py_INCLUDE_DIRS_RELEASE} )
set(sparetools-py_LIBRARIES ${sparetools-py_LIBRARIES_RELEASE} )
set(sparetools-py_DEFINITIONS ${sparetools-py_DEFINITIONS_RELEASE} )


# Definition of extra CMake variables from cmake_extra_variables


# Only the last installed configuration BUILD_MODULES are included to avoid the collision
foreach(_BUILD_MODULE ${sparetools-py_BUILD_MODULES_PATHS_RELEASE} )
    message(${sparetools-py_MESSAGE_MODE} "Conan: Including build module from '${_BUILD_MODULE}'")
    include(${_BUILD_MODULE})
endforeach()


