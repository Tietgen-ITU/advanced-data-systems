cmake_minimum_required(VERSION 3.13)

project(ssbgen)
add_executable(ssbgen main.cpp)

add_subdirectory(external/ssbgen)

target_link_directories(ssbgen PRIVATE ${CMAKE_SOURCE_DIR}/out/build/external/ssbgen)
target_link_libraries(ssbgen 
                      PRIVATE psgen)
