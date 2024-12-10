#include <vector>
#include <iostream>

int BuscaBinaria(const std::vector<int>& vetor, int chave, int baixo, int alto) {
    if (baixo > alto) {
        return -1; 
    }

    int meio = (baixo + alto) / 2;
    int elemento = vetor[meio];

    if (chave == elemento) {
        return elemento;
    } else if (chave < elemento) {
        return BuscaBinaria(vetor, chave, baixo, meio - 1);
    } else {
        return BuscaBinaria(vetor, chave, meio + 1, alto);
    }
}

int main() {
    std::vector<int> vetor = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
    int chave = 7;
    int resultado = BuscaBinaria(vetor, chave, 0, vetor.size() - 1);

    if (resultado != -1) {
        std::cout << "Elemento encontrado: " << resultado << std::endl;
    } else {
        std::cout << "Elemento não encontrado." << std::endl;
    }

    return 0;
}
