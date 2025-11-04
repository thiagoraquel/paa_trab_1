# solvers/backtracking_solver.py

from typing import Set, Tuple
from graph import Graph 

class BacktrackingSolver:
    """
    Encontra a Cobertura Mínima de Vértices (CMV) usando Backtracking
    com poda baseada no Upper Bound (melhor solução encontrada até agora).
    
    Este é o Branch and Bound simplificado, onde o Lower Bound (LB) é 
    simplesmente o tamanho da cobertura parcial atual.
    """

    def __init__(self, graph: Graph):
        self.graph = graph
        # Upper Bound (UB): O tamanho da melhor cobertura completa encontrada.
        self.upper_bound: int = graph.num_vertices 
        self.best_cover: Set[int] = set(range(graph.num_vertices))

    def _find_cover_recursive(self, 
                              uncovered_edges: Set[Tuple[int, int]], 
                              current_cover: Set[int]) -> None:
        """
        Função recursiva principal de Backtracking com Poda.
        
        Args:
            uncovered_edges (Set): O conjunto de arestas que ainda precisam ser cobertas.
            current_cover (Set): O conjunto de vértices já incluídos na cobertura.
        """
        
        # 1. Poda (Pruning)
        # O Lower Bound (LB) mais simples é o tamanho atual da cobertura parcial.
        # Se |C_parcial| for >= UB, não há necessidade de continuar.
        # LB = len(current_cover)
        if len(current_cover) >= self.upper_bound:
            # Poda: Nenhuma solução válida nesta subárvore pode ser melhor.
            return
            
        # 2. Condição de Parada (Solução Válida)
        if not uncovered_edges:
            # Encontrou uma cobertura completa E sabemos que ela é melhor que o UB atual
            # (devido à verificação da Poda).
            self.upper_bound = len(current_cover)
            self.best_cover = current_cover.copy()
            return

        # 3. Escolha do Vértice de Ramificação
        # Pega a primeira aresta (u, v) que ainda não foi coberta.
        u, v = next(iter(uncovered_edges)) 

        # --- Ramificação ---

        # Ramo 1: Incluir 'u' na cobertura
        # Calcula as novas arestas não cobertas (remove todas as incidentes em u)
        new_uncovered_edges_u = {edge for edge in uncovered_edges if u not in edge}
        self._find_cover_recursive(new_uncovered_edges_u, current_cover.union({u}))

        # Ramo 2: Incluir 'v' na cobertura
        # Calcula as novas arestas não cobertas (remove todas as incidentes em v)
        new_uncovered_edges_v = {edge for edge in uncovered_edges if v not in edge}
        self._find_cover_recursive(new_uncovered_edges_v, current_cover.union({v}))


    def solve(self) -> Set[int]:
        """
        Inicia a busca pelo Backtracking com Poda.
        
        Returns:
            Set[int]: O conjunto de vértices da cobertura ótima.
        """
        # Formato canônico de arestas (u, v) onde u < v para garantir consistência
        canonical_edges = set(tuple(sorted((u, v))) for u, v in self.graph.edges)
            
        # Reseta o estado
        self.upper_bound = self.graph.num_vertices
        self.best_cover = set(range(self.graph.num_vertices)) 
        
        self._find_cover_recursive(canonical_edges, set())
        
        return self.best_cover