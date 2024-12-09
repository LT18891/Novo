###############################################################
# Modelo Avançado de Previsão da Taxa de Câmbio USD/BRL
# Utilizando Teoria Avançada de Probabilidade e um Modelo
# Bayesiano Estrutural de Séries Temporais (BSTS) em R
#
# Este código demonstra um fluxo completo:
# 1. Carregamento de dados históricos da taxa de câmbio USD/BRL.
# 2. Pré-processamento e análise exploratória.
# 3. Configuração de um modelo Bayesiano Estrutural de Série Temporal,
#    integrando componentes latentes (tendência, sazonalidade, regressões).
# 4. Ajuste do modelo via MCMC (Markov Chain Monte Carlo).
# 5. Verificação do ajuste e diagnóstico da convergência.
# 6. Previsão futura da taxa de câmbio com intervalos de confiança.
# 7. Interpretação dos resultados.
#
# Notas:
# - O modelo BSTS utiliza fundamentos de probabilidade avançada, modelagem
#   hierárquica e MCMC, incorporando incerteza sobre parâmetros e componentes.
# - Variáveis e comentários em Português.
# - Requer as bibliotecas: bsts, xts, lubridate, ggplot2, coda.
#
# Observação: Este é um exemplo hipotético e pode requerer ajustes de acordo
# com a fonte de dados real. Aqui, assumimos que temos dados diários da série.
###############################################################

# Limpando o ambiente
rm(list=ls()); gc()

# Instalar pacotes se necessário:
# install.packages(c("bsts", "xts", "lubridate", "ggplot2", "coda"))

library(bsts)
library(xts)
library(lubridate)
library(ggplot2)
library(coda)

##############################################
# 1. Carregamento e Preparação dos Dados
##############################################

# Suponha que você possua um arquivo CSV com a série histórica do dólar em relação ao real.
# O arquivo deve conter pelo menos duas colunas: Data e Preco.
# Formato:
# Data,Preco
# 2020-01-01,4.03
# 2020-01-02,4.05
# ...
#
# Aqui, simularemos dados aleatórios para efeito de demonstração.
# Em um caso real, ajuste o caminho do arquivo e utilize os dados reais.

set.seed(123)

# Cria uma sequência de datas diárias por 3 anos (por exemplo)
datas <- seq.Date(from=as.Date("2020-01-01"),
                  to=as.Date("2022-12-31"),
                  by="day")

# Simular uma série de câmbio com tendência suave, sazonalidade semanal (pequena)
# e ruído estocástico. Suponha que o câmbio em 2020 começou em ~4.00 BRL/USD
# e teve uma leve tendência de alta com volatilidade.
tamanho <- length(datas)
tendencia_base <- seq(from=4.0, to=5.5, length.out = tamanho)
# Sazonalidade semanal: pequenas flutuações, por ex. mais alto segundas e sextas
sazonalidade_semanal <- 0.05*sin(2*pi*(1:tamanho)/7)
# Ruído aleatório
ruido <- rnorm(tamanho, mean=0, sd=0.05)

precos <- tendencia_base + sazonalidade_semanal + ruido

# Criar um data.frame
dados <- data.frame(Data = datas,
                    Preco = precos)

# Converter para xts
dados_xts <- xts(dados$Preco, order.by=dados$Data)

##############################################
# 2. Análise Exploratória
##############################################

# Plotagem simples da série
ggplot(dados, aes(x=Data, y=Preco)) +
  geom_line(color="blue") +
  ggtitle("Série Histórica do Preço do Dólar (USD/BRL)") +
  xlab("Data") + ylab("Preço (BRL)") +
  theme_minimal()

# Estatísticas básicas
summary(dados$Preco)
# Podemos observar média, min, max etc.

##############################################
# 3. Construção do Modelo BSTS
##############################################
#
# O BSTS (Bayesian Structural Time Series) é um modelo bayesiano que decompõe a série
# em componentes: Tendência, Sazonalidade, Regressões (opcionais), e um componente
# de erro. Ele utiliza MCMC para estimar a distribuição posterior dos parâmetros.
#
# Componentes:
# - Tendência local (Local Level ou Random Walk)
# - Sazonalidade semanal (7 dias) - caso haja padrão sazonal
# - Podemos adicionar regressões externas (ex: indicadores econômicos)
#   Para este exemplo, não adicionaremos regressões exógenas, mas isso é possível.
#
# O BSTS fornecerá previsões com intervalos de credibilidade baseados na distribuição
# posterior dos parâmetros.

# Definir a sazonalidade semanal (periodo de 7 dias)
# Notar que a série é diária, portanto período = 7
componente_sazonal <- list()
componente_sazonal <- AddSeasonal(state.specification = componente_sazonal,
                                  y = dados_xts,
                                  nseasons = 7) # sazonalidade semanal

