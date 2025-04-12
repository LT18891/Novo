###############################################################
# PROJETO: Sistema de Previsão de Vendas com Análise Estatística
# AUTOR:   Luiz Tiago Wilcke
# DATA:    Abril/2025
#
# Descrição:
#    Este código em R exemplifica um projeto complexo utilizando
#    apenas bibliotecas padrões do R. São simulados dados de vendas
#    mensais para um período de 10 anos (120 meses). Em seguida, são
#    realizadas análises exploratórias, ajuste de modelo ARIMA e de um
#    modelo de regressão linear com dummies sazonais, previsão dos próximos
#    12 meses e avaliação dos resíduos.
#
#    Foram incluídas correções para o erro "figure margins too large".
###############################################################

###############################
# 1. SIMULAÇÃO DOS DADOS
###############################
set.seed(123)  # Para garantir reprodutibilidade

# Definir parâmetros da simulação
n_anos <- 10           # 10 anos
n_meses <- n_anos * 12 # 120 meses

# Criar um vetor de datas (usando seq.Date)
data_inicio <- as.Date("2015-01-01")
datas <- seq.Date(from = data_inicio, by = "month", length.out = n_meses)

# Criar um vetor de meses (1 a 12) para efeitos sazonais
meses <- rep(1:12, times = n_anos)

# Simular componente de tendência: vendas aumentam linearmente ao longo do tempo
tendencia <- 100 + (1:n_meses) * 0.5

# Simular componente sazonal: efeito periódico mensal com amplitude
efeito_sazonal <- 10 * sin(2 * pi * meses / 12)

# Simular erro aleatório
erro <- rnorm(n_meses, mean = 0, sd = 5)

# Combinar os componentes para gerar as vendas
vendas <- tendencia + efeito_sazonal + erro

# Criar objeto de série temporal com classe "ts"
vendas_ts <- ts(vendas, start = c(2015, 1), frequency = 12)

# Criar data frame com os dados simulados
dados <- data.frame(Data = datas,
                    Mes = meses,
                    Vendas = vendas)

# Visualizar as primeiras linhas dos dados
head(dados)


###############################
# 2. ANÁLISE EXPLORATÓRIA (EDA)
###############################
# Fechar dispositivos gráficos abertos e ajustar margens para evitar erro
graphics.off()  
par(mar = c(4, 4, 2, 1))

# Plot da série de vendas ao longo do tempo com gráfico base
plot(dados$Data, dados$Vendas, type = "l", col = "blue",
     main = "Série Histórica de Vendas",
     xlab = "Data", ylab = "Vendas")

# Decomposição clássica de séries temporais
decomposicao <- decompose(vendas_ts, type = "additive")
plot(decomposicao)

# Analisar Autocorrelação (ACF) e Autocorrelação Parcial (PACF)
acf(vendas_ts, main = "ACF das Vendas")
pacf(vendas_ts, main = "PACF das Vendas")


###############################
# 3. AJUSTE DO MODELO ARIMA
###############################
# Ajustar um modelo ARIMA manualmente (ordem escolhida: (1,1,1))
modelo_arima <- arima(vendas_ts, order = c(1, 1, 1))
print(modelo_arima)

# Previsão para os próximos 12 meses usando a função predict
previsao_arima <- predict(modelo_arima, n.ahead = 12)

# Obter valores previstos e desvios padrões (erro-padrão)
valores_previstos <- previsao_arima$pred
dp_previstos <- previsao_arima$se

# Construir intervalos de confiança (aproximadamente 95%)
limite_inferior <- valores_previstos - 1.96 * dp_previstos
limite_superior <- valores_previstos + 1.96 * dp_previstos

# Exibir as previsões em forma de data frame
dados_previsao <- data.frame(
  Mes = seq(max(dados$Data) + 1, by = "month", length.out = 12),
  Previsto = valores_previstos,
  LI = limite_inferior,
  LS = limite_superior
)
print(dados_previsao)


###############################
# 4. MODELO DE REGRESSÃO LINEAR COM DUMMY SAZONAL
###############################
# Criar variáveis dummy para os 12 meses
dados$MesF <- factor(dados$Mes, levels = 1:12, labels = month.abb)
# Criar uma variável "Tempo" para representar a tendência
dados$Tempo <- 1:nrow(dados)

