# Instalar e carregar pacotes necessários (caso não estejam instalados)
if (!require(ggplot2)) {
  install.packages("ggplot2")
  library(ggplot2)
}

# Parâmetros do Modelo (Movimento Geométrico Browniano)
taxa_media    <- 0.05      # Taxa média de retorno anual (5%)
volatilidade  <- 0.2       # Volatilidade anual (20%)
preco_inicial <- 5.00      # Preço inicial do dólar em reais

# Configurações da simulação
tempo_total <- 1         # Período de simulação em anos (1 ano)
num_passos  <- 252       # Número de passos (por exemplo, dias úteis no ano)
dt          <- tempo_total / num_passos  # Intervalo de tempo em anos

# Vetor para armazenar os preços simulados
precos <- numeric(num_passos + 1)
precos[1] <- preco_inicial

# Simulação usando o método de Euler-Maruyama para a equação diferencial estocástica:
# dS = taxa_media * S * dt + volatilidade * S * dW
set.seed(123)  # para reprodutibilidade
for (i in 2:(num_passos + 1)) {
  dW <- rnorm(1, mean = 0, sd = sqrt(dt))  # incremento do processo de Wiener
  precos[i] <- precos[i - 1] * exp((taxa_media - 0.5 * volatilidade^2) * dt +
                                     volatilidade * dW)
}

# Arredondar os preços para 3 dígitos de precisão
precos_arredondados <- round(precos, 3)

# Exibir os 10 primeiros valores simulados
cat("Primeiros 10 valores simulados do preço do dólar (R$):\n")
print(precos_arredondados[1:10])

# Criar um data frame para a plotagem
dias <- 0:num_passos
df_simulacao <- data.frame(Dia = dias, Preco = precos_arredondados)

# Plotar a trajetória simulada do preço do dólar
grafico <- ggplot(df_simulacao, aes(x = Dia, y = Preco)) +
  geom_line(color = "blue", size = 1) +
  labs(title = "Simulação do Preço do Dólar (R$) via EDE",
       x = "Dias",
       y = "Preço do Dólar (R$)") +
  theme_minimal()

print(grafico)

# Exibir o preço final previsto (após 1 ano) com 3 dígitos de precisão
preco_final <- precos_arredondados[length(precos_arredondados)]
cat("Preço final previsto do dólar (R$) após 1 ano:", preco_final, "\n")



