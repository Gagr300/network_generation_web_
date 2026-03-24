from dotmotif import Motif
import networkx as nx
from itertools import combinations, product, permutations

'''
possible_motifs = {
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

# Определение всех 16 мотивов для триплетов
motifs = {
    2:
    [# M0
    Motif("""
      noWayEdge(a, b) {
          a !> b
          b !> a
      }
      noWayEdge(A, B)
    """),
    # M1
    Motif("""
      oneWayEdge(a, b) {
          a -> b
          b !> a
      }
      oneWayEdge(A, B)
      """),
    # M2
    Motif("""
      twoWayEdge(a, b) {
          a -> b
          b -> a
      }
      twoWayEdge(A, B)
      """)
    ],
    3:
    [# M0
    Motif("""
      noWayEdge(a, b) {
          a !> b
          b !> a
      }
      noWayEdge(A, B)
      noWayEdge(B, C)
      noWayEdge(A, C)
    """),

    # M1
    Motif("""
      oneWayEdge(a, b) {
          a -> b
          b !> a
      }
      noWayEdge(a, b) {
          a !> b
          b !> a
      }
      oneWayEdge(A, B)
      noWayEdge(B, C)
      noWayEdge(A, C)
    """),

    # M2
    Motif("""
      twoWayEdge(a, b) {
          a -> b
          b -> a
      }
      noWayEdge(a, b) {
          a !> b
          b !> a
      }
      twoWayEdge(A, B)
      noWayEdge(B, C)
      noWayEdge(A, C)
    """),

    # M3
    Motif("""
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
      oneWayEdge(B, A)
      oneWayEdge(B, C)
      noWayEdge(A, C)
    """),

    # M4
    Motif("""
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
      oneWayEdge(B, A)
      oneWayEdge(C, B)
      noWayEdge(A, C)
    """),

    # M5
    Motif("""
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
      oneWayEdge(A, B)
      oneWayEdge(C, B)
      noWayEdge(A, C)
    """),

    # M6
    Motif("""
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
      twoWayEdge(A, B)
      oneWayEdge(B, C)
      noWayEdge(A, C)
    """),

    # M7
    Motif("""
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
      twoWayEdge(A, B)
      oneWayEdge(C, B)
      noWayEdge(A, C)
    """),

    # M8
    Motif("""
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
      twoWayEdge(A, B)
      twoWayEdge(B, C)
      noWayEdge(A, C)
    """),

    # M9
    Motif("""
      oneWayEdge(a, b) {
          a -> b
          b !> a
      }
      oneWayEdge(A, B)
      oneWayEdge(B, C)
      oneWayEdge(C, A)
    """),

    # M10
    Motif("""
      oneWayEdge(a, b) {
          a -> b
          b !> a
      }
      oneWayEdge(A, B)
      oneWayEdge(B, C)
      oneWayEdge(A, C)
    """),

    # M11
    Motif("""
      oneWayEdge(a, b) {
          a -> b
          b !> a
      }
      twoWayEdge(a, b) {
          a -> b
          b -> a
      }
      oneWayEdge(B, A)
      oneWayEdge(B, C)
      twoWayEdge(A, C)
    """),

    # M12
    Motif("""
      oneWayEdge(a, b) {
          a -> b
          b !> a
      }
      twoWayEdge(a, b) {
          a -> b
          b -> a
      }
      oneWayEdge(A, B)
      oneWayEdge(C, B)
      twoWayEdge(A, C)
    """),

    # M13
    Motif("""
      oneWayEdge(a, b) {
          a -> b
          b !> a
      }
      twoWayEdge(a, b) {
          a -> b
          b -> a
      }
      oneWayEdge(A, B)
      twoWayEdge(B, C)
      oneWayEdge(C, A)
    """),

    # M14
    Motif("""
      oneWayEdge(a, b) {
          a -> b
          b !> a
      }
      twoWayEdge(a, b) {
          a -> b
          b -> a
      }
      oneWayEdge(A, B)
      twoWayEdge(B, C)
      twoWayEdge(C, A)
    """),

    # M15
    Motif("""
      twoWayEdge(a, b) {
          a -> b
          b -> a
      }
      twoWayEdge(A, B)
      twoWayEdge(B, C)
      twoWayEdge(C, A)
    """)
],
}

# Список ребер для каждого мотива
motifs_edges = {
    2 : [
        [],  # M0
        [('A', 'B')],  # M1
        [('A', 'B'), ('B', 'A')], # M2
    ],
    3 : [
        [],  # M0
        [('A', 'B')],  # M1
        [('A', 'B'), ('B', 'A')],  # M2
        [('B', 'A'), ('B', 'C')],  # M3
        [('B', 'A'), ('C', 'B')],  # M4
        [('A', 'B'), ('C', 'B')],  # M5
        [('A', 'B'), ('B', 'A'), ('B', 'C')],  # M6
        [('A', 'B'), ('B', 'A'), ('C', 'B')],  # M7
        [('A', 'B'), ('B', 'A'), ('B', 'C'), ('C', 'B')],  # M8
        [('A', 'B'), ('B', 'C'), ('C', 'A')],  # M9
        [('A', 'B'), ('B', 'C'), ('A', 'C')],  # M10
        [('B', 'A'), ('B', 'C'), ('C', 'A'), ('A', 'C')],  # M11
        [('A', 'B'), ('C', 'B'), ('C', 'A'), ('A', 'C')],  # M12
        [('A', 'B'), ('B', 'C'), ('C', 'B'), ('C', 'A')],  # M13
        [('A', 'B'), ('B', 'C'), ('C', 'B'), ('C', 'A'), ('A', 'C')],  # M14
        [('A', 'B'), ('B', 'A'), ('B', 'C'), ('C', 'B'), ('C', 'A'), ('A', 'C')]  # M15
    ],

}

motifs_digraphs = {
    2 : [
        nx.DiGraph({'A': [], 'B': []}),  # M0
        nx.DiGraph({'A': ['B'], 'B': []}),  # M1
        nx.DiGraph({'A': ['B'], 'B': ['A']}),  # M2
    ],
    3 : [
        nx.DiGraph({'A': [], 'B': [], 'C': []}),  # M0
        nx.DiGraph({'A': ['B'], 'B': [], 'C': []}),  # M1
        nx.DiGraph({'A': ['B'], 'B': ['A'], 'C': []}),  # M2
        nx.DiGraph({'A': [], 'B': ['A', 'C'], 'C': []}),  # M3
        nx.DiGraph({'A': [], 'B': ['A'], 'C': ['B']}),  # M4
        nx.DiGraph({'A': ['B'], 'B': [], 'C': ['B']}),  # M5
        nx.DiGraph({'A': ['B'], 'B': ['A', 'C'], 'C': []}),  # M6
        nx.DiGraph({'A': ['B'], 'B': ['A'], 'C': ['B']}),  # M7
        nx.DiGraph({'A': ['B'], 'B': ['A', 'C'], 'C': ['B']}),  # M8
        nx.DiGraph({'A': ['B'], 'B': ['C'], 'C': ['A']}),  # M9
        nx.DiGraph({'A': ['B', 'C'], 'B': ['C'], 'C': []}),  # M10
        nx.DiGraph({'A': ['C'], 'B': ['A', 'C'], 'C': ['A']}),  # M11
        nx.DiGraph({'A': ['B', 'C'], 'B': [], 'C': ['B', 'A']}),  # M12
        nx.DiGraph({'A': ['B'], 'B': ['C'], 'C': ['B', 'A']}),  # M13
        nx.DiGraph({'A': ['B', 'C'], 'B': ['C'], 'C': ['B', 'A']}),  # M14
        nx.DiGraph({'A': ['B', 'C'], 'B': ['A', 'C'], 'C': ['A', 'B']})  # M15
    ],
}
'''

motifs = {}
motifs_edges = {}
motifs_digraphs = {}
possible_motifs = {}
opposite_graph_index = {}


def generate_all_digraphs(n):
    """
    Генерирует все возможные ориентированные графы на n вершинах
    """
    vertices = list(range(n))
    all_edges = list(combinations(vertices, 2))

    # Для каждой пары вершин в соответсиве ставится одно из 4 состояний:
    # 0 - нет дуг
    # 1 - дуга v->u
    # 2 - дуга u->v
    # 3 - две дуги

    all_graphs = []

    for edge_states in product([0, 1, 2, 3], repeat=len(all_edges)):
        G = nx.DiGraph()
        G.add_nodes_from(vertices)

        # Добавляем дуги
        for (v, u), state in zip(all_edges, edge_states):
            if state == 1:
                G.add_edge(v, u)
            elif state == 2:
                G.add_edge(u, v)
            elif state == 3:
                G.add_edge(v, u)
                G.add_edge(u, v)

        # Проверяем на изоморфность
        is_isomorphic = False
        for existing in all_graphs:
            if nx.is_isomorphic(G, existing):
                is_isomorphic = True
                break

        if not is_isomorphic:
            all_graphs.append(G)

    return all_graphs


def graph_to_motif_string(G, vertex_names=None):
    """
    Преобразует граф в строку мотива для библиотеки dotmotif
    """
    n = G.number_of_nodes()
    if vertex_names is None:
        vertex_names = [chr(65 + i) for i in range(n)]  # A, B, C, ...

    # Три типа состояний пар вершин
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

    motif_lines = []
    nodes = list(G.nodes())
    n = len(nodes)
    for i in range(n):
        v = nodes[i]
        for j in range(i + 1, n):
            u = nodes[j]
            if G.has_edge(v, u) and G.has_edge(u, v):
                motif_lines.append(f"twoWayEdge({vertex_names[v]}, {vertex_names[u]})")
            elif G.has_edge(v, u):
                motif_lines.append(f"oneWayEdge({vertex_names[v]}, {vertex_names[u]})")
            elif G.has_edge(u, v):
                motif_lines.append(f"oneWayEdge({vertex_names[u]}, {vertex_names[v]})")
            else:
                motif_lines.append(f"noWayEdge({vertex_names[v]}, {vertex_names[u]})")

    # полная строку
    motif_string = edge_definitions + "\n" + "\n".join(motif_lines)

    return motif_string


def graph_in_another(pattern_edges, graph_edges, vertex_names):
    """
    Проверяет, встречается ли один граф-паттергн в другом
    """
    if len(pattern_edges) > len(graph_edges):
        return False
    graph_edges_set = set(graph_edges)
    # Перебираем все комбинации отображений
    for mapping_tuple in permutations(vertex_names, len(vertex_names)):
        mapping = {vertex_names[i]: mapping_tuple[i] for i in range(len(vertex_names))}
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


def get_reverse_motif_index(n, motif_index):
    """
    Вычисляет индекс противоположного мотива для заданного мотива.
    """
    if n not in motifs_digraphs:
        raise ValueError(f"Motif size {n} not supported")

    if motif_index < 0 or motif_index >= len(motifs_digraphs[n]):
        raise ValueError(f"Motif index {motif_index} out of range for size {n}")

    original_graph = motifs_digraphs[n][motif_index]

    # противоположный граф (разность полного графа и исходного)
    complement_graph = nx.DiGraph()
    complement_graph.add_nodes_from(range(n))

    for i in range(n):
        for j in range(i + 1, n):
            has_ij = original_graph.has_edge(i, j)
            has_ji = original_graph.has_edge(j, i)

            # noWayEdge (0,0) → twoWayEdge (1,1)
            # twoWayEdge (1,1) → noWayEdge (0,0)
            # oneWayEdge i->j (1,0) → oneWayEdge j->i (0,1)
            # oneWayEdge j->i (0,1) → oneWayEdge i->j (1,0)

            if not has_ij and not has_ji:  # noWayEdge
                complement_graph.add_edge(i, j)
                complement_graph.add_edge(j, i)
            elif has_ij and has_ji:  # twoWayEdge
                pass
            elif has_ij and not has_ji:  # oneWayEdge i->j
                complement_graph.add_edge(j, i)
            elif not has_ij and has_ji:  # oneWayEdge j->i
                complement_graph.add_edge(i, j)

    # Находим индекс противоположного мотива
    complement_index = None
    for idx, candidate in enumerate(motifs_digraphs[n]):
        if nx.is_isomorphic(complement_graph, candidate):
            return idx

    print(f"Warning: Complement motif not found for index {motif_index} (size {n})")
    return -1


def generate_motifs_for_n(n):
    """
    Генерация всех мотивов на n вершинах
    """

    print(f"Генерация всех мотивов для {n} вершин...")

    mtfs_digraphs = sorted(list(generate_all_digraphs(n)), key=lambda g: len(g.edges()))
    print(f"Найдено {len(mtfs_digraphs)} неизоморфных ориентированных графов")

    vertex_names = [chr(65 + c) for c in range(n)]

    mtfs = []
    mtfs_edges = []
    possible_mtfs = []

    for idx, G in enumerate(mtfs_digraphs):
        # Генерация объекта Motif
        motif_string = graph_to_motif_string(G, vertex_names)
        mtfs.append(Motif(motif_string))

        # Генерация списка ребер
        edges = []
        for u, v in G.edges():
            edges.append((vertex_names[u], vertex_names[v]))
        mtfs_edges.append(edges)

        # Генерация объекта DiGraph
        possible_mtfs.append([])
        for idx2, H in enumerate(mtfs_digraphs):
            if graph_in_another(G.edges(), H.edges(), list(range(n))):
                possible_mtfs[idx].append(idx2)
    return mtfs, mtfs_edges, mtfs_digraphs, possible_mtfs


for k in range(2, 5):
    motifs[k], motifs_edges[k], motifs_digraphs[k], possible_motifs[k] = generate_motifs_for_n(k)
    opposite_graph_index[k] = [get_reverse_motif_index(k, i) for i in range(len(motifs[k]))]
