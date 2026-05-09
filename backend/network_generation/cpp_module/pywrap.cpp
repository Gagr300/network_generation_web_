#define PYBIND11_DETAILED_ERROR_MESSAGES

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "my_motif_counter.h"

namespace py = pybind11;

PYBIND11_MODULE(motif_counter_cpp, m) {
    m.doc() = "C++ module for motif counting";

    py::class_<MyMotifCounter>(m, "MyMotifCounter")
        .def(py::init<>(),
             "Create MotifCounter")

        .def("count_motifs_fast", &MyMotifCounter::count_motifs_fast,
             "Fast motif counting using subgraph enumeration",
             py::arg("nodes_list"),
             py::arg("edges_list"),
             py::arg("num_nodes"),
             py::arg("motifs_list"),
             py::arg("motif_size"));
}