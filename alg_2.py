# Usamos um dicionário 'memo' para armazenar os resultados de subproblemas já calculados.
# A chave será um 'frozenset' de arestas (imutável), e o valor será o tamanho da cobertura mínima para aquele subgrafo.
memo = {}

def encontrar_cobertura_exata_recursivo(arestas_restantes):
    """
    Função recursiva auxiliar que encontra o tamanho da cobertura mínima de vértices.
    Utiliza um frozenset de arestas para representar o estado do grafo.
    """
    # Converter para frozenset para que possa ser usado como chave de dicionário (memoização)
    arestas_restantes_fs = frozenset(arestas_restantes)
    
    # --- CASO BASE ---
    # Se não há mais arestas, a cobertura necessária é 0.
    if not arestas_restantes_fs:
        return 0
        
    # --- MEMOIZAÇÃO ---
    # Se já resolvemos este subproblema antes, retornamos o resultado armazenado.
    if arestas_restantes_fs in memo:
        return memo[arestas_restantes_fs]

    # --- PASSO RECURSIVO ---
    # 1. Escolha uma aresta (u, v) do grafo restante.
    # Usamos next(iter(...)) para pegar um elemento qualquer do conjunto de forma eficiente.
    u, v = next(iter(arestas_restantes_fs))
    
    # 2. Ramo 1: Adicionar o vértice 'u' à cobertura.
    #    Removemos 'u' e todas as suas arestas incidentes.
    arestas_apos_remover_u = {aresta for aresta in arestas_restantes_fs if u not in aresta}
    custo1 = 1 + encontrar_cobertura_exata_recursivo(arestas_apos_remover_u)
    
    # 3. Ramo 2: Adicionar o vértice 'v' à cobertura.
    #    Removemos 'v' e todas as suas arestas incidentes.
    arestas_apos_remover_v = {aresta for aresta in arestas_restantes_fs if v not in aresta}
    custo2 = 1 + encontrar_cobertura_exata_recursivo(arestas_apos_remover_v)
    
    # 4. A solução ótima para este estado é o mínimo entre os dois ramos.
    resultado = min(custo1, custo2)
    
    # Armazenamos o resultado no dicionário de memoização antes de retornar.
    memo[arestas_restantes_fs] = resultado
    
    return resultado

def cobertura_minima_exata(num_vertices, arestas):
    """
    Função principal que prepara e inicia a busca pela cobertura mínima exata.
    """
    # Limpa o cache de memoização para garantir que execuções anteriores não interfiram.
    global memo
    memo = {}
    
    # A entrada 'arestas' é uma lista de tuplas. Convertê-la para um set no início
    # pode otimizar as operações subsequentes.
    conjunto_de_arestas = set(frozenset(aresta) for aresta in arestas) # Normaliza (1,0) e (0,1)
    
    return encontrar_cobertura_exata_recursivo(conjunto_de_arestas)


# --- Exemplo de Uso ---
# O mesmo grafo do exemplo anterior
V = 6
arestas = [
    (0, 1), (0, 2), (1, 3), (2, 3),
    (2, 4), (3, 4), (4, 5)
]

arestas_2 = [
    (0, 1), (0, 2), (0, 3),
    (1, 2)
]

print("--- Algoritmo Exato (Recursivo com Poda) ---")
tamanho_cobertura_otima = cobertura_minima_exata(V, arestas_2)

print(f"Número de Vértices: {V}")
print(f"Arestas: {arestas_2}")
print(f"Tamanho da Cobertura de Vértices MÍNIMA (Ótima): {tamanho_cobertura_otima}")

# A solução ótima para este grafo é 3. Ex: {1, 2, 4} ou {0, 3, 4}.
# O algoritmo deve retornar o tamanho 3.