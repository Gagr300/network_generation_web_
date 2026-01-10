import networkx as nx
from dotmotif import Motif, GrandIsoExecutor
from random import randrange, choices, choice
from itertools import permutations
from typing import Callable, Optional
from .triplets import motifs, motifs_edges, motifs_digraphs


class SubgraphStructure:
    class SubgraphType:
        def __init__(self, motif, count, index) -> None:
            self.index = index
            self.motif = motif
            self.count = count
            self.nodes = set(a for a, b in motifs[0].list_edge_constraints().keys()) | set(
                b for a, b in motifs[0].list_edge_constraints().keys())
            self.probability = 0

    def __init__(self, graph, motif_types):
        self.motif_subgraphs = {}
        self.graph = graph
        self.motifs_sum = 0
        self.inv_graph = nx.difference(nx.complete_graph(graph.nodes(), nx.DiGraph()), graph)
        self.E = GrandIsoExecutor(graph=self.graph)
        self.E_inv = GrandIsoExecutor(graph=self.inv_graph)
        for i in range(len(motif_types)):
            if i == 0:  # no edges at all
                motif_count = len(self.E_inv.find(motif_types[15]))  # full_graph
            elif i == 1:  #
                motif_count = len(self.E_inv.find(motif_types[14]))  # oneway twoway twoway
            elif i == 2:
                motif_count = len(self.E_inv.find(motif_types[8]))  # noway twoway twoway
            else:
                motif_count = len(self.E.find(motif_types[i]))
            self.motif_subgraphs[motif_types[i]] = self.SubgraphType(motif_types[i], motif_count, i)
            self.motifs_sum += motif_count
        self.left_probabilities = [0] * len(motif_types)

        if self.motifs_sum > 0:
            for x in self.motif_subgraphs:
                self.motif_subgraphs[x].probability = self.motif_subgraphs[x].count / self.motifs_sum
                self.left_probabilities[self.motif_subgraphs[x].index] = self.motif_subgraphs[x].probability


class RandomGraphGenerator:
    def __init__(self, graph, motif_types) -> None:
        self.graph = graph
        self.N = len(self.graph.nodes())
        self.M = len(self.graph.edges())
        self.subgraphStructure = SubgraphStructure(self.graph, motif_types)
        self.motif_types = motif_types
        self.possible_motifs = {
            0: list(range(16)),
            1: list(range(1, 16)),
            2: [2, 6, 7, 8, 11, 12, 13, 14, 15],
            3: [3, 6, 8, 10, 11, 12, 13, 14, 15],
            4: [4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            5: [5, 7, 8, 10, 11, 12, 13, 14, 15],
            6: [6, 8, 12, 13, 14, 15],
            7: [7, 8, 11, 13, 14, 15],
            8: [8, 14, 15],
            9: [9, 13, 14, 15],
            10: [10, 11, 14, 15],
            11: [11, 14, 15],
            12: [12, 14, 15],
            13: [13, 14, 15],
            14: [14, 15],
            15: [15]
        }
        self.progress_callback = None  # отслеживание прогресса

    def set_progress_callback(self, callback: Callable[[int, int], None]):
        self.progress_callback = callback

    def wegner_multiplet_model(self):
        print('wegner_multiplet_model')
        new_graph = nx.DiGraph()
        new_graph.add_nodes_from([i for i in range(self.N)])

        iteration = 0
        max_iterations = self.M * 100

        while len(new_graph.edges()) < self.M and iteration < max_iterations:
            iteration += 1

            # тройка вершин
            a, b, c = randrange(self.N), randrange(self.N), randrange(self.N)
            if a == b or b == c or a == c:
                continue

            # определение возможных мотивов
            triangle = nx.DiGraph(new_graph.subgraph([a, b, c]))
            cur_motif = [i for i in range(16) if nx.is_isomorphic(motifs_digraphs[i], triangle)][0]
            possible_motif_indices = self.possible_motifs[cur_motif]
            weights = [max(0.0001, self.subgraphStructure.left_probabilities[idx]) for idx in possible_motif_indices]
            normalized_weights = [w / sum(weights) for w in weights]

            rnd_motif_subgraph = choices(possible_motif_indices, weights=normalized_weights)[0]

            # поиск оптимальной перестановки вершин
            best_dict = None
            min_dif = 1000

            for A, B, C in permutations([a, b, c]):
                dict_nodes = {'A': A, 'B': B, 'C': C}
                triangle = nx.DiGraph(new_graph.subgraph([a, b, c]))
                triangle.add_edges_from([(dict_nodes[i], dict_nodes[j]) for i, j in motifs_edges[rnd_motif_subgraph]])

                dif = len(triangle.edges()) - len(motifs_edges[rnd_motif_subgraph])

                if dif < min_dif:
                    min_dif = dif
                    best_dict = dict_nodes

            # добавление ребер в результирующий граф
            new_graph.add_edges_from([(best_dict[i], best_dict[j]) for i, j in motifs_edges[rnd_motif_subgraph]])

            # обновление прогресса
            if self.progress_callback:
                self.progress_callback(len(new_graph.edges()), self.M)

        if iteration >= max_iterations:
            print(f"Warning: Reached maximum iterations ({max_iterations})")

        return new_graph
