# Autor: Luiz Tiago Wilcke
# Data: 27/02/2025
# Descrição: Modelo estatístico para prever o desemprego utilizando regressão linear múltipla
# com simulação de dados econômicos, ajuste do modelo, previsão e plotagem dos resultados.

# Definir semente para reprodutibilidade
set.seed(123)

# Número de observações (por exemplo, meses ou trimestres)
n_obs <- 200

# Criar vetor de tempo
tempo <- 1:n_obs

# Simular variáveis econômicas 
PIB <- rnorm(n_obs, mean = 100, sd = 10)                # Produto Interno Bruto
taxa_inflacao <- rnorm(n_obs, mean = 3, sd = 1)           # Taxa de inflação (em %)
taxa_juros <- rnorm(n_obs, mean = 5, sd = 1.5)            # Taxa de juros (em %)
investimento <- rnorm(n_obs, mean = 50, sd = 5)           # Nível de investimento
exportacoes <- rnorm(n_obs, mean = 30, sd = 4)            # Valor das exportações

# Simular a taxa de desemprego (em %) como função das variáveis econômicas e de um erro aleatório
erro <- rnorm(n_obs, mean = 0, sd = 2)
desemprego <- 15 - 0.08 * PIB + 1.5 * taxa_inflacao + 0.5 * taxa_juros -
  0.2 * investimento - 0.1 * exportacoes + erro

# Criar um data frame com os dados simulados
dados <- data.frame(tempo = tempo,
                    PIB = PIB,
                    taxa_inflacao = taxa_inflacao,
                    taxa_juros = taxa_juros,
                    investimento = investimento,
                    exportacoes = exportacoes,
                    desemprego = desemprego)

# Dividir os dados em conjunto de treinamento (80%) e teste (20%)
indice_treinamento <- 1:round(0.8 * n_obs)
dados_treinamento <- dados[indice_treinamento, ]
dados_teste <- dados[-indice_treinamento, ]

# Ajustar o modelo de regressão linear múltipla para prever o desemprego
modelo <- lm(desemprego ~ PIB + taxa_inflacao + taxa_juros + investimento + exportacoes,
             data = dados_treinamento)

# Exibir o resumo do modelo
print(summary(modelo))

# Fazer previsões para o conjunto de teste
previsoes <- predict(modelo, newdata = dados_teste)

# Calcular o erro médio absoluto das previsões
erro_medio <- mean(abs(dados_teste$desemprego - previsoes))
cat("Erro médio absoluto:", erro_medio, "\n")

# Plotagem: Comparação entre desemprego real e previsto ao longo do tempo (conjunto de teste)
plot(dados_teste$tempo, dados_teste$desemprego, type = "l", col = "blue", lwd = 2,
     xlab = "Tempo", ylab = "Taxa de Desemprego (%)",
     main = "Desemprego Real vs Previsto")
lines(dados_teste$tempo, previsoes, col = "red", lwd = 2)
legend("topright", legend = c("Real", "Previsto"), col = c("blue", "red"), lty = 1, lwd = 2)

# Plotagem dos resíduos do modelo (conjunto de teste)
residuos <- dados_teste$desemprego - previsoes

par(mfrow = c(1, 2))
plot(dados_teste$tempo, residuos, type = "o", col = "purple", xlab = "Tempo",
     ylab = "Resíduos", main = "Resíduos do Modelo")
hist(residuos, col = "gray", border = "white", main = "Histograma dos Resíduos",
     xlab = "Resíduos")
par(mfrow = c(1, 1))

