# ----- Configuração Inicial e Instalação dos Pacotes Necessários -----

# Se necessário, instala os pacotes
if(!require(forecast)) install.packages("forecast", dependencies = TRUE)
if(!require(ggplot2)) install.packages("ggplot2", dependencies = TRUE)
if(!require(tseries)) install.packages("tseries", dependencies = TRUE)
if(!require(gridExtra)) install.packages("gridExtra", dependencies = TRUE)

library(forecast)
library(ggplot2)
library(tseries)
library(gridExtra)

# ----- Fechar Dispositivos Gráficos Abertos e Ajustar Margens -----

# Fecha qualquer dispositivo gráfico aberto (útil para limpar a área de plotagem)
if(!is.null(dev.list())) dev.off()

# Ajusta as margens para evitar o erro "figure margins too large"
par(mar = c(2, 2, 2, 2))

# ----- 1. Simulação dos Dados -----

set.seed(123)

n <- 120  # 120 meses, de janeiro de 2010 a dezembro de 2019
datas <- seq.Date(from = as.Date("2010-01-01"), by = "month", length.out = n)

# Variáveis exógenas (nomes em português):
inflacao        <- round(rnorm(n, mean = 0.5, sd = 0.1), 2)    # taxa de inflação
producao_opep   <- round(rnorm(n, mean = 100, sd = 10), 1)      # produção da OPEP
consumo_mundial <- round(rnorm(n, mean = 300, sd = 20), 1)       # consumo mundial
estoques        <- round(rnorm(n, mean = 50, sd = 5), 1)         # estoques

# Componente sazonal (variação mensal, utilizando função seno)
mes     <- as.numeric(format(datas, "%m"))
sazonal <- 5 * sin(2 * pi * mes / 12)

# Simulação do preço do petróleo com influência das variáveis exógenas e do efeito sazonal
preco_petroleo <- round(50 + 0.5 * inflacao +
                          0.3 * producao_opep +
                          0.2 * consumo_mundial -
                          0.4 * estoques +
                          sazonal + rnorm(n, 0, 1), 2)

# Criação do DataFrame com todos os dados simulados
dados <- data.frame(
  Data            = datas, 
  preco_petroleo  = preco_petroleo,
  inflacao        = inflacao,
  producao_opep   = producao_opep,
  consumo_mundial = consumo_mundial,
  estoques        = estoques
)

# Visualiza as primeiras linhas dos dados
print(head(dados))

# ----- 2. Preparação dos Dados para Modelagem -----

# Converte a série do preço do petróleo em objeto ts (mensal: frequência 12)
ts_preco_petroleo <- ts(dados$preco_petroleo, start = c(2010, 1), frequency = 12)

# Criação da matriz com as variáveis exógenas
xreg <- cbind(
  inflacao       = dados$inflacao,
  producao_opep  = dados$producao_opep,
  consumo_mundial= dados$consumo_mundial,
  estoques       = dados$estoques
)

# ----- 3. Ajuste do Modelo SARIMAX -----

# Ajusta o modelo SARIMAX utilizando a função auto.arima() (com componentes sazonais e variáveis exógenas)
modelo_sarimax <- auto.arima(ts_preco_petroleo, xreg = xreg, seasonal = TRUE)

# Exibe o resumo do modelo
summary(modelo_sarimax)

# ----- 4. Diagnóstico dos Resíduos -----

# Ajusta a área de plotagem para múltiplos gráficos e garante margens reduzidas
par(mfrow = c(2,2), mar = c(2, 2, 2, 2))

# Gráfico dos resíduos ao longo do tempo
plot(modelo_sarimax$residuals, main = "Resíduos do Modelo", ylab = "Resíduos", xlab = "Tempo")
abline(h = 0, col = "red")

# QQ-plot dos resíduos
qqnorm(modelo_sarimax$residuals, main = "QQ-Plot dos Resíduos")
qqline(modelo_sarimax$residuals, col = "blue")

# ACF dos resíduos
acf(modelo_sarimax$residuals, main = "ACF dos Resíduos")

# PACF dos resíduos
pacf(modelo_sarimax$residuals, main = "PACF dos Resíduos")

# Retorna a área de plotagem para um único gráfico
par(mfrow = c(1,1))

# ----- 5. Previsão para 12 Meses à Frente -----

h <- 12  # Horizonte de previsão: 12 meses

# Define os valores futuros para cada variável exógena (mantendo os últimos valores observados)
inflacao_fut        <- rep(tail(inflacao, 1), h)
producao_opep_fut   <- rep(tail(producao_opep, 1), h)
consumo_mundial_fut <- rep(tail(consumo_mundial, 1), h)
estoques_fut        <- rep(tail(estoques, 1), h)

xreg_fut <- cbind(
  inflacao       = inflacao_fut,
  producao_opep  = producao_opep_fut,
  consumo_mundial= consumo_mundial_fut,
  estoques       = estoques_fut
)

# Gera a previsão
previsao <- forecast(modelo_sarimax, xreg = xreg_fut, h = h)

# ----- 6. Visualização dos Resultados -----

# Gráfico da previsão utilizando autoplot (baseado em ggplot2)
plot_previsao <- autoplot(previsao) +
  ggtitle("Previsão do Preço do Petróleo com SARIMAX\nAutor: Luiz Tiago Wilcke") +
  xlab("Ano") +
  ylab("Preço do Petróleo") +
  theme_minimal()
print(plot_previsao)

# Exibe a previsão numérica com maior precisão
print(previsao, digits = 10)

# Gráfico adicional: Série histórica e previsão (intervalo de confiança)

# Gráfico da série histórica do preço do petróleo
p1 <- ggplot(dados, aes(x = Data, y = preco_petroleo)) +
  geom_line(color = "blue") +
  ggtitle("Série Histórica do Preço do Petróleo") +
  xlab("Data") + 
  ylab("Preço do Petróleo") +
  theme_minimal()

# Cria um DataFrame para os dados de previsão
datas_fut <- seq.Date(from = as.Date("2020-01-01"), by = "month", length.out = h)
prev_df <- data.frame(
  Data           = datas_fut, 
  Previsao       = as.numeric(previsao$mean),
  LimiteInferior = as.numeric(previsao$lower[, 2]),
  LimiteSuperior = as.numeric(previsao$upper[, 2])
)

# Gráfico da previsão com os intervalos de confiança
p2 <- ggplot(prev_df, aes(x = Data, y = Previsao)) +
  geom_line(color = "darkgreen") +
  geom_ribbon(aes(ymin = LimiteInferior, ymax = LimiteSuperior), fill = "grey80", alpha = 0.5) +
  ggtitle("Previsão com Intervalos de Confiança (12 Meses)") +
  xlab("Data") +
  ylab("Preço do Petróleo Previsto") +
  theme_minimal()

# Exibe os dois gráficos empilhados
grid.arrange(p1, p2, ncol = 1)
