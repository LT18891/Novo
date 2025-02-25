# Função para verificar, instalar (se necessário) e carregar um pacote
load_package <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg)
  }
  library(pkg, character.only = TRUE)
}

# Carregar o pacote necessário
load_package("randtoolbox")

# Definir a função a ser integrada
f <- function(x, y) {
  sin(pi * x) * cos(pi * y)
}

# Função para estimar a integral usando a sequência Sobol
estimate_integral_sobol <- function(n_points, func) {
  # Gerar pontos da sequência Sobol em [0, 1]^2
  points <- sobol(n = n_points, dim = 2)
  
  # Avaliar a função em cada ponto (utilizando vetorização)
  values <- func(points[, 1], points[, 2])
  
  # Estimar a integral como a média dos valores calculados
  integral <- mean(values)
  
  list(integral = integral, points = points)
}

# Parâmetros
n_points <- 1000

# Estimar a integral e capturar os pontos gerados
result <- estimate_integral_sobol(n_points, f)

# Exibir o resultado
cat("Estimativa da integral usando QMC (Sobol):", result$integral, "\n")

# Visualizar os pontos gerados
plot(result$points, pch = 20, col = "blue",
     main = "Sequência Sobol em [0, 1]^2",
     xlab = "x", ylab = "y")

