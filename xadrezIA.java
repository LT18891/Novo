import javax.swing.*;
import javax.swing.border.LineBorder;
import java.awt.*;
import java.awt.event.*;
import java.util.*;
import java.util.List;

public class JogoXadrezIA extends JFrame {
    /**
     * 
     */
    private static final long serialVersionUID = 1L;

    // Representação do Tabuleiro Inicial
    private final String[][] tabuleiroInicial = {
        {"r", "n", "b", "q", "k", "b", "n", "r"},
        {"p", "p", "p", "p", "p", "p", "p", "p"},
        {null, null, null, null, null, null, null, null},
        {null, null, null, null, null, null, null, null},
        {null, null, null, null, null, null, null, null},
        {null, null, null, null, null, null, null, null},
        {"P", "P", "P", "P", "P", "P", "P", "P"},
        {"R", "N", "B", "Q", "K", "B", "N", "R"}
    };

    // Mapeamento dos Símbolos Unicode para as Peças
    private final Map<String, String> simbolosPecas = new HashMap<>();

    // Estado do Jogo
    private String[][] tabuleiro;
    private int[] pecaSelecionada = null;
    private String jogadorAtual = "brancas"; // "brancas" ou "pretas"
    private boolean jogoFinalizado = false;
    private String dificuldade = "fácil";
    private List<Movimento> historicoMovimentos = new ArrayList<>();

    // Componentes da GUI
    private JPanel painelTabuleiro;
    private JLabel labelStatus;
    private JLabel labelAutor; // Novo JLabel para a legenda do autor
    private JComboBox<String> comboDificuldade;
    private JButton botaoReiniciar;
    private JButton[][] botoesTabuleiro = new JButton[8][8];

    public JogoXadrezIA() {
        inicializarSimbolosPecas();
        inicializarEstadoJogo();
        configurarInterface();
        inicializarTabuleiro();
    }

    // Inicializar o mapeamento dos símbolos das peças
    private void inicializarSimbolosPecas() {
        simbolosPecas.put("P", "\u2659");
        simbolosPecas.put("p", "\u265F");
        simbolosPecas.put("R", "\u2656");
        simbolosPecas.put("r", "\u265C");
        simbolosPecas.put("N", "\u2658");
        simbolosPecas.put("n", "\u265E");
        simbolosPecas.put("B", "\u2657");
        simbolosPecas.put("b", "\u265D");
        simbolosPecas.put("Q", "\u2655");
        simbolosPecas.put("q", "\u265B");
        simbolosPecas.put("K", "\u2654");
        simbolosPecas.put("k", "\u265A");
    }

    // Inicializar o estado do jogo
    private void inicializarEstadoJogo() {
        tabuleiro = new String[8][8];
        for (int i = 0; i < 8; i++) {
            tabuleiro[i] = Arrays.copyOf(tabuleiroInicial[i], 8);
        }
    }

