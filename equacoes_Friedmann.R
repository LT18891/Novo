# Instala e carrega os pacotes necessários
if(!require(deSolve)) install.packages("deSolve")
if(!require(ggplot2)) install.packages("ggplot2")
if(!require(gridExtra)) install.packages("gridExtra")

library(deSolve)
library(ggplot2)
library(gridExtra)

# Parâmetros do modelo
H0 <- 1              # Parâmetro de Hubble atual (em unidades de H0^-1, para trabalhar com tempo adimensional)
omega_m <- 0.3       # Densidade de matéria
omega_lambda <- 0.7  # Densidade de energia escura (constante cosmológica)

# Função que define a equação diferencial:
# Para um universo plano com matéria e Λ, a equação de Friedmann (em termos do fator de escala 'a') é:
#   (da/dt) = a * H(a) = H0 * sqrt(omega_m / a + omega_lambda * a^2)
f_derivada <- function(tempo, estado, parametros) {
  a <- estado[1]
  with(as.list(parametros), {
    da_dt <- H0 * sqrt(omega_m / a + omega_lambda * a^2)
    list(c(da_dt))
  })
}

# Condição inicial: um valor pequeno para o fator de escala (próximo do Big Bang)
estado_inicial <- c(a = 1e-3)
parametros <- c(H0 = H0, omega_m = omega_m, omega_lambda = omega_lambda)

# Definindo a sequência de tempo para a integração (o intervalo deve ser longo o suficiente para que 'a' atinja valores maiores)
tempo_inicial <- 0
tempo_final   <- 4   # Esse valor é adimensional (unidades de H0^-1)
passos        <- 1000
vetor_tempo   <- seq(tempo_inicial, tempo_final, length.out = passos)

# Resolver a ODE utilizando o pacote deSolve
solucao <- ode(y = estado_inicial, times = vetor_tempo, func = f_derivada, parms = parametros)
solucao_df <- as.data.frame(solucao)
names(solucao_df) <- c("tempo", "fator_escala")

# Cálculo da derivada (da/dt) conforme a equação original e do parâmetro de Hubble H = (da/dt) / a
solucao_df$derivada <- H0 * sqrt(omega_m / solucao_df$fator_escala + omega_lambda * solucao_df$fator_escala^2)
solucao_df$H <- solucao_df$derivada / solucao_df$fator_escala

# Cálculo do parâmetro de desaceleração q = - (a * a'') / (a')^2 
# A segunda derivada (a'') é aproximada numericamente
dadt <- solucao_df$derivada
dt   <- solucao_df$tempo
a_segunda_deriv <- c(NA, diff(dadt) / diff(dt))  # primeira posição sem valor
solucao_df$q <- - solucao_df$fator_escala * a_segunda_deriv / (solucao_df$derivada^2)

# Cálculo do redshift: z = 1/a - 1 (considerando que a = 1 atualmente)
solucao_df$redshift <- 1 / solucao_df$fator_escala - 1

# Identifica o instante aproximado em que o fator de escala atinge 1 (universo "atual")
indice_a1 <- which.min(abs(solucao_df$fator_escala - 1))
tempo_a1 <- solucao_df$tempo[indice_a1]
H_a1     <- solucao_df$H[indice_a1]
q_a1     <- solucao_df$q[indice_a1]

cat("---- Valores Numéricos Importantes ----\n")
cat("Tempo aproximado quando o fator de escala a ≈ 1:", round(tempo_a1, 3), "\n")
cat("Valor de H(t) nesse tempo:", round(H_a1, 3), "\n")
cat("Valor do parâmetro de desaceleração q(t) nesse tempo:", round(q_a1, 3), "\n\n")

# Geração dos gráficos

# 1. Fator de Escala vs Tempo
grafico1 <- ggplot(solucao_df, aes(x = tempo, y = fator_escala)) +
  geom_line(color = "blue", size = 1) +
  labs(title = "Expansão do Universo: Fator de Escala vs Tempo",
       x = "Tempo (unidades de H0⁻¹)",
       y = "Fator de Escala (a)") +
  theme_minimal()

# 2. Parâmetro de Hubble vs Tempo
grafico2 <- ggplot(solucao_df, aes(x = tempo, y = H)) +
  geom_line(color = "red", size = 1) +
  labs(title = "Parâmetro de Hubble vs Tempo",
       x = "Tempo (unidades de H0⁻¹)",
       y = "H(t)") +
  theme_minimal()

# 3. Parâmetro de Desaceleração vs Tempo
grafico3 <- ggplot(solucao_df, aes(x = tempo, y = q)) +
  geom_line(color = "darkgreen", size = 1) +
  labs(title = "Parâmetro de Desaceleração vs Tempo",
       x = "Tempo (unidades de H0⁻¹)",
       y = "q(t)") +
  theme_minimal()

# 4. Redshift vs Tempo
grafico4 <- ggplot(solucao_df, aes(x = tempo, y = redshift)) +
  geom_line(color = "purple", size = 1) +
  labs(title = "Redshift vs Tempo",
       x = "Tempo (unidades de H0⁻¹)",
       y = "Redshift (z)") +
  theme_minimal()

# Exibe os gráficos em um grid
grid.arrange(grafico1, grafico2, grafico3, grafico4, ncol = 2)

