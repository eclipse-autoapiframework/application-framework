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

FIND_PACKAGE(protobuf REQUIRED)

set(TARGET vaf_protobuf)

file(GLOB SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/*.proto)
protobuf_generate_cpp(PROTO_SRC PROTO_HEADER ${SOURCES})

add_library(${TARGET} STATIC ${PROTO_HEADER} ${PROTO_SRC})

target_include_directories(${TARGET}
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
        $<INSTALL_INTERFACE:include>)

target_link_libraries(${TARGET}
    PUBLIC
        protobuf::protobuf
    )

if(VAF_STAND_ALONE_BUILD)
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
