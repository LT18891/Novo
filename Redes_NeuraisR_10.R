##############################################
# 1. SIMULAÇÃO E PRE-PROCESSAMENTO DOS DADOS
##############################################
# Seja n o número de amostras:
n <- 1000

# Geramos as variáveis explicativas:
# PIB \sim U(1000, 5000)
PIB <- runif(n, min = 1000, max = 5000)
# População \sim U(1e6, 1e7)
Populacao <- runif(n, min = 1e6, max = 1e7)
# Investimentos \sim U(50, 200) (em milhões)
Investimentos <- runif(n, min = 50, max = 200)

# A variável resposta (taxa de desemprego) é definida como:
#
#   Y = 0.05 * PIB - 0.000001 * População + 0.2 * Investimentos + \epsilon,
#
# onde \epsilon \sim \mathcal{N}(0, 5^2)
Desemprego <- 0.05 * PIB - 0.000001 * Populacao + 0.2 * Investimentos + 
  rnorm(n, mean = 0, sd = 5)

# Criação do data frame para facilitar a manipulação dos dados:
dados <- data.frame(PIB, Populacao, Investimentos, Desemprego)
cat("Visualização das primeiras linhas dos dados:\n")
print(head(dados))

# Carregando o pacote dplyr para manipulação dos dados:
library(dplyr)
variaveis <- dados %>% select(PIB, Populacao, Investimentos)
resposta <- dados$Desemprego

# Normalização dos dados utilizando o z-score:
# Para cada variável, seja X, temos:
#
#   \tilde{X} = \frac{X - \mu_X}{\sigma_X},
#
# onde \mu_X é a média e \sigma_X é o desvio padrão.
media <- apply(variaveis, 2, mean)
desvio <- apply(variaveis, 2, sd)
variaveis_normalizadas <- scale(variaveis, center = media, scale = desvio)
variaveis_normalizadas <- as.matrix(variaveis_normalizadas)

# Dividindo o conjunto de dados em treino (80%) e teste (20%):
indices <- sample(1:n, size = 0.8 * n)
x_treino <- variaveis_normalizadas[indices, ]
x_teste <- variaveis_normalizadas[-indices, ]
y_treino <- matrix(resposta[indices], ncol = 1)
y_teste <- matrix(resposta[-indices], ncol = 1)

##############################################
# 2. DEFINIÇÃO MATEMÁTICA E IMPLEMENTAÇÃO DA REDE NEURAL
##############################################
# Nossa rede neural é estruturada da seguinte forma:
#
#   - Camada de Entrada: 3 neurônios (variáveis: PIB, População, Investimentos)
#   - Camada Oculta: 40 neurônios com função de ativação ReLU
#   - Camada de Saída: 1 neurônio com ativação linear (para regressão)
#
# Seja:
#   X \in \mathbb{R}^{n \times d}, onde d=3,
#   W^{(1)} \in \mathbb{R}^{d \times h} (pesos da camada oculta, h=40),
#   b^{(1)} \in \mathbb{R}^{1 \times h} (bias da camada oculta),
#   W^{(2)} \in \mathbb{R}^{h \times 1} (pesos da camada de saída),
#   b^{(2)} \in \mathbb{R}^{1 \times 1} (bias da camada de saída).
#
# A propagação direta (forward propagation) é definida por:
#
#   Z^{(1)} = X W^{(1)} + b^{(1)}   \quad  (n \times h)
#   A^{(1)} = \phi(Z^{(1)}), \quad \text{onde } \phi(x) = \max(0, x) \; (\text{ReLU})
#   Z^{(2)} = A^{(1)} W^{(2)} + b^{(2)} \quad (n \times 1)
#   \hat{Y} = Z^{(2)} \quad (\text{saída linear})
#
# O custo é medido pelo Erro Quadrático Médio (MSE):
#
#   J = \frac{1}{n} \sum_{i=1}^{n} (\hat{y}_i - y_i)^2.
#
# As derivadas necessárias para o algoritmo de retropropagação (backpropagation)
# são obtidas a partir da diferenciação das funções de custo e ativação.

