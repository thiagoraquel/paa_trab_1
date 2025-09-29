import pandas as pd
import matplotlib.pyplot as plt

def plot_experiments(filename: str = "experiments/results.csv"):
    """
    Plota os resultados dos experimentos salvos em 'experiments/results.csv'.
    """
    df = pd.read_csv(filename)

    for solver in df["Algoritmo"].unique():
        subset = df[df["Algoritmo"] == solver]
        plt.plot(subset["Vertices"], subset["Tempo Médio (s)"], marker='o', label=solver)

    plt.title("Complexidade Temporal - Cobertura Mínima de Vértices")
    plt.xlabel("Número de vértices (n)")
    plt.ylabel("Tempo médio de execução (s)")
    plt.legend()
    plt.grid(True)
    plt.savefig("experiments/resultados.png", dpi=300)
    plt.show()
