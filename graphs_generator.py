import networkx as nx
import os
from typing import Optional

def salvar_grafo_em_txt(g: nx.Graph, nome_modelo: str, parametros: dict, pasta_destino: str = 'grafos_de_teste'):
    """
    Salva um grafo do networkx em um arquivo .txt no formato SNAP (u v por linha).

    Args:
        g (nx.Graph): O objeto de grafo a ser salvo.
        nome_modelo (str): O nome do modelo (ex: 'erdos_renyi').
        parametros (dict): Dicionário com os parâmetros usados para gerar o grafo.
        pasta_destino (str): O nome da pasta onde os arquivos serão salvos.
    """
    # Cria a pasta de destino se ela não existir
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f"Pasta '{pasta_destino}' criada.")

    # Cria um nome de arquivo descritivo
    params_str = '_'.join([f'{k}{v}' for k, v in parametros.items()])
    filename = f"{nome_modelo}_{params_str}.txt"
    filepath = os.path.join(pasta_destino, filename)

    print(f"Gerando arquivo: {filepath}...")

    with open(filepath, 'w') as f:
        # Adiciona um cabeçalho informativo (opcional, mas útil)
        f.write(f"# Modelo: {nome_modelo.replace('_', ' ').title()}\n")
        f.write(f"# Parâmetros: {parametros}\n")
        f.write(f"# Vértices: {g.number_of_nodes()}\n")
        f.write(f"# Arestas: {g.number_of_edges()}\n")
        f.write("# FromNodeId\tToNodeId\n")
        
        # Escreve as arestas no formato u v
        for u, v in g.edges():
            f.write(f"{u}\t{v}\n")
            
    print(" -> Concluído.")

# --- Bloco Principal para Gerar os Arquivos ---
if __name__ == "__main__":
    tamanhos_dos_grafos = [37, 38, 39]
    pasta = 'grafos_de_teste'
    
    print("="*60)
    print(f"INICIANDO A GERAÇÃO DOS ARQUIVOS DE GRAFO NA PASTA '{pasta}'")
    print("="*60)

    # --- 1. Modelo Erdos-Renyi ---
    # Usaremos uma probabilidade p=0.2 para gerar grafos com conectividade razoável
    for n in tamanhos_dos_grafos:
        p = 0.2
        g = nx.erdos_renyi_graph(n=n, p=p, seed=42)
        salvar_grafo_em_txt(g, 'erdos_renyi', {'n': n, 'p': p}, pasta)

    # --- 2. Modelo Barabasi-Albert ---
    # m=3: cada novo nó se conecta a 3 nós existentes
    for n in tamanhos_dos_grafos:
        m = 3
        g = nx.barabasi_albert_graph(n=n, m=m, seed=42)
        salvar_grafo_em_txt(g, 'barabasi_albert', {'n': n, 'm': m}, pasta)
        
    # --- 3. Modelo Watts-Strogatz ---
    # k=4: cada nó se conecta aos 4 vizinhos mais próximos inicialmente
    # p=0.25: 25% de chance de "rewiring" de cada aresta
    for n in tamanhos_dos_grafos:
        k = 4
        p = 0.25
        g = nx.watts_strogatz_graph(n=n, k=k, p=p, seed=42)
        salvar_grafo_em_txt(g, 'watts_strogatz', {'n': n, 'k': k, 'p': p}, pasta)
        
    print("\nTodos os arquivos de grafo foram gerados com sucesso!")