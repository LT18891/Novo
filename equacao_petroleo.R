# Instalar (se necessário) e carregar o pacote de resolução de EDOs
if (!require("deSolve")) install.packages("deSolve")
library(deSolve)

# Definição dos parâmetros do modelo
# delta: coeficiente de amortecimento (dissipação)
# omega: frequência natural do sistema
# gamma: coeficiente de não linearidade (termo cúbico)
# A: amplitude da força externa (oscilatória)
# omega_f: frequência da força externa
parametros <- c(delta = 0.2, 
                omega = 0.5, 
                gamma = 0.01, 
                A = 10, 
                omega_f = 0.2)

# Definição do sistema de equações diferenciais
# Variáveis:
#   preco: preço do barril de petróleo
#   velocidade: variação do preço (derivada)
# Equações:
#   d(preco)/dt = velocidade
#   d(velocidade)/dt = - delta * velocidade - (omega^2)*preco - gamma*(preco^3) + A*sin(omega_f*t)
sistemaEDO <- function(t, y, parametros) {
  with(as.list(c(y, parametros)), {
    dpreco <- velocidade
    dvelocidade <- -delta * velocidade - (omega^2) * preco - gamma * (preco^3) + A * sin(omega_f * t)
    list(c(dpreco, dvelocidade))
  })
}

# Condições iniciais
condicoes_iniciais <- c(preco = 50, velocidade = 0)

# Vetor de tempo para a simulação
tempo <- seq(0, 100, by = 0.1)

# Solução do sistema de equações diferenciais
solucao <- ode(y = condicoes_iniciais, times = tempo, func = sistemaEDO, parms = parametros)
solucao_df <- as.data.frame(solucao)

# Plot 1: Evolução do Preço do Barril de Petróleo ao longo do tempo
plot(solucao_df$time, solucao_df$preco, type = "l", lwd = 2, col = "blue",
     xlab = "Tempo", ylab = "Preço do Barril", 
     main = "Evolução do Preço do Barril de Petróleo")

# Plot 2: Variação do Preço (Velocidade) ao longo do tempo
plot(solucao_df$time, solucao_df$velocidade, type = "l", lwd = 2, col = "red",
     xlab = "Tempo", ylab = "Variação do Preço", 
     main = "Variação do Preço do Barril (Velocidade)")

# Plot 3: Diagrama de Fase (Preço vs. Velocidade)
plot(solucao_df$preco, solucao_df$velocidade, type = "l", lwd = 2, col = "purple",
     xlab = "Preço do Barril", ylab = "Variação do Preço", 
     main = "Diagrama de Fase: Preço vs. Variação")

# Plot 4: Força de Oscilação Aplicada (A*sin(omega_f*t))
forca <- parametros["A"] * sin(parametros["omega_f"] * tempo)
plot(tempo, forca, type = "l", lwd = 2, col = "green",
     xlab = "Tempo", ylab = "Força de Oscilação", 
     main = "Força de Oscilação Aplicada ao Sistema")

