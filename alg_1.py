def approx_vertex_cover(num_vertices, edges):
    """
    Implementa o algoritmo de aproximação de fator 2 para o Problema de Cobertura de Vértices
    com complexidade de tempo O(V + E), que simplifica para O(E) em grafos conexos.

    Args:
        num_vertices (int): O número de vértices no grafo (nomeados de 0 a V-1).
        edges (list of tuples): Uma lista de arestas, onde cada aresta é uma tupla (u, v).

    Returns:
        set: Um conjunto de vértices que formam a cobertura.
    """
    # Passo 1: Inicializar estruturas de dados.
    # A lista 'coberto' rastreia se um vértice já foi adicionado à cobertura.
    # Acessar um array/lista por índice é uma operação O(1).
    # Complexidade: O(V)
    vertex_is_covered = [False] * num_vertices
    
    # O conjunto que armazenará nossa cobertura de vértices.
    vertex_cover_set = set()

    # Passo 2: Iterar sobre todas as arestas do grafo.
    # Este loop executará exatamente E vezes.
    # Complexidade: O(E)
    for u, v in edges:
        # Passo 3: Verificar se a aresta (u, v) já está coberta.
        # Uma aresta está coberta se pelo menos um de seus vértices já está na cobertura.
        # As verificações em 'vertex_is_covered' são O(1).
        if not vertex_is_covered[u] and not vertex_is_covered[v]:
            # Se a aresta não está coberta, adicionamos AMBOS os vértices à cobertura.
            vertex_is_covered[u] = True
            vertex_is_covered[v] = True
            vertex_cover_set.add(u)
            vertex_cover_set.add(v)

    return vertex_cover_set

# --- Exemplo de Uso ---
# Grafo com 6 vértices (0 a 5) e 7 arestas
V = 6
# Lista de arestas (cada tupla é uma aresta)
arestas = [
    (0, 1), (1, 2), 
    (0, 2)
]

# Encontrar a cobertura de vértices aproximada
cobertura = approx_vertex_cover(V, arestas)

print(f"Número de Vértices: {V}")
print(f"Arestas: {arestas}")
print(f"Cobertura de Vértices encontrada (aproximada): {sorted(list(cobertura))}")
print(f"Tamanho da cobertura: {len(cobertura)}")

# Para este grafo, uma cobertura mínima ótima seria {0, 3, 4} ou {1, 2, 4}, com tamanho 3.
# O nosso algoritmo pode retornar {0, 1, 2, 3, 4, 5} dependendo da ordem das arestas,
# mas uma ordem comum de processamento daria {0, 1, 3, 2, 4, 5} -> {0,1} da (0,1),
# {3,2} da (2,3) [pois (1,3) já está coberto por 1], {4,5} da (4,5) [pois (2,4) já está coberto por 2].
# Resultando em {0, 1, 2, 3, 4, 5}.
# Se a aresta (1,3) fosse processada primeiro, o resultado seria {1,3}, {2,4}, {0} [da 0,2], {5} [da 4,5]
# O ponto principal é que o tamanho da cobertura encontrada será no máximo 2x o tamanho da ótima.
# Neste caso, 2 * 3 = 6. Nossa cobertura de tamanho 4 ou 6 (dependendo da ordem) satisfaz a condição.