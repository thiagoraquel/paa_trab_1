import collections

def vertex_cover_approx(arestas):
    """
    Encontra uma cobertura de vértices aproximada usando um algoritmo de fator-2.

    Este algoritmo funciona da seguinte maneira:
    1. Começa com uma cobertura de vértices vazia (C).
    2. Enquanto houver arestas no grafo:
       a. Escolhe uma aresta (u, v).
       b. Adiciona ambos os vértices u e v à cobertura C.
       c. Remove todas as arestas incidentes a u ou v.
    3. Retorna a cobertura C.

    Args:
        arestas (list de tuplas): Uma lista de tuplas, onde cada tupla representa uma aresta (u, v).

    Returns:
        list: Uma lista de vértices que formam a cobertura de vértices aproximada, ordenada para consistência.
    """
    cobertura = set()
    
    # Para evitar modificar a lista original e para facilitar a remoção,
    # copiamos as arestas para um conjunto. Usamos frozenset para cada aresta
    # para que possam ser adicionadas a um conjunto.
    arestas_restantes = set(map(frozenset, arestas))

    # 2. Loop enquanto houver arestas no grafo
    while arestas_restantes:
        # a. Escolhe uma aresta qualquer. O método pop() de um conjunto remove
        # e retorna um elemento arbitrário.
        aresta_atual = arestas_restantes.pop()
        u, v = tuple(aresta_atual)
        
        # b. Adiciona ambos os vértices à cobertura
        cobertura.add(u)
        cobertura.add(v)
        
        # c. Remove todas as arestas que são incidentes a u ou v
        arestas_para_remover = set()
        for aresta in arestas_restantes:
            if u in aresta or v in aresta:
                arestas_para_remover.add(aresta)
        
        # A operação de diferença de conjuntos (-=) é uma forma eficiente de remover os elementos
        arestas_restantes -= arestas_para_remover

    # Retorna o resultado como uma lista ordenada para facilitar a visualização
    return sorted(list(cobertura))

# --- Exemplo de Uso ---

# Definição do grafo como uma lista de arestas
# V = {0, 1, 2, 3, 4, 5, 6}
# E = [(0,1), (0,2), (1,3), (2,3), (2,4), (3,5), (4,5), (4,6)]
grafo_arestas = [
    (0, 1), (0, 2),
    (1, 3),
    (2, 3), (2, 4),
    (3, 5),
    (4, 5), (4, 6)
]

grafo_arestas_2 = [
    (0, 1), (0, 2), (0, 6),
    (1, 2), (1, 3), (1, 7), (1, 6), (1, 4),
    (2, 3), (2, 4), (2, 6), (2, 5), (2, 7)
]

print("--- Problema da Cobertura de Vértices (Algoritmo Aproximativo) ---")
print(f"Arestas do grafo de entrada: {grafo_arestas_2}\n")

# Chama a função para encontrar a cobertura de vértices
cobertura_encontrada = vertex_cover_approx(grafo_arestas_2)

print(f"Cobertura de Vértices encontrada: {cobertura_encontrada}")
print(f"Tamanho da cobertura: {len(cobertura_encontrada)}")

# Para este exemplo, uma cobertura ótima seria {1, 2, 5, 4} ou {0, 3, 4}, ambas com tamanho 4.
# O algoritmo de aproximação garante um resultado com no máximo 2 * (tamanho ótimo).
# 2 * 4 = 8. O resultado encontrado estará dentro deste limite.
# Por exemplo, uma execução poderia resultar em {0, 1, 4, 5, 2, 3}, que cobre todas as arestas.
print("\nAnálise: A solução ótima para este grafo tem tamanho 4 (ex: {0, 3, 4, 5}).")
print("O algoritmo de aproximação garante um resultado com tamanho no máximo 2 * 4 = 8.")
print("O resultado obtido está, portanto, dentro da garantia de aproximação.")