# Modelo de Heston para simulação de preços de ações com volatilidade estocástica

# Parâmetros do modelo:
S0 <- 100           # Preço inicial da ação (valor inicial de S)
v0 <- 0.04          # Volatilidade inicial (ou variância instantânea, exemplo: 4%)
mu <- 0.1           # Taxa de retorno média da ação (drift, ou retorno esperado, 10% ao ano)
kappa <- 2          # Taxa de reversão da volatilidade (quanto maior, mais rápido a volatilidade retorna à média)
theta <- 0.04       # Volatilidade média de longo prazo (valor para o qual a volatilidade tende a reverter, 4%)
sigma_v <- 0.3      # Volatilidade da volatilidade (intensidade dos choques na volatilidade)
rho <- -0.7         # Correlação entre os ruídos dW1 (preço) e dW2 (volatilidade), que captura a relação entre choques nos dois processos

# Configurações da simulação:
N <- 252            # Número de passos (por exemplo, 252 dias de negociação em 1 ano)
T <- 1              # Horizonte de tempo total da simulação (1 ano)
dt <- T / N         # Tamanho de cada passo de tempo

# Vetores para armazenar os resultados da simulação:
precos <- numeric(N + 1)          # Vetor para os preços da ação ao longo do tempo
volatilidades <- numeric(N + 1)   # Vetor para armazenar a evolução da volatilidade (variância)

# Condições iniciais:
precos[1] <- S0                   # Inicializa o preço da ação com S0
volatilidades[1] <- v0            # Inicializa a volatilidade com v0

set.seed(123)  # Define uma semente para a geração de números aleatórios, garantindo reprodutibilidade

# Simulação do Modelo de Heston utilizando o método de Euler–Maruyama:
for (i in 1:N) {
  # Gera o incremento do processo de Wiener para o preço (dW1):
  # dW1 segue uma distribuição normal com média 0 e desvio padrão sqrt(dt)
  dW1 <- rnorm(1, mean = 0, sd = sqrt(dt))
  
  # Gera um incremento adicional dZ, também com distribuição normal,
  # que será usado para construir o processo dW2 com a correlação desejada.
  dZ  <- rnorm(1, mean = 0, sd = sqrt(dt))
  
  # Calcula o incremento do processo de Wiener para a volatilidade (dW2)
  # Incorporando a correlação com dW1:
  # dW2 = rho * dW1 + sqrt(1 - rho^2) * dZ garante que a correlação entre dW1 e dW2 seja igual a rho.
  dW2 <- rho * dW1 + sqrt(1 - rho^2) * dZ
  
  # Atualiza o preço da ação:
  # A equação do preço incorpora dois termos:
  # 1. Drift determinístico: mu * S * dt
  # 2. Difusão estocástica: sqrt(v) * S * dW1
  # O uso de sqrt(max(volatilidades[i], 0)) garante que não haja tentativa de calcular a raiz de um valor negativo.
  precos[i+1] <- precos[i] + mu * precos[i] * dt + sqrt(max(volatilidades[i], 0)) * precos[i] * dW1
  
  # Atualiza a volatilidade (variância) usando a equação de reversão à média:
  # Termo determinístico (drift): kappa * (theta - v) * dt, que empurra a volatilidade para theta
  # Termo estocástico (difusão): sigma_v * sqrt(v) * dW2
  volatilidades[i+1] <- volatilidades[i] + 
    kappa * (theta - volatilidades[i]) * dt + 
    sigma_v * sqrt(max(volatilidades[i], 0)) * dW2
  
  # Garante que a volatilidade não se torne negativa, ajustando para o mínimo de 0.
  volatilidades[i+1] <- max(volatilidades[i+1], 0)
}

# Plotando a evolução do preço da ação ao longo do tempo:
plot(seq(0, T, by = dt), precos, type = 'l', col = 'blue', lwd = 2,
     xlab = 'Tempo (anos)', ylab = 'Preço da Ação',
     main = 'Simulação do Modelo de Heston')

