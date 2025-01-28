import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.*;
import java.util.List;

/**
 * Classe principal que inicia o jogo de Go.
 */
public class JogoGo {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new InterfaceGo();
        });
    }
}

/**
 * Representa o estado do tabuleiro de Go.
 */
class Tabuleiro implements Cloneable {
    public static final int VAZIO = 0;
    public static final int PRETO = 1;
    public static final int BRANCO = 2;

    private int tamanho;
    private int[][] grade;
    private int jogadorAtual;
    private int contadorPasses;
    private int capturasPreto;
    private int capturasBranco;

    /**
     * Construtor padrão com tamanho 19x19.
     */
    public Tabuleiro() {
        this(19);
    }

    /**
     * Construtor com tamanho personalizado.
     *
     * @param tamanho Tamanho do tabuleiro (ex: 19 para 19x19)
     */
    public Tabuleiro(int tamanho) {
        this.tamanho = tamanho;
        grade = new int[tamanho][tamanho];
        jogadorAtual = PRETO;
        contadorPasses = 0;
        capturasPreto = 0;
        capturasBranco = 0;
    }

    /**
     * Realiza uma jogada no tabuleiro.
     *
     * @param linha  Linha da jogada
     * @param coluna Coluna da jogada
     * @return true se a jogada for válida, false caso contrário
     */
    public boolean fazerJogada(int linha, int coluna) {
        if (linha < 0 || linha >= tamanho || coluna < 0 || coluna >= tamanho) {
            return false; // Jogada fora do tabuleiro
        }

        if (grade[linha][coluna] != VAZIO) {
            return false; // Célula já ocupada
        }

        // Clonar o tabuleiro para verificar a jogada
        Tabuleiro testeTabuleiro = this.clone();
        testeTabuleiro.grade[linha][coluna] = jogadorAtual;

        // Verificar capturas adversárias
        List<int[]> capturas = testeTabuleiro.verificarCapturas(linha, coluna);
        for (int[] pos : capturas) {
            testeTabuleiro.removerGrupo(pos[0], pos[1]);
            if (jogadorAtual == PRETO) {
                testeTabuleiro.capturasBranco++;
            } else {
                testeTabuleiro.capturasPreto++;
            }
        }

        // Verificar se a jogada é suicida
        if (!testeTabuleiro.temLiberdade(linha, coluna)) {
            return false; // Suicídio não é permitido
        }

        // Atualizar o tabuleiro original
        this.grade[linha][coluna] = jogadorAtual;
        for (int[] pos : capturas) {
            removerGrupo(pos[0], pos[1]);
            if (jogadorAtual == PRETO) {
                capturasBranco++;
            } else {
                capturasPreto++;
            }
        }

        // Alternar o jogador
        jogadorAtual = (jogadorAtual == PRETO) ? BRANCO : PRETO;
        contadorPasses = 0;
        return true;
    }

    /**
     * Passa a vez para o próximo jogador.
     */
    public void passarTurno() {
        jogadorAtual = (jogadorAtual == PRETO) ? BRANCO : PRETO;
        contadorPasses++;
    }

    /**
     * Obtém todas as jogadas possíveis no estado atual do tabuleiro.
     *
     * @return Lista de jogadas possíveis (linha, coluna). (-1, -1) representa passar turno.
     */
    public List<int[]> obterJogadasPossiveis() {
        List<int[]> jogadas = new ArrayList<>();
        for (int i = 0; i < tamanho; i++) {
            for (int j = 0; j < tamanho; j++) {
                if (grade[i][j] == VAZIO) {
                    jogadas.add(new int[]{i, j});
                }
            }
        }
        jogadas.add(new int[]{-1, -1}); // Representa a opção de passar
        return jogadas;
    }

    /**
     * Verifica se o jogo foi finalizado.
     *
     * @return true se ambos os jogadores passaram consecutivamente, false caso contrário
     */
    public boolean isFinalizado() {
        return contadorPasses >= 2;
    }

