import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;

public class DistribuicaoNormalPlotSemJFree extends JFrame {

    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	// Campos de entrada
    private JTextField campoMedia;
    private JTextField campoDesvio;
    private JTextField campoMinX;
    private JTextField campoMaxX;
    private JTextField campoPasso;

    // Painel para a fórmula
    private JEditorPane painelFormula;

    // Painel do gráfico
    private GraficoPanel painelGrafico;

    // Contexto matemático para precisão de 20 dígitos
    private static final MathContext MC = new MathContext(20, RoundingMode.HALF_UP);

    public DistribuicaoNormalPlotSemJFree() {
        super("Distribuição Normal - Plotagem");

        // Painel superior com parâmetros
        JPanel painelParametros = new JPanel(new GridLayout(2, 5, 5, 5));
        painelParametros.setBorder(BorderFactory.createTitledBorder("Parâmetros da Distribuição Normal"));

        painelParametros.add(new JLabel("Média (μ):"));
        campoMedia = new JTextField("0");
        painelParametros.add(campoMedia);

        painelParametros.add(new JLabel("Desvio (σ):"));
        campoDesvio = new JTextField("1");
        painelParametros.add(campoDesvio);

        painelParametros.add(new JLabel("x mínimo:"));
        campoMinX = new JTextField("-5");
        painelParametros.add(campoMinX);

        painelParametros.add(new JLabel("x máximo:"));
        campoMaxX = new JTextField("5");
        painelParametros.add(campoMaxX);

        painelParametros.add(new JLabel("Passo:"));
        campoPasso = new JTextField("0.1");
        painelParametros.add(campoPasso);

        // Botão para calcular e plotar
        JButton botaoCalcular = new JButton("Calcular e Plotar");
        botaoCalcular.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                plotarDistribuicao();
            }
        });

        // Painel para a fórmula
        painelFormula = new JEditorPane();
        painelFormula.setContentType("text/html");
        painelFormula.setEditable(false);

        // Fórmula da distribuição normal (renderizada via imagem LaTeX)
        String formulaURL = "https://latex.codecogs.com/png.latex?\\large f(x)=\\frac{1}{\\sigma\\sqrt{2\\pi}}e^{-(x-\\mu)^{2}/(2\\sigma^{2})}";
        String html = "<html><div style='text-align:center;'><img src=\"" + formulaURL + "\" alt=\"Fórmula da Normal\"></div></html>";
        painelFormula.setText(html);

        // Painel do gráfico
        painelGrafico = new GraficoPanel();

        // Legenda com autor em azul
        JLabel legenda = new JLabel("autor: Luiz Tiago Wilcke", SwingConstants.RIGHT);
        legenda.setForeground(Color.BLUE);

        // Layout principal
        JPanel painelTop = new JPanel(new BorderLayout());
        painelTop.add(painelParametros, BorderLayout.CENTER);
        painelTop.add(botaoCalcular, BorderLayout.EAST);

        getContentPane().setLayout(new BorderLayout());
        getContentPane().add(painelTop, BorderLayout.NORTH);
        getContentPane().add(painelFormula, BorderLayout.SOUTH);
        getContentPane().add(painelGrafico, BorderLayout.CENTER);
        getContentPane().add(legenda, BorderLayout.PAGE_END);

        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
    }

    private void plotarDistribuicao() {
        try {
            BigDecimal media = new BigDecimal(campoMedia.getText().trim());
            BigDecimal desvio = new BigDecimal(campoDesvio.getText().trim());
            BigDecimal minX = new BigDecimal(campoMinX.getText().trim());
            BigDecimal maxX = new BigDecimal(campoMaxX.getText().trim());
            BigDecimal passo = new BigDecimal(campoPasso.getText().trim());

            // Verifica se desvio > 0
            if (desvio.compareTo(BigDecimal.ZERO) <= 0) {
                JOptionPane.showMessageDialog(this, "O desvio-padrão deve ser maior que 0.", "Erro", JOptionPane.ERROR_MESSAGE);
                return;
            }

            // Gera os pontos
            int n = (int) ((maxX.subtract(minX)).divide(passo, MC).doubleValue()) + 1;
            double[] xs = new double[n];
            double[] ys = new double[n];

            BigDecimal x = minX;
            for (int i = 0; i < n; i++) {
                BigDecimal yBD = densidadeNormal(x, media, desvio);
                xs[i] = x.doubleValue();
                ys[i] = yBD.doubleValue();
                x = x.add(passo, MC);
            }

            painelGrafico.setData(xs, ys);
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Entradas inválidas.", "Erro", JOptionPane.ERROR_MESSAGE);
        }
    }

    // Função densidade de probabilidade da Normal
    private BigDecimal densidadeNormal(BigDecimal x, BigDecimal mu, BigDecimal sigma) {
        // f(x) = 1/(sigma*sqrt(2*pi)) * exp(-((x - mu)^2)/(2*sigma^2))
        BigDecimal two = new BigDecimal("2");
        BigDecimal pi = pi(MC);
        BigDecimal diff = x.subtract(mu, MC);

        BigDecimal sigmaSquared = sigma.multiply(sigma, MC);
        BigDecimal exponent = diff.multiply(diff, MC).divide(two.multiply(sigmaSquared, MC), MC).negate();

        BigDecimal denom = sigma.multiply(sqrt(two.multiply(pi, MC)), MC);
        BigDecimal factor = BigDecimal.ONE.divide(denom, MC);

        BigDecimal result = factor.multiply(exp(exponent), MC);
        return result;
    }

    // Aproximação de pi usando uma constante (para 20 dígitos é suficiente)
    private static BigDecimal pi(MathContext mc) {
        // Valor de pi com 30 dígitos, por segurança
        return new BigDecimal("3.141592653589793238462643383279").round(mc);
    }

    // Cálculo de sqrt de BigDecimal (Newton-Raphson)
    private static BigDecimal sqrt(BigDecimal A) {
        return sqrt(A, MC);
    }

    private static BigDecimal sqrt(BigDecimal A, MathContext mc) {
        if (A.compareTo(BigDecimal.ZERO) < 0) {
            throw new ArithmeticException("Abaixo de zero");
        }
        if (A.compareTo(BigDecimal.ZERO) == 0) {
            return BigDecimal.ZERO;
        }

        BigDecimal x0 = BigDecimal.ZERO;
        BigDecimal x1 = A;
        // Newton-Raphson
        while (true) {
            x0 = x1;
            x1 = x0.subtract(x0.multiply(x0, mc).subtract(A, mc).divide(x0.multiply(new BigDecimal("2"), mc), mc), mc);
            if (x0.subtract(x1, mc).abs().compareTo(new BigDecimal("1e-19")) < 0) {
                return x1.round(mc);
            }
        }
    }

    // Exponencial de BigDecimal (aproximação)
    // Aqui podemos usar uma série de Taylor ou outra aproximação.
    // Série de Taylor: exp(x) = sum_{n=0}^∞ x^n / n!
    // Para 20 dígitos de precisão, vamos usar umas 50 iterações, dependendo do tamanho de x.
    private static BigDecimal exp(BigDecimal x) {
        return exp(x, MC);
    }

    private static BigDecimal exp(BigDecimal x, MathContext mc) {
        BigDecimal sum = BigDecimal.ONE;
        BigDecimal term = BigDecimal.ONE;
        BigDecimal n = BigDecimal.ONE;
        BigDecimal limit = new BigDecimal("1e-25");
        int i = 1;
        while (true) {
            term = term.multiply(x, mc).divide(n, mc);
            if (term.abs().compareTo(limit) < 0 || i > 200) {
                break;
            }
            sum = sum.add(term, mc);
            n = n.add(BigDecimal.ONE);
            i++;
        }
        return sum.round(mc);
    }

    // Painel gráfico customizado
    class GraficoPanel extends JPanel {
        private double[] xs;
        private double[] ys;

        public void setData(double[] xs, double[] ys) {
            this.xs = xs;
            this.ys = ys;
            repaint();
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            if (xs == null || ys == null || xs.length == 0) {
                return;
            }

            Graphics2D g2 = (Graphics2D) g.create();
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            int w = getWidth();
            int h = getHeight();

            // Encontra min e max de X e Y
            double minX = xs[0];
            double maxX = xs[xs.length - 1];
            double minY = 0; // A PDF da normal >= 0 sempre
            double maxY = 0;
            for (double y : ys) {
                if (y > maxY) maxY = y;
            }

            // Margens
            int margin = 40;

            // Mapeia para coordenadas de tela
            // xTela = margin + ( (x - minX)/(maxX-minX) )*(w - 2*margin)
            // yTela = h - margin - ( (y - minY)/(maxY-minY) )*(h-2*margin)
            // maxY pode ser 0 se degenerate, mas dificilmente será. Se sigma > 0, normal é bem definida.
            if (maxY <= 0) {
                maxY = 1; // Evitar divisão por zero
            }

            // Desenha eixos
            g2.setColor(Color.BLACK);
            // Eixo X
            int xEixoY = h - margin; 
            g2.drawLine(margin, xEixoY, w - margin, xEixoY);

            // Eixo Y
            g2.drawLine(margin, margin, margin, h - margin);

            // Plot da função
            g2.setColor(Color.RED);
            for (int i = 0; i < xs.length - 1; i++) {
                int x1 = (int) (margin + ((xs[i] - minX) / (maxX - minX)) * (w - 2 * margin));
                int y1 = (int) (h - margin - ((ys[i] - minY) / (maxY - minY)) * (h - 2 * margin));

                int x2 = (int) (margin + ((xs[i + 1] - minX) / (maxX - minX)) * (w - 2 * margin));
                int y2 = (int) (h - margin - ((ys[i + 1] - minY) / (maxY - minY)) * (h - 2 * margin));

                g2.drawLine(x1, y1, x2, y2);
            }

            // Opcional: desenhar alguns valores de referência no eixo X
            g2.setColor(Color.BLACK);
            // Marcas no eixo X (colocar algumas)
            for (int i = 0; i <= 5; i++) {
                double xv = minX + i * (maxX - minX) / 5.0;
                int xp = (int) (margin + ((xv - minX) / (maxX - minX)) * (w - 2 * margin));
                g2.drawLine(xp, xEixoY - 5, xp, xEixoY + 5);
                g2.drawString(String.format("%.2f", xv), xp - 10, xEixoY + 20);
            }

            // Marcas no eixo Y (colocar algumas)
            for (int i = 0; i <= 5; i++) {
                double yv = minY + i * (maxY - minY) / 5.0;
                int yp = (int) (h - margin - ((yv - minY) / (maxY - minY)) * (h - 2 * margin));
                g2.drawLine(margin - 5, yp, margin + 5, yp);
                g2.drawString(String.format("%.2e", yv), margin - 60, yp + 5);
            }

            g2.dispose();
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new DistribuicaoNormalPlotSemJFree().setVisible(true);
        });
    }
}
