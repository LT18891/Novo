# -*- coding: utf-8 -*-
# Jogo: Bruxinha vs Demônios 
# Para rodar:
#   pip install pygame
#   python jogo.py
#autor: Luiz Tiago Wilcke 
import os, sys, math, random
import pygame
from pygame import Rect
from pygame.math import Vector2 as Vetor

# Garante caminhos relativos ao arquivo
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ------------------ Configurações ------------------
LARGURA, ALTURA = 960, 540
FPS_ALVO = 60
GRAVIDADE = 2200.0
PISO_Y = 420
VELOCIDADE = 260
PULO = 720
RECARGA_SEG = 0.18
DANO_TIRO = 25
VIDA_JOGADOR = 100
VIDA_DEMONIO = 70

# Texturas globais (preenchidas após init)
TEX = {}

# --------- Utilidades ----------
def carregar_animacao(pasta, prefixo):
    frames = []
    i = 0
    while True:
        caminho = os.path.join("assets", pasta, f"{prefixo}_{i}.png")
        if not os.path.exists(caminho):
            break
        img = pygame.image.load(caminho).convert_alpha()
        frames.append(img)
        i += 1
    return frames

def desenhar_texto(tela, txt, x, y, tamanho=24, cor=(230,240,255)):
    fonte = pygame.font.SysFont("consolas", tamanho, bold=True)
    img = fonte.render(txt, True, cor)
    tela.blit(img, (x,y))

def clamp(v,a,b): return max(a, min(b, v))

def carregar_recursos():
    """Chamar APÓS pygame.init() e set_mode."""
    TEX['tiro']   = pygame.image.load(os.path.join("assets","efeitos","tiro.png")).convert_alpha()
    TEX['muzzle'] = pygame.image.load(os.path.join("assets","efeitos","muzzle.png")).convert_alpha()
    TEX['bg0']    = pygame.image.load(os.path.join("assets","fundos","parallax_0.png")).convert()
    TEX['bg1']    = pygame.image.load(os.path.join("assets","fundos","parallax_1.png")).convert()
    TEX['chao']   = pygame.image.load(os.path.join("assets","chao.png")).convert()

# ----------------- Classes -----------------
class Animacao:
    def __init__(self, frames, dur=0.08):
        self.frames = frames
        self.dur = dur
        self.t = 0.0
        self.i = 0
    def passo(self, dt):
        if len(self.frames) <= 1: return
        self.t += dt
        while self.t >= self.dur:
            self.t -= self.dur
            self.i = (self.i+1)%len(self.frames)
    def frame(self): return self.frames[self.i]

class Particula:
    def __init__(self, pos, vel, vida, raio, cor):
        self.pos = Vetor(pos)
        self.vel = Vetor(vel)
        self.vida = vida
        self.raio = raio
        self.cor = cor
    def update(self, dt):
        self.vida -= dt
        self.pos += self.vel*dt
        self.vel *= 0.98
    def draw(self, tela, off):
        if self.vida>0:
            pygame.draw.circle(tela, self.cor, (int(self.pos.x-off.x), int(self.pos.y-off.y)), max(1,int(self.raio)))

class Tiro:
    def __init__(self, pos, dirx):
        self.img = TEX['tiro']
        self.pos = Vetor(pos)
        self.vel = Vetor(650*dirx, random.uniform(-20,20))
        self.vivo = True
        self.rect = self.img.get_rect(center=self.pos)
        self.tempo = 0.0
    def update(self, dt, demônios):
        self.tempo += dt
        self.pos += self.vel*dt
        self.rect.center = self.pos
        if self.pos.x < -50 or self.pos.x>4000:
            self.vivo = False
        # colisão simples
        for d in demônios:
            if d.vivo and self.rect.colliderect(d.rect.inflate(-20,-20)):
                d.vida -= DANO_TIRO
                d.tomar_dano()
                self.vivo = False
                break
    def draw(self, tela, off):
        tela.blit(self.img, (self.rect.x-off.x, self.rect.y-off.y))

