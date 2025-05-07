# previsor.R
# Autor: Luiz Tiago Wilcke
# Modelo de previsão de séries temporais usando ARIMA e Redes Neurais (nnetar) em R puro

# --- Instalação automática dos pacotes necessários ---
pacotes <- c("forecast", "ggplot2")
for (pkg in pacotes) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cran.r-project.org")
  }
}

# --- Carregamento das bibliotecas ---
library(forecast)
library(ggplot2)

# --- Geração de dados fictícios ---
set.seed(123)
n <- 120  # 120 meses (10 anos)
time <- 1:n
# Série com tendência linear, sazonalidade anual e ruído gaussiano
serie <- 0.05 * time + 10 * sin(2 * pi * time / 12) + rnorm(n, sd = 3)
ts_data <- ts(serie, start = c(2015, 1), frequency = 12)

# --- Divisão em treino e teste ---
horizonte <- 12  # prever 12 meses à frente
train_length <- length(ts_data) - horizonte
ts_train <- window(ts_data, end = c(2015 + (train_length-1) %/% 12, (train_length-1) %% 12 + 1))
ts_test  <- window(ts_data, start = c(2015 + train_length %/% 12, train_length %% 12 + 1))

# --- Ajuste de modelo ARIMA ---n
modelo_arima <- auto.arima(ts_train)
previsao_arima <- forecast(modelo_arima, h = horizonte)

# --- Ajuste de Rede Neural Autoregressiva ---
modelo_nn <- nnetar(ts_train)
previsao_nn <- forecast(modelo_nn, h = horizonte)

# --- Cálculo de métricas de precisão ---
metricas_arima <- accuracy(previsao_arima, ts_test)
metricas_nn    <- accuracy(previsao_nn, ts_test)

# --- Impressão de resultados ---
cat("=== Métricas ARIMA (horizonte =", horizonte, "meses) ===\n")
print(metricas_arima)
cat("\n=== Métricas Rede Neural (nnetar) ===\n")
print(metricas_nn)

# --- Visualização ---
# Série completa com previsões
autoplot(ts_data) +
  autolayer(previsao_arima, series = "ARIMA", PI = FALSE) +
  autolayer(previsao_nn, series = "Rede Neural", PI = FALSE) +
  labs(
    title = "Previsão de Demanda de Petróleo (Dados Fictícios)",
    x = "Tempo (meses)", y = "Demanda"
  ) +
  scale_colour_manual(
    values = c("ARIMA" = "blue", "Rede Neural" = "red")
  ) +
  theme_minimal()

