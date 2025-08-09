#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Príncipe do Deserto — Fase 1 (inspirado em plataforma árabe clássica)
Autor: Luiz Tiago Wilcke

Atualizações:
- Correção de colisão vertical (bounding box central com raio correto)
- Pulo funcional (coyote time + jump buffer)
- Tiro 8-direções (↑, ↓, diagonais) com X
- Dragões que cospem fogo (rajadas e bolas em arco)
- Pequenos ajustes de física e IA
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

import pygame
from pygame import Rect
from pygame.math import Vector2 as V2

# ---------------- Configurações gerais ----------------
LARGURA, ALTURA = 960, 540
FPS = 60
TAM_TILE = 32

# Paleta
AREIA = (229, 200, 148)
CEU1  = (12, 9, 35)
CEU2  = (49, 23, 85)
DUNA1 = (170, 140, 90)
DUNA2 = (140, 110, 70)
CIDADE= (70, 60, 80)
CASTELO=(120, 100, 80)
TELHADO=(165, 60, 50)
PEDRA = (98, 82, 70)
OURO  = (255, 210, 70)
VERDE = (60, 180, 120)
VERM  = (200, 60, 60)
LARANJA = (255, 140, 40)
BRANCO=(240, 240, 240)
PRETO = (0, 0, 0)

# ---------------- Mapa da fase (layout original) ----------------
# Legenda:
#   # bloco sólido, - plataforma (um sentido), ^ espinho, o moeda, > porta/saída
#   @ jogador spawn, g guarda, d dragão cuspidor de fogo
MAPA_TXT = """
................................................................
................................................................
......................................d.....................>...
.........................o......................................
......................---...........................----........
..............o.................................................
..............#####....................o....................o...
.....o......................----.............................o..
###########...........o.......................g.............d...
..........#.....................o..................----.........
..........#..........---........................................
..........#..............................................o......
..........#..@..................................................
..........##########################.............#####..........
.....................o.....................o....................
..................#######..............#########................
...........o....................................................
.......#########.............g....................o.............
......................o.........................................
###############....########################.....#################
"""

# ---------------- Tipos de tile ----------------
SOLIDO = '#'
PLATAF = '-'
ESPINHO= '^'
MOEDA  = 'o'
PORTA  = '>'
SPAWN  = '@'
GUARDA = 'g'
DRAGAO = 'd'
VAZIO  = '.'

# --------------- Utilidades --------------------
def clamp(x, a, b):
    return a if x < a else b if x > b else x

