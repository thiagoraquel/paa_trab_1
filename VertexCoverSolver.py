import random
import matplotlib.pyplot as plt
import networkx as nx
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
    def _from_generated_file(cls, filepath: str):
        """
        Cria uma instância de VertexCoverSolver a partir de um arquivo .txt
        gerado por um dos modelos (Erdos-Renyi, etc.). Este método assume
        que os IDs dos vértices são sequenciais a partir de 0 e que não há
        arestas duplicadas ou laços no arquivo.

        Args:
            filepath (str): O caminho para o arquivo .txt do grafo gerado.

        Returns:
            VertexCoverSolver: Uma nova instância da classe com o grafo carregado.
        """
        edges = []
        max_vertex_id = -1

        print(f"Lendo o arquivo de grafo gerado: {filepath}...")
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    # Ignora linhas de comentário que começam com '#'
                    if line.startswith('#'):
                        continue
                    
                    # Ignora linhas em branco
                    if not line.strip():
                        continue

                    try:
                        u_str, v_str = line.strip().split()
                        u, v = int(u_str), int(v_str)
                        
                        edges.append((u, v))
                        
                        # Mantém o controle do maior ID de vértice encontrado
                        current_max = max(u, v)
                        if current_max > max_vertex_id:
                            max_vertex_id = current_max
                            
                    except ValueError:
                        print(f"Aviso: Ignorando linha mal formatada: '{line.strip()}'")
                        continue
            
            # O número de vértices em um grafo 0-indexado é o maior ID + 1.
            # Se o grafo estiver vazio, max_vertex_id será -1, resultando em 0 vértices.
            num_vertices = max_vertex_id + 1
            
            # Se não houver arestas e nenhum vértice, num_vertices será 0.
            # Se um grafo tiver vértices isolados, eles podem não estar na lista de arestas.
            # Os cabeçalhos do nosso arquivo gerado ajudam a verificar isso.
            # Para este método simplificado, confiamos que N = max_id + 1.
            if num_vertices == 0 and edges:
                 raise ValueError("Erro: Arestas encontradas, mas nenhum vértice válido foi identificado.")

            print("Grafo carregado com sucesso!")
            print(f"  - Vértices: {num_vertices}")
            print(f"  - Arestas: {len(edges)}")
            
            # Como não há remapeamento, o mapa de tradução é None.
            # A classe já lida com isso.
            return cls(num_vertices, edges)

        except FileNotFoundError:
            print(f"Erro: Arquivo não encontrado em '{filepath}'")
            return None
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao ler o arquivo: {e}")
            return None

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

    # --- Algoritmo 2: Exato Recursivo (MODIFICADO PARA RETORNAR OS VÉRTICES) ---
    def _find_exact_cover_nodes_recursive(self, remaining_edges_fs: frozenset) -> frozenset:
        """
        Função recursiva que encontra o CONJUNTO de vértices da cobertura mínima.
        """
        if not remaining_edges_fs:
            return frozenset()
        
        if remaining_edges_fs in self.memo:
            return self.memo[remaining_edges_fs]

        # Pega uma aresta qualquer para decidir
        u, v = next(iter(remaining_edges_fs))
        
        # Ramo 1: Adicionar 'u' à cobertura
        edges_after_removing_u = frozenset({edge for edge in remaining_edges_fs if u not in edge})
        cover1 = {u}.union(self._find_exact_cover_nodes_recursive(edges_after_removing_u))
        
        # Ramo 2: Adicionar 'v' à cobertura
        edges_after_removing_v = frozenset({edge for edge in remaining_edges_fs if v not in edge})
        cover2 = {v}.union(self._find_exact_cover_nodes_recursive(edges_after_removing_v))
        
        # Escolhe a cobertura de menor tamanho
        result = cover1 if len(cover1) < len(cover2) else cover2
        self.memo[remaining_edges_fs] = result
        
        return result

    def _solve_exact_with_nodes(self) -> Set[int]:
        """
        Função principal que inicia a busca pela cobertura mínima exata,
        retornando o conjunto de vértices.
        """
        self.memo.clear()
        edge_set = frozenset(map(frozenset, self.graph.edges))
        return self._find_exact_cover_nodes_recursive(edge_set)

    # --- Algoritmo 3: Busca Tabu (Meta-heurística) ---
    def _solve_tabu_search(
        self,
        max_iters: int = 10000,
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

def visualizar_grafo_com_cobertura(solver: VertexCoverSolver, cover_nodes: Set[int], title: str):
    """
    Cria e exibe uma visualização de um grafo, destacando os nós da cobertura.

    Args:
        solver (VertexCoverSolver): A instância do solver contendo o grafo.
        cover_nodes (Set[int]): Um conjunto com os IDs dos vértices na cobertura.
        title (str): O título do gráfico.
    """
    # Cria um objeto de grafo do networkx a partir dos dados do solver
    g = nx.Graph()
    g.add_nodes_from(range(solver.graph.num_vertices))
    g.add_edges_from(solver.graph.edges)

    # Define as cores dos nós: vermelho para cobertura, azul para os demais
    node_colors = []
    for node in g.nodes():
        if node in cover_nodes:
            node_colors.append('tomato')  # Cor para nós na cobertura
        else:
            node_colors.append('skyblue') # Cor para nós fora da cobertura

    plt.figure(figsize=(12, 10))
    
    # Usa um layout que tenta evitar sobreposição de nós
    pos = nx.spring_layout(g, seed=42)
    
    # Desenha o grafo
    nx.draw(g, pos,
            with_labels=True,      # Mostra os IDs dos vértices
            node_color=node_colors,  # Aplica a lista de cores
            node_size=600,         # Tamanho dos nós
            font_size=10,          # Tamanho da fonte dos IDs
            width=1.5)             # Largura das arestas

    plt.title(title, size=16)
    plt.show()

# --- Bloco de Teste ---
if __name__ == "__main__":
    
    # Use o novo método para carregar os arquivos gerados
    print("=" * 50)
    print("Testando grafo Erdos-Renyi com 34 vértices (método simplificado)")
    #caminho_arquivo_er30 = 'grafos_de_teste/erdos_renyi_n35_p0.2.txt'
    #caminho_arquivo_er30 = 'grafos_de_teste/barabasi_albert_n35_m3.txt'
    caminho_arquivo_er30 = 'grafos_de_teste/watts_strogatz_n35_k4_p0.25.txt'

    # Chamando o novo método, mais eficiente
    solver_er30 = VertexCoverSolver._from_generated_file(caminho_arquivo_er30)
    
    if solver_er30:
        # --- 1. Algoritmo de Aproximação (Fator 2) ---
        print("\n--- 1. Algoritmo de Aproximação (Fator 2) ---")
        approx_cover = solver_er30._solve_approximation()
        print(f"Vértices encontrados: {sorted(list(approx_cover))}")
        print(f"Tamanho da cobertura: {len(approx_cover)}")
        # Visualização
        visualizar_grafo_com_cobertura(solver_er30, approx_cover, "Cobertura - Algoritmo de Aproximação")

        # --- 2. Algoritmo Exato ---
        print("\n--- 2. Algoritmo Exato ---")
        # Chamando a nova função que retorna os nós
        optimal_cover_nodes = solver_er30._solve_exact_with_nodes()
        print(f"Vértices encontrados: {sorted(list(optimal_cover_nodes))}")
        print(f"Tamanho da cobertura ótima: {len(optimal_cover_nodes)}")
        # Visualização
        visualizar_grafo_com_cobertura(solver_er30, optimal_cover_nodes, "Cobertura - Algoritmo Exato (Ótimo)")
        
        # --- 3. Busca Tabu ---
        print("\n--- 3. Busca Tabu ---")
        ts_cover, ts_cost = solver_er30._solve_tabu_search(max_iters=1000, rng_seed=42)
        print(f"Vértices encontrados: {sorted(ts_cover)}")
        # O custo da busca tabu inclui penalidades, o tamanho real é len(ts_cover)
        print(f"Tamanho da cobertura: {len(ts_cover)}")
        print(f"Custo final da solução (tamanho + penalidades): {ts_cost}")
        # Visualização
        visualizar_grafo_com_cobertura(solver_er30, set(ts_cover), "Cobertura - Busca Tabu")