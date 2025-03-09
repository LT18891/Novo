# --- Limpar dispositivos gráficos abertos ---
while (!is.null(dev.list())) dev.off()

# --- Instalação e carregamento dos pacotes necessários ---
if (!require("tidyverse")) install.packages("tidyverse", dependencies = TRUE)
if (!require("forecast")) install.packages("forecast", dependencies = TRUE)
if (!require("ggplot2")) install.packages("ggplot2", dependencies = TRUE)

library(tidyverse)
library(forecast)
library(ggplot2)

# --- 1. Gerar dados sintéticos de aquecimento global ---
set.seed(123)  # Para reprodutibilidade
anos <- 1880:2020
n <- length(anos)

# Simular a concentração de CO2 (em ppm) com tendência de aumento:
# Aproximadamente 280 ppm em 1880 até 415 ppm em 2020, com variação aleatória
concentracao_CO2 <- seq(from = 280, to = 415, length.out = n) + rnorm(n, 0, 2)

# Simular a temperatura média global (em °C):
# Temperatura base de 13°C, com efeito linear do CO2 e erro autocorrelacionado (processo AR(1))
phi <- 0.7  # Parâmetro do processo AR(1)
erro <- numeric(n)
erro[1] <- rnorm(1, 0, 0.2)
for (i in 2:n) {
  erro[i] <- phi * erro[i - 1] + rnorm(1, 0, 0.2)
}
temperatura_media <- 13 + 0.02 * (concentracao_CO2 - 280) + erro

# Criar um data frame com os dados
dados <- data.frame(
  Ano = anos,
  CO2 = concentracao_CO2,
  Temperatura = temperatura_media
)

# Visualizar as primeiras linhas dos dados
head(dados)

# --- 2. Converter os dados em objetos de série temporal ---
# Como os dados são anuais, a frequência é 1
serie_temperatura <- ts(dados$Temperatura, start = 1880, frequency = 1)
serie_CO2 <- ts(dados$CO2, start = 1880, frequency = 1)

# --- 3. Análise exploratória dos dados (plots base R) ---
# Ajustar as margens e dividir a área de plotagem para dois gráficos
par(mfrow = c(2, 1), mar = c(4, 4, 2, 1))

plot(serie_temperatura,
     main = "Temperatura Média Global (°C)",
     ylab = "Temperatura (°C)",
     xlab = "Ano")

plot(serie_CO2,
     main = "Concentração de CO2 (ppm)",
     ylab = "CO2 (ppm)",
     xlab = "Ano")

# Restaurar o layout padrão de plotagem
par(mfrow = c(1, 1))

# --- 4. Ajuste de Modelo ARIMA com Regressor Exógeno ---
# Ajustar um modelo ARIMA à série de temperatura utilizando a série de CO2 como variável exógena
modelo_arima <- auto.arima(serie_temperatura, xreg = serie_CO2)
summary(modelo_arima)

# Diagnóstico dos resíduos do modelo
checkresiduals(modelo_arima)

# --- 5. Previsão para os Próximos 20 Anos ---
anos_futuros <- 2021:(2020 + 20)
n_futuro <- length(anos_futuros)

# Simular valores futuros para a concentração de CO2
# Supondo um aumento médio anual de aproximadamente 0.75 ppm
CO2_futuro <- seq(from = tail(dados$CO2, 1), length.out = n_futuro, by = 0.75)

# Gerar a previsão do modelo ARIMA com a variável exógena
previsao <- forecast(modelo_arima, xreg = CO2_futuro, h = n_futuro)

# Plot da previsão utilizando base R
plot(previsao,
     main = "Previsão de Temperatura para os Próximos 20 Anos",
     ylab = "Temperatura (°C)",
     xlab = "Ano")

# --- 6. Visualização Integrada com ggplot2 ---
# Criar um data frame com os dados da previsão
previsao_df <- data.frame(
  Ano = anos_futuros,
  TemperaturaPrevista = as.numeric(previsao$mean),
  LimInf = as.numeric(previsao$lower[, 2]),
  LimSup = as.numeric(previsao$upper[, 2])
)

# Plot final utilizando ggplot2 com 'linewidth' (substituindo 'size')
p <- ggplot() +
  geom_line(data = dados, aes(x = Ano, y = Temperatura), color = "blue", linewidth = 1) +
  geom_line(data = previsao_df, aes(x = Ano, y = TemperaturaPrevista),
            color = "red", linewidth = 1, linetype = "dashed") +
  geom_ribbon(data = previsao_df, aes(x = Ano, ymin = LimInf, ymax = LimSup),
              fill = "red", alpha = 0.2) +
  labs(title = "Previsão de Aquecimento Global",
       subtitle = "Modelo ARIMA com Regressor Exógeno (CO2)",
       x = "Ano",
       y = "Temperatura Média Global (°C)") +
  theme_minimal()

# Exibir o gráfico final
print(p)
