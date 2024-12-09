public class Quicksort {

    public static void main(String[] args) {
        int[] numeros = { 10, 7, 8, 9, 1, 5 };
        int tamanho = numeros.length;

        quicksort(numeros, 0, tamanho - 1);

        System.out.println("Array ordenado: ");
        for (int numero : numeros) {
            System.out.print(numero + " ");
        }
    }

    // Método principal do Quicksort
    public static void quicksort(int[] array, int inicio, int fim) {
        if (inicio < fim) {
            int indicePivo = particionar(array, inicio, fim);

            // Ordenar os elementos antes e depois do pivô
            quicksort(array, inicio, indicePivo - 1);
            quicksort(array, indicePivo + 1, fim);
        }
    }

    // Método para particionar o array
    public static int particionar(int[] array, int inicio, int fim) {
        int pivo = array[fim];
        int i = (inicio - 1); // Índice do menor elemento

        for (int j = inicio; j < fim; j++) {
            // Se o elemento atual é menor ou igual ao pivô
            if (array[j] <= pivo) {
                i++;

                // Trocar array[i] e array[j]
                int temp = array[i];
                array[i] = array[j];
                array[j] = temp;
            }
        }

        // Trocar array[i+1] e array[fim] (ou pivô)
        int temp = array[i + 1];
        array[i + 1] = array[fim];
        array[fim] = temp;

        return i + 1;
    }
}
