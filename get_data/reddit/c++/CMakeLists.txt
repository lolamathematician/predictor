cmake_minimum_required(VERSION 3.10)
project(predictor)

#add_library(my_python3.7m SHARED IMPORTED)
add_subdirectory(pybind11)
pybind11_add_module(predictor process_results.cpp)