    // Configurar a interface gráfica
    private void configurarInterface() {
        setTitle("Jogo de Xadrez com IA");
        setSize(520, 800); // Aumentar a altura para acomodar a legenda
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        // Título
        JLabel titulo = new JLabel("Jogo de Xadrez com IA", SwingConstants.CENTER);
        titulo.setFont(new Font("Orbitron", Font.BOLD, 24));
        titulo.setForeground(new Color(0xFF3333));
        titulo.setBorder(BorderFactory.createEmptyBorder(10, 0, 10, 0));
        add(titulo, BorderLayout.NORTH);

        // Tabuleiro
        painelTabuleiro = new JPanel(new GridLayout(8, 8));
        painelTabuleiro.setBorder(BorderFactory.createLineBorder(Color.BLACK, 4));
        add(painelTabuleiro, BorderLayout.CENTER);

        // Rodapé (Controles, Status e Legenda)
        JPanel painelFooter = new JPanel();
        painelFooter.setLayout(new BoxLayout(painelFooter, BoxLayout.Y_AXIS));
        painelFooter.setBackground(new Color(0x0D0D0D));

        // Controles
        JPanel painelControles = new JPanel(new FlowLayout());
        painelControles.setBackground(new Color(0x0D0D0D));
        painelControles.add(new JLabel("Nível de Dificuldade:"));

        comboDificuldade = new JComboBox<>(new String[]{"Fácil", "Médio", "Difícil"});
        painelControles.add(comboDificuldade);

        botaoReiniciar = new JButton("Reiniciar Jogo");
        botaoReiniciar.addActionListener(e -> reiniciarJogo());
        painelControles.add(botaoReiniciar);

        painelFooter.add(painelControles);

        // Status
        labelStatus = new JLabel("Turno: Brancas", SwingConstants.CENTER);
        labelStatus.setFont(new Font("Arial", Font.PLAIN, 18));
        labelStatus.setForeground(Color.WHITE);
        labelStatus.setBackground(new Color(0x0D0D0D));
        labelStatus.setOpaque(true);
        labelStatus.setBorder(BorderFactory.createEmptyBorder(10, 0, 10, 0));
        painelFooter.add(labelStatus);

        // Legenda do Autor
        labelAutor = new JLabel("Autor: Luiz Tiago Wilcke-Jogo em Java", SwingConstants.CENTER);
        labelAutor.setFont(new Font("Arial", Font.PLAIN, 14));
        labelAutor.setForeground(Color.BLUE);
        labelAutor.setBorder(BorderFactory.createEmptyBorder(5, 0, 5, 0));
        painelFooter.add(labelAutor);

        add(painelFooter, BorderLayout.SOUTH);

        // Personalizar cores do painel principal
        painelTabuleiro.setBackground(new Color(0x1A1A1A));
        labelStatus.setBackground(new Color(0x0D0D0D));

        // Exibir a janela
        setVisible(true);
    }

    // Inicializar o tabuleiro na GUI
    private void inicializarTabuleiro() {
        painelTabuleiro.removeAll();
        for (int x = 0; x < 8; x++) {
            for (int y = 0; y < 8; y++) {
                JButton casa = new JButton();
                casa.setFont(new Font("SansSerif", Font.PLAIN, 32));
                casa.setFocusable(false);
                casa.setMargin(new Insets(0,0,0,0));
                casa.setBorder(new LineBorder(Color.BLACK));
                casa.setBackground((x + y) % 2 == 0 ? new Color(0x4D4D4D) : new Color(0x1A1A1A));
                casa.setForeground(Color.WHITE);
                if (tabuleiro[x][y] != null) {
                    casa.setText(simbolosPecas.get(tabuleiro[x][y]));
                }
                int posX = x;
                int posY = y;
                casa.addActionListener(e -> lidarCliqueCasa(posX, posY));
                botoesTabuleiro[x][y] = casa;
                painelTabuleiro.add(casa);
            }
        }
        painelTabuleiro.revalidate();
        painelTabuleiro.repaint();
        atualizarStatus();
    }

    // Atualizar a interface do tabuleiro
    private void atualizarInterfaceTabuleiro() {
        for (int x = 0; x < 8; x++) {
            for (int y = 0; y < 8; y++) {
                JButton casa = botoesTabuleiro[x][y];
                if (tabuleiro[x][y] != null) {
                    casa.setText(simbolosPecas.get(tabuleiro[x][y]));
                } else {
                    casa.setText("");
                }
                casa.setBorder(new LineBorder(Color.BLACK));
                // Resetar cores
                casa.setBackground((x + y) % 2 == 0 ? new Color(0x4D4D4D) : new Color(0x1A1A1A));
            }
        }
        if (pecaSelecionada != null) {
            int selX = pecaSelecionada[0];
            int selY = pecaSelecionada[1];
            botoesTabuleiro[selX][selY].setBorder(new LineBorder(new Color(0x00FFEA), 3));
            List<int[]> movimentos = obterMovimentosPossiveis(pecaSelecionada, tabuleiro);
            for (int[] move : movimentos) {
                botoesTabuleiro[move[0]][move[1]].setBackground(new Color(0x00FFEA));
                botoesTabuleiro[move[0]][move[1]].setForeground(Color.WHITE);
            }
        }
        atualizarStatus();
    }