# Adicionar tendência local (Local Linear Trend)
componente_tendencia <- AddLocalLinearTrend(state.specification = componente_sazonal,
                                            y = dados_xts)

# Modelo final de especificação do estado
modelo_especificacao <- componente_tendencia

##############################################
# 4. Ajuste do Modelo via MCMC
##############################################
#
# O ajuste do BSTS é feito via MCMC, e nós definimos o número de iterações.
# Mais iterações = melhor aproximação do posterior, porém mais custo computacional.
# Aqui usamos um número relativamente pequeno para demonstração, mas no real
# deve-se usar pelo menos algumas milhares de iterações e descartar um "burn-in".

iteracoes_mcmc <- 2000   # idealmente mais alto (e.g. 5000, 10000)
modelo_bsts <- bsts(dados_xts,
                    state.specification = modelo_especificacao,
                    niter = iteracoes_mcmc,
                    seed = 123)

##############################################
# 5. Diagnóstico e Verificação da Convergência
##############################################

# Podemos examinar as cadeias MCMC
# Este modelo gera uma grande quantidade de parâmetros. Vamos olhar, por exemplo,
# a evolução da variância do erro.
plot(modelo_bsts, "coef") # se houver coeficientes de regressão
plot(modelo_bsts, "sigma.obs") # evolução da incerteza do erro de observação

# Resumo do modelo
summary(modelo_bsts)

# Extração das cadeias para diagnóstico
cadenas_sigma <- MCMC(modelo_bsts, "sigma.obs")
# Usar o pacote 'coda' para diagnosticar convergência
gelman.diag(cadenas_sigma)

# Se o diagnóstico estiver satisfatório (Rhat próximo de 1), passamos adiante.

##############################################
# 6. Previsão Futura
##############################################
#
# Suponhamos que queremos prever os próximos 30 dias do câmbio.
# O BSTS gera predições baseadas nas distribuições posteriores dos parâmetros.

periodo_previsao <- 30
previsao <- predict(modelo_bsts, horizon = periodo_previsao, burn = 500) 
# burn = 500 descarta as primeiras 500 iterações para estabilizar a convergência

# A previsão retorna valores esperados e intervalos de credibilidade
previsao_mediana <- previsao$mean
previsao_intervalo <- t(apply(previsao$distribution, 2, quantile, c(0.025, 0.975)))

# Criar data.frame para plotar a previsão
datas_futuras <- seq(from = tail(dados$Data,1) + 1,
                     length.out = periodo_previsao,
                     by="day")

df_previsao <- data.frame(
  Data = datas_futuras,
  Preco_Previsto = previsao_mediana,
  LI_95 = previsao_intervalo[,1],
  LS_95 = previsao_intervalo[,2]
)

##############################################
# 7. Visualização das Previsões
##############################################

# Combinar dados históricos e previsão
dados_completo <- rbind(
  data.frame(Data = dados$Data, Preco = dados$Preco, Tipo="Histórico"),
  data.frame(Data = df_previsao$Data, Preco = df_previsao$Preco_Previsto, Tipo="Previsão")
)

ggplot() +
  geom_line(data = subset(dados_completo, Tipo=="Histórico"), aes(x=Data, y=Preco), color="blue") +
  geom_line(data = subset(dados_completo, Tipo=="Previsão"), aes(x=Data, y=Preco), color="red", linetype="dashed") +
  geom_ribbon(data = df_previsao, aes(x=Data, ymin=LI_95, ymax=LS_95), alpha=0.2, fill="red") +
  ggtitle("Previsão do Preço do Dólar (USD/BRL) com BSTS") +
  xlab("Data") + ylab("Preço (BRL)") +
  theme_minimal()

##############################################
# Interpretação:
# - A linha azul representa o histórico da taxa de câmbio.
# - A linha vermelha tracejada representa a mediana das previsões futuras.
# - A faixa vermelha (intervalo de confiança) reflete a incerteza da previsão.
#
# Este modelo BSTS, por ser Bayesianamente estruturado, incorpora toda a incerteza
# sobre parâmetros e componentes não observados, produzindo intervalos de credibilidade
# diretamente da distribuição posterior. Assim, temos um arcabouço avançado de
# probabilidade e inferência bayesiana, indo além de simples modelos ARIMA clássicos.
#
# Ajustes possíveis:
# - Aumentar número de iterações MCMC.
# - Testar outros componentes (ex: regressões com variáveis macroeconômicas).
# - Ajustar a sazonalidade, adicionar efeitos determinísticos ou tendências mais complexas.
#
###############################################################
