Pelo que entendi, o código baseia-se na ideia do problema do Caixeiro Viajante, que consiste em sair de uma cidade inicial, passar por todas as outras até retornar ao início, sem repetir nenhuma cidade. 
A ideia de juntar com o Algoritmo Genético é basear na ideia do Caixeiro Viajante, onde serão geradas rotas e devemos selecionar as rotas com menores distâncias para continuar com o processo do Algoritmo genético.
Fiz alguns testes com exemplos aleatórios e gerei até agora a matriz com a distância e as rotas, ta em c++ porque eu não consegui pensar em como fazer em python, mas podemos alterar mais pra frente, se quiser.
Tava tentando entender todo o problema com o GPT, mas esse código foi 95% desenvolvido por mim.

Certas ideias anotadas: 

1. Inicialização (você já fez!)

    Criar a matriz de distâncias ✅

    Gerar uma população inicial de rotas aleatórias ✅

    Calcular o custo de cada rota ✅

2. Seleção (escolher os melhores pais)

    Ordenar a população pelo custo.

    Selecionar os melhores (por exemplo, os 2 ou 4 com menor custo).

3. Cruzamento (crossover)

    Combinar duas rotas (pais) para gerar novos filhos.

    Ex: Pega metade de um pai e preenche o resto com o que falta do outro (sem repetir cidades).

    Repita até ter o mesmo número de filhos que o tamanho da população inicial.

4. Mutação

    Com uma pequena chance (por ex. 5%), troque duas cidades aleatórias de uma rota.

    Isso evita que o algoritmo fique preso em soluções locais.

5. Nova geração

    Substitua a população antiga pela nova (ou misture as melhores antigas com os filhos).

    Repita do passo 2 por várias gerações (ex: 100 vezes).

6. Parada

    Quando atingir um número de gerações ou se o custo parar de melhorar.
