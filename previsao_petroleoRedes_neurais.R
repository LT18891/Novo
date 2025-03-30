library(torch)
library(ggplot2)
library(dplyr)

# ---------------------------
# 1. Gerando Dados Sintéticos
# ---------------------------
set.seed(123)
num_dias <- 500
dias <- 1:num_dias
# Série temporal simulando preços do petróleo com tendência, sazonalidade e ruído
preco_petroleo <- 50 + 0.05 * dias + sin(dias / 10) * 10 + rnorm(num_dias, mean = 0, sd = 2)
dados <- data.frame(dia = dias, preco_petroleo = preco_petroleo)

# Visualização dos dados sintéticos
ggplot(dados, aes(x = dia, y = preco_petroleo)) +
  geom_line(color = "blue") +
  labs(title = "Preço do Petróleo - Dados Sintéticos", x = "Dia", y = "Preço") +
  theme_minimal()

# -------------------------------------------
# 2. Preparação dos Dados para Aprendizado
# -------------------------------------------
# Função para converter a série temporal em dados supervisionados utilizando uma janela (look_back)
criar_sequencias <- function(dados, look_back = 10) {
  X <- list()
  y <- list()
  for(i in 1:(nrow(dados) - look_back)) {
    seq_x <- dados$preco_petroleo[i:(i + look_back - 1)]
    seq_y <- dados$preco_petroleo[i + look_back]
    X[[i]] <- seq_x
    y[[i]] <- seq_y
  }
  # Cria um array com dimensões: [amostras, look_back, 1]
  X_array <- array(unlist(X), dim = c(length(X), look_back, 1))
  # Cria um array com dimensões: [amostras, 1]
  y_array <- array(unlist(y), dim = c(length(y), 1))
  return(list(X = X_array, y = y_array))
}

look_back <- 10
sequencias <- criar_sequencias(dados, look_back = look_back)

# Divisão dos dados em treinamento (80%) e teste (20%), mantendo as dimensões com drop = FALSE
num_amostras <- dim(sequencias$X)[1]
tamanho_treino <- floor(0.8 * num_amostras)
X_treino <- sequencias$X[1:tamanho_treino, , , drop = FALSE]
y_treino <- sequencias$y[1:tamanho_treino, , drop = FALSE]
X_teste  <- sequencias$X[(tamanho_treino + 1):num_amostras, , , drop = FALSE]
y_teste  <- sequencias$y[(tamanho_treino + 1):num_amostras, , drop = FALSE]

# ---------------------------
# 3. Normalização dos Dados
# ---------------------------
# Normalização Min-Max baseada em todos os preços
min_val <- min(dados$preco_petroleo)
max_val <- max(dados$preco_petroleo)

normalizar <- function(x) {
  (x - min_val) / (max_val - min_val)
}
desnormalizar <- function(x) {
  x * (max_val - min_val) + min_val
}

X_treino_norm <- array(normalizar(X_treino), dim = dim(X_treino))
y_treino_norm <- normalizar(y_treino)
X_teste_norm  <- array(normalizar(X_teste), dim = dim(X_teste))
y_teste_norm  <- normalizar(y_teste)

# Converter para tensores do torch
X_treino_tensor <- torch_tensor(X_treino_norm, dtype = torch_float())
y_treino_tensor <- torch_tensor(y_treino_norm, dtype = torch_float())
X_teste_tensor  <- torch_tensor(X_teste_norm,  dtype = torch_float())
y_teste_tensor  <- torch_tensor(y_teste_norm,  dtype = torch_float())

# Verifica e, se necessário, adiciona a dimensão extra para X (garantindo 3D: [amostras, look_back, 1])
if (length(X_treino_tensor$size()) == 2) {
  X_treino_tensor <- X_treino_tensor$unsqueeze(3)
}
if (length(X_teste_tensor$size()) == 2) {
  X_teste_tensor <- X_teste_tensor$unsqueeze(3)
}

