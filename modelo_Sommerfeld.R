# Autor: Luiz Tiago Wilcke
# Modelo de Drude-Sommerfeld para condutividade em metais
# ---------------------------------------------------------
# Este código implementa o modelo de Drude-Sommerfeld, que combina:
#   - O modelo clássico de Drude para a condutividade dos elétrons:
#       sigma = (n * e^2 * tau) / m_e
#   - O tratamento quântico dos elétrons como um gás degenerado (modelo de Sommerfeld):
#       Energia de Fermi: E_F = (hbar^2/(2*m_e)) * (3*pi^2*n)^(2/3)
#       Velocidade de Fermi: v_F = sqrt(2 * E_F/m_e)
#       Comprimento de caminho médio: l = v_F * tau
#
# Onde:
#   n         : densidade de elétrons (m^-3)
#   e         : carga elementar (C)
#   tau       : tempo de relaxação (s)
#   m_e       : massa do elétron (kg)
#   hbar      : constante de Planck reduzida (J.s)
#   k_B       : constante de Boltzmann (J/K)
#
# Além disso, definimos a função de distribuição de Fermi–Dirac:
#   f(E) = 1 / (exp((E - mu) / (k_B * T)) + 1)
# Para temperaturas muito baixas, o potencial químico mu pode ser aproximado
# pela energia de Fermi (E_F).

# ---------------------------
# Definição de constantes
# ---------------------------
pi <- 3.141592653589793      # Valor de π
hbar <- 1.054571817e-34      # Constante de Planck reduzida (J.s)
e <- 1.602176634e-19         # Carga elementar (C)
m_e <- 9.10938356e-31        # Massa do elétron (kg)
k_B <- 1.380649e-23          # Constante de Boltzmann (J/K)

# ---------------------------
# Parâmetros do sistema
# ---------------------------
n_eletrons <- 8.5e28         # Densidade de elétrons (m^-3), ex: cobre ~8.5e28 m^-3
tau <- 2.5e-14               # Tempo de relaxação (s) (valor aproximado)
temperatura <- 300           # Temperatura (K), ex: temperatura ambiente

# ---------------------------
# Cálculo da Energia de Fermi
# ---------------------------
# E_F = (hbar^2 / (2*m_e)) * (3*pi^2*n)^(2/3)
energia_fermi <- (hbar^2 / (2 * m_e)) * (3 * pi^2 * n_eletrons)^(2/3)  # Energia em Joules
energia_fermi_eV <- energia_fermi / e  # Conversão de Joules para elétron-volt (eV)

# ---------------------------
# Cálculo da Velocidade de Fermi
# ---------------------------
# v_F = sqrt(2 * E_F / m_e)
v_F <- sqrt(2 * energia_fermi / m_e)  # Velocidade em m/s

# ---------------------------
# Cálculo do Comprimento de Caminho Médio
# ---------------------------
# l = v_F * tau
comprimento_caminho <- v_F * tau  # Comprimento em metros

# ---------------------------
# Cálculo da Condutividade (Modelo de Drude)
# ---------------------------
# sigma = (n * e^2 * tau) / m_e
sigma <- (n_eletrons * e^2 * tau) / m_e  # Condutividade em S/m (Siemens por metro)

# Exibindo os resultados
cat("Resultados do Modelo de Drude-Sommerfeld:\n")
cat("Energia de Fermi:", energia_fermi, "J (", energia_fermi_eV, "eV )\n")
cat("Velocidade de Fermi:", v_F, "m/s\n")
cat("Comprimento de caminho médio:", comprimento_caminho, "m\n")
cat("Condutividade:", sigma, "S/m\n\n")

# ---------------------------
# Função de Distribuição de Fermi-Dirac
# ---------------------------
# f(E) = 1 / (exp((E - mu) / (k_B * T)) + 1)
# Para T próximo de 0 K, mu ≈ E_F
fermi_dirac <- function(energia, mu, T) {
  # energia: vetor de energias (J)
  # mu     : potencial químico (J) (aproximadamente energia de Fermi em baixas temperaturas)
  # T      : temperatura (K)
  return(1 / (exp((energia - mu) / (k_B * T)) + 1))
}

# ---------------------------
# Plot da Distribuição de Fermi-Dirac
# ---------------------------
# Criaremos um vetor de energias em torno da energia de Fermi para visualizar a
# variação da função de distribuição.
energia_min <- energia_fermi - 5 * k_B * temperatura  # Limite inferior (J)
energia_max <- energia_fermi + 5 * k_B * temperatura  # Limite superior (J)
energia_seq <- seq(energia_min, energia_max, length.out = 1000)  # Vetor de energias

# Calcula a distribuição de Fermi-Dirac com mu ≈ energia_fermi
distribuicao <- fermi_dirac(energia_seq, energia_fermi, temperatura)

# Plot do gráfico: Energia (convertida para eV) vs. f(E)
plot(energia_seq / e, distribuicao, type = "l", lwd = 2,
     xlab = "Energia (eV)", ylab = "f(E)",
     main = "Distribuição de Fermi-Dirac")
grid()
