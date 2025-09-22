# visualization.py

import matplotlib.pyplot as plt
import networkx as nx
from typing import Set
from graph import Graph

def visualizar_grafo_com_cobertura(graph: Graph, cover_nodes: Set[int], title: str):
    """
    Cria e exibe uma visualização de um grafo, destacando os nós da cobertura.

    Args:
        graph (Graph): O objeto de grafo a ser visualizado.
        cover_nodes (Set[int]): Um conjunto com os IDs dos vértices na cobertura.
        title (str): O título do gráfico.
    """
    g = nx.Graph()
    g.add_nodes_from(range(graph.num_vertices))
    g.add_edges_from(graph.edges)

    node_colors = ['tomato' if node in cover_nodes else 'skyblue' for node in g.nodes()]

    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(g, seed=42)
    
    nx.draw(g, pos,
            with_labels=True,
            node_color=node_colors,
            node_size=600,
            font_size=10,
            width=1.5)

    plt.title(title, size=16)
    plt.show()