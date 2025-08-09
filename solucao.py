#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solucionador SAT (CDCL)

Recursos:
- Literais vigiados (watched literals)
- Propagação unitária
- Aprendizado de cláusulas (1-UIP) e backjump não cronológico
- Heurística VSIDS (pontuação com decaimento)
- Reinícios segundo a sequência de Luby
- Pré-processamento simples (unidades e literais puros)
- DRAT-lite (registro das cláusulas aprendidas)

Uso:
  python3 sat_cdcl_pt.py problema.cnf
  cat problema.cnf | python3 sat_cdcl_pt.py
"""

import sys, random, time
from collections import defaultdict, deque

# ----------------- Utilidades -----------------
def ler_dimacs(linhas):
    numero_variaveis = numero_clausulas = 0
    clausulas = []
    for linha in linhas:
        linha = linha.strip()
        if not linha or linha.startswith('c'):
            continue
        if linha.startswith('p'):
            _, fmt, numero_variaveis, numero_clausulas = linha.split()
            numero_variaveis, numero_clausulas = int(numero_variaveis), int(numero_clausulas)
        else:
            lits = list(map(int, linha.split()))
            if not lits:
                continue
            assert lits[-1] == 0, "Cláusula deve terminar com 0"
            lits = lits[:-1]
            # remove duplicatas e tautologias
            conjunto = set(lits)
            if any((-l) in conjunto for l in conjunto):
                continue  # tautologia: sempre verdadeira
            clausulas.append(list(conjunto))
    return numero_variaveis, clausulas

def variavel(lit): 
    return abs(lit)

# ----------------- Solver -----------------
class CDCL:
    def __init__(self, numero_variaveis, clausulas_iniciais, semente=7):
        self.n = numero_variaveis
        self.clausulas_originais = [list(c) for c in clausulas_iniciais]

        self.clausulas = []                      # base + aprendidas
        self.vigilancias = defaultdict(list)     # lit -> [(id_clausula, outro_lit)]
        self.atribuicao = [0]*(self.n+1)         # -1 falso, +1 verdadeiro, 0 indefinido
        self.nivel = [0]*(self.n+1)              # nível de decisão de cada variável
        self.razao = [None]*(self.n+1)           # id da cláusula que implicou a variável
        self.trilha = []                         # pilha de literais atribuídos
        self.marcos_trilha = []                  # índices separando níveis na trilha

        self.atividade = [0.0]*(self.n+1)        # VSIDS: atividade por variável
        self.incremento_variavel = 1.0
        self.decaimento_variavel = 0.95
        self.conjunto_ordem = set(range(1, self.n+1))  # variáveis livres

        self.aleatorio = random.Random(semente)
        self.reinicios = 0
        self.conflitos = 0
        self.drats = []                          # DRAT-lite: cláusulas aprendidas

        # carregar cláusulas iniciais
        for c in self.clausulas_originais:
            if not self.adicionar_clausula(c, aprendida=False):
                raise RuntimeError("UNSAT imediato ao adicionar cláusulas iniciais")

        # pré-processamento
        self.preprocessar()

    # ---------- Watched literals ----------
    def adicionar_clausula(self, clausula, aprendida=True):
        clausula = list(dict.fromkeys(clausula))  # deduplicar preservando ordem

        # remover literais já satisfeitos e falsos
        if any(self.valor(l) is True for l in clausula):
            return True
        clausula = [l for l in clausula if self.valor(l) is not False]
        if not clausula:
            return False  # cláusula vazia: conflito imediato

        if len(clausula) == 1:
            # unit: força imediatamente
            if not self.enfileirar(clausula[0], razao=None):
                return False

        id_clausula = len(self.clausulas)
        self.clausulas.append(clausula)

        # registrar vigilâncias
        if len(clausula) == 1:
            self.vigilancias[clausula[0]].append((id_clausula, clausula[0]))
        else:
            a, b = clausula[0], clausula[1]
            self.vigilancias[a].append((id_clausula, b))
            self.vigilancias[b].append((id_clausula, a))

        if aprendida:
            self.drats.append(list(clausula))
        return True

    def valor(self, lit):
        v = variavel(lit)
        val = self.atribuicao[v]
        if val == 0:
            return None
        return (val == 1) if lit > 0 else (val == -1)

    # ---------- Atribuição / propagação ----------
    def novo_nivel_decisao(self):
        self.marcos_trilha.append(len(self.trilha))

    def enfileirar(self, lit, razao):
        v = variavel(lit)
        val = 1 if lit > 0 else -1
        if self.atribuicao[v] != 0:
            return self.atribuicao[v] == val
        self.atribuicao[v] = val
        self.nivel[v] = len(self.marcos_trilha)
        self.razao[v] = razao
        if v in self.conjunto_ordem:
            self.conjunto_ordem.remove(v)
        self.trilha.append(lit)
        return True

    def propagar(self):
        """Retorna id da cláusula em conflito, ou None se ok."""
        inicio = self.marcos_trilha[-1] if self.marcos_trilha else 0
        fila = deque(self.trilha[inicio:])
        while fila:
            lit = fila.popleft()
            neg = -lit
            lista = self.vigilancias[neg]
            i = 0
            while i < len(lista):
                id_clausula, outro = lista[i]
                clausula = self.clausulas[id_clausula]

                if self.valor(outro) is True:
                    i += 1
                    continue

                # tentar mover vigilância de -lit para outro literal não-falso
                substituido = False
                for l in clausula:
                    if l == neg or l == outro:
                        continue
                    if self.valor(l) is not False:
                        lista[i] = lista[-1]; lista.pop()
                        self.vigilancias[l].append((id_clausula, outro))
                        substituido = True
                        break
                if substituido:
                    continue

                # sem substituto: vira unit ou conflito
                if self.valor(outro) is False:
                    return id_clausula  # conflito
                else:
                    # unit: força 'outro'
                    if self.enfileirar(outro, razao=id_clausula):
                        fila.append(outro)
                        i += 1
                    else:
                        return id_clausula
        return None

    # ---------- Análise de conflito (1-UIP) ----------
    def analisar(self, id_conflito):
        self.conflitos += 1
        clausula = list(self.clausulas[id_conflito])
        vistos = set()
        aprendida = []
        caminho = 0
        p = None

        nivel_atual = len(self.marcos_trilha)
        for l in clausula:
            if self.nivel[variavel(l)] == nivel_atual:
                caminho += 1

        while True:
            # aumentar atividade das variáveis que aparecem na cláusula
            for l in clausula:
                self.impulsionar_atividade_variavel(variavel(l))

            # voltar na trilha até encontrar literal do nível atual presente na cláusula
            while self.trilha:
                p = self.trilha[-1]
                if variavel(p) in [variavel(x) for x in clausula if self.nivel[variavel(x)] == nivel_atual]:
                    break
                self.trilha.pop()

            # construir resolvente removendo p
            nova = []
            for l in clausula:
                if variavel(l) != variavel(p):
                    if variavel(l) not in vistos:
                        vistos.add(variavel(l))
                        if self.nivel[variavel(l)] == nivel_atual:
                            caminho += 1
                        else:
                            aprendida.append(l)
                        nova.append(l)

            id_razao = self.razao[variavel(p)]
            caminho -= 1
            self.trilha.pop()

            if id_razao is None:
                # p foi uma decisão: fecha cláusula aprendida com ~p
                aprendida.append(-p)
                break

            # resolvente: (clausula \ {p}) ∪ (razao(p) \ {~p})
            clausula = [l for l in self.clausulas[id_razao] if variavel(l) != variavel(p)] + nova

            if caminho == 0:
                aprendida.append(-p)
                break

        # normalizar: primeiro literal é do maior nível
        niveis = [self.nivel[variavel(l)] for l in aprendida]
        if not niveis:
            return [], 0  # cláusula vazia -> UNSAT

        maior = max(niveis)
        idx_maior = next(i for i, nv in enumerate(niveis) if nv == maior)
        aprendida[0], aprendida[idx_maior] = aprendida[idx_maior], aprendida[0]

        # nível de salto = maior nível entre os demais literais
        nivel_salto = 0
        for i in range(1, len(aprendida)):
            nivel_salto = max(nivel_salto, self.nivel[variavel(aprendida[i])])

        return aprendida, nivel_salto

    def cancelar_ate(self, nivel_objetivo):
        while len(self.marcos_trilha) > nivel_objetivo:
            inicio = self.marcos_trilha.pop()
            while len(self.trilha) > inicio:
                lit = self.trilha.pop()
                v = variavel(lit)
                self.atribuicao[v] = 0
                self.nivel[v] = 0
                self.razao[v] = None
                self.conjunto_ordem.add(v)

    # ---------- VSIDS ----------
    def impulsionar_atividade_variavel(self, v):
        self.atividade[v] += self.incremento_variavel
        if self.atividade[v] > 1e100:
            for i in range(1, self.n+1):
                self.atividade[i] *= 1e-100
            self.incremento_variavel *= 1e-100

    def decair_atividade(self):
        self.incremento_variavel /= self.decaimento_variavel

    def escolher_literal_decisao(self):
        melhor_v = None
        melhor_atividade = -1.0
        for v in self.conjunto_ordem:
            if self.atividade[v] > melhor_atividade:
                melhor_atividade = self.atividade[v]
                melhor_v = v
        if melhor_v is None:
            return None
        # fase padrão positiva
        return melhor_v

    # ---------- Reinícios (Luby) ----------
    def luby(self, i):
        k = 1
        while (1 << k) - 1 < i:
            k += 1
        if i == (1 << k) - 1:
            return 1 << (k - 1)
        return self.luby(i - (1 << (k - 1)) + 1)

    # ---------- Pré-processamento ----------
    def preprocessar(self):
        alterou = True
        while alterou:
            alterou = False
            # unidades
            unidades = []
            for idc, c in enumerate(self.clausulas):
                vivos = [l for l in c if self.valor(l) is not False]
                if not vivos:
                    raise RuntimeError("UNSAT durante pré-processamento (cláusula vazia)")
                if len(vivos) == 1 and self.valor(vivos[0]) is None:
                    unidades.append(vivos[0])

            for u in unidades:
                if self.enfileirar(u, razao=None):
                    conflito = self.propagar()
                    if conflito is not None:
                        raise RuntimeError("UNSAT durante pré-processamento")
                    alterou = True

            # literais puros
            if not alterou:
                contagem = defaultdict(int)
                for c in self.clausulas:
                    for l in c:
                        if self.valor(l) is None:
                            contagem[l] += 1
                vistos = set()
                for l in list(contagem.keys()):
                    v = variavel(l)
                    if v in vistos:
                        continue
                    if contagem.get(l, 0) > 0 and contagem.get(-l, 0) == 0:
                        if self.enfileirar(l, razao=None):
                            conflito = self.propagar()
                            if conflito is not None:
                                raise RuntimeError("UNSAT durante pré-processamento")
                            alterou = True
                    elif contagem.get(-l, 0) > 0 and contagem.get(l, 0) == 0:
                        if self.enfileirar(-l, razao=None):
                            conflito = self.propagar()
                            if conflito is not None:
                                raise RuntimeError("UNSAT durante pré-processamento")
                            alterou = True
                    vistos.add(v)

    # ---------- Loop principal ----------
    def resolver(self, tempo_max=None):
        inicio = time.time()
        base_orcamento = 100
        indice_luby = 1
        proximo_reinicio = base_orcamento * self.luby(indice_luby)

        # propagar após pré-processamento
        conflito = self.propagar()
        if conflito is not None:
            return False

        while True:
            if tempo_max and time.time() - inicio > tempo_max:
                print("INDETERMINADO: timeout", file=sys.stderr)
                return None

            # todas as variáveis atribuídas?
            if all(self.atribuicao[i] != 0 for i in range(1, self.n+1)):
                return True

            # decisão
            decisao = self.escolher_literal_decisao()
            if decisao is None:
                return True
            self.novo_nivel_decisao()
            if not self.enfileirar(decisao, razao=None):
                return False

            while True:
                conflito = self.propagar()
                if conflito is None:
                    break
                aprendida, nivel_salto = self.analisar(conflito)
                self.decair_atividade()

                if aprendida == []:
                    return False  # cláusula vazia aprendida -> UNSAT

                self.cancelar_ate(nivel_salto)
                if not self.adicionar_clausula(aprendida, aprendida=True):
                    return False
                if not self.enfileirar(aprendida[0], razao=len(self.clausulas)-1):
                    return False

                # reinício?
                if self.conflitos >= proximo_reinicio:
                    self.reinicios += 1
                    self.cancelar_ate(0)
                    indice_luby += 1
                    proximo_reinicio += base_orcamento * self.luby(indice_luby)
                    break

# ----------------- Execução CLI -----------------
def main():
    if len(sys.argv) > 1 and sys.argv[1] not in ('-', '--'):
        with open(sys.argv[1], 'r', encoding='utf-8', errors='ignore') as f:
            dados = f.readlines()
    else:
        dados = sys.stdin.readlines()

    numero_variaveis, clausulas = ler_dimacs(dados)
    solver = CDCL(numero_variaveis, clausulas)

    resultado = solver.resolver()
    if resultado is True:
        print("SAT")
        # modelo para 1..n
        modelo = []
        for v in range(1, solver.n+1):
            val = solver.atribuicao[v]
            if val == 0:
                val = 1
            modelo.append(v if val == 1 else -v)
        # saída estilo DIMACS (linhas 'v')
        linha = []
        for lit in modelo:
            linha.append(str(lit))
            if len(linha) > 12:
                print("v " + " ".join(linha) + " 0")
                linha = []
        if linha:
            print("v " + " ".join(linha) + " 0")

        if solver.drats:
            print("c DRAT-lite (cláusulas aprendidas):")
            for c in solver.drats:
                print("c l", " ".join(map(str, c)), "0")

    elif resultado is False:
        print("UNSAT")
    else:
        print("UNKNOWN")

if __name__ == "__main__":
    main()