    // Atualizar o status do jogo
    private void atualizarStatus() {
        if (jogoFinalizado) {
            labelStatus.setText("Fim do Jogo: " + (jogadorAtual.equals("brancas") ? "Pretas" : "Brancas") + " venceram!");
        } else {
            labelStatus.setText("Turno: " + (jogadorAtual.equals("brancas") ? "Brancas" : "Pretas"));
        }
    }

    // Manipular cliques nas casas do tabuleiro
    private void lidarCliqueCasa(int x, int y) {
        if (jogoFinalizado) return;

        String peca = tabuleiro[x][y];
        if (pecaSelecionada != null) {
            int selX = pecaSelecionada[0];
            int selY = pecaSelecionada[1];
            List<int[]> movimentosPossiveis = obterMovimentosPossiveis(pecaSelecionada, tabuleiro);
            boolean movimentoValido = movimentosPossiveis.stream().anyMatch(move -> move[0] == x && move[1] == y);
            if (movimentoValido) {
                realizarMovimento(pecaSelecionada, new int[]{x, y});
                pecaSelecionada = null;
                atualizarInterfaceTabuleiro();
                // IA joga se for a vez das pretas
                if (!jogoFinalizado && jogadorAtual.equals("pretas")) {
                    jogadaIA();
                }
                return;
            }
        }

        if (peca != null && ehPecaDoJogador(peca, jogadorAtual)) {
            pecaSelecionada = new int[]{x, y};
            atualizarInterfaceTabuleiro();
        }
    }

    // Verificar se a peça pertence ao jogador atual
    private boolean ehPecaDoJogador(String peca, String jogador) {
        if (jogador.equals("brancas")) {
            return peca.equals(peca.toUpperCase());
        } else {
            return peca.equals(peca.toLowerCase());
        }
    }

    // Verificar se a peça é do oponente
    private boolean ehPecaDoOponente(String peca, boolean isBrancas) {
        if (isBrancas) {
            return peca.equals(peca.toLowerCase());
        } else {
            return peca.equals(peca.toUpperCase());
        }
    }

    // Gerar movimentos possíveis para uma peça
    private List<int[]> obterMovimentosPossiveis(int[] posicao, String[][] estadoTabuleiro) {
        return obterMovimentosPossiveis(posicao, estadoTabuleiro, true);
    }

