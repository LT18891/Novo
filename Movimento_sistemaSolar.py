import pygame
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys
import math
import numpy as np

# Classe Planeta
class Planeta:
    def __init__(self, nome, massa, raio, cor, posicao_inicial, velocidade_inicial):
        self.nome = nome
        self.massa = massa  # em kg
        self.raio = raio    # em metros (para visualização)
        self.cor = cor
        self.posicao = np.array(posicao_inicial, dtype='float64')  # em metros
        self.velocidade = np.array(velocidade_inicial, dtype='float64')  # em m/s
        self.trajetoria = []

    def desenhar(self, tela, escala, centro):
        x = centro[0] + self.posicao[0] / escala
        y = centro[1] + self.posicao[1] / escala
        # Ajuste do tamanho visual para melhor visibilidade
        tamanho_visual = max(int(self.raio / 1e7), 2)
        pygame.draw.circle(tela, self.cor, (int(x), int(y)), tamanho_visual)

    def atualizar_trajetoria(self, escala, centro):
        x = centro[0] + self.posicao[0] / escala
        y = centro[1] + self.posicao[1] / escala
        self.trajetoria.append((int(x), int(y)))
        if len(self.trajetoria) > 1000:
            self.trajetoria.pop(0)

    def desenhar_trajetoria(self, tela):
        if len(self.trajetoria) > 1:
            pygame.draw.lines(tela, self.cor, False, self.trajetoria, 1)

# Função para calcular a força gravitacional entre dois corpos
def calcular_forca_gravitacional(objeto1, objeto2, G):
    vetor_posicao = objeto2.posicao - objeto1.posicao
    distancia = np.linalg.norm(vetor_posicao)
    if distancia == 0:
        return np.array([0.0, 0.0])
    forca = G * objeto1.massa * objeto2.massa / distancia**2
    direcao = vetor_posicao / distancia
    aceleracao = (forca / objeto1.massa) * direcao
    return aceleracao