    /**
     * Retorna o jogador atual.
     *
     * @return PRETO ou BRANCO
     */
    public int getJogadorAtual() {
        return jogadorAtual;
    }

    /**
     * Obtém o valor de uma célula específica.
     *
     * @param linha  Linha da célula
     * @param coluna Coluna da célula
     * @return VAZIO, PRETO ou BRANCO
     */
    public int getCelula(int linha, int coluna) {
        return grade[linha][coluna];
    }

    /**
     * Retorna o tamanho do tabuleiro.
     *
     * @return Tamanho do tabuleiro (ex: 19)
     */
    public int getTamanho() {
        return tamanho;
    }

    /**
     * Retorna o número de capturas do jogador preto.
     *
     * @return Número de capturas do preto
     */
    public int getCapturasPreto() {
        return capturasPreto;
    }

    /**
     * Retorna o número de capturas do jogador branco.
     *
     * @return Número de capturas do branco
     */
    public int getCapturasBranco() {
        return capturasBranco;
    }

    /**
     * Cria uma cópia profunda do tabuleiro.
     *
     * @return Cópia clonada do tabuleiro
     */
    @Override
    protected Tabuleiro clone() {
        Tabuleiro copia = new Tabuleiro(this.tamanho);
        for (int i = 0; i < tamanho; i++) {
            System.arraycopy(this.grade[i], 0, copia.grade[i], 0, tamanho);
        }
        copia.jogadorAtual = this.jogadorAtual;
        copia.contadorPasses = this.contadorPasses;
        copia.capturasPreto = this.capturasPreto;
        copia.capturasBranco = this.capturasBranco;
        return copia;
    }

    /**
     * Verifica e retorna as posições das peças adversárias que devem ser capturadas.
     *
     * @param linha  Linha da jogada
     * @param coluna Coluna da jogada
     * @return Lista de posições a serem capturadas
     */
    private List<int[]> verificarCapturas(int linha, int coluna) {
        List<int[]> capturas = new ArrayList<>();
        int[] direcoes = {-1, 0, 1, 0, -1}; // Representa as direções: cima, direita, baixo, esquerda

        for (int i = 0; i < 4; i++) {
            int novoX = linha + direcoes[i];
            int novoY = coluna + direcoes[i + 1];
            if (novoX >= 0 && novoX < tamanho && novoY >= 0 && novoY < tamanho) {
                if (grade[novoX][novoY] == (jogadorAtual == PRETO ? BRANCO : PRETO)) {
                    if (!temLiberdade(novoX, novoY)) {
                        capturas.add(new int[]{novoX, novoY});
                    }
                }
            }
        }

        return capturas;
    }

    /**
     * Remove um grupo de peças a partir de uma posição específica.
     *
     * @param linha  Linha da peça
     * @param coluna Coluna da peça
     */
    private void removerGrupo(int linha, int coluna) {
        List<int[]> grupo = obterGrupo(linha, coluna);
        for (int[] pos : grupo) {
            grade[pos[0]][pos[1]] = VAZIO;
        }
    }

    /**
     * Obtém todas as peças conectadas ao grupo da posição especificada.
     *
     * @param linha  Linha da peça
     * @param coluna Coluna da peça
     * @return Lista de posições no grupo
     */
    private List<int[]> obterGrupo(int linha, int coluna) {
        List<int[]> grupo = new ArrayList<>();
        boolean[][] visitado = new boolean[tamanho][tamanho];
        int cor = grade[linha][coluna];
        if (cor == VAZIO) {
            return grupo;
        }

        Stack<int[]> pilha = new Stack<>();
        pilha.push(new int[]{linha, coluna});
        visitado[linha][coluna] = true;

        while (!pilha.isEmpty()) {
            int[] pos = pilha.pop();
            grupo.add(pos);
            int[] direcoes = {-1, 0, 1, 0, -1}; // Cima, Direita, Baixo, Esquerda

            for (int i = 0; i < 4; i++) {
                int novoX = pos[0] + direcoes[i];
                int novoY = pos[1] + direcoes[i + 1];
                if (novoX >= 0 && novoX < tamanho && novoY >= 0 && novoY < tamanho) {
                    if (!visitado[novoX][novoY] && grade[novoX][novoY] == cor) {
                        pilha.push(new int[]{novoX, novoY});
                        visitado[novoX][novoY] = true;
                    }
                }
            }
        }

        return grupo;
    }

