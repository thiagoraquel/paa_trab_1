import pandas as pd
import matplotlib.pyplot as plt

def plot_experiments(filename: str = "experiments/results.csv", algoritmo: int = None, gerador: int = None):
    """
    Plota os resultados dos experimentos salvos em 'experiments/results.csv'.
    """
    df = pd.read_csv(filename)

    # Dicionários para mapear os códigos para nomes legíveis
    nomes_algoritmos = {
        1: "Aproximado",
        2: "Exato",
        3: "Backtracking",
        4: "IDDFS",
        5: "Busca Tabu",
    }

    nomes_geradores = {
        1: "Erdos-Renyi",
        2: "Barabasi-Albert",
        3: "Watts-Strogatz"
    }

    # Obtém os nomes com base nos códigos, usando um valor padrão se não encontrar
    nome_algoritmo = nomes_algoritmos.get(algoritmo, f"Algoritmo {algoritmo}")
    nome_gerador = nomes_geradores.get(gerador, f"Gerador {gerador}")

    plt.figure(figsize=(10, 6)) # Opcional: define um tamanho maior para o gráfico

    for solver in df["Algoritmo"].unique():
        subset = df[df["Algoritmo"] == solver]
        # Ordena por número de vértices para garantir que a linha seja plotada corretamente
        subset = subset.sort_values(by="Vertices")
        plt.plot(subset["Vertices"], subset["Tempo Médio (s)"], marker='o', label=solver)

    # Se o algoritmo for Exato (código 2), usa escala logarítmica
    if algoritmo in [2, 3, 4]:  # algoritmos exatos
        plt.yscale("log")
        plt.ylabel("Tempo médio de execução (s) - Escala Log") # Atualiza o label para indicar log
    else:
        plt.ylabel("Tempo médio de execução (s)")

    # Título usando os nomes obtidos dos dicionários.
    # Uso de aspas simples na f-string externa para evitar conflitos se houver aspas internas (embora não haja agora).
    plt.title(f'Complexidade Temporal - CMV - {nome_algoritmo} - {nome_gerador}')
    plt.xlabel("Número de vértices (n)")
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.5) # Grid melhorado para escala log
    
    plt.tight_layout() # Ajusta o layout para evitar cortes
    plt.savefig("experiments/resultados.png", dpi=300)
    plt.show()