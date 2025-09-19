#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Dict, Set, Tuple, List, Optional
from collections import deque
import math
import sys

Pos = Tuple[int, int]  # (linha, coluna)

DIGITOS = set(range(1, 10))


def bloco_id(l: int, c: int) -> int:
    """Retorna o índice do bloco 3x3 (0..8) para a posição (l,c)."""
    return (l // 3) * 3 + (c // 3)


def vizinhos_de(pos: Pos) -> Set[Pos]:
    """Todos os vizinhos (mesma linha, coluna ou bloco 3x3)."""
    l, c = pos
    v: Set[Pos] = set()
    # linha e coluna
    for j in range(9):
        if j != c:
            v.add((l, j))
    for i in range(9):
        if i != l:
            v.add((i, c))
    # bloco
    bi, bj = (l // 3) * 3, (c // 3) * 3
    for i in range(bi, bi + 3):
        for j in range(bj, bj + 3):
            if (i, j) != pos:
                v.add((i, j))
    return v


class SudokuCSP:
    def __init__(self, tabuleiro: List[List[int]]) -> None:
        self.variaveis: List[Pos] = [(i, j) for i in range(9) for j in range(9)]
        self.vizinhos: Dict[Pos, Set[Pos]] = {p: vizinhos_de(p) for p in self.variaveis}
        # Domínios: {posição -> conjunto de valores possíveis}
        self.dominios: Dict[Pos, Set[int]] = {}
        for i in range(9):
            for j in range(9):
                v = tabuleiro[i][j]
                if v == 0:
                    self.dominios[(i, j)] = set(DIGITOS)
                else:
                    self.dominios[(i, j)] = {v}
        # Restrições binárias padrão de Sudoku: todos vizinhos devem ser diferentes
        self._aplicar_restricoes_iniciais()

    def _aplicar_restricoes_iniciais(self) -> None:
        """Remove dos domínios valores impossíveis usando as pistas iniciais."""
        alterado = True
        while alterado:
            alterado = False
            for pos, dominio in self.dominios.items():
                if len(dominio) == 1:
                    val = next(iter(dominio))
                    for v in self.vizinhos[pos]:
                        if val in self.dominios[v] and len(self.dominios[v]) > 1:
                            self.dominios[v].discard(val)
                            alterado = True

    # -------------------- AC-3 -------------------- #

    def ac3(self) -> bool:
        """Propagação de restrições (arc-consistency)."""
        fila = deque()  # fila de arcos (Xi, Xj)
        for Xi in self.variaveis:
            for Xj in self.vizinhos[Xi]:
                fila.append((Xi, Xj))
        while fila:
            Xi, Xj = fila.popleft()
            if self._revisar(Xi, Xj):
                if len(self.dominios[Xi]) == 0:
                    return False
                for Xk in self.vizinhos[Xi] - {Xj}:
                    fila.append((Xk, Xi))
        return True

    def _revisar(self, Xi: Pos, Xj: Pos) -> bool:
        """Remove valores de Dom(Xi) que não têm suporte em Dom(Xj)."""
        removidos = False
        valores_remover = set()
        for x in self.dominios[Xi]:
            # em Sudoku: x tem suporte em Xj se existe y != x em Dom(Xj)
            if not any((y != x) for y in self.dominios[Xj]):
                valores_remover.add(x)
        if valores_remover:
            self.dominios[Xi] -= valores_remover
            removidos = True
        return removidos

    # -------------------- Backtracking com heurísticas -------------------- #

    def resolvido(self) -> bool:
        return all(len(self.dominios[p]) == 1 for p in self.variaveis)

    def _selecionar_variavel_MRV(self) -> Pos:
        """Escolhe variável não atribuída com menor domínio (MRV)."""
        candidatos = [p for p in self.variaveis if len(self.dominios[p]) > 1]
        return min(candidatos, key=lambda p: len(self.dominios[p]))

    def _ordenar_valores_LCV(self, pos: Pos) -> List[int]:
        """Ordena valores que menos restringem vizinhos (LCV)."""
        def impacto(v: int) -> int:
            # número de remoções que v causaria nos domínios dos vizinhos
            s = 0
            for w in self.vizinhos[pos]:
                if v in self.dominios[w] and len(self.dominios[w]) > 1:
                    s += 1
            return s
        return sorted(self.dominios[pos], key=impacto)

    def _atribuir(self, pos: Pos, valor: int,
                  remocoes: Dict[Pos, Set[int]]) -> bool:
        """Atribui valor a pos e faz forward checking; registra remoções."""
        # manter apenas 'valor' no domínio de pos
        outros = self.dominios[pos] - {valor}
        if not self._remover_valores(pos, outros, remocoes):
            return False
        # forward checking: retirar 'valor' dos vizinhos
        for v in self.vizinhos[pos]:
            if valor in self.dominios[v]:
                if not self._remover_valores(v, {valor}, remocoes):
                    return False
                # Se algum vizinho ficou com domínio unitário, propaga mais uma vez
                if len(self.dominios[v]) == 1:
                    unico = next(iter(self.dominios[v]))
                    # verificar inconsistência imediata
                    for w in self.vizinhos[v]:
                        if unico in self.dominios[w] and len(self.dominios[w]) == 1:
                            # conflito direto
                            return False
        return True

    def _remover_valores(self, pos: Pos, valores: Set[int],
                         remocoes: Dict[Pos, Set[int]]) -> bool:
        """Remove valores do domínio de pos e registra; retorna False se esvaziar domínio."""
        if not valores:
            return True
        if pos not in remocoes:
            remocoes[pos] = set()
        for v in valores:
            if v in self.dominios[pos]:
                self.dominios[pos].remove(v)
                remocoes[pos].add(v)
                if len(self.dominios[pos]) == 0:
                    return False
        return True

    def _desfazer(self, remocoes: Dict[Pos, Set[int]]) -> None:
        """Restaura domínios após backtrack."""
        for pos, vals in remocoes.items():
            self.dominios[pos].update(vals)

    def backtracking(self) -> bool:
        """Resolve por backtracking com MRV + LCV + forward checking."""
        if self.resolvido():
            return True
        pos = self._selecionar_variavel_MRV()
        for valor in self._ordenar_valores_LCV(pos):
            remocoes: Dict[Pos, Set[int]] = {}
            if self._atribuir(pos, valor, remocoes):
                # Pequena propagação adicional via AC-3 local (opcional, caro porém robusto)
                snapshot = {p: set(self.dominios[p]) for p in self.variaveis}
                if self.ac3() and self.backtracking():
                    return True
                # restaura snapshot (mais rápido do que desfazer AC-3 valor a valor)
                for p in self.variaveis:
                    self.dominios[p] = snapshot[p]
            self._desfazer(remocoes)
        return False

    # -------------------- utilidades -------------------- #

    def como_matriz(self) -> List[List[int]]:
        M = [[0]*9 for _ in range(9)]
        for i in range(9):
            for j in range(9):
                dom = self.dominios[(i, j)]
                M[i][j] = next(iter(dom)) if len(dom) == 1 else 0
        return M


def ler_tabuleiro_de_string(s: str) -> List[List[int]]:
    """
    Lê 81 caracteres (dígitos ou '.'/ '0' como vazio) em linhas 9x9.
    Ex.: "530070000600195000098000060800060003..." (81 chars)
    """
    s = ''.join(ch for ch in s if not ch.isspace())
    if len(s) != 81:
        raise ValueError("A string do Sudoku deve ter exatamente 81 caracteres.")
    M = [[0]*9 for _ in range(9)]
    k = 0
    for i in range(9):
        for j in range(9):
            ch = s[k]; k += 1
            if ch in '0.':
                M[i][j] = 0
            elif ch.isdigit() and ch != '0':
                M[i][j] = int(ch)
            else:
                raise ValueError(f"Caractere inválido: {ch}")
    return M


def imprimir(M: List[List[int]]) -> None:
    for i, linha in enumerate(M):
        if i % 3 == 0 and i != 0:
            print("------+-------+------")
        partes = []
        for j, v in enumerate(linha):
            sep = " | " if j % 3 == 0 and j != 0 else ""
            partes.append(sep + (str(v) if v != 0 else "."))
        print(' '.join(partes))


if __name__ == "__main__":
    # Exemplo difícil (Norvig hard style)
    exemplo = (
        "53..7...."
        "6..195..."
        ".98....6."
        "8...6...3"
        "4..8.3..1"
        "7...2...6"
        ".6....28."
        "...419..5"
        "....8..79"
    )
    # Você pode passar um sudoku por argumento (81 chars):
    # python sudoku_csp.py 53..7....6..195....98....6.8...6...3...
    if len(sys.argv) > 1:
        exemplo = sys.argv[1]

    tab = ler_tabuleiro_de_string(exemplo)
    print("Sudoku (entrada):")
    imprimir(tab)

    csp = SudokuCSP(tab)
    ok_ac3 = csp.ac3()
    if not ok_ac3:
        print("\nSem solução após AC-3.")
        sys.exit(1)

    if csp.backtracking():
        print("\nSolução:")
        imprimir(csp.como_matriz())
    else:
        print("\nNenhuma solução encontrada.")
