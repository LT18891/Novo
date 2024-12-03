from typing import List, Callable

def ordenacao_rapida(
    lista_desordenada: List[int],
    comparador: Callable[[int, int], bool] = lambda x, y: x < y
) -> List[int]:
    if len(lista_desordenada) <= 1:
        return lista_desordenada.copy()
    
    primeiro_elemento = lista_desordenada[0]
    elemento_medio = lista_desordenada[len(lista_desordenada) // 2]
    ultimo_elemento = lista_desordenada[-1]
    pivô = mediana_de_tres(primeiro_elemento, elemento_medio, ultimo_elemento)

    menores: List[int] = []
    iguais: List[int] = []
    maiores: List[int] = []

    for elemento in lista_desordenada:
        if comparador(elemento, pivô):
            menores.append(elemento)
        elif comparador(pivô, elemento):
            maiores.append(elemento)
        else:
            iguais.append(elemento)
    
    return ordenacao_rapida(menores, comparador) + iguais + ordenacao_rapida(maiores, comparador)

def mediana_de_tres(a: int, b: int, c: int) -> int:
    if (a < b and b < c) or (c < b and b < a):
        return b
    elif (b < a and a < c) or (c < a and a < b):
        return a
    else:
        return c

if __name__ == "__main__":
    lista_exemplo = [33, 10, 59, 26, 41, 58]
    lista_ordenada = ordenacao_rapida(lista_exemplo)
    print(f"Lista original: {lista_exemplo}")
    print(f"Lista ordenada: {lista_ordenada}")
