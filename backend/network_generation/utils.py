import networkx as nx
import numpy as np


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
