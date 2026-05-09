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
        //std::cout << "g1\n";
        //for (auto x : nodes1){
        //    for(auto y : nodes1){
        //        if (g1.has_edge(x,y)) std::cout << x << ' ' << y << '\n';
        //    }
        //}
        //std::cout << "g2\n";
        //for (auto x : nodes2){
        //    for(auto y : nodes2){
        //        if (g2.has_edge(x,y)) std::cout << x << ' ' << y << '\n';
        //    }
        //}


        // Генерируем все перестановки вершин второго графа
        std::vector<int> perm(n);
        for (int i = 0; i < n; i++) perm[i] = i;

        do {
            bool is_match = true;

            // Проверяем соответствие ребер при данной перестановке
            for (int i = 0; i < n && is_match; i++) {
                //std::cout << nodes1[i] << '-' << nodes2[perm[i]] << ' ';
                for (int j = 0; j < n && is_match; j++) {
                    bool edge1 = g1.has_edge(nodes1[i], nodes1[j]);
                    bool edge2 = g2.has_edge(nodes2[perm[i]], nodes2[perm[j]]);

                    if (edge1 != edge2) {
                        is_match = false;
                    }
                }
            }
            //std::cout << '\n';

            if (is_match) return true;

        } while (std::next_permutation(perm.begin(), perm.end()));

        return false;
    }

public:
    MyMotifCounter() {}

    py::list count_motifs_fast(py::list g_nodes, py::list g_edges, int n, py::list motifs_list, int motif_size) {
        //std::cout << "=== count_motifs_fast ===" << std::endl;
        //std::cout << "n=" << n << ", edges=" << g_edges.size()
        //          << ", motifs=" << motifs_list.size() << ", size=" << motif_size << std::endl;

        // Создаем граф
        Graph graph;
        for (auto node : g_nodes){
            graph.add_node((py::str(node)).cast<std::string>());
        }

        for (auto edge : g_edges) {
            py::tuple edge_tuple = edge.cast<py::tuple>();
            py::str tmp = py::str(edge_tuple[0]);
            std::string u = (py::str(edge_tuple[0])).cast<std::string>();
            std::string v = (py::str(edge_tuple[1])).cast<std::string>();
            graph.add_edge(u, v);
        }

        //std::cout << "Graph has " << graph.node_count() << " nodes and "
        //         << graph.edge_count() << " edges" << std::endl;

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

        // Перебираем все комбинации из motif_size вершин
        if (n >= motif_size) {
            std::vector<bool> selector(n);
            std::fill(selector.end() - motif_size, selector.end(), true);

            int combination_count = 0;

            do {
                std::vector<std::string> selected_nodes;
                for (int i = 0; i < n; i++) {
                    if (selector[i]) {
                        selected_nodes.push_back(graph_nodes[i]);
                    }
                }

                // Создаем подграф на выбранных вершинах
                Graph subgraph;
                for (const auto& node : selected_nodes) {
                    subgraph.add_node(node);
                }
                //std:: cout<< std::string(10, '-') << '\n';
                //for (auto x : subgraph.nodes) {
                //    std::cout << x << ' ';
                //}
                //std::cout << '\n';
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
                    //std::cout << i << ' ';
                    if (are_isomorphic(subgraph, motifs[i])) {
                        //std::cout << '+' << '\n';
                        counts[i]++;
                        break;  // Подграф может соответствовать только одному мотиву
                    }
                }

                combination_count++;

                // Вывод прогресса для больших графов
                //if (combination_count % 100000 == 0) {
                //    std::cout << "Processed " << combination_count << " combinations..." << std::endl;
                //}

            } while (std::next_permutation(selector.begin(), selector.end()));

            //std::cout << "Total combinations checked: " << combination_count << std::endl;
        }

        // Вывод результатов
        // std::cout << "Results:" << std::endl;
        // for (size_t i = 0; i < counts.size(); i++) {
        //    std::cout << "  Motif " << i << ": " << counts[i] << std::endl;
        //}

        py::list result;
        for (int c : counts) {
            result.append(c);
        }
        return result;
    }
};

#endif // MY_MOTIF_COUNTER_H