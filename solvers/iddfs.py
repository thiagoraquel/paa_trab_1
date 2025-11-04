# solvers/iddfs_solver.py

from typing import Set, Tuple, List, Optional
from graph import Graph 
from collections import deque # Mantida para consistência, mas não usada na recursão DFS

class IDDFSSolver:
    """
    Algoritmo Exato para Cobertura Mínima de Vértices (CMV) utilizando
    Iterative Deepening Depth-First Search (IDDFS).
    
    A busca iterativa garante a solução mínima (ótima), e a busca em profundidade 
    limitada (DFS-L) garante a exatidão e a eficiência FPT para k pequeno.
    """

    def __init__(self, graph: Graph):
        self.graph = graph

    def _depth_limited_search(self, 
                              uncovered_edges: Set[Tuple[int, int]], 
                              k_limit: int) -> Optional[Set[int]]:
        """
        Executa uma Busca em Profundidade (DFS) com um limite de profundidade (budget k).
        
        Args:
            uncovered_edges (Set): As arestas que precisam ser cobertas.
            k_limit (int): O orçamento restante de vértices para a cobertura.
            
        Retorna:
            Set[int]: O conjunto de vértices da cobertura restante se sucesso, ou None se falha.
        """
        
        # 1. Condições de Parada
        if not uncovered_edges:
            return set() # Sucesso: Encontrou a cobertura restante.
        
        if k_limit <= 0:
            return None # Falha: Orçamento esgotado e ainda há arestas não cobertas.

        # Poda Opcional (melhora a eficiência, mas não a exatidão):
        # max_matching = self._get_max_matching_size(uncovered_edges) 
        # if max_matching > k_limit:
        #     return None # Falha: O Emparelhamento Máximo exige mais vértices do que k_limit.

        # 2. Ramificação (Escolha da Aresta)
        # Escolhe a primeira aresta (u, v) para iniciar a ramificação
        u, v = next(iter(uncovered_edges)) 

        # --- Ramo 1: Incluir 'u' na cobertura ---
        
        # Arestas cobertas por u: remove todas as incidentes em u
        new_uncovered_u = {edge for edge in uncovered_edges if u not in edge}
        
        # Chamada recursiva com orçamento k-1
        result_u = self._depth_limited_search(new_uncovered_u, k_limit - 1)

        if result_u is not None:
            # Sucesso no Ramo u: a solução é {u} unida à solução restante
            return {u}.union(result_u) 

        # --- Ramo 2: Incluir 'v' na cobertura ---
        
        # Arestas cobertas por v: remove todas as incidentes em v
        new_uncovered_v = {edge for edge in uncovered_edges if v not in edge}
        
        # Chamada recursiva com orçamento k-1
        result_v = self._depth_limited_search(new_uncovered_v, k_limit - 1)

        if result_v is not None:
            # Sucesso no Ramo v
            return {v}.union(result_v) 

        # 3. Falha
        return None # Falha: Nenhum dos ramos encontrou uma solução dentro do k_limit.

    def solve(self) -> Set[int]:
        """
        Implementa o Iterative Deepening (Busca Iterativa) para encontrar
        a Cobertura Mínima.
        """
        # Formato canônico de arestas (u, v) onde u < v para garantir consistência
        canonical_edges = set(tuple(sorted((u, v))) for u, v in self.graph.edges)
        
        # Se o grafo não tiver arestas, a CMV é 0.
        if not canonical_edges:
            return set()

        # O limite superior máximo de k é o número total de vértices
        max_k = self.graph.num_vertices 
        
        # Iterative Deepening: A busca mais profunda (k crescente) é feita a cada iteração
        for k in range(1, max_k + 1):
            # Tenta encontrar uma cobertura de tamanho k
            # O DLS atua como um "teste de existência" para uma solução de tamanho k
            solution = self._depth_limited_search(canonical_edges, k)
            
            if solution is not None:
                # O primeiro k que retorna uma solução é o k mínimo (a Cobertura Mínima).
                return solution
                
        # Caso de fallback, embora o loop deva encontrar uma solução (todos os vértices)
        return set(range(max_k))