# Apresentação

## Importações:

- marimo: faz o papel de notebook, separa em células e adiciona ambiente markdown e Latex visual com os elementos UI

- matplotlib: faz o papel de motor gráfico, gerando as imagens em função dos dados

- numpy: base da implementação numérica da simulação, através da qual fazemos cálculos vetorizados, implementando o efeito do ruído inteiramente de uma vez em uma grande quantidade de valores. Faz todo o papel matemático.

- scipy: usamos a função complementar do erro erfc que representa o $\text{Q(x)}=\frac{1}{2}\text{erfc}(\frac{x}{\sqrt{2}})$ onde calculamos as curvas teóricas de BER.

- path: manipulação de caminhos

- shutil: manipulação de arquivos e pastas

## Definições

Com base no que foi pedido na proposta, os seguintes valores são definidos. Apesar de constantes, mantive os nomes em minúsculo.

fc = 10.0        : frequência da portadora.
os = 4           : fator de sobreamostragem. fs = os*fc
alpha = 0.15     : roll-off factor.
ebn0_points      : valores considerados para energia do sinal
modulation_cases : quais modulações são consideradas e realizadas.
num_bits_target  : valor máximo de bits gerados para a simulação até conseguir 100 erros
output_path      : caminho para saçvar artefatos gerados.

## Codificação Gray

int_to_gray: apenas retorna o argumento após passar por uma operação bitwise de XOR com a versão deslocada bitwise. 

Como a implementação dessas operações é bitwise, ela diretamente usa a forma binária do valor passado.

gray_to_int: toma um valor em gray e transforma em seu correspondente binário, facilita a implementação ao abstrair a interpretação de cada símbolo na sua forma binária.

A implementação é iterativa. Para um valor qualquer, usa a operação xor bitwise contra uma string de 0s do mesmo tamanho que a palavra em gray, faz deslocamento bitwise.

A codificação em Gray permite que a constelação seja distribuída sequencialmente de forma crescente sobre o plano com cada símbolo representando um valor cuja palavra de bits difere em apenas uma casa. Na modulação PSK o valor é expressado pela fase em uma sequência anti-horária, já no QAM, centrado em 0, cada step em uma direção ortogonal aproxima-se da palavra seguinte de forma crescente no eixo x e no eixo y em suas respectivas direções e decrescente na direção oposta. 

Quando ocorre um erro de símbolo, por proximidade maior a um vizinho, que é estatisticamente mais provável quão maior a relação $\frac{E_b}{N_0}$, o erro é de um bit e daí tiramos a aproximação usual de $\frac{SER}{b}$ = BER

## Constelaçõoes e mapeamento

qam_constellation: Gera uma constelação QAM quadrada tomando como argumento a quantidade de símbolos, diretamente calculando o lado do quadrado, que representa a quantidade de símbolos por fase ou quadratura (por espaço ortogonal de sinal). Ele escolhe os valores espaçando de 2 unidades entre o menor valor ao valor mais alto simetricamente, colocando os valores no final, em um formato de número complexo para serialização.

psk_constellation: Gera uma constelação de módulo constante variando a fase ao fazer exponencial de 0 a (m-1) dividido por m, que dá todos os valores fracionários menores que 1 proporcionais à rotação desejada de 360/m graus

bits_to_symbols: Transforma a stream de bits equiprováveis em um bloco de bits de tamanho $log_2(M)$. Ao definir o tamanho do bloco, ele usa a função reshape que toma os valores e separa em blocos desse tamanho, e então transforma cada bloco em um valor decimal através do produto vetorial de cada caracter do bloco com o valor correspondente posicional do caracter em binário. 

Depois disso guarda em um array numpy ao transformar o número em codificação gray. Ou seja, ordena os valores decimais na ordem Gray, interpretando-os como binários. É uma cola para remepeamento. 

Gera uma constelação do tamanho correto e reordena-a de modo que o símbolo binário está na ordem Gray

É uma maneira de gerar uma constelação fazendo apenas seus símbolos e voltando sem colocar uma camada mais humana no meio da implementação. 

--- 

symbols_to_bits: implementa a detecção baseada em distância euclidiana para ambas as modulações. 

Toma os símbolos esperados e os recebidos e calcula a distância de cada símbolo recebido para cada símbolo da constelação vetorialmente e eleva ao quadrado. Após isso, retorna o menor valor por coluna. Isso ainda está ordenado por Gray. Depois disso é feita a reversão do mapeamento Gray. 

Após isso faz uma transformação de inteiro pra binário e os coloca em sequência.

## Pulsos de Transmissão.

pulse_coeffs: se o nome passado é "nrz", o pulso é dado por 4 "amostras" da onda quadrada ideal., se não, aplica a fórmula do RRC como ela é implementada em diversas fontes.

## Conexão: 

simulate_link: essa função toma todos os parâmetros relevantes para simular uma comunicação:

def simulate_link(kind, m, pulse_name, ebn0_db, num_symbols, rng, alpha, fc, os):

kind: tipo de modulação
m           : ordem
pulse_name  : qual pulso
ebn0_db     : valor de eb_n0 em dB
num_symbols : número de símbolos na stream
rng         : gerador pseudoaleatório travado na seed
alpha       : roll-off
fc          : frequência da portadora
os          : oversampling

* bits_tx: gera os bits com rng.integers permitindo valores 0 e 1 com o tamanho ihual a número de bits multiplicado por número de bits por símbolo, calculado com os valores passados.

essa função então chama funções que fizemos anteriormente, especialmente a bits_to_symbols que dá conta do fluxo: bits -> blocos -> índices -> remapping Gray -> vetor constelação

Cria o pulso com pulse_coeffs

faz upsample inserindo zeros

shaped = np.convolve(upsampled, pulse, mode="full") faz a formatação de cada símbolo escolhido em um pulso correspondente através da convolução.

Definimos a frequência de amostragem e guardamos cada amostra em um vetor chamado t de tempo.

implementa a portadora

tx é a linha que faz a modulação separando real e imaginário

Eb/N0 para linear

energia média

desvio padrão do ruído

simula o canal awgn ao somar os valores transmitidos com um valor que multiplica o desvio do ruído por uma distribuição normal normalizada (0 a 100%)

Faz a demodulação ortogonal

Passa pelo filtro casado (pulso invertido no tempo)

Compensação de atrado e guarda índices de amostragem

Faz a decisão com symbols_to_bits e guarda em um vetor

símbolos -> dist euclidiana -> "desmapeia" do Gray -> vetor de bits

Calcula a BER ao comparar bit a bit e ver quantos estavam errados. 