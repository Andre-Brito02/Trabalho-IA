import random as rd
import math
import time
import matplotlib.pyplot as plt
from multiprocessing import Pool

# === CLASSE ROTA ===
class Rota:
    def __init__(self, rota, custo):
        self.rota = rota
        self.custo = custo

# === FUNÇÃO PARA LER ARQUIVO TSP ===
def ler_tsp(path):
    cidades = []
    tipo = 'EUC_2D'
    lendo_coord = False
    with open(path, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha.startswith("EDGE_WEIGHT_TYPE"):
                tipo = linha.split(":")[1].strip()
            elif linha == "NODE_COORD_SECTION":
                lendo_coord = True
                continue
            elif linha == "EOF":
                break
            elif lendo_coord:
                partes = linha.split()
                if len(partes) >= 3:
                    try:
                        x = float(partes[1])
                        y = float(partes[2])
                        cidades.append((x, y))
                    except ValueError:
                        pass
    return cidades, tipo

# === CONVERSÃO E DISTÂNCIA ===
def deg2rad(deg):
    return math.pi * deg / 180.0

def geo_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(deg2rad, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return round(R * c)

# === MATRIZ DE DISTÂNCIAS ===
def gerar_matriz_distancias(cidades, tipo):
    tamanho = len(cidades)
    matriz = [[0.0] * tamanho for _ in range(tamanho)]
    for i in range(tamanho):
        for j in range(i + 1, tamanho):
            xi, yi = cidades[i]
            xj, yj = cidades[j]
            if tipo == "GEO":
                dist = geo_distance(xi, yi, xj, yj)
            elif tipo == "EUC_2D":
                dist = round(math.hypot(xj - xi, yj - yi))
            else:
                raise ValueError(f"Tipo de distância não suportado: {tipo}")
            matriz[i][j] = dist
            matriz[j][i] = dist
    return matriz

# === GERA ROTA ALEATÓRIA ===
def geraRotaUnica(tamanho):
    return rd.sample(range(tamanho), tamanho)

def calculaDistancia(rota, distancia):
    custo = 0
    for i in range(len(rota) - 1):
        custo += distancia[rota[i]][rota[i + 1]]
    custo += distancia[rota[-1]][rota[0]]
    return custo

# === SELEÇÃO, CROSSOVER E MUTAÇÃO ===
def selecao_torneio(populacao, matriz, tamanho_torneio=5):
    torneio = rd.sample(populacao, tamanho_torneio)
    return min(torneio, key=lambda r: r.custo)

def crossover_ox(pai1, pai2):
    tamanho = len(pai1)
    inicio, fim = sorted(rd.sample(range(tamanho), 2))
    filho = [None] * tamanho
    filho[inicio:fim] = pai1[inicio:fim]
    pos = fim
    for cidade in pai2:
        if cidade not in filho:
            while filho[pos % tamanho] is not None:
                pos += 1
            filho[pos % tamanho] = cidade
    return filho

def mutacao(rota, prob_mutacao=0.15):
    if rd.random() < prob_mutacao:
        if rd.random() < 0.5:
            i, j = rd.sample(range(len(rota)), 2)
            rota[i], rota[j] = rota[j], rota[i]
        else:
            i, j = sorted(rd.sample(range(len(rota)), 2))
            rota[i:j+1] = reversed(rota[i:j+1])
    return rota

def dois_opt(rota, matriz):
    melhor_rota = rota[:]
    melhor_custo = calculaDistancia(rota, matriz)
    max_iteracoes = 10
    iteracao = 0
    while iteracao < max_iteracoes:
        melhorou = False
        for i in range(1, len(rota) - 2):
            for j in range(i + 1, len(rota)):
                if j - i == 1: continue
                nova_rota = melhor_rota[:i] + melhor_rota[i:j][::-1] + melhor_rota[j:]
                novo_custo = calculaDistancia(nova_rota, matriz)
                if novo_custo < melhor_custo:
                    melhor_rota = nova_rota
                    melhor_custo = novo_custo
                    melhorou = True
        if not melhorou:
            break
        iteracao += 1
    return melhor_rota, melhor_custo

# === ALGORITMO GENÉTICO ===
def algoritmo_genetico(args):
    matriz, num_cidades, arquivo_nome = args
    quantidade_de_rotas = max(50, num_cidades // 2)
    populacao = [Rota(geraRotaUnica(num_cidades), calculaDistancia(geraRotaUnica(num_cidades), matriz)) for _ in range(quantidade_de_rotas)]
    num_geracoes = 5000
    prob_crossover = 0.9
    prob_mutacao = 0.15
    elitismo = 2
    max_sem_melhora = 300

    melhor_custo = float('inf')
    sem_melhora = 0
    historico_custos = []
    inicio = time.time()

    for geracao in range(num_geracoes):
        nova_populacao = []
        populacao.sort(key=lambda r: r.custo)
        nova_populacao.extend(populacao[:elitismo])

        while len(nova_populacao) < quantidade_de_rotas:
            pai1 = selecao_torneio(populacao, matriz)
            pai2 = selecao_torneio(populacao, matriz)
            if rd.random() < prob_crossover:
                filho1 = crossover_ox(pai1.rota, pai2.rota)
                filho2 = crossover_ox(pai2.rota, pai1.rota)
            else:
                filho1 = pai1.rota[:]
                filho2 = pai2.rota[:]
            filho1 = mutacao(filho1, prob_mutacao)
            filho2 = mutacao(filho2, prob_mutacao)
            nova_populacao.append(Rota(filho1, calculaDistancia(filho1, matriz)))
            if len(nova_populacao) < quantidade_de_rotas:
                nova_populacao.append(Rota(filho2, calculaDistancia(filho2, matriz)))

        populacao = nova_populacao
        atual_melhor = min(populacao, key=lambda r: r.custo).custo
        historico_custos.append(atual_melhor)

        if atual_melhor < melhor_custo:
            melhor_custo = atual_melhor
            sem_melhora = 0
        else:
            sem_melhora += 1
        if sem_melhora >= max_sem_melhora:
            break

    melhor_rota = min(populacao, key=lambda r: r.custo)
    rota_opt, custo_opt = dois_opt(melhor_rota.rota, matriz)
    fim = time.time()
    tempo_execucao = fim - inicio

    print(f"✅ Melhor custo para {arquivo_nome}: {custo_opt}")

    return {
        "arquivo": arquivo_nome,
        "caminho": rota_opt,
        "distancia": custo_opt,
        "tempo": tempo_execucao,
        "historico": historico_custos
    }

# === MAIN ===
def main():
    rd.seed(42)
    arquivos = ["burma14.tsp", "ch150.tsp", "lin318.tsp"]
    tarefas = []
    for caminho in arquivos:
        try:
            cidades, tipo = ler_tsp(caminho)
            matriz = gerar_matriz_distancias(cidades, tipo)
            tarefas.append((matriz, len(cidades), caminho))
        except Exception as e:
            print(f"Erro ao processar {caminho}: {e}")

    with Pool() as pool:
        resultados = pool.map(algoritmo_genetico, tarefas)

    with open("melhores_custos.txt", "w") as f:
        for res in resultados:
            f.write(f"{res['arquivo']}: {res['distancia']}\n")

    # === GRAFICO DE CUSTOS ===
    for res in resultados:
        plt.figure()
        plt.plot(res['historico'])
        plt.xlabel("Geração")
        plt.ylabel("Distância")
        plt.title(f"Evolução da distância - {res['arquivo']}")
        plt.grid(True)
        plt.savefig(f"grafico_{res['arquivo'].split('.')[0]}.png")

    # === GRAFICO DE TEMPO DE EXECUÇÃO ===
    plt.figure()
    nomes = [res['arquivo'] for res in resultados]
    tempos = [res['tempo'] for res in resultados]
    plt.bar(nomes, tempos, color='orange')
    plt.ylabel("Tempo (s)")
    plt.title("Tempo de execução por instância")
    plt.grid(axis='y')
    plt.savefig("grafico_tempos_execucao.png")

if __name__ == "__main__":
    main()