    /**
     * Verifica se uma peça ou grupo de peças tem pelo menos uma liberdade.
     *
     * @param linha  Linha da peça
     * @param coluna Coluna da peça
     * @return true se tiver pelo menos uma liberdade, false caso contrário
     */
    private boolean temLiberdade(int linha, int coluna) {
        List<int[]> grupo = obterGrupo(linha, coluna);
        for (int[] pos : grupo) {
            int[] direcoes = {-1, 0, 1, 0, -1}; // Cima, Direita, Baixo, Esquerda
            for (int i = 0; i < 4; i++) {
                int novoX = pos[0] + direcoes[i];
                int novoY = pos[1] + direcoes[i + 1];
                if (novoX >= 0 && novoX < tamanho && novoY >= 0 && novoY < tamanho) {
                    if (grade[novoX][novoY] == VAZIO) {
                        return true;
                    }
                }
            }
        }
        return false;
    }
}

/**
 * Representa um nó na árvore do MCTS.
 */
class NodoMCTS {
    Tabuleiro tabuleiro;
    NodoMCTS pai;
    List<NodoMCTS> filhos;
    int[] movimento;
    int visitas;
    double vitorias;

    private static final double CONSTANTE_EXPLORACAO = Math.sqrt(2);
    private static final Random random = new Random();

    /**
     * Construtor do nó MCTS.
     *
     * @param tabuleiro Estado do tabuleiro
     * @param pai       Nó pai
     * @param movimento Movimento que levou a este nó
     */
    public NodoMCTS(Tabuleiro tabuleiro, NodoMCTS pai, int[] movimento) {
        this.tabuleiro = tabuleiro;
        this.pai = pai;
        this.movimento = movimento;
        this.filhos = new ArrayList<>();
        this.visitas = 0;
        this.vitorias = 0.0;
    }

    /**
     * Seleciona o melhor filho baseado na fórmula UCT.
     *
     * @return Melhor nó filho
     */
    public NodoMCTS selecionarFilho() {
        NodoMCTS melhorFilho = null;
        double melhorValor = Double.NEGATIVE_INFINITY;

        for (NodoMCTS filho : filhos) {
            double valor;
            if (filho.visitas == 0) {
                valor = Double.POSITIVE_INFINITY;
            } else {
                double explotacao = filho.vitorias / filho.visitas;
                double exploracao = CONSTANTE_EXPLORACAO * Math.sqrt(Math.log(this.visitas) / filho.visitas);
                valor = explotacao + exploracao;
            }

            if (valor > melhorValor) {
                melhorValor = valor;
                melhorFilho = filho;
            }
        }
        return melhorFilho;
    }

    /**
     * Expande o nó criando filhos para todas as jogadas possíveis.
     */
    public void expandir() {
        List<int[]> jogadasPossiveis = tabuleiro.obterJogadasPossiveis();
        for (int[] jogada : jogadasPossiveis) {
            Tabuleiro novoTabuleiro = tabuleiro.clone();
            if (jogada[0] == -1 && jogada[1] == -1) {
                novoTabuleiro.passarTurno();
            } else {
                novoTabuleiro.fazerJogada(jogada[0], jogada[1]);
            }
            NodoMCTS filho = new NodoMCTS(novoTabuleiro, this, jogada);
            filhos.add(filho);
        }
    }

