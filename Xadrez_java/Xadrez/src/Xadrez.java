import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.List;

public class Xadrez {
    // Dimensões da janela e tabuleiro
    private static final int LARGURA_TABULEIRO = 640;
    private static final int ALTURA_TABULEIRO = 640;
    private static final int LARGURA_JANELA = 1000;
    private static final int ALTURA_JANELA = 640;
    private static final int TAMANHO_QUADRADO = LARGURA_TABULEIRO / 8;

    // Cores
    private static final Color BRANCO = new Color(255, 255, 255);
    private static final Color PRETO = new Color(0, 0, 0);
    private static final Color AZUL = new Color(0, 0, 255);
    private static final Color VERMELHO = new Color(255, 0, 0);
    private static final Color CINZA = new Color(128, 128, 128);
    private static final Color VERDE = new Color(0, 255, 0);
    private static final Color AMARELO = new Color(255, 255, 0);
    private static final Color AZUL_LEGENDA = new Color(0, 0, 255);

    // Símbolos Unicode das peças
    private static final java.util.Map<String, String> SIMBOLOS_PECAS = new java.util.HashMap<>();
    static {
        SIMBOLOS_PECAS.put("rei_azul", "\u2654");
        SIMBOLOS_PECAS.put("rainha_azul", "\u2655");
        SIMBOLOS_PECAS.put("torre_azul", "\u2656");
        SIMBOLOS_PECAS.put("bispo_azul", "\u2657");
        SIMBOLOS_PECAS.put("cavalo_azul", "\u2658");
        SIMBOLOS_PECAS.put("peao_azul", "\u2659");

        SIMBOLOS_PECAS.put("rei_vermelho", "\u265A");
        SIMBOLOS_PECAS.put("rainha_vermelho", "\u265B");
        SIMBOLOS_PECAS.put("torre_vermelho", "\u265C");
        SIMBOLOS_PECAS.put("bispo_vermelho", "\u265D");
        SIMBOLOS_PECAS.put("cavalo_vermelho", "\u265E");
        SIMBOLOS_PECAS.put("peao_vermelho", "\u265F");
    }

