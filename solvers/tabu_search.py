import random
from typing import List, Tuple, Dict, Optional
# Presume que 'graph' tem os métodos:
# graph.num_vertices -> int
# graph.count_uncovered_edges(cover) -> int
# graph.get_neighbors(v) -> List[int]
from graph import Graph 

def _cost_function(graph: Graph, cover: List[bool], penalty: int) -> int:
    """Função de custo para a Busca Tabu. (Usada apenas no início)"""
    uncovered = graph.count_uncovered_edges(cover)
    size = sum(cover)
    return uncovered * penalty + size

def _calculate_delta_cost(
    graph: Graph, 
    current_cover: List[bool], 
    v: int, 
    penalty: int
) -> int:
    """
    Calcula a *mudança* no custo (delta) ao "flipar" o vértice v.
    Esta é a otimização principal.
    """
    old_state = current_cover[v]
    delta_size = 0
    delta_uncovered = 0
    
    # Itera apenas sobre os vizinhos do vértice 'v'
    for u in graph.list_adj[v]:
        # O estado da aresta (v, u) só muda se o vizinho 'u' não estiver na cobertura
        if not current_cover[u]:
            if old_state:
                # Caso 1: Removendo 'v' (True -> False)
                # A aresta (v, u) se torna descoberta
                delta_uncovered += 1
            else:
                # Caso 2: Adicionando 'v' (False -> True)
                # A aresta (v, u) se torna coberta
                delta_uncovered -= 1

    if old_state:
        # Removendo 'v'
        delta_size = -1
    else:
        # Adicionando 'v'
        delta_size = +1
        
    return (delta_uncovered * penalty) + delta_size

def solve_tabu_search(
    graph: Graph,
    max_iters: int = 10000,
    tabu_tenure: int = 7,
    penalty: int = 1000,
    rng_seed: Optional[int] = None
) -> Tuple[List[int], int]:
    """
    Busca Tabu OTIMIZADA para Cobertura de Vértices usando "Delta Evaluation".
    """
    rng = random.Random(rng_seed)
    
    # --- Inicialização ---
    current = [True] * graph.num_vertices
    # Custo total é calculado APENAS UMA VEZ
    current_cost = _cost_function(graph, current, penalty) 

    best = current[:]
    best_cost = current_cost

    tabu: Dict[Tuple[int, bool], int] = {} # (vértice, novo_estado) -> iteração_tabu

    for it in range(1, max_iters + 1):
        best_move = None
        best_move_cost = float("inf") # Custo total do melhor vizinho

        # --- Exploração da Vizinhança (Otimizada) ---
        for v in range(graph.num_vertices):
            
            # 1. Calcula o delta do custo (muito rápido)
            delta_cost = _calculate_delta_cost(graph, current, v, penalty)
            new_cost = current_cost + delta_cost
            
            # 2. Verifica se o movimento é tabu
            new_state = not current[v]
            is_tabu = tabu.get((v, new_state), 0) > it

            # 3. Critério de Aspiração
            if (not is_tabu) or (new_cost < best_cost):
                if new_cost < best_move_cost:
                    best_move_cost = new_cost
                    best_move = v

        if best_move is None:
            # Nenhum movimento válido encontrado (pode acontecer)
            break 

        # --- Aplica o Melhor Movimento ---
        v = best_move
        old_state = current[v]
        
        # Atualiza a solução atual e seu custo (sem recalcular)
        current[v] = not old_state
        current_cost = best_move_cost
        
        # Adiciona o inverso do movimento à lista tabu
        # (Proíbe mover 'v' de volta para 'old_state')
        tabu[(v, old_state)] = it + tabu_tenure

        # --- Atualiza a Melhor Solução Global ---
        if current_cost < best_cost:
            best = current[:]
            best_cost = current_cost
            
    cover_vertices = [i for i, in_cover in enumerate(best) if in_cover]
    
    # Recalcula o custo final da 'best' para garantir 
    # (apenas por segurança, 'best_cost' deve estar correto)
    final_best_cost = _cost_function(graph, best, penalty)
    
    return cover_vertices, final_best_cost