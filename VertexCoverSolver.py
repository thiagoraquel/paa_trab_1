import random
import networkx
from typing import List, Tuple, Dict, Optional, Set

class VertexCoverSolver:
    """
    Superclasse que encapsula diferentes algoritmos para resolver o problema de
    cobertura de vértices em um grafo.

    Atributos:
        graph (Graph): O objeto de grafo no qual os algoritmos serão executados.
        memo (Dict): Um cache para memoização usado pelo algoritmo exato.
    """
    @classmethod
    def _from_snap_file(cls, filepath: str):
        """
        Cria uma instância de VertexCoverSolver a partir de um arquivo de texto no formato SNAP.
        Este método lida com IDs de vértices não sequenciais e arestas duplicadas.

        Args:
            filepath (str): O caminho para o arquivo .txt do dataset.

        Returns:
            VertexCoverSolver: Uma nova instância da classe com o grafo carregado e mapeado.
        """
        unique_edges = set()
        all_node_ids = set()

        print(f"Lendo o arquivo de grafo: {filepath}...")
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                try:
                    u_str, v_str = line.strip().split()
                    u_orig, v_orig = int(u_str), int(v_str)
                    
                    # Ignora laços (arestas de um nó para ele mesmo)
                    if u_orig == v_orig:
                        continue

                    all_node_ids.add(u_orig)
                    all_node_ids.add(v_orig)
                    
                    # Normaliza a aresta para evitar duplicatas (ex: (1,0) e (0,1))
                    edge = tuple(sorted((u_orig, v_orig)))
                    unique_edges.add(edge)
                except ValueError:
                    # Ignora linhas mal formatadas
                    continue
        
        # --- Mapeamento de IDs Originais para Novos IDs (0 a N-1) ---
        # Ordenar garante que o mapeamento seja sempre o mesmo
        sorted_original_ids = sorted(list(all_node_ids))
        
        # Mapa para converter IDs originais para os novos, internos ao algoritmo
        map_original_to_new = {original_id: new_id for new_id, original_id in enumerate(sorted_original_ids)}
        
        # Lista para converter os resultados de volta para os IDs originais
        # O índice da lista é o novo ID, o valor é o ID original.
        list_new_to_original = sorted_original_ids
        
        # --- Remapeia as arestas para usar os novos IDs ---
        remapped_edges = []
        for u_orig, v_orig in unique_edges:
            new_u = map_original_to_new[u_orig]
            new_v = map_original_to_new[v_orig]
            remapped_edges.append((new_u, new_v))
            
        num_vertices = len(all_node_ids)
        print(f"Grafo carregado com sucesso!")
        print(f"  - Vértices únicos: {num_vertices}")
        print(f"  - Arestas únicas: {len(remapped_edges)}")
        
        # Cria a instância da classe com os dados processados e o mapa de tradução
        return cls(num_vertices, remapped_edges, list_new_to_original)

    class Graph:
        """
        Representa um grafo não direcionado simples. É uma subclasse interna
        para manter a estrutura do grafo junto com os algoritmos que a utilizam.

        Atributos:
            num_vertices (int): Número de vértices (0 a n-1).
            edges (List[Tuple[int, int]]): Lista de arestas (u, v).
            list_adj (List[List[int]]): Lista de adjacência para acesso rápido aos vizinhos.
        """
        def __init__(self, num_vertices: int, edges: List[Tuple[int, int]]):
            self.num_vertices = num_vertices
            self.edges = edges
            self.list_adj = [[] for _ in range(num_vertices)]
            for a, b in edges:
                if a == b:
                    continue
                self.list_adj[a].append(b)
                self.list_adj[b].append(a)

        def __repr__(self) -> str:
            return f"Graph(num_vertices={self.num_vertices}, arestas={self.edges})"

        def _all_edges_covered(self, cover: List[bool]) -> bool:
            """Verifica se uma dada cobertura de vértices cobre todas as arestas."""
            return all(cover[a] or cover[b] for a, b in self.edges)

        def _uncovered_edges_count(self, cover: List[bool]) -> int:
            """Conta o número de arestas não cobertas por uma dada solução."""
            return sum(1 for a, b in self.edges if not (cover[a] or cover[b]))

    def __init__(self, num_vertices: int, edges: List[Tuple[int, int]], new_to_original_map: Optional[List[int]] = None):
        """
        Inicializa o solucionador com um grafo específico.

        Args:
            num_vertices (int): O número de vértices no grafo.
            edges (List[Tuple[int, int]]): A lista de arestas do grafo.
        """
        self.graph = self.Graph(num_vertices, edges)
        self.memo = {}
        # Armazena o mapa para traduzir os resultados de volta
        self.new_to_original_map = new_to_original_map

        # --- NOVO MÉTODO para traduzir resultados ---
    def _remap_cover_to_original(self, cover_new_ids: List[int]) -> List[int]:
        """
        Converte uma cobertura de vértices com IDs internos (0 a N-1) de volta
        para os IDs originais do arquivo.
        """
        if self.new_to_original_map is None:
            print("Aviso: Grafo não foi criado a partir de um arquivo, retornando IDs internos.")
            return cover_new_ids
        
        return [self.new_to_original_map[new_id] for new_id in cover_new_ids]

    def _find_exact_cover_recursive(self, remaining_edges_fs: frozenset) -> int:
        """
        Função recursiva auxiliar que encontra o tamanho da cobertura mínima.
        """
        if not remaining_edges_fs:
            return 0
        
        if remaining_edges_fs in self.memo:
            return self.memo[remaining_edges_fs]

        u, v = next(iter(remaining_edges_fs))
        
        # Ramo 1: Adicionar 'u' à cobertura
        edges_after_removing_u = {edge for edge in remaining_edges_fs if u not in edge}
        cost1 = 1 + self._find_exact_cover_recursive(frozenset(edges_after_removing_u))
        
        # Ramo 2: Adicionar 'v' à cobertura
        edges_after_removing_v = {edge for edge in remaining_edges_fs if v not in edge}
        cost2 = 1 + self._find_exact_cover_recursive(frozenset(edges_after_removing_v))
        
        result = min(cost1, cost2)

        #revisar se isto é necessário depois
        self.memo[remaining_edges_fs] = result
        
        return result
    
    # _ts é para a taboo search
    def _initial_solution_ts(self) -> List[bool]:
        """Solução inicial trivial: todos os vértices na cobertura."""
        return [True] * self.graph.num_vertices

    # _ts é para a taboo search
    def _cost_function_ts(self, cover: List[bool], penalty: int) -> int:
        """
        Função de custo para a Busca Tabu.
        Penaliza arestas não cobertas e o tamanho da cobertura.
        """
        uncovered = self.graph._uncovered_edges_count(cover)
        size = sum(cover)
        return uncovered * penalty + size

    # --- Algoritmo 1: Aproximação de Fator 2 ---
    def _solve_approximation(self) -> Set[int]:
        """
        Implementa o algoritmo de aproximação de fator 2.
        Itera sobre as arestas e adiciona ambos os vértices à cobertura se a aresta
        não estiver coberta.

        Returns:
            Set[int]: Um conjunto de vértices que formam a cobertura.
        """
        vertex_is_covered = [False] * self.graph.num_vertices
        vertex_cover_set = set()

        for u, v in self.graph.edges:
            if not vertex_is_covered[u] and not vertex_is_covered[v]:
                vertex_is_covered[u] = True
                vertex_is_covered[v] = True
                vertex_cover_set.add(u)
                vertex_cover_set.add(v)
        
        return vertex_cover_set

    # --- Algoritmo 2: Exato Recursivo com Memoização ---
    def _solve_exact_recursive(self) -> int:
        """
        Função principal que inicia a busca pela cobertura mínima exata.
        Usa recursão com poda e memoização para encontrar a solução ótima.
        
        AVISO: Este algoritmo tem complexidade exponencial e é inviável
        para grafos grandes.

        Returns:
            int: O tamanho da cobertura de vértices mínima (ótima).
        """
        self.memo.clear()  # Limpa o cache para execuções limpas
        
        # Normaliza arestas (ex: (1,0) e (0,1) são a mesma coisa) e converte para frozenset
        edge_set = set(frozenset(edge) for edge in self.graph.edges)
        
        return self._find_exact_cover_recursive(frozenset(edge_set))

    # --- Algoritmo 3: Busca Tabu (Meta-heurística) ---
    def _solve_tabu_search(
        self,
        max_iters: int = 500,
        tabu_tenure: int = 7,
        penalty: int = 1000,
        rng_seed: Optional[int] = None
    ) -> Tuple[List[int], int]:
        """
        Busca Tabu para Cobertura de Vértices.

        Args:
            max_iters (int): Número máximo de iterações.
            tabu_tenure (int): Por quantas iterações um movimento é considerado tabu.
            penalty (int): Peso para cada aresta não coberta na função de custo.
            rng_seed (Optional[int]): Semente para o gerador de números aleatórios.

        Returns:
            Tuple[List[int], int]: Uma tupla contendo os vértices da melhor cobertura
                                   encontrada e o seu custo.
        """
        rng = random.Random(rng_seed)
        current = self._initial_solution_ts()
        current_cost = self._cost_function_ts(current, penalty)

        best = current[:]
        best_cost = current_cost

        # Lista tabu: (vértice, estado_antigo) -> iteração_expiração
        tabu: Dict[Tuple[int, bool], int] = {}

        for it in range(1, max_iters + 1):
            best_move = None
            best_move_cost = float("inf")

            for v in range(self.graph.num_vertices):
                new_state = not current[v]
                
                # Simula o movimento
                current[v] = new_state
                new_cost = self._cost_function_ts(current, penalty)
                current[v] = not new_state  # Desfaz o movimento

                is_tabu = tabu.get((v, not new_state), 0) > it

                # Critério de aspiração: permite movimento tabu se melhora a melhor solução global
                if (not is_tabu) or (new_cost < best_cost):
                    if new_cost < best_move_cost:
                        best_move_cost = new_cost
                        best_move = (v, new_state)

            if best_move is None:
                break

            v, new_state = best_move
            old_state = current[v]
            current[v] = new_state
            current_cost = best_move_cost

            if current_cost < best_cost:
                best = current[:]
                best_cost = current_cost

            tabu[(v, old_state)] = it + tabu_tenure

        cover_vertices = [i for i, in_cover in enumerate(best) if in_cover]
        return cover_vertices, best_cost


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