# Carregar pacotes
library(ggplot2)

# Parâmetros do modelo
preco_inicial <- 80       # Preço inicial do petróleo (USD)
mu <- 0.05                # Drift anual médio (ex: 5% ao ano)
sigma <- 0.2              # Volatilidade difusiva anual (20% ao ano)
lambda <- 0.3             # Intensidade de saltos: 0.3 saltos/ano em média
mu_J <- -0.5              # Média do log do tamanho do salto
sigma_J <- 0.7            # Desvio-padrão do log do tamanho do salto

# Horizonte e discretização
T_final <- 1              # 1 ano
n_passos <- 252           # Aproximar dias úteis
delta_t <- T_final / n_passos

# Número de cenários a simular
n_caminhos <- 10

set.seed(123) # Fixar semente para reprodutibilidade

# Matriz para armazenar preços
matriz_precos <- matrix(NA, nrow = n_passos+1, ncol = n_caminhos)
matriz_precos[1,] <- preco_inicial

# Loop de simulação
for (j in 1:n_caminhos) {
  P <- preco_inicial
  for (i in 2:(n_passos+1)) {
    # 1. Gerar ruído normal para o componente difusivo
    Z <- rnorm(1, mean = 0, sd = 1)
    
    # 2. Calcular o incremento difusivo sem salto:
    #   P_t * exp((mu - sigma^2/2)*dt + sigma*sqrt(dt)*Z)
    P_sem_salto <- P * exp((mu - 0.5 * sigma^2)*delta_t + sigma * sqrt(delta_t)*Z)
    
    # 3. Determinar se ocorre salto neste intervalo:
    #   N_t ~ Poisson(lambda * dt)
    N_t <- rpois(1, lambda = lambda * delta_t)
    
    # 4. Se houver salto (N_t >= 1), gerar tamanho do salto:
    #   X ~ N(mu_J, sigma_J^2), J = exp(X)
    #   Se mais de um salto, multiplicar os fatores
    if (N_t > 0) {
      # Gerar N_t valores de salto
      X_saltos <- rnorm(N_t, mean = mu_J, sd = sigma_J)
      J_fatores <- exp(X_saltos)
      
      # Multiplicar todos os saltos
      fator_salto <- prod(J_fatores)
      
      # Atualizar o preço com o salto
      P <- P_sem_salto * fator_salto
    } else {
      # Sem salto
      P <- P_sem_salto
    }
    
    matriz_precos[i,j] <- P
  }
}

# Preparar dados para plotagem
df_plot <- data.frame(
  tempo = rep(0:n_passos, times = n_caminhos),
  preco = as.vector(matriz_precos),
  caminho = rep(1:n_caminhos, each = n_passos+1)
)

# Plotar os caminhos simulados
ggplot(df_plot, aes(x = tempo, y = preco, group = caminho, color = factor(caminho))) +
  geom_line(show.legend = FALSE) +
  labs(title = "Simulações do preço do petróleo com Modelo de Salto-Difusão (Merton)",
       x = "Passos de tempo (dias úteis)",
       y = "Preço (USD)") +
  theme_minimal()


