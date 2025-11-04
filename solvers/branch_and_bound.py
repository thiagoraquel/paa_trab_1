# solvers/branch_and_bound.py

from typing import Set, Dict, Tuple, List, Optional
from graph import Graph # Assumindo a classe Graph do seu exemplo
from collections import deque

class BranchAndBoundSolver:
    """
    Encontra a cobertura de vértices mínima exata usando Branch and Bound.
    A poda é feita usando um Lower Bound baseado no Emparelhamento Máximo 
    do subgrafo residual, que é calculado usando o algoritmo de Edmonds-Karp 
    (Fluxo Máximo).
    """

    def __init__(self, graph: Graph):
        self.graph = graph
        # Upper Bound: O tamanho da melhor cobertura encontrada até agora.
        self.upper_bound: int = graph.num_vertices 
        self.best_cover: Set[int] = set(range(graph.num_vertices))

    # --- Funções Auxiliares de Emparelhamento Máximo (Base do Lower Bound) ---

    def _edmonds_karp_bfs(self, graph_capacity: List[List[int]], source: int, sink: int) -> Optional[List[int]]:
        """
        Busca em Largura (BFS) para encontrar um caminho aumentante na rede residual.
        Retorna o caminho como uma lista de predecessores, ou None se não houver caminho.
        """
        n = len(graph_capacity)
        parent = [-1] * n
        queue = deque([source])
        parent[source] = source

        while queue:
            u = queue.popleft()
            for v in range(n):
                # Se houver capacidade residual de u para v e v não foi visitado
                if parent[v] == -1 and graph_capacity[u][v] > 0:
                    parent[v] = u
                    if v == sink:
                        # Caminho encontrado
                        path = []
                        curr = sink
                        while curr != source:
                            path.append(curr)
                            curr = parent[curr]
                        path.append(source)
                        return path[::-1] # Retorna o caminho da fonte ao sumidouro
                    queue.append(v)
        return None

    def _max_flow(self, capacity_matrix: List[List[int]], source: int, sink: int) -> int:
        """
        Implementa o algoritmo de Edmonds-Karp para encontrar o fluxo máximo.
        """
        n = len(capacity_matrix)
        residual_capacity = [row[:] for row in capacity_matrix]
        max_flow = 0
        
        while True:
            path = self._edmonds_karp_bfs(residual_capacity, source, sink)
            if not path:
                break

            # Encontra a capacidade do caminho
            path_flow = float('inf')
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                path_flow = min(path_flow, residual_capacity[u][v])

            # Atualiza a capacidade residual
            max_flow += path_flow
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                residual_capacity[u][v] -= path_flow  # Fluxo para frente
                residual_capacity[v][u] += path_flow  # Fluxo de retorno

        return max_flow

    def _maximum_matching_lower_bound(self, residual_edges: Set[Tuple[int, int]]) -> int:
        """
        Calcula o Emparelhamento Máximo no subgrafo residual G' usando Fluxo Máximo.
        
        LB = Emparelhamento Máximo. (Exato para grafos bipartidos; para grafos gerais,
        seria necessário o algoritmo de Edmonds, que é mais complexo).
        """
        if not residual_edges:
            return 0

        # Para usar o algoritmo de fluxo, precisamos criar um grafo Bipartido artificial.
        # Os vértices originais V' são divididos em V_left e V_right.
        
        # 1. Mapeamento e Grafo Bipartido
        # A cardinalidade do Emparelhamento Máximo é sempre um Lower Bound (LB) válido.
        # Esta implementação de LB é exata para o emparelhamento, mas é muito custosa.
        
        V_prime = set()
        for u, v in residual_edges:
            V_prime.add(u)
            V_prime.add(v)
        
        # Simplificação: Particionamento arbitrário de V' em duas partes U e W.
        # Para um grafo G' geral, não há uma bipartição garantida.
        # Usaremos o maior vértice na aresta para garantir a separação de u e v.
        U = set(v for v in V_prime if v % 2 == 0)
        W = V_prime - U

        # Mapeamento: source, sink, e novos índices
        # Source (0), V_left (1 a |U|), V_right (|U|+1 a |U|+|W|), Sink (|U|+|W|+1)
        source, sink = 0, len(V_prime) + 1
        
        u_map = {u_val: i + 1 for i, u_val in enumerate(U)}
        w_map = {w_val: i + len(U) + 1 for i, w_val in enumerate(W)}
        
        total_nodes = len(V_prime) + 2
        capacity = [[0] * total_nodes for _ in range(total_nodes)]

        # 2. Capacidades
        # Arestas Source -> V_left (capacidade 1)
        for u_val in U:
            capacity[source][u_map[u_val]] = 1

        # Arestas V_right -> Sink (capacidade 1)
        for w_val in W:
            capacity[w_map[w_val]][sink] = 1

        # Arestas V_left -> V_right (capacidade 1)
        for u, v in residual_edges:
            u_in_U = u in U
            u_val = u if u_in_U else v
            v_val = v if u_in_U else u
            
            if u_in_U and v in W:
                capacity[u_map[u_val]][w_map[v_val]] = 1

        # 3. Cálculo
        max_matching_size = self._max_flow(capacity, source, sink)
        return max_matching_size

    # --- Função Principal de Branch and Bound ---

    def _find_cover_recursive(self, 
                              uncovered_edges: Set[Tuple[int, int]], 
                              current_cover: Set[int]) -> None:
        """
        Função recursiva principal de Branch and Bound com poda.
        """
        
        # 1. Condição de Parada (Solução Válida)
        if not uncovered_edges:
            if len(current_cover) < self.upper_bound:
                self.upper_bound = len(current_cover)
                self.best_cover = current_cover.copy()
            return
        
        # 2. Lower Bound (LB) e Poda (Pruning)
        lower_bound = len(current_cover) + self._maximum_matching_lower_bound(uncovered_edges)
        
        if lower_bound >= self.upper_bound:
            # Poda: A subárvore não pode conter uma solução melhor que o UB.
            return

        # 3. Escolha do Vértice de Ramificação
        # Escolhe a aresta (u, v) que ainda não foi coberta
        u, v = next(iter(uncovered_edges)) 

        # --- Ramificação ---

        # Ramo 1: Incluir 'u' na cobertura
        new_uncovered_edges_u = {edge for edge in uncovered_edges if u not in edge}
        self._find_cover_recursive(new_uncovered_edges_u, current_cover.union({u}))
        
        # Ramo 2: Incluir 'v' na cobertura
        new_uncovered_edges_v = {edge for edge in uncovered_edges if v not in edge}
        self._find_cover_recursive(new_uncovered_edges_v, current_cover.union({v}))


    def solve(self) -> Set[int]:
        """
        Inicia a busca pelo Branch and Bound.
        """
        # Formato canônico de arestas (u, v) onde u < v para garantir consistência
        canonical_edges = set(tuple(sorted((u, v))) for u, v in self.graph.edges)
            
        # Reseta o estado
        self.upper_bound = self.graph.num_vertices
        self.best_cover = set(range(self.graph.num_vertices)) 
        
        self._find_cover_recursive(canonical_edges, set())
        
        return self.best_cover