# Ajustar um modelo de regressão linear (Vendas ~ Tempo + dummies de mês)
modelo_lm <- lm(Vendas ~ Tempo + MesF, data = dados)
summary(modelo_lm)

# Previsão com o modelo de regressão linear para os próximos 12 meses
novos_dados <- data.frame(
  Tempo = (nrow(dados) + 1):(nrow(dados) + 12),
  MesF = factor(rep(1:12, length.out = 12), levels = 1:12, labels = month.abb)
)
previsao_lm <- predict(modelo_lm, newdata = novos_dados, interval = "confidence")
dados_previsao_lm <- data.frame(
  Mes = seq(max(dados$Data) + 1, by = "month", length.out = 12),
  Previsto = previsao_lm[,"fit"],
  LI = previsao_lm[,"lwr"],
  LS = previsao_lm[,"upr"]
)
print(dados_previsao_lm)


###############################
# 5. COMPARAÇÃO E VISUALIZAÇÃO DAS PREVISÕES
###############################
# Fechar dispositivos e ajustar margens novamente
graphics.off()  
par(mar = c(4, 4, 2, 1))

# Plotar a série original de vendas
datas_todos <- c(dados$Data, as.Date(dados_previsao$Mes), as.Date(dados_previsao_lm$Mes))
plot(dados$Data, dados$Vendas, type = "l", col = "black",
     main = "Previsão de Vendas: ARIMA vs Regressão Linear",
     xlab = "Data", ylab = "Vendas",
     xlim = c(min(dados$Data), max(datas_todos)))

# Acrescentar as previsões do modelo ARIMA
novas_datas <- as.Date(dados_previsao$Mes)
lines(novas_datas, dados_previsao$Previsto, col = "red", lwd = 2)
lines(novas_datas, dados_previsao$LI, col = "red", lty = 2)
lines(novas_datas, dados_previsao$LS, col = "red", lty = 2)

# Acrescentar as previsões do modelo de Regressão Linear
novas_datas_lm <- as.Date(dados_previsao_lm$Mes)
lines(novas_datas_lm, dados_previsao_lm$Previsto, col = "blue", lwd = 2)
lines(novas_datas_lm, dados_previsao_lm$LI, col = "blue", lty = 2)
lines(novas_datas_lm, dados_previsao_lm$LS, col = "blue", lty = 2)

# Legenda do gráfico
legend("topleft", legend = c("Dados Reais", "Previsão ARIMA", "Previsão LM"),
       col = c("black", "red", "blue"), lwd = 2)


###############################
# 6. ANÁLISE DOS RESÍDUOS DO MODELO ARIMA
###############################
# Fechar dispositivos e ajustar margens novamente
graphics.off()  
par(mar = c(4, 4, 2, 1))

# Plotar os resíduos do modelo ARIMA e o ACF dos resíduos
residuos <- residuals(modelo_arima)
par(mfrow = c(2, 1))
plot(residuos, type = "o", col = "purple",
     main = "Resíduos do Modelo ARIMA", ylab = "Resíduos", xlab = "Tempo")
acf(residuos, main = "ACF dos Resíduos do Modelo ARIMA")
par(mfrow = c(1, 1))


###############################
# 7. CONCLUSÃO
###############################
# Este script demonstrou:
#   - Simulação de uma série temporal com tendência, sazonalidade e ruído.
#   - Análise exploratória dos dados, com decomposição, ACF e PACF.
#   - Ajuste de um modelo ARIMA e previsão para os próximos 12 meses.
#   - Ajuste de um modelo de regressão linear com variáveis dummy sazonais.
#   - Comparação gráfica entre as previsões dos modelos ARIMA e LM.
#   - Análise dos resíduos do modelo ARIMA para identificar possíveis padrões.
#
# Expansões possíveis:
#   - Inclusão de validação cruzada e medidas adicionais de desempenho.
#   - Uso de pacotes especializados para séries temporais (ex: forecast).
#   - Desenvolvimento de aplicativos interativos (Shiny) e automatização com RMarkdown.
#
# FIM DO PROJETO
