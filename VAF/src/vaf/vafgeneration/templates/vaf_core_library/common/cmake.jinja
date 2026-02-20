find_package(Threads)

set(TARGET vaf_core)
add_library(${TARGET} STATIC)
target_sources(
  ${TARGET}
  PRIVATE "${CMAKE_CURRENT_LIST_DIR}/include/vaf/receiver_handler_container.h"
          "${CMAKE_CURRENT_LIST_DIR}/include/vaf/user_controller_interface.h"
          "${CMAKE_CURRENT_LIST_DIR}/include/vaf/container_types.h"
          "${CMAKE_CURRENT_LIST_DIR}/include/vaf/runtime.h"
          "${CMAKE_CURRENT_LIST_DIR}/include/vaf/controller_interface.h"
          "${CMAKE_CURRENT_LIST_DIR}/include/vaf/executable_controller_base.h"
          "${CMAKE_CURRENT_LIST_DIR}/include/vaf/executable_controller_interface.h"
          "${CMAKE_CURRENT_LIST_DIR}/include/vaf/module_states.h"
          "${CMAKE_CURRENT_LIST_DIR}/include/vaf/output_sync_stream.h"
          "${CMAKE_CURRENT_LIST_DIR}/include/vaf/future.h"
          "${CMAKE_CURRENT_LIST_DIR}/include/vaf/result.h"
          "${CMAKE_CURRENT_LIST_DIR}/include/vaf/data_ptr.h"
          "${CMAKE_CURRENT_LIST_DIR}/include/vaf/internal/data_ptr_helper.h"
          "${CMAKE_CURRENT_LIST_DIR}/src/controller_interface.cpp"
          "${CMAKE_CURRENT_LIST_DIR}/src/executable_controller_base.cpp"
          "${CMAKE_CURRENT_LIST_DIR}/src/executor.cpp"
          "${CMAKE_CURRENT_LIST_DIR}/src/logging.cpp"
          "${CMAKE_CURRENT_LIST_DIR}/src/runtime.cpp")

target_include_directories(
        ${TARGET} PUBLIC "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
        "$<INSTALL_INTERFACE:include>")

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
