# Avoid multiple calls to find_package to append duplicated properties to the targets
include_guard()########### VARIABLES #######################################################################
#############################################################################################
set(sparetools-py_FRAMEWORKS_FOUND_RELEASE "") # Will be filled later
conan_find_apple_frameworks(sparetools-py_FRAMEWORKS_FOUND_RELEASE "${sparetools-py_FRAMEWORKS_RELEASE}" "${sparetools-py_FRAMEWORK_DIRS_RELEASE}")

set(sparetools-py_LIBRARIES_TARGETS "") # Will be filled later


######## Create an interface target to contain all the dependencies (frameworks, system and conan deps)
if(NOT TARGET sparetools-py_DEPS_TARGET)
    add_library(sparetools-py_DEPS_TARGET INTERFACE IMPORTED)
endif()

set_property(TARGET sparetools-py_DEPS_TARGET
             APPEND PROPERTY INTERFACE_LINK_LIBRARIES
             $<$<CONFIG:Release>:${sparetools-py_FRAMEWORKS_FOUND_RELEASE}>
             $<$<CONFIG:Release>:${sparetools-py_SYSTEM_LIBS_RELEASE}>
             $<$<CONFIG:Release>:>)

####### Find the libraries declared in cpp_info.libs, create an IMPORTED target for each one and link the
####### sparetools-py_DEPS_TARGET to all of them
conan_package_library_targets("${sparetools-py_LIBS_RELEASE}"    # libraries
                              "${sparetools-py_LIB_DIRS_RELEASE}" # package_libdir
                              "${sparetools-py_BIN_DIRS_RELEASE}" # package_bindir
                              "${sparetools-py_LIBRARY_TYPE_RELEASE}"
                              "${sparetools-py_IS_HOST_WINDOWS_RELEASE}"
                              sparetools-py_DEPS_TARGET
                              sparetools-py_LIBRARIES_TARGETS  # out_libraries_targets
                              "_RELEASE"
                              "sparetools-py"    # package_name
                              "${sparetools-py_NO_SONAME_MODE_RELEASE}")  # soname

# FIXME: What is the result of this for multi-config? All configs adding themselves to path?
set(CMAKE_MODULE_PATH ${sparetools-py_BUILD_DIRS_RELEASE} ${CMAKE_MODULE_PATH})

########## GLOBAL TARGET PROPERTIES Release ########################################
    set_property(TARGET sparetools-py::sparetools-py
                 APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                 $<$<CONFIG:Release>:${sparetools-py_OBJECTS_RELEASE}>
                 $<$<CONFIG:Release>:${sparetools-py_LIBRARIES_TARGETS}>
                 )

    if("${sparetools-py_LIBS_RELEASE}" STREQUAL "")
        # If the package is not declaring any "cpp_info.libs" the package deps, system libs,
        # frameworks etc are not linked to the imported targets and we need to do it to the
        # global target
        set_property(TARGET sparetools-py::sparetools-py
                     APPEND PROPERTY INTERFACE_LINK_LIBRARIES
                     sparetools-py_DEPS_TARGET)
    endif()

    set_property(TARGET sparetools-py::sparetools-py
                 APPEND PROPERTY INTERFACE_LINK_OPTIONS
                 $<$<CONFIG:Release>:${sparetools-py_LINKER_FLAGS_RELEASE}>)
    set_property(TARGET sparetools-py::sparetools-py
                 APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
                 $<$<CONFIG:Release>:${sparetools-py_INCLUDE_DIRS_RELEASE}>)
    # Necessary to find LINK shared libraries in Linux
    set_property(TARGET sparetools-py::sparetools-py
                 APPEND PROPERTY INTERFACE_LINK_DIRECTORIES
                 $<$<CONFIG:Release>:${sparetools-py_LIB_DIRS_RELEASE}>)
    set_property(TARGET sparetools-py::sparetools-py
                 APPEND PROPERTY INTERFACE_COMPILE_DEFINITIONS
                 $<$<CONFIG:Release>:${sparetools-py_COMPILE_DEFINITIONS_RELEASE}>)
    set_property(TARGET sparetools-py::sparetools-py
                 APPEND PROPERTY INTERFACE_COMPILE_OPTIONS
                 $<$<CONFIG:Release>:${sparetools-py_COMPILE_OPTIONS_RELEASE}>)

########## For the modules (FindXXX)
set(sparetools-py_LIBRARIES_RELEASE sparetools-py::sparetools-py)
