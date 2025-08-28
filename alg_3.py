import random
from typing import List, Tuple, Dict, Optional

class Graph:
    """
    Grafo não direcionado simples.
    n: número de vértices (0..n-1)
    edges: lista de arestas (u, v)
    """
    def __init__(self, n: int, edges: List[Tuple[int, int]]):
        self.n = n
        self.edges = edges
        self.adj = [[] for _ in range(n)]
        for u, v in edges:
            if u == v:
                continue
            self.adj[u].append(v)
            self.adj[v].append(u)

    def uncovered_edges(self, cover: List[bool]) -> int:
        """Conta o número de arestas não cobertas."""
        return sum(1 for u, v in self.edges if not (cover[u] or cover[v]))

    def all_edges_covered(self, cover: List[bool]) -> bool:
        return all(cover[u] or cover[v] for u, v in self.edges)


def initial_solution(g: Graph) -> List[bool]:
    """Solução inicial trivial: todos os vértices na cobertura."""
    return [True] * g.n


def cost_function(g: Graph, cover: List[bool], penalty: int = 1000) -> int:
    """
    Custo: penaliza fortemente arestas não cobertas e depois o tamanho do conjunto.
    penalty: peso para cada aresta não coberta (valor alto para priorizar viabilidade)
    """
    uncovered = g.uncovered_edges(cover)
    size = sum(cover)
    return uncovered * penalty + size


def neighbors(g: Graph, cover: List[bool]) -> List[Tuple[int, bool]]:
    """
    Movimentos possíveis: adicionar um vértice fora da cobertura ou remover um vértice da cobertura.
    Retorna lista de (vértice, novo_estado).
    """
    moves = []
    for v in range(g.n):
        moves.append((v, not cover[v]))
    return moves


def tabu_search_vertex_cover(
    g: Graph,
    max_iters: int = 10000,
    tabu_tenure: int = 7,
    penalty: int = 1000,
    rng_seed: Optional[int] = None
) -> Tuple[List[bool], int]:
    """
    Busca Tabu para Cobertura de Vértices.
    Retorna (melhor_cobertura, custo_dela).
    """
    rng = random.Random(rng_seed)
    current = initial_solution(g)
    current_cost = cost_function(g, current, penalty)

    best = current[:]
    best_cost = current_cost

    # Lista tabu: (vértice, estado_antigo) -> iteração_expiração
    tabu: Dict[Tuple[int, bool], int] = {}

    for it in range(1, max_iters + 1):
        best_move = None
        best_move_cost = float("inf")

        for v in range(g.n):
            new_state = not current[v]
            move = (v, new_state)
            # Aplica movimento
            current[v] = new_state
            new_cost = cost_function(g, current, penalty)
            current[v] = not new_state  # desfaz para testar outros

            is_tabu = tabu.get((v, not new_state), 0) > it

            # Aspiração: permite tabu se melhora melhor_global
            if (not is_tabu) or (new_cost < best_cost):
                if new_cost < best_move_cost:
                    best_move_cost = new_cost
                    best_move = (v, new_state)

        if best_move is None:
            break  # sem movimentos possíveis (raro)

        # Aplica melhor movimento
        v, new_state = best_move
        old_state = current[v]
        current[v] = new_state
        current_cost = best_move_cost

        # Atualiza melhor global
        if current_cost < best_cost:
            best = current[:]
            best_cost = current_cost

        # Atualiza tabu: impedir reverter movimento recente
        tabu[(v, old_state)] = it + tabu_tenure

    return best, best_cost


if __name__ == "__main__":
    # Exemplo: Grafo simples (ciclo de 5 vértices)
    n = 5
    edges = [(0,1),(1,2),(2,3),(3,4),(4,0)]
    g = Graph(n, edges)

    best_cover, cost = tabu_search_vertex_cover(g, max_iters=2000, tabu_tenure=7, rng_seed=42)

    cover_vertices = [i for i, in_cover in enumerate(best_cover) if in_cover]
    print("Cobertura encontrada:", cover_vertices)
    print("Custo final:", cost)
    print("Todas as arestas cobertas?", g.all_edges_covered(best_cover))
