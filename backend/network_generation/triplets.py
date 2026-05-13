from dotmotif import Motif
import networkx as nx
from itertools import combinations, product, permutations
from networkx.algorithms.isomorphism import DiGraphMatcher

edge_definitions = """
oneWayEdge(a, b) {
    a -> b
    b !> a
}
twoWayEdge(a, b) {
    a -> b
    b -> a
}
noWayEdge(a, b) {
    a !> b
    b !> a
}
"""


class MyMotif:
    def __init__(self, n, digraph):
        self.n = n  # количетсво вершин в мотиве
        self.digraph = digraph  # DiGraph
        self.motif_string = self.graph_to_motif()  # строка для генерации объекта Motif
        print(self.motif_string)
        self.motif = Motif(self.motif_string)  # Motif
        self.edges = list(self.digraph.edges())  # список дуг
        self.possible_motifs = []  # индексы мотивов, которые могут быть получены на его основе
        self.opposite_graph_index = None  # индекс противоположного мотива
        self.isomorphism = len(list(DiGraphMatcher(self.digraph, self.digraph).subgraph_isomorphisms_iter()))

    def set_attrs(self, **kwargs):
        """
        Установка значений атрибутов
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Неверный атрибут {key}")

    def graph_to_motif(self):
        """
        Преобразует граф в строку мотива и мотив для библиотеки dotmotif
        """
        motif_lines = []
        nodes = list(self.digraph.nodes())
        for i in range(self.n):
            v = nodes[i]
            for j in range(i + 1, self.n):
                u = nodes[j]
                # есть дуги в обе стороны
                if self.digraph.has_edge(v, u) and self.digraph.has_edge(u, v):
                    motif_lines.append(f"twoWayEdge({v}, {u})")
                # есть одна дуга в одну сторону
                elif self.digraph.has_edge(v, u):
                    motif_lines.append(f"oneWayEdge({v}, {u})")
                # есть одна дуга в другую сторону
                elif self.digraph.has_edge(u, v):
                    motif_lines.append(f"oneWayEdge({u}, {v})")
                # нет дуг
                else:
                    motif_lines.append(f"noWayEdge({v}, {u})")

        # полная строка для генерации объекта Motif
        return edge_definitions + "\n" + "\n".join(motif_lines)


motifs = {}


def generate_all_digraphs(n, nodes):
    """
    Генерирует все возможные ориентированные графы на n вершинах
    """
    all_edges = list(combinations(nodes, 2))

    """
    Для каждой пары вершин в соответствие ставится одно из 4 состояний:
    0 - нет дуг
    1 - дуга v->u
    2 - дуга u->v
    3 - две дуги
    """

    all_graphs = []

    for edge_states in product([0, 1, 2, 3], repeat=len(all_edges)):
        G = nx.DiGraph()
        G.add_nodes_from(nodes)

        # добавление дуг
        for (v, u), state in zip(all_edges, edge_states):
            if state == 1:
                G.add_edge(v, u)
            elif state == 2:
                G.add_edge(u, v)
            elif state == 3:
                G.add_edge(v, u)
                G.add_edge(u, v)

        # проверка на изоморфность
        is_isomorphic = False
        for existing in all_graphs:
            if nx.is_isomorphic(G, existing):
                is_isomorphic = True
                break

        if not is_isomorphic:
            all_graphs.append(G)

    return all_graphs


def graph_in_another(nodes, pattern_edges, graph_edges):
    """
    Проверяет, встречается ли один граф-паттерн в другом
    """
    if len(pattern_edges) > len(graph_edges):
        return False
    graph_edges_set = set(graph_edges)

    # перебор всех комбинаций отображений
    for mapping_tuple in permutations(nodes, len(nodes)):
        mapping = {nodes[i]: mapping_tuple[i] for i in range(len(nodes))}
        pattern_matched = True
        for u, v in pattern_edges:
            mapped_u = mapping[u]
            mapped_v = mapping[v]
            if (mapped_u, mapped_v) not in graph_edges_set:
                pattern_matched = False
                break

        if pattern_matched:
            return True

    return False


def generate_motifs(n):
    """
    Генерация всех мотивов на n вершинах
    """
    nodes = [chr(65 + i) for i in range(n)]

    print(f"Генерация всех мотивов для {n} вершин...")
    motifs_digraphs = sorted(list(generate_all_digraphs(n, nodes)), key=lambda g: len(g.edges()))
    print(f"Найдено {len(motifs_digraphs)} неизоморфных ориентированных графов")
    motifs[n] = [MyMotif(n, DiG) for DiG in motifs_digraphs]

    def get_opposite_motif_index(motif_index):
        """
        Вычисляет индекс противоположного мотива для заданного мотива.
        """
        if motif_index < 0 or motif_index >= len(motifs_digraphs):
            raise ValueError(f"Motif index {motif_index} out of range for size {n}")

        # противоположный граф (разность полного графа и исходного)
        complement_graph = nx.DiGraph()
        complement_graph.add_nodes_from(nodes)

        for i in range(n):
            a = nodes[i]
            for j in range(i + 1, n):
                b = nodes[j]
                has_ij = motifs[n][motif_index].digraph.has_edge(a, b)
                has_ji = motifs[n][motif_index].digraph.has_edge(b, a)

                """
                noWayEdge (0,0) → twoWayEdge (1,1)
                twoWayEdge (1,1) → noWayEdge (0,0)
                oneWayEdge i->j (1,0) → oneWayEdge j->i (0,1)
                oneWayEdge j->i (0,1) → oneWayEdge i->j (1,0)
                """

                if not has_ij and not has_ji:  # noWayEdge
                    complement_graph.add_edge(a, b)
                    complement_graph.add_edge(b, a)
                elif has_ij and has_ji:  # twoWayEdge
                    pass
                elif has_ij and not has_ji:  # oneWayEdge i->j
                    complement_graph.add_edge(b, a)
                elif not has_ij and has_ji:  # oneWayEdge j->i
                    complement_graph.add_edge(a, b)

        # поиск индекса противоположного мотива
        for _idx, candidate in enumerate(motifs[n]):
            if nx.is_isomorphic(complement_graph, candidate.digraph):
                return _idx

        print(f"Warning: Complement motif not found for index {motif_index} (size {n})")
        return -1

    for idx in range(len(motifs[n])):
        # получение индекса противоположного мотива
        motifs[n][idx].set_attrs(opposite_graph_index=get_opposite_motif_index(idx))

        # получение возможных "надстроек"
        for idx2, H in enumerate(motifs_digraphs):
            if graph_in_another(nodes, motifs[n][idx].digraph.edges(), H.edges()):
                motifs[n][idx].possible_motifs.append(idx2)


for k in range(2, 4):
    generate_motifs(k)