# Função para atualizar posições e velocidades usando o Método Leapfrog
def atualizar_posicoes_velocidades(planetas, dt, G):
    aceleracoes = [np.array([0.0, 0.0]) for _ in planetas]

    # Calcular acelerações devido a todas as outras massas
    for i, planeta1 in enumerate(planetas):
        for j, planeta2 in enumerate(planetas):
            if i != j:
                aceleracoes[i] += calcular_forca_gravitacional(planeta1, planeta2, G)

    # Atualizar velocidades (meio passo)
    for i, planeta in enumerate(planetas):
        planeta.velocidade += aceleracoes[i] * (dt / 2)

    # Atualizar posições
    for planeta in planetas:
        planeta.posicao += planeta.velocidade * dt

    # Recalcular acelerações após a atualização das posições
    aceleracoes = [np.array([0.0, 0.0]) for _ in planetas]
    for i, planeta1 in enumerate(planetas):
        for j, planeta2 in enumerate(planetas):
            if i != j:
                aceleracoes[i] += calcular_forca_gravitacional(planeta1, planeta2, G)

    # Atualizar velocidades (meio passo)
    for i, planeta in enumerate(planetas):
        planeta.velocidade += aceleracoes[i] * (dt / 2)

    # Atualizar trajetórias
    for planeta in planetas:
        if planeta.nome != 'Sol':
            planeta.atualizar_trajetoria(ESCALA_DISTANCIA, (LARGURA_TELA // 2, ALTURA_TELA // 2))

# Definição das constantes físicas
G = 6.67430e-11  # Constante gravitacional em m^3 kg^-1 s^-2
ESCALA_DISTANCIA = 7.5e9  # Escala para converter metros em pixels (ajustada para visualização)
TEMPO_ESCALA = 3600 * 24  # 1 dia em segundos

# Definição dos planetas com dados aproximados
MASSAS = {
    'Mercúrio': 3.3011e23,
    'Vênus': 4.8675e24,
    'Terra': 5.972e24,
    'Marte': 6.4171e23,
    'Júpiter': 1.8982e27,
    'Saturno': 5.6834e26,
    'Urano': 8.6810e25,
    'Netuno': 1.02413e26,
    'Sol': 1.9885e30
}

# Distâncias médias ao Sol em metros
DISTANCIAS = {
    'Mercúrio': 5.791e10,
    'Vênus': 1.082e11,
    'Terra': 1.496e11,
    'Marte': 2.279e11,
    'Júpiter': 7.785e11,
    'Saturno': 1.433e12,
    'Urano': 2.872e12,
    'Netuno': 4.495e12
}

# Velocidades orbitais médias em m/s
VELOCIDADES = {
    'Mercúrio': 47870,
    'Vênus': 35020,
    'Terra': 29800,
    'Marte': 24130,
    'Júpiter': 13070,
    'Saturno': 9680,
    'Urano': 6800,
    'Netuno': 5430
}

# Raio para visualização (arbitrário para melhor visualização)
RAIOS = {
    'Sol': 6.9634e8,
    'Mercúrio': 2.4397e6,
    'Vênus': 6.0518e6,
    'Terra': 6.371e6,
    'Marte': 3.3895e6,
    'Júpiter': 6.9911e7,
    'Saturno': 5.8232e7,
    'Urano': 2.5362e7,
    'Netuno': 2.4622e7
}

# Cores dos planetas
CORES = {
    'Sol': (255, 255, 0),        # Amarelo
    'Mercúrio': (128, 128, 128), # Cinza
    'Vênus': (255, 165, 0),      # Laranja
    'Terra': (0, 0, 255),        # Azul
    'Marte': (255, 0, 0),        # Vermelho
    'Júpiter': (255, 140, 0),    # Laranja escuro
    'Saturno': (210, 180, 140),  # Bronze
    'Urano': (173, 216, 230),    # Azul claro
    'Netuno': (0, 0, 139)        # Azul escuro
}

# Inicializando os planetas
def criar_planetas(velocidades_iniciais):
    planetas = []

    # Inicializando o Sol
    sol = Planeta(
        nome='Sol',
        massa=MASSAS['Sol'],
        raio=RAIOS['Sol'],
        cor=CORES['Sol'],
        posicao_inicial=(0, 0),
        velocidade_inicial=(0, 0)
    )
    planetas.append(sol)

    # Inicializando os planetas
    for nome in ['Mercúrio', 'Vênus', 'Terra', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Netuno']:
        planeta = Planeta(
            nome=nome,
            massa=MASSAS[nome],
            raio=RAIOS[nome],
            cor=CORES[nome],
            posicao_inicial=(DISTANCIAS[nome], 0),
            velocidade_inicial=(0, velocidades_iniciais.get(nome, VELOCIDADES[nome]))
        )
        planetas.append(planeta)

    return planetas

# Função para ajustar as velocidades iniciais via Tkinter
def interface_entrada_velocidades():
    def iniciar_simulacao():
        try:
            velocidades_iniciais = {}
            for nome in ['Mercúrio', 'Vênus', 'Terra', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Netuno']:
                valor = float(entradas[nome].get())
                velocidades_iniciais[nome] = valor
            janela.destroy()
            pygame_simulacao(velocidades_iniciais)
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira valores numéricos válidos para as velocidades.")

    # Criando a janela Tkinter
    janela = tk.Tk()
    janela.title("Configuração das Velocidades Iniciais dos Planetas")
    janela.geometry("400x400")

    label_instrucoes = ttk.Label(janela, text="Insira as velocidades iniciais dos planetas em m/s:")
    label_instrucoes.pack(pady=10)

    entradas = {}
    for nome in ['Mercúrio', 'Vênus', 'Terra', 'Marte', 'Júpiter', 'Saturno', 'Urano', 'Netuno']:
        frame = ttk.Frame(janela)
        frame.pack(pady=5, padx=10, fill='x')

        label = ttk.Label(frame, text=f"{nome}:", width=15, anchor='w')
        label.pack(side='left')

        entrada = ttk.Entry(frame)
        entrada.insert(0, f"{VELOCIDADES[nome]:.2f}")
        entrada.pack(side='left', expand=True, fill='x')
        entradas[nome] = entrada

    botao_iniciar = ttk.Button(janela, text="Iniciar Simulação", command=iniciar_simulacao)
    botao_iniciar.pack(pady=20)

    janela.mainloop()

# Função para executar a simulação com Pygame
def pygame_simulacao(velocidades_iniciais):
    # Inicialização do Pygame
    pygame.init()

    # Configurações da tela
    global LARGURA_TELA, ALTURA_TELA
    LARGURA_TELA = 1200
    ALTURA_TELA = 800
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Simulação Realista do Sistema Solar")

    # Cores
    PRETO = (0, 0, 0)
    BRANCO = (255, 255, 255)

    # FPS (Frames por Segundo)
    FPS = 60
    relogio = pygame.time.Clock()

    # Criação dos planetas
    planetas = criar_planetas(velocidades_iniciais)

    # Centro da tela (posição do Sol)
    centro = (LARGURA_TELA // 2, ALTURA_TELA // 2)

    # Fonte para exibir informações
    fonte = pygame.font.SysFont(None, 24)

    # Tempo simulado em segundos
    tempo_simulado = 0

    # Loop principal da simulação
    rodando = True
    while rodando:
        relogio.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                sys.exit()
            # Controle de velocidade da simulação
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_UP:
                    global TEMPO_ESCALA
                    TEMPO_ESCALA *= 2
                elif evento.key == pygame.K_DOWN:
                    TEMPO_ESCALA /= 2
                    if TEMPO_ESCALA < 1:
                        TEMPO_ESCALA = 1

        # Atualizar posições e velocidades
        atualizar_posicoes_velocidades(planetas, TEMPO_ESCALA, G)
        tempo_simulado += TEMPO_ESCALA

        # Preencher o fundo
        tela.fill(PRETO)

        # Desenhar as trajetórias
        for planeta in planetas:
            planeta.desenhar_trajetoria(tela)

        # Desenhar os planetas
        for planeta in planetas:
            planeta.desenhar(tela, ESCALA_DISTANCIA, centro)

        # Desenhar o Sol no centro
        sol = planetas[0]
        pygame.draw.circle(tela, sol.cor, centro, max(int(sol.raio / 1e7), 10))

        # Exibir informações
        texto_tempo = fonte.render(f"Tempo Simulado: {tempo_simulado / (3600 * 24):.2f} dias", True, BRANCO)
        tela.blit(texto_tempo, (10, 10))

        texto_velocidade = fonte.render(f"Velocidade da Simulação: {TEMPO_ESCALA / (3600 * 24):.2f} dias/segundo", True, BRANCO)
        tela.blit(texto_velocidade, (10, 30))

        texto_controles = fonte.render("Use as setas para cima e para baixo para ajustar a velocidade da simulação.", True, BRANCO)
        tela.blit(texto_controles, (10, 50))

        # Atualizar a tela
        pygame.display.flip()

# Executando a interface de entrada
if __name__ == "__main__":
    interface_entrada_velocidades()
