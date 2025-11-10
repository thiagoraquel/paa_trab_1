-----

# Algoritmos para Cobertura Mínima de Vértices

Implementação de algoritmos para resolver o problema da Cobertura Mínima de Vértices, com uma interface de linha de comando (CLI) para testes e análise de complexidade.

## Algoritmos Implementados

1.  **Aproximação (Fator 2)**: Rápido e eficiente, garante uma solução no máximo duas vezes maior que a ótima.
2.  **Algoritmos Exatos (Ótimo)**: Encontram a solução ótima. Viável apenas para grafos pequenos (\< 40 vértices).

    2.1. **Backtracking com Poda Upperbound**: Busca de backtracking que armazena a melhor solução encontrada até agora e realiza poda caso uma árvore de decisão tenha custo maior que a melhor solução armazenada até o momento.

    2.2. **Recursão com Algoritmo Dinâmico e Memoização**: Explora a árvore recursivamente ao buscar em cada aresta escolhida (u,v), a solução com o vértice u incluso na cobertura mínima ou o vértice v. O algoritmo guarda o resultado dos conjuntos de subproblemas já encontrados antes, aumentando a velocidade quando revisitar esses mesmos casos futuramente. 

    2.3. **Aprofundamento Iterativo**: O algoritmo irá procurar a solução com a iteração de uma busca de profundidade limitada, aumentando o orçamento da busca sempre que uma solução não for retornada. Quando a solução for encontrada, ela necessariamente será ótima, pois todos os outros casos com menor orçamento já foram testados anteriormente.
4.  **Busca Tabu (Meta-heurística)**: Busca local otimizada para encontrar soluções de alta qualidade em tempo razoável.

## Funcionalidades

  * **CLI Interativa**: Guia o usuário na escolha do modo, grafo e algoritmo.
  * **Visualização de Grafos**: Gera uma imagem do grafo com a cobertura de vértices destacada.
  * **Dois Modos de Execução**:
    1.  **Testes Individuais**: Aplica os algoritmos em grafos pré-definidos na pasta `grafos_de_teste/`.
    2.  **Modo de Experimentação**: Analisa o tempo de execução dos algoritmos em grafos de tamanhos variados, gerando gráficos de complexidade.

## Como Executar

### 1\. Pré-requisitos

Certifique-se de ter o Python 3 instalado. Instale as dependências com:

```bash
pip install matplotlib networkx pandas
```

Observação: o pandas é necessário apenas para plotar os gráficos de complexidade, então não é necessário se o modo de experimentação não for ser utilizado.

### 2\. Clonar e Rodar

Clone o repositório e execute o script principal:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
python main.py
```

### 3\. Usando a CLI

Ao executar, o programa perguntará qual modo você deseja usar:

  * **Opção `[1]` - Testes Individuais**:

      * Escolha um dos grafos listados da pasta `grafos_de_teste/`.
      * Escolha um ou todos os algoritmos para executar.
      * O programa imprimirá os resultados e exibirá uma visualização do grafo para cada algoritmo.

  * **Opção `[2]` - Modo de Experimentação**:

      * Defina o tamanho inicial, final e o incremento para a geração de grafos.
      * Escolha um algoritmo para analisar.
      * Defina o número de repetições por tamanho de grafo.
      * Ao final, um gráfico de `Tempo vs. Tamanho do Grafo` será gerado e exibido, com os dados e imagens salvos na pasta `experiments/`.

## Estrutura do Projeto

```
.
├── grafos_de_teste/   # Instâncias de grafos para teste
├── solvers/           # Implementação dos algoritmos
├── experiments/       # Saída dos resultados (.csv) e imagens (.png) dos experimentos
├── main.py            # Script principal com a CLI
├── graph.py           # Definição da classe Graph
└── ...                # Módulos de suporte
```

-----
