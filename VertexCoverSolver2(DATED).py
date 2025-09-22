import random
from typing import List, Tuple, Dict, Optional, Set

class VertexCoverSolver:
    """
    Superclasse que encapsula diferentes algoritmos para resolver o problema de
    cobertura de vértices em um grafo.
    """
    
    # --- NOVO MÉTODO DE CLASSE PARA LER ARQUIVOS SNAP ---
    @classmethod
    def from_snap_file(cls, filepath: str):
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
        Subclasse interna que representa um grafo não direcionado simples.
        """
        def __init__(self, num_vertices: int, edges: List[Tuple[int, int]]):
            self.num_vertices = num_vertices
            self.edges = edges
            self.adj_list = [[] for _ in range(num_vertices)]
            for u, v in edges:
                if u == v:
                    continue
                self.adj_list[u].append(v)
                self.adj_list[v].append(u)

        def __repr__(self) -> str:
            # Mostra apenas o início da lista de arestas para não poluir a saída
            edge_preview = str(self.edges[:5]) + ('...' if len(self.edges) > 5 else '')
            return f"Graph(num_vertices={self.num_vertices}, num_edges={len(self.edges)}, edges_preview={edge_preview})"

        def all_edges_covered(self, cover: List[bool]) -> bool:
            return all(cover[u] or cover[v] for u, v in self.edges)

        def uncovered_edges_count(self, cover: List[bool]) -> int:
            return sum(1 for u, v in self.edges if not (cover[u] or cover[v]))

    # --- __init__ MODIFICADO para armazenar o mapa ---
    def __init__(self, num_vertices: int, edges: List[Tuple[int, int]], new_to_original_map: Optional[List[int]] = None):
        """
        Inicializa o solucionador com um grafo específico.
        """
        self.graph = self.Graph(num_vertices, edges)
        self.memo = {}
        # Armazena o mapa para traduzir os resultados de volta
        self.new_to_original_map = new_to_original_map

    # --- NOVO MÉTODO para traduzir resultados ---
    def remap_cover_to_original(self, cover_new_ids: List[int]) -> List[int]:
        """
        Converte uma cobertura de vértices com IDs internos (0 a N-1) de volta
        para os IDs originais do arquivo.
        """
        if self.new_to_original_map is None:
            print("Aviso: Grafo não foi criado a partir de um arquivo, retornando IDs internos.")
            return cover_new_ids
        
        return [self.new_to_original_map[new_id] for new_id in cover_new_ids]

    # ... (Restante dos seus métodos de algoritmos, sem alterações necessárias) ...
    # Eu ajustei os métodos para usar os nomes de atributos corretos da classe Graph, ex: self.graph.num_vertices
    
    def solve_approximation(self) -> Set[int]:
        vertex_is_covered = [False] * self.graph.num_vertices
        vertex_cover_set = set()
        for u, v in self.graph.edges:
            if not vertex_is_covered[u] and not vertex_is_covered[v]:
                vertex_is_covered[u] = True
                vertex_is_covered[v] = True
                vertex_cover_set.add(u)
                vertex_cover_set.add(v)
        return vertex_cover_set
        
    def _initial_solution_ts(self) -> List[bool]:
        return [True] * self.graph.num_vertices

    def _cost_function_ts(self, cover: List[bool], penalty: int) -> int:
        uncovered = self.graph.uncovered_edges_count(cover)
        size = sum(cover)
        return uncovered * penalty + size

    def solve_tabu_search(self, max_iters: int = 10000, tabu_tenure: int = 7, penalty: int = 1000) -> Tuple[List[int], int]:
        current = self._initial_solution_ts()
        current_cost = self._cost_function_ts(current, penalty)
        best = current[:]
        best_cost = current_cost
        tabu: Dict[Tuple[int, bool], int] = {}

        for it in range(1, max_iters + 1):
            best_move = None
            best_move_cost = float("inf")
            for v in range(self.graph.num_vertices):
                new_state = not current[v]
                current[v] = new_state
                new_cost = self._cost_function_ts(current, penalty)
                current[v] = not new_state
                is_tabu = tabu.get((v, not new_state), 0) > it
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
    
# --- Bloco de Teste Atualizado ---
if __name__ == "__main__":
    
    # Para testar, vamos criar um arquivo de exemplo chamado 'CA-GrQc.txt'
    # com o conteúdo que você forneceu.
    sample_content = """# Directed graph (each unordered pair of nodes is saved once): CA-GrQc.txt 
# Collaboration network of Arxiv General Relativity category
# Nodes: 5242 Edges: 28980
# FromNodeId     ToNodeId
3466    937
3466    5233
8579    3466
3466    10310
15931   3466
937     5233
100     200
200     300
"""
    with open('CA-GrQc.txt', 'w') as f:
        f.write(sample_content)
        
    # --- Uso do novo método ---
    # Agora, em vez de criar o grafo manualmente, usamos o método de fábrica
    solver_snap = VertexCoverSolver.from_snap_file('CA-GrQc2.txt')
    
    print("\n" + "=" * 50)
    print("TESTANDO GRAFO CARREGADO DO ARQUIVO SNAP")
    #print(f"Objeto Graph interno: {solver_snap.graph}")
    print(f"Número de vértices do grafo: {solver_snap.graph.num_vertices}")
    print("=" * 50)

    # 1. Testando o Algoritmo de Aproximação (é rápido, ideal para grafos grandes)
    print("\n--- 1. Algoritmo de Aproximação (Fator 2) ---")
    approx_cover_new_ids = solver_snap.solve_approximation()
    
    # Converte os IDs da cobertura de volta para os IDs originais do arquivo
    approx_cover_original_ids = solver_snap.remap_cover_to_original(sorted(list(approx_cover_new_ids)))
    
    print(f"Tamanho da cobertura encontrada: {len(approx_cover_original_ids)}")
    #print(f"Vértices na cobertura (IDs Originais): {approx_cover_original_ids}")
    
    # O algoritmo exato e a busca tabu funcionarão da mesma forma, mas podem ser
    # lentos para um grafo grande como o do SNAP.
    # Por exemplo, para a busca tabu:
    # ts_cover_new, ts_cost = solver_snap.solve_tabu_search(max_iters=100)
    # ts_cover_orig = solver_snap.remap_cover_to_original(ts_cover_new)
    # print(f"Cobertura da Busca Tabu (IDs Originais): {ts_cover_orig}")