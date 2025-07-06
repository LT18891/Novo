# -*- coding: utf-8 -*-
# Autor: LT

import pygame
import random

# Inicialização do módulo mixer para sons
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# Configurações da janela
LARGURA_JANELA = 800
ALTURA_JANELA = 700
TAMANHO_BLOCO = 30
COLUNAS = 10
LINHAS = 20
TOPO_TABULEIRO = ALTURA_JANELA - LINHAS * TAMANHO_BLOCO

# Cores (R, G, B)
CORES = [
    (0, 0, 0),        # 0: vazio
    (0, 255, 255),    # 1: ciano (I)
    (0, 0, 255),      # 2: azul (J)
    (255, 165, 0),    # 3: laranja (L)
    (255, 255, 0),    # 4: amarelo (O)
    (0, 255, 0),      # 5: verde (S)
    (128, 0, 128),    # 6: roxo (T)
    (255, 0, 0)       # 7: vermelho (Z)
]

# Formatos das formas (5x5)
FORMAS = [
    [['.....', '.....', '..00.', '.00..', '.....'],    # S
     ['.....', '..0..', '..00.', '...0.', '.....']],
    [['.....', '.....', '.00..', '..00.', '.....'],    # Z
     ['.....', '..0..', '.00..', '.0...', '.....']],
    [['..0..', '..0..', '..0..', '..0..', '.....'],    # I
     ['.....', '0000.', '.....', '.....', '.....']],
    [['.....', '.00..', '.00..', '.....', '.....']],   # O
    [['.....', '.0...', '.000.', '.....', '.....'],    # J
     ['.....', '..00.', '..0..', '..0..', '.....'],
     ['.....', '.....', '.000.', '...0.', '.....'],
     ['.....', '..0..', '..0..', '.00..', '.....']],
    [['.....', '...0.', '.000.', '.....', '.....'],    # L
     ['.....', '..0..', '..0..', '..00.', '.....'],
     ['.....', '.....', '.000.', '.0...', '.....'],
     ['.....', '.00..', '..0..', '..0..', '.....']],
    [['.....', '..0..', '.000.', '.....', '.....'],    # T
     ['.....', '..0..', '..00.', '..0..', '.....'],
     ['.....', '.....', '.000.', '..0..', '.....'],
     ['.....', '..0..', '.00..', '..0..', '.....']]
]

class Forma:
    def __init__(self, x, y, formato):
        self.x = x
        self.y = y
        self.formato = formato
        self.rotação = 0

    @property
    def imagem(self):
        return self.formato[self.rotação % len(self.formato)]

    def girar(self):
        self.rotação = (self.rotação + 1) % len(self.formato)

# Cria grade vazia com bloqueios atuais
def criar_grade(blocos):
    grade = [[(0, 0, 0) for _ in range(COLUNAS)] for _ in range(LINHAS)]
    for (j, i), cor_index in blocos.items():
        if 0 <= i < LINHAS and 0 <= j < COLUNAS:
            grade[i][j] = CORES[cor_index]
    return grade

# Converte formato para posições reais
def converter_posição(forma):
    posições = []
    for i, linha in enumerate(forma.imagem):
        for j, char in enumerate(linha):
            if char == '0':
                posições.append((forma.x + j - 2, forma.y + i - 4))
    return posições

# Verifica se a forma cabe
def forma_valida(forma, grade):
    posições_vazias = {(j, i) for i in range(LINHAS) for j in range(COLUNAS) if grade[i][j] == (0, 0, 0)}
    for pos in converter_posição(forma):
        if pos not in posições_vazias and pos[1] > -1:
            return False
    return True

# Remove linhas completas e faz cair as peças acima
def limpar_linhas(grade, blocos):
    linhas_completas = [i for i in range(LINHAS) if (0, 0, 0) not in grade[i]]
    for linha in linhas_completas:
        for j in range(COLUNAS):
            blocos.pop((j, linha), None)
    # Faz as peças acima caírem
    if linhas_completas:
        for (j, i) in sorted(list(blocos), key=lambda x: x[1]):
            # conta quantas linhas removidas estão abaixo da peça
            queda = sum(1 for linha in linhas_completas if linha > i)
            if queda > 0:
                cor = blocos.pop((j, i))
                blocos[(j, i + queda)] = cor
    return len(linhas_completas)

# Desenha texto na tela
def mostrar_texto(surface, texto, tamanho, x, y):
    fonte = pygame.font.SysFont('comicsans', tamanho, bold=True)
    label = fonte.render(texto, True, (255, 255, 255))
    surface.blit(label, (x, y))

# Função principal do jogo
def main():
    tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pygame.display.set_caption('Tetris - LT')
    relogio = pygame.time.Clock()
    blocos = {}
    grade = criar_grade(blocos)

    cair_tempo = 0
    queda_velocidade = 0.27
    nivel = 0
    pontuação = 0

    peça_atual = Forma(5, 0, random.choice(FORMAS))
    próxima_peça = Forma(5, 0, random.choice(FORMAS))

    rodando = True
    while rodando:
        grade = criar_grade(blocos)
        cair_tempo += relogio.get_rawtime()
        relogio.tick()

        # Aumenta velocidade com o nível
        if pontuação // 10 > nivel:
            nivel += 1
            queda_velocidade = max(0.12, queda_velocidade - 0.02)

        # Queda automática
        if cair_tempo / 1000 >= queda_velocidade:
            cair_tempo = 0
            peça_atual.y += 1
            if not forma_valida(peça_atual, grade) and peça_atual.y > 0:
                peça_atual.y -= 1
                # fixa peça na grade
                for pos in converter_posição(peça_atual):
                    blocos[pos] = FORMAS.index(peça_atual.formato) + 1
                # gera nova peça
                peça_atual = próxima_peça
                próxima_peça = Forma(5, 0, random.choice(FORMAS))
                # limpa linhas completas
                linhas = limpar_linhas(grade, blocos)
                if linhas > 0:
                    pontuação += linhas * 10

        # Eventos do usuário
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_LEFT:
                    peça_atual.x -= 1
                    if not forma_valida(peça_atual, grade): peça_atual.x += 1
                if evento.key == pygame.K_RIGHT:
                    peça_atual.x += 1
                    if not forma_valida(peça_atual, grade): peça_atual.x -= 1
                if evento.key == pygame.K_DOWN:
                    peça_atual.y += 1
                    if not forma_valida(peça_atual, grade): peça_atual.y -= 1
                if evento.key == pygame.K_UP:
                    peça_atual.girar()
                    if not forma_valida(peça_atual, grade): peça_atual.girar()

        # Desenho de fundo
        tela.fill((0, 0, 0))

        # Desenha grade fixa e peças
        for i in range(LINHAS):
            for j in range(COLUNAS):
                pygame.draw.rect(tela, grade[i][j],
                                 (j * TAMANHO_BLOCO, TOPO_TABULEIRO + i * TAMANHO_BLOCO,
                                  TAMANHO_BLOCO, TAMANHO_BLOCO), 0)
                pygame.draw.rect(tela, (128, 128, 128),
                                 (j * TAMANHO_BLOCO, TOPO_TABULEIRO + i * TAMANHO_BLOCO,
                                  TAMANHO_BLOCO, TAMANHO_BLOCO), 1)

        # Desenha peça atual
        for x, y in converter_posição(peça_atual):
            if y > -1:
                pygame.draw.rect(tela, CORES[FORMAS.index(peça_atual.formato) + 1],
                                 (x * TAMANHO_BLOCO, TOPO_TABULEIRO + y * TAMANHO_BLOCO,
                                  TAMANHO_BLOCO, TAMANHO_BLOCO), 0)

        # Exibe pontuação, próxima peça e legenda do autor
        mostrar_texto(tela, f'Pontuação: {pontuação}', 30, 550, 100)
        mostrar_texto(tela, f'Próxima:', 30, 550, 150)
        mostrar_texto(tela, 'Autor: LT', 20, 550, 50)

        # Desenha próxima peça
        for i, linha in enumerate(próxima_peça.imagem):
            for j, char in enumerate(linha):
                if char == '0':
                    pygame.draw.rect(tela, CORES[FORMAS.index(próxima_peça.formato) + 1],
                                     (550 + j * TAMANHO_BLOCO, 200 + i * TAMANHO_BLOCO,
                                      TAMANHO_BLOCO, TAMANHO_BLOCO), 0)

        pygame.display.update()

        # Verifica fim de jogo
        if any(y < 1 for (_, y) in blocos): rodando = False

    # Tela de fim de jogo
    tela.fill((0, 0, 0))
    mostrar_texto(tela, 'Fim de jogo', 60, LARGURA_JANELA // 2 - 150, ALTURA_JANELA // 2 - 30)
    mostrar_texto(tela, f'Pontuação final: {pontuação}', 40, LARGURA_JANELA // 2 - 170, ALTURA_JANELA // 2 + 30)
    pygame.display.update()
    pygame.time.delay(3000)
    pygame.quit()

if __name__ == '__main__':
    main()