    /**
     * Realiza uma simulação até o final do jogo.
     *
     * @return 1.0 se BRANCO vencer, 0.0 se PRETO vencer
     */
    public double simular() {
        Tabuleiro simTabuleiro = tabuleiro.clone();
        while (!simTabuleiro.isFinalizado()) {
            List<int[]> jogadas = simTabuleiro.obterJogadasPossiveis();
            if (jogadas.isEmpty()) {
                break;
            }
            int[] jogada = politicaSelecao(simTabuleiro, jogadas);
            if (jogada[0] == -1 && jogada[1] == -1) {
                simTabuleiro.passarTurno();
            } else {
                simTabuleiro.fazerJogada(jogada[0], jogada[1]);
            }
        }
        // Determinar vencedor com base nas capturas
        if (simTabuleiro.getCapturasBranco() > simTabuleiro.getCapturasPreto()) {
            return 1.0; // BRANCO venceu
        } else if (simTabuleiro.getCapturasPreto() > simTabuleiro.getCapturasBranco()) {
            return 0.0; // PRETO venceu
        } else {
            return 0.5; // Empate
        }
    }

    /**
     * Política de seleção de jogadas: prioriza o centro ou escolhe aleatoriamente.
     *
     * @param tabuleiro Estado do tabuleiro
     * @param jogadas   Lista de jogadas possíveis
     * @return Jogada selecionada
     */
    private int[] politicaSelecao(Tabuleiro tabuleiro, List<int[]> jogadas) {
        // Para maior diversidade, vamos escolher aleatoriamente
        return jogadas.get(random.nextInt(jogadas.size()));
    }

    /**
     * Retropropaga o resultado da simulação.
     *
     * @param resultado Resultado da simulação (1.0 para BRANCO, 0.0 para PRETO, 0.5 para empate)
     */
    public void retropropagar(double resultado) {
        this.visitas += 1;
        this.vitorias += resultado;
        if (pai != null) {
            pai.retropropagar(resultado);
        }
    }

    /**
     * Obtém os filhos do nó.
     *
     * @return Lista de nós filhos
     */
    public List<NodoMCTS> getFilhos() {
        return filhos;
    }

    /**
     * Obtém o movimento que levou a este nó.
     *
     * @return Vetor de dois elementos representando a jogada (linha, coluna)
     */
    public int[] getMovimento() {
        return movimento;
    }

    /**
     * Obtém o número de visitas ao nó.
     *
     * @return Número de visitas
     */
    public int getVisitas() {
        return visitas;
    }
}

/**
 * Gerencia a interface gráfica do jogo de Go.
 */
class InterfaceGo extends JFrame {
    private Tabuleiro tabuleiro;
    private JPanel painelTabuleiro;
    private JLabel barraStatus;
    private final int TAMANHO_CANVAS = 800;
    private final int TAMANHO_CELULA = TAMANHO_CANVAS / (19 + 1);
    private boolean computadorPensando = false;

