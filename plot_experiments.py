from glob import glob
import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_experiments(filename: str, algoritmo: int, gerador: int, unified: bool = False):
    """
    Plota os resultados dos experimentos.
    
    Args:
        filename (str): Caminho do CSV individual. Ignorado se unified=True.
        algoritmo (int): Código do algoritmo (1–5).
        gerador (int): Código do gerador (1–3).
        unified (bool): Se True, plota todos os algoritmos para o mesmo gerador.
    """
    # Dicionários para mapear os códigos para nomes legíveis
    nomes_algoritmos = {
        1: "Aproximado",
        2: "Dinamico",
        3: "Backtracking",
        4: "IDDFS",
        5: "Busca Tabu",
    }

    nomes_geradores = {
        1: "Erdos-Renyi",
        2: "Barabasi-Albert",
        3: "Watts-Strogatz"
    }

    nome_gerador = nomes_geradores.get(gerador, f"Gerador {gerador}")

    plt.figure(figsize=(10, 6)) # Opcional: define um tamanho maior para o gráfico
    
    # --- Modo Unificado ---
    if unified:
        # Busca todos os CSVs referentes ao mesmo gerador
        pattern = f"experiments/resultados_{nome_gerador.replace(' ', '_').lower()}_*.csv"
        arquivos = glob(pattern)

        if not arquivos:
            print(f"Nenhum arquivo encontrado para o gerador '{nome_gerador}'.")
            return

        for arquivo in arquivos:
            df = pd.read_csv(arquivo)

            # Extrai nome do algoritmo a partir do nome do arquivo
            base = os.path.basename(arquivo)
            nome_algoritmo = base.replace(f"resultados_{nome_gerador.replace(' ', '_').lower()}_", "").replace(".csv", "").replace("_", " ").title()

            df = df.sort_values(by="Vertices")
            plt.plot(df["Vertices"], df["Tempo Médio (s)"], marker='o', label=nome_algoritmo)

        plt.yscale("log")
        plt.ylabel("Tempo médio de execução (s) [Escala Log]")
        plt.title(f"Comparação de Algoritmos - CMV - {nome_gerador}")

        nome_saida = f"experiments/plot_comparativo_{nome_gerador.replace(' ', '_').lower()}.png"

    # --- Modo Individual ---
    else:
        if filename is None or algoritmo is None:
            print("Erro: filename e algoritmo devem ser especificados no modo individual.")
            return

        df = pd.read_csv(filename)

        # Obtém os nomes com base nos códigos, usando um valor padrão se não encontrar
        nome_algoritmo = nomes_algoritmos.get(algoritmo, f"Algoritmo {algoritmo}")

        for solver in df["Algoritmo"].unique():
            subset = df[df["Algoritmo"] == solver].sort_values(by="Vertices")
            plt.plot(subset["Vertices"], subset["Tempo Médio (s)"], marker='o', label=solver)

        if algoritmo in [2, 3, 4]:
            plt.yscale("log")
            plt.ylabel("Tempo médio de execução (s) - Escala Log")
        else:
            plt.ylabel("Tempo médio de execução (s)")

        plt.title(f"Complexidade Temporal - CMV - {nome_algoritmo} - {nome_gerador}")
        nome_saida = f"experiments/plot_{nome_gerador.replace(' ', '_').lower()}_{nome_algoritmo.replace(' ', '_').lower()}.png"

    plt.xlabel("Número de vértices (n)")
    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.5) # Grid melhorado para escala log
    plt.tight_layout() # Ajusta o layout para evitar cortes
    plt.savefig(nome_saida, dpi=300)
    plt.show()

    print(f"Gráfico salvo em '{nome_saida}'")
