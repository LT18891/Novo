# Autor: Luiz Tiago Wilcke
# Descrição: Este script aplica um modelo SARIMA sofisticado para prever a proliferação da gripe,
# utilizando dados sintéticos incorporados no próprio código.
#
# O script realiza:
#  - Geração de dados sintéticos mensais de casos de gripe (de janeiro de 2015 a dezembro de 2019)
#  - Conversão dos dados em uma série temporal com componente sazonal (frequência mensal)
#  - Teste de estacionariedade e, se necessário, aplicação de diferenciação para estabilizar a série
#  - Ajuste de um modelo SARIMA utilizando a função auto.arima com busca exaustiva
#  - Análise dos resíduos para validar o ajuste do modelo
#  - Geração e visualização de previsões para os próximos 12 meses

# Carregar bibliotecas necessárias
library(forecast)   # Para modelagem e previsão com modelos ARIMA/SARIMA
library(tseries)    # Para testes de estacionariedade
library(ggplot2)    # Para visualização dos gráficos
library(lubridate)  # Para manipulação de datas

# Fixar semente para reprodutibilidade dos dados sintéticos
set.seed(123)

# Gerar dados sintéticos mensais de casos de gripe entre janeiro de 2015 e dezembro de 2019
datas <- seq(as.Date("2015-01-01"), as.Date("2019-12-01"), by = "month")
n <- length(datas)

# Gerar casos com padrão sazonal: média base + componente sazonal (senoidal) + ruído aleatório
casos <- round(50 + 15 * sin(2 * pi * (1:n) / 12) + rnorm(n, mean = 0, sd = 5))

# Criar um data frame com os dados gerados
dados_gripe <- data.frame(data = datas, casos = casos)

# Exibir os primeiros registros dos dados gerados
print(head(dados_gripe))

# Converter os dados em uma série temporal
# Como os dados são mensais, definimos a frequência como 12
data_inicio <- c(year(min(dados_gripe$data)), month(min(dados_gripe$data)))
serie_temporal <- ts(dados_gripe$casos, start = data_inicio, frequency = 12)

# Visualizar a série temporal
autoplot(serie_temporal) +
  ggtitle("Casos Mensais de Gripe (2015-2019)") +
  xlab("Ano") + ylab("Número de Casos")

# Teste de estacionariedade: Teste ADF (Augmented Dickey-Fuller)
resultado_adf <- adf.test(serie_temporal, alternative = "stationary")
print(resultado_adf)

# Determinar quantas diferenciações são necessárias para tornar a série estacionária
num_diferenciacoes <- ndiffs(serie_temporal)
cat("Número de diferenciações necessárias:", num_diferenciacoes, "\n")

# Se necessário, transformar a série para estacionariedade
if(num_diferenciacoes > 0){
  serie_estacionaria <- diff(serie_temporal, differences = num_diferenciacoes)
  cat("Série diferenciada para alcançar estacionariedade.\n")
  print(adf.test(serie_estacionaria, alternative = "stationary"))
} else {
  serie_estacionaria <- serie_temporal
  cat("A série já é estacionária.\n")
}

# Ajuste do modelo SARIMA:
# Utilizamos a função auto.arima com busca exaustiva (stepwise=FALSE, approximation=FALSE) para identificar os melhores parâmetros,
# incluindo os componentes sazonais.
modelo_sarima <- auto.arima(serie_temporal,
                            seasonal = TRUE,
                            stepwise = FALSE,
                            approximation = FALSE,
                            trace = TRUE)
summary(modelo_sarima)

# Análise dos resíduos do modelo:
# Verificar se os resíduos se comportam como ruído branco (indicando que o modelo capturou bem a dinâmica dos dados)
checkresiduals(modelo_sarima)

# Gerar previsão para os próximos 12 meses
previsao <- forecast(modelo_sarima, h = 12)

# Visualizar a previsão
autoplot(previsao) +
  ggtitle("Previsão de Casos de Gripe - Próximos 12 Meses") +
  xlab("Ano") + ylab("Número de Casos")

# Exibir os valores previstos e os intervalos de confiança
print(previsao)

# Salvar o modelo ajustado para uso futuro (opcional)
saveRDS(modelo_sarima, file = "modelo_sarima_gripe.rds")

# Fim do script.
