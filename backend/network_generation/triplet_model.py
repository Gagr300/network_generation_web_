import networkx as nx
from dotmotif import Motif, GrandIsoExecutor
from random import randrange, choices
from itertools import permutations
from typing import Callable
from .triplets import motifs
import numpy as np
from typing import Literal
from .cpp_module import motif_counter_cpp


class SubgraphStructure:
    class SubgraphType:
        def __init__(self, motif, count, index) -> None:
            self.index = index
            self.motif = motif
            self.count = count
            self.nodes = set(a for a, b in motif.motif.list_edge_constraints().keys()) | set(
                b for a, b in motif.motif.list_edge_constraints().keys())
            self.probability = {'frequency': 0,
                                'soft-max': 0}

    def __init__(self, graph, motif_size=3, use_cpp_module=True):
        self.motif_subgraphs = {}
        self.graph = graph
        self.motifs_sum, self.motif_sum_exp = 0, 0
        self.inv_graph = nx.difference(nx.complete_graph(graph.nodes(), nx.DiGraph()), graph)
        self.E = GrandIsoExecutor(graph=self.graph)
        self.E_inv = GrandIsoExecutor(graph=self.inv_graph)
        self.num_of_motifs = len(motifs[motif_size])
        self.motif_size = motif_size

        if use_cpp_module:
            # с использованием модуля на C++
            self.cpp_counter = motif_counter_cpp.MyMotifCounter()

            # список вершин и ребер графа
            nodes_list = list(graph.nodes())
            edges_list = list(graph.edges())

            # подсчет мотивов
            motif_counts = self.cpp_counter.count_motifs_fast(
                nodes_list,
                edges_list,
                len(graph.nodes()),
                [mtf.edges for mtf in motifs[self.motif_size]],
                self.motif_size
            )

            # определение SubgraphType
            for i, count in enumerate(motif_counts):
                self.motif_subgraphs[motifs[motif_size][i].motif] = \
                    self.SubgraphType(motifs[motif_size][i], count, i)
                self.motifs_sum += count
        else:
            # использование dotmotif
            for i in range(self.num_of_motifs):
                # если рассматривается мотив - слабо связный подграф
                if nx.is_weakly_connected(motifs[self.motif_size][i].digraph):
                    motif_count = len(self.E.find(motifs[self.motif_size][i].motif)) // \
                                  motifs[self.motif_size][i].isomorphism
                # если рассматривется состоение подграфа, которое не является мотивом
                else:
                    opos_idx = motifs[self.motif_size][i].opposite_graph_index
                    if nx.is_weakly_connected(motifs[self.motif_size][opos_idx].digraph):
                        motif_count = len(self.E_inv.find(motifs[self.motif_size][opos_idx].motif)) // \
                                      motifs[self.motif_size][opos_idx].isomorphism
                    else:
                        pass
                self.motif_subgraphs[motifs[self.motif_size][i].motif] = self.SubgraphType(
                    motifs[self.motif_size][i], motif_count, i)
                self.motifs_sum += motif_count

        self.mx_v = max((self.motif_subgraphs[x].count for x in self.motif_subgraphs))
        self.motif_sum_exp = np.sum(
            (np.exp((self.motif_subgraphs[x].count - self.mx_v) / 0.3) for x in self.motif_subgraphs))

        # вычисление верочтностей
        if self.motifs_sum > 0:
            for x in self.motif_subgraphs:
                self.motif_subgraphs[x].probability['frequency'] = self.motif_subgraphs[x].count / self.motifs_sum
                self.motif_subgraphs[x].probability['laplace'] = (self.motif_subgraphs[x].count + 1) / (
                        self.motifs_sum + len(self.motif_subgraphs))
                self.motif_subgraphs[x].probability['soft-max'] = np.exp(
                    (self.motif_subgraphs[x].count - self.mx_v) / 0.3) / self.motif_sum_exp


class RandomGraphGenerator:
    def __init__(self, graph, motif_size=3) -> None:
        self.graph = graph                  # граф, на основе которого будут генерироваться новые (исходный)
        self.N = len(self.graph.nodes())    # количество вершин в исходном графе
        self.M = len(self.graph.edges())    # количество дуг в исходном графе
        self.subgraphStructure = SubgraphStructure(self.graph, motif_size)
        self.motif_size = motif_size        # количество вершин в подграфах
        self.progress_callback = None       # отслеживание прогресса
        indegree, outdegree = list(d for n, d in self.graph.in_degree()), list(d for n, d in self.graph.out_degree())
        self.node_selection_probability = sorted([x + y for x, y in zip(indegree, outdegree)])

    def set_progress_callback(self, callback: Callable[[int, int], None]):
        # отслеживание прогресса
        self.progress_callback = callback

    def wegner_multiplet_model(self, new_n=None,
                               probability_type: Literal['frequency', 'laplace', 'soft-max'] = 'frequency',
                               use_nodes_probability=True):
        # если требуется граф того же размера, что и исходный
        if new_n is None:
            new_n = self.N
            new_m = self.M
            degree_sum = sum(self.node_selection_probability)
            node_selection_probability = [x / degree_sum for x in self.node_selection_probability]
        # если было задано иное необходимое количество вершин в генерируемом графе
        else:
            new_m = int(self.M / self.N * new_n)
            node_selection_probability = self.node_selection_probability * (new_n // self.N) + [
                self.node_selection_probability[randrange(self.N)] for _ in range(new_n % self.N)]
            degree_sum = sum(node_selection_probability)
            node_selection_probability = [x / degree_sum for x in node_selection_probability]

        # создание пустого графа с new_n вершинами
        new_graph = nx.DiGraph()
        new_graph.add_nodes_from([i for i in range(new_n)])

        iteration = 0
        max_iterations = new_m * 100

        while len(new_graph.edges()) < new_m and iteration < max_iterations:
            iteration += 1

            # выбор подмножества вершин
            if use_nodes_probability:
                selected_nodes = np.random.choice(range(new_n), size=self.motif_size, replace=False,
                                                  p=node_selection_probability)

            else:
                selected_nodes = [randrange(new_n) for _ in range(self.motif_size)]
                if len(set(selected_nodes)) < self.motif_size:
                    continue
            # подграф на выбранных вершинах
            subgraph = nx.DiGraph(new_graph.subgraph(selected_nodes))

            # определение текущего состояния подграфа
            cur_motif = \
                [i for i in range(len(motifs[self.motif_size])) if
                 nx.is_isomorphic(motifs[self.motif_size][i].digraph, subgraph)][0]
            possible_motif_indices = motifs[self.motif_size][cur_motif].possible_motifs # возможные "надстройки"
            weights = [max(0.0001,
                           self.subgraphStructure.motif_subgraphs[
                               motifs[self.motif_size][idx].motif].probability[
                               probability_type]) for idx in
                       possible_motif_indices]
            normalized_weights = [w / sum(weights) for w in weights]

            rnd_motif_subgraph = choices(possible_motif_indices, weights=normalized_weights)[0]

            # поиск оптимальной перестановки вершин
            best_dict = None
            min_dif = 1000

            for perm_nodes in permutations(selected_nodes):
                dict_nodes = {x: y for x, y in
                              zip((chr(ord('A') + i) for i in range(self.motif_size)), perm_nodes)}
                subgraph = nx.DiGraph(new_graph.subgraph(perm_nodes))
                subgraph.add_edges_from(
                    [(dict_nodes[i], dict_nodes[j]) for i, j in
                     motifs[self.motif_size][rnd_motif_subgraph].edges])

                dif = len(subgraph.edges()) - len(motifs[self.motif_size][rnd_motif_subgraph].edges)

                if dif < min_dif:
                    min_dif = dif
                    best_dict = dict_nodes

            # добавление ребер в результирующий граф
            new_graph.add_edges_from(
                [(best_dict[i], best_dict[j]) for i, j in motifs[self.motif_size][rnd_motif_subgraph].edges])

            # обновление прогресса
            if self.progress_callback:
                self.progress_callback(len(new_graph.edges()), new_m)

        # если граф не был сгенерирован
        if iteration >= max_iterations:
            print(f"Warning: Reached maximum iterations ({max_iterations})")
        return new_graph
