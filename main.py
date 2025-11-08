# main.py
import glob
import sys
from graph import Graph
from solvers.approximation import solve_approximation
from solvers.dinamic_memo import DinamicMemoSolver
from solvers.tabu_search import solve_tabu_search
from solvers.branch_and_bound import BranchAndBoundSolver
from solvers.backtracking import BacktrackingSolver
from solvers.iddfs import IDDFSSolver
from visualization import visualizar_grafo_com_cobertura
from run_experiments import run_experiments
from plot_experiments import plot_experiments

def selecionar_grafo() -> str:
    """
    Encontra arquivos de grafo na pasta 'grafos_de_teste', exibe um menu
    para o usuário e retorna o caminho do arquivo escolhido.
    """
    caminho_pasta = 'grafos_de_teste/*.txt'
    grafos_disponiveis = glob.glob(caminho_pasta)

    if not grafos_disponiveis:
        print(f"Erro: Nenhum arquivo de grafo (.txt) encontrado na pasta '{caminho_pasta}'.")
        print("Por favor, adicione arquivos de instância e tente novamente.")
        sys.exit()

    print("=" * 60)
    print("Por favor, escolha um grafo para testar:")
    for i, caminho in enumerate(grafos_disponiveis, start=1):
        print(f"  [{i}] - {caminho}")
    print("=" * 60)

    while True:
        try:
            escolha_str = input(f"Digite o número do grafo (1-{len(grafos_disponiveis)}): ")
            escolha_int = int(escolha_str)
            if 1 <= escolha_int <= len(grafos_disponiveis):
                return grafos_disponiveis[escolha_int - 1]
            else:
                print("Opção inválida. Por favor, digite um número da lista.")
        except ValueError:
            print("Entrada inválida. Por favor, digite apenas o número.")
        except (KeyboardInterrupt, EOFError):
            print("\nSeleção cancelada. Encerrando o programa.")
            sys.exit()

def selecionar_algoritmo() -> int:
    """
    Exibe um menu para o usuário escolher qual algoritmo executar.
    Retorna o número da opção escolhida.
    """
    print("\n" + "=" * 60)
    print("Qual algoritmo você gostaria de executar?")
    print("  [1] - Algoritmo de Aproximação (Fator 2)")
    print("  [2] - Algoritmo Exato Dinâmico com Memoização (Ótimo)")
    print("  [3] - Algoritmo Exato Backtracking com Poda Upperbound (Ótimo)")
    print("  [4] - Algoritmo Exato Iterativo de Aprofundamento (Ótimo)")
    print("  [5] - Busca Tabu (Meta-heurística)")
    print("  [6] - Executar TODOS os algoritmos (apenas no modo individual)")
    print("=" * 60)
    
    while True:
        try:
            escolha_str = input("Digite o número do algoritmo (1-6): ")
            escolha_int = int(escolha_str)
            if 1 <= escolha_int <= 6:
                return escolha_int
            else:
                print("Opção inválida. Por favor, digite um número de 1 a 6.")
        except ValueError:
            print("Entrada inválida. Por favor, digite apenas o número.")
        except (KeyboardInterrupt, EOFError):
            print("\nSeleção cancelada. Encerrando o programa.")
            sys.exit()

def selecionar_gerador() -> int:
    """
    Exibe um menu para o usuário escolher qual gerador de grafos utilizar.
    Retorna o número da opção escolhida.
    """
    print("\n" + "=" * 60)
    print("Qual gerador de grafos você gostaria de usar para os experimentos?")
    print("  [1] - Erdos-Renyi")
    print("  [2] - Barabasi-Albert")
    print("  [3] - Watts-Strogatz")
    print("=" * 60)
    
    while True:
        try:
            escolha_str = input("Digite o número do gerador (1-3): ")
            escolha_int = int(escolha_str)
            if 1 <= escolha_int <= 3:
                return escolha_int
            else:
                print("Opção inválida. Por favor, digite um número de 1 a 3.")
        except ValueError:
            print("Entrada inválida. Por favor, digite apenas o número.")
        except (KeyboardInterrupt, EOFError):
            print("\nSeleção cancelada. Encerrando o programa.")
            sys.exit()


