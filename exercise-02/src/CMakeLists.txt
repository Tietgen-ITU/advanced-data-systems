cmake_minimum_required(VERSION 3.30)

project(sgen)
add_executable(sgen main.cpp)

add_subdirectory(ssbgen)

target_link_libraries(sgen 
                      PRIVATE ssbgen)
target_include_directories(sgen 
                           PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/ssbgen/include)

target_compile_definitions(sgen PUBLIC DB2)
target_compile_definitions(sgen PUBLIC MAC)
target_compile_definitions(sgen PUBLIC SSBM)
target_compile_definitions(sgen PUBLIC DBNAME="dss")