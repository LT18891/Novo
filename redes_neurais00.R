if (!require("neuralnet")) {
  install.packages("neuralnet")
  library(neuralnet)
}
if (!require("ggplot2")) {
  install.packages("ggplot2")
  library(ggplot2)
}

set.seed(123)
n <- 200
PIB <- runif(n, 50, 150)
Inflacao <- runif(n, 1, 10)
Taxa_Juros <- runif(n, 0.5, 5)
erro <- rnorm(n, 0, 1)
Crescimento <- 0.3 * PIB - 0.5 * Inflacao - 0.2 * Taxa_Juros + erro
dados <- data.frame(PIB, Inflacao, Taxa_Juros, Crescimento)

maxs <- apply(dados, 2, max)
mins <- apply(dados, 2, min)
dados_norm <- as.data.frame(scale(dados, center = mins, scale = maxs - mins))

rede <- neuralnet(Crescimento ~ PIB + Inflacao + Taxa_Juros, dados_norm, hidden = 50, linear.output = TRUE)
plot(rede, rep = "best")

pred <- compute(rede, dados_norm[, c("PIB", "Inflacao", "Taxa_Juros")])
dados$Predito <- pred$net.result * (max(dados$Crescimento) - min(dados$Crescimento)) + min(dados$Crescimento)

ggplot(dados, aes(x = Crescimento, y = Predito)) +
  geom_point(color = "blue", size = 2) +
  geom_abline(slope = 1, intercept = 0, color = "red", linetype = "dashed") +
  labs(title = "Comparação: Crescimento Real vs Predito",
       x = "Crescimento Real", y = "Crescimento Predito") +
  theme_minimal()