    private List<int[]> obterMovimentosPossiveis(int[] posicao, String[][] estadoTabuleiro, boolean verificarSegurancaRei) {
        List<int[]> movimentos = new ArrayList<>();
        int x = posicao[0];
        int y = posicao[1];
        String peca = estadoTabuleiro[x][y];
        if (peca == null) return movimentos;

        Map<String, int[][]> direcoes = new HashMap<>();
        direcoes.put("P", new int[][]{{-1, 0}, {-1, -1}, {-1, 1}});
        direcoes.put("p", new int[][]{{1, 0}, {1, -1}, {1, 1}});
        direcoes.put("R", new int[][]{{1,0}, {-1,0}, {0,1}, {0,-1}});
        direcoes.put("B", new int[][]{{1,1}, {1,-1}, {-1,1}, {-1,-1}});
        direcoes.put("Q", new int[][]{{1,0}, {-1,0}, {0,1}, {0,-1}, {1,1}, {1,-1}, {-1,1}, {-1,-1}});
        direcoes.put("K", new int[][]{{1,0}, {-1,0}, {0,1}, {0,-1}, {1,1}, {1,-1}, {-1,1}, {-1,-1}});
        direcoes.put("N", new int[][]{{2,1}, {1,2}, {-1,2}, {-2,1}, {-2,-1}, {-1,-2}, {1,-2}, {2,-1}});

        String tipoPeca = peca.toUpperCase();
        boolean isBrancas = peca.equals(peca.toUpperCase());
        String oponente = isBrancas ? "pretas" : "brancas";

        switch (tipoPeca) {
            case "P":
                // Movimento para frente
                int[][] direcaoP = direcoes.get(peca);
                int fx = x + direcaoP[0][0];
                int fy = y + direcaoP[0][1];
                if (ehPosicaoValida(fx, fy) && estadoTabuleiro[fx][fy] == null) {
                    movimentos.add(new int[]{fx, fy});
                    // Primeiro movimento pode avançar duas casas
                    if ((isBrancas && x == 6) || (!isBrancas && x == 1)) {
                        int duplaFrente = x + direcaoP[0][0] * 2;
                        if (ehPosicaoValida(duplaFrente, fy) && estadoTabuleiro[duplaFrente][fy] == null) {
                            movimentos.add(new int[]{duplaFrente, fy});
                        }
                    }
                }
                // Capturas
                for (int i = 1; i < direcaoP.length; i++) {
                    int cx = x + direcaoP[i][0];
                    int cy = y + direcaoP[i][1];
                    if (ehPosicaoValida(cx, cy) && estadoTabuleiro[cx][cy] != null
                            && ehPecaDoOponente(estadoTabuleiro[cx][cy], isBrancas)) {
                        movimentos.add(new int[]{cx, cy});
                    }
                }
                // En Passant (não implementado)
                break;
            case "N":
                for (int[] dir : direcoes.get("N")) {
                    int nx = x + dir[0];
                    int ny = y + dir[1];
                    if (ehPosicaoValida(nx, ny) && (estadoTabuleiro[nx][ny] == null
                            || ehPecaDoOponente(estadoTabuleiro[nx][ny], isBrancas))) {
                        movimentos.add(new int[]{nx, ny});
                    }
                }
                break;
            case "R":
            case "B":
            case "Q":
                for (int[] dir : direcoes.get(tipoPeca)) {
                    int nx = x + dir[0];
                    int ny = y + dir[1];
                    while (ehPosicaoValida(nx, ny)) {
                        if (estadoTabuleiro[nx][ny] == null) {
                            movimentos.add(new int[]{nx, ny});
                        } else {
                            if (ehPecaDoOponente(estadoTabuleiro[nx][ny], isBrancas)) {
                                movimentos.add(new int[]{nx, ny});
                            }
                            break;
                        }
                        nx += dir[0];
                        ny += dir[1];
                    }
                }
                break;
            case "K":
                for (int[] dir : direcoes.get("K")) {
                    int kx = x + dir[0];
                    int ky = y + dir[1];
                    if (ehPosicaoValida(kx, ky) && (estadoTabuleiro[kx][ky] == null
                            || ehPecaDoOponente(estadoTabuleiro[kx][ky], isBrancas))) {
                        movimentos.add(new int[]{kx, ky});
                    }
                }
                // Roque (não implementado)
                break;
            default:
                break;
        }

        // Filtrar movimentos que deixam o rei em xeque, se necessário
        if (verificarSegurancaRei) {
            List<int[]> movimentosLegais = new ArrayList<>();
            for (int[] move : movimentos) {
                String[][] novoTabuleiro = clonarTabuleiro(estadoTabuleiro);
                novoTabuleiro[move[0]][move[1]] = novoTabuleiro[x][y];
                novoTabuleiro[x][y] = null;
                String jogador = isBrancas ? "brancas" : "pretas";
                if (!estaEmXeque(novoTabuleiro, jogador)) {
                    movimentosLegais.add(move);
                }
            }
            return movimentosLegais;
        } else {
            return movimentos;
        }
    }

    // Clonar o tabuleiro para simulações
    private String[][] clonarTabuleiro(String[][] estadoTabuleiro) {
        String[][] novoTabuleiro = new String[8][8];
        for (int i = 0; i < 8; i++) {
            novoTabuleiro[i] = Arrays.copyOf(estadoTabuleiro[i], 8);
        }
        return novoTabuleiro;
    }

