import random as rd
import math
import time
import matplotlib.pyplot as plt
from multiprocessing import Pool

# Cada indivíduo é uma instância de Rota
class Rota:
    def __init__(self, rota, custo):
        self.rota = rota
        self.custo = custo
        
# Função para ler arquivos TSP
def ler_tsp(path):
    cidades = [] # Lista de tuplas com as coordenadas da cidade
    tipo = 'EUC_2D'
    lendo_coordenada = False
    with open(path, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha.startswith("EDGE_WEIGHT_TYPE"):
                tipo = linha.split(":")[1].strip()
            elif linha == "NODE_COORD_SECTION":
                lendo_coordenada = True
                continue
            elif linha == "EOF":
                break
            elif lendo_coordenada:
                partes = linha.split()
                if len(partes) >= 3:
                    try:
                        x = float(partes[1])
                        y = float(partes[2])
                        cidades.append((x,y))
                    except ValueError:
                        pass
    return cidades, tipo

# Conversão para tipos GEO
def conversao_angulos_para_radianos(angulo_graus):
    return math.pi * angulo_graus / 180.0

def distancia_geometrica(latitude1, longitude1, latitude2, longitude2):
    raio_terra = 6371.0
    # Converte coordenadas para radianos
    latitude1, longitude1, latitude2, longitude2 = map(conversao_angulos_para_radianos, [latitude1, longitude1, latitude2, longitude2])
    distancia_latitude = latitude2 - latitude1
    distancia_longitude = longitude2 - longitude1
    # === Fórmula de Haversine ===
    a = math.sin(distancia_latitude/2)**2 + math.cos(latitude1) * math.cos(latitude2) * math.sin(distancia_longitude/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return round(raio_terra * c)

# Matriz de distância
def gerar_matriz_distancias(cidades, tipo):
    tamanho = len(cidades)
    matriz = [[0.0] * tamanho for _ in range(tamanho)]
    for i in range(tamanho):
        for j in range(i + 1, tamanho):
            xi, yi = cidades[i]
            xj, yj = cidades[j]
            if tipo == "GEO":
                distancia = distancia_geometrica(xi, yi, xj, yj)
            elif tipo == "EUC_2D":
                distancia = round(math.hypot(xj - xi, yj - yi))
            else:
                raise ValueError(f"Tipo de distância não suportado: {tipo}")
            matriz[i][j] = distancia
            matriz[j][i] = distancia
    return matriz

def gera_rota_unica(tamanho):
    return rd.sample(range(tamanho), tamanho)

def calcula_distancia(rota, distancia):
    custo = 0
    for i in range(len(rota) - 1):
        custo += distancia[rota[i]][rota[i+1]]
    custo += distancia[rota[-1]][rota[0]]
    return custo

# Gerar uma solução inicial razoável, ajudando o o AG a convergir mais rápido
def vizinho_mais_proximo(numero_cidades, matriz):
    rota = [0] # Começa na primeira cidade
    visitadas = {0}
    while len(rota) < numero_cidades:
        atual = rota[-1]
        # Busca pela cidade mais próxima
        menor_distancia = float('inf')
        proxima = None
        for j in range(numero_cidades):
            if j not in visitadas and matriz[atual][j] < menor_distancia:
                menor_distancia = matriz[atual][j]
                proxima = j
        rota.append(proxima)
        visitadas.add(proxima)
    return rota

# Seleciona individuos para cruzamento e mutacao com base em seu custo
def selecao_torneio(populacao, tamanho_torneio=7):
    torneio = rd.sample(populacao, tamanho_torneio)
    # encontra o elemento de menor custo
    return min(torneio, key=lambda r: r.custo)

# Combina duas rotas e gera uma nova, preservando caracteristicas de ambos, mantendo a validação da rota
def crossover_ordenado(pai1, pai2):
    tamanho = len(pai1)
    inicio, fim = sorted(rd.sample(range(tamanho), 2))
    filho = [None] * tamanho
    filho[inicio:fim] = pai1[inicio:fim]
    posicao = fim
    for cidade in pai2:
        if cidade not in filho:
            while filho[posicao % tamanho] is not None:
                posicao += 1
            filho[posicao % tamanho] = cidade
    assert all(c in filho for c in range(tamanho)), "Crossover gerou rota inválida"
    return filho

# Variações aleatórias para promover diversidade
def mutacao(rota, probabilidade_mutacao):
    rota = rota[:]
    if rd.random() < probabilidade_mutacao:
        if rd.random() < 0.5: # Troca
            i, j = rd.sample(range(len(rota)), 2)
            rota[i], rota[j] = rota[j], rota[i]
        else: # Inversão
            i, j = sorted(rd.sample(range(len(rota)), 2))
            rota[i:j+1] = reversed(rota[i:j+1])
    return rota
        
# Melhorar uma rota existente geradas pelo crossover e mutacao, otimizando a ordem para reduzir o custo total
def heuristica_dois_opt(rota, matriz):
    melhor_rota = rota[:]
    melhor_custo = calcula_distancia(rota, matriz)
    maximo_iteracoes = 50
    iteracao = 0
    while iteracao < maximo_iteracoes:
        melhorou = False
        for i in range(1, len(rota) - 2):
            for j in range(i + 1, len(rota)):
                if j - i == 1: continue
                nova_rota = melhor_rota[:i] + melhor_rota[i:j][::-1] + melhor_rota[j:]
                novo_custo = calcula_distancia(nova_rota, matriz)
                if novo_custo < melhor_custo:
                    melhor_rota = nova_rota
                    melhor_custo = novo_custo
                    melhorou = True
        if not melhorou:
            break
        iteracao += 1
    return melhor_rota, melhor_custo

# Algoritmo Genético
def algoritmo_genetico(args):
    matriz, numero_cidades, nome_arquivo = args
    quantidade_de_rotas = max(100, numero_cidades)
    numero_geracoes = max(5000, numero_cidades * 20)
    elitismo = 2
    maximo_sem_melhora = max(300, numero_cidades * 2)
    
    populacao = []
    for _ in range(quantidade_de_rotas - 1):
        rota = gera_rota_unica(numero_cidades)
        populacao.append(Rota(rota, calcula_distancia(rota, matriz)))
    rota_vizinho_proximo = vizinho_mais_proximo(numero_cidades, matriz)
    populacao.append(Rota(rota_vizinho_proximo, calcula_distancia(rota_vizinho_proximo, matriz)))
    
    melhor_custo = float('inf')
    sem_melhora = 0
    historico_custos = []
    inicio = time.time()
    
    for geracao in range(numero_geracoes):
        nova_populacao = []
        populacao.sort(key=lambda r: r.custo)
        nova_populacao.extend(populacao[:elitismo])
        
        probabilidade_mutacao = 0.2 * (1 - geracao / numero_geracoes) + 0.05
        
        while len(nova_populacao) < quantidade_de_rotas:
            pai1 = selecao_torneio(populacao)
            pai2 = selecao_torneio(populacao)
            
            filho1 = crossover_ordenado(pai1.rota, pai2.rota)
            filho2 = crossover_ordenado(pai2.rota, pai1.rota)
            
            if rd.random() < probabilidade_mutacao:
                filho1 = mutacao(filho1, probabilidade_mutacao)
            
            if rd.random() < probabilidade_mutacao:
                filho2 = mutacao(filho2, probabilidade_mutacao)
                
            nova_populacao.append(Rota(filho1, calcula_distancia(filho1, matriz)))
            if len(nova_populacao) < quantidade_de_rotas:
                nova_populacao.append(Rota(filho2, calcula_distancia(filho2, matriz)))
                
        if geracao % 50 == 0:
            melhor_atual = min(populacao, key=lambda r: r.custo)
            rota_opt, custo_opt = heuristica_dois_opt(melhor_atual.rota, matriz)
            nova_populacao.append(Rota(rota_opt, custo_opt))
            
        populacao = nova_populacao
        atual_melhor = min(populacao, key=lambda r: r.custo).custo
        historico_custos.append(atual_melhor)
        
        if atual_melhor < melhor_custo:
            melhor_custo = atual_melhor
            sem_melhora = 0
        else:
            sem_melhora += 1
        if sem_melhora >= maximo_sem_melhora:
            break
        
    melhor_rota = min(populacao, key=lambda r: r.custo)
    rota_opt, custo_opt = heuristica_dois_opt(melhor_rota.rota, matriz)
    fim = time.time()
    tempo_execucao = fim - inicio
        
    print(f"✅ Melhor custo para {nome_arquivo}: {custo_opt}")
        
    return {
        "arquivo": nome_arquivo,
        "caminho": rota_opt,
        "distancia": custo_opt,
        "tempo": tempo_execucao,
        "historico": historico_custos
    }
    
def main():
    rd.seed(42)
    arquivos = ["burma14.tsp", "ch150.tsp", "lin318.tsp"]
    tarefas = []
    cidades_por_arquivos = {}
    for caminho in arquivos:
        try:
            cidades, tipo = ler_tsp(caminho)
            matriz = gerar_matriz_distancias(cidades, tipo)
            tarefas.append((matriz, len(cidades), caminho))
            cidades_por_arquivos[caminho] = (cidades, tipo)
        except Exception as e:
            print(f"Erro ao processar {caminho}: {e}")
    
    with Pool() as pool:
        resultados = pool.map(algoritmo_genetico, tarefas)
        
    with open("melhores_custos.txt", "w") as f:
        for res in resultados:
            f.write(f"{res['arquivo']}: {res['distancia']}\n")
    
    for res in resultados:
        plt.figure()
        plt.plot(res['historico'])
        plt.xlabel("Geração")
        plt.ylabel("Distância")
        plt.title(f"Evolução da distância - {res['arquivo']}")
        plt.grid(True)
        plt.savefig(f"grafico_{res['arquivo'].split('.')[0]}.png")
        plt.close()
        
    plt.figure()
    nomes = [res['arquivo'] for res in resultados]
    tempos = [res['tempo'] for res in resultados]
    plt.bar(nomes, tempos, color='orange')
    plt.ylabel("Tempo (s)")
    plt.title("Tempo de execução por instância")
    plt.grid(axis='y')
    plt.savefig("grafico_tempos_execucao.png")
    plt.close()
            
if __name__ == "__main__":
    main()