# ---------------------------
# 4. Construção do Modelo LSTM com Torch
# ---------------------------
# Definindo um módulo LSTM com uma camada LSTM e uma camada densa (linear)
modelo <- nn_module(
  "ModeloLSTM",
  initialize = function(input_size, hidden_size, num_layers, output_size) {
    self$lstm <- nn_lstm(
      input_size = input_size,
      hidden_size = hidden_size,
      num_layers = num_layers,
      batch_first = TRUE
    )
    self$fc <- nn_linear(hidden_size, output_size)
  },
  forward = function(x) {
    # x: [batch, seq_len, input_size]
    lstm_out <- self$lstm(x)
    # lstm_out[[1]] tem dimensão [batch, seq_len, hidden_size]; pegamos o último passo de tempo
    ultimo_passo <- lstm_out[[1]][ , dim(x)[2], ]
    saida <- self$fc(ultimo_passo)
    saida
  }
)

# Instanciando o modelo
input_size <- 1
hidden_size <- 50
num_layers <- 1
output_size <- 1
modelo_inst <- modelo(input_size, hidden_size, num_layers, output_size)

# Definindo a função de perda (MSE) e o otimizador (Adam)
loss_fn <- nn_mse_loss()
optimizer <- optim_adam(modelo_inst$parameters, lr = 0.001)

# ---------------------------
# 5. Treinamento do Modelo
# ---------------------------
num_epochs <- 50
batch_size <- 16
num_batches <- ceiling(tamanho_treino / batch_size)
loss_history <- numeric(num_epochs)

for (epoch in 1:num_epochs) {
  modelo_inst$train()
  epoch_loss <- 0
  # Embaralha as amostras para o treinamento em mini-batches
  indices <- sample(1:tamanho_treino)
  for (i in seq(1, tamanho_treino, by = batch_size)) {
    batch_indices <- indices[i:min(i + batch_size - 1, tamanho_treino)]
    # Garantindo a indexação correta com 3 índices para X e 2 para y
    X_batch <- X_treino_tensor[batch_indices,,, drop = FALSE]
    y_batch <- y_treino_tensor[batch_indices,, drop = FALSE]
    
    optimizer$zero_grad()
    pred <- modelo_inst(X_batch)
    loss <- loss_fn(pred, y_batch)
    loss$backward()
    optimizer$step()
    epoch_loss <- epoch_loss + loss$item()
  }
  loss_history[epoch] <- epoch_loss / num_batches
  cat(sprintf("Época %d/%d - Loss: %f\n", epoch, num_epochs, loss_history[epoch]))
}

# ---------------------------
# 6. Previsões e Visualização dos Resultados
# ---------------------------
modelo_inst$eval()
with_no_grad({
  predicoes_tensor <- modelo_inst(X_teste_tensor)
})
predicoes_norm <- as_array(predicoes_tensor)
predicoes <- desnormalizar(predicoes_norm)
y_teste_real <- desnormalizar(as_array(y_teste_tensor))

# Data frame para plotagem dos resultados
df_plot <- data.frame(
  indice = 1:length(y_teste_real),
  preco_real = as.vector(y_teste_real),
  preco_previsto = as.vector(predicoes)
)

ggplot(df_plot, aes(x = indice)) +
  geom_line(aes(y = preco_real), color = "blue") +
  geom_line(aes(y = preco_previsto), color = "red") +
  labs(title = "Previsão do Preço do Petróleo (Torch)",
       subtitle = "Linha Azul: Preço Real | Linha Vermelha: Preço Previsto",
       x = "Índice das Amostras do Conjunto de Teste",
       y = "Preço do Petróleo") +
  theme_minimal()

# Plot do histórico de perda durante o treinamento
df_loss <- data.frame(epoca = 1:num_epochs, loss = loss_history)
ggplot(df_loss, aes(x = epoca, y = loss)) +
  geom_line(color = "darkgreen") +
  labs(title = "Histórico de Perda Durante o Treinamento",
       x = "Época", y = "MSE") +
  theme_minimal()
