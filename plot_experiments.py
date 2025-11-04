import pandas as pd
import matplotlib.pyplot as plt

def plot_experiments(filename: str = "experiments/results.csv", algoritmo: int = None, gerador: int = None):
    """
    Plota os resultados dos experimentos salvos em 'experiments/results.csv'.
    """
    df = pd.read_csv(filename)

    for solver in df["Algoritmo"].unique():
        subset = df[df["Algoritmo"] == solver]
        plt.plot(subset["Vertices"], subset["Tempo Médio (s)"], marker='o', label=solver)

    if algoritmo == 2:  # Exato
        plt.yscale("log")

    plt.title(f"Complexidade Temporal - Cobertura Mínima de Vértices - {"Aproximado" if algoritmo == 1 else "Exato" if algoritmo == 2 else "Busca Tabu"} - {"Erdos-Renyi" if gerador == 1 else "Barabasi-Albert" if gerador == 2 else "Watts-Strogatz"}")
    plt.xlabel("Número de vértices (n)")
    plt.ylabel("Tempo médio de execução (s)")
    plt.legend()
    plt.grid(True)
    plt.savefig("experiments/resultados.png", dpi=300)
    plt.show()