    // Verificar se a posição é válida no tabuleiro
    private boolean ehPosicaoValida(int x, int y) {
        return x >= 0 && x < 8 && y >= 0 && y < 8;
    }

    // Realizar um movimento
    private void realizarMovimento(int[] de, int[] para) {
        String pecaMovida = tabuleiro[de[0]][de[1]];
        String pecaCapturada = tabuleiro[para[0]][para[1]];
        tabuleiro[para[0]][para[1]] = pecaMovida;
        tabuleiro[de[0]][de[1]] = null;

        // Promoção de Peão (sempre promove para Rainha)
        if (pecaMovida.toUpperCase().equals("P") && (para[0] == 0 || para[0] == 7)) {
            tabuleiro[para[0]][para[1]] = pecaMovida.equals("P") ? "Q" : "q";
        }

        historicoMovimentos.add(new Movimento(de, para, pecaMovida, pecaCapturada));
        jogadorAtual = jogadorAtual.equals("brancas") ? "pretas" : "brancas";
        verificarFimDeJogo();
    }

    // Verificar se o rei está em xeque
    private boolean estaEmXeque(String[][] estadoTabuleiro, String jogador) {
        String rei = jogador.equals("brancas") ? "K" : "k";
        int[] posRei = null;

        // Encontrar a posição do rei
        for (int x = 0; x < 8; x++) {
            for (int y = 0; y < 8; y++) {
                if (estadoTabuleiro[x][y] != null && estadoTabuleiro[x][y].equals(rei)) {
                    posRei = new int[]{x, y};
                    break;
                }
            }
            if (posRei != null) break;
        }

        if (posRei == null) return true; // Rei não encontrado, está em xeque

        String oponente = jogador.equals("brancas") ? "pretas" : "brancas";

        // Iterar sobre todas as peças do oponente e verificar se alguma pode atacar o rei
        for (int x = 0; x < 8; x++) {
            for (int y = 0; y < 8; y++) {
                String peca = estadoTabuleiro[x][y];
                if (peca != null && ehPecaDoJogador(peca, oponente)) {
                    List<int[]> movimentosAtaque = obterMovimentosPossiveis(new int[]{x, y}, estadoTabuleiro, false);
                    for (int[] move : movimentosAtaque) {
                        if (move[0] == posRei[0] && move[1] == posRei[1]) {
                            return true;
                        }
                    }
                }
            }
        }
        return false;
    }

    // Verificar o fim de jogo (xeque-mate)
    private void verificarFimDeJogo() {
        if (estaEmXeque(tabuleiro, jogadorAtual)) {
            List<Movimento> todosMovimentos = gerarTodosMovimentos(tabuleiro, jogadorAtual);
            if (todosMovimentos.isEmpty()) {
                jogoFinalizado = true;
                atualizarStatus();
                return;
            } else {
                labelStatus.setText("Xeque! Turno: " + (jogadorAtual.equals("brancas") ? "Brancas" : "Pretas"));
                return;
            }
        } else {
            // Verificar empate (não implementado)
            labelStatus.setText("Turno: " + (jogadorAtual.equals("brancas") ? "Brancas" : "Pretas"));
        }
    }

    // Gerar todos os movimentos legais para um jogador
    private List<Movimento> gerarTodosMovimentos(String[][] estadoTabuleiro, String jogador) {
        List<Movimento> movimentos = new ArrayList<>();
        for (int x = 0; x < 8; x++) {
            for (int y = 0; y < 8; y++) {
                String peca = estadoTabuleiro[x][y];
                if (peca != null && ehPecaDoJogador(peca, jogador)) {
                    List<int[]> movimentosPeca = obterMovimentosPossiveis(new int[]{x, y}, estadoTabuleiro);
                    for (int[] move : movimentosPeca) {
                        movimentos.add(new Movimento(new int[]{x, y}, move, peca, estadoTabuleiro[move[0]][move[1]]));
                    }
                }
            }
        }
        return movimentos;
    }

