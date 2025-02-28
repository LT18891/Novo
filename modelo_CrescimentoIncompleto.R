if (!require("vars")) install.packages("vars")
if (!require("forecast")) install.packages("forecast")
if (!require("ggplot2")) install.packages("ggplot2")
if (!require("urca")) install.packages("urca")
if (!require("tseries")) install.packages("tseries")
if (!require("tsDyn")) install.packages("tsDyn")
if (!require("strucchange")) install.packages("strucchange")
if (!require("rugarch")) install.packages("rugarch")
if (!require("rmgarch")) install.packages("rmgarch")

library(vars)
library(forecast)
library(ggplot2)
library(urca)
library(tseries)
library(tsDyn)
library(strucchange)
library(rugarch)
library(rmgarch)

#--------------------------------------------------------------------
# 1. Geração de dados simulados
#--------------------------------------------------------------------
set.seed(123)
anos <- 1990:2020
n <- length(anos)

# Para aumentar a chance de cointegração, simulamos duas variáveis com tendência (integradas)
PIB          <- cumsum(rnorm(n, mean = 2, sd = 1)) + 100       # PIB (tendência acumulada)
Investimento <- cumsum(rnorm(n, mean = 0.2, sd = 0.1)) + 50      # Investimento (tendência)
Exportacao   <- cumsum(rnorm(n, mean = 0.15, sd = 0.08)) + 30     # Exportações (tendência)
Consumo      <- cumsum(rnorm(n, mean = 1.5, sd = 0.8)) + 50       # Consumo das Famílias
TaxaJuros    <- rnorm(n, mean = 2.5, sd = 0.3)                   # Taxa de Juros (geralmente estacionária)

dados <- data.frame(
  Ano = anos,
  PIB = PIB,
  Investimento = Investimento,
  Exportacao = Exportacao,
  Consumo = Consumo,
  TaxaJuros = TaxaJuros
)

# Converter os dados (exceto a coluna 'Ano') em uma série temporal multivariada
serie_temporal <- ts(dados[ , -1], start = anos[1], frequency = 1)

#--------------------------------------------------------------------
# 2. Teste de Estacionariedade (ADF) para cada variável
#--------------------------------------------------------------------
cat("Testes de estacionariedade (p-valores do ADF):\n")
cat("PIB:", adf.test(PIB)$p.value, "\n")
cat("Investimento:", adf.test(Investimento)$p.value, "\n")
cat("Exportacao:", adf.test(Exportacao)$p.value, "\n")
cat("Consumo:", adf.test(Consumo)$p.value, "\n")
cat("TaxaJuros:", adf.test(TaxaJuros)$p.value, "\n\n")

#--------------------------------------------------------------------
# 3. Teste de Cointegração (Johansen) para as variáveis com tendência
#    (Excluímos TaxaJuros por ser estacionária)
#--------------------------------------------------------------------
variaveis_tendencia <- serie_temporal[, c("PIB", "Investimento", "Exportacao", "Consumo")]
teste_cointegracao <- ca.jo(variaveis_tendencia, type = "trace", ecdet = "const", K = 2)
summary(teste_cointegracao)

#--------------------------------------------------------------------
# 4. Estimação do Modelo VECM (se houver cointegração)
#    Utilizando r = 1 (por exemplo) e defasagem de 2 períodos.
#--------------------------------------------------------------------
# Se o teste indicar pelo menos uma relação de cointegração, usamos VECM.
modelo_vecm <- VECM(variaveis_tendencia, lag = 2, r = 1, estim = "ML")
summary(modelo_vecm)

# Para facilitar a previsão, convertemos o VECM em representação VAR:
modelo_var <- vec2var(teste_cointegracao, r = 1)

#--------------------------------------------------------------------
# 5. Previsão para os próximos 10 anos com o modelo VAR
#--------------------------------------------------------------------
previsao_var <- predict(modelo_var, n.ahead = 10)

# Extraindo a previsão do PIB
previsao_pib <- previsao_var$fcst$PIB

# Organizar dados para plotagem
anos_previsao <- (max(anos) + 1):(max(anos) + 10)
df_previsao <- data.frame(
  Ano = anos_previsao,
  PIB_previsto = previsao_pib[, "fcst"],
  Limite_inferior = previsao_pib[, "lower"],
  Limite_superior = previsao_pib[, "upper"]
)

# Plot da previsão do PIB
ggplot(df_previsao, aes(x = Ano, y = PIB_previsto)) +
  geom_line(color = "blue", size = 1) +
  geom_ribbon(aes(ymin = Limite_inferior, ymax = Limite_superior), alpha = 0.2, fill = "blue") +
  labs(title = "Previsão do PIB para os Próximos 10 Anos",
       x = "Ano",
       y = "PIB") +
  theme_minimal()

#--------------------------------------------------------------------
# 6. Análise de Funções de Impulso-Resposta e Decomposição da Variância
#--------------------------------------------------------------------
# IRF: efeito do Investimento sobre o PIB
irf_investimento <- irf(modelo_var, impulse = "Investimento", response = "PIB", n.ahead = 10, boot = TRUE)
plot(irf_investimento)

# Decomposição da Variância (fevd)
fevd_resultado <- fevd(modelo_var, n.ahead = 10)
print(fevd_resultado)

#--------------------------------------------------------------------
# 7. Detecção de Pontos de Quebra Estrutural na Série do PIB
#--------------------------------------------------------------------
bp_pib <- breakpoints(PIB ~ 1)
summary(bp_pib)
plot(bp_pib)

#--------------------------------------------------------------------
# 8. Modelagem de Heterocedasticidade com um Modelo Multivariado GARCH (DCC)
#--------------------------------------------------------------------
# Especificação univariada para cada série (usaremos as quatro variáveis com tendência)
spec_univariada <- ugarchspec(
  variance.model = list(model = "sGARCH", garchOrder = c(1, 1)),
  mean.model = list(armaOrder = c(1, 1), include.mean = TRUE),
  distribution.model = "norm"
)

# Replicar a especificação para cada série (4 variáveis)
spec_multivariada <- multispec(replicate(4, spec_univariada))

# Especificação DCC
dcc_spec <- dccspec(uspec = spec_multivariada, dccOrder = c(1, 1), distribution = "mvnorm")

# Ajustar o modelo DCC usando as variáveis: PIB, Investimento, Exportacao e Consumo
dcc_fit <- dccfit(dcc_spec, data = variaveis_tendencia)
print(dcc_fit)

#--------------------------------------------------------------------
# Fim do modelo 
#--------------------------------------------------------------------

