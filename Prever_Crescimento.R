# Rede neural para prever o crescimento econômico

if (!require(neuralnet)) install.packages("neuralnet", dependencies = TRUE)
if (!require(ggplot2)) install.packages("ggplot2", dependencies = TRUE)
if (!require(caret)) install.packages("caret", dependencies = TRUE)
library(neuralnet)
library(ggplot2)
library(caret)

set.seed(123)
n <- 200
dados <- data.frame(
  PIB = runif(n, 100, 500),
  Inflacao = runif(n, 0, 10),
  TaxaJuros = runif(n, 0, 15),
  Investimento = runif(n, 20, 100),
  Exportacoes = runif(n, 10, 80)
)
dados$Crescimento <- with(dados, 0.05 * PIB - 0.3 * Inflacao - 
                            0.2 * TaxaJuros + 0.4 * Investimento + 
                            0.3 * Exportacoes + rnorm(n, mean = 0, sd = 10))
head(dados)

maxs <- apply(dados, 2, max)
mins <- apply(dados, 2, min)
dados_norm <- as.data.frame(scale(dados, center = mins, scale = maxs - mins))

formula_modelo <- as.formula("Crescimento ~ PIB + Inflacao + TaxaJuros + Investimento + Exportacoes")
lista_redes <- list()
estruturas <- list(c(3), c(4), c(5), c(3,2), c(4,2), c(5,3), c(3,3), c(4,4))

for(i in 1:20) {
  estrutura_escolhida <- estruturas[[sample(1:length(estruturas), 1)]]
  cat("Treinando a rede neural", i, "com estrutura:", paste(estrutura_escolhida, collapse = "-"), "\n")
  rede <- neuralnet(formula_modelo, data = dados_norm, hidden = estrutura_escolhida, 
                    linear.output = TRUE, stepmax = 1e6)
  lista_redes[[i]] <- rede
  if(.Platform$OS.type == "windows"){
    windows()
  } else {
    X11()
  }
  plot(rede, main = paste("Rede Neural", i, "\nEstrutura:", paste(estrutura_escolhida, collapse = "-")))
  Sys.sleep(1)
}

cat("Treinamento concluído. Foram geradas 20 redes neurais e as imagens foram abertas em janelas.\n")

erros_RMSE <- numeric(20)
for(i in 1:20){
  rede <- lista_redes[[i]]
  resultados <- compute(rede, dados_norm[, c("PIB", "Inflacao", "TaxaJuros", "Investimento", "Exportacoes")])
  predicoes <- resultados$net.result
  rmse <- sqrt(mean((dados_norm$Crescimento - predicoes)^2))
  erros_RMSE[i] <- rmse
}

df_erros <- data.frame(Modelo = 1:20, RMSE = erros_RMSE)
grafico_rmse <- ggplot(df_erros, aes(x = Modelo, y = RMSE)) +
  geom_line() +
  geom_point(size = 3) +
  ggtitle("Erro RMSE de cada Rede Neural") +
  xlab("Modelo") +
  ylab("RMSE") +
  theme_minimal()
print(grafico_rmse)

save(lista_redes, file = "lista_redes.RData")
cat("Processo completo: 20 redes neurais treinadas e os modelos avaliados via RMSE.\n")