    // Valores das peças
    private static final java.util.Map<String, Integer> VALOR_PECAS = new java.util.HashMap<>();
    static {
        VALOR_PECAS.put("peao", 10);
        VALOR_PECAS.put("cavalo", 30);
        VALOR_PECAS.put("bispo", 30);
        VALOR_PECAS.put("torre", 50);
        VALOR_PECAS.put("rainha", 90);
        VALOR_PECAS.put("rei", 900);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("Jogo de Xadrez do Tiago");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

            Jogo jogo = new Jogo();
            TabuleiroPanel panel = new TabuleiroPanel(jogo);

            frame.add(panel);
            frame.pack(); // Ajusta o tamanho da janela de acordo com o tamanho preferido do painel
            frame.setLocationRelativeTo(null); // Centraliza a janela na tela
            frame.setResizable(false);
            frame.setVisible(true);
        });
    }

    // Classe Peca
    static class Peca {
        String tipo;  // rei, rainha, bispo, cavalo, torre, peao
        String cor;   // azul ou vermelho
        String simbolo;
        int movimentos_realizados = 0;

        Peca(String tipo, String cor) {
            this.tipo = tipo;
            this.cor = cor;
            this.simbolo = SIMBOLOS_PECAS.get(tipo + "_" + cor);
        }

        List<Point> movimentos_validos(int x, int y, Peca[][] tabuleiro, java.util.Map<String, java.util.Map<String, Boolean>> roque_disponivel) {
            List<Point> movimentos = new ArrayList<>();

            if (tipo.equals("peao")) {
                int direcao = (cor.equals("azul")) ? -1 : 1;
                int novo_y = y + direcao;
                if (novo_y >= 0 && novo_y < 8) {
                    if (tabuleiro[novo_y][x] == null) {
                        movimentos.add(new Point(x, novo_y));
                        // Movimento duplo
                        if ((cor.equals("azul") && y == 6) || (cor.equals("vermelho") && y == 1)) {
                            int novo_y2 = y + 2 * direcao;
                            if (novo_y2 >= 0 && novo_y2 < 8 && tabuleiro[novo_y2][x] == null) {
                                movimentos.add(new Point(x, novo_y2));
                            }
                        }
                    }
                    // Captura diagonal
                    for (int dx : new int[]{-1, 1}) {
                        int nx = x + dx;
                        if (nx >= 0 && nx < 8) {
                            Peca pecaDestino = tabuleiro[novo_y][nx];
                            if (pecaDestino != null && !pecaDestino.cor.equals(cor)) {
                                movimentos.add(new Point(nx, novo_y));
                            }
                        }
                    }
                }
            } else if (tipo.equals("torre")) {
                int[][] direcoes = {{-1,0},{1,0},{0,-1},{0,1}};
                for (int[] d : direcoes) {
                    int nx = x + d[0];
                    int ny = y + d[1];
                    while (nx >= 0 && nx < 8 && ny >= 0 && ny < 8) {
                        Peca p = tabuleiro[ny][nx];
                        if (p == null) {
                            movimentos.add(new Point(nx, ny));
                        } else if (!p.cor.equals(cor)) {
                            movimentos.add(new Point(nx, ny));
                            break;
                        } else {
                            break;
                        }
                        nx += d[0];
                        ny += d[1];
                    }
                }
            } else if (tipo.equals("bispo")) {
                int[][] direcoes = {{-1,-1},{-1,1},{1,-1},{1,1}};
                for (int[] d : direcoes) {
                    int nx = x + d[0];
                    int ny = y + d[1];
                    while (nx >= 0 && nx < 8 && ny >= 0 && ny < 8) {
                        Peca p = tabuleiro[ny][nx];
                        if (p == null) {
                            movimentos.add(new Point(nx, ny));
                        } else if (!p.cor.equals(cor)) {
                            movimentos.add(new Point(nx, ny));
                            break;
                        } else {
                            break;
                        }
                        nx += d[0];
                        ny += d[1];
                    }
                }
            } else if (tipo.equals("rainha")) {
                int[][] direcoes = {
                    {-1,0},{1,0},{0,-1},{0,1},
                    {-1,-1},{-1,1},{1,-1},{1,1}
                };
                for (int[] d : direcoes) {
                    int nx = x + d[0];
                    int ny = y + d[1];
                    while (nx >= 0 && nx < 8 && ny >= 0 && ny < 8) {
                        Peca p = tabuleiro[ny][nx];
                        if (p == null) {
                            movimentos.add(new Point(nx, ny));
                        } else if (!p.cor.equals(cor)) {
                            movimentos.add(new Point(nx, ny));
                            break;
                        } else {
                            break;
                        }
                        nx += d[0];
                        ny += d[1];
                    }
                }
            } else if (tipo.equals("rei")) {
                int[][] direcoes = {
                    {-1,-1},{-1,0},{-1,1},
                    {0,-1},{0,1},
                    {1,-1},{1,0},{1,1}
                };
                for (int[] d : direcoes) {
                    int nx = x + d[0];
                    int ny = y + d[1];
                    if (nx >= 0 && nx < 8 && ny >= 0 && ny < 8) {
                        Peca p = tabuleiro[ny][nx];
                        if (p == null || !p.cor.equals(cor)) {
                            movimentos.add(new Point(nx, ny));
                        }
                    }
                }
            } else if (tipo.equals("cavalo")) {
                int[][] movimentosCavalo = {
                    {1,2},{1,-2},{-1,2},{-1,-2},
                    {2,1},{2,-1},{-2,1},{-2,-1}
                };
                for (int[] mc : movimentosCavalo) {
                    int nx = x + mc[0];
                    int ny = y + mc[1];
                    if (nx >= 0 && nx < 8 && ny >= 0 && ny < 8) {
                        Peca p = tabuleiro[ny][nx];
                        if (p == null || !p.cor.equals(cor)) {
                            movimentos.add(new Point(nx, ny));
                        }
                    }
                }
            }
            return movimentos;
        }

        Peca copia() {
            Peca p = new Peca(this.tipo, this.cor);
            p.movimentos_realizados = this.movimentos_realizados;
            return p;
        }
    }

    // Classe Jogo
    static class Jogo {
        Peca[][] tabuleiro = new Peca[8][8];
        String jogador_atual = "azul";
        List<MovimentoHistorico> historico = new ArrayList<>();
        java.util.Map<String, java.util.Map<String, Boolean>> roque_disponivel = new java.util.HashMap<>();

        Jogo() {
            java.util.Map<String, Boolean> azulRoque = new java.util.HashMap<>();
            azulRoque.put("roque_menos", true);
            azulRoque.put("roque_mais", true);

            java.util.Map<String, Boolean> vermelhoRoque = new java.util.HashMap<>();
            vermelhoRoque.put("roque_menos", true);
            vermelhoRoque.put("roque_mais", true);

            roque_disponivel.put("azul", azulRoque);
            roque_disponivel.put("vermelho", vermelhoRoque);

            iniciar_tabuleiro();
        }

        void iniciar_tabuleiro() {
            // Peças azuis
            for (int i = 0; i < 8; i++) {
                tabuleiro[6][i] = new Peca("peao", "azul");
            }
            tabuleiro[7][0] = new Peca("torre", "azul");
            tabuleiro[7][1] = new Peca("cavalo", "azul");
            tabuleiro[7][2] = new Peca("bispo", "azul");
            tabuleiro[7][3] = new Peca("rainha", "azul");
            tabuleiro[7][4] = new Peca("rei", "azul");
            tabuleiro[7][5] = new Peca("bispo", "azul");
            tabuleiro[7][6] = new Peca("cavalo", "azul");
            tabuleiro[7][7] = new Peca("torre", "azul");

            // Peças vermelhas
            for (int i = 0; i < 8; i++) {
                tabuleiro[1][i] = new Peca("peao", "vermelho");
            }
            tabuleiro[0][0] = new Peca("torre", "vermelho");
            tabuleiro[0][1] = new Peca("cavalo", "vermelho");
            tabuleiro[0][2] = new Peca("bispo", "vermelho");
            tabuleiro[0][3] = new Peca("rainha", "vermelho");
            tabuleiro[0][4] = new Peca("rei", "vermelho");
            tabuleiro[0][5] = new Peca("bispo", "vermelho");
            tabuleiro[0][6] = new Peca("cavalo", "vermelho");
            tabuleiro[0][7] = new Peca("torre", "vermelho");
        }

        void mover_peca(Point origem, Point destino) {
            mover_peca(origem, destino, false, null);
        }

        void mover_peca(Point origem, Point destino, boolean is_ai_move, Double eval_score) {
            int x1 = origem.x;
            int y1 = origem.y;
            int x2 = destino.x;
            int y2 = destino.y;
            Peca peca = tabuleiro[y1][x1];
            Peca destino_peca = tabuleiro[y2][x2];
            tabuleiro[y2][x2] = peca;
            tabuleiro[y1][x1] = null;
            peca.movimentos_realizados++;

            // Promoção de peão
            if (peca.tipo.equals("peao") && (y2 == 0 || y2 == 7)) {
                promocao_peao(x2, y2, peca.cor);
            }

            if (peca.tipo.equals("rei")) {
                roque_disponivel.get(peca.cor).put("roque_mais", false);
                roque_disponivel.get(peca.cor).put("roque_menos", false);
            }
            if (peca.tipo.equals("torre")) {
                if (x1 == 0) {
                    roque_disponivel.get(peca.cor).put("roque_menos", false);
                } else if (x1 == 7) {
                    roque_disponivel.get(peca.cor).put("roque_mais", false);
                }
            }

            String descricao;
            if (is_ai_move) {
                descricao = "IA move " + capitalize(peca.tipo) + " de (" + x1 + "," + y1 + ") para (" + x2 + "," + y2 + ")";
                if (eval_score != null) {
                    descricao += " | Eval: " + eval_score;
                }
                historico.add(new MovimentoHistorico("vermelho", descricao));
            } else {
                descricao = "Jogador move " + capitalize(peca.tipo) + " de (" + x1 + "," + y1 + ") para (" + x2 + "," + y2 + ")";
                historico.add(new MovimentoHistorico("azul", descricao));
            }
        }

        void promocao_peao(int x, int y, String cor) {
            String[] opcoes = {"R (Rainha)", "B (Bispo)", "C (Cavalo)", "T (Torre)"};
            String escolha = (String) JOptionPane.showInputDialog(null, 
                "Escolha a peça para promoção:", 
                "Promoção de Peão",
                JOptionPane.QUESTION_MESSAGE, 
                null, 
                opcoes, 
                opcoes[0]);
            if (escolha != null) {
                Peca novaPeca = null;
                if (escolha.startsWith("R")) {
                    novaPeca = new Peca("rainha", cor);
                } else if (escolha.startsWith("B")) {
                    novaPeca = new Peca("bispo", cor);
                } else if (escolha.startsWith("C")) {
                    novaPeca = new Peca("cavalo", cor);
                } else if (escolha.startsWith("T")) {
                    novaPeca = new Peca("torre", cor);
                }
                if (novaPeca != null) {
                    tabuleiro[y][x] = novaPeca;
                }
            }
        }

        boolean esta_em_xeque(String cor) {
            Point rei_pos = null;
            for (int y = 0; y < 8; y++) {
                for (int x = 0; x < 8; x++) {
                    Peca p = tabuleiro[y][x];
                    if (p != null && p.tipo.equals("rei") && p.cor.equals(cor)) {
                        rei_pos = new Point(x, y);
                        break;
                    }
                }
                if (rei_pos != null) break;
            }

            if (rei_pos == null) return false;

            String cor_oponente = cor.equals("azul") ? "vermelho" : "azul";
            for (int y = 0; y < 8; y++) {
                for (int x = 0; x < 8; x++) {
                    Peca p = tabuleiro[y][x];
                    if (p != null && p.cor.equals(cor_oponente)) {
                        List<Point> movimentos = p.movimentos_validos(x, y, tabuleiro, roque_disponivel);
                        for (Point mov : movimentos) {
                            if (mov.equals(rei_pos)) {
                                return true;
                            }
                        }
                    }
                }
            }
            return false;
        }

        boolean esta_em_xeque_mate(String cor) {
            if (!esta_em_xeque(cor)) return false;
            List<Movimento> movimentos = obter_movimentos_validos(cor);
            for (Movimento mv : movimentos) {
                Jogo copiaJogo = copia();
                copiaJogo.mover_peca(mv.origem, mv.destino);
                if (!copiaJogo.esta_em_xeque(cor)) {
                    return false;
                }
            }
            return true;
        }

        List<Movimento> obter_movimentos_validos(String cor) {
            List<Movimento> movimentos = new ArrayList<>();
            for (int y = 0; y < 8; y++) {
                for (int x = 0; x < 8; x++) {
                    Peca p = tabuleiro[y][x];
                    if (p != null && p.cor.equals(cor)) {
                        List<Point> mv = p.movimentos_validos(x, y, tabuleiro, roque_disponivel);
                        for (Point d : mv) {
                            movimentos.add(new Movimento(new Point(x,y), d));
                        }
                    }
                }
            }
            // Filtrar movimentos que deixam o rei em xeque
            List<Movimento> legais = new ArrayList<>();
            for (Movimento m : movimentos) {
                Jogo c = copia();
                c.mover_peca(m.origem, m.destino);
                if (!c.esta_em_xeque(cor)) {
                    legais.add(m);
                }
            }
            return legais;
        }

        int avaliar_tabuleiro() {
            int valor = 0;
            for (int y = 0; y < 8; y++) {
                for (int x = 0; x < 8; x++) {
                    Peca p = tabuleiro[y][x];
                    if (p != null) {
                        int val = VALOR_PECAS.getOrDefault(p.tipo, 0);
                        if (p.cor.equals("vermelho")) {
                            valor += val;
                        } else {
                            valor -= val;
                        }
                    }
                }
            }
            return valor;
        }

        Jogo copia() {
            Jogo novo = new Jogo();
            // limpar histórico e recriar estado
            novo.historico = new ArrayList<>(this.historico);
            for (int y=0; y<8; y++){
                for (int x=0; x<8; x++){
                    if (this.tabuleiro[y][x] != null) {
                        novo.tabuleiro[y][x] = this.tabuleiro[y][x].copia();
                    } else {
                        novo.tabuleiro[y][x] = null;
                    }
                }
            }
            novo.jogador_atual = this.jogador_atual;
            // Copiar disponibilidade de roque
            novo.roque_disponivel = new java.util.HashMap<>();
            for (String c : this.roque_disponivel.keySet()) {
                java.util.Map<String, Boolean> rd = new java.util.HashMap<>();
                rd.put("roque_menos", this.roque_disponivel.get(c).get("roque_menos"));
                rd.put("roque_mais", this.roque_disponivel.get(c).get("roque_mais"));
                novo.roque_disponivel.put(c, rd);
            }
            return novo;
        }

        MovimentoAval minimax(int profundidade, boolean maximizando, double alpha, double beta) {
            String cor = maximizando ? "vermelho" : "azul";
            if (profundidade == 0 || esta_em_xeque_mate("azul") || esta_em_xeque_mate("vermelho")) {
                return new MovimentoAval(avaliar_tabuleiro(), null);
            }

            List<Movimento> movimentos = obter_movimentos_validos(cor);
            if (movimentos.isEmpty()) {
                return new MovimentoAval(avaliar_tabuleiro(), null);
            }

            Movimento melhor = null;

            if (maximizando) {
                double maxEval = Double.NEGATIVE_INFINITY;
                for (Movimento mov : movimentos) {
                    Jogo copiaJ = copia();
                    copiaJ.mover_peca(mov.origem, mov.destino);
                    MovimentoAval eval_atual = copiaJ.minimax(profundidade - 1, false, alpha, beta);
                    if (eval_atual.valor > maxEval) {
                        maxEval = eval_atual.valor;
                        melhor = mov;
                    }
                    alpha = Math.max(alpha, eval_atual.valor);
                    if (beta <= alpha) {
                        break;
                    }
                }
                return new MovimentoAval(maxEval, melhor);
            } else {
                double minEval = Double.POSITIVE_INFINITY;
                for (Movimento mov : movimentos) {
                    Jogo copiaJ = copia();
                    copiaJ.mover_peca(mov.origem, mov.destino);
                    MovimentoAval eval_atual = copiaJ.minimax(profundidade - 1, true, alpha, beta);
                    if (eval_atual.valor < minEval) {
                        minEval = eval_atual.valor;
                        melhor = mov;
                    }
                    beta = Math.min(beta, eval_atual.valor);
                    if (beta <= alpha) {
                        break;
                    }
                }
                return new MovimentoAval(minEval, melhor);
            }
        }
    }

    // Classe para armazenar histórico
    static class MovimentoHistorico {
        String cor_jogador;
        String descricao;

        MovimentoHistorico(String cor_jogador, String descricao) {
            this.cor_jogador = cor_jogador;
            this.descricao = descricao;
        }
    }

    static class Movimento {
        Point origem;
        Point destino;
        Movimento(Point origem, Point destino) {
            this.origem = origem;
            this.destino = destino;
        }
    }

    static class MovimentoAval {
        double valor;
        Movimento movimento;
        MovimentoAval(double valor, Movimento movimento) {
            this.valor = valor;
            this.movimento = movimento;
        }
    }

    static String capitalize(String s) {
        if (s == null || s.isEmpty()) return s;
        return s.substring(0,1).toUpperCase() + s.substring(1);
    }

    // Painel do tabuleiro
    static class TabuleiroPanel extends JPanel {
        Jogo jogo;
        Point selecionado = null;
        List<Point> movimentos_legais = new ArrayList<>();
        Font fonte_pecas;
        Font fonte_info;
        Font fonte_legenda;
        boolean fim_de_jogo = false;

        TabuleiroPanel(Jogo jogo) {
            this.jogo = jogo;
            this.fonte_pecas = new Font("SansSerif", Font.PLAIN, TAMANHO_QUADRADO - 10);
            this.fonte_info = new Font("SansSerif", Font.PLAIN, 18);
            this.fonte_legenda = new Font("SansSerif", Font.PLAIN, 20);

            addMouseListener(new MouseAdapter() {
                @Override
                public void mouseClicked(MouseEvent e) {
                    if (fim_de_jogo) return;
                    int x = e.getX();
                    int y = e.getY();
                    if (x >= LARGURA_TABULEIRO || y >= ALTURA_TABULEIRO) {
                        return;
                    }
                    int cx = x / TAMANHO_QUADRADO;
                    int cy = y / TAMANHO_QUADRADO;

                    if (jogo.jogador_atual.equals("vermelho")) {
                        // Turno da IA
                        MovimentoAval bestMove = jogo.minimax(3, true, Double.NEGATIVE_INFINITY, Double.POSITIVE_INFINITY);
                        if (bestMove.movimento != null) {
                            jogo.mover_peca(bestMove.movimento.origem, bestMove.movimento.destino, true, bestMove.valor);
                        }
                        if (jogo.esta_em_xeque_mate("azul") || jogo.esta_em_xeque_mate("vermelho")) {
                            fim_de_jogo = true;
                        }
                        jogo.jogador_atual = "azul";
                        repaint();
                        return;
                    }

                    if (selecionado != null) {
                        // Tentando mover
                        Point destino = new Point(cx, cy);
                        if (movimentos_legais.contains(destino)) {
                            jogo.mover_peca(selecionado, destino);
                            if (jogo.esta_em_xeque_mate("vermelho")) {
                                fim_de_jogo = true;
                            }
                            jogo.jogador_atual = "vermelho";
                            selecionado = null;
                            movimentos_legais.clear();
                            repaint();
                            // Agora IA joga automaticamente
                            SwingUtilities.invokeLater(() -> {
                                if (!fim_de_jogo && jogo.jogador_atual.equals("vermelho")) {
                                    MovimentoAval bestMove = jogo.minimax(3, true, Double.NEGATIVE_INFINITY, Double.POSITIVE_INFINITY);
                                    if (bestMove.movimento != null) {
                                        jogo.mover_peca(bestMove.movimento.origem, bestMove.movimento.destino, true, bestMove.valor);
                                    }
                                    if (jogo.esta_em_xeque_mate("azul") || jogo.esta_em_xeque_mate("vermelho")) {
                                        fim_de_jogo = true;
                                    }
                                    jogo.jogador_atual = "azul";
                                    repaint();
                                }
                            });
                        } else {
                            selecionado = null;
                            movimentos_legais.clear();
                            repaint();
                        }
                    } else {
                        Peca p = jogo.tabuleiro[cy][cx];
                        if (p != null && p.cor.equals("azul")) {
                            List<Point> movs = p.movimentos_validos(cx, cy, jogo.tabuleiro, jogo.roque_disponivel);
                            // Filtrar movimentos que não deixam o rei em xeque
                            List<Point> legais = new ArrayList<>();
                            for (Point m : movs) {
                                Jogo copiaJ = jogo.copia();
                                copiaJ.mover_peca(new Point(cx,cy), m);
                                if (!copiaJ.esta_em_xeque("azul")) {
                                    legais.add(m);
                                }
                            }
                            if (!legais.isEmpty()) {
                                selecionado = new Point(cx,cy);
                                movimentos_legais = legais;
                                repaint();
                            }
                        }
                    }
                }
            });
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);

            // Desenhar tabuleiro
            for (int yy = 0; yy < 8; yy++) {
                for (int xx = 0; xx < 8; xx++) {
                    Color cor = ((xx + yy) % 2 == 0) ? BRANCO : CINZA;
                    g.setColor(cor);
                    g.fillRect(xx * TAMANHO_QUADRADO, yy * TAMANHO_QUADRADO, TAMANHO_QUADRADO, TAMANHO_QUADRADO);
                    Peca p = jogo.tabuleiro[yy][xx];
                    if (p != null) {
                        g.setColor(PRETO);
                        g.setFont(fonte_pecas);
                        FontMetrics fm = g.getFontMetrics();
                        int textWidth = fm.stringWidth(p.simbolo);
                        int textHeight = fm.getAscent();
                        int px = xx * TAMANHO_QUADRADO + (TAMANHO_QUADRADO - textWidth) / 2;
                        int py = yy * TAMANHO_QUADRADO + (TAMANHO_QUADRADO + textHeight) / 2 - 5;
                        g.drawString(p.simbolo, px, py);
                    }
                }
            }

            // Destacar peça selecionada e movimentos possíveis
            if (selecionado != null) {
                g.setColor(AMARELO);
                g.drawRect(selecionado.x*TAMANHO_QUADRADO, selecionado.y*TAMANHO_QUADRADO, TAMANHO_QUADRADO, TAMANHO_QUADRADO);
                g.setColor(VERDE);
                for (Point m : movimentos_legais) {
                    int cx = m.x*TAMANHO_QUADRADO + TAMANHO_QUADRADO/2;
                    int cy = m.y*TAMANHO_QUADRADO + TAMANHO_QUADRADO/2;
                    g.fillOval(cx-5, cy-5, 10, 10);
                }
            }

            // Desenhar área de informações
            g.setColor(PRETO);
            g.drawLine(LARGURA_TABULEIRO, 0, LARGURA_TABULEIRO, ALTURA_TABULEIRO);

            g.setFont(fonte_info);
            g.setColor(PRETO);
            g.drawString("Histórico de Movimentos:", LARGURA_TABULEIRO + 20, 30);

            int y_offset = 60;
            for (int i = Math.max(0, jogo.historico.size()-25); i < jogo.historico.size(); i++) {
                MovimentoHistorico mh = jogo.historico.get(i);
                g.setColor(mh.cor_jogador.equals("azul") ? AZUL : VERMELHO);
                // Dividir texto em múltiplas linhas se necessário
                List<String> linhas = dividirTexto(mh.descricao, 300, g.getFontMetrics());
                for (String linha : linhas) {
                    if (y_offset > ALTURA_TABULEIRO - 60) break;
                    g.drawString(linha, LARGURA_TABULEIRO + 20, y_offset);
                    y_offset += 20;
                }
            }

            // Legenda do autor em azul
            g.setColor(AZUL_LEGENDA);
            g.setFont(fonte_legenda);
            g.drawString("autor: Luiz Tiago Wilcke", LARGURA_TABULEIRO + 20, ALTURA_TABULEIRO - 20);

            if (fim_de_jogo) {
                g.setFont(new Font("SansSerif", Font.BOLD, 50));
                g.setColor(PRETO);
                FontMetrics fm = g.getFontMetrics();
                String txt = "Xeque-mate!";
                int tw = fm.stringWidth(txt);
                int th = fm.getAscent();
                int px = (LARGURA_TABULEIRO - tw)/2;
                int py = (ALTURA_TABULEIRO + th)/2;
                g.drawString(txt, px, py);
            }
        }

        private List<String> dividirTexto(String texto, int largura_max, FontMetrics fm) {
            List<String> linhas = new ArrayList<>();
            String[] palavras = texto.split(" ");
            String linha_atual = "";
            for (String palavra : palavras) {
                String teste = linha_atual + palavra + " ";
                int w = fm.stringWidth(teste);
                if (w < largura_max) {
                    linha_atual = teste;
                } else {
                    linhas.add(linha_atual);
                    linha_atual = palavra + " ";
                }
            }
            if (!linha_atual.isEmpty()) {
                linhas.add(linha_atual);
            }
            return linhas;
        }

        @Override
        public Dimension getPreferredSize() {
            return new Dimension(LARGURA_JANELA, ALTURA_JANELA);
        }
    }
}
