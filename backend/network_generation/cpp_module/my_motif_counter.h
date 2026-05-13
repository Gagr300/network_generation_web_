#ifndef MY_MOTIF_COUNTER_H
#define MY_MOTIF_COUNTER_H

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <string>
#include <algorithm>
#include <map>
#include <set>
#include <iostream>
#include <sstream>
#include <omp.h>

namespace py = pybind11;

struct Graph {
    std::set<std::string> nodes;
    std::map<std::string, std::set<std::string>> adj_list;

    Graph() {}

    void add_node(const std::string& v) {
        nodes.insert(v);
        if (adj_list.find(v) == adj_list.end()) {
            adj_list[v] = std::set<std::string>();
        }
    }

    void add_edge(const std::string& u, const std::string& v) {
        adj_list[u].insert(v);
    }

    bool has_edge(const std::string& u, const std::string& v) const {
        auto it = adj_list.find(u);
        if (it == adj_list.end()) return false;
        return it->second.find(v) != it->second.end();
    }

    int node_count() const {
        return nodes.size();
    }

    int edge_count() const {
        int count = 0;
        for (const auto& pair : adj_list) {
            count += pair.second.size();
        }
        return count;
    }
};

class MyMotifCounter {
private:
    // Проверка изоморфизма двух графов
    bool are_isomorphic(const Graph& g1, const Graph& g2) {
        if (g1.node_count() != g2.node_count()) return false;
        if (g1.edge_count() != g2.edge_count()) return false;

        int n = g1.node_count();
        std::vector<std::string> nodes1(g1.nodes.begin(), g1.nodes.end());
        std::vector<std::string> nodes2(g2.nodes.begin(), g2.nodes.end());

        std::sort(nodes1.begin(), nodes1.end());
        std::sort(nodes2.begin(), nodes2.end());

        // Генерируем все перестановки вершин второго графа
        std::vector<int> perm(n);
        for (int i = 0; i < n; i++) perm[i] = i;

        do {
            bool is_match = true;

            // Проверяем соответствие ребер при данной перестановке
            for (int i = 0; i < n && is_match; i++) {
                for (int j = 0; j < n && is_match; j++) {
                    bool edge1 = g1.has_edge(nodes1[i], nodes1[j]);
                    bool edge2 = g2.has_edge(nodes2[perm[i]], nodes2[perm[j]]);

                    if (edge1 != edge2) {
                        is_match = false;
                    }
                }
            }

            if (is_match) return true;

        } while (std::next_permutation(perm.begin(), perm.end()));

        return false;
    }

public:
    MyMotifCounter() {}

    py::list count_motifs_fast(py::list g_nodes, py::list g_edges, int n, py::list motifs_list, int motif_size, int num_threads = 4) {
        // Создаем граф
        Graph graph;
        for (auto node : g_nodes){
            graph.add_node((py::str(node)).cast<std::string>());
        }

        for (auto edge : g_edges) {
            py::tuple edge_tuple = edge.cast<py::tuple>();
            std::string u = (py::str(edge_tuple[0])).cast<std::string>();
            std::string v = (py::str(edge_tuple[1])).cast<std::string>();
            graph.add_edge(u, v);
        }

        // Создаем мотивы для сравнения
        std::vector<Graph> motifs;
        for (auto motif_edges_item : motifs_list) {
            py::list motif_edges = motif_edges_item.cast<py::list>();
            Graph motif_graph;

            for (char c = 'A'; c - 'A' < motif_size; c++){
                motif_graph.add_node(std::string(1, c));
            }

            for (auto edge : motif_edges) {
                py::tuple edge_tuple = edge.cast<py::tuple>();
                std::string u = edge_tuple[0].cast<std::string>();
                std::string v = edge_tuple[1].cast<std::string>();
                motif_graph.add_edge(u, v);
            }
            motifs.push_back(motif_graph);
        }

        // Инициализируем счетчики
        std::vector<int> counts(motifs.size(), 0);

        // Получаем все вершины графа
        std::vector<std::string> graph_nodes(graph.nodes.begin(), graph.nodes.end());

        // Устанавливаем количество потоков
        omp_set_num_threads(num_threads);

        // Перебираем все комбинации из motif_size вершин
        if (n >= motif_size) {
            // Генерируем все комбинации заранее
            std::vector<std::vector<int>> all_combinations;
            std::vector<bool> selector(n);
            std::fill(selector.end() - motif_size, selector.end(), true);

            do {
                std::vector<int> combination;
                for (int i = 0; i < n; i++) {
                    if (selector[i]) {
                        combination.push_back(i);
                    }
                }
                all_combinations.push_back(combination);
            } while (std::next_permutation(selector.begin(), selector.end()));

            // Параллельная обработка комбинаций
            #pragma omp parallel
            {
                // Локальные счетчики для каждого потока
                std::vector<int> local_counts(motifs.size(), 0);

                #pragma omp for schedule(dynamic, 100)
                for (int idx = 0; idx < all_combinations.size(); idx++) {
                    const auto& combination = all_combinations[idx];

                    std::vector<std::string> selected_nodes;
                    for (int node_idx : combination) {
                        selected_nodes.push_back(graph_nodes[node_idx]);
                    }

                    // Создаем подграф на выбранных вершинах
                    Graph subgraph;
                    for (const auto& node : selected_nodes) {
                        subgraph.add_node(node);
                    }

                    // Добавляем только те ребра, где оба конца в selected_nodes
                    for (const auto& u : selected_nodes) {
                        for (const auto& v : selected_nodes) {
                            if (u != v && graph.has_edge(u, v)) {
                                subgraph.add_edge(u, v);
                            }
                        }
                    }

                    // Сравниваем подграф с каждым мотивом
                    for (size_t i = 0; i < motifs.size(); i++) {
                        if (are_isomorphic(subgraph, motifs[i])) {
                            local_counts[i]++;
                            break;  // Подграф может соответствовать только одному мотиву
                        }
                    }
                }

                // Объединение результатов из разных потоков
                #pragma omp critical
                {
                    for (size_t i = 0; i < counts.size(); i++) {
                        counts[i] += local_counts[i];
                    }
                }
            }
        }

        py::list result;
        for (int c : counts) {
            result.append(c);
        }
        return result;
    }
};

#endif // MY_MOTIF_COUNTER_H