def main():
    """
    Ponto de entrada principal para testar os algoritmos de cobertura de vértices.
    """
    print("="*60)
    print("Escolha o modo de execução:")
    print("  [1] - Testar grafo individual (modo original)")
    print("  [2] - Executar experimentos automáticos (modo complexidade)")
    print("="*60)

    while True:
        try:
            modo = int(input("Digite 1 ou 2: "))
            if modo == 1:
                # Modo original
                caminho_arquivo = selecionar_grafo()
                print("\n" + "=" * 60)
                print(f"Iniciando análise para o grafo: {caminho_arquivo}")
                print("=" * 60)

                grafo = Graph.from_generated_file(caminho_arquivo)
    
                if grafo:
                    # Pede ao usuário para escolher o algoritmo
                    algoritmo_escolhido = selecionar_algoritmo()

                    # Executa o(s) algoritmo(s) com base na escolha
                    
                    if algoritmo_escolhido in [1, 6]:
                        print("\n--- Algoritmo de Aproximação (Fator 2) ---")
                        approx_cover = solve_approximation(grafo)
                        print(f"Vértices encontrados: {sorted(list(approx_cover))}")
                        print(f"Tamanho da cobertura: {len(approx_cover)}")
                        visualizar_grafo_com_cobertura(grafo, approx_cover, "Cobertura - Algoritmo de Aproximação")

                    if algoritmo_escolhido in [2, 6]:
                        if grafo.num_vertices < 41:
                            print("\n--- Algoritmo Dinâmico com Memoização ---\n")
                            dinamic_memo = DinamicMemoSolver(grafo)
                            optimal_cover_nodes = dinamic_memo.solve()
                            print(f"Vértices encontrados: {sorted(list(optimal_cover_nodes))}")
                            print(f"Tamanho da cobertura ótima: {len(optimal_cover_nodes)}")
                            visualizar_grafo_com_cobertura(grafo, optimal_cover_nodes, "Cobertura - Algoritmo Exato (Ótimo)")  
                        else:
                            print("\n--- Algoritmo Exato (PULADO) ---")
                            print(f"O grafo com {grafo.num_vertices} vértices é muito grande para o algoritmo exato.")

                    if algoritmo_escolhido in [3, 6]:
                        if grafo.num_vertices < 41:
                            print("\n--algoritmo backtracking")
                            backtracking = BacktrackingSolver(grafo)
                            optimal_cover_nodes = backtracking.solve()
                            print(f"Vértices encontrados: {sorted(list(optimal_cover_nodes))}")
                            print(f"Tamanho da cobertura ótima: {len(optimal_cover_nodes)}")
                        else:
                            print("\n--- Algoritmo Exato (PULADO) ---")
                            print(f"O grafo com {grafo.num_vertices} vértices é muito grande para o algoritmo exato.")

                    if algoritmo_escolhido in [4, 6]:
                        if grafo.num_vertices < 41:    
                            print("\n--algoritmo depth first")
                            iddfs = IDDFSSolver(grafo)
                            optimal_cover_nodes = iddfs.solve()
                            print(f"Vértices encontrados: {sorted(list(optimal_cover_nodes))}")
                            print(f"Tamanho da cobertura ótima: {len(optimal_cover_nodes)}")
                        else:
                            print("\n--- Algoritmo Exato (PULADO) ---")
                            print(f"O grafo com {grafo.num_vertices} vértices é muito grande para o algoritmo exato.")

                    if algoritmo_escolhido in [5, 6]:
                        # ATENÇÃO: Pode ser muito lento para grafos com mais de 40 vértices.
                        if grafo.num_vertices < 41:
                            print("\n--- Busca Tabu ---")
                            ts_cover, ts_cost = solve_tabu_search(grafo, max_iters=1000, rng_seed=42)
                            print(f"Vértices encontrados: {sorted(ts_cover)}")
                            print(f"Tamanho da cobertura: {len(ts_cover)}")
                            print(f"Custo final da solução (tamanho + penalidades): {ts_cost}")
                            visualizar_grafo_com_cobertura(grafo, set(ts_cover), "Cobertura - Busca Tabu")
                        else:
                            print("\n--- Algoritmo Exato (PULADO) ---")
                            print(f"O grafo com {grafo.num_vertices} vértices é muito grande para o algoritmo exato.")
                        
                print("\n" + "=" * 60)
                print("Análise concluída.")
                print("=" * 60)

            elif modo == 2:
                # Modo experimento
                start = int(input("Tamanho inicial do grafo (start): "))
                stop = int(input("Tamanho final do grafo (stop): "))
                step = int(input("Incremento (step): "))

                gerador = selecionar_gerador()

                algorithm = selecionar_algoritmo()
                if algorithm == 6:
                    print("Para experimentos, por favor escolha apenas um algoritmo (1, 2, 3, 4 ou 5).")
                    continue
                repetitions = int(input("Número de repetições por grafo (para cálculo da média): "))
                run_experiments(start, stop, step, algorithm, repetitions, gerador)
                plot_experiments(f"experiments/resultados_{'erdos-renyi' if gerador == 1 else 'barabasi-albert' if gerador == 2 else 'watts-strogatz'}_{ 'aproximado' if algorithm == 1 else 'dinamico' if algorithm == 2 else 'backtracking' if algorithm == 3 else 'iddfs' if algorithm == 4 else 'busca_tabu' }.csv", algoritmo=algorithm, gerador=gerador)
                break

            else:
                print("Opção inválida. Por favor, digite 1 ou 2.")
        
        except ValueError:
            print("Entrada inválida. Por favor, digite apenas o número.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada. Encerrando o programa.")
            sys.exit()

if __name__ == "__main__":
    main()