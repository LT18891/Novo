import pygame
import sys

# Inicialização do Pygame
pygame.init()

# Configurações da tela
LARGURA_TELA, ALTURA_TELA = 800, 600
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Ze_palito)")
relogio = pygame.time.Clock()
FPS = 60

# Definição de cores
BRANCO   = (255, 255, 255)
PRETO    = (0, 0, 0)
VERDE    = (0, 255, 0)
VERMELHO = (255, 0, 0)
AZUL     = (0, 0, 255)
AMARELO  = (255, 255, 0)

# ============================================================
# Funções para criar "imagens" usando recursos do Pygame
# ============================================================

def criar_camada_fundo1():
    """
    Cria uma camada de fundo com "montanhas" desenhadas.
    Essa camada ficará mais distante (movimentação lenta).
    """
    camada = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
    camada.fill((20, 20, 50))  # tom de azul escuro
    # Desenha algumas montanhas usando polígonos
    pygame.draw.polygon(camada, (30, 30, 70), [(0, ALTURA_TELA), (200, 300), (400, ALTURA_TELA)])
    pygame.draw.polygon(camada, (30, 30, 70), [(300, ALTURA_TELA), (500, 250), (700, ALTURA_TELA)])
    pygame.draw.polygon(camada, (30, 30, 70), [(600, ALTURA_TELA), (800, 350), (LARGURA_TELA + 200, ALTURA_TELA)])
    return camada

def criar_camada_fundo2():
    """
    Cria uma camada intermediária de fundo, com "árvores" desenhadas.
    """
    camada = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    camada.fill((0, 0, 0, 0))
    # Desenha algumas árvores simples
    pygame.draw.rect(camada, (34, 139, 34), (50, ALTURA_TELA - 150, 30, 150))
    pygame.draw.circle(camada, (34, 139, 34), (65, ALTURA_TELA - 150), 40)
    
    pygame.draw.rect(camada, (34, 139, 34), (300, ALTURA_TELA - 180, 30, 180))
    pygame.draw.circle(camada, (34, 139, 34), (315, ALTURA_TELA - 180), 50)
    
    pygame.draw.rect(camada, (34, 139, 34), (550, ALTURA_TELA - 160, 30, 160))
    pygame.draw.circle(camada, (34, 139, 34), (565, ALTURA_TELA - 160), 45)
    return camada

def criar_camada_fundo3():
    """
    Cria uma camada de fundo com "nuvens" desenhadas.
    Essa camada ficará mais próxima (movimento mais rápido).
    """
    camada = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    camada.fill((0, 0, 0, 0))
    # Desenha nuvens com elipses
    pygame.draw.ellipse(camada, BRANCO, (100, 50, 150, 60))
    pygame.draw.ellipse(camada, BRANCO, (200, 30, 150, 60))
    pygame.draw.ellipse(camada, BRANCO, (500, 70, 200, 80))
    return camada

def criar_sprites_ze_palito():
    """
    Cria uma "sprite sheet" do Zé-Palito com 8 frames.
    Cada frame é gerado desenhando formas (corpo, cabeça, braços) com pequenas variações.
    """
    sprites = []
    for i in range(8):
        superficie = pygame.Surface((64, 64), pygame.SRCALPHA)
        # Corpo: retângulo amarelo
        pygame.draw.rect(superficie, (255, 200, 0), (20, 30, 24, 30))
        # Cabeça: círculo com tom de pele
        pygame.draw.circle(superficie, (255, 220, 180), (32, 20), 12)
        # Braços: variação simples para simular a caminhada
        if i % 2 == 0:
            pygame.draw.line(superficie, PRETO, (20, 40), (0, 50), 4)
            pygame.draw.line(superficie, PRETO, (44, 40), (64, 50), 4)
        else:
            pygame.draw.line(superficie, PRETO, (20, 40), (0, 60), 4)
            pygame.draw.line(superficie, PRETO, (44, 40), (64, 60), 4)
        sprites.append(superficie)
    return sprites

def criar_sprites_inimigo():
    """
    Cria uma "sprite sheet" dos inimigos com 4 frames.
    Cada frame é gerado desenhando um corpo vermelho com "espinhos" e variações simples.
    """
    sprites = []
    for i in range(4):
        superficie = pygame.Surface((64, 64), pygame.SRCALPHA)
        # Corpo do inimigo: retângulo vermelho
        pygame.draw.rect(superficie, (200, 0, 0), (10, 20, 44, 30))
        # Espinhos: desenha dois triângulos no topo
        pygame.draw.polygon(superficie, (150, 0, 0), [(10, 20), (20, 10), (30, 20)])
        pygame.draw.polygon(superficie, (150, 0, 0), [(30, 20), (40, 10), (50, 20)])
        # Variação simples: desenha uma linha extra em um dos lados
        if i % 2 == 0:
            pygame.draw.line(superficie, PRETO, (10, 20), (10, 10), 2)
        else:
            pygame.draw.line(superficie, PRETO, (50, 20), (50, 10), 2)
        sprites.append(superficie)
    return sprites

# ============================================================
# Criação dos recursos do jogo (fundos e sprites)
# ============================================================

fundo_camada1 = criar_camada_fundo1()
fundo_camada2 = criar_camada_fundo2()
fundo_camada3 = criar_camada_fundo3()
camadas_parallax = [
    (fundo_camada1, 0.2),  # camada mais distante (movimento lento)
    (fundo_camada2, 0.5),
    (fundo_camada3, 0.8)
]

# ============================================================
# CLASSE: FundoParallax
# ============================================================
class FundoParallax:
    def __init__(self, camadas):
        """
        camadas: lista de tuplas (imagem, fator_de_velocidade)
        """
        self.camadas = camadas

    def desenhar(self, tela, deslocamento):
        for imagem, fator in self.camadas:
            if imagem:
                # Calcula o deslocamento para a camada atual
                offset_x = deslocamento * fator % imagem.get_width()
                tela.blit(imagem, (-offset_x, 0))
                # Se a imagem não cobrir toda a tela, desenha uma segunda cópia
                if imagem.get_width() - offset_x < LARGURA_TELA:
                    tela.blit(imagem, (imagem.get_width() - offset_x, 0))

fundo = FundoParallax(camadas_parallax)

# ============================================================
# CLASSE: ZéPalito (Personagem Jogador)
# ============================================================
class ZePalito(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprites = criar_sprites_ze_palito()
        self.largura_sprite = 64
        self.altura_sprite = 64
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.velocidade = 5
        self.forca_pulo = 15
        self.gravidade = 0.8
        self.no_chao = False
        self.indice_animacao = 0
        self.timer_animacao = 0
        self.virado_para_direita = True

    def atualizar(self, grupo_plataformas):
        teclas = pygame.key.get_pressed()
        dx = 0
        if teclas[pygame.K_LEFT]:
            dx = -self.velocidade
            self.virado_para_direita = False
        if teclas[pygame.K_RIGHT]:
            dx = self.velocidade
            self.virado_para_direita = True

        # Aplica a gravidade
        self.vel_y += self.gravidade
        if self.vel_y > 10:
            self.vel_y = 10
        dy = self.vel_y

        # Movimento horizontal e verificação de colisões com as plataformas
        self.rect.x += dx
        for plataforma in grupo_plataformas:
            if self.rect.colliderect(plataforma.rect):
                if dx > 0:
                    self.rect.right = plataforma.rect.left
                elif dx < 0:
                    self.rect.left = plataforma.rect.right

        # Movimento vertical e verificação de colisões
        self.rect.y += dy
        self.no_chao = False
        for plataforma in grupo_plataformas:
            if self.rect.colliderect(plataforma.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plataforma.rect.top
                    self.vel_y = 0
                    self.no_chao = True
                elif self.vel_y < 0:
                    self.rect.top = plataforma.rect.bottom
                    self.vel_y = 0

        # Atualiza a animação (variação simples entre frames)
        if dx != 0:
            self.timer_animacao += 1
            if self.timer_animacao >= 5:
                self.timer_animacao = 0
                self.indice_animacao = (self.indice_animacao + 1) % len(self.sprites)
                self.image = self.sprites[self.indice_animacao]
        else:
            self.indice_animacao = 0
            self.image = self.sprites[self.indice_animacao]

        # Inverte a imagem se o personagem estiver virado para a esquerda
        if not self.virado_para_direita:
            self.image = pygame.transform.flip(self.sprites[self.indice_animacao], True, False)

    def pular(self):
        if self.no_chao:
            self.vel_y = -self.forca_pulo

# ============================================================
# CLASSE: Plataforma
# ============================================================
class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill(VERDE)
        self.rect = self.image.get_rect(topleft=(x, y))

# ============================================================
# CLASSE: Inimigo
# ============================================================
class Inimigo(pygame.sprite.Sprite):
    def __init__(self, x, y, limite_esquerdo, limite_direito, velocidade):
        super().__init__()
        self.sprites = criar_sprites_inimigo()
        self.largura_sprite = 64
        self.altura_sprite = 64
        self.image = self.sprites[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.limite_esquerdo = limite_esquerdo
        self.limite_direito = limite_direito
        self.velocidade = velocidade
        self.indice_animacao = 0
        self.timer_animacao = 0
        self.virado_para_direita = True

    def atualizar(self):
        self.rect.x += self.velocidade
        # Inverte a direção ao atingir os limites da área de patrulha
        if self.rect.left < self.limite_esquerdo or self.rect.right > self.limite_direito:
            self.velocidade *= -1
            self.virado_para_direita = not self.virado_para_direita

        self.timer_animacao += 1
        if self.timer_animacao >= 10:
            self.timer_animacao = 0
            self.indice_animacao = (self.indice_animacao + 1) % len(self.sprites)
            self.image = self.sprites[self.indice_animacao]
        if not self.virado_para_direita:
            self.image = pygame.transform.flip(self.sprites[self.indice_animacao], True, False)

# ============================================================
# CLASSE: Nível
# ============================================================
class Nivel:
    def __init__(self, ze_palito):
        self.grupo_plataformas = pygame.sprite.Group()
        self.grupo_inimigos = pygame.sprite.Group()
        self.ze_palito = ze_palito

        # Dados simples do nível: (x, y, largura, altura)
        dados_nivel = [
            (0, ALTURA_TELA - 40, 2000, 40),   # Chão
            (300, ALTURA_TELA - 150, 200, 20),
            (600, ALTURA_TELA - 250, 150, 20),
            (900, ALTURA_TELA - 350, 200, 20),
            (1200, ALTURA_TELA - 200, 200, 20),
            (1500, ALTURA_TELA - 300, 150, 20)
        ]
        for dado in dados_nivel:
            plat = Plataforma(*dado)
            self.grupo_plataformas.add(plat)

        # Cria inimigos em pontos estratégicos do nível
        inimigo1 = Inimigo(350, ALTURA_TELA - 190, 300, 500, 2)
        inimigo2 = Inimigo(950, ALTURA_TELA - 390, 900, 1100, 3)
        self.grupo_inimigos.add(inimigo1, inimigo2)

        # Variável que controla o deslocamento do mundo (scrolling)
        self.deslocamento_mundo = 0

    def atualizar(self):
        # Sistema de câmera: se o Zé-Palito se aproximar das bordas da tela, desloca o cenário
        centro_ze = self.ze_palito.rect.centerx
        if centro_ze > 600:
            deslocar = centro_ze - 600
            self.ze_palito.rect.x -= deslocar
            self.deslocamento_mundo -= deslocar
            for plataforma in self.grupo_plataformas:
                plataforma.rect.x -= deslocar
            for inimigo in self.grupo_inimigos:
                inimigo.rect.x -= deslocar
        elif centro_ze < 200:
            deslocar = 200 - centro_ze
            self.ze_palito.rect.x += deslocar
            self.deslocamento_mundo += deslocar
            for plataforma in self.grupo_plataformas:
                plataforma.rect.x += deslocar
            for inimigo in self.grupo_inimigos:
                inimigo.rect.x += deslocar

        # Atualiza os inimigos
        for inimigo in self.grupo_inimigos:
            inimigo.atualizar()

    def desenhar(self, tela):
        self.grupo_plataformas.draw(tela)
        self.grupo_inimigos.draw(tela)

# ============================================================
# Instanciação dos objetos principais do jogo
# ============================================================
ze_palito = ZePalito(100, ALTURA_TELA - 100)
nivel = Nivel(ze_palito)

# ============================================================
# LOOP PRINCIPAL DO JOGO
# ============================================================
jogo_rodando = True
while jogo_rodando:
    relogio.tick(FPS)
    
    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jogo_rodando = False
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                ze_palito.pular()

    # Atualiza o Zé-Palito e o nível
    ze_palito.atualizar(nivel.grupo_plataformas)
    nivel.atualizar()

    # Verifica colisões entre o Zé-Palito e os inimigos
    if pygame.sprite.spritecollide(ze_palito, nivel.grupo_inimigos, False):
        print("Você foi atingido por um inimigo!")
        # Reinicia a posição do Zé-Palito e recria o nível
        ze_palito.rect.topleft = (100, ALTURA_TELA - 100)
        nivel.deslocamento_mundo = 0
        nivel = Nivel(ze_palito)

    # Desenha o cenário
    tela.fill(AZUL)  # Fundo de cor azul
    fundo.desenhar(tela, nivel.deslocamento_mundo)
    nivel.desenhar(tela)
    tela.blit(ze_palito.image, ze_palito.rect)
    
    pygame.display.flip()

pygame.quit()
sys.exit()
