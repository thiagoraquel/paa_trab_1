import random
from typing import List, Tuple, Dict, Optional
from graph import Graph 

def _cost_function(graph: Graph, cover: List[bool], penalty: int) -> int:
    """Função de custo para a Busca Tabu."""
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
    penalty: int = None, # Mudamos para None para calcular dinamicamente
    rng_seed: Optional[int] = None
) -> Tuple[List[int], int]:
    """
    Busca Tabu OTIMIZADA para Cobertura de Vértices usando "Delta Evaluation".
    """
    rng = random.Random(rng_seed)
    
    # --- CORREÇÃO 1: Penalidade Dinâmica ---
    if penalty is None or penalty <= graph.num_vertices:
        penalty = graph.num_vertices + 1

    # --- Inicialização ---
    
    # 1. 'best' (Bandeira do Recorde) começa na primeira solução VÁLIDA conhecida.
    best = [True] * graph.num_vertices
    best_cost = _cost_function(graph, best, penalty) # Custo será 'graph.num_vertices'
    
    # 2. 'current' (Explorador) começa em um ponto aleatório 50/50.
    #    (Substitui a linha: current = [True] * graph.num_vertices)
    current = [rng.choice([True, False]) for _ in range(graph.num_vertices)]
    
    # O custo e a contagem de descobertas do Explorador são calculados
    current_uncovered_count = graph.count_uncovered_edges(current) # Lento, mas só faz 1 vez
    current_size = sum(current)
    current_cost = (current_uncovered_count * penalty) + current_size
    
    # Se, por sorte, a solução aleatória for válida E melhor, ela se torna o 'best'
    if current_uncovered_count == 0 and current_cost < best_cost:
        best = current[:]
        best_cost = current_cost

    tabu: Dict[Tuple[int, bool], int] = {} 

    for it in range(1, max_iters + 1):
        best_move = None
        best_move_cost = float("inf")
        
        # --- Variável inútil (best_move_delta_uncovered) foi REMOVIDA daqui ---

        # --- Exploração da Vizinhança (Otimizada) ---
        for v in range(graph.num_vertices):
            
            delta_cost = _calculate_delta_cost(graph, current, v, penalty)
            new_cost = current_cost + delta_cost
            
            new_state = not current[v]
            is_tabu = tabu.get((v, new_state), 0) > it

            # 3. Critério de Aspiração
            if (not is_tabu) or (new_cost < best_cost):
                if new_cost < best_move_cost:
                    best_move_cost = new_cost
                    best_move = v

        if best_move is None:
            break 

        # --- Aplica o Melhor Movimento ---
        v = best_move
        old_state = current[v]
        
        # Recalcula o delta de arestas descobertas apenas para o movimento escolhido
        delta_uncovered_count = 0
        for u in graph.list_adj[v]:
            if not current[u]:
                if old_state: # Estava True (removendo) -> fica descoberto
                    delta_uncovered_count += 1
                else: # Estava False (adicionando) -> fica coberto
                    delta_uncovered_count -= 1
        
        current_uncovered_count += delta_uncovered_count
        
        current[v] = not old_state
        current_cost = best_move_cost
        
        tabu[(v, old_state)] = it + tabu_tenure

        # --- Atualiza a Melhor Solução Global ---
        # --- CORREÇÃO 2: Blindagem Lógica ---
        # Só atualizamos o 'best' se o custo for menor E (CRUCIAL) se a solução for válida.
        if current_cost < best_cost and current_uncovered_count == 0:
            best = current[:]
            best_cost = current_cost
            
    cover_vertices = [i for i, in_cover in enumerate(best) if in_cover]
    final_best_cost = _cost_function(graph, best, penalty)
    
    return cover_vertices, final_best_cost