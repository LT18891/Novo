import javax.swing.*;
import java.awt.*;
import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;
import java.text.DecimalFormat;
import java.util.Random;

public class ModeloPrecoPetroleoSemBibliotecaExterna extends JFrame {

    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private JTextField campoPrecoInicial;
    private JTextField campoKappa;
    private JTextField campoTheta;
    private JTextField campoSigma;
    private JTextField campoTempoTotal;
    private JTextField campoPassos;
    private JTextField campoSimulacoes;
    private JLabel labelEquacao;

    private PainelGraficos painelGraficos;

    // Dados gerados pela simulação
    private double[] tempos;
    private double[] precoMedio;
    private double[] finais;

    public ModeloPrecoPetroleoSemBibliotecaExterna() {
        super("Modelo Preço do Petróleo (Equações Diferenciais) - Sem Lib. Externa");

        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1200, 800);
        setLocationRelativeTo(null);

        // Painel de entrada de dados
        JPanel panelInput = new JPanel(new GridLayout(8, 2));
        panelInput.setBorder(BorderFactory.createTitledBorder("Parâmetros do Modelo"));

        panelInput.add(new JLabel("Preço Inicial (P0):"));
        campoPrecoInicial = new JTextField("80.0");
        panelInput.add(campoPrecoInicial);

        panelInput.add(new JLabel("Taxa de Reversão (kappa):"));
        campoKappa = new JTextField("0.5");
        panelInput.add(campoKappa);

        panelInput.add(new JLabel("Média de Longo Prazo (theta):"));
        campoTheta = new JTextField("70.0");
        panelInput.add(campoTheta);

        panelInput.add(new JLabel("Volatilidade (sigma):"));
        campoSigma = new JTextField("0.2");
        panelInput.add(campoSigma);

        panelInput.add(new JLabel("Tempo Final (T em anos):"));
        campoTempoTotal = new JTextField("1.0");
        panelInput.add(campoTempoTotal);

        panelInput.add(new JLabel("Número de Passos (N):"));
        campoPassos = new JTextField("252");
        panelInput.add(campoPassos);

        panelInput.add(new JLabel("Número de Simulações (M):"));
        campoSimulacoes = new JTextField("10000");
        panelInput.add(campoSimulacoes);

        JButton botaoSimular = new JButton("Simular");
        panelInput.add(botaoSimular);

        labelEquacao = new JLabel("<html><center><h3>Equação do Modelo</h3>"
                + "<p>dP(t) = κ(θ - P(t)) dt + σ P(t) dW<sub>t</sub></p></center></html>",
                SwingConstants.CENTER);
        panelInput.add(labelEquacao);

        getContentPane().add(panelInput, BorderLayout.WEST);

        // Painel de gráficos
        painelGraficos = new PainelGraficos();
        painelGraficos.setBorder(BorderFactory.createTitledBorder("Resultados"));
        getContentPane().add(painelGraficos, BorderLayout.CENTER);

