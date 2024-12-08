import java.awt.*;
import java.awt.event.*;
import java.text.DecimalFormat;
import javax.swing.*;

public class SimulacaoFotovoltaica extends JFrame {

    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private JTextField campoNumPontos;
    private JTextField campoComprimento;
    private JTextField campoMassa;
    private JTextField campoV0;
    private JButton botaoCalcular;
    private JTextArea areaExplicacoes;
    private JPanel painelPlotagem;
    private JList<String> listaResultados;
    private JComboBox<String> comboPotencial;

    private double[] autovalores;
    private double[][] autovetores;
    private double[] eixoX;
    private double[] potencial; // Armazena V(x)

    public SimulacaoFotovoltaica() {
        super("Simulação Fotovoltaica com Equação de Schrödinger");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1200, 800);
        setLayout(new BorderLayout());

        // Painel de parâmetros superiores
        JPanel painelParametros = new JPanel(new FlowLayout());

        painelParametros.add(new JLabel("Número de pontos (N):"));
        campoNumPontos = new JTextField("200", 5);
        painelParametros.add(campoNumPontos);

        painelParametros.add(new JLabel("Comprimento (L):"));
        campoComprimento = new JTextField("1.0", 5);
        painelParametros.add(campoComprimento);

        painelParametros.add(new JLabel("Massa (m):"));
        campoMassa = new JTextField("1.0", 5);
        painelParametros.add(campoMassa);

        painelParametros.add(new JLabel("Tipo de Potencial:"));
        comboPotencial = new JComboBox<>(new String[]{"Poço Infinito", "Barreira Central"});
        painelParametros.add(comboPotencial);

        painelParametros.add(new JLabel("V0 (para barreira):"));
        campoV0 = new JTextField("50.0", 5);
        painelParametros.add(campoV0);

        botaoCalcular = new JButton("Calcular");
        painelParametros.add(botaoCalcular);

        add(painelParametros, BorderLayout.NORTH);

        JSplitPane splitCentral = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);

        JPanel painelEsquerda = new JPanel(new BorderLayout());

        JLabel labelEquacao = new JLabel("<html><center>Equação de Schrödinger Unidimensional:<br>"
                + "-(ℏ²/(2m)) (d²ψ/dx²) + V(x) ψ = E ψ</center></html>");
        labelEquacao.setHorizontalAlignment(SwingConstants.CENTER);

        painelEsquerda.add(labelEquacao, BorderLayout.NORTH);

        areaExplicacoes = new JTextArea();
        areaExplicacoes.setEditable(false);
        areaExplicacoes.setText(
                "Explicação:\n"
                + "Este programa resolve a equação de Schrödinger independente do tempo para diferentes potenciais.\n"
                + "Assume-se h_bar=1, massa m, e discretização do espaço com N pontos.\n\n"
                + "Potenciais Disponíveis:\n"
                + "1) Poço Infinito: V(x)=0 no interior e fronteiras infinitas forçando ψ=0 nas bordas.\n"
                + "2) Barreira Central: Uma barreira de altura V0 no centro do domínio.\n\n"
                + "Isto pode representar, de forma simplificada, situações encontradas em estruturas fotovoltaicas,\n"
                + "onde potenciais efetivos confinam ou separam portadores. Os autovalores encontrados correspondem\n"
                + "a níveis de energia quantizados.\n\n"
                + "Após o cálculo, as energias são listadas. As autofunções correspondentes aos primeiros modos\n"
                + "e o potencial V(x) são plotados no painel à direita.\n"
        );
        JScrollPane scrollExplicacoes = new JScrollPane(areaExplicacoes);
        painelEsquerda.add(scrollExplicacoes, BorderLayout.CENTER);

        listaResultados = new JList<>();
        painelEsquerda.add(new JScrollPane(listaResultados), BorderLayout.SOUTH);

        splitCentral.setLeftComponent(painelEsquerda);

        painelPlotagem = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                if (autovetores != null && eixoX != null && potencial != null) {
                    Graphics2D g2 = (Graphics2D) g;
                    g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

                    int w = getWidth();
                    int h = getHeight();

                    int modosPlotar = Math.min(3, autovetores[0].length);

                    // Determina min e max para função de onda
                    double minY = Double.MAX_VALUE;
                    double maxY = -Double.MAX_VALUE;
                    for (int m = 0; m < modosPlotar; m++) {
                        for (int i = 0; i < eixoX.length; i++) {
                            double val = autovetores[i][m];
                            if (val < minY) minY = val;
                            if (val > maxY) maxY = val;
                        }
                    }

                    // Também considerar o potencial para ajustar o gráfico
                    double minV = Double.MAX_VALUE;
                    double maxV = -Double.MAX_VALUE;
                    for (int i=0; i<eixoX.length; i++){
                        if (potencial[i]<minV) minV=potencial[i];
                        if (potencial[i]>maxV) maxV=potencial[i];
                    }

                    // Ajustar a escala para mostrar potencial e autofunções juntos
                    // Uma forma simples: Normalizamos o potencial para caber no mesmo range do gráfico de ψ
                    double rangeYFunc = maxY - minY;
                    if (rangeYFunc < 1e-15) rangeYFunc = 1.0; 
                    double rangeX = eixoX[eixoX.length - 1] - eixoX[0];

                    // Normalizar o potencial para ficar no mesmo nível da função de onda (por exemplo, colocar V/(maxV) * algo)
                    // Vamos colocar o potencial escalado para caber no gráfico vertical.
                    // Por exemplo, escalamos o potencial tal que maxV corresponde a (maxY - minY)/2.
                    // Ou mais simples: V_esc = (V - minV) * (rangeYFunc/(3*maxV)) para não dominar.
                    // Se maxV=0 (poço infinito), isso evita divisão por zero. Se maxV=0, não plotaremos potencial.
                    boolean plotarPotencial = (maxV>1e-15);

                    // Margens
                    int margin = 50;

                    // Desenhar eixos
                    g2.setColor(Color.BLACK);
                    // Eixo X
                    g2.drawLine(margin, h/2, w-margin, h/2);
                    // Eixo Y
                    g2.drawLine(margin, margin, margin, h-margin);

                    for (int k=0; k<=5; k++) {
                        double xval = eixoX[0] + k*(rangeX/5.0);
                        int xp = margin + (int)((xval - eixoX[0])*(w-2*margin)/rangeX);
                        g2.drawLine(xp, h/2 - 5, xp, h/2 + 5);
                        g2.drawString(String.format("%.2f", xval), xp-10, h/2+20);
                    }

                    for (int k=0; k<=4; k++) {
                        double yval = minY + k*(rangeYFunc/4.0);
                        int yp = h - margin - (int)((yval - minY)*(h-2*margin)/rangeYFunc);
                        g2.drawLine(margin-5, yp, margin+5, yp);
                        g2.drawString(String.format("%.2f", yval), margin-45, yp+5);
                    }

                    // Plotar potencial (se houver)
                    if (plotarPotencial) {
                        g2.setColor(Color.MAGENTA);
                        double scaleV = (rangeYFunc/(3.0*maxV)); 
                        int xpOld=0;
                        int ypOld=0;
                        for (int i=0; i<eixoX.length; i++){
                            double xval = eixoX[i];
                            double vval = potencial[i];
                            double vesc = (vval - minV)*scaleV + minY;
                            int xp = margin + (int)((xval - eixoX[0])*(w-2*margin)/rangeX);
                            int yp = h - margin - (int)((vesc - minY)*(h-2*margin)/rangeYFunc);
                            if (i>0) g2.drawLine(xpOld, ypOld, xp, yp);
                            xpOld = xp;
                            ypOld = yp;
                        }
                        g2.drawString("Potencial (escala reduzida)", margin+10, margin+20);
                    }

                    // Plotar autofunções
                    Color[] cores = {Color.RED, Color.BLUE, Color.GREEN};
                    for (int m = 0; m < modosPlotar; m++) {
                        g2.setColor(cores[m % cores.length]);
                        int xpOld = 0;
                        int ypOld = 0;
                        for (int i = 0; i < eixoX.length; i++) {
                            double xval = eixoX[i];
                            double yval = autovetores[i][m];
                            int xp = margin + (int)((xval - eixoX[0])*(w-2*margin)/rangeX);
                            int yp = h - margin - (int)((yval - minY)*(h-2*margin)/rangeYFunc);
                            if (i > 0) {
                                g2.drawLine(xpOld, ypOld, xp, yp);
                            }
                            xpOld = xp;
                            ypOld = yp;
                        }
                        g2.drawString("Modo " + (m+1), margin+10, margin+40*(m+1));
                    }
                }
            }
        };

        splitCentral.setRightComponent(painelPlotagem);
        add(splitCentral, BorderLayout.CENTER);

        // Rodapé com o autor
        JLabel labelAutor = new JLabel("Autor: Luiz Tiago Wilcke", SwingConstants.CENTER);
        add(labelAutor, BorderLayout.SOUTH);

        botaoCalcular.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                try {
                    int N = Integer.parseInt(campoNumPontos.getText().trim());
                    double L = Double.parseDouble(campoComprimento.getText().trim());
                    double m = Double.parseDouble(campoMassa.getText().trim());
                    double V0 = Double.parseDouble(campoV0.getText().trim());
                    String tipo = (String) comboPotencial.getSelectedItem();

                    realizarCalculo(N, L, m, tipo, V0);
                } catch (NumberFormatException ex) {
                    JOptionPane.showMessageDialog(SimulacaoFotovoltaica.this,
                            "Parâmetros inválidos.", "Erro", JOptionPane.ERROR_MESSAGE);
                }
            }
        });
    }

    private void realizarCalculo(int N, double L, double m, String tipoPotencial, double V0) {
        double dx = L/(N-1);
        eixoX = new double[N];
        for (int i=0; i<N; i++) {
            eixoX[i] = i*dx;
        }

        potencial = new double[N];
        // Definir o potencial
        if (tipoPotencial.equals("Poço Infinito")) {
            // V(x)=0 no interior, infinito nas bordas implicitamente
            for (int i=0; i<N; i++){
                potencial[i]=0.0;
            }
        } else if (tipoPotencial.equals("Barreira Central")) {
            // Colocar uma barreira V0 no centro do domínio. Por exemplo, na região [L/3, 2L/3]
            double x1 = L/3.0;
            double x2 = 2.0*L/3.0;
            for (int i=0; i<N; i++){
                double x = eixoX[i];
                if (x>=x1 && x<=x2) {
                    potencial[i] = V0;
                } else {
                    potencial[i] = 0.0;
                }
            }
        }

        double h_bar = 1.0;
        double fator = - (h_bar*h_bar)/(2.0*m*dx*dx);

        // (N-2) pontos internos
        int Nint = N-2;
        double[][] H = new double[Nint][Nint];

        // Montar a parte cinética
        for (int i = 0; i < Nint; i++) {
            if (i > 0) {
                H[i][i-1] = fator;
            }
            H[i][i] = -2.0*fator;
            if (i < Nint-1) {
                H[i][i+1] = fator;
            }
        }

        // Incluir a parte do potencial: V(i)*δ(i,j)
        // O ponto i interno corresponde ao eixoX[i+1]
        for (int i=0; i<Nint; i++){
            double Vi = potencial[i+1]; 
            // adicionar V(i) na diagonal
            H[i][i] += Vi;
        }

        // Agora calculamos autovalores e autovetores pelo método de Jacobi
        double[][] eigenVectors = new double[Nint][Nint];
        double[] eigenValues = new double[Nint];
        for (int i=0; i<Nint; i++){
            eigenValues[i] = H[i][i];
            for(int j=0;j<Nint;j++){
                eigenVectors[i][j] = (i==j)?1.0:0.0;
            }
        }

        jacobiEigenDecomposition(H, eigenValues, eigenVectors);

        // Ordenar
        for (int i = 0; i < Nint-1; i++) {
            int minIndex = i;
            for (int j = i+1; j < Nint; j++) {
                if (eigenValues[j]<eigenValues[minIndex]) {
                    minIndex = j;
                }
            }
            if (minIndex != i) {
                double tempVal = eigenValues[i];
                eigenValues[i] = eigenValues[minIndex];
                eigenValues[minIndex] = tempVal;

                double[] tempVec = eigenVectors[minIndex];
                eigenVectors[minIndex] = eigenVectors[i];
                eigenVectors[i] = tempVec;
            }
        }

        // Expandir autovetores
        autovalores = eigenValues;
        autovetores = new double[N][Nint];
        for (int modo = 0; modo < Nint; modo++) {
            double norm = 0.0;
            for (int i=0; i<Nint; i++) {
                norm += eigenVectors[modo][i]*eigenVectors[modo][i];
            }
            norm = Math.sqrt(norm);

            autovetores[0][modo] = 0.0;
            for (int i=0; i<Nint; i++) {
                autovetores[i+1][modo] = eigenVectors[modo][i]/norm;
            }
            autovetores[N-1][modo] = 0.0;
        }

        DecimalFormat df = new DecimalFormat("#.###############"); // 15 dígitos de precisão
        String[] lista = new String[Nint];
        for (int i=0; i<Nint; i++) {
            lista[i] = "Modo " + (i+1) + ": Energia = " + df.format(autovalores[i]);
        }

        listaResultados.setListData(lista);
        painelPlotagem.repaint();
    }

    // Método de Jacobi para decomposição
    private void jacobiEigenDecomposition(double[][] H, double[] eigenValues, double[][] eigenVectors) {
        int n = H.length;
        double eps = 1e-15;
        int maxIter = 1000*n*n;

        for(int iter=0; iter<maxIter; iter++){
            double maxOff = 0.0;
            int p=0, q=0;
            for(int i=0; i<n-1; i++){
                for(int j=i+1; j<n; j++){
                    double val = Math.abs(H[i][j]);
                    if(val > maxOff){
                        maxOff = val;
                        p=i; q=j;
                    }
                }
            }

            if(maxOff < eps) break;

            double diff = eigenValues[q] - eigenValues[p];
            double t;
            if(Math.abs(H[p][q])<eps){
                t=0.0;
            } else {
                double phi = diff/(2.0*H[p][q]);
                t = 1.0/(Math.abs(phi)+Math.sqrt(phi*phi+1.0));
                if(phi<0.0) t = -t;
            }
            double c = 1.0/Math.sqrt(t*t+1.0);
            double s = t*c;
            double tau = s/(1.0+c);

            double hpq = H[p][q];
            H[p][q]=0.0;
            eigenValues[p] = eigenValues[p]-t*hpq;
            eigenValues[q] = eigenValues[q]+t*hpq;

            for(int i=0; i<p; i++){
                double g=H[i][p];
                double h=H[i][q];
                H[i][p]=g - s*(h + g*tau);
                H[i][q]=h + s*(g - h*tau);
            }
            for(int i=p+1; i<q; i++){
                double g=H[p][i];
                double h=H[i][q];
                H[p][i]=g - s*(h + g*tau);
                H[i][q]=h + s*(g - h*tau);
            }
            for(int i=q+1; i<n; i++){
                double g=H[p][i];
                double h=H[q][i];
                H[p][i]=g - s*(h + g*tau);
                H[q][i]=h + s*(g - h*tau);
            }

            for(int i=0; i<n; i++){
                double g=eigenVectors[i][p];
                double h=eigenVectors[i][q];
                eigenVectors[i][p] = g - s*(h + g*tau);
                eigenVectors[i][q] = h + s*(g - h*tau);
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            SimulacaoFotovoltaica frame = new SimulacaoFotovoltaica();
            frame.setVisible(true);
        });
    }
}
