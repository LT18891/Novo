if(!require(ggplot2)) install.packages("ggplot2")
if(!require(latex2exp)) install.packages("latex2exp")
library(ggplot2)
library(latex2exp)
n_simulacoes <- 10000
set.seed(123)
taxa_estelar <- runif(n_simulacoes, min = 1, max = 3)
fracao_planetas <- runif(n_simulacoes, min = 0.5, max = 1)
num_planetas_habitaveis <- runif(n_simulacoes, min = 0.1, max = 2)
fracao_vida <- runif(n_simulacoes, min = 0.01, max = 1)
fracao_inteligencia <- runif(n_simulacoes, min = 0.001, max = 1)
fracao_comunicacao <- runif(n_simulacoes, min = 0.001, max = 1)
tempo_sinal <- runif(n_simulacoes, min = 100, max = 10000)
N <- taxa_estelar * fracao_planetas * num_planetas_habitaveis * fracao_vida * 
  fracao_inteligencia * fracao_comunicacao * tempo_sinal
prob_existencia <- mean(N >= 1)
df <- data.frame(N = N)
p1 <- ggplot(df, aes(x = N)) +
  geom_histogram(bins = 50, fill = "skyblue", color = "black", alpha = 0.7) +
  scale_x_continuous(trans = 'log10') +
  labs(title = "Civilizações Detectáveis na Galáxia",
       subtitle = paste("P(>=1) =", round(prob_existencia, 4)),
       x = "N (Escala Log)", y = "Frequência") +
  theme_minimal()
p1 <- p1 + annotate("text", x = Inf, y = Inf,
                    label = TeX("$N = R^* \\times f_p \\times n_e \\times f_l \\times f_i \\times f_c \\times L$"),
                    hjust = 1.1, vjust = 2, size = 5, color = "darkred")
summary_stats <- summary(N)
mediana <- median(N)
media_N <- mean(N)
dp_N <- sd(N)
df_stats <- data.frame(Estatistica = c("Mínimo", "1º Quartil", "Mediana", "Média", "3º Quartil", "Máximo", "Desvio Padrão"),
                       Valor = c(summary_stats[1], summary_stats[2], mediana, media_N, summary_stats[5], summary_stats[6], dp_N))
p2 <- ggplot(df_stats, aes(x = Estatistica, y = Valor)) +
  geom_bar(stat = "identity", fill = "tomato", color = "black", alpha = 0.8) +
  labs(title = "Estatísticas de N", x = "Estatística", y = "Valor") +
  theme_minimal()
densidade <- density(N)
df_density <- data.frame(x = densidade$x, y = densidade$y)
p3 <- ggplot(df_density, aes(x = x, y = y)) +
  geom_line(color = "blue", size = 1) +
  scale_x_continuous(trans = 'log10') +
  labs(title = "Densidade de N", x = "N (Escala Log)", y = "Densidade") +
  theme_minimal()
quantis <- quantile(N, probs = seq(0,1,0.1))
df_quantis <- data.frame(Prob = seq(0,1,0.1), Valor = quantis)
p4 <- ggplot(df_quantis, aes(x = Prob, y = Valor)) +
  geom_point(color = "purple", size = 3) +
  geom_line(color = "purple", size = 1) +
  scale_y_continuous(trans = 'log10') +
  labs(title = "Quantis de N", x = "Probabilidade", y = "N (Escala Log)") +
  theme_minimal()
grupo1 <- runif(n_simulacoes, min = 1, max = 3)
grupo2 <- runif(n_simulacoes, min = 0.5, max = 1)
grupo3 <- runif(n_simulacoes, min = 0.1, max = 2)
grupo4 <- runif(n_simulacoes, min = 0.01, max = 1)
grupo5 <- runif(n_simulacoes, min = 0.001, max = 1)
grupo6 <- runif(n_simulacoes, min = 0.001, max = 1)
grupo7 <- runif(n_simulacoes, min = 100, max = 10000)
N2 <- grupo1 * grupo2 * grupo3 * grupo4 * grupo5 * grupo6 * grupo7
df2 <- data.frame(N = N2, Grupo = "Conjunto 2")
df1 <- data.frame(N = N, Grupo = "Conjunto 1")
df_total <- rbind(df1, df2)
p5 <- ggplot(df_total, aes(x = N, fill = Grupo)) +
  geom_histogram(bins = 50, alpha = 0.6, position = "identity", color = "black") +
  scale_x_continuous(trans = 'log10') +
  labs(title = "Comparação de Dois Conjuntos", x = "N (Escala Log)", y = "Frequência") +
  theme_minimal()
p6 <- ggplot(df_total, aes(x = Grupo, y = N)) +
  geom_boxplot(fill = c("orange", "lightgreen"), alpha = 0.7) +
  scale_y_continuous(trans = 'log10') +
  labs(title = "Boxplot de N por Conjunto", x = "Grupo", y = "N (Escala Log)") +
  theme_minimal()
library(gridExtra)
grid_arrange <- grid.arrange(p1, p2, p3, p4, p5, p6, ncol = 2)
print("Média de N - Conjunto 1:")
print(mean(df1$N))
print("Média de N - Conjunto 2:")
print(mean(df2$N))
