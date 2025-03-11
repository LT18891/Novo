# Simulação de uma "célula fotovoltaica quântica" usando um poço quântico

# Carregar a biblioteca necessária
library(ggplot2)

# Constantes físicas
const_hbar <- 1.0545718e-34         # Constante de Planck reduzida (J.s)
massa_electron <- 9.10938356e-31    # Massa do elétron (kg)
# Exemplo: GaAs, onde a massa efetiva é aproximadamente 0.067 vezes a massa do elétron
massa_efetiva <- 0.067 * massa_electron  

# Parâmetros da malha espacial
n_pontos <- 1000                  # Número de pontos da malha
x_min <- -10e-9                   # Limite inferior (m)
x_max <- 10e-9                    # Limite superior (m)
x <- seq(x_min, x_max, length.out = n_pontos)
dx <- x[2] - x[1]                 # Espaçamento da malha

# Definição do potencial V(x)
# Dentro do poço: V = 0; fora do poço: V = V_barreira (por exemplo, 0.3 eV)
V0 <- 0                           # Potencial dentro do poço (J)
V_barreira <- 0.3 * 1.60218e-19    # Potencial da barreira (J) (0.3 eV)
V <- rep(V_barreira, n_pontos)     # Inicializa V com o valor da barreira

# Definir a largura do poço (por exemplo, 5 nm) e posicioná-lo no centro da malha
largura_poco <- 5e-9              # Largura do poço (m)
centro <- round(n_pontos / 2)
pontos_poco <- round(largura_poco / dx)
inicio_poco <- centro - round(pontos_poco / 2)
fim_poco <- centro + round(pontos_poco / 2)
V[inicio_poco:fim_poco] <- V0      # Dentro do poço, V = 0

# Construção da matriz Hamiltoniana H usando diferenças finitas
# A equação de Schrödinger estacionária:
#   - (ℏ²/(2*m)) d²ψ/dx² + V(x) ψ = E ψ
# Discretizando a segunda derivada:
#   ψ''(x) ≈ [ψ(x+dx) - 2ψ(x) + ψ(x-dx)] / (dx)²
# Portanto, o coeficiente para o operador cinético é:
coeficiente <- -const_hbar^2 / (2 * massa_efetiva) / (dx^2)

# Construir a matriz T (parte cinética) manualmente preenchendo as diagonais
T <- matrix(0, nrow = n_pontos, ncol = n_pontos)
for (i in 1:n_pontos) {
  T[i, i] <- -2
  if (i > 1) {
    T[i, i - 1] <- 1
  }
  if (i < n_pontos) {
    T[i, i + 1] <- 1
  }
}
T <- coeficiente * T

# Construir a matriz Hamiltoniana: H = T + V(x) na diagonal
H <- T + diag(V)

# Resolver o problema de autovalores: H · ψ = E · ψ
solucao <- eigen(H, symmetric = TRUE)
autovalores <- solucao$values      # Energias em Joules
autovetores <- solucao$vectors      # Autofunções

# Converter as energias de Joules para elétron-volts (eV)
autovalores_eV <- autovalores / 1.60218e-19

# Exibir os níveis de energia dos 4 primeiros estados
cat("Níveis de energia dos 4 primeiros estados (em eV):\n")
print(autovalores_eV[1:4])

# Plotar as primeiras 4 autofunções normalizadas e deslocadas verticalmente
num_estados <- 4   # Número de estados a serem plotados
dados_plot <- data.frame()

for (i in 1:num_estados) {
  psi <- autovetores[, i]
  norma <- sqrt(sum(psi^2) * dx)
  psi_norm <- psi / norma
  
  energia_atual <- autovalores_eV[i]
  dados_plot <- rbind(dados_plot,
                      data.frame(x = x * 1e9,         # converter posição para nm
                                 psi = psi_norm + energia_atual,
                                 estado = paste("Estado", i, "(E =", round(energia_atual, 3), "eV)")))
}

ggplot(dados_plot, aes(x = x, y = psi, color = estado)) +
  geom_line() +
  labs(x = "Posição (nm)",
       y = "ψ (normalizada, deslocada por E)",
       title = "Autofunções dos primeiros estados quânticos\n(simulação de poço quântico)") +
  theme_minimal()

