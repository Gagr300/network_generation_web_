import networkx as nx
import numpy as np
from scipy import stats
from collections import Counter
from scipy.spatial import distance


def evaluate_quality(g, g_rnd, m, m_rnd):
    indeg = Counter(d for n, d in g.in_degree())
    indeg_g_rnd = Counter(d for n, d in g_rnd.in_degree())
    min_value_indeg = min(min(indeg), min(indeg_g_rnd))
    max_value_indeg = max(max(indeg), max(indeg_g_rnd))
    sm_indeg = sum(indeg.values())
    sm_rnd_indeg = sum(indeg_g_rnd.values())

    outdeg = Counter(d for n, d in g.out_degree())
    outdeg_g_rnd = Counter(d for n, d in g_rnd.out_degree())
    min_value_outdeg = min(min(outdeg), min(outdeg_g_rnd))
    max_value_outdeg = max(max(outdeg), max(outdeg_g_rnd))
    sm_outdeg = sum(outdeg.values())
    sm_rnd_outdeg = sum(outdeg_g_rnd.values())

    m_sum = sum(m)
    m_sum_rnd = sum(m)

    comparison = dict()

    descr = 'Коэффициент корреляции Спирмена для распределения мотивов:'
    res = stats.spearmanr(m, m_rnd)
    print(descr, res)
    comparison[descr] = res

    descr = 'Расстояние Дженсена-Шеннона для распределения мотивов:'
    res = distance.jensenshannon(
        [x / m_sum for x in m],
        [x / m_sum_rnd for x in m_rnd])
    print(descr, res)
    comparison[descr] = res

    descr = 'Коэффициент корреляции Спирмена для распределения степеней захода:'
    res = stats.spearmanr([indeg_g_rnd.get(i, 0) for i in range(min_value_indeg, max_value_indeg + 1)],
                          [indeg.get(i, 0) for i in range(min_value_indeg, max_value_indeg + 1)])
    print(descr, res)
    comparison[descr] = res

    descr = 'Коэффициент корреляции Спирмена для распределения степеней исхода:'
    res = stats.spearmanr([outdeg_g_rnd.get(i, 0) for i in range(min_value_outdeg, max_value_outdeg + 1)],
                          [outdeg.get(i, 0) for i in range(min_value_outdeg, max_value_outdeg + 1)])
    print(descr, res)
    comparison[descr] = res

    descr = 'Расстояние Дженсена-Шеннона для распределения степеней захода:'
    res = distance.jensenshannon(
        [indeg_g_rnd.get(i, 0) / sm_rnd_indeg for i in range(min_value_indeg, max_value_indeg + 1)],
        [indeg.get(i, 0) / sm_indeg for i in range(min_value_indeg, max_value_indeg + 1)])
    print(descr, res)
    comparison[descr] = res

    descr = 'Расстояние Дженсена-Шеннона для распределения степеней исхода:'
    res = distance.jensenshannon(
        [outdeg_g_rnd.get(i, 0) / sm_rnd_outdeg for i in range(min_value_outdeg, max_value_outdeg + 1)],
        [outdeg.get(i, 0) / sm_outdeg for i in range(min_value_outdeg, max_value_outdeg + 1)])
    print(descr, res)
    comparison[descr] = res

    return comparison


def graph_to_json(G):
    """Конвертирует граф NetworkX в JSON формат"""
    nodes = [{"id": str(node)} for node in G.nodes()]
    edges = [{"source": str(source), "target": str(target)} for source, target in G.edges()]

    return {
        "nodes": nodes,
        "edges": edges
    }


def calculate_graph_metrics(G):
    """Рассчитывает основные метрики графа"""

    in_degrees = [d for n, d in G.in_degree()]
    out_degrees = [d for n, d in G.out_degree()]
    weak_components = list(nx.weakly_connected_components(G))
    clustering = nx.clustering(G)
    strong_components = list(nx.strongly_connected_components(G))
    largest_strong = max(strong_components, key=len)

    metrics = {
        'num_nodes': G.number_of_nodes(),
        'num_edges': G.number_of_edges(),
        'density': nx.density(G),
        'min_in_degree': min(in_degrees),
        'max_in_degree': max(in_degrees),
        'min_out_degree': min(out_degrees),
        'max_out_degree': max(out_degrees),
        'weakly_connected': len(weak_components) == 1 if weak_components else False,
        'avg_clustering': sum(clustering.values()) / len(clustering) if clustering else 0,
        'reciprocity': nx.overall_reciprocity(G),
        'strongly_connected_nodes': len(largest_strong),
        'strongly_connected': len(strong_components) == 1,
        'transitivity': nx.transitivity(G.subgraph(largest_strong))
    }

    return metrics