    // Implementação da IA
    private void jogadaIA() {
        if (jogoFinalizado) return;
        dificuldade = (String) comboDificuldade.getSelectedItem();
        Movimento movimento;
        if (dificuldade.equals("Fácil")) {
            movimento = obterMovimentoAleatorio(tabuleiro, "pretas");
        } else if (dificuldade.equals("Médio")) {
            movimento = obterMovimentoMinimax(tabuleiro, 3, "pretas");
        } else { // Difícil
            movimento = obterMovimentoMinimax(tabuleiro, 4, "pretas");
        }
        if (movimento != null) {
            realizarMovimento(movimento.de, movimento.para);
            atualizarInterfaceTabuleiro();
            // Se a IA conseguir realizar outro movimento, chama novamente (para evitar loops infinitos)
            if (!jogoFinalizado && jogadorAtual.equals("pretas")) {
                jogadaIA();
            }
        }
    }

    // IA Nível Fácil: Movimento Aleatório
    private Movimento obterMovimentoAleatorio(String[][] estadoTabuleiro, String jogador) {
        List<Movimento> todosMovimentos = gerarTodosMovimentos(estadoTabuleiro, jogador);
        if (todosMovimentos.isEmpty()) return null;
        Random rand = new Random();
        return todosMovimentos.get(rand.nextInt(todosMovimentos.size()));
    }

    // IA Níveis Médio e Difícil: Minimax com Poda Alfa-Beta
    private Movimento obterMovimentoMinimax(String[][] estadoTabuleiro, int profundidade, String jogador) {
        List<Movimento> todosMovimentos = gerarTodosMovimentos(estadoTabuleiro, jogador);
        if (todosMovimentos.isEmpty()) return null;

        Movimento melhorMovimento = null;
        int melhorValor = jogador.equals("pretas") ? Integer.MAX_VALUE : Integer.MIN_VALUE;

        for (Movimento movimento : todosMovimentos) {
            String[][] novoTabuleiro = clonarTabuleiro(estadoTabuleiro);
            novoTabuleiro[movimento.para[0]][movimento.para[1]] = novoTabuleiro[movimento.de[0]][movimento.de[1]];
            novoTabuleiro[movimento.de[0]][movimento.de[1]] = null;
            // Promoção de Peão
            if (movimento.pecaMovida.toUpperCase().equals("P") && (movimento.para[0] == 0 || movimento.para[0] == 7)) {
                novoTabuleiro[movimento.para[0]][movimento.para[1]] = movimento.pecaMovida.equals("P") ? "Q" : "q";
            }
            int valorTabuleiro = minimax(novoTabuleiro, profundidade - 1, Integer.MIN_VALUE, Integer.MAX_VALUE, jogador.equals("pretas") ? "brancas" : "pretas");

            if (jogador.equals("pretas")) {
                if (valorTabuleiro < melhorValor) {
                    melhorValor = valorTabuleiro;
                    melhorMovimento = movimento;
                }
            } else {
                if (valorTabuleiro > melhorValor) {
                    melhorValor = valorTabuleiro;
                    melhorMovimento = movimento;
                }
            }
        }

        return melhorMovimento;
    }

