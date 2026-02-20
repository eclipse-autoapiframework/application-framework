##=======================================================================
##  COPYRIGHT
##  -------------------------------------------------------------------------------------------------------------------
##  \verbatim
##  Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
##  SPDX-License-Identifier: Apache-2.0
##  \endverbatim
##  -------------------------------------------------------------------------------------------------------------------
##  FILE DESCRIPTION
##  -------------------------------------------------------------------------------------------------------------------
##        \file    CMakeLists.txt
##=======================================================================

set(TARGET vaf_protobuf_transformer)

add_library(${TARGET} INTERFACE)

target_include_directories(${TARGET}
    INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>)

target_link_libraries(${TARGET}
    INTERFACE
        vaf_module_interfaces
    )

if(VAF_STAND_ALONE_BUILD)
  # Install headers only if the include directory exists
  if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/include")
      install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include/
              DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
  endif()

  # Install the library
  install(TARGETS ${TARGET}
    EXPORT ${TARGET}Targets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  )

  # Export the target
  install(EXPORT ${TARGET}Targets
    FILE ${TARGET}Config.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${TARGET}
  )
endif()
