import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.DecimalFormat;
import java.util.Random;

public class ModeloEstocasticoRealDolar extends JFrame {
    
    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	// Parâmetros do modelo (valores iniciais)
    private double mi = 0.02;      // µ: taxa de drift base
    private double gama = 0.01;    // γ: amplitude do termo sazonal
    private double sigma = 0.1;    // σ: volatilidade
    private double passo = 0.01;   // tamanho do passo de tempo (discretização)
    private int passosTotal = 1000; // número total de passos de tempo
    private double X0 = 5.0;       // valor inicial do câmbio

    // Vetor de tempos e valores
    private double[] tempos;
    private double[] valoresX;

    // Componentes da interface
    private JTextArea areaTexto;
    private PainelPlotagem painelPlot;

    // Campos de entrada para o usuário
    private JTextField campoMi, campoGama, campoSigma, campoPasso, campoPassosTotal, campoX0;

    public ModeloEstocasticoRealDolar() {
        super("Simulação Estocástica Real/Dólar");

        // Painel superior com campos de entrada
        JPanel painelControle = new JPanel(new FlowLayout(FlowLayout.LEFT));
        
        painelControle.add(new JLabel("µ:"));
        campoMi = new JTextField(Double.toString(mi), 5);
        painelControle.add(campoMi);

        painelControle.add(new JLabel("γ:"));
        campoGama = new JTextField(Double.toString(gama), 5);
        painelControle.add(campoGama);

        painelControle.add(new JLabel("σ:"));
        campoSigma = new JTextField(Double.toString(sigma), 5);
        painelControle.add(campoSigma);

        painelControle.add(new JLabel("Passo:"));
        campoPasso = new JTextField(Double.toString(passo), 5);
        painelControle.add(campoPasso);

        painelControle.add(new JLabel("Passos Totais:"));
        campoPassosTotal = new JTextField(Integer.toString(passosTotal), 5);
        painelControle.add(campoPassosTotal);

        painelControle.add(new JLabel("X0:"));
        campoX0 = new JTextField(Double.toString(X0), 5);
        painelControle.add(campoX0);

        JButton botaoRecalcular = new JButton("Recalcular");
        painelControle.add(botaoRecalcular);

        // Ação do botão recalcular
        botaoRecalcular.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                // Ler valores dos campos
                mi = Double.parseDouble(campoMi.getText());
                gama = Double.parseDouble(campoGama.getText());
                sigma = Double.parseDouble(campoSigma.getText());
                passo = Double.parseDouble(campoPasso.getText());
                passosTotal = Integer.parseInt(campoPassosTotal.getText());
                X0 = Double.parseDouble(campoX0.getText());

                // Re-simular e atualizar interface
                simular();
                painelPlot.setDados(valoresX, tempos);
                atualizarAreaTexto();
                painelPlot.repaint();
            }
        });

        // Gerar dados iniciais
        simular();

        // Configura layout da janela
        setLayout(new BorderLayout());
        add(painelControle, BorderLayout.NORTH);

        // Painel de plotagem
        painelPlot = new PainelPlotagem(valoresX, tempos);
        painelPlot.setPreferredSize(new Dimension(800, 600));
        add(painelPlot, BorderLayout.CENTER);

        // Área de texto para valores numéricos
        areaTexto = new JTextArea();
        areaTexto.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(areaTexto);
        scrollPane.setPreferredSize(new Dimension(300, 600));
        add(scrollPane, BorderLayout.EAST);

        atualizarAreaTexto();

        pack();
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setVisible(true);
    }

    private void simular() {
        valoresX = new double[passosTotal + 1];
        tempos = new double[passosTotal + 1];

        valoresX[0] = X0;
        tempos[0] = 0.0;

        Random rnd = new Random();

        // Método de Euler-Maruyama para SDE:
        // X_{n+1} = X_n + (µ + γ sin(t_n))*X_n*∆t + σ X_n √(∆t)*Z, onde Z ~ N(0,1)
        for (int i = 0; i < passosTotal; i++) {
            double t = tempos[i];
            double X = valoresX[i];
            
            double drift = (mi + gama * Math.sin(t)) * X; 
            double difusao = sigma * X;

            double dW = rnd.nextGaussian() * Math.sqrt(passo);
            double X_prox = X + drift * passo + difusao * dW;

            tempos[i+1] = t + passo;
            valoresX[i+1] = X_prox;
        }
    }

    private void atualizarAreaTexto() {
        DecimalFormat df = new DecimalFormat("#.####################"); // até 20 dígitos decimais
        StringBuilder sb = new StringBuilder();
        sb.append("Valores Simulados (20 dígitos de precisão):\n");
        for (int i = 0; i < valoresX.length; i++) {
            sb.append("t=").append(df.format(tempos[i])).append("  X=").append(df.format(valoresX[i])).append("\n");
        }
        areaTexto.setText(sb.toString());
    }

    // Painel personalizado para plotar o gráfico e desenhar a equação
    class PainelPlotagem extends JPanel {
        private double[] valores;
        private double[] t;
        
        public PainelPlotagem(double[] valores, double[] t) {
            this.valores = valores;
            this.t = t;
            setBackground(Color.WHITE);
        }

        public void setDados(double[] valores, double[] t) {
            this.valores = valores;
            this.t = t;
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            
            if (valores == null || valores.length == 0) {
                return;
            }

            // Margens
            int margemEsq = 50;
            int margemDir = 20;
            int margemSup = 60;
            int margemInf = 50;

            int largura = getWidth();
            int altura = getHeight();

            // Encontrar min e max dos dados
            double minX = Double.MAX_VALUE;
            double maxX = Double.MIN_VALUE;
            double minT = t[0];
            double maxT = t[t.length - 1];

            for (double val : valores) {
                if (val < minX) minX = val;
                if (val > maxX) maxX = val;
            }

            // Escalas
            double escalaX = (largura - margemEsq - margemDir) / (maxT - minT);
            double escalaY = (altura - margemSup - margemInf) / (maxX - minX);

            // Eixos
            g.setColor(Color.BLACK);
            // Eixo x
            g.drawLine(margemEsq, altura - margemInf, largura - margemDir, altura - margemInf);
            // Eixo y
            g.drawLine(margemEsq, margemSup, margemEsq, altura - margemInf);

            // Desenhar valores no eixo Y (algumas marcas)
            g.setColor(Color.GRAY);
            int numMarcasY = 5;
            for (int i = 0; i <= numMarcasY; i++) {
                double yVal = minX + i * (maxX - minX) / numMarcasY;
                int yPix = (int) (altura - margemInf - (yVal - minX) * escalaY);
                g.drawLine(margemEsq - 5, yPix, margemEsq, yPix);
                g.drawString(String.format("%.2f", yVal), margemEsq - 45, yPix + 5);
            }

            // Desenhar valores no eixo X (algumas marcas)
            int numMarcasX = 5;
            for (int i = 0; i <= numMarcasX; i++) {
                double tVal = minT + i * (maxT - minT) / numMarcasX;
                int xPix = (int) (margemEsq + (tVal - minT) * escalaX);
                g.drawLine(xPix, altura - margemInf, xPix, altura - margemInf + 5);
                g.drawString(String.format("%.2f", tVal), xPix - 10, altura - margemInf + 20);
            }

            // Plotar a trajetória
            g.setColor(Color.BLUE);
            for (int i = 0; i < valores.length - 1; i++) {
                int x1 = (int) (margemEsq + (t[i] - minT) * escalaX);
                int y1 = (int) (altura - margemInf - (valores[i] - minX) * escalaY);
                int x2 = (int) (margemEsq + (t[i+1] - minT) * escalaX);
                int y2 = (int) (altura - margemInf - (valores[i+1] - minX) * escalaY);
                g.drawLine(x1, y1, x2, y2);
            }

            // Desenhar a equação
            g.setColor(Color.BLACK);
            Font fonteOriginal = g.getFont();
            Font fonteEquacao = fonteOriginal.deriveFont(Font.ITALIC, 16f);
            g.setFont(fonteEquacao);

            // Equação: dX(t) = (µ + γ sin(t)) X(t) dt + σ X(t) dW(t)
            String eq = "dX(t) = [ (µ + γ sin(t)) X(t) ] dt + σ X(t) dW(t)";
            FontMetrics fm = g.getFontMetrics();
            int eqWidth = fm.stringWidth(eq);
            g.drawString(eq, (largura - eqWidth)/2, margemSup - 30);

            // Voltar para a fonte original
            g.setFont(fonteOriginal);

            // Título e legendas
            g.drawString("Simulação do câmbio Real/Dólar (SDE)", largura/2 - 100, margemSup - 10);
            g.drawString("Tempo (t)", largura/2 - 20, altura - 10);

            // Rotação do texto do eixo Y
            Graphics2D g2 = (Graphics2D) g;
            g2.rotate(-Math.PI/2);
            g2.drawString("Valor de X(t) (R$/US$)", -altura/2 - 40, margemEsq - 30);
            g2.rotate(Math.PI/2);
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new ModeloEstocasticoRealDolar());
    }
}
