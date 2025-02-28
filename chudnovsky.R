# Instalar e carregar o pacote Rmpfr (se ainda não estiver instalado)
if (!require("Rmpfr")) install.packages("Rmpfr")
library(Rmpfr)

# Para obter 100 dígitos decimais, precisamos de aproximadamente 350 bits de precisão 
# (100 × log2(10) ≈ 332, adicionamos margem)
precisao <- 350

# Inicializa a soma da série
soma <- mpfr(0, precBits = precisao)

# Definir uma tolerância pequena para o critério de parada (por exemplo, 1e-105)
tolerancia <- mpfr("1e-105", precBits = precisao)

k <- 0
repeat {
  # Calcular o termo k da série de Chudnovsky:
  # termo(k) = (-1)^k * (6k)! * (13591409 + 545140134k) /
  #            [ (3k)! * (k!)^3 * (640320)^(3k) ]
  
  numerador <- (-1)^k * factorialMpfr(6 * k) * mpfr(13591409 + 545140134 * k, precBits = precisao)
  denominador <- factorialMpfr(3 * k) * (factorialMpfr(k)^3) * (mpfr(640320, precBits = precisao)^(3 * k))
  termo <- numerador / denominador
  
  soma <- soma + termo
  
  if (abs(termo) < tolerancia) break
  k <- k + 1
}

# A constante multiplicativa da fórmula de Chudnovsky:
# fator = 12 / (640320^(3/2))
fator <- mpfr(12, precBits = precisao) / (mpfr(640320, precBits = precisao)^(mpfr(3, precBits = precisao)/2))

# A fórmula de Chudnovsky nos dá 1/π, então:
pi_calculado <- 1 / (fator * soma)

# Exibir π com 110 dígitos (para garantir os 100 dígitos desejados)
cat("π com 100 dígitos de precisão:\n")
print(format(pi_calculado, digits = 110))
