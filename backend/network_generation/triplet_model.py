import networkx as nx
from dotmotif import Motif, GrandIsoExecutor
from random import randrange, choices, choice
from itertools import permutations
from typing import Callable, Optional
from .triplets import motifs, motifs_edges, motifs_digraphs, possible_motifs, opposite_graph_index


class SubgraphStructure:
    class SubgraphType:
        def __init__(self, motif, count, index) -> None:
            self.index = index
            self.motif = motif
            self.count = count
            self.nodes = set(a for a, b in motifs[3][0].list_edge_constraints().keys()) | set(
                b for a, b in motifs[3][0].list_edge_constraints().keys())
            self.probability = 0

    def __init__(self, graph, num_of_nodes_in_motif=3):
        self.motif_subgraphs = {}
        self.graph = graph
        self.motifs_sum = 0
        self.inv_graph = nx.difference(nx.complete_graph(graph.nodes(), nx.DiGraph()), graph)
        self.E = GrandIsoExecutor(graph=self.graph)
        self.E_inv = GrandIsoExecutor(graph=self.inv_graph)
        self.num_of_motifs = len(motifs[num_of_nodes_in_motif])
        self.num_of_nodes_in_motif = num_of_nodes_in_motif

        for i in range(self.num_of_motifs):
            if nx.is_weakly_connected(motifs_digraphs[self.num_of_nodes_in_motif][i]):
                motif_count = len(self.E.find(motifs[self.num_of_nodes_in_motif][i]))
            else:
                if nx.is_weakly_connected(motifs_digraphs[self.num_of_nodes_in_motif][opposite_graph_index[self.num_of_nodes_in_motif][i]]):
                    motif_count = len(self.E_inv.find(motifs[self.num_of_nodes_in_motif][opposite_graph_index[self.num_of_nodes_in_motif][i]]))
                else:
                    print(self.num_of_nodes_in_motif, i, motifs_edges[self.num_of_nodes_in_motif][i])
            self.motif_subgraphs[motifs[self.num_of_nodes_in_motif][i]] = self.SubgraphType(
                motifs[self.num_of_nodes_in_motif][i],
                motif_count, i)
            self.motifs_sum += motif_count
        self.left_probabilities = [0] * len(motifs[self.num_of_nodes_in_motif])

        if self.motifs_sum > 0:
            for x in self.motif_subgraphs:
                self.motif_subgraphs[x].probability = self.motif_subgraphs[x].count / self.motifs_sum
                self.left_probabilities[self.motif_subgraphs[x].index] = self.motif_subgraphs[x].probability


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

    def wegner_multiplet_model(self):
        new_graph = nx.DiGraph()
        new_graph.add_nodes_from([i for i in range(self.N)])

        iteration = 0
        max_iterations = self.M * 100

        while len(new_graph.edges()) < self.M and iteration < max_iterations:
            iteration += 1

            # тройка вершин
            selected_nodes = [randrange(self.N) for _ in range(self.num_of_nodes_in_motif)]
            if len(set(selected_nodes)) < self.num_of_nodes_in_motif:
                continue

            # определение возможных мотивов
            triangle = nx.DiGraph(new_graph.subgraph(selected_nodes))
            cur_motif = \
                [i for i in range(len(motifs[self.num_of_nodes_in_motif])) if
                 nx.is_isomorphic(motifs_digraphs[self.num_of_nodes_in_motif][i], triangle)][0]
            possible_motif_indices = possible_motifs[self.num_of_nodes_in_motif][cur_motif]
            weights = [max(0.0001, self.subgraphStructure.left_probabilities[idx]) for idx in possible_motif_indices]
            normalized_weights = [w / sum(weights) for w in weights]

            rnd_motif_subgraph = choices(possible_motif_indices, weights=normalized_weights)[0]

            # поиск оптимальной перестановки вершин
            best_dict = None
            min_dif = 1000

            for perm_nodes in permutations(selected_nodes):
                dict_nodes = {x: y for x, y in
                              zip((chr(ord('A') + i) for i in range(self.num_of_nodes_in_motif)), perm_nodes)}
                triangle = nx.DiGraph(new_graph.subgraph(perm_nodes))
                triangle.add_edges_from(
                    [(dict_nodes[i], dict_nodes[j]) for i, j in
                     motifs_edges[self.num_of_nodes_in_motif][rnd_motif_subgraph]])

                dif = len(triangle.edges()) - len(motifs_edges[self.num_of_nodes_in_motif][rnd_motif_subgraph])

                if dif < min_dif:
                    min_dif = dif
                    best_dict = dict_nodes

            # добавление ребер в результирующий граф
            new_graph.add_edges_from(
                [(best_dict[i], best_dict[j]) for i, j in motifs_edges[self.num_of_nodes_in_motif][rnd_motif_subgraph]])

            # обновление прогресса
            if self.progress_callback:
                self.progress_callback(len(new_graph.edges()), self.M)

        if iteration >= max_iterations:
            print(f"Warning: Reached maximum iterations ({max_iterations})")

        return new_graph
