
library(ggplot2)       # Para visualizações avançadas
library(dplyr)         # Para manipulação de dados
library(scatterplot3d) # Para gráficos 3D

# Definir semente para reprodutibilidade
set.seed(123)

# Parâmetros do modelo
num_estrelas <- 50000   # Número de estrelas a simular
escala_R    <- 5       # Escala radial (kpc)
escala_z    <- 0.3     # Escala vertical (kpc)

# 1. SIMULAÇÃO DAS POSIÇÕES
# -------------------------
# Distribuição radial: R segue uma distribuição exponencial
# Usando a transformação inversa: R = -escala_R * log(U), com U ~ Uniforme(0,1)
R <- -escala_R * log(runif(num_estrelas))

# Distribuição angular: theta uniformemente distribuído entre 0 e 2pi
theta <- runif(num_estrelas, 0, 2 * pi)

# Converter para coordenadas cartesianas no plano galáctico
x <- R * cos(theta)
y <- R * sin(theta)

# Distribuição vertical: z simulada como uma normal centrada em 0
z <- rnorm(num_estrelas, mean = 0, sd = escala_z)

# Criar data frame com os dados simulados
dados_estrelas <- data.frame(x = x, y = y, z = z, R = R)

# 2. PLOTAGENS GRÁFICAS
# ---------------------

# Gráfico 1: Dispersão das estrelas no plano galáctico (x vs y)
plot1 <- ggplot(dados_estrelas, aes(x = x, y = y)) +
  geom_point(alpha = 0.3, size = 0.5, color = "blue") +
  labs(title = "Distribuição de Estrelas no Plano Galáctico",
       x = "Coordenada X (kpc)", y = "Coordenada Y (kpc)") +
  theme_minimal()

# Gráfico 2: Histograma da distribuição radial (R) com densidade estimada
plot2 <- ggplot(dados_estrelas, aes(x = R)) +
  geom_histogram(aes(y = ..density..), bins = 50, fill = "darkgreen", color = "black", alpha = 0.7) +
  geom_density(color = "red", size = 1) +
  labs(title = "Histograma da Distância Radial (R)",
       x = "Distância Radial (kpc)", y = "Densidade") +
  theme_minimal()

# Gráfico 3: Histograma da distribuição vertical (z)
plot3 <- ggplot(dados_estrelas, aes(x = z)) +
  geom_histogram(aes(y = ..density..), bins = 50, fill = "purple", color = "black", alpha = 0.7) +
  geom_density(color = "orange", size = 1) +
  labs(title = "Histograma da Distribuição Vertical (z)",
       x = "Coordenada Vertical z (kpc)", y = "Densidade") +
  theme_minimal()

# Gráfico 4: Diagrama 3D das posições das estrelas
scatterplot3d(x, y, z, pch = 16, color = "blue",
              main = "Distribuição 3D das Estrelas",
              xlab = "X (kpc)", ylab = "Y (kpc)", zlab = "Z (kpc)")

# Exibir os gráficos 1, 2 e 3
print(plot1)
print(plot2)
print(plot3)

# 3. ANÁLISE ESTATÍSTICA AVANÇADA
# ------------------------------

# (a) Ajuste linear da densidade radial na escala logarítmica
# Estimar a densidade empírica de R
densidade_R <- density(R)
dados_densidade <- data.frame(R = densidade_R$x, densidade = densidade_R$y)

# Ajuste linear: log(densidade) ~ R. Em um disco exponencial, espera-se que log(densidade) decaia linearmente com R.
modelo_linear <- lm(log(densidade) ~ R, data = dados_densidade)
summary_modelo <- summary(modelo_linear)

print(summary_modelo)

# Gráfico 5: Ajuste linear da densidade radial em escala logarítmica
plot5 <- ggplot(dados_densidade, aes(x = R, y = log(densidade))) +
  geom_point(color = "darkred") +
  geom_smooth(method = "lm", color = "black") +
  labs(title = "Ajuste Linear da Densidade Radial (Escala Logarítmica)",
       x = "R (kpc)", y = "log(Densidade)") +
  theme_minimal()

print(plot5)

# (b) Simulação de contagem de estrelas em anéis radiais
# Definir os limites dos anéis (bins)
bins <- seq(0, max(R), length.out = 30)
# Calcular o centro de cada anel
centros <- (bins[-1] + bins[-length(bins)]) / 2
# Contar o número de estrelas em cada anel
contagens <- hist(R, breaks = bins, plot = FALSE)$counts
dados_contagem <- data.frame(centro = centros, contagem = contagens)

# Gráfico 6: Número de estrelas por anel radial
plot6 <- ggplot(dados_contagem, aes(x = centro, y = contagem)) +
  geom_bar(stat = "identity", fill = "skyblue", color = "black", alpha = 0.7) +
  labs(title = "Contagem de Estrelas por Anel Radial",
       x = "Raio (kpc)", y = "Número de Estrelas") +
  theme_minimal()

print(plot6)
