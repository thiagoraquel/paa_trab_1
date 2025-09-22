# solvers/approximation.py

from typing import Set
from graph import Graph

def solve_approximation(graph: Graph) -> Set[int]:
    """
    Implementa o algoritmo de aproximação de fator 2 para a cobertura de vértices.

    Args:
        graph (Graph): O objeto de grafo a ser resolvido.

    Returns:
        Set[int]: Um conjunto de vértices que formam a cobertura.
    """
    vertex_is_covered = [False] * graph.num_vertices
    vertex_cover_set = set()

    for u, v in graph.edges:
        if not vertex_is_covered[u] and not vertex_is_covered[v]:
            vertex_is_covered[u] = True
            vertex_is_covered[v] = True
            vertex_cover_set.add(u)
            vertex_cover_set.add(v)
    
    return vertex_cover_set