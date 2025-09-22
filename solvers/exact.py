# solvers/exact.py

from typing import Set, Dict
from graph import Graph

class ExactSolver:
    """
    Encontra a cobertura de vértices mínima exata usando um algoritmo
    recursivo de branch-and-bound com memoização.
    """
    def __init__(self, graph: Graph):
        self.graph = graph
        self.memo: Dict[frozenset, frozenset] = {}

    def _find_cover_recursive(self, remaining_edges: frozenset) -> frozenset:
        """
        Função recursiva auxiliar que encontra o conjunto de vértices.
        """
        if not remaining_edges:
            return frozenset()
        
        if remaining_edges in self.memo:
            return self.memo[remaining_edges]

        u, v = next(iter(remaining_edges))
        
        # Ramo 1: Adicionar 'u' à cobertura
        edges_after_u = frozenset({edge for edge in remaining_edges if u not in edge})
        cover1 = {u}.union(self._find_cover_recursive(edges_after_u))
        
        # Ramo 2: Adicionar 'v' à cobertura
        edges_after_v = frozenset({edge for edge in remaining_edges if v not in edge})
        cover2 = {v}.union(self._find_cover_recursive(edges_after_v))
        
        # Escolhe a cobertura de menor tamanho
        result = cover1 if len(cover1) < len(cover2) else cover2
        self.memo[remaining_edges] = result
        
        return result

    def solve(self) -> Set[int]:
        """
        Inicia a busca pela cobertura mínima exata.
        
        Returns:
            Set[int]: O conjunto de vértices da cobertura ótima.
        """
        self.memo.clear()
        # Converte cada aresta (tupla) em um frozenset para garantir consistência
        edge_set = frozenset(map(frozenset, self.graph.edges))
        return self._find_cover_recursive(edge_set)