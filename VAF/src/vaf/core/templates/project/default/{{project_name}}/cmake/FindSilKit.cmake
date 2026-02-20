# Workaround for statically linked SIL Kit

# Locate the spdlog library
find_library(SPDLOG_LIBRARY
  NAMES spdlog
  PATHS /usr/local/lib
  NO_DEFAULT_PATH
)

# Locate the yaml-cpp library
find_library(YAML_CPP_LIBRARY
  NAMES rapidyaml-static
  PATHS /usr/local/lib
  NO_DEFAULT_PATH
)

# Locate the SIL Kit library
find_library(SILKIT_LIBRARY
  NAMES SilKit
  PATHS /usr/local/lib
  NO_DEFAULT_PATH
)

# Set the imported targets
if(SPDLOG_LIBRARY AND YAML_CPP_LIBRARY AND SILKIT_LIBRARY)
  add_library(spdlog STATIC IMPORTED)
  set_property(TARGET spdlog PROPERTY IMPORTED_LOCATION ${SPDLOG_LIBRARY})

  add_library(yaml_cpp STATIC IMPORTED)
  set_property(TARGET yaml_cpp PROPERTY IMPORTED_LOCATION ${YAML_CPP_LIBRARY})

  add_library(SilKit::SilKit STATIC IMPORTED)
  set_property(TARGET SilKit::SilKit PROPERTY IMPORTED_LOCATION ${SILKIT_LIBRARY})

  target_link_libraries(SilKit::SilKit INTERFACE yaml_cpp spdlog)
else()
  if(NOT SilKit_FIND_QUIETLY)
    if(NOT SPDLOG_LIBRARY)
      message(WARNING "SilKit dependency spdlog library not found")
    endif()
    if(NOT YAML_CPP_LIBRARY)
      message(WARNING "SilKit dependency yaml-cpp library not found")
    endif()
    if(NOT SILKIT_LIBRARY)
      message(WARNING "SilKit library not found")
    endif()
  endif()
  if(SilKit_FIND_REQUIRED)
    message(FATAL_ERROR "SilKit or dependencies not found")
  endif()
endif()
