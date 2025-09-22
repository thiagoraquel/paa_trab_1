# graph.py

from typing import List, Tuple

class Graph:
    """
    Representa um grafo não direcionado simples.

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
            if a >= num_vertices or b >= num_vertices:
                raise ValueError(f"Vértice {a} ou {b} está fora do intervalo [0, {num_vertices-1}]")
            if a == b:
                continue
            self.list_adj[a].append(b)
            self.list_adj[b].append(a)

    def count_uncovered_edges(self, cover: List[bool]) -> int:
        """Conta o número de arestas não cobertas por uma dada solução."""
        return sum(1 for a, b in self.edges if not (cover[a] or cover[b]))


    @classmethod
    def from_generated_file(cls, filepath: str):
        """
        Cria uma instância de Graph a partir de um arquivo .txt.

        Args:
            filepath (str): O caminho para o arquivo .txt do grafo gerado.

        Returns:
            Graph: Uma nova instância da classe com o grafo carregado, ou None em caso de erro.
        """
        edges = []
        max_vertex_id = -1

        print(f"Lendo o arquivo de grafo gerado: {filepath}...")
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    
                    try:
                        u_str, v_str = line.strip().split()
                        u, v = int(u_str), int(v_str)
                        edges.append((u, v))
                        max_vertex_id = max(max_vertex_id, u, v)
                    except ValueError:
                        print(f"Aviso: Ignorando linha mal formatada: '{line.strip()}'")
                        continue
            
            num_vertices = max_vertex_id + 1
            if num_vertices == 0 and edges:
                 raise ValueError("Erro: Arestas encontradas, mas nenhum vértice válido foi identificado.")

            print("Grafo carregado com sucesso!")
            print(f"  - Vértices: {num_vertices}")
            print(f"  - Arestas: {len(edges)}")
            
            return cls(num_vertices, edges)

        except FileNotFoundError:
            print(f"Erro: Arquivo não encontrado em '{filepath}'")
            return None
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao ler o arquivo: {e}")
            return None