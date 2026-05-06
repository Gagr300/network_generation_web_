import networkx as nx
from dotmotif import Motif, GrandIsoExecutor
from random import randrange, choices, choice
from itertools import permutations
from typing import Callable, Optional
from .triplets import motifs
import numpy as np
from typing import Literal


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

    def __init__(self, graph, num_of_nodes_in_motif=3):
        self.motif_subgraphs = {}
        self.graph = graph
        self.motifs_sum, self.motif_sum_exp = 0, 0
        self.inv_graph = nx.difference(nx.complete_graph(graph.nodes(), nx.DiGraph()), graph)
        self.E = GrandIsoExecutor(graph=self.graph)
        self.E_inv = GrandIsoExecutor(graph=self.inv_graph)
        self.num_of_motifs = len(motifs[num_of_nodes_in_motif])
        self.num_of_nodes_in_motif = num_of_nodes_in_motif

        for i in range(self.num_of_motifs):
            if nx.is_weakly_connected(motifs[self.num_of_nodes_in_motif][i].digraph):
                motif_count = len(self.E.find(motifs[self.num_of_nodes_in_motif][i].motif)) / \
                              motifs[self.num_of_nodes_in_motif][i].isomorphism
            else:
                opos_idx = motifs[self.num_of_nodes_in_motif][i].opposite_graph_index
                if nx.is_weakly_connected(motifs[self.num_of_nodes_in_motif][opos_idx].digraph):
                    motif_count = len(self.E_inv.find(motifs[self.num_of_nodes_in_motif][opos_idx].motif)) / \
                                  motifs[self.num_of_nodes_in_motif][opos_idx].isomorphism
                else:
                    pass
            self.motif_subgraphs[motifs[self.num_of_nodes_in_motif][i].motif] = self.SubgraphType(
                motifs[self.num_of_nodes_in_motif][i], motif_count, i)
            self.motifs_sum += motif_count

        self.mx_v = max((self.motif_subgraphs[x].count for x in self.motif_subgraphs))
        self.motif_sum_exp = np.sum(
            (np.exp((self.motif_subgraphs[x].count - self.mx_v) / 0.3) for x in self.motif_subgraphs))
        if self.motifs_sum > 0:
            for x in self.motif_subgraphs:
                self.motif_subgraphs[x].probability['frequency'] = self.motif_subgraphs[x].count / self.motifs_sum
                self.motif_subgraphs[x].probability['laplace'] = (self.motif_subgraphs[x].count + 1) / (
                        self.motifs_sum + len(self.motif_subgraphs))
                self.motif_subgraphs[x].probability['soft-max'] = np.exp(
                    (self.motif_subgraphs[x].count - self.mx_v) / 0.3) / self.motif_sum_exp


class RandomGraphGenerator:
    def __init__(self, graph, num_of_nodes_in_motif=3) -> None:
        self.graph = graph
        self.N = len(self.graph.nodes())
        self.M = len(self.graph.edges())
        self.subgraphStructure = SubgraphStructure(self.graph, num_of_nodes_in_motif)
        self.num_of_nodes_in_motif = num_of_nodes_in_motif
        self.progress_callback = None  # отслеживание прогресса

    def set_progress_callback(self, callback: Callable[[int, int], None]):
        self.progress_callback = callback

    def wegner_multiplet_model(self, new_n=None,
                               probability_type: Literal['frequency', 'laplace', 'soft-max'] = 'frequency'):
        if new_n is None:
            new_n = self.N
            new_m = self.M
        else:
            new_m = int(self.M / self.N * new_n)

        mx_in_degrees = max((d for n, d in self.graph.in_degree()))
        mx_out_degrees = max((d for n, d in self.graph.out_degree()))

        new_graph = nx.DiGraph()
        new_graph.add_nodes_from([i for i in range(new_n)])

        iteration = 0
        max_iterations = new_m * 100
        print(1)

        while len(new_graph.edges()) < new_m and iteration < max_iterations:
            iteration += 1
            print(2 - iteration)

            # тройка вершин
            selected_nodes = [randrange(new_n) for _ in range(self.num_of_nodes_in_motif)]
            if len(set(selected_nodes)) < self.num_of_nodes_in_motif:
                continue

            # определение возможных мотивов
            triangle = nx.DiGraph(new_graph.subgraph(selected_nodes))
            cur_motif = \
                [i for i in range(len(motifs[self.num_of_nodes_in_motif])) if
                 nx.is_isomorphic(motifs[self.num_of_nodes_in_motif][i].digraph, triangle)][0]
            possible_motif_indices = motifs[self.num_of_nodes_in_motif][cur_motif].possible_motifs
            weights = [max(0.0001,
                           self.subgraphStructure.motif_subgraphs[
                               motifs[self.num_of_nodes_in_motif][idx].motif].probability[
                               probability_type]) for idx in
                       possible_motif_indices]
            normalized_weights = [w / sum(weights) for w in weights]

            rnd_motif_subgraph = choices(possible_motif_indices, weights=normalized_weights)[0]

            print(3)
            # поиск оптимальной перестановки вершин
            best_dict = None
            min_dif = 1000

            for perm_nodes in permutations(selected_nodes):
                print(4)
                dict_nodes = {x: y for x, y in
                              zip((chr(ord('A') + i) for i in range(self.num_of_nodes_in_motif)), perm_nodes)}
                triangle = nx.DiGraph(new_graph.subgraph(perm_nodes))
                triangle.add_edges_from(
                    [(dict_nodes[i], dict_nodes[j]) for i, j in
                     motifs[self.num_of_nodes_in_motif][rnd_motif_subgraph].edges])

                dif = len(triangle.edges()) - len(motifs[self.num_of_nodes_in_motif][rnd_motif_subgraph].edges)

                if dif < min_dif:
                    min_dif = dif
                    best_dict = dict_nodes

            # добавление ребер в результирующий граф
            new_graph.add_edges_from(
                [(best_dict[i], best_dict[j]) for i, j in motifs[self.num_of_nodes_in_motif][rnd_motif_subgraph].edges])

            # обновление прогресса
            if self.progress_callback:
                self.progress_callback(len(new_graph.edges()), new_m)

        if iteration >= max_iterations:
            print(f"Warning: Reached maximum iterations ({max_iterations})")
        print(new_graph.edges())
        return new_graph
