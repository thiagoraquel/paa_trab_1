
# --- Bloco de Teste ---
if __name__ == "__main__":
    # Grafo de exemplo 1: Um pouco mais complexo para testar os algoritmos
    num_vertices_g1 = 6
    arestas_g1 = [
        (0, 1), (0, 2), (1, 3), (2, 3),
        (2, 4), (3, 4), (4, 5)
    ]
    
    # Inicializa o solucionador para o primeiro grafo
    solver_g1 = VertexCoverSolver(num_vertices_g1, arestas_g1)
    
    print("=" * 50)
    #print(f"TESTANDO GRAFO 1: {solver_g1.graph}")
    print("=" * 50)

    # 1. Testando o Algoritmo de Aproximação
    print("\n--- 1. Algoritmo de Aproximação (Fator 2) ---")
    approx_cover = solver_g1._solve_approximation()
    #print(f"Cobertura encontrada: {sorted(list(approx_cover))}")
    print(f"Tamanho da cobertura: {len(approx_cover)}")

    # 2. Testando a Busca Tabu
    print("\n--- 2. Busca Tabu ---")
    ts_cover, ts_cost = solver_g1._solve_tabu_search(max_iters=5000, rng_seed=42)
    #print(f"Cobertura encontrada: {sorted(ts_cover)}")
    print(f"Custo final da solução: {ts_cost}")
    # Verificação final
    cover_bool = [i in ts_cover for i in range(solver_g1.graph.num_vertices)]
    print(f"Todas as arestas estão cobertas? {solver_g1.graph._all_edges_covered(cover_bool)}")

    # ----------------------------------------------------------------------------------

    # Grafo de exemplo 2: Pequeno, adequado para o algoritmo exato
    num_vertices_g2 = 4
    arestas_g2 = [
        (0, 1), (0, 2), (0, 3),
        (1, 2)
    ]
    
    # Inicializa o solucionador para o segundo grafo
    solver_g2 = VertexCoverSolver(num_vertices_g2, arestas_g2)
    
    print("\n" + "=" * 50)
    #print(f"TESTANDO GRAFO 2: {solver_g2.graph}")
    print("=" * 50)
    
    # 3. Testando o Algoritmo Exato Recursivo
    # Nota: Este algoritmo é muito lento para o Grafo 1, por isso usamos o Grafo 2.
    
    #print("\n--- 3. Algoritmo Exato (Recursivo com Memoização) ---")
    #optimal_size = solver_g2._solve_exact_recursive()
    #print(f"Tamanho da Cobertura MÍNIMA (Ótima): {optimal_size}")

        # --- Uso do novo método ---
    # Agora, em vez de criar o grafo manualmente, usamos o método de fábrica
    solver_snap = VertexCoverSolver._from_snap_file('CA-GrQc2.txt')
    
    print("\n" + "=" * 50)
    print("TESTANDO GRAFO CARREGADO DO ARQUIVO SNAP")
    #print(f"Objeto Graph interno: {solver_snap.graph}")
    print(f"Número de vértices do grafo: {solver_snap.graph.num_vertices}")
    print("=" * 50)

    # 1. Testando o Algoritmo de Aproximação (é rápido, ideal para grafos grandes)
    print("\n--- 1. Algoritmo de Aproximação (Fator 2) ---")
    approx_cover_new_ids = solver_snap._solve_approximation()
    
    # Converte os IDs da cobertura de volta para os IDs originais do arquivo
    approx_cover_original_ids = solver_snap._remap_cover_to_original(sorted(list(approx_cover_new_ids)))
    
    print(f"Tamanho da cobertura encontrada: {len(approx_cover_original_ids)}")

    # 2. Testando a Busca Tabu
    print("\n--- 2. Busca Tabu ---")
    ts_cover, ts_cost = solver_snap._solve_tabu_search(max_iters=500, rng_seed=42)
    #print(f"Cobertura encontrada: {sorted(ts_cover)}")
    print(f"Custo final da solução: {ts_cost}")
    # Verificação final
    cover_bool = [i in ts_cover for i in range(solver_snap.graph.num_vertices)]
    print(f"Todas as arestas estão cobertas? {solver_snap.graph._all_edges_covered(cover_bool)}")
    