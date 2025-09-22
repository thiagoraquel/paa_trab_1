# solvers/tabu_search.py

import random
from typing import List, Tuple, Dict, Optional
from graph import Graph

def _cost_function(graph: Graph, cover: List[bool], penalty: int) -> int:
    """Função de custo para a Busca Tabu."""
    uncovered = graph.count_uncovered_edges(cover)
    size = sum(cover)
    return uncovered * penalty + size

def solve_tabu_search(
    graph: Graph,
    max_iters: int = 10000,
    tabu_tenure: int = 7,
    penalty: int = 1000,
    rng_seed: Optional[int] = None
) -> Tuple[List[int], int]:
    """
    Busca Tabu para Cobertura de Vértices.

    Args:
        graph (Graph): O objeto de grafo a ser resolvido.
        max_iters (int): Número máximo de iterações.
        tabu_tenure (int): Por quantas iterações um movimento é tabu.
        penalty (int): Peso para cada aresta não coberta.
        rng_seed (Optional[int]): Semente para o gerador de números aleatórios.

    Returns:
        Tuple[List[int], int]: Vértices da melhor cobertura e seu custo.
    """
    rng = random.Random(rng_seed)
    # Solução inicial trivial: todos os vértices na cobertura
    current = [True] * graph.num_vertices
    current_cost = _cost_function(graph, current, penalty)

    best = current[:]
    best_cost = current_cost

    tabu: Dict[Tuple[int, bool], int] = {}

    for it in range(1, max_iters + 1):
        best_move = None
        best_move_cost = float("inf")

        # Explora a vizinhança (todos os movimentos de 'flip' de 1 bit)
        for v in range(graph.num_vertices):
            # Simula o movimento de flip
            current[v] = not current[v]
            new_cost = _cost_function(graph, current, penalty)
            
            # Verifica se o movimento é tabu
            is_tabu = tabu.get((v, current[v]), 0) > it

            # Critério de aspiração: permite movimento tabu se melhora a melhor solução global
            if (not is_tabu) or (new_cost < best_cost):
                if new_cost < best_move_cost:
                    best_move_cost = new_cost
                    best_move = v

            # Desfaz o movimento para continuar a busca na vizinhança
            current[v] = not current[v]

        if best_move is None:
            break

        # Aplica o melhor movimento encontrado
        v = best_move
        old_state = current[v]
        current[v] = not current[v]
        current_cost = best_move_cost
        
        # Adiciona o inverso do movimento à lista tabu
        tabu[(v, old_state)] = it + tabu_tenure

        # Atualiza a melhor solução encontrada
        if current_cost < best_cost:
            best = current[:]
            best_cost = current_cost
            
    cover_vertices = [i for i, in_cover in enumerate(best) if in_cover]
    return cover_vertices, best_cost