class Jogador:
    def __init__(self, x, y):
        self.pos = Vetor(x,y)
        self.vel = Vetor(0,0)
        self.no_chao = False
        self.dir = 1
        self.vida = VIDA_JOGADOR

        self.anim = {
            "idle":  Animacao(carregar_animacao("bruxa","bruxa_idle")),
            "andar": Animacao(carregar_animacao("bruxa","bruxa_andar"), dur=0.07),
            "atirar":Animacao(carregar_animacao("bruxa","bruxa_atirar"), dur=0.06),
            "pular": Animacao(carregar_animacao("bruxa","bruxa_pular"), dur=0.08)
        }
        self.estado = "idle"
        self.recarga = 0.0
        self.shake = 0.0

    def atualizar(self, dt, teclas, tiros, particulas):
        acel = 0
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:  acel -= 1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]: acel += 1
        self.vel.x = acel * VELOCIDADE
        if acel != 0: self.dir = 1 if acel>0 else -1

        if (teclas[pygame.K_w] or teclas[pygame.K_UP] or teclas[pygame.K_SPACE]) and self.no_chao:
            self.vel.y = -PULO
            self.no_chao = False

        self.vel.y += GRAVIDADE*dt
        self.pos += self.vel*dt

        if self.pos.y >= PISO_Y:
            self.pos.y = PISO_Y
            self.vel.y = 0
            self.no_chao = True

        if not self.no_chao: self.estado = "pular"
        elif abs(self.vel.x)>1: self.estado = "andar"
        else: self.estado = "idle"

        self.recarga -= dt
        if (teclas[pygame.K_j] or teclas[pygame.K_z]) and self.recarga<=0:
            self.estado = "atirar"
            self.recarga = RECARGA_SEG
            origem = self.pos + Vetor(38*self.dir, -18)
            tiros.append(Tiro(origem, self.dir))
            # recuo + partículas
            self.shake = 0.15
            for i in range(8):
                ang = random.uniform(-0.3,0.3)
                particulas.append(Particula(origem, (random.uniform(180,260)*math.cos(ang), random.uniform(-50,50)*math.sin(ang)), 0.25, 2, (120,255,140)))

        self.anim[self.estado].passo(dt)
        self.shake = max(0.0, self.shake - dt*1.5)

    def desenhar(self, tela, off):
        img = self.anim[self.estado].frame()
        if self.dir==-1:
            img = pygame.transform.flip(img, True, False)
        pos = (int(self.pos.x-img.get_width()//2-off.x), int(self.pos.y-img.get_height()-12-off.y))
        tela.blit(img, pos)

        # muzzle quando atirando
        if self.estado=="atirar" and self.recarga>RECARGA_SEG-0.09:
            mx = self.pos.x + 42*self.dir - off.x - (TEX['muzzle'].get_width() if self.dir==1 else 0)
            my = self.pos.y - 26 - off.y
            imgm = TEX['muzzle'] if self.dir==1 else pygame.transform.flip(TEX['muzzle'], True, False)
            tela.blit(imgm, (int(mx), int(my)))

        # barra de vida
        pygame.draw.rect(tela, (30,30,40), (20,20, 210, 18), border_radius=6)
        pygame.draw.rect(tela, (120,255,140), (22,22, int( (self.vida/VIDA_JOGADOR)*206 ), 14), border_radius=6)

class Demonio:
    def __init__(self, x, y):
        self.pos = Vetor(x,y)
        self.vel = Vetor(0,0)
        self.dir = -1
        self.vida = VIDA_DEMONIO
        self.vivo = True
        self.t_atk = 0.0

        self.anim_andar = Animacao(carregar_animacao("demonio","demonio_andar"), dur=0.09)
        self.anim_atk = Animacao(carregar_animacao("demonio","demonio_atacar"), dur=0.1)
        self.estado = "andar"
        self.rect = self.anim_andar.frame().get_rect(center=(x,y-20))

    def tomar_dano(self):
        self.estado = "andar"
        self.dir *= -1

    def update(self, dt, jogador, particulas):
        if not self.vivo: return
        dist = jogador.pos.x - self.pos.x
        self.dir = 1 if dist>0 else -1
        self.vel.x = clamp(abs(dist)*0.5, 30, 140) * self.dir
        self.pos.x += self.vel.x*dt

        if abs(dist) < 70 and abs(jogador.pos.y - self.pos.y)<50:
            self.estado = "atacar"
            self.t_atk += dt
            if self.t_atk>0.5:
                self.t_atk = 0
                jogador.vida -= 10
                for i in range(8):
                    particulas.append(Particula(self.pos, (random.uniform(-60,60), random.uniform(-80,-10)), 0.4, 3, (240,80,80)))
        else:
            self.estado = "andar"
            self.t_atk = 0

        if self.vida<=0:
            self.vivo = False
            for i in range(14):
                particulas.append(Particula(self.pos, (random.uniform(-120,120), random.uniform(-80,-10)), 0.6, 4, (240,80,80)))

        (self.anim_atk if self.estado=="atacar" else self.anim_andar).passo(dt)
        frm = self.anim_atk.frame() if self.estado=="atacar" else self.anim_andar.frame()
        self.rect = frm.get_rect(center=(self.pos.x, self.pos.y-20))

    def draw(self, tela, off):
        frm = self.anim_atk.frame() if self.estado=="atacar" else self.anim_andar.frame()
        img = pygame.transform.flip(frm, True, False) if self.dir==-1 else frm
        tela.blit(img, (self.rect.x-off.x, self.rect.y-off.y))

# ----------------- Mundo / Câmera / Luz -----------------
def desenhar_fundo(tela, cam_x):
    p0, p1 = TEX['bg0'], TEX['bg1']
    for i in range(-1, 5):
        x0 = int(- (cam_x*0.2) % p0.get_width()) + i*p0.get_width()
        x1 = int(- (cam_x*0.5) % p1.get_width()) + i*p1.get_width()
        tela.blit(p1, (x1,0))
        tela.blit(p0, (x0,0))

def desenhar_chao(tela, cam_x):
    tile = TEX['chao']
    y = PISO_Y + 12
    w = tile.get_width()
    for i in range(-1, 40):
        x = int(- (cam_x) % w) + i*w
        tela.blit(tile, (x, y))

def mascara_luz(tamanho, pontos):
    """
    Cria uma máscara de luz para multiplicar sobre a cena.
    - Preenche com cinza escuro (escurece o cenário).
    - Para cada ponto de luz, desenha um gradiente branco (255) no centro
      decaindo até ~30 nas bordas, e combina usando BLEND_RGBA_MAX.
    """
    s = pygame.Surface(tamanho, pygame.SRCALPHA)
    s.fill((25,25,25,255))  # bem escuro fora das luzes
    for (x,y,raio) in pontos:
        raio = int(max(10, raio))
        grad = pygame.Surface((raio*2, raio*2), pygame.SRCALPHA)
        # desenha do maior para o menor, ficando mais claro no centro
        for r in range(raio, 0, -4):
            t = r/raio  # 0->centro, 1->borda (aqui r decresce)
            g = int(25 + 230*(t))  # 255 no centro, ~25 na borda
            if g>255: g=255
            pygame.draw.circle(grad, (g,g,g,255), (raio,raio), r)
        # Combina pegando o máximo (para luzes sobrepostas somarem)
        s.blit(grad, (int(x-raio), int(y-raio)), special_flags=pygame.BLEND_RGBA_MAX)
    return s

# ----------------- Loop principal -----------------
def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Bruxinha vs Demônios")
    relogio = pygame.time.Clock()

    # IMPORTANTE: carregar imagens após init/set_mode
    carregar_recursos()

    jogador = Jogador(180, PISO_Y)
    tiros = []
    dem = [Demonio(700+i*260, PISO_Y) for i in range(4)]
    particulas = []

    camera = Vetor(0,0)
    pontos = 0
    fim = False

    while True:
        dt = min(1/30, relogio.tick(FPS_ALVO)/1000.0)

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_ESCAPE]:
            pygame.quit(); sys.exit()

        if not fim:
            jogador.atualizar(dt, teclas, tiros, particulas)
            for t in tiros[:]:
                t.update(dt, dem)
                if not t.vivo:
                    tiros.remove(t)
                    pontos += 5
            for d in dem[:]:
                d.update(dt, jogador, particulas)
                if not d.vivo:
                    dem.remove(d)
                    pontos += 20

            for p in particulas[:]:
                p.update(dt)
                if p.vida<=0:
                    particulas.remove(p)

            if jogador.vida <= 0:
                fim = True

        alvo = Vetor( clamp(jogador.pos.x-LARGURA*0.4, 0, 9999), 0 )
        camera += (alvo - camera) * 5.0 * dt
        if jogador.shake>0:
            camera += Vetor( random.uniform(-4,4), random.uniform(-4,4) )

        tela.fill((12,14,20))
        desenhar_fundo(tela, camera.x)
        desenhar_chao(tela, camera.x)

        for t in tiros: t.draw(tela, camera)
        for d in dem: d.draw(tela, camera)
        jogador.desenhar(tela, camera)
        for p in particulas: p.draw(tela, camera)

        pontos_luz = [(jogador.pos.x-camera.x, jogador.pos.y-20, 210)]
        for t in tiros:
            pontos_luz.append((t.pos.x-camera.x, t.pos.y-10, 110))
        tela.blit(mascara_luz((LARGURA,ALTURA), pontos_luz), (0,0), special_flags=pygame.BLEND_RGBA_MULT)

        desenhar_texto(tela, f"Pontos: {pontos}", 760, 20, 24)
        if fim:
            desenhar_texto(tela, "Derrota! Aperte ESC para sair.", 280, 240, 28, (255,120,120))
        elif len(dem)==0:
            desenhar_texto(tela, "Vitória! Todos os demônios caíram!", 250, 240, 28, (120,255,140))

        pygame.display.flip()

if __name__ == "__main__":
    main()