        botaoSimular.addActionListener(e -> {
            try {
                executarSimulacao();
                painelGraficos.setData(tempos, precoMedio, finais);
                painelGraficos.repaint();
            } catch (Exception ex) {
                ex.printStackTrace();
                JOptionPane.showMessageDialog(this, "Erro na simulação: " + ex.getMessage());
            }
        });
    }

    private void executarSimulacao() {
        // Obter parâmetros com alta precisão
        MathContext mc = new MathContext(25, RoundingMode.HALF_UP);

        BigDecimal P0 = new BigDecimal(campoPrecoInicial.getText(), mc);
        BigDecimal kappa = new BigDecimal(campoKappa.getText(), mc);
        BigDecimal theta = new BigDecimal(campoTheta.getText(), mc);
        BigDecimal sigma = new BigDecimal(campoSigma.getText(), mc);
        BigDecimal T = new BigDecimal(campoTempoTotal.getText(), mc);

        int N = Integer.parseInt(campoPassos.getText());
        int M = Integer.parseInt(campoSimulacoes.getText());

        // Delta t
        BigDecimal dt = T.divide(new BigDecimal(N, mc), mc);

        tempos = new double[N+1];
        for (int i = 0; i <= N; i++) {
            tempos[i] = i * dt.doubleValue();
        }

        finais = new double[M];
        Random rng = new Random();

        precoMedio = new double[N+1];
        for (int i = 0; i <= N; i++) {
            precoMedio[i] = 0.0;
        }

        for (int j = 0; j < M; j++) {
            BigDecimal P = P0;
            for (int i = 1; i <= N; i++) {
                double Z = rng.nextGaussian();
                // Euler-Maruyama
                BigDecimal diffDet = kappa.multiply(theta.subtract(P, mc), mc).multiply(dt, mc);
                BigDecimal diffEst = sigma.multiply(P, mc)
                        .multiply(new BigDecimal(Z * Math.sqrt(dt.doubleValue()), mc), mc);
                P = P.add(diffDet, mc).add(diffEst, mc);

                if (j == 0) {
                    precoMedio[i] = P.doubleValue();
                } else {
                    precoMedio[i] += P.doubleValue();
                }
            }
            finais[j] = P.doubleValue();
        }

        // Calcular média
        for (int i = 0; i <= N; i++) {
            precoMedio[i] = precoMedio[i] / M;
        }
    }

    // Painel customizado para plotagem
    static class PainelGraficos extends JPanel {
        private double[] tempos;
        private double[] precoMedio;
        private double[] finais;

        // Ajusta os dados para plotagem
        public void setData(double[] tempos, double[] precoMedio, double[] finais) {
            this.tempos = tempos;
            this.precoMedio = precoMedio;
            this.finais = finais;
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            if (tempos == null || precoMedio == null || finais == null) {
                return;
            }

            Graphics2D g2 = (Graphics2D) g;
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            int width = getWidth();
            int height = getHeight();

            int chartWidth = width / 2;
            int chartHeight = height - 50;

            g2.setFont(new Font("SansSerif", Font.PLAIN, 12));

            // Desenha dois gráficos lado a lado:
            // Esquerda: gráfico de linha (evolução média)
            // Direita: histograma (distribuição final)

            int padding = 60;
            int lineChartX = padding;
            int lineChartY = padding;
            int lineChartW = chartWidth - 2 * padding;
            int lineChartH = chartHeight - 2 * padding;

            // Determinar minY e maxY para o gráfico de linha
            double minY = Double.MAX_VALUE;
            double maxY = -Double.MAX_VALUE;
            for (double v : precoMedio) {
                if (v < minY) minY = v;
                if (v > maxY) maxY = v;
            }
            double marginY = (maxY - minY) * 0.1;
            maxY += marginY;
            minY -= marginY;

            // Desenha eixos do gráfico de linha
            g2.setColor(Color.BLACK);
            // eixo X
            g2.drawLine(lineChartX, lineChartY+lineChartH, lineChartX+lineChartW, lineChartY+lineChartH);
            // eixo Y
            g2.drawLine(lineChartX, lineChartY, lineChartX, lineChartY+lineChartH);

            // Título do gráfico de linha
            g2.drawString("Evolução Média do Preço do Petróleo", lineChartX, lineChartY - 20);

            // Marcas no eixo X (tempo)
            int numXTicks = 5; // por exemplo, 5 divisões
            for (int i = 0; i <= numXTicks; i++) {
                double tVal = tempos[tempos.length-1] * i / numXTicks;
                int xPos = lineChartX + (int)((tVal - tempos[0])/(tempos[tempos.length-1]-tempos[0]) * lineChartW);
                g2.drawLine(xPos, lineChartY+lineChartH, xPos, lineChartY+lineChartH+5);
                String label = String.format("%.2f a", tVal);
                int strWidth = g2.getFontMetrics().stringWidth(label);
                g2.drawString(label, xPos - strWidth/2, lineChartY+lineChartH+20);
            }

            // Marcas no eixo Y (preço)
            int numYTicks = 5;
            for (int i = 0; i <= numYTicks; i++) {
                double pVal = minY + (maxY - minY)*i/numYTicks;
                int yPos = lineChartY+lineChartH - (int)((pVal - minY)/(maxY-minY)*lineChartH);
                g2.drawLine(lineChartX-5, yPos, lineChartX, yPos);
                String label = String.format("$%.2f", pVal);
                int strWidth = g2.getFontMetrics().stringWidth(label);
                g2.drawString(label, lineChartX - strWidth - 10, yPos+5);
            }

            // Desenha a linha do preço médio
            g2.setColor(Color.BLUE);
            for (int i = 0; i < tempos.length - 1; i++) {
                int x1 = lineChartX + (int)(((tempos[i]-tempos[0])/(tempos[tempos.length-1]-tempos[0])) * lineChartW);
                int y1 = lineChartY+lineChartH - (int)(((precoMedio[i]-minY)/(maxY-minY)) * lineChartH);
                int x2 = lineChartX + (int)(((tempos[i+1]-tempos[0])/(tempos[tempos.length-1]-tempos[0])) * lineChartW);
                int y2 = lineChartY+lineChartH - (int)(((precoMedio[i+1]-minY)/(maxY-minY)) * lineChartH);
                g2.drawLine(x1, y1, x2, y2);
            }

            // Histograma à direita
            int histX = chartWidth + padding;
            int histY = padding;
            int histW = chartWidth - 2 * padding;
            int histH = chartHeight - 2 * padding;

            int bins = 50;
            double minVal = Double.MAX_VALUE;
            double maxVal = -Double.MAX_VALUE;
            for (double v : finais) {
                if (v < minVal) minVal = v;
                if (v > maxVal) maxVal = v;
            }
            double range = maxVal - minVal;
            double binSize = range / bins;
            int[] counts = new int[bins];
            for (double v : finais) {
                int bin = (int)((v - minVal) / binSize);
                if (bin >= bins) bin = bins - 1; // garantir não estourar
                counts[bin]++;
            }
            int maxCount = 0;
            for (int c : counts) {
                if (c > maxCount) maxCount = c;
            }

            // Eixos do histograma
            g2.setColor(Color.BLACK);
            g2.drawLine(histX, histY+histH, histX+histW, histY+histH); // X
            g2.drawLine(histX, histY, histX, histY+histH); // Y

            g2.drawString("Distribuição Final do Preço", histX, histY - 20);

            // Marcas no eixo X (preço final)
            int numXHistTicks = 5;
            for (int i = 0; i <= numXHistTicks; i++) {
                double val = minVal + i*(range/numXHistTicks);
                int xPos = histX + (int)((val - minVal)/range * histW);
                g2.drawLine(xPos, histY+histH, xPos, histY+histH+5);
                String label = String.format("$%.2f", val);
                int strWidth = g2.getFontMetrics().stringWidth(label);
                g2.drawString(label, xPos - strWidth/2, histY+histH+20);
            }

            // Marcas no eixo Y (frequência)
            int numYHistTicks = 5;
            for (int i = 0; i <= numYHistTicks; i++) {
                int cVal = (int)(maxCount*i/numYHistTicks);
                int yPos = histY+histH - (int)((cVal/(double)maxCount)*histH);
                g2.drawLine(histX-5, yPos, histX, yPos);
                String label = String.valueOf(cVal);
                int strWidth = g2.getFontMetrics().stringWidth(label);
                g2.drawString(label, histX - strWidth - 10, yPos+5);
            }

            // Desenha o histograma
            g2.setColor(new Color(200,50,50));
            for (int i = 0; i < bins; i++) {
                int barX = histX + (int)((double)i/(double)bins * histW);
                int barW = (int)( (1.0/bins) * histW );
                int barH = (int)((counts[i] / (double)maxCount) * histH);
                int barY = histY + histH - barH;
                g2.fillRect(barX, barY, barW, barH);
            }

        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            ModeloPrecoPetroleoSemBibliotecaExterna frame = new ModeloPrecoPetroleoSemBibliotecaExterna();
            frame.setVisible(true);
        });
    }
}
