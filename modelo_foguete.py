import pygame
import numpy as np
import matplotlib.pyplot as plt

# Inicializa o Pygame
pygame.init()

# Configurações da tela
largura, altura = 800, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Simulador de Foguete")

# Cores
branco = (255, 255, 255)
azul_claro = (173, 216, 230)
cinza = (169, 169, 169)
preto = (0, 0, 0)

# Função para calcular a altitude
def calcular_altitude(tempo, massa_inicial, empuxo, impulso_especifico, area_frontal, coef_resistencia):
    g = 9.81
    velocidade_escape = impulso_especifico * g
    massa = massa_inicial - tempo * (empuxo / velocidade_escape)
    if massa <= 0:
        return None
    resistencia_ar = 0.5 * coef_resistencia * area_frontal * (empuxo / massa)**2
    aceleracao = (empuxo - massa * g - resistencia_ar) / massa
    altura = (0.5 * aceleracao * tempo ** 2)
    return altura

# Função para animar o foguete
def animar_foguete(altura_maxima):
    foguete_y = altura - 50
    for altura_atual in np.linspace(0, altura_maxima, num=100):
        tela.fill(azul_claro)
        # Desenha o foguete
        pygame.draw.rect(tela, cinza, (largura // 2 - 10, foguete_y - altura_atual, 20, 40))
        pygame.draw.polygon(tela, preto, [(largura // 2 - 10, foguete_y - altura_atual), (largura // 2 + 10, foguete_y - altura_atual), (largura // 2, foguete_y - altura_atual - 20)])
        
        pygame.display.flip()
        pygame.time.delay(50)

# Função de cálculo e plotagem
def calcular_e_plotar(massa_inicial, empuxo, impulso_especifico, area_frontal, coef_resistencia):
    tempos = np.linspace(0, 100, 100)
    alturas = [calcular_altitude(t, massa_inicial, empuxo, impulso_especifico, area_frontal, coef_resistencia) for t in tempos]
    
    fig, ax = plt.subplots()
    ax.plot(tempos, alturas, label="Altitude (m)")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Altitude (m)")
    ax.set_title("Altitude do Foguete ao Longo do Tempo")
    plt.show()
    
    altura_final = max(filter(None, alturas))
    animar_foguete(altura_final)

# Loop principal
executando = True
while executando:
    tela.fill(azul_claro)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            executando = False
            
    # Valores de exemplo (substituir por inputs na versão completa)
    massa_inicial = 1000
    empuxo = 5000
    impulso_especifico = 300
    area_frontal = 2
    coef_resistencia = 0.5
    
    calcular_e_plotar(massa_inicial, empuxo, impulso_especifico, area_frontal, coef_resistencia)
    executando = False  # Apenas um loop para animação

pygame.quit()
