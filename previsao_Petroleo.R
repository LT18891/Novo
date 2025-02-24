library(forecast)
library(ggplot2)
library(tibble)

set.seed(123)
n <- 120
tempo <- seq.Date(from = as.Date("2010-01-01"), by = "month", length.out = n)
preco_petroleo <- cumsum(rnorm(n, mean = 0.5, sd = 2)) + 50

dados <- tibble(tempo = tempo, preco_petroleo = preco_petroleo)
serie_petroleo <- ts(dados$preco_petroleo, start = c(2010, 1), frequency = 12)
modelo_arima <- auto.arima(serie_petroleo)
previsao <- forecast(modelo_arima, h = 12)
previsao$mean  <- round(previsao$mean, 3)
previsao$lower <- round(previsao$lower, 3)
previsao$upper <- round(previsao$upper, 3)
grafico <- autoplot(previsao) +
  labs(title = "Previsão do Preço do Petróleo",
       x = "Ano",
       y = "Preço do Petróleo") +
  theme_minimal()

print(grafico)
