########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(sparetools-py_COMPONENT_NAMES "")
if(DEFINED sparetools-py_FIND_DEPENDENCY_NAMES)
  list(APPEND sparetools-py_FIND_DEPENDENCY_NAMES )
  list(REMOVE_DUPLICATES sparetools-py_FIND_DEPENDENCY_NAMES)
else()
  set(sparetools-py_FIND_DEPENDENCY_NAMES )
endif()

########### VARIABLES #######################################################################
#############################################################################################
set(sparetools-py_PACKAGE_FOLDER_RELEASE "/home/sparrow/.conan2/p/b/spare95a887e6579a1/p")
set(sparetools-py_BUILD_MODULES_PATHS_RELEASE )


set(sparetools-py_INCLUDE_DIRS_RELEASE )
set(sparetools-py_RES_DIRS_RELEASE )
set(sparetools-py_DEFINITIONS_RELEASE )
set(sparetools-py_SHARED_LINK_FLAGS_RELEASE )
set(sparetools-py_EXE_LINK_FLAGS_RELEASE )
set(sparetools-py_OBJECTS_RELEASE )
set(sparetools-py_COMPILE_DEFINITIONS_RELEASE )
set(sparetools-py_COMPILE_OPTIONS_C_RELEASE )
set(sparetools-py_COMPILE_OPTIONS_CXX_RELEASE )
set(sparetools-py_LIB_DIRS_RELEASE "${sparetools-py_PACKAGE_FOLDER_RELEASE}/lib")
set(sparetools-py_BIN_DIRS_RELEASE "${sparetools-py_PACKAGE_FOLDER_RELEASE}/bin")
set(sparetools-py_LIBRARY_TYPE_RELEASE UNKNOWN)
set(sparetools-py_IS_HOST_WINDOWS_RELEASE 0)
set(sparetools-py_LIBS_RELEASE )
set(sparetools-py_SYSTEM_LIBS_RELEASE )
set(sparetools-py_FRAMEWORK_DIRS_RELEASE )
set(sparetools-py_FRAMEWORKS_RELEASE )
set(sparetools-py_BUILD_DIRS_RELEASE )
set(sparetools-py_NO_SONAME_MODE_RELEASE FALSE)


# COMPOUND VARIABLES
set(sparetools-py_COMPILE_OPTIONS_RELEASE
    "$<$<COMPILE_LANGUAGE:CXX>:${sparetools-py_COMPILE_OPTIONS_CXX_RELEASE}>"
    "$<$<COMPILE_LANGUAGE:C>:${sparetools-py_COMPILE_OPTIONS_C_RELEASE}>")
set(sparetools-py_LINKER_FLAGS_RELEASE
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${sparetools-py_SHARED_LINK_FLAGS_RELEASE}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${sparetools-py_SHARED_LINK_FLAGS_RELEASE}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${sparetools-py_EXE_LINK_FLAGS_RELEASE}>")


set(sparetools-py_COMPONENTS_RELEASE )