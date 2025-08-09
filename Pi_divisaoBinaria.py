#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Autor: Luiz Tiago Wilcke
# Cálculo de ~1000 dígitos de π por Chudnovsky com divisão binária adaptativa


from decimal import Decimal, getcontext

def calcular_pi(digitos=1000):
    """
    Retorna π com 'digitos' casas decimais.
    Implementação:
      - Fórmula de Chudnovsky
      - Divisão binária (binary splitting) adaptativa sem recursão profunda
      - Acúmulo inteiro (P, Q, T) e apenas 1 sqrt no final (Decimal)
    """
    # Precisão de segurança: alguns dígitos extras para erros de arredondamento
    margem = 10
    getcontext().prec = digitos + margem

    # Cada termo de Chudnovsky rende ~14.18164746 dígitos
    # Estimativa mínima de termos necessários:
    import math
    termos_necessarios = max(1, math.ceil(digitos / 14.181647462725477))

    # Constantes inteiras usadas na recorrência
    C = 640320
    C3_24 = (C**3) // 24  # 640320^3 / 24  (inteiro exato)
    # Fórmula:
    # P(a,b) = prod_{k=a}^{b-1} (6k-5)(2k-1)(6k-1)
    # Q(a,b) = prod_{k=a}^{b-1} k^3 * C3_24
    # T(a,b) = sum_{k=a}^{b-1} (-1)^k * P(a,k+1)*A / Q(a,k+1)
    # onde A_k = 13591409 + 545140134*k incorporado no T via divisão binária

    def combinar(P_esq, Q_esq, T_esq, P_dir, Q_dir, T_dir):
        """
        Combinação de duas metades (esquerda e direita) no esquema de divisão binária.
        Tudo em inteiros: T precisa incorporar o termo A_k corretamente.
        """
        P = P_esq * P_dir
        Q = Q_esq * Q_dir
        T = T_esq * Q_dir + P_esq * T_dir
        return P, Q, T

    # Vamos construir as “folhas” (intervalos unitários) e ir combinando iterativamente,
    # evitando recursão: é o diferencial "novo" desta engenharia.
    folhas = []
    for k in range(termos_necessarios):
        # P_unit, Q_unit e T_unit para o termo k..k+1
        # Componentes de P:
        p1 = 6*k - 5
        p2 = 2*k - 1
        p3 = 6*k - 1
        P_unit = (p1 * p2 * p3) if k > 0 else 1  # por convenção, P(0,1)=1

        # Q: k^3 * C3_24 (para k>0), e 1 para k=0
        if k == 0:
            Q_unit = 1
        else:
            Q_unit = (k*k*k) * C3_24

        # A_k:
        A_k = 13591409 + 545140134 * k

        # Sinal (-1)^k embutido no T_unit
        if (k % 2) == 0:
            T_unit = A_k * P_unit
        else:
            T_unit = -A_k * P_unit

        # Guarda folha (P,Q,T) do intervalo [k,k+1)
        folhas.append((P_unit, Q_unit, T_unit))

    # Combinação “árvore binária” iterativa
    while len(folhas) > 1:
        nova_lista = []
        # Combina aos pares
        it = iter(folhas)
        for esquerda in it:
            try:
                direita = next(it)
            except StopIteration:
                # ímpar: carrega a última sem combinar
                nova_lista.append(esquerda)
                break
            nova_lista.append(combinar(*esquerda, *direita))
        folhas = nova_lista

    P_total, Q_total, T_total = folhas[0]

    # Agora, fórmula final:
    # 1/pi = (12 / C^1.5) * (T_total / Q_total)
    # => pi = (Q_total * C^1.5) / (12 * T_total)
    # Usamos Decimal apenas aqui (uma sqrt).
    C_decimal = Decimal(C)
    fator = (C_decimal.sqrt() ** 3)  # C^(3/2) = (sqrt(C))^3
    numerador = Decimal(Q_total) * fator
    denominador = Decimal(12) * Decimal(T_total)
    pi_decimal = numerador / denominador

    # Arredondar/formatar com 'digitos' casas decimais
    # Retorna como string com ponto decimal.
    # (Opcional: remover arredondamento extra colocando quantize)
    return +pi_decimal  # o operador + aplica o contexto atual (prec)

# --------- Execução direta / exemplo ---------
if __name__ == "__main__":
    digitos_desejados = 1000
    pi = calcular_pi(digitos_desejados)
    # Imprimir π com 1000 dígitos após o ponto:
    texto = format(pi, f'.{digitos_desejados}f')
    print(texto)
