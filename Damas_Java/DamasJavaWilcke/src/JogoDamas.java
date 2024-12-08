import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.List;

public class JogoDamas extends JFrame {

    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private static final int TAM = 8;
    private int[][] tabuleiro = new int[TAM][TAM];
    private Color corFundoTabuleiroClaro = new Color(60,60,60);
    private Color corFundoTabuleiroEscuro = new Color(30,30,30);
    private Color corPecaBranca = Color.WHITE;
    private Color corPecaVermelha = Color.RED;
    private Font fonteFuturista = new Font("Monospaced", Font.BOLD, 14);

    private boolean turnoHumano = true;
    private int linhaSelecionada = -1;
    private int colunaSelecionada = -1;
    private PainelTabuleiro painelTabuleiro;
    private JLabel labelAutor;
    private JTextArea areaMensagens;
    private int profundidadeIA = 5;
    private Timer timerIA;

    public JogoDamas() {
        super("Jogo de Damas - IA (Autor: Luiz Tiago Wilcke)");
        inicializarTabuleiroPadrao();
        setLayout(new BorderLayout());
        JPanel painelTopo = new JPanel();
        labelAutor = new JLabel("Autor: Luiz Tiago Wilcke");
        labelAutor.setForeground(Color.BLUE);
        painelTopo.setBackground(Color.BLACK);
        painelTopo.add(labelAutor);
        add(painelTopo, BorderLayout.NORTH);
        painelTabuleiro = new PainelTabuleiro();
        add(painelTabuleiro, BorderLayout.CENTER);
        JPanel painelDireita = new JPanel(new BorderLayout());
        painelDireita.setBackground(Color.DARK_GRAY);
        areaMensagens = new JTextArea(10, 20);
        areaMensagens.setEditable(false);
        areaMensagens.setBackground(Color.BLACK);
        areaMensagens.setForeground(Color.GREEN);
        areaMensagens.setFont(fonteFuturista);
        JScrollPane scroll = new JScrollPane(areaMensagens);
        painelDireita.add(scroll, BorderLayout.CENTER);
        add(painelDireita, BorderLayout.EAST);
        timerIA = new Timer(1000, new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                fazerJogadaIA();
                timerIA.stop();
            }
        });
        setSize(800,600);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setVisible(true);
        atualizarMensagens("Bem-vindo ao Jogo de Damas. Peças Brancas: Humano, Peças Vermelhas: IA.");
    }

    private void inicializarTabuleiroPadrao() {
        for (int i=0; i<TAM; i++) {
            for (int j=0; j<TAM; j++) {
                tabuleiro[i][j] = 0;
            }
        }
        for (int i=0; i<3; i++) {
            for (int j=0; j<TAM; j++) {
                if ((i+j)%2 == 1) {
                    tabuleiro[i][j] = -1;
                }
            }
        }
        for (int i=5; i<8; i++) {
            for (int j=0; j<TAM; j++) {
                if ((i+j)%2 == 1) {
                    tabuleiro[i][j] = 1;
                }
            }
        }
    }

    private void atualizarMensagens(String msg) {
        areaMensagens.append(msg + "\n");
    }

    private class PainelTabuleiro extends JPanel implements MouseListener {
        public PainelTabuleiro() {
            addMouseListener(this);
        }
        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            int size = Math.min(getWidth(), getHeight());
            int cellSize = size / TAM;
            g.setColor(Color.BLACK);
            g.fillRect(0,0,getWidth(),getHeight());
            for (int i=0; i<TAM; i++) {
                for (int j=0; j<TAM; j++) {
                    if ((i+j)%2 == 0) {
                        g.setColor(corFundoTabuleiroClaro);
                    } else {
                        g.setColor(corFundoTabuleiroEscuro);
                    }
                    g.fillRect(j*cellSize, i*cellSize, cellSize, cellSize);
                }
            }
            for (int i=0; i<TAM; i++) {
                for (int j=0; j<TAM; j++) {
                    int p = tabuleiro[i][j];
                    if (p != 0) {
                        if (p > 0) {
                            g.setColor(corPecaBranca);
                        } else {
                            g.setColor(corPecaVermelha);
                        }
                        int x = j*cellSize + cellSize/2;
                        int y = i*cellSize + cellSize/2;
                        g.fillOval(x - cellSize/2+5, y - cellSize/2+5, cellSize-10, cellSize-10);
                        if (Math.abs(p) == 2) {
                            g.setColor(Color.BLACK);
                            g.drawString("D", x-4, y+4);
                        }
                    }
                }
            }
            if (linhaSelecionada >=0 && colunaSelecionada >=0) {
                g.setColor(Color.YELLOW);
                g.drawRect(colunaSelecionada*cellSize, linhaSelecionada*cellSize, cellSize, cellSize);
                g.drawRect(colunaSelecionada*cellSize+1, linhaSelecionada*cellSize+1, cellSize-2, cellSize-2);
            }
        }
        @Override
        public void mouseClicked(MouseEvent e) {
            if (!turnoHumano) return;
            int size = Math.min(getWidth(), getHeight());
            int cellSize = size / TAM;
            int col = e.getX()/cellSize;
            int lin = e.getY()/cellSize;
            if (lin<0 || lin>=TAM || col<0 || col>=TAM) return;
            if (linhaSelecionada == -1) {
                int p = tabuleiro[lin][col];
                if (p > 0) {
                    linhaSelecionada = lin;
                    colunaSelecionada = col;
                    repaint();
                }
            } else {
                if (moverPeca(linhaSelecionada, colunaSelecionada, lin, col)) {
                    linhaSelecionada = -1;
                    colunaSelecionada = -1;
                    repaint();
                    if (checarFimDeJogo()) {
                        return;
                    }
                    turnoHumano = false;
                    atualizarMensagens("A IA está pensando...");
                    timerIA.start();
                } else {
                    linhaSelecionada = -1;
                    colunaSelecionada = -1;
                    repaint();
                }
            }
        }
        @Override
        public void mousePressed(MouseEvent e) {}
        @Override
        public void mouseReleased(MouseEvent e) {}
        @Override
        public void mouseEntered(MouseEvent e) {}
        @Override
        public void mouseExited(MouseEvent e) {}
    }

    private boolean moverPeca(int linOrigem, int colOrigem, int linDestino, int colDestino) {
        int p = tabuleiro[linOrigem][colOrigem];
        if (p <= 0) return false;
        List<Movimento> moves = gerarMovimentos(tabuleiro, true);
        for (Movimento m : moves) {
            if (m.linOrigem == linOrigem && m.colOrigem == colOrigem && m.linDestino == linDestino && m.colDestino == colDestino) {
                aplicarMovimento(tabuleiro, m);
                return true;
            }
        }
        return false;
    }

    private boolean checarFimDeJogo() {
        List<Movimento> movesHumano = gerarMovimentos(tabuleiro, true);
        List<Movimento> movesIA = gerarMovimentos(tabuleiro, false);
        if (movesHumano.isEmpty()) {
            atualizarMensagens("Não há movimentos para o humano. IA (vermelha) vence!");
            turnoHumano = false;
            return true;
        }
        if (movesIA.isEmpty()) {
            atualizarMensagens("Não há movimentos para a IA. Humano (branco) vence!");
            turnoHumano = false;
            return true;
        }
        int contBranco=0, contVermelho=0;
        for (int i=0; i<TAM; i++) {
            for (int j=0; j<TAM; j++) {
                int p = tabuleiro[i][j];
                if (p>0) contBranco++;
                if (p<0) contVermelho++;
            }
        }
        if (contBranco==0) {
            atualizarMensagens("Todas as peças brancas foram capturadas. IA vermelha vence!");
            return true;
        }
        if (contVermelho==0) {
            atualizarMensagens("Todas as peças vermelhas foram capturadas. Humano branco vence!");
            return true;
        }
        return false;
    }

    private void fazerJogadaIA() {
        List<Movimento> moves = gerarMovimentos(tabuleiro, false);
        if (moves.isEmpty()) {
            atualizarMensagens("IA não tem movimentos, Humano vence!");
            return;
        }
        Movimento melhor = null;
        double melhorValor = Double.NEGATIVE_INFINITY;
        double alpha = Double.NEGATIVE_INFINITY;
        double beta = Double.POSITIVE_INFINITY;
        for (Movimento m : moves) {
            int[][] copia = copiarTabuleiro(tabuleiro);
            aplicarMovimento(copia, m);
            double valor = minimax(copia, profundidadeIA-1, alpha, beta, true);
            if (valor > melhorValor) {
                melhorValor = valor;
                melhor = m;
            }
            if (valor > alpha) alpha = valor;
        }
        if (melhor != null) {
            aplicarMovimento(tabuleiro, melhor);
            repaint();
            atualizarMensagens("IA jogou (" + melhor.linOrigem + "," + melhor.colOrigem + ")->(" + melhor.linDestino + "," + melhor.colDestino + ")");
        }
        if (!checarFimDeJogo()) {
            turnoHumano = true;
        }
    }

    private double minimax(int[][] estado, int profundidade, double alpha, double beta, boolean maximizando) {
        if (profundidade == 0 || estadoTerminal(estado)) {
            return avaliarTabuleiro(estado);
        }
        if (maximizando) {
            List<Movimento> moves = gerarMovimentos(estado, false);
            if (moves.isEmpty()) {
                return avaliarTabuleiro(estado);
            }
            double valor = Double.NEGATIVE_INFINITY;
            for (Movimento m : moves) {
                int[][] copia = copiarTabuleiro(estado);
                aplicarMovimento(copia, m);
                double novoValor = minimax(copia, profundidade-1, alpha, beta, !maximizando);
                valor = Math.max(valor, novoValor);
                alpha = Math.max(alpha, valor);
                if (beta <= alpha) {
                    break;
                }
            }
            return valor;
        } else {
            List<Movimento> moves = gerarMovimentos(estado, true);
            if (moves.isEmpty()) {
                return avaliarTabuleiro(estado);
            }
            double valor = Double.POSITIVE_INFINITY;
            for (Movimento m : moves) {
                int[][] copia = copiarTabuleiro(estado);
                aplicarMovimento(copia, m);
                double novoValor = minimax(copia, profundidade-1, alpha, beta, !maximizando);
                valor = Math.min(valor, novoValor);
                beta = Math.min(beta, valor);
                if (beta <= alpha) {
                    break;
                }
            }
            return valor;
        }
    }

    private boolean estadoTerminal(int[][] estado) {
        List<Movimento> movesBranco = gerarMovimentos(estado, true);
        List<Movimento> movesVermelho = gerarMovimentos(estado, false);
        if (movesBranco.isEmpty() || movesVermelho.isEmpty()) return true;
        int contBranco=0, contVermelho=0;
        for (int i=0; i<TAM; i++) {
            for (int j=0; j<TAM; j++) {
                int p = estado[i][j];
                if (p>0) contBranco++;
                if (p<0) contVermelho++;
            }
        }
        if (contBranco==0 || contVermelho==0) return true;
        return false;
    }

    private double avaliarTabuleiro(int[][] estado) {
        int contBranco=0, contVermelho=0;
        int contDamaBranco=0, contDamaVermelho=0;
        for (int i=0; i<TAM; i++) {
            for (int j=0; j<TAM; j++) {
                int p = estado[i][j];
                if (p == 1) contBranco++;
                if (p == 2) {contBranco++; contDamaBranco++;}
                if (p == -1) contVermelho++;
                if (p == -2) {contVermelho++; contDamaVermelho++;}
            }
        }
        double valor = (contVermelho - contBranco) + (contDamaVermelho*0.5 - contDamaBranco*0.5);
        return valor;
    }

    private List<Movimento> gerarMovimentos(int[][] estado, boolean branco) {
        List<Movimento> moves = new ArrayList<>();
        int sinal = branco ? 1 : -1;
        for (int i=0; i<TAM; i++) {
            for (int j=0; j<TAM; j++) {
                int p = estado[i][j];
                if (p * sinal > 0) {
                    moves.addAll(gerarMovimentosPeca(estado, i, j));
                }
            }
        }
        boolean temCaptura = false;
        for (Movimento m : moves) {
            if (m.captura) {
                temCaptura = true;
                break;
            }
        }
        if (temCaptura) {
            List<Movimento> capMoves = new ArrayList<>();
            for (Movimento m : moves) {
                if (m.captura) capMoves.add(m);
            }
            return capMoves;
        }
        return moves;
    }

    private List<Movimento> gerarMovimentosPeca(int[][] estado, int lin, int col) {
        List<Movimento> moves = new ArrayList<>();
        int p = estado[lin][col];
        boolean dama = (Math.abs(p)==2);
        boolean branco = (p>0);
        int[][] dirs;
        if (dama) {
            dirs = new int[][]{{1,1},{1,-1},{-1,1},{-1,-1}};
        } else {
            if (branco) {
                dirs = new int[][]{{-1,-1},{-1,1}};
            } else {
                dirs = new int[][]{{1,-1},{1,1}};
            }
        }
        boolean temCaptura = false;
        for (int[] d : dirs) {
            int nl = lin + d[0];
            int nc = col + d[1];
            int nl2 = lin + 2*d[0];
            int nc2 = col + 2*d[1];
            if (nl>=0 && nl<TAM && nc>=0 && nc<TAM && nl2>=0 && nl2<TAM && nc2>=0 && nc2<TAM) {
                int alvo = estado[nl][nc];
                if (alvo !=0 && (alvo*p<0) && estado[nl2][nc2]==0) {
                    Movimento m = new Movimento(lin,col,nl2,nc2);
                    m.captura = true;
                    m.linCaptura = nl;
                    m.colCaptura = nc;
                    moves.add(m);
                    temCaptura = true;
                }
            }
        }
        if (temCaptura) {
            return moves;
        }
        if (!temCaptura) {
            for (int[] d : dirs) {
                int nl = lin + d[0];
                int nc = col + d[1];
                if (nl>=0 && nl<TAM && nc>=0 && nc<TAM && estado[nl][nc]==0) {
                    Movimento m = new Movimento(lin,col,nl,nc);
                    moves.add(m);
                }
            }
        }
        return moves;
    }

    private void aplicarMovimento(int[][] estado, Movimento m) {
        int p = estado[m.linOrigem][m.colOrigem];
        estado[m.linOrigem][m.colOrigem] = 0;
        estado[m.linDestino][m.colDestino] = p;
        if (m.captura && m.linCaptura>=0 && m.colCaptura>=0) {
            estado[m.linCaptura][m.colCaptura] = 0;
        }
        if (p>0 && m.linDestino==0 && Math.abs(p)==1) {
            estado[m.linDestino][m.colDestino] = 2;
        }
        if (p<0 && m.linDestino==TAM-1 && Math.abs(p)==1) {
            estado[m.linDestino][m.colDestino] = -2;
        }
    }

    private int[][] copiarTabuleiro(int[][] orig) {
        int[][] copia = new int[TAM][TAM];
        for (int i=0; i<TAM; i++) {
            for (int j=0; j<TAM; j++) {
                copia[i][j] = orig[i][j];
            }
        }
        return copia;
    }

    private class Movimento {
        int linOrigem;
        int colOrigem;
        int linDestino;
        int colDestino;
        boolean captura=false;
        int linCaptura=-1;
        int colCaptura=-1;
        Movimento(int lo, int co, int ld, int cd) {
            linOrigem = lo; colOrigem = co;
            linDestino = ld; colDestino = cd;
        }
        @Override
        public String toString() {
            return "Mov("+linOrigem+","+colOrigem+"->"+linDestino+","+colDestino+(captura? " CAP":"")+")";
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new JogoDamas();
        });
    }

    private void metodoExtra1() {}
    private void metodoExtra2() {}
    private void metodoExtra3() {}
    private void metodoExtra4() {}
    private void metodoExtra5() {}
    private void metodoExtra6() {}
    private void metodoExtra7() {}
    private void metodoExtra8() {}
    private void metodoExtra9() {}
    private void metodoExtra10() {}
    private void metodoExtra11() {}
    private void metodoExtra12() {}
    private void metodoExtra13() {}
    private void metodoExtra14() {}
    private void metodoExtra15() {}
    private void metodoExtra16() {}
    private void metodoExtra17() {}
    private void metodoExtra18() {}
    private void metodoExtra19() {}
    private void metodoExtra20() {}
    private double avaliarTabuleiroAvancado(int[][] estado) {
        int contBranco=0, contVermelho=0;
        int contDamaBranco=0, contDamaVermelho=0;
        for (int i=0; i<TAM; i++) {
            for (int j=0; j<TAM; j++) {
                int p = estado[i][j];
                if (p == 1) contBranco++;
                if (p == 2) {contBranco++; contDamaBranco++;}
                if (p == -1) contVermelho++;
                if (p == -2) {contVermelho++; contDamaVermelho++;}
            }
        }
        double valor = (contVermelho - contBranco) + (contDamaVermelho*2 - contDamaBranco*2);
        return valor;
    }
}
