import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.Queue;
import java.util.Random;

public class PacManJava extends JPanel {
    /**
     * 
     */
    private static final long serialVersionUID = 1L;
    // Definições de constantes
    private final int LARGURA = 1600; // 40 colunas * 40 pixels
    private final int ALTURA = 840;    // 800 pixels para o jogo + 40 pixels para a legenda
    private final int TAMANHO_CELULA = 40;
    private final int LINHAS = (ALTURA - 40) / TAMANHO_CELULA; // 20 linhas para o labirinto
    private final int COLUNAS = 40; // 40 caracteres por linha
    private final int NUM_FANTASMAS = 6;
    private Timer timer; // Utilizando javax.swing.Timer
    private Labirinto labirinto;
    private PacMan pacMan;
    private ArrayList<Fantasma> fantasmas;
    private int pontuacao;
    private int vidas;
    private boolean jogoAtivo;
    private boolean venceu;

    // Construtor da classe principal
    public PacManJava() {
        setPreferredSize(new Dimension(LARGURA, ALTURA));
        setBackground(Color.BLACK);
        setFocusable(true);
        setLayout(null); // Desativar layout para garantir o foco
        adicionarKeyBindings();

        labirinto = new Labirinto();
        pacMan = new PacMan(labirinto.getPosicaoInicialPacMan());
        fantasmas = new ArrayList<>();
        for (int i = 0; i < NUM_FANTASMAS; i++) {
            fantasmas.add(new Fantasma(labirinto.getPosicaoInicialFantasma(i), i));
        }
        pontuacao = 0;
        vidas = 3;
        jogoAtivo = true;
        venceu = false;

        // Inicialização do Timer com intervalo de 100ms
        timer = new Timer(100, new ActionListener() { // Atualiza a cada 100ms para suavizar movimento
            @Override
            public void actionPerformed(ActionEvent e) {
                if (jogoAtivo) {
                    pacMan.mover(labirinto);
                    for (Fantasma fantasma : fantasmas) {
                        fantasma.mover(labirinto, pacMan);
                    }
                    verificarColisoes();
                    verificarComidas();
                    verificarVitoria();
                }
                repaint();
            }
        });
        timer.start();

        // Solicita foco para capturar eventos de teclado após o painel ser exibido
        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {
                requestFocusInWindow();
            }
        });
    }

    // Método para adicionar Key Bindings
    private void adicionarKeyBindings() {
        int condition = JComponent.WHEN_IN_FOCUSED_WINDOW;
        InputMap inputMap = getInputMap(condition);
        ActionMap actionMap = getActionMap();

        // Movimentação para cima
        inputMap.put(KeyStroke.getKeyStroke("UP"), "moverCima");
        inputMap.put(KeyStroke.getKeyStroke("W"), "moverCima");
        actionMap.put("moverCima", new AbstractAction() {
            @Override
            public void actionPerformed(ActionEvent e) {
                pacMan.setDirecao(1);
                System.out.println("Direção: Cima");
            }
        });

        // Movimentação para baixo
        inputMap.put(KeyStroke.getKeyStroke("DOWN"), "moverBaixo");
        inputMap.put(KeyStroke.getKeyStroke("S"), "moverBaixo");
        actionMap.put("moverBaixo", new AbstractAction() {
            @Override
            public void actionPerformed(ActionEvent e) {
                pacMan.setDirecao(2);
                System.out.println("Direção: Baixo");
            }
        });

        // Movimentação para esquerda
        inputMap.put(KeyStroke.getKeyStroke("LEFT"), "moverEsquerda");
        inputMap.put(KeyStroke.getKeyStroke("A"), "moverEsquerda");
        actionMap.put("moverEsquerda", new AbstractAction() {
            @Override
            public void actionPerformed(ActionEvent e) {
                pacMan.setDirecao(3);
                System.out.println("Direção: Esquerda");
            }
        });

        // Movimentação para direita
        inputMap.put(KeyStroke.getKeyStroke("RIGHT"), "moverDireita");
        inputMap.put(KeyStroke.getKeyStroke("D"), "moverDireita");
        actionMap.put("moverDireita", new AbstractAction() {
            @Override
            public void actionPerformed(ActionEvent e) {
                pacMan.setDirecao(4);
                System.out.println("Direção: Direita");
            }
        });

        // Reiniciar o jogo com 'R'
        inputMap.put(KeyStroke.getKeyStroke("R"), "reiniciarJogo");
        actionMap.put("reiniciarJogo", new AbstractAction() {
            @Override
            public void actionPerformed(ActionEvent e) {
                if (!jogoAtivo) {
                    reiniciarJogo();
                    System.out.println("Jogo reiniciado.");
                }
            }
        });
    }

    // Método principal para iniciar o jogo
    public static void main(String[] args) {
        JFrame janela = new JFrame("Pac-Man em Java");
        PacManJava jogo = new PacManJava();
        janela.add(jogo);
        janela.pack();
        janela.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        janela.setLocationRelativeTo(null);
        janela.setVisible(true);
    }

    // Método para desenhar o jogo
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        // Desenhar a legenda na parte superior
        g.setColor(Color.WHITE);
        g.setFont(new Font("Arial", Font.BOLD, 24));
        String autor = "Autor: Luiz Tiago Wilcke";
        int larguraTexto = g.getFontMetrics().stringWidth(autor);
        g.drawString(autor, (LARGURA - larguraTexto) / 2, 30);

        // Deslocar o contexto gráfico para baixo para desenhar o labirinto e os personagens
        int OFFSET_Y = 40;
        g.translate(0, OFFSET_Y);

        // Desenhar o labirinto, PacMan e Fantasmas
        labirinto.desenhar(g, TAMANHO_CELULA);
        pacMan.desenhar(g, TAMANHO_CELULA);
        for (Fantasma fantasma : fantasmas) {
            fantasma.desenhar(g, TAMANHO_CELULA);
        }
        desenharInformacoes(g);
        if (!jogoAtivo) {
            desenharMensagemFim(g);
        }

        // Reverter a translação do contexto gráfico
        g.translate(0, -OFFSET_Y);
    }

    // Método para desenhar pontuação e vidas
    private void desenharInformacoes(Graphics g) {
        g.setColor(Color.WHITE);
        g.setFont(new Font("Arial", Font.BOLD, 18));
        g.drawString("Pontuação: " + pontuacao, 10, ALTURA - 10);
        g.drawString("Vidas: " + vidas, LARGURA - 100, ALTURA - 10);
    }

    // Método para desenhar mensagem de fim de jogo
    private void desenharMensagemFim(Graphics g) {
        g.setColor(Color.RED);
        g.setFont(new Font("Arial", Font.BOLD, 36));
        String mensagem;
        if (vidas <= 0) {
            mensagem = "Game Over! Pressione R para Reiniciar.";
        } else if (venceu) {
            mensagem = "Parabéns! Você Venceu! Pressione R para Reiniciar.";
        } else {
            mensagem = "";
        }
        if (!mensagem.isEmpty()) {
            int larguraTexto = g.getFontMetrics().stringWidth(mensagem);
            g.drawString(mensagem, (LARGURA - larguraTexto) / 2, ALTURA / 2);
        }
    }

    // Método para verificar colisões entre Pac-Man e Fantasmas
    private void verificarColisoes() {
        for (Fantasma fantasma : fantasmas) {
            if (pacMan.getPosicao().equals(fantasma.getPosicao())) {
                vidas--;
                System.out.println("Colisão detectada! Vidas restantes: " + vidas);
                if (vidas > 0) {
                    pacMan.resetarPosicao(labirinto.getPosicaoInicialPacMan());
                    for (Fantasma f : fantasmas) {
                        f.resetarPosicao(labirinto.getPosicaoInicialFantasma(fantasmas.indexOf(f)));
                    }
                } else {
                    jogoAtivo = false;
                    timer.stop();
                    System.out.println("Todas as vidas perdidas.");
                }
            }
        }
    }

    // Método para verificar se Pac-Man comeu alguma comida
    private void verificarComidas() {
        Posicao pos = pacMan.getPosicao();
        if (labirinto.comerPonto(pos)) {
            pontuacao += 10;
            System.out.println("Ponto comido! Pontuação: " + pontuacao);
        }
        if (labirinto.comerPontoEspecial(pos)) {
            pontuacao += 50;
            System.out.println("Ponto especial comido! Pontuação: " + pontuacao);
            // Fantasmas entram em modo fugitivo
            for (Fantasma fantasma : fantasmas) {
                fantasma.setFugitivo(true);
            }
            // Timer para voltar os fantasmas ao normal após 10 segundos
            Timer fugidaTimer = new Timer(10000, new ActionListener() {
                @Override
                public void actionPerformed(ActionEvent e) {
                    for (Fantasma fantasma : fantasmas) {
                        fantasma.setFugitivo(false);
                    }
                    System.out.println("Fantasmas voltaram ao normal.");
                }
            });
            fugidaTimer.setRepeats(false);
            fugidaTimer.start();
        }
    }

    // Método para verificar condição de vitória
    private void verificarVitoria() {
        if (labirinto.todasComidasComidas()) {
            jogoAtivo = false;
            venceu = true;
            timer.stop();
            System.out.println("Todas as comidas foram comidas. Você venceu!");
        }
    }

    // Método para reiniciar o jogo
    private void reiniciarJogo() {
        pacMan.resetarPosicao(labirinto.getPosicaoInicialPacMan());
        fantasmas.clear();
        for (int i = 0; i < NUM_FANTASMAS; i++) {
            fantasmas.add(new Fantasma(labirinto.getPosicaoInicialFantasma(i), i));
        }
        pontuacao = 0;
        vidas = 3;
        jogoAtivo = true;
        venceu = false;
        labirinto.resetarLabirinto();
        timer.start();
        System.out.println("Jogo reiniciado.");
    }

    // Classe para representar a posição no labirinto
    class Posicao {
        int linha;
        int coluna;

        public Posicao(int linha, int coluna) {
            this.linha = linha;
            this.coluna = coluna;
        }

        @Override
        public boolean equals(Object obj) {
            if (obj instanceof Posicao) {
                Posicao outra = (Posicao) obj;
                return this.linha == outra.linha && this.coluna == outra.coluna;
            }
            return false;
        }
    }

    // Classe para representar o Labirinto
    class Labirinto {
        private char[][] matrizLabirinto;

        public Labirinto() {
            // Definição do labirinto
            matrizLabirinto = new char[LINHAS][COLUNAS];
            String[] linhasLabirinto = {
                "########################################",
                "#............##............##............#",
                "#.####.#####.##.#####.####.##.#####.####.#",
                "#o####.#####.##.#####.####.##.#####.####o#",
                "#........................................#",
                "#.####.##.##########.##########.##.####.#",
                "#.####.##.##########.##########.##.####.#",
                "#........................................#",
                "#.####.##.##.##########.##.##.##.##.####.#",
                "#.####.##.##.##########.##.##.##.##.####.#",
                "#o..##..................................##o#",
                "###.##.##.##.##########.##.##.##.##.##.###",
                "###.##.##.##.##########.##.##.##.##.##.###",
                "#........................................#",
                "#.####.##.##.##########.##.##.##.##.####.#",
                "#.####.##.##.##########.##.##.##.##.####.#",
                "#o..##..................................##o#",
                "###.##.##.##.##########.##.##.##.##.##.###",
                "###.##.##.##.##########.##.##.##.##.##.###",
                "#........................................#",
                "########################################"
            };

            // Preenche a matrizLabirinto com os caracteres do labirinto
            for (int i = 0; i < LINHAS; i++) {
                String linha = linhasLabirinto[i % linhasLabirinto.length];
                for (int j = 0; j < COLUNAS; j++) {
                    if (j < linha.length()) {
                        matrizLabirinto[i][j] = linha.charAt(j);
                    } else {
                        matrizLabirinto[i][j] = ' ';
                    }
                }
            }
        }

        // Método para desenhar o labirinto
        public void desenhar(Graphics g, int tamanhoCelula) {
            for (int i = 0; i < LINHAS; i++) {
                for (int j = 0; j < COLUNAS; j++) {
                    switch (matrizLabirinto[i][j]) {
                        case '#':
                            g.setColor(Color.BLUE);
                            g.fillRect(j * tamanhoCelula, i * tamanhoCelula, tamanhoCelula, tamanhoCelula);
                            break;
                        case '.':
                            g.setColor(Color.WHITE);
                            g.fillOval(j * tamanhoCelula + tamanhoCelula / 2 - 3, i * tamanhoCelula + tamanhoCelula / 2 - 3, 6, 6);
                            break;
                        case 'o':
                            g.setColor(Color.WHITE);
                            g.fillOval(j * tamanhoCelula + tamanhoCelula / 2 - 6, i * tamanhoCelula + tamanhoCelula / 2 - 6, 12, 12);
                            break;
                        default:
                            // Espaço vazio
                            break;
                    }
                }
            }
        }

        // Método para obter a posição inicial do Pac-Man
        public Posicao getPosicaoInicialPacMan() {
            return new Posicao(10, 20); // Ajustado conforme necessário
        }

        // Método para obter a posição inicial dos Fantasmas
        public Posicao getPosicaoInicialFantasma(int index) {
            // Definir posições iniciais diferentes para cada fantasma
            switch (index) {
                case 0: return new Posicao(1, 1);
                case 1: return new Posicao(1, COLUNAS - 2);
                case 2: return new Posicao(LINHAS - 2, 1);
                case 3: return new Posicao(LINHAS - 2, COLUNAS - 2);
                case 4: return new Posicao(4, 20); // Ajustado para evitar colisão imediata
                case 5: return new Posicao(7, 20); // Ajustado para evitar colisão imediata
                default: return new Posicao(1, 1);
            }
        }

        // Método para comer ponto
        public boolean comerPonto(Posicao pos) {
            if (matrizLabirinto[pos.linha][pos.coluna] == '.') {
                matrizLabirinto[pos.linha][pos.coluna] = ' ';
                return true;
            }
            return false;
        }

        // Método para comer ponto especial
        public boolean comerPontoEspecial(Posicao pos) {
            if (matrizLabirinto[pos.linha][pos.coluna] == 'o') {
                matrizLabirinto[pos.linha][pos.coluna] = ' ';
                return true;
            }
            return false;
        }

        // Método para verificar se todas as comidas foram comidas
        public boolean todasComidasComidas() {
            for (int i = 0; i < LINHAS; i++) {
                for (int j = 0; j < COLUNAS; j++) {
                    if (matrizLabirinto[i][j] == '.' || matrizLabirinto[i][j] == 'o') {
                        return false;
                    }
                }
            }
            return true;
        }

        // Método para verificar se uma posição é livre (não é parede)
        public boolean isLivre(int linha, int coluna) {
            if (linha >= 0 && linha < LINHAS && coluna >= 0 && coluna < COLUNAS) {
                return matrizLabirinto[linha][coluna] != '#';
            }
            return false;
        }

        // Método para obter o número de linhas
        public int getLinhas() {
            return LINHAS;
        }

        // Método para obter o número de colunas
        public int getColunas() {
            return COLUNAS;
        }

        // Método para resetar o labirinto (restaurar todas as comidas)
        public void resetarLabirinto() {
            String[] linhasLabirinto = {
                "########################################",
                "#............##............##............#",
                "#.####.#####.##.#####.####.##.#####.####.#",
                "#o####.#####.##.#####.####.##.#####.####o#",
                "#........................................#",
                "#.####.##.##########.##########.##.####.#",
                "#.####.##.##########.##########.##.####.#",
                "#........................................#",
                "#.####.##.##.##########.##.##.##.##.####.#",
                "#.####.##.##.##########.##.##.##.##.####.#",
                "#o..##..................................##o#",
                "###.##.##.##.##########.##.##.##.##.##.###",
                "###.##.##.##.##########.##.##.##.##.##.###",
                "#........................................#",
                "#.####.##.##.##########.##.##.##.##.####.#",
                "#.####.##.##.##########.##.##.##.##.####.#",
                "#o..##..................................##o#",
                "###.##.##.##.##########.##.##.##.##.##.###",
                "###.##.##.##.##########.##.##.##.##.##.###",
                "#........................................#",
                "########################################"
            };

            // Preenche a matrizLabirinto com os caracteres do labirinto
            for (int i = 0; i < LINHAS; i++) {
                String linha = linhasLabirinto[i % linhasLabirinto.length];
                for (int j = 0; j < COLUNAS; j++) {
                    if (j < linha.length()) {
                        matrizLabirinto[i][j] = linha.charAt(j);
                    } else {
                        matrizLabirinto[i][j] = ' ';
                    }
                }
            }
        }
    }

    // Classe para representar o Pac-Man
    class PacMan {
        private Posicao posicao;
        private int direcao; // 0: Parado, 1: Cima, 2: Baixo, 3: Esquerda, 4: Direita

        public PacMan(Posicao posInicial) {
            posicao = posInicial;
            direcao = 0;
        }

        public Posicao getPosicao() {
            return posicao;
        }

        public void setDirecao(int novaDirecao) {
            direcao = novaDirecao;
        }

        // Método para desenhar o Pac-Man
        public void desenhar(Graphics g, int tamanhoCelula) {
            g.setColor(Color.YELLOW);
            int x = posicao.coluna * tamanhoCelula;
            int y = posicao.linha * tamanhoCelula;

            // Desenhar Pac-Man com a boca aberta na direção atual
            int startAngle;
            switch (direcao) {
                case 1: // Cima
                    startAngle = 90;
                    break;
                case 2: // Baixo
                    startAngle = 270;
                    break;
                case 3: // Esquerda
                    startAngle = 180;
                    break;
                case 4: // Direita
                    startAngle = 0;
                    break;
                default:
                    startAngle = 0;
                    break;
            }
            g.fillArc(x, y, tamanhoCelula, tamanhoCelula, startAngle, 300);
        }

        // Método para mover o Pac-Man
        public void mover(Labirinto labirinto) {
            int novaLinha = posicao.linha;
            int novaColuna = posicao.coluna;

            switch (direcao) {
                case 1: // Cima
                    novaLinha--;
                    break;
                case 2: // Baixo
                    novaLinha++;
                    break;
                case 3: // Esquerda
                    novaColuna--;
                    break;
                case 4: // Direita
                    novaColuna++;
                    break;
                default:
                    break;
            }

            // Verifica se a nova posição é válida (não é parede)
            if (labirinto.isLivre(novaLinha, novaColuna)) {
                posicao.linha = novaLinha;
                posicao.coluna = novaColuna;
                // System.out.println("Pac-Man moveu para: (" + novaLinha + ", " + novaColuna + ")");
            }
        }

        // Método para resetar a posição do Pac-Man
        public void resetarPosicao(Posicao posInicial) {
            posicao = posInicial;
            direcao = 0;
            // System.out.println("Pac-Man resetado para: (" + posInicial.linha + ", " + posInicial.coluna + ")");
        }
    }

    // Classe para representar os Fantasmas
    class Fantasma {
        private Posicao posicao;
        private Color cor;
        private boolean fugitivo;
        private int indexFantasma;
        private Random random;

        public Fantasma(Posicao posInicial, int index) {
            posicao = posInicial;
            cor = obterCorFantasma(index);
            fugitivo = false;
            indexFantasma = index;
            random = new Random();
        }

        public Posicao getPosicao() {
            return posicao;
        }

        // Método para definir se o fantasma está fugindo
        public void setFugitivo(boolean status) {
            fugitivo = status;
            if (fugitivo) {
                cor = Color.CYAN; // Cor diferente quando fugindo
            } else {
                cor = obterCorFantasma(indexFantasma);
            }
        }

        // Método para obter a cor do fantasma com base no índice
        private Color obterCorFantasma(int index) {
            switch (index) {
                case 0: return Color.RED;
                case 1: return Color.PINK;
                case 2: return Color.ORANGE;
                case 3: return Color.GREEN;
                case 4: return Color.MAGENTA;
                case 5: return Color.GRAY;
                default: return Color.WHITE;
            }
        }

        // Método para desenhar o Fantasma
        public void desenhar(Graphics g, int tamanhoCelula) {
            g.setColor(cor);
            int x = posicao.coluna * tamanhoCelula;
            int y = posicao.linha * tamanhoCelula;

            // Desenhar o corpo do fantasma
            g.fillOval(x, y, tamanhoCelula, tamanhoCelula);

            // Desenhar os olhos
            g.setColor(Color.WHITE);
            g.fillOval(x + tamanhoCelula / 4, y + tamanhoCelula / 4, tamanhoCelula / 5, tamanhoCelula / 5);
            g.fillOval(x + (3 * tamanhoCelula) / 5, y + tamanhoCelula / 4, tamanhoCelula / 5, tamanhoCelula / 5);
            g.setColor(Color.BLACK);
            g.fillOval(x + tamanhoCelula / 4 + 2, y + tamanhoCelula / 4 + 2, tamanhoCelula / 10, tamanhoCelula / 10);
            g.fillOval(x + (3 * tamanhoCelula) / 5 + 2, y + tamanhoCelula / 4 + 2, tamanhoCelula / 10, tamanhoCelula / 10);
        }

        // Método para mover o Fantasma com IA (BFS)
        public void mover(Labirinto labirinto, PacMan pacMan) {
            Posicao alvo = fugitivo ? labirinto.getPosicaoInicialPacMan() : pacMan.getPosicao();
            Posicao proximoPasso = encontrarProximoPasso(labirinto, alvo);
            if (proximoPasso != null) {
                posicao = proximoPasso;
                // System.out.println("Fantasma " + indexFantasma + " moveu para: (" + posicao.linha + ", " + posicao.coluna + ")");
            } else {
                // Movimentação aleatória se não encontrar caminho
                moverAleatoriamente(labirinto);
            }
        }

        // Método para encontrar o próximo passo usando BFS
        private Posicao encontrarProximoPasso(Labirinto labirinto, Posicao alvo) {
            boolean[][] visitado = new boolean[labirinto.getLinhas()][labirinto.getColunas()];
            Posicao[][] anterior = new Posicao[labirinto.getLinhas()][labirinto.getColunas()];
            Queue<Posicao> fila = new LinkedList<>();
            fila.add(posicao);
            visitado[posicao.linha][posicao.coluna] = true;

            int[] direcoesLinha = {-1, 1, 0, 0};
            int[] direcoesColuna = {0, 0, -1, 1};

            while (!fila.isEmpty()) {
                Posicao atual = fila.poll();
                if (atual.equals(alvo)) {
                    break;
                }
                for (int i = 0; i < 4; i++) {
                    int novaLinha = atual.linha + direcoesLinha[i];
                    int novaColuna = atual.coluna + direcoesColuna[i];
                    if (labirinto.isLivre(novaLinha, novaColuna) && !visitado[novaLinha][novaColuna]) {
                        visitado[novaLinha][novaColuna] = true;
                        anterior[novaLinha][novaColuna] = atual;
                        fila.add(new Posicao(novaLinha, novaColuna));
                    }
                }
            }

            if (!alvo.equals(posicao)) {
                Posicao passo = alvo;
                while (anterior[passo.linha][passo.coluna] != null && !anterior[passo.linha][passo.coluna].equals(posicao)) {
                    passo = anterior[passo.linha][passo.coluna];
                }
                if (anterior[passo.linha][passo.coluna] != null) {
                    return passo;
                }
            }
            return null;
        }

        // Método para mover o Fantasma aleatoriamente
        private void moverAleatoriamente(Labirinto labirinto) {
            int direcao = random.nextInt(4);
            int novaLinha = posicao.linha;
            int novaColuna = posicao.coluna;

            switch (direcao) {
                case 0: // Cima
                    novaLinha--;
                    break;
                case 1: // Baixo
                    novaLinha++;
                    break;
                case 2: // Esquerda
                    novaColuna--;
                    break;
                case 3: // Direita
                    novaColuna++;
                    break;
            }

            // Verifica se a nova posição é válida (não é parede)
            if (labirinto.isLivre(novaLinha, novaColuna)) {
                posicao.linha = novaLinha;
                posicao.coluna = novaColuna;
                // System.out.println("Fantasma " + indexFantasma + " moveu aleatoriamente para: (" + posicao.linha + ", " + posicao.coluna + ")");
            }
        }

        // Método para resetar a posição do Fantasma
        public void resetarPosicao(Posicao posInicial) {
            posicao = posInicial;
            setFugitivo(false);
            // System.out.println("Fantasma " + indexFantasma + " resetado para: (" + posInicial.linha + ", " + posInicial.coluna + ")");
        }
    }
}

