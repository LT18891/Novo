library(ggplot2)
library(dplyr)
library(gridExtra)

nu <- 10
alpha <- 0.05

x_vals <- seq(-5, 5, length.out = 1000)
densidade <- dt(x_vals, df = nu)
dados <- data.frame(x = x_vals, densidade = densidade)

q_inferior <- qt(alpha / 2, df = nu)
q_superior <- qt(1 - alpha / 2, df = nu)

plot_t <- ggplot(dados, aes(x = x, y = densidade)) +
  geom_line(color = "blue", size = 1) +
  labs(title = "Distribuição t-Student com 10 Graus de Liberdade",
       x = "Valores de t", y = "Densidade") +
  theme_minimal() +
  geom_vline(xintercept = c(q_inferior, q_superior), linetype = "dashed", color = "red") +
  annotate("text", x = q_inferior, y = max(dados$densidade)*0.9,
           label = sprintf("q = %.2f", q_inferior), angle = 90, vjust = -0.5, color = "red") +
  annotate("text", x = q_superior, y = max(dados$densidade)*0.9,
           label = sprintf("q = %.2f", q_superior), angle = 90, vjust = -0.5, color = "red") +
  geom_area(data = subset(dados, x <= q_inferior), aes(x = x, y = densidade), fill = "red", alpha = 0.3) +
  geom_area(data = subset(dados, x >= q_superior), aes(x = x, y = densidade), fill = "red", alpha = 0.3)

set.seed(123)
n <- 1000
dados_simulados <- rt(n, df = nu)
df_sim <- data.frame(valor = dados_simulados)

plot_hist <- ggplot(df_sim, aes(x = valor)) +
  geom_histogram(aes(y = ..density..), bins = 30,
                 color = "black", fill = "lightblue", alpha = 0.6) +
  stat_function(fun = function(x) dt(x, df = nu),
                color = "darkblue", size = 1) +
  labs(title = "Histograma da Amostra Simulada com Densidade t-Student",
       x = "Valores", y = "Densidade") +
  theme_minimal()

grid.arrange(plot_t, plot_hist, ncol = 2)
