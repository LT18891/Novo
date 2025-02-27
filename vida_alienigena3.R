# Autor: Luiz Tiago Wilcke
# Data: 27/02/2025
# Descrição: Modelo estatístico avançado para prever a quantidade de planetas com vida na Galáxia
# utilizando simulação Monte Carlo para incorporar incertezas dos parâmetros do modelo.

set.seed(123)

n_simulacoes <- 100000

media_log_estrelas <- log(1e11)
desvio_log_estrelas <- 0.2
n_estrelas <- rlnorm(n_simulacoes, meanlog = media_log_estrelas, sdlog = desvio_log_estrelas)

forma1_fp <- 80
forma2_fp <- 20
fracao_estrelas_com_planetas <- rbeta(n_simulacoes, shape1 = forma1_fp, shape2 = forma2_fp)

forma_ne <- 2
escala_ne <- 0.25
numero_planetas_habitaveis <- rgamma(n_simulacoes, shape = forma_ne, scale = escala_ne)

forma1_fl <- 1
forma2_fl <- 4
fracao_planetas_com_vida <- rbeta(n_simulacoes, shape1 = forma1_fl, shape2 = forma2_fl)

n_planetas_com_vida <- n_estrelas * fracao_estrelas_com_planetas * numero_planetas_habitaveis * fracao_planetas_com_vida

resumo_planetas <- summary(n_planetas_com_vida)
media_planetas <- mean(n_planetas_com_vida)
mediana_planetas <- median(n_planetas_com_vida)
desvio_planetas <- sd(n_planetas_com_vida)

print(resumo_planetas)
cat("Média de planetas com vida:", media_planetas, "\n")
cat("Mediana de planetas com vida:", mediana_planetas, "\n")
cat("Desvio padrão:", desvio_planetas, "\n")

par(mfrow = c(2,2))
hist(n_planetas_com_vida, breaks = 50, col = "skyblue",
     main = "Histograma: Planetas com Vida",
     xlab = "Número de Planetas com Vida")
plot(density(n_planetas_com_vida), main = "Densidade: Planetas com Vida",
     xlab = "Número de Planetas com Vida", col = "red", lwd = 2)
boxplot(n_planetas_com_vida, main = "Boxplot: Planetas com Vida",
        ylab = "Número de Planetas com Vida", col = "lightgreen")
plot(ecdf(n_planetas_com_vida), main = "Função de Distribuição Acumulada",
     xlab = "Número de Planetas com Vida", ylab = "Probabilidade")
par(mfrow = c(1,1))