# Função de ativação ReLU e sua derivada:
relu <- function(x) {
  # Função: \phi(x) = \max(0, x)
  m <- pmax(0, x)
  dim(m) <- dim(x)  # preserva a forma original
  return(m)
}
d_relu <- function(x) {
  # Derivada da ReLU:
  # \phi'(x) =
  #   \begin{cases}
  #      1, & \text{se } x > 0, \\
  #      0, & \text{caso contrário.}
  #   \end{cases}
  m <- ifelse(x > 0, 1, 0)
  dim(m) <- dim(x)
  return(m)
}

# Especificações da rede:
input_dim  <- ncol(x_treino)  # d = 3
hidden_dim <- 40             # h = 40
output_dim <- 1              # saída = 1

# Função para inicializar pesos de forma aleatória (distribuição Normal):
inicializa_pesos <- function(linhas, colunas) {
  # \theta \sim \mathcal{N}(0, 0.1^2)
  matrix(rnorm(linhas * colunas, mean = 0, sd = 0.1), nrow = linhas, ncol = colunas)
}

# Inicializando os parâmetros:
# Pesos e bias para a camada oculta:
W1 <- inicializa_pesos(input_dim, hidden_dim)  # W^{(1)} \in \mathbb{R}^{3 \times 40}
b1 <- matrix(0, nrow = 1, ncol = hidden_dim)     # b^{(1)} \in \mathbb{R}^{1 \times 40}

# Pesos e bias para a camada de saída:
W2 <- inicializa_pesos(hidden_dim, output_dim)   # W^{(2)} \in \mathbb{R}^{40 \times 1}
b2 <- matrix(0, nrow = 1, ncol = output_dim)       # b^{(2)} \in \mathbb{R}^{1 \times 1}

# Parâmetros de treinamento:
epocas <- 100
taxa_aprendizado <- 0.01
n_treino <- nrow(x_treino)
hist_error <- numeric(epocas)

# ------------------------------
# Algoritmo de Gradiente Descendente (Batch)
# ------------------------------
for (epoca in 1:epocas) {
  
  # 1. Propagação Direta (Forward Propagation)
  # Cálculo da ativação da camada oculta:
  #   Z^{(1)} = X W^{(1)} + b^{(1)}
  z1 <- x_treino %*% W1 + matrix(b1, nrow = n_treino, ncol = hidden_dim, byrow = TRUE)
  # Aplicação da função ReLU:
  a1 <- relu(z1)
  
  # Cálculo da camada de saída:
  #   Z^{(2)} = A^{(1)} W^{(2)} + b^{(2)}
  z2 <- a1 %*% W2 + matrix(b2, nrow = n_treino, ncol = output_dim, byrow = TRUE)
  y_pred <- z2  # Saída linear: \hat{Y} = Z^{(2)}
  
  # 2. Cálculo do Custo (Erro Quadrático Médio)
  #   J = \frac{1}{n} \sum_{i=1}^{n} (\hat{y}_i - y_i)^2
  erro <- y_pred - y_treino
  custo <- mean(erro^2)
  hist_error[epoca] <- custo
  
  # 3. Retropropagação (Backpropagation)
  #
  # Derivada do custo em relação à saída:
  #   \frac{\partial J}{\partial Z^{(2)}} = \frac{2}{n}(Z^{(2)} - Y)
  dz2 <- (2 / n_treino) * erro
  
  # Gradiente para W^{(2)}:
  #   \frac{\partial J}{\partial W^{(2)}} = (A^{(1)})^T dz2
  dW2 <- t(a1) %*% dz2
  # Gradiente para b^{(2)} (soma sobre as linhas):
  db2 <- colSums(dz2)
  
  # Propagação do gradiente para a camada oculta:
  #   da^{(1)} = dz2 (W^{(2)})^T
  da1 <- dz2 %*% t(W2)
  # Aplicando a derivada da função ReLU:
  #   dz^{(1)} = da^{(1)} \odot \phi'(z^{(1)}), onde \odot é o produto elemento a elemento
  dz1 <- da1 * d_relu(z1)
  
  # Gradiente para W^{(1)}:
  #   \frac{\partial J}{\partial W^{(1)}} = (X)^T dz^{(1)}
  dW1 <- t(x_treino) %*% dz1
  # Gradiente para b^{(1)}:
  db1 <- colSums(dz1)
  
  # 4. Atualização dos Parâmetros (Regra do Gradiente Descendente):
  #   \theta = \theta - \eta \nabla_\theta J
  W2 <- W2 - taxa_aprendizado * dW2
  b2 <- b2 - taxa_aprendizado * db2
  W1 <- W1 - taxa_aprendizado * dW1
  b1 <- b1 - taxa_aprendizado * db1
  
  if (epoca %% 10 == 0) {
    cat(sprintf("Época %d - Custo (MSE): %.4f\n", epoca, custo))
  }
}

