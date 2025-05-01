import random as rd

class Rota:
    def __init__(self):
        self.rotas = []
        self.custo = 0
        
        
def exibeMatriz(distancia):
    for linha in distancia:
        print(linha)
        
def geraRotas():
    rota = []
    rota.append(rd.sample(range(0, 8), 8))  # Gera uma rota única
    return rota

def calculaDistancia(rota, distancia):
    custo = 0
    for i in range(len(rota) - 1):
        custo += distancia[rota[i]][rota[i+1]]
    
    custo += distancia[rota[-1]][rota[0]]  # A última cidade volta para a primeira
    return custo
        
# Inicializa a classe Rota
novasRotas = Rota()
tamanho = 8

# Gera a matriz de distâncias
distancia = [[0 for _ in range(tamanho)] for _ in range(tamanho)]

for i in range(tamanho):
    for j in range(i + 1, tamanho):
        numero = rd.randint(1, 10)
        distancia[i][j] = numero
        distancia[j][i] = numero

# Exibe a matriz de distâncias
exibeMatriz(distancia)

# Gera e calcula o custo das rotas
for i in range(8):
    nova_rota = geraRotas()[0]  # A função geraRotas retorna uma lista com uma rota, então pegamos o primeiro elemento
    novasRotas.rotas.append(nova_rota)
    custo = calculaDistancia(nova_rota, distancia)
    novasRotas.custo += custo  # Soma o custo ao custo total (pode ser ajustado dependendo do seu objetivo)

# Exibe as rotas e seus custos
print("\nRotas geradas:")
for rota in novasRotas.rotas:
    custo = calculaDistancia(rota, distancia)  # Calcula o custo para cada rota gerada
    print(f"{rota} = {custo}")
