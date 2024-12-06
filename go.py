# jogo_go.py

import tkinter as tk
import random
import math
import copy


TAMANHO_TABULEIRO = 9
VIDAS_MAX = 1000  


VAZIO = 0
PRETO = 1
BRANCO = 2

class Tabuleiro:
    def __init__(self, tamanho=TAMANHO_TABULEIRO):
        self.tamanho = tamanho
        self.grade = [[VAZIO for _ in range(tamanho)] for _ in range(tamanho)]
        self.jogador_atual = PRETO
        self.passes = 0  # Contador de passes consecutivos

    def fazer_jogada(self, linha, coluna):
        if self.grade[linha][coluna] == VAZIO:
            self.grade[linha][coluna] = self.jogador_atual
            self.jogador_atual = BRANCO if self.jogador_atual == PRETO else PRETO
            self.passes = 0  # Resetar contador de passes
            return True
        return False

    def passar_turno(self):
        self.jogador_atual = BRANCO if self.jogador_atual == PRETO else PRETO
        self.passes += 1

    def obter_jogadas_possiveis(self):
        jogadas = []
        for i in range(self.tamanho):
            for j in range(self.tamanho):
                if self.grade[i][j] == VAZIO:
                    jogadas.append((i, j))
        jogadas.append(('passar', 'passar'))  # Opção de passar
        return jogadas

    def is_finalizado(self):
        # Finaliza o jogo se ambos os jogadores passarem consecutivamente
        return self.passes >= 2

    def copiar(self):
        return copy.deepcopy(self)

class NodoMCTS:
    def __init__(self, tabuleiro, pai=None, movimento=None):
        self.tabuleiro = tabuleiro
        self.pai = pai
        self.movimento = movimento
        self.filhos = []
        self.visitas = 0
        self.vitorias = 0

    def selecionar_filho(self):
        # Usar a fórmula UCT
        melhor_valor = -float('inf')
        melhor_filho = None
        for filho in self.filhos:
            if filho.visitas == 0:
                valor = float('inf')
            else:
                valor = (filho.vitorias / filho.visitas) + math.sqrt(2 * math.log(self.visitas) / filho.visitas)
            if valor > melhor_valor:
                melhor_valor = valor
                melhor_filho = filho
        return melhor_filho

    def expandir(self):
        jogadas_possiveis = self.tabuleiro.obter_jogadas_possiveis()
        for jogada in jogadas_possiveis:
            novo_tabuleiro = self.tabuleiro.copiar()
            if jogada == ('passar', 'passar'):
                novo_tabuleiro.passar_turno()
            else:
                novo_tabuleiro.fazer_jogada(*jogada)
            filho = NodoMCTS(novo_tabuleiro, pai=self, movimento=jogada)
            self.filhos.append(filho)

    def simular(self):
        tabuleiro_sim = self.tabuleiro.copiar()
        while not tabuleiro_sim.is_finalizado():
            jogadas = tabuleiro_sim.obter_jogadas_possiveis()
            if not jogadas:
                break
            jogada = random.choice(jogadas)
            if jogada == ('passar', 'passar'):
                tabuleiro_sim.passar_turno()
            else:
                tabuleiro_sim.fazer_jogada(*jogada)
        # Simplificação: considerar empate
        # Em uma implementação completa, calcular a pontuação real
        if tabuleiro_sim.jogador_atual == PRETO:
            return 1  # Vitória para Branco
        else:
            return 0  # Vitória para Preto

    def backpropagar(self, resultado):
        self.visitas += 1
        self.vitorias += resultado
        if self.pai:
            self.pai.backpropagar(resultado)

def mcts(root, iteracoes=VIDAS_MAX):
    for _ in range(iteracoes):
        nodo = root
        # Seleção
        while nodo.filhos:
            nodo = nodo.selecionar_filho()
        # Expansão
        if nodo.visitas > 0:
            nodo.expandir()
            if nodo.filhos:
                nodo = random.choice(nodo.filhos)
        # Simulação
        resultado = nodo.simular()
        # Retropropagação
        nodo.backpropagar(resultado)
    # Escolher o filho com mais visitas
    melhor_filho = max(root.filhos, key=lambda f: f.visitas)
    return melhor_filho.movimento

class InterfaceGo:
    def __init__(self, master):
        self.master = master
        self.master.title("Jogo de Go com MCTS")
        self.tabuleiro = Tabuleiro()
        self.canvas = tk.Canvas(master, width=450, height=450, bg="#DEB887")
        self.canvas.pack()
        self.desenhar_tabuleiro()
        self.canvas.bind("<Button-1>", self.clique_mouse)
        self.atualizar_interface()
        self.jogador_humano = PRETO  # Define o humano como jogador Preto
        self.jogador_computador = BRANCO  # Computador joga Branco

    def desenhar_tabuleiro(self):
        passo = 450 / (self.tabuleiro.tamanho + 1)
        self.passo = passo
        self.linhas = self.tabuleiro.tamanho
        # Desenhar linhas horizontais e verticais
        for i in range(1, self.linhas + 1):
            self.canvas.create_line(passo, passo * i, 450 - passo, passo * i)
            self.canvas.create_line(passo * i, passo, passo * i, 450 - passo)
        # Desenhar pontos de estrela (opcional para 9x9)
        pontos_estrela = [(3,3), (3,7), (7,3), (7,7), (5,5)]
        for (i, j) in pontos_estrela:
            x = passo * j
            y = passo * i
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="black")

    def atualizar_interface(self):
        self.canvas.delete("peca")
        for i in range(self.tabuleiro.tamanho):
            for j in range(self.tabuleiro.tamanho):
                if self.tabuleiro.grade[i][j] != VAZIO:
                    x = self.passo * (j + 1)
                    y = self.passo * (i + 1)
                    cor = "black" if self.tabuleiro.grade[i][j] == PRETO else "white"
                    self.canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill=cor, tags="peca")
        self.master.update()

    def clique_mouse(self, evento):
        if self.tabuleiro.jogador_atual != self.jogador_humano:
            return  # Não é a vez do humano

        passo = self.passo
        j = int(round((evento.x) / passo)) - 1
        i = int(round((evento.y) / passo)) - 1
        if 0 <= i < self.tabuleiro.tamanho and 0 <= j < self.tabuleiro.tamanho:
            jogada_valida = self.tabuleiro.fazer_jogada(i, j)
            if jogada_valida:
                self.atualizar_interface()
                if self.tabuleiro.is_finalizado():
                    self.finalizar_jogo()
                else:
                    self.jogada_computador()
        else:
            # Clique fora do tabuleiro, considerar como passar
            self.tabuleiro.passar_turno()
            self.atualizar_interface()
            if self.tabuleiro.is_finalizado():
                self.finalizar_jogo()
            else:
                self.jogada_computador()

    def jogada_computador(self):
        if self.tabuleiro.jogador_atual != self.jogador_computador:
            return
        root_nodo = NodoMCTS(self.tabuleiro.copiar())
        movimento = mcts(root_nodo)
        if movimento:
            if movimento == ('passar', 'passar'):
                self.tabuleiro.passar_turno()
            else:
                self.tabuleiro.fazer_jogada(*movimento)
            self.atualizar_interface()
            if self.tabuleiro.is_finalizado():
                self.finalizar_jogo()

    def finalizar_jogo(self):
      
        print("Jogo finalizado!")
     
        self.master.quit()

def main():
    root = tk.Tk()
    jogo = InterfaceGo(root)
    root.mainloop()

if __name__ == "__main__":
    main()