# Visualização do histórico do custo ao longo do treinamento:
plot(1:epocas, hist_error, type = "l", col = "blue", lwd = 2,
     xlab = "Época", ylab = "Custo (MSE)",
     main = "Histórico do Custo Durante o Treinamento")

##############################################
# 3. AVALIAÇÃO NO CONJUNTO DE TESTE
##############################################
n_teste <- nrow(x_teste)
# Propagação direta para as amostras de teste:
z1_teste <- x_teste %*% W1 + matrix(b1, nrow = n_teste, ncol = hidden_dim, byrow = TRUE)
a1_teste <- relu(z1_teste)
z2_teste <- a1_teste %*% W2 + matrix(b2, nrow = n_teste, ncol = output_dim, byrow = TRUE)
y_teste_pred <- z2_teste

# Cálculo do erro e do MSE:
erro_teste <- y_teste_pred - y_teste
mse_teste <- mean(erro_teste^2)
cat("Erro Quadrático Médio (MSE) no conjunto de teste:", mse_teste, "\n")

##############################################
# 4. DESENHO DA ARQUITETURA DA REDE NEURAL (VISUALIZAÇÃO ESTILO CLÁSSICO)
##############################################
desenhar_rede_neural <- function() {
  # Configuração do dispositivo gráfico:
  par(mar = c(1, 1, 3, 1), bg = "white")
  
  # Cria um plot em branco que servirá de tela:
  plot(0, type = "n", xlim = c(0, 6), ylim = c(0, 6),
       axes = FALSE, xlab = "", ylab = "",
       main = "Arquitetura da Rede Neural\n(Autor: Luiz Tiago Wilcke)",
       cex.main = 1.2, font.main = 2)
  
  # Definindo as posições horizontais (x) para cada camada:
  x_input  <- 1
  x_hidden <- 3
  x_output <- 5
  
  # Definindo as posições verticais (y) para os neurônios de cada camada:
  y_input  <- seq(2, 4, length.out = 3)        # 3 neurônios de entrada
  y_hidden <- seq(0.5, 5.5, length.out = 40)      # 40 neurônios na camada oculta
  y_output <- 3                                 # 1 neurônio na saída
  
  # Função auxiliar para desenhar neurônios usando círculos:
  desenhar_neuronios <- function(x, ys, cor_fundo, cor_borda = "black", raio = 0.12) {
    symbols(x = rep(x, length(ys)), y = ys, circles = rep(raio, length(ys)),
            inches = FALSE, add = TRUE, fg = cor_borda, bg = cor_fundo)
  }
  
  # Desenha cada camada com cores diferenciadas:
  desenhar_neuronios(x_input, y_input, cor_fundo = "skyblue")
  text(x_input, max(y_input) + 0.4, "Entrada\n3 neurônios", cex = 0.9, font = 2)
  
  desenhar_neuronios(x_hidden, y_hidden, cor_fundo = "lightgreen")
  text(x_hidden, max(y_hidden) + 0.4, "Oculta\n40 neurônios", cex = 0.9, font = 2)
  
  desenhar_neuronios(x_output, y_output, cor_fundo = "salmon")
  text(x_output, y_output + 0.4, "Saída\n1 neurônio", cex = 0.9, font = 2)
  
  # Desenha as conexões entre as camadas:
  # Ajustando a transparência da cor das linhas
  cor_linha <- grDevices::adjustcolor("gray30", alpha.f = 0.3)
  
  # Conexões da camada de entrada para a oculta:
  for (yin in y_input) {
    for (yhid in y_hidden) {
      segments(x_input + 0.12, yin, x_hidden - 0.12, yhid, col = cor_linha)
    }
  }
  
  # Conexões da camada oculta para a saída:
  for (yhid in y_hidden) {
    segments(x_hidden + 0.12, yhid, x_output - 0.12, y_output, col = cor_linha)
  }
  
  # Rótulo do autor no rodapé:
  mtext("Autor: Luiz Tiago Wilcke", side = 1, line = -1.5, cex = 0.8, adj = 1)
}

# Exibe o diagrama da rede neural:
desenhar_rede_neural()

