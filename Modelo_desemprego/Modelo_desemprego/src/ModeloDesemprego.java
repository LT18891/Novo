import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.text.DecimalFormat;
import java.util.Random;

public class ModeloDesemprego extends JFrame {

    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private JTextField alphaField;
    private JTextField betaField;
    private JTextField sigmaField;
    private JTextField tempoFinalField;
    private JTextField passosEspaciaisField;
    private JTextField passosTemporaisField;

    private JButton calcularButton;
    private PlotPanel plotPanel;

    private double[] ultimaSolucao;
    private double alpha, beta, sigma;
    private double T;
    private int N, M;

    public ModeloDesemprego() {
        super("Modelo Probabilístico - Taxa de Desemprego");

        // Painel superior com a equação e o autor
        JPanel topoPanel = new JPanel(new BorderLayout());
        JLabel autorLabel = new JLabel("<html><span style='color:blue'>Autor: Luiz Tiago Wilcke</span></html>", SwingConstants.CENTER);
        topoPanel.add(autorLabel, BorderLayout.NORTH);

        JLabel eqLabel = new JLabel("<html><center>Equação Diferencial Probabilística:<br>"
                + "∂u/∂t = α ∂²u/∂x² - β u(t,x) + σ ξ(t,x)</center></html>", SwingConstants.CENTER);
        topoPanel.add(eqLabel, BorderLayout.CENTER);

        add(topoPanel, BorderLayout.NORTH);

        // Painel central com campos de entrada
        JPanel inputPanel = new JPanel(new GridLayout(7, 2, 5, 5));
        inputPanel.setBorder(BorderFactory.createTitledBorder("Parâmetros"));

        inputPanel.add(new JLabel("Alpha (α):"));
        alphaField = new JTextField("0.1");
        inputPanel.add(alphaField);

        inputPanel.add(new JLabel("Beta (β):"));
        betaField = new JTextField("0.05");
        inputPanel.add(betaField);

        inputPanel.add(new JLabel("Sigma (σ):"));
        sigmaField = new JTextField("0.1");
        inputPanel.add(sigmaField);

        inputPanel.add(new JLabel("Tempo final (T):"));
        tempoFinalField = new JTextField("1.0");
        inputPanel.add(tempoFinalField);

        inputPanel.add(new JLabel("Passos espaciais (N):"));
        passosEspaciaisField = new JTextField("100");
        inputPanel.add(passosEspaciaisField);

        inputPanel.add(new JLabel("Passos temporais (M):"));
        passosTemporaisField = new JTextField("100");
        inputPanel.add(passosTemporaisField);

        calcularButton = new JButton("Calcular");
        inputPanel.add(new JLabel(""));
        inputPanel.add(calcularButton);

        add(inputPanel, BorderLayout.WEST);

        // Painel de plotagem
        plotPanel = new PlotPanel();
        plotPanel.setPreferredSize(new Dimension(600, 400));
        add(plotPanel, BorderLayout.CENTER);

        // Ação do botão Calcular
        calcularButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                calcularSolucao();
            }
        });

        pack();
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    }

    private void calcularSolucao() {
        try {
            alpha = Double.parseDouble(alphaField.getText());
            beta = Double.parseDouble(betaField.getText());
            sigma = Double.parseDouble(sigmaField.getText());
            T = Double.parseDouble(tempoFinalField.getText());
            N = Integer.parseInt(passosEspaciaisField.getText());
            M = Integer.parseInt(passosTemporaisField.getText());

            // Parâmetros do esquema numérico
            double L = 1.0; // comprimento espacial (fixo, apenas exemplo)
            double dx = L / (N - 1);
            double dt = T / M;

            double[] u = new double[N];
            double[] uNew = new double[N];

            // Condição inicial: supondamos u(x,0) = exp(-10*(x-0.5)^2), apenas exemplo
            for (int i = 0; i < N; i++) {
                double x = i * dx;
                u[i] = Math.exp(-10.0 * (x - 0.5) * (x - 0.5));
            }

            // Ruído
            Random rand = new Random();

            // Solver simples (Euler explícito + aproximação do ruído)
            // du/dt = α d²u/dx² - β u + σ ξ
            // Discretização:
            // u^{n+1}_i = u^n_i + dt [ α (u^n_{i+1} - 2u^n_i + u^n_{i-1})/dx² - β u^n_i + σ * W ]
            // W ~ Normal(0,1/dt) para simular ruído branco aproximado (não rigoroso, apenas ilustrativo)
            
            for (int n = 0; n < M; n++) {
                for (int i = 1; i < N - 1; i++) {
                    double lap = (u[i+1] - 2*u[i] + u[i-1]) / (dx*dx);
                    double noise = sigma * rand.nextGaussian() / Math.sqrt(dt);
                    uNew[i] = u[i] + dt*(alpha*lap - beta*u[i]) + dt*noise;
                }

                // Condições de fronteira (Dirichlet simples: u=0 nas pontas)
                uNew[0] = 0.0;
                uNew[N-1] = 0.0;

                // Troca
                double[] temp = u;
                u = uNew;
                uNew = temp;
            }

            ultimaSolucao = u;
            plotPanel.setData(u);

            // Imprime resultado no console com 8 digitos de precisão
            DecimalFormat df = new DecimalFormat("#.########");
            System.out.println("Resultado Final (u(t_final,x)):");
            for (int i = 0; i < N; i++) {
                System.out.println("x=" + df.format(i*dx) + " : " + df.format(u[i]));
            }

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Erro nos parâmetros: " + ex.getMessage());
        }
    }

    // Painel para plotar a solução final
    class PlotPanel extends JPanel {
        private double[] data;

        public void setData(double[] d) {
            this.data = d;
            repaint();
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            if (data == null || data.length == 0) return;

            int w = getWidth();
            int h = getHeight();

            double max = Double.NEGATIVE_INFINITY;
            double min = Double.POSITIVE_INFINITY;
            for (double v : data) {
                if (v > max) max = v;
                if (v < min) min = v;
            }

            // Evita problema se todos forem iguais
            if (max == min) {
                max = min + 1e-6;
            }

            // Plotar linha
            int len = data.length;
            int margin = 40;
            int plotW = w - 2*margin;
            int plotH = h - 2*margin;

            g.setColor(Color.BLACK);
            g.drawRect(margin, margin, plotW, plotH);

            g.drawString("u(t_final,x)", margin + 5, margin - 10);

            for (int i = 0; i < len - 1; i++) {
                int x1 = margin + (int)((double)i/(len-1)*plotW);
                int x2 = margin + (int)((double)(i+1)/(len-1)*plotW);
                int y1 = margin + plotH - (int)((data[i]-min)/(max-min)*plotH);
                int y2 = margin + plotH - (int)((data[i+1]-min)/(max-min)*plotH);

                g.setColor(Color.RED);
                g.drawLine(x1, y1, x2, y2);
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new ModeloDesemprego().setVisible(true);
        });
    }
}
