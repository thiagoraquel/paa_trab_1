import time
import csv
import networkx as nx
from solvers.approximation import solve_approximation
from solvers.exact import ExactSolver
from solvers.tabu_search import solve_tabu_search
from graph import Graph

def nx_to_custom_graph(nx_graph) -> Graph:
    """
    Converte um grafo NetworkX para a classe Graph do projeto.

    Args:
        nx_graph (networkx.Graph): Grafo NetworkX.

    Returns:
        Graph: Grafo convertido para a classe própria.
    """
    num_vertices = nx_graph.number_of_nodes()
    edges = list(nx_graph.edges())
    return Graph(num_vertices, edges)

def run_experiments(start: int, stop: int, step: int, algorithm: int, repetitions: int = 40, gerador: int = 1):
                    results = []
                    sizes = list(range(start, stop + 1, step))
                    algo_name = {1: "Aproximado", 2: "Exato", 3: "Busca_Tabu"}[algorithm]
                    gerador_name = {1: "Erdos-Renyi", 2: "Barabasi-Albert", 3: "Watts-Strogatz"}[gerador]

                    for n in sizes:
                        print(f"\nMedindo para grafo com {n} vértices ({gerador_name})...")
                        if gerador == 1:
                            nx_graph = nx.erdos_renyi_graph(n, p=0.2)
                        elif gerador == 2:
                            nx_graph = nx.barabasi_albert_graph(n, m=3)
                        elif gerador == 3:
                            nx_graph = nx.watts_strogatz_graph(n, k=4, p=0.25)
                        grafo = nx_to_custom_graph(nx_graph)

                        times = []
                        for i in range(repetitions):
                            start_time = time.perf_counter()
                            if algorithm == 1:
                                solve_approximation(grafo)
                            elif algorithm == 2:
                                solver = ExactSolver(grafo)
                                solver.solve()
                            elif algorithm == 3:
                                solve_tabu_search(grafo)
                            end_time = time.perf_counter()
                            elapsed = end_time - start_time
                            times.append(elapsed)

                            # registra cada execução individual no resultado

                        avg_time = sum(times) / repetitions
                        results.append([gerador_name, algo_name, n, avg_time])
                        print(f"{algo_name} | n={n} | tempo médio = {avg_time:.5f}s")

                    # salva CSV com colunas: Gerador, Algoritmo, Vertices, Repeticao, Tempo (s)
                    filename = f"experiments/resultados_{gerador_name.replace(' ', '_').lower()}_{algo_name.lower()}.csv"
                    with open(filename, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(["Gerador", "Algoritmo", "Vertices", "Tempo Médio (s)"])
                        writer.writerows(results)

                    print(f"\nExperimentos concluídos. Resultados salvos em '{filename}'.")