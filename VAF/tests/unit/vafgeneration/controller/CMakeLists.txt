cmake_minimum_required(VERSION 3.21)
project(MyExecutable)

find_package(Threads)

add_executable(${PROJECT_NAME})

target_compile_options(${PROJECT_NAME}
  PRIVATE
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wall>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wextra>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wshadow>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wnon-virtual-dtor>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wold-style-cast>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wcast-align>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wunused>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Woverloaded-virtual>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-pedantic>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wconversion>
    $<$<AND:$<PLATFORM_ID:Linux>,$<C_COMPILER_ID:GNU>>:-Wsign-conversion>)

target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_14)

target_compile_definitions(${PROJECT_NAME} PUBLIC)

set(target ${PROJECT_NAME})
set_target_properties(${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/${PROJECT_NAME}/bin)

target_include_directories(${PROJECT_NAME}
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
    $<INSTALL_INTERFACE:include>
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src)

target_sources(
  ${PROJECT_NAME}
  PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include/executable_controller/executable_controller.h
    ${CMAKE_CURRENT_SOURCE_DIR}/src/executable_controller/executable_controller.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp
)

# cmake-format: off
target_link_libraries(
  ${PROJECT_NAME}
  PRIVATE
    Threads::Threads
    vaf_core
    vaf_my_module3
    vaf_my_module4
    vaf_my_module1
    vaf_my_module2
    my_app1
    my_app2
    vaf_persistency
    vaf_MyExecutable_user_controller
)
# cmake-format: on

# Define files to be installed
install(TARGETS ${PROJECT_NAME} DESTINATION "opt/${PROJECT_NAME}/bin")

install(PROGRAMS "/usr/local/bin/sil-kit-registry" DESTINATION "opt/silkit/bin")

file(GLOB PROTO_FILES "../../libs/protobuf_serdes/proto/*.proto")
