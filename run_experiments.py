import time
import csv
import networkx as nx
from solvers.approximation import solve_approximation
from solvers.backtracking import BacktrackingSolver
from solvers.dinamic_memo import DinamicMemoSolver
from solvers.iddfs import IDDFSSolver
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

def gerar_instancias(gerador_func, sizes, repetitions):
    instancias = {}

    # Gera matriz de instancias: para cada tamanho, uma lista de grafos
    for n in sizes:
        instancias[n] = []
        for _ in range(repetitions):
            while True:
                nx_g = gerador_func(n)
                # Garante que o grafo tenha pelo menos uma aresta
                if nx_g.number_of_edges() > 0:
                    instancias[n].append(nx_to_custom_graph(nx_g))
                    break
    return instancias

def run_experiments(start: int, stop: int, step: int, algorithm: int, repetitions: int = 40, gerador: int = 1):
    """
    Executa experimentos de desempenho para diferentes algoritmos e geradores de grafos.

    Args:
        start (int): Tamanho inicial do grafo (número de vértices).
        stop (int): Tamanho final do grafo (número de vértices).
        step (int): Passo para aumentar o tamanho do grafo.
        algorithm (int): Identificador do algoritmo a ser utilizado.
        repetitions (int, optional): Número de repetições para cada experimento. Padrão é 40.
        gerador (int, optional): Identificador do gerador de grafos a ser utilizado. Padrão é 1.
    """
    results = []
    sizes = list(range(start, stop + 1, step))

    geradores = {
        1: ("Erdos-Renyi", lambda n: nx.erdos_renyi_graph(n, p=0.2)),
        2: ("Barabasi-Albert", lambda n: nx.barabasi_albert_graph(n, m=2)),
        3: ("Watts-Strogatz", lambda n: nx.watts_strogatz_graph(n, k=4, p=0.25)),
    }

    algoritmos = {
        1: ("Aproximado", lambda g: solve_approximation(g)),
        2: ("Dinamico", lambda g: DinamicMemoSolver(g).solve()),
        3: ("Backtracking", lambda g: BacktrackingSolver(g).solve()),
        4: ("IDDFS", lambda g: IDDFSSolver(g).solve()),
        5: ("Busca_Tabu", lambda g: solve_tabu_search(g)),
    }

    gerador_name, gerador_func = geradores[gerador]

    # Se for executar todos, exclui o Dinâmico (já que ele será executado separadamente)
    if algorithm == 6:
        algoritmos_escolhidos = [v for k, v in algoritmos.items() if k != 2 and k != 5]
    else:
        algoritmos_escolhidos = [algoritmos[algorithm]]

    # Gera todas as instâncias antes dos experimentos
    print("Gerando instâncias aleatórias compartilhadas...")
    instancias = gerar_instancias(gerador_func, sizes, repetitions)

    # Executa o Dinâmico uma única vez (para calculo de tempo e solução ótima, que será usada para qualidade)
    if algorithm != 2:  # Se for apenas o Dinâmico, não precisa rodar duas vezes
        print("Calculando soluções ótimas com algoritmo Dinâmico...")
        solucoes_otimas = {}
        tempos_dinamico = {}
        for n in sizes:
            solucoes_otimas[n] = []
            tempos_dinamico[n] = []
            for grafo in instancias[n]:
                start_time = time.perf_counter()
                solucao_otima = DinamicMemoSolver(grafo).solve()
                end_time = time.perf_counter()

                tempos_dinamico[n].append(end_time - start_time)
                solucoes_otimas[n].append(len(solucao_otima))

            avg_time_dyn = sum(tempos_dinamico[n]) / repetitions
            avg_quality_dyn = 1.0  # Sempre 1, já que é ótimo

            if algorithm == 6:  # Só salvar se for o modo todos
                results.append([gerador_name, "Dinamico", n, avg_time_dyn, avg_quality_dyn])
            print(f"Dinamico | n={n} | tempo médio={avg_time_dyn:.4f}s")

    # Salva resultados do Dinâmico, para evitar reexecução
    if algorithm == 6:
        filename_dyn = f"experiments/resultados_{gerador_name.replace(' ', '_').lower()}_dinamico.csv"
        with open(filename_dyn, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Gerador", "Algoritmo", "Vertices", "Tempo Médio (s)", "Qualidade Média"])
            filtered_results = [row for row in results if row[1] == "Dinamico"]
            writer.writerows(filtered_results)

        print(f"Resultados do Dinâmico salvos em '{filename_dyn}'.")

    # Experimentos para os outros algoritmos
    for algo_name, algo_func in algoritmos_escolhidos:
        print(f"\nExecutando {algo_name}...")
        for n in sizes:
            tempos, qualidades = [], []
            for i, grafo in enumerate(instancias[n]):  # mesmas instâncias para todos os algoritmos
                start_time = time.perf_counter()
                solucao_alg = algo_func(grafo)
                end_time = time.perf_counter()

                tempos.append(end_time - start_time)
                tamanho_solucao_otima = solucoes_otimas[n][i]
                qualidades.append(len(solucao_alg) / tamanho_solucao_otima)

            avg_time = sum(tempos) / repetitions
            avg_quality = sum(qualidades) / repetitions
            results.append([gerador_name, algo_name, n, avg_time, avg_quality])
            print(f"{algo_name} | n={n} | tempo médio = {avg_time:.5f}s | qualidade média = {avg_quality:.5f}")

        # salva CSV com colunas: Gerador, Algoritmo, Vertices, Repeticao, Tempo (s)
        filename = f"experiments/resultados_{gerador_name.replace(' ', '_').lower()}_{algo_name.lower()}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Gerador", "Algoritmo", "Vertices", "Tempo Médio (s)", "Qualidade Média"])
            filtered_results = [row for row in results if row[1] == algo_name]
            writer.writerows(filtered_results)

        print(f"\nExperimentos do {algo_name} concluídos. Resultados salvos em '{filename}'.")