def desenhar_padrao_tijolo(surf, cor_fundo, cor_linha):
    surf.fill(cor_fundo)
    w, h = surf.get_size()
    esp = 8
    for y in range(0, h, esp):
        desloc = (y // esp) % 2 * (esp // 2)
        for x in range(-desloc, w, esp):
            pygame.draw.rect(surf, cor_linha, (x, y, esp-1, 1))
    for x in range(0, w, esp):
        pygame.draw.line(surf, cor_linha, (x, 0), (x, h), 1)

def desenhar_padrao_madeira(surf):
    surf.fill((120, 80, 40))
    w, h = surf.get_size()
    for y in range(0, h, 6):
        pygame.draw.line(surf, (90,60,30), (0,y*6), (w,y*6), 1)

# --------------- Camadas de fundo (parallax) ---------------
def desenhar_ceu(screen):
    grad = pygame.Surface((1, ALTURA))
    for y in range(ALTURA):
        t = y / ALTURA
        r = int(CEU1[0]*(1-t) + CEU2[0]*t)
        g = int(CEU1[1]*(1-t) + CEU2[1]*t)
        b = int(CEU1[2]*(1-t) + CEU2[2]*t)
        grad.set_at((0, y), (r, g, b))
    grad = pygame.transform.scale(grad, (LARGURA, ALTURA))
    screen.blit(grad, (0,0))

def desenhar_dunas(screen, cam_x):
    for i, (cor, vel) in enumerate(((DUNA1, 0.15), (DUNA2, 0.25))):
        ybase = ALTURA*0.75 + i*10
        pontos = []
        for x in range(-100, LARGURA+100, 30):
            xx = x + int(-cam_x*vel) % 200
            y = ybase + 20*math.sin(0.008*(x + i*200))
            pontos.append((xx, y))
        pontos = [(-200, ALTURA), *pontos, (LARGURA+200, ALTURA)]
        pygame.draw.polygon(screen, cor, pontos)

def desenhar_silhuetas(screen, cam_x):
    base_y = ALTURA*0.65
    random.seed(1234)
    for i, vel in enumerate((0.35, 0.5)):
        off = int(-cam_x*vel)
        for k in range(-3, 6):
            x0 = k*220 + (off % 220)
            h = 80 + 50*((i+k)%3==0)
            corpo = Rect(x0, base_y - h - i*10, 160, h)
            pygame.draw.rect(screen, CIDADE if i==0 else CASTELO, corpo)
            pygame.draw.circle(screen, CASTELO, (x0+40, corpo.top), 10)
            pygame.draw.circle(screen, CASTELO, (x0+120, corpo.top+5), 12)
            for j in range(4):
                pygame.draw.rect(screen, (30,25,40), (x0+15+j*35, corpo.top+20, 10, 16))

# --------------- Entidades --------------------
@dataclass
class Projetil:
    pos: V2
    vel: V2
    tempo: float = 0.0
    vivo: bool = True

    def atualizar(self, dt: float, colisores: List[Rect]):
        self.pos += self.vel * dt
        self.tempo += dt
        caixa = Rect(int(self.pos.x)-4, int(self.pos.y)-2, 8, 4)
        for c in colisores:
            if caixa.colliderect(c):
                self.vivo = False
                break
        if not (-1000 < self.pos.x < 100000):
            self.vivo = False

    def desenhar(self, tela, cam):
        r = Rect(int(self.pos.x - cam.x)-4, int(self.pos.y - cam.y)-2, 8, 4)
        pygame.draw.rect(tela, BRANCO, r)

@dataclass
class BolaDeFogo:
    pos: V2
    vel: V2
    grav: float = 700.0
    vida: float = 3.0
    vivo: bool = True

    def atualizar(self, dt: float, colisores: List[Rect]):
        self.vel.y += self.grav * dt
        self.pos += self.vel * dt
        self.vida -= dt
        caixa = Rect(int(self.pos.x)-5, int(self.pos.y)-5, 10, 10)
        for c in colisores:
            if caixa.colliderect(c):
                self.vivo = False
                break
        if self.vida <= 0 or not (-2000 < self.pos.x < 100000) or self.pos.y > 20000:
            self.vivo = False

    def desenhar(self, tela, cam):
        x = int(self.pos.x - cam.x)
        y = int(self.pos.y - cam.y)
        pygame.draw.circle(tela, LARANJA, (x, y), 6)
        pygame.draw.circle(tela, VERM, (x, y), 6, 2)

@dataclass
class InimigoGuarda:
    pos: V2
    vel: V2 = field(default_factory=lambda: V2(0,0))
    virado: int = 1
    vivo: bool = True
    vida: int = 2

    def atualizar(self, dt, mundo):
        if not self.vivo: return
        g = 1600
        self.vel.y += g*dt
        frente = self.pos + V2(self.virado*18, 24)
        if not mundo.tem_chao(frente + V2(0, 2)):
            self.virado *= -1
        self.vel.x = 100 * self.virado
        self.pos, self.vel = mundo.mover_com_colisao(self.pos, self.vel, dt, raio=12)
        for p in mundo.projeteis:
            if (p.pos - self.pos).length() < 18 and p.vivo:
                p.vivo = False
                self.vida -= 1
                if self.vida <= 0:
                    self.vivo = False

    def desenhar(self, tela, cam):
        if not self.vivo: return
        cx, cy = int(self.pos.x - cam.x), int(self.pos.y - cam.y)
        corpo = Rect(cx-12, cy-24, 24, 32)
        pygame.draw.rect(tela, (90,70,120), corpo)
        elmo = Rect(cx-12, cy-32, 24, 10)
        pygame.draw.rect(tela, (60,50,90), elmo)
        xesp = cx + (14 if self.virado>0 else -18)
        pygame.draw.line(tela, BRANCO, (xesp, cy-10), (xesp, cy+10), 2)

@dataclass
class Dragao:
    pos: V2
    fase: float = 0.0
    virado: int = -1
    vivo: bool = True
    cooldown: float = 0.0

    def atualizar(self, dt, mundo, jogador):
        if not self.vivo: return
        # paira em movimento senoidal leve
        self.fase += dt
        self.pos.y += math.sin(self.fase*1.3) * 10 * dt
        # vira para o jogador
        self.virado = 1 if (jogador.pos.x > self.pos.x) else -1
        # atira fogo em rajadas
        self.cooldown -= dt
        dist = (jogador.pos - self.pos).length()
        if self.cooldown <= 0 and dist < 800:
            self.disparar(mundo, jogador)
            self.cooldown = 2.2

    def disparar(self, mundo, jogador):
        # 1) rajada de 3 bolas em leque
        base = (jogador.pos - self.pos).normalize() if (jogador.pos - self.pos).length() > 1 else V2(self.virado, -0.1)
        angulos = (-0.2, 0.0, 0.2)
        for a in angulos:
            dirv = V2(base.x*math.cos(a) - base.y*math.sin(a),
                      base.x*math.sin(a) + base.y*math.cos(a))
            v0 = dirv * 260 + V2(0, -40)
            mundo.fogos.append(BolaDeFogo(self.pos + V2(self.virado*24, -8), v0))
        # 2) jato curto horizontal
        for j in range(4):
            desloc = V2(self.virado*(30+12*j), -6)
            mundo.fogos.append(BolaDeFogo(self.pos + desloc, V2(self.virado*(220+20*j), -20)))

    def desenhar(self, tela, cam):
        if not self.vivo: return
        cx, cy = int(self.pos.x - cam.x), int(self.pos.y - cam.y)
        cor_corpo = (60, 110, 90)
        # corpo
        pygame.draw.ellipse(tela, cor_corpo, (cx-28, cy-16, 56, 32))
        # cabeça
        pygame.draw.circle(tela, cor_corpo, (cx + (24*self.virado), cy-6), 10)
        # asa
        asa = [(cx-10, cy-2), (cx-40, cy-18), (cx-16, cy-6)]
        pygame.draw.polygon(tela, (80,150,120), asa)
        pygame.draw.polygon(tela, PRETO, asa, 2)
        # chifres/olho
        pygame.draw.line(tela, BRANCO, (cx + (24*self.virado), cy-12), (cx + (28*self.virado), cy-18), 2)
        pygame.draw.circle(tela, BRANCO, (cx + (28*self.virado), cy-8), 2)

@dataclass
class Jogador:
    pos: V2
    vel: V2 = field(default_factory=lambda: V2(0,0))
    no_chao: bool = False
    pulos: int = 0
    cron_coyote: float = 0.0
    cron_buffer_pulo: float = 0.0
    pode_atirar: float = 0.0
    invul: float = 0.0
    vida: int = 3
    moedas: int = 0
    rolando: float = 0.0
    virado: int = 1

    def atualizar(self, dt, teclas, mundo):
        # input horizontal
        direcao = 0
        if teclas[pygame.K_LEFT]: direcao -= 1
        if teclas[pygame.K_RIGHT]: direcao += 1
        vmax = 230 if self.rolando<=0 else 300
        ax = 1600
        alvo = direcao * vmax
        if abs(alvo - self.vel.x) < ax*dt: self.vel.x = alvo
        else: self.vel.x += ax*dt * (1 if alvo>self.vel.x else -1)
        if direcao != 0: self.virado = direcao

        # gravidade
        g = 1600
        self.vel.y += g*dt
        if self.rolando > 0: self.rolando -= dt

        # coyote/buffer
        if self.no_chao:
            self.cron_coyote = 0.12
            self.pulos = 1
        else:
            self.cron_coyote -= dt
        self.cron_buffer_pulo -= dt

        # pulo
        if self.cron_buffer_pulo > 0 and (self.cron_coyote > 0 or self.pulos>0):
            self.vel.y = -520
            self.no_chao = False
            self.cron_coyote = 0
            self.cron_buffer_pulo = 0
            self.pulos -= 1

        # mover com colisão (CAIXA CENTRAL CORRIGIDA)
        self.pos, self.vel, toque_chao = mundo.mover_com_colisao_jogador(self.pos, self.vel, dt, raio=12)
        self.no_chao = toque_chao

        # coleta moedas
        self.moedas += mundo.coletar_moedas_em(self.pos, raio=14)

        # dano espinho
        if mundo.em_espinho(self.pos) and self.invul<=0:
            self.vida -= 1
            self.invul = 1.0
            self.vel += V2(-self.virado*80, -300)
        if self.invul>0: self.invul -= dt

        # dano fogo
        if mundo.fogo_atinge_jogador(self.pos) and self.invul<=0:
            self.vida -= 1
            self.invul = 1.0
            self.vel += V2(-self.virado*80, -300)

        # cooldown projétil
        if self.pode_atirar > 0: self.pode_atirar -= dt

    def requisitar_pulo(self):
        self.cron_buffer_pulo = 0.12

    def requisitar_tiro(self, projeteis, teclas):
        if self.pode_atirar > 0: 
            return
        # Direção de tiro (8 direções)
        dx = (1 if self.virado>0 else -1)
        dy = 0
        if teclas[pygame.K_UP]:    dy -= 1
        if teclas[pygame.K_DOWN]:  dy += 1
        if not (teclas[pygame.K_LEFT] or teclas[pygame.K_RIGHT]):
            # parado, permite virar apenas pelo up/down
            if teclas[pygame.K_LEFT]:  dx = -1
            if teclas[pygame.K_RIGHT]: dx =  1
        vdir = V2(dx, dy)
        if vdir.length() == 0:
            vdir = V2(self.virado, 0)
        vdir = vdir.normalize()
        projeteis.append(Projetil(self.pos + V2(self.virado*16, -6), vdir*420))
        self.pode_atirar = 0.22

    def requisitar_rolar(self):
        if self.no_chao and self.rolando<=0:
            self.rolando = 0.35

    def desenhar(self, tela, cam):
        cx, cy = int(self.pos.x - cam.x), int(self.pos.y - cam.y)
        corpo = Rect(cx-12, cy-24, 24, 32)
        cor = (220,190,120) if self.invul<=0 or int(self.invul*10)%2==0 else (220,120,120)
        pygame.draw.rect(tela, cor, corpo, border_radius=4)
        pygame.draw.rect(tela, (90,30,30), (cx-12, cy-18, 24, 10))
        pygame.draw.rect(tela, (40,60,120), (cx-12, cy-8, 24, 16))
        xlen = cx + (10 if self.virado>0 else -10)
        pygame.draw.line(tela, (200, 50, 50), (cx, cy-20), (xlen, cy-25), 3)

# --------------- Mundo / colisões ----------------
class Mundo:
    def __init__(self, mapa_txt: str):
        linhas = [l for l in mapa_txt.strip('\n').split('\n')]
        self.h = len(linhas)
        self.w = len(linhas[0])
        self.tiles = linhas
        self.solidos: List[Rect] = []
        self.plataformas: List[Rect] = []
        self.espinhos: List[Rect] = []
        self.moedas: Dict[Tuple[int,int], bool] = {}
        self.porta: Rect | None = None
        self.guardas: List[InimigoGuarda] = []
        self.dragoes: List[Dragao] = []
        self.projeteis: List[Projetil] = []
        self.fogos: List[BolaDeFogo] = []
        self.spawn = V2(64, 64)

        for j, linha in enumerate(self.tiles):
            for i, ch in enumerate(linha):
                x, y = i*TAM_TILE, j*TAM_TILE
                r = Rect(x, y, TAM_TILE, TAM_TILE)
                if ch == SOLIDO:
                    self.solidos.append(r)
                elif ch == PLATAF:
                    self.plataformas.append(r)
                elif ch == ESPINHO:
                    self.espinhos.append(r)
                elif ch == MOEDA:
                    self.moedas[(i,j)] = True
                elif ch == PORTA:
                    self.porta = r
                elif ch == SPAWN:
                    self.spawn = V2(x+TAM_TILE/2, y+TAM_TILE/2)
                elif ch == GUARDA:
                    self.guardas.append(InimigoGuarda(V2(x+TAM_TILE/2, y)))
                elif ch == DRAGAO:
                    self.dragoes.append(Dragao(V2(x+TAM_TILE/2, y - 20)))

        self.tx_solid = pygame.Surface((TAM_TILE, TAM_TILE))
        desenhar_padrao_tijolo(self.tx_solid, PEDRA, (70,60,55))
        self.tx_plat = pygame.Surface((TAM_TILE, 8), pygame.SRCALPHA)
        desenhar_padrao_madeira(self.tx_plat)
        self.tx_esp = pygame.Surface((TAM_TILE, TAM_TILE), pygame.SRCALPHA)
        for k in range(0, TAM_TILE, 8):
            pygame.draw.polygon(self.tx_esp, VERM, [(k, TAM_TILE),(k+4, TAM_TILE-12),(k+8, TAM_TILE)], 0)
        self.tx_moeda = pygame.Surface((TAM_TILE, TAM_TILE), pygame.SRCALPHA)
        pygame.draw.circle(self.tx_moeda, OURO, (TAM_TILE//2, TAM_TILE//2), 6)
        pygame.draw.circle(self.tx_moeda, (200,160,40), (TAM_TILE//2, TAM_TILE//2), 6, 2)

    def retangulos_visiveis(self, cam):
        ini_i = max(0, int(cam.x // TAM_TILE) - 2)
        fim_i = min(self.w, int((cam.x+LARGURA)//TAM_TILE) + 3)
        ini_j = max(0, int(cam.y // TAM_TILE) - 2)
        fim_j = min(self.h, int((cam.y+ALTURA)//TAM_TILE) + 3)
        return ini_i, fim_i, ini_j, fim_j

    def tem_chao(self, ponto: V2) -> bool:
        r = Rect(int(ponto.x)-1, int(ponto.y), 2, 2)
        for b in self.solidos:
            if r.colliderect(b): return True
        for p in self.plataformas:
            if r.colliderect(Rect(p.x, p.y, p.w, 6)): return True
        return False

    def mover_com_colisao(self, pos, vel, dt, raio=12):
        pos = pos.copy(); vel = vel.copy()
        # Eixo Y
        pos.y += vel.y * dt
        caixa = Rect(int(pos.x - raio), int(pos.y - raio), 2*raio, 2*raio)  # CORRIGIDO
        for b in self.solidos:
            if caixa.colliderect(b):
                if vel.y > 0 and caixa.bottom > b.top:
                    pos.y = b.top - raio  # CORRIGIDO
                    vel.y = 0
                    caixa.bottom = b.top
                elif vel.y < 0 and caixa.top < b.bottom:
                    pos.y = b.bottom + raio  # CORRIGIDO
                    vel.y = 0
                    caixa.top = b.bottom
        for p in self.plataformas:
            tope = Rect(p.x, p.y, p.w, 6)
            if vel.y > 0 and caixa.bottom >= tope.top and caixa.bottom - vel.y*dt <= tope.top and caixa.centerx in range(p.x, p.right):
                pos.y = tope.top - raio  # CORRIGIDO
                vel.y = 0
                caixa.bottom = tope.top
        # Eixo X
        pos.x += vel.x * dt
        caixa = Rect(int(pos.x - raio), int(pos.y - raio), 2*raio, 2*raio)  # CORRIGIDO
        for b in self.solidos:
            if caixa.colliderect(b):
                if vel.x > 0:
                    pos.x = b.left - raio
                elif vel.x < 0:
                    pos.x = b.right + raio
                vel.x = 0
                caixa.x = int(pos.x - raio)
        return pos, vel

    def mover_com_colisao_jogador(self, pos, vel, dt, raio=12):
        pos_y = pos.copy(); vel_y = vel.copy()
        pos_y.y += vel_y.y * dt
        caixa = Rect(int(pos_y.x - raio), int(pos_y.y - raio), 2*raio, 2*raio)  # CORRIGIDO
        toque_chao = False
        for b in self.solidos:
            if caixa.colliderect(b):
                if vel_y.y > 0 and caixa.bottom > b.top:
                    pos_y.y = b.top - raio  # CORRIGIDO
                    vel_y.y = 0
                    toque_chao = True
                    caixa.bottom = b.top
                elif vel_y.y < 0 and caixa.top < b.bottom:
                    pos_y.y = b.bottom + raio  # CORRIGIDO
                    vel_y.y = 0
                    caixa.top = b.bottom
        for p in self.plataformas:
            tope = Rect(p.x, p.y, p.w, 6)
            if vel_y.y > 0 and caixa.bottom >= tope.top and caixa.bottom - vel_y.y*dt <= tope.top and caixa.centerx in range(p.x, p.right):
                pos_y.y = tope.top - raio  # CORRIGIDO
                vel_y.y = 0
                toque_chao = True
                caixa.bottom = tope.top

        pos_x = pos_y.copy(); vel_x = vel_y.copy()
        pos_x.x += vel_x.x * dt
        caixa = Rect(int(pos_x.x - raio), int(pos_x.y - raio), 2*raio, 2*raio)  # CORRIGIDO
        for b in self.solidos:
            if caixa.colliderect(b):
                if vel_x.x > 0:
                    pos_x.x = b.left - raio
                elif vel_x.x < 0:
                    pos_x.x = b.right + raio
                vel_x.x = 0
                caixa.x = int(pos_x.x - raio)
        return pos_x, vel_x, toque_chao

    def coletar_moedas_em(self, pos, raio=14) -> int:
        coletadas = 0
        r = Rect(int(pos.x-raio), int(pos.y-raio), 2*raio, 2*raio)
        apagar = []
        for (i,j), ok in self.moedas.items():
            if not ok: continue
            tile_r = Rect(i*TAM_TILE, j*TAM_TILE, TAM_TILE, TAM_TILE)
            if r.colliderect(tile_r):
                coletadas += 1
                apagar.append((i,j))
        for key in apagar:
            self.moedas[key] = False
        return coletadas

    def em_espinho(self, pos) -> bool:
        r = Rect(int(pos.x-10), int(pos.y-10), 20, 20)
        return any(r.colliderect(e) for e in self.espinhos)

    def fogo_atinge_jogador(self, pos) -> bool:
        r = Rect(int(pos.x-10), int(pos.y-12), 20, 24)
        for f in self.fogos:
            if Rect(int(f.pos.x-6), int(f.pos.y-6), 12, 12).colliderect(r):
                f.vivo = False
                return True
        return False

    # ---------- Desenho ----------
    def desenhar_tiles(self, tela, cam):
        ini_i, fim_i, ini_j, fim_j = self.retangulos_visiveis(cam)
        for j in range(ini_j, fim_j):
            for i in range(ini_i, fim_i):
                ch = self.tiles[j][i]
                x, y = i*TAM_TILE - cam.x, j*TAM_TILE - cam.y
                if ch == SOLIDO:
                    tela.blit(self.tx_solid, (x, y))
                elif ch == PLATAF:
                    tela.blit(self.tx_plat, (x, y+10))
                elif ch == ESPINHO:
                    tela.blit(self.tx_esp, (x, y))
                elif ch == MOEDA and self.moedas.get((i,j), False):
                    tela.blit(self.tx_moeda, (x+8, y+8))
                elif ch == PORTA:
                    pygame.draw.rect(tela, (150,120,90), (x+8,y+6, TAM_TILE-16, TAM_TILE-12))
                    pygame.draw.arc(tela, (110,90,70), (x+8,y-8, TAM_TILE-16, 28), math.pi, 2*math.pi, 4)

# --------------- Câmera ---------------
@dataclass
class Camera:
    pos: V2
    def atualizar(self, alvo: V2, dt: float):
        alvo_cam = alvo - V2(LARGURA*0.45, ALTURA*0.55)
        self.pos += (alvo_cam - self.pos) * clamp(5.0*dt, 0.0, 1.0)
        self.pos.x = clamp(self.pos.x, 0, 1e7)

# --------------- Jogo -----------------
def jogo():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Príncipe do Deserto — Fase 1 (by Luiz Tiago Wilcke)")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("consolas", 18)

    mundo = Mundo(MAPA_TXT)
    jogador = Jogador(mundo.spawn.copy())
    cam = Camera(V2(0,0))

    rodando = True
    venceu = False

    while rodando:
        dt = relogio.tick(FPS) / 1000.0
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: rodando = False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE: rodando = False
                if ev.key == pygame.K_z: jogador.requisitar_pulo()
                if ev.key == pygame.K_x: jogador.requisitar_tiro(mundo.projeteis, pygame.key.get_pressed())
                if ev.key == pygame.K_c: jogador.requisitar_rolar()

        teclas = pygame.key.get_pressed()

        # Atualizações
        jogador.atualizar(dt, teclas, mundo)
        for g in mundo.guardas:
            g.atualizar(dt, mundo)
        for d in mundo.dragoes:
            d.atualizar(dt, mundo, jogador)

        # projéteis do jogador
        for p in mundo.projeteis:
            p.atualizar(dt, mundo.solidos)
        mundo.projeteis = [p for p in mundo.projeteis if p.vivo]

        # fogo dos dragões
        for f in mundo.fogos:
            f.atualizar(dt, mundo.solidos)
        mundo.fogos = [f for f in mundo.fogos if f.vivo]

        # Câmera e parallax
        cam.atualizar(jogador.pos, dt)

        # Chegou na porta?
        if mundo.porta and Rect(int(jogador.pos.x-10), int(jogador.pos.y-20), 20, 30).colliderect(mundo.porta):
            venceu = True

        # Derrota simples (caiu/sem vida)
        if jogador.vida <= 0 or jogador.pos.y > (mundo.h*TAM_TILE + 200):
            jogador = Jogador(mundo.spawn.copy())
            mundo.projeteis.clear()
            mundo.fogos.clear()
            venceu = False

        # ----------------- Desenho -----------------
        desenhar_ceu(tela)
        desenhar_dunas(tela, cam.pos.x)
        desenhar_silhuetas(tela, cam.pos.x)
        pygame.draw.rect(tela, AREIA, (0, ALTURA-40, LARGURA, 40))

        mundo.desenhar_tiles(tela, cam.pos)
        for g in mundo.guardas:
            g.desenhar(tela, cam.pos)
        for d in mundo.dragoes:
            d.desenhar(tela, cam.pos)
        for f in mundo.fogos:
            f.desenhar(tela, cam.pos)
        for p in mundo.projeteis:
            p.desenhar(tela, cam.pos)
        jogador.desenhar(tela, cam.pos)

        # HUD
        hud = f"Autor: Luiz Tiago Wilcke | Vida: {jogador.vida}  Moedas: {jogador.moedas}"
        tela.blit(fonte.render(hud, True, BRANCO), (10, 10))
        if venceu:
            msg = fonte.render("Fase concluída! (entre na porta para reiniciar)", True, OURO)
            tela.blit(msg, (LARGURA//2 - msg.get_width()//2, 40))

        pygame.display.flip()

    pygame.quit()

# --------------- Execução ---------------
if __name__ == "__main__":
    jogo()
