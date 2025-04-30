#include <iostream>
#include <cstdlib>  // rand, srand
#include <ctime>   
#include <iomanip>
#include <vector>
#include <random>
#include <algorithm>

using namespace std;

// Estrutura para armazenar uma rota e seu custo
struct Rota {
    vector<int> caminho;
    int custo;
};

// Exibe a matriz de distâncias
void exibeMatriz(int distancia[8][8]){
    for(int i = 0; i < 8; i++){
        for(int j = 0; j < 8; j++){
            cout << setw(4) << distancia[i][j] << " ";
        }
        cout << endl;
    }
}

// Gera uma rota aleatória embaralhada
vector<int> geraRota(){
    vector<int> rota;
    for(int i = 0; i < 8; i++)
        rota.push_back(i);

    random_device rd;
    mt19937 g(rd());
    shuffle(rota.begin(), rota.end(), g);

    return rota;
}

// Calcula o custo de uma rota
int calculaDistancia(const vector<int>& lista, int distancia[8][8]){
    int custo = 0;
    for (int i = 0; i < lista.size() - 1; i++) {
        custo += distancia[lista[i]][lista[i + 1]];
    }
    // Retorno à cidade inicial
    custo += distancia[lista.back()][lista[0]];
    return custo;
}

// Exibe uma rota
void exibeRota(const Rota& rota) {
    for (int cidade : rota.caminho) {
        cout << cidade << " ";
    }
    cout << "| Custo: " << rota.custo << endl;
}

int main() {
    srand(time(nullptr));
    int distancia[8][8];

    // Preenche matriz de distâncias simétrica
    for(int i = 0; i < 8; i++){
        for(int j = i + 1; j < 8; j++){
            int numero = rand() % 10 + 1;
            distancia[i][j] = numero;
            distancia[j][i] = numero;
        }
        distancia[i][i] = 0;
    }

    exibeMatriz(distancia);
    cout << endl;

    // Gera população inicial de rotas
    vector<Rota> populacao;
    for (int i = 0; i < 5; i++) {
        vector<int> caminho = geraRota();
        int custo = calculaDistancia(caminho, distancia);
        populacao.push_back({caminho, custo});
    }

    // Exibe as rotas geradas
    cout << "Rotas geradas:\n";
    for (const Rota& r : populacao) {
        exibeRota(r);
    }
}
