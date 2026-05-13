import networkx as nx
import numpy as np
from scipy import stats
from collections import Counter
from scipy.spatial import distance
from .triplet_model import SubgraphStructure
from .triplets import motifs


def evaluate_quality(g: nx.DiGraph, g_rnd: nx.DiGraph, m: list, m_rnd: list):
    """
    Сравнение двух графов
    """
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
    comparison[descr] = (res.statistic, res.pvalue)

    descr = 'Коэффициент корреляции Спирмена для распределения степеней захода:'
    res = stats.spearmanr([indeg_g_rnd.get(i, 0) for i in range(min_value_indeg, max_value_indeg + 1)],
                          [indeg.get(i, 0) for i in range(min_value_indeg, max_value_indeg + 1)])
    comparison[descr] = (res.statistic, res.pvalue)

    descr = 'Коэффициент корреляции Спирмена для распределения степеней исхода:'
    res = stats.spearmanr([outdeg_g_rnd.get(i, 0) for i in range(min_value_outdeg, max_value_outdeg + 1)],
                          [outdeg.get(i, 0) for i in range(min_value_outdeg, max_value_outdeg + 1)])
    comparison[descr] = (res.statistic, res.pvalue)

    descr = 'Расстояние Дженсена-Шеннона для распределения мотивов:'
    res = distance.jensenshannon(
        [x / m_sum for x in m],
        [x / m_sum_rnd for x in m_rnd])
    comparison[descr] = res

    descr = 'Расстояние Дженсена-Шеннона для распределения степеней захода:'
    res = distance.jensenshannon(
        [indeg_g_rnd.get(i, 0) / sm_rnd_indeg for i in range(min_value_indeg, max_value_indeg + 1)],
        [indeg.get(i, 0) / sm_indeg for i in range(min_value_indeg, max_value_indeg + 1)])

    comparison[descr] = res

    descr = 'Расстояние Дженсена-Шеннона для распределения степеней исхода:'
    res = distance.jensenshannon(
        [outdeg_g_rnd.get(i, 0) / sm_rnd_outdeg for i in range(min_value_outdeg, max_value_outdeg + 1)],
        [outdeg.get(i, 0) / sm_outdeg for i in range(min_value_outdeg, max_value_outdeg + 1)])

    comparison[descr] = res

    return comparison


def graph_to_json(g: nx.DiGraph):
    """
    Конвертация графа NetworkX в JSON формат
    """
    nodes = [{"id": str(node)} for node in g.nodes()]
    edges = [{"source": str(source), "target": str(target)} for source, target in g.edges()]

    return {
        "nodes": nodes,
        "edges": edges
    }


def calculate_graph_metrics(g: nx.DiGraph):
    """Рассчитывает основные метрики графа"""

    in_degrees = [d for n, d in g.in_degree()]
    out_degrees = [d for n, d in g.out_degree()]
    weak_components = list(nx.weakly_connected_components(g))
    clustering = nx.clustering(g)
    strong_components = list(nx.strongly_connected_components(g))
    largest_strong = max(strong_components, key=len)

    metrics = {
        'num_nodes': g.number_of_nodes(),
        'num_edges': g.number_of_edges(),
        'density': nx.density(g),
        'min_in_degree': min(in_degrees),
        'max_in_degree': max(in_degrees),
        'min_out_degree': min(out_degrees),
        'max_out_degree': max(out_degrees),
        'weakly_connected': len(weak_components) == 1 if weak_components else False,
        'strongly_connected': len(strong_components) == 1,
        'strongly_connected_nodes': len(largest_strong),
        'transitivity': nx.transitivity(g.subgraph(largest_strong)),
        'reciprocity': nx.overall_reciprocity(g),
        'avg_clustering': sum(clustering.values()) / len(clustering) if clustering else 0,
    }
    return metrics


def read_generate_and_save_to_excel(path: str):
    if path.endswith('txt'):
        g = nx.read_edgelist(path, create_using=nx.DiGraph())
    elif path.endswith('csv'):
        g = nx.read_edgelist(path=path, delimiter=',', create_using=nx.DiGraph())
    else:
        print('Wrong data type')
        return

    A = nx.to_numpy_array(g)
    nodes = len(g.nodes())  # количество вершин
    edges = len(g.edges())  # количество дуг
    probability = edges / (nodes * (nodes - 1))  # вероятность появления дуги
    indeg, outdeg = list(d for n, d in g.in_degree()), list(d for n, d in g.out_degree())  # списки полустепеней

    ss_g = SubgraphStructure(g)

    # генерация графов
    print('\n' * 2, '-' * 20, '\n' * 2, 'Starting generation', '\n' * 2)
    g_rnd = dict()
    g_rnd['nx.gnp_random_graph'] = nx.gnp_random_graph(nodes, probability, directed=True)
    print('nx.gnp_random_graph done!')
    g_rnd['nx.fast_gnp_random_graph'] = nx.fast_gnp_random_graph(nodes, probability, directed=True)
    print('nx.fast_gnp_random_graph done!')
    g_rnd['nx.binomial_graph'] = nx.binomial_graph(nodes, probability, directed=True)
    print('nx.binomial_graph done!')
    g_rnd['nx.directedconfiguration_model'] = nx.directed_configuration_model(indeg, outdeg, create_using=nx.DiGraph)
    print('nx.directed_configuration_model done!')

    # вычисление метрик
    res = dict()
    for x in g_rnd:
        print(f'{'\n' * 2}{'-' * 20}{'\n' * 2}Модель: {x}{'\n' * 2}')
        ss_new_g = SubgraphStructure(g_rnd[x])
        res[x] = calculate_graph_metrics(g_rnd[x])
        res[x] |= evaluate_quality(g, g_rnd[x], [ss_g.motif_subgraphs[m.motif].count for m in motifs[3]],
                                       [ss_new_g.motif_subgraphs[m.motif].count for m in motifs[3]])

        for i in res[x]:
            if isinstance(res[x][i], float):
                print(i, f'{res[x][i]:.5f}')
            elif isinstance(res[x][i], tuple):
                print(i, f'{res[x][i][0]:.5f} {res[x][i][1]:.5f}')
            else:
                print(i, res[x][i])