    private int minimax(String[][] estadoTabuleiro, int profundidade, int alfa, int beta, String jogador) {
        if (profundidade == 0) {
            return avaliarTabuleiro(estadoTabuleiro);
        }

        if (jogador.equals("brancas")) {
            int maxEval = Integer.MIN_VALUE;
            List<Movimento> todosMovimentos = gerarTodosMovimentos(estadoTabuleiro, "brancas");
            if (todosMovimentos.isEmpty()) return avaliarTabuleiro(estadoTabuleiro);
            for (Movimento movimento : todosMovimentos) {
                String[][] novoTabuleiro = clonarTabuleiro(estadoTabuleiro);
                novoTabuleiro[movimento.para[0]][movimento.para[1]] = novoTabuleiro[movimento.de[0]][movimento.de[1]];
                novoTabuleiro[movimento.de[0]][movimento.de[1]] = null;
                // Promoção de Peão
                if (movimento.pecaMovida.toUpperCase().equals("P") && (movimento.para[0] == 0 || movimento.para[0] == 7)) {
                    novoTabuleiro[movimento.para[0]][movimento.para[1]] = movimento.pecaMovida.equals("P") ? "Q" : "q";
                }
                int aval = minimax(novoTabuleiro, profundidade - 1, alfa, beta, "pretas");
                maxEval = Math.max(maxEval, aval);
                alfa = Math.max(alfa, aval);
                if (beta <= alfa) break;
            }
            return maxEval;
        } else { // "pretas"
            int minEval = Integer.MAX_VALUE;
            List<Movimento> todosMovimentos = gerarTodosMovimentos(estadoTabuleiro, "pretas");
            if (todosMovimentos.isEmpty()) return avaliarTabuleiro(estadoTabuleiro);
            for (Movimento movimento : todosMovimentos) {
                String[][] novoTabuleiro = clonarTabuleiro(estadoTabuleiro);
                novoTabuleiro[movimento.para[0]][movimento.para[1]] = novoTabuleiro[movimento.de[0]][movimento.de[1]];
                novoTabuleiro[movimento.de[0]][movimento.de[1]] = null;
                // Promoção de Peão
                if (movimento.pecaMovida.toUpperCase().equals("P") && (movimento.para[0] == 0 || movimento.para[0] == 7)) {
                    novoTabuleiro[movimento.para[0]][movimento.para[1]] = movimento.pecaMovida.equals("P") ? "Q" : "q";
                }
                int aval = minimax(novoTabuleiro, profundidade - 1, alfa, beta, "brancas");
                minEval = Math.min(minEval, aval);
                beta = Math.min(beta, aval);
                if (beta <= alfa) break;
            }
            return minEval;
        }
    }

    // Avaliação do Tabuleiro
    private int avaliarTabuleiro(String[][] estadoTabuleiro) {
        Map<String, Integer> valorPecas = new HashMap<>();
        valorPecas.put("P", 10); valorPecas.put("p", -10);
        valorPecas.put("N", 30); valorPecas.put("n", -30);
        valorPecas.put("B", 30); valorPecas.put("b", -30);
        valorPecas.put("R", 50); valorPecas.put("r", -50);
        valorPecas.put("Q", 90); valorPecas.put("q", -90);
        valorPecas.put("K", 900); valorPecas.put("k", -900);

        int pontuacao = 0;
        for (int x = 0; x < 8; x++) {
            for (int y = 0; y < 8; y++) {
                String peca = estadoTabuleiro[x][y];
                if (peca != null) {
                    pontuacao += valorPecas.getOrDefault(peca, 0);
                }
            }
        }
        return pontuacao;
    }

    // Reiniciar o jogo
    private void reiniciarJogo() {
        inicializarEstadoJogo();
        pecaSelecionada = null;
        jogadorAtual = "brancas";
        jogoFinalizado = false;
        historicoMovimentos.clear();
        inicializarTabuleiro();
    }

    // Classe para representar um movimento
    private class Movimento {
        int[] de;
        int[] para;
        String pecaMovida;
        String pecaCapturada;

        Movimento(int[] de, int[] para, String pecaMovida, String pecaCapturada) {
            this.de = de;
            this.para = para;
            this.pecaMovida = pecaMovida;
            this.pecaCapturada = pecaCapturada;
        }
    }

    // Método principal para executar o jogo
    public static void main(String[] args) {
        // Definir o tema escuro para a interface
        try {
            UIManager.setLookAndFeel(UIManager.getCrossPlatformLookAndFeelClassName());
        } catch(Exception ignored){}

        SwingUtilities.invokeLater(() -> new JogoXadrezIA());
    }
}
