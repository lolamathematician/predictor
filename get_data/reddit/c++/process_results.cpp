//
// Created by mrjoeybux on 23/07/2020.
//
#include "process_results.h"
#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>
#include <pybind11/stl.h>
namespace py = pybind11;

void ResultProcessor::configure(vector<string>& fields_to_keep){
    this->FieldsToKeep = fields_to_keep;
}

unordered_map<string, string> ResultProcessor::process_one(unordered_map<string, string>& result_to_process){
    unordered_map<string, string> processed_result;
    for(auto & i : this->FieldsToKeep){
        processed_result[i] = result_to_process.at(i);
    }
    return processed_result;
}

vector<unordered_map<string, string>> ResultProcessor::process_many(vector<unordered_map<string, string>>& results_to_process){
    uint N = results_to_process.size();
    vector<unordered_map<string, string>> processed_results(N);
    for(uint i = 0; i < N; i++){
        processed_results[i] = this->process_one(results_to_process[i]);
    }
    return processed_results;
}

PYBIND11_MODULE(predictor, m){
    py::class_<ResultProcessor>(m, "ResultProcessor")
    .def(py::init<>())
    .def("configure", &ResultProcessor::configure)
    .def("process_one", &ResultProcessor::process_one)
    .def("process_many", &ResultProcessor::process_many);
}