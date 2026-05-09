import networkx as nx
import numpy as np
from scipy import stats
from collections import Counter
from scipy.spatial import distance
from .triplet_model import SubgraphStructure
from .triplets import motifs


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
    print(descr, f'{res.statistic:.5f}, {res.pvalue:.5f} ')
    comparison[descr] = res

    descr = 'Коэффициент корреляции Спирмена для распределения степеней захода:'
    res = stats.spearmanr([indeg_g_rnd.get(i, 0) for i in range(min_value_indeg, max_value_indeg + 1)],
                          [indeg.get(i, 0) for i in range(min_value_indeg, max_value_indeg + 1)])
    print(descr, f'{res.statistic:.5f}, {res.pvalue:.5f} ')
    comparison[descr] = res

    descr = 'Коэффициент корреляции Спирмена для распределения степеней исхода:'
    res = stats.spearmanr([outdeg_g_rnd.get(i, 0) for i in range(min_value_outdeg, max_value_outdeg + 1)],
                          [outdeg.get(i, 0) for i in range(min_value_outdeg, max_value_outdeg + 1)])
    print(descr, f'{res.statistic:.5f}, {res.pvalue:.5f} ')
    comparison[descr] = res


    descr = 'Расстояние Дженсена-Шеннона для распределения мотивов:'
    res = distance.jensenshannon(
        [x / m_sum for x in m],
        [x / m_sum_rnd for x in m_rnd])
    print(descr, f'{res:.5f}')
    comparison[descr] = res

    descr = 'Расстояние Дженсена-Шеннона для распределения степеней захода:'
    res = distance.jensenshannon(
        [indeg_g_rnd.get(i, 0) / sm_rnd_indeg for i in range(min_value_indeg, max_value_indeg + 1)],
        [indeg.get(i, 0) / sm_indeg for i in range(min_value_indeg, max_value_indeg + 1)])
    print(descr, f'{res:.5f}')

    comparison[descr] = res

    descr = 'Расстояние Дженсена-Шеннона для распределения степеней исхода:'
    res = distance.jensenshannon(
        [outdeg_g_rnd.get(i, 0) / sm_rnd_outdeg for i in range(min_value_outdeg, max_value_outdeg + 1)],
        [outdeg.get(i, 0) / sm_outdeg for i in range(min_value_outdeg, max_value_outdeg + 1)])
    print(descr, f'{res:.5f}')

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


def read_generate_and_save_to_excel(path):
    if path.endswith('txt'):
        G = nx.read_edgelist(path, create_using=nx.DiGraph())
    elif path.endswith('csv'):
        G = nx.read_edgelist(path=path, delimiter=',', create_using=nx.DiGraph())
    else:
        print('Wrong data t')
        return

    A = nx.to_numpy_array(G)
    nodes = len(G.nodes())  # количество вершин
    edges = len(G.edges())  # количество дуг
    probability = edges / (nodes * (nodes - 1))  # вероятность появления дуги
    indeg, outdeg = list(d for n, d in G.in_degree()), list(d for n, d in G.out_degree())

    ss_G = SubgraphStructure(G)

    print('\n' * 2, '-' * 20, '\n' * 2, 'Starting Generation', '\n' * 2)

    g_rnd = dict()
    g_rnd['nx.gnp_random_graph'] = nx.gnp_random_graph(nodes, probability, directed=True)
    print('nx.gnp_random_graph done!')
    g_rnd['nx.fast_gnp_random_graph'] = nx.fast_gnp_random_graph(nodes, probability, directed=True)
    print('nx.fast_gnp_random_graph done!')
    g_rnd['nx.binomial_graph'] = nx.binomial_graph(nodes, probability, directed=True)
    print('nx.binomial_graph done!')
    #g_rnd['nx.directedconfiguration_model'] = nx.directed_configuration_model(indeg, outdeg)

    for x in g_rnd:
        print('\n' * 2, '-' * 20, '\n' * 2)
        print(x, '\n' * 2)

        metrics = calculate_graph_metrics(g_rnd[x])
        for i in ['num_nodes', 'num_edges', 'density',
                  'min_in_degree', 'max_in_degree', 'min_out_degree'
            , 'max_out_degree', 'weakly_connected', 'strongly_connected', 'strongly_connected_nodes',
                  'transitivity', 'reciprocity', 'avg_clustering']:
            if i in ['density', 'transitivity', 'reciprocity', 'avg_clustering']:
                print(i, f'{metrics[i]:.5f}')

            else:
                print(i, metrics[i])
        ss_new_G = SubgraphStructure(g_rnd[x])
        evaluate_quality(G, g_rnd[x], [ss_G.motif_subgraphs[m.motif].count for m in motifs[3]],
                         [ss_new_G.motif_subgraphs[m.motif].count for m in motifs[3]])
