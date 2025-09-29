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

def run_experiments(start: int, stop: int, step: int, algorithm: int, repetitions: int = 40):
    results = []
    sizes = list(range(start, stop + 1, step))
    algo_name = {1: "Aproximado", 2: "Exato", 3: "Busca_Tabu"}[algorithm]

    for n in sizes:
        print(f"\nMedindo para grafo com {n} vértices...")
        nx_graph = nx.barabasi_albert_graph(n, m=3)
        grafo = nx_to_custom_graph(nx_graph)

        times = []
        for _ in range(repetitions):
            start_time = time.perf_counter()
            if algorithm == 1:
                solve_approximation(grafo)
            elif algorithm == 2 and n < 41:
                solver = ExactSolver(grafo)
                solver.solve()
            elif algorithm == 3:
                solve_tabu_search(grafo)
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        avg_time = sum(times) / repetitions
        results.append([algo_name, n, avg_time])
        print(f"{algo_name} | n={n} | tempo médio = {avg_time:.5f}s")

    filename = f"experiments/resultados_{algo_name.lower()}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Algoritmo", "Vertices", "Tempo Médio (s)"])
        writer.writerows(results)

    print(f"\nExperimentos concluídos. Resultados salvos em '{filename}'.")