    /**
     * Construtor da interface gráfica.
     */
    public InterfaceGo() {
        tabuleiro = new Tabuleiro();
        setTitle("Jogo de Go com MCTS");
        setSize(TAMANHO_CANVAS + 200, TAMANHO_CANVAS + 100); // Ajuste para incluir menus e barra de status
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        criarMenu();
        criarBarraStatus();

        painelTabuleiro = new PainelTabuleiro();
        painelTabuleiro.setPreferredSize(new Dimension(TAMANHO_CANVAS, TAMANHO_CANVAS));
        add(painelTabuleiro, BorderLayout.CENTER);

        painelTabuleiro.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                if (computadorPensando || tabuleiro.isFinalizado()) {
                    return;
                }

                int x = e.getX();
                int y = e.getY();

                // Mapear as coordenadas de clique para a interseção mais próxima
                int coluna = (int) Math.round((double) x / TAMANHO_CELULA) - 1;
                int linha = (int) Math.round((double) y / TAMANHO_CELULA) - 1;

                // Verificar se está dentro dos limites do tabuleiro
                if (linha >= 0 && linha < tabuleiro.getTamanho() && coluna >= 0 && coluna < tabuleiro.getTamanho()) {
                    // Verificar a distância para a interseção mais próxima
                    double deltaX = (double) x / TAMANHO_CELULA - coluna - 1;
                    double deltaY = (double) y / TAMANHO_CELULA - linha - 1;
                    double distancia = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

                    // Definir um limite de distância para considerar o clique válido
                    if (distancia > 0.3) { // Ajuste conforme necessário
                        // Clique muito longe de qualquer interseção
                        return;
                    }

                    if (tabuleiro.fazerJogada(linha, coluna)) {
                        atualizarInterface();
                        if (tabuleiro.isFinalizado()) {
                            finalizarJogo();
                        } else {
                            jogadaComputador();
                        }
                    } else {
                        JOptionPane.showMessageDialog(InterfaceGo.this, "Jogada inválida!", "Erro", JOptionPane.ERROR_MESSAGE);
                    }
                }
            }
        });

        setVisible(true);
    }

    /**
     * Cria o menu superior da aplicação.
     */
    private void criarMenu() {
        JMenuBar menuBar = new JMenuBar();

        // Menu Jogo
        JMenu menuJogo = new JMenu("Jogo");
        JMenuItem itemNovoJogo = new JMenuItem("Novo Jogo");
        itemNovoJogo.addActionListener(e -> novoJogo());
        JMenuItem itemSair = new JMenuItem("Sair");
        itemSair.addActionListener(e -> System.exit(0));
        menuJogo.add(itemNovoJogo);
        menuJogo.addSeparator();
        menuJogo.add(itemSair);
        menuBar.add(menuJogo);

        // Menu Ajuda
        JMenu menuAjuda = new JMenu("Ajuda");
        JMenuItem itemSobre = new JMenuItem("Sobre");
        itemSobre.addActionListener(e -> mostrarSobre());
        menuAjuda.add(itemSobre);
        menuBar.add(menuAjuda);

        setJMenuBar(menuBar);
    }

    /**
     * Cria a barra de status na parte inferior da janela.
     */
    private void criarBarraStatus() {
        barraStatus = new JLabel("Vez do Preto | Capturas: Preto=0 | Branco=0");
        barraStatus.setBorder(BorderFactory.createEtchedBorder());
        add(barraStatus, BorderLayout.SOUTH);
    }

    /**
     * Exibe a janela "Sobre" com informações sobre o jogo e o criador.
     */
    private void mostrarSobre() {
        String sobreTexto = "Jogo de Go com MCTS\n" +
                "Desenvolvido por Luiz Tiago Wilcke\n\n" +
                "Este é um jogo de Go implementado em Java utilizando a biblioteca Swing.\n" +
                "O computador utiliza o algoritmo de Monte Carlo Tree Search (MCTS) para determinar suas jogadas.";
        JOptionPane.showMessageDialog(this, sobreTexto, "Sobre", JOptionPane.INFORMATION_MESSAGE);
    }

    /**
     * Reinicia o jogo após confirmação do usuário.
     */
    private void novoJogo() {
        int confirm = JOptionPane.showConfirmDialog(this, "Tem certeza que deseja iniciar um novo jogo?", "Novo Jogo", JOptionPane.YES_NO_OPTION);
        if (confirm == JOptionPane.YES_OPTION) {
            tabuleiro = new Tabuleiro();
            atualizarInterface();
            barraStatus.setText("Vez do Preto | Capturas: Preto=0 | Branco=0");
        }
    }

    /**
     * Atualiza a interface gráfica após uma jogada.
     */
    private void atualizarInterface() {
        painelTabuleiro.repaint();
        String vez = (tabuleiro.getJogadorAtual() == Tabuleiro.PRETO) ? "Preto" : "Branco";
        barraStatus.setText("Vez do " + vez + " | Capturas: Preto=" + tabuleiro.getCapturasPreto() + " | Branco=" + tabuleiro.getCapturasBranco());
    }

    /**
     * Executa a jogada do computador utilizando MCTS.
     */
    private void jogadaComputador() {
        computadorPensando = true;
        barraStatus.setText("Computador está pensando... | Capturas: Preto=" + tabuleiro.getCapturasPreto() + " | Branco=" + tabuleiro.getCapturasBranco());
        setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));

        SwingWorker<int[], Void> worker = new SwingWorker<int[], Void>() {
            @Override
            protected int[] doInBackground() throws Exception {
                // Configuração do MCTS
                Tabuleiro rootTabuleiro = tabuleiro.clone();
                NodoMCTS rootNodo = new NodoMCTS(rootTabuleiro, null, null);
                return mcts(rootNodo, 1000); // VIDAS_MAX = 1000
            }

            @Override
            protected void done() {
                try {
                    int[] movimento = get();
                    if (movimento != null) {
                        if (movimento[0] == -1 && movimento[1] == -1) {
                            tabuleiro.passarTurno();
                        } else {
                            if (!tabuleiro.fazerJogada(movimento[0], movimento[1])) {
                                // Jogada inválida, passar turno
                                tabuleiro.passarTurno();
                            }
                        }
                        atualizarInterface();
                        if (tabuleiro.isFinalizado()) {
                            finalizarJogo();
                        }
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                } finally {
                    computadorPensando = false;
                    setCursor(Cursor.getDefaultCursor());
                    if (!tabuleiro.isFinalizado()) {
                        String vez = (tabuleiro.getJogadorAtual() == Tabuleiro.PRETO) ? "Preto" : "Branco";
                        barraStatus.setText("Vez do " + vez + " | Capturas: Preto=" + tabuleiro.getCapturasPreto() + " | Branco=" + tabuleiro.getCapturasBranco());
                    }
                }
            }
        };

        worker.execute();
    }

    /**
     * Finaliza o jogo exibindo uma mensagem com o vencedor.
     */
    private void finalizarJogo() {
        String vencedor;
        if (tabuleiro.getCapturasPreto() > tabuleiro.getCapturasBranco()) {
            vencedor = "Preto";
        } else if (tabuleiro.getCapturasBranco() > tabuleiro.getCapturasPreto()) {
            vencedor = "Branco";
        } else {
            vencedor = "Empate";
        }
        String mensagem = "Jogo finalizado!\nVencedor: " + vencedor + "\nCapturas: Preto=" + tabuleiro.getCapturasPreto() + " | Branco=" + tabuleiro.getCapturasBranco();
        JOptionPane.showMessageDialog(this, mensagem, "Final do Jogo", JOptionPane.INFORMATION_MESSAGE);
        barraStatus.setText(mensagem);
    }

    /**
     * Implementa o algoritmo MCTS para determinar a melhor jogada.
     *
     * @param root      Nó raiz do MCTS
     * @param iteracoes Número de iterações (VIDAS_MAX)
     * @return Melhor movimento encontrado pelo MCTS
     */
    private int[] mcts(NodoMCTS root, int iteracoes) {
        for (int i = 0; i < iteracoes; i++) {
            NodoMCTS nodo = root;
            // Seleção
            while (nodo.getFilhos() != null && !nodo.getFilhos().isEmpty()) {
                nodo = nodo.selecionarFilho();
            }
            // Expansão
            if (nodo.getVisitas() > 0 && !nodo.tabuleiro.isFinalizado()) {
                nodo.expandir();
                List<NodoMCTS> filhos = nodo.getFilhos();
                if (filhos != null && !filhos.isEmpty()) {
                    nodo = filhos.get(new Random().nextInt(filhos.size()));
                }
            }
            // Simulação
            double resultado = nodo.simular();
            // Retropropagação
            nodo.retropropagar(resultado);
        }
        // Escolher o filho com mais visitas
        if (root.getFilhos() == null || root.getFilhos().isEmpty()) {
            return null;
        }
        NodoMCTS melhorFilho = null;
        int maxVisitas = -1;
        for (NodoMCTS filho : root.getFilhos()) {
            if (filho.getVisitas() > maxVisitas) {
                maxVisitas = filho.getVisitas();
                melhorFilho = filho;
            }
        }
        return (melhorFilho != null) ? melhorFilho.getMovimento() : null;
    }

    /**
     * Classe interna para desenhar o tabuleiro e as peças.
     */
    class PainelTabuleiro extends JPanel {
        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            desenharTabuleiro(g);
            desenharPecas(g);
        }

        /**
         * Desenha as linhas do tabuleiro e os pontos de estrela (hoshi).
         *
         * @param g Objeto Graphics para desenhar
         */
        private void desenharTabuleiro(Graphics g) {
            g.setColor(Color.BLACK);
            int tamanho = tabuleiro.getTamanho();
            for (int i = 1; i <= tamanho; i++) {
                // Linhas horizontais
                g.drawLine(TAMANHO_CELULA, TAMANHO_CELULA * i, TAMANHO_CELULA * tamanho, TAMANHO_CELULA * i);
                // Linhas verticais
                g.drawLine(TAMANHO_CELULA * i, TAMANHO_CELULA, TAMANHO_CELULA * i, TAMANHO_CELULA * tamanho);
            }

            // Desenhar pontos de estrela (hoshi) para 19x19
            int[][] hoshiCoords = {
                {4, 4}, {4, 10}, {4, 16},
                {10, 4}, {10, 10}, {10, 16},
                {16, 4}, {16, 10}, {16, 16}
            };
            for (int[] coord : hoshiCoords) {
                int x = TAMANHO_CELULA * coord[1];
                int y = TAMANHO_CELULA * coord[0];
                g.fillOval(x - 5, y - 5, 10, 10);
            }
        }

        /**
         * Desenha as peças no tabuleiro.
         *
         * @param g Objeto Graphics para desenhar
         */
        private void desenharPecas(Graphics g) {
            for (int i = 0; i < tabuleiro.getTamanho(); i++) {
                for (int j = 0; j < tabuleiro.getTamanho(); j++) {
                    if (tabuleiro.getCelula(i, j) != Tabuleiro.VAZIO) {
                        int x = TAMANHO_CELULA * (j + 1);
                        int y = TAMANHO_CELULA * (i + 1);
                        if (tabuleiro.getCelula(i, j) == Tabuleiro.PRETO) {
                            desenharPeca(g, x, y, Color.BLACK, Color.DARK_GRAY);
                        } else {
                            desenharPeca(g, x, y, Color.WHITE, Color.LIGHT_GRAY);
                        }
                    }
                }
            }
        }

        /**
         * Desenha uma peça com efeito de sombra para melhor visualização.
         *
         * @param g      Objeto Graphics para desenhar
         * @param x      Coordenada X central da peça
         * @param y      Coordenada Y central da peça
         * @param cor    Cor principal da peça
         * @param sombra Cor da sombra da peça
         */
        private void desenharPeca(Graphics g, int x, int y, Color cor, Color sombra) {
            // Desenhar sombra para efeito 3D
            g.setColor(sombra);
            g.fillOval(x - (int)(0.4 * TAMANHO_CELULA), y - (int)(0.4 * TAMANHO_CELULA),
                       (int)(0.8 * TAMANHO_CELULA), (int)(0.8 * TAMANHO_CELULA));
            // Desenhar a pedra
            g.setColor(cor);
            g.fillOval(x - (int)(0.35 * TAMANHO_CELULA), y - (int)(0.35 * TAMANHO_CELULA),
                       (int)(0.7 * TAMANHO_CELULA), (int)(0.7 * TAMANHO_CELULA));
        }
    }
}
