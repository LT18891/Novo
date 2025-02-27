# Autor: Luiz Tiago Wilcke
# Data: 27/02/2025
# Descrição: Implementação do método de Monte Carlo para integração numérica
# de funções de uma ou mais variáveis, com estimativa do erro padrão.

integracaoMonteCarlo <- function(funcao, limites, numPontos = 100000) {
  dimensao <- length(limites)
  pontosAleatorios <- matrix(NA, nrow = numPontos, ncol = dimensao)
  for (i in 1:dimensao) {
    pontosAleatorios[, i] <- runif(numPontos, min = limites[[i]][1], max = limites[[i]][2])
  }
  volume <- prod(sapply(limites, function(lim) { lim[2] - lim[1] }))
  valoresFuncao <- apply(pontosAleatorios, 1, funcao)
  mediaValores <- mean(valoresFuncao)
  integralEstimada <- volume * mediaValores
  erroPadrao <- volume * sd(valoresFuncao) / sqrt(numPontos)
  resultado <- list(integral = integralEstimada, erro = erroPadrao, pontos = pontosAleatorios, valores = valoresFuncao)
  return(resultado)
}

funcaoUmDim <- function(x) { return(sin(x)) }
limitesUmDim <- list(c(0, pi))
resultadoUmDim <- integracaoMonteCarlo(funcaoUmDim, limitesUmDim, numPontos = 100000)
cat("Integração de sin(x) no intervalo [0, pi]:\n")
cat("Integral estimada:", resultadoUmDim$integral, "\n")
cat("Erro estimado:", resultadoUmDim$erro, "\n\n")

funcaoDuasDim <- function(ponto) { return(exp(- (ponto[1]^2 + ponto[2]^2))) }
limitesDuasDim <- list(c(-1, 1), c(-1, 1))
resultadoDuasDim <- integracaoMonteCarlo(funcaoDuasDim, limitesDuasDim, numPontos = 1000000)
cat("Integração de exp(-(x^2 + y^2)) sobre o quadrado [-1,1] x [-1,1]:\n")
cat("Integral estimada:", resultadoDuasDim$integral, "\n")
cat("Erro estimado:", resultadoDuasDim$erro, "\n")

x <- seq(-1, 1, length.out = 100)
y <- seq(-1, 1, length.out = 100)
z <- outer(x, y, function(x, y) { exp(- (x^2 + y^2)) })
contour(x, y, z, nlevels = 10, col = "blue", xlab = "x", ylab = "y")
points(resultadoDuasDim$pontos, col = rgb(1, 0, 0, 0.1), pch = 16)
