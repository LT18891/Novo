import java.awt.BorderLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

public class ModeloDesempregoDiferencialGUI extends JFrame {
    private static final long serialVersionUID = 1L;

    // Campos de entrada
    private JTextField campoA;
    private JTextField campoB;
    private JTextField campoC;
    private JTextField campoD;
    private JTextField campoE;
    private JTextField campoF;
    private JTextField campoGCoef;
    private JTextField campoH;
    private JTextField campoU0;
    private JTextField campoG0;
    private JTextField campoI0;
    private JTextField campoTempo;

    private JButton botaoCalcular;
    private JPanel painelGraficoU;
    private JPanel painelGraficoG;
    private JPanel painelGraficoI;
    private JLabel labelEquacoes;

    public ModeloDesempregoDiferencialGUI() {
        super("Modelo de Previsão de Desemprego com Equações Diferenciais");

        // Painel principal com BorderLayout
        JPanel painelPrincipal = new JPanel(new BorderLayout(10, 10));
        painelPrincipal.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        // Painel de entrada com GridBagLayout
        JPanel painelEntrada = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5); // Espaçamento entre componentes
        gbc.anchor = GridBagConstraints.WEST;

        // Labels e campos de entrada
        JLabel labelA = new JLabel("Coeficiente a:");
        gbc.gridx = 0;
        gbc.gridy = 0;
        painelEntrada.add(labelA, gbc);

        campoA = new JTextField("-0.5", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoA, gbc);

        JLabel labelB = new JLabel("Coeficiente b:");
        gbc.gridx = 0;
        gbc.gridy = 1;
        painelEntrada.add(labelB, gbc);

        campoB = new JTextField("0.3", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoB, gbc);

        JLabel labelC = new JLabel("Coeficiente c:");
        gbc.gridx = 0;
        gbc.gridy = 2;
        painelEntrada.add(labelC, gbc);

        campoC = new JTextField("0.2", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoC, gbc);

        JLabel labelD = new JLabel("Coeficiente d:");
        gbc.gridx = 0;
        gbc.gridy = 3;
        painelEntrada.add(labelD, gbc);

        campoD = new JTextField("0.1", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoD, gbc);

        JLabel labelE = new JLabel("Coeficiente e:");
        gbc.gridx = 0;
        gbc.gridy = 4;
        painelEntrada.add(labelE, gbc);

        campoE = new JTextField("0.05", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoE, gbc);

        JLabel labelF = new JLabel("Coeficiente f:");
        gbc.gridx = 0;
        gbc.gridy = 5;
        painelEntrada.add(labelF, gbc);

        campoF = new JTextField("0.02", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoF, gbc);

        JLabel labelGCoef = new JLabel("Coeficiente g:");
        gbc.gridx = 0;
        gbc.gridy = 6;
        painelEntrada.add(labelGCoef, gbc);

        campoGCoef = new JTextField("0.03", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoGCoef, gbc);

        JLabel labelH = new JLabel("Coeficiente h:");
        gbc.gridx = 0;
        gbc.gridy = 7;
        painelEntrada.add(labelH, gbc);

        campoH = new JTextField("0.04", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoH, gbc);

        JLabel labelG0 = new JLabel("Crescimento do PIB Inicial (G₀):");
        gbc.gridx = 0;
        gbc.gridy = 8;
        painelEntrada.add(labelG0, gbc);

        campoG0 = new JTextField("2.0", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoG0, gbc);

        JLabel labelI0 = new JLabel("Inflação Inicial (I₀):");
        gbc.gridx = 0;
        gbc.gridy = 9;
        painelEntrada.add(labelI0, gbc);

        campoI0 = new JTextField("3.0", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoI0, gbc);

        JLabel labelU0 = new JLabel("Desemprego Inicial (U₀):");
        gbc.gridx = 0;
        gbc.gridy = 10;
        painelEntrada.add(labelU0, gbc);

        campoU0 = new JTextField("5.0", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoU0, gbc);

        JLabel labelTempo = new JLabel("Tempo de Simulação (anos):");
        gbc.gridx = 0;
        gbc.gridy = 11;
        painelEntrada.add(labelTempo, gbc);

        campoTempo = new JTextField("10", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoTempo, gbc);

        // Botão de calcular
        botaoCalcular = new JButton("Calcular e Plotar");
        gbc.gridx = 0;
        gbc.gridy = 12;
        gbc.gridwidth = 2;
        gbc.anchor = GridBagConstraints.CENTER;
        painelEntrada.add(botaoCalcular, gbc);

        painelPrincipal.add(painelEntrada, BorderLayout.WEST);

        // Área para exibir as equações
        labelEquacoes = new JLabel(getEquacoesHTML());
        labelEquacoes.setBorder(BorderFactory.createTitledBorder("Equações do Modelo"));
        painelPrincipal.add(labelEquacoes, BorderLayout.NORTH);

        // Painéis dos gráficos
        painelGraficoU = new JPanel(new BorderLayout());
        painelGraficoG = new JPanel(new BorderLayout());
        painelGraficoI = new JPanel(new BorderLayout());

        JPanel painelGraficos = new JPanel(new GridBagLayout());
        GridBagConstraints gbcGraficos = new GridBagConstraints();
        gbcGraficos.insets = new Insets(5, 5, 5, 5);
        gbcGraficos.gridx = 0;
        gbcGraficos.gridy = 0;
        gbcGraficos.weightx = 1.0;
        gbcGraficos.weighty = 1.0;
        gbcGraficos.fill = GridBagConstraints.BOTH;
        painelGraficos.add(painelGraficoU, gbcGraficos);

        gbcGraficos.gridx = 1;
        painelGraficos.add(painelGraficoG, gbcGraficos);

        gbcGraficos.gridx = 2;
        painelGraficos.add(painelGraficoI, gbcGraficos);

        painelPrincipal.add(painelGraficos, BorderLayout.CENTER);

        setContentPane(painelPrincipal);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1600, 800);
        setLocationRelativeTo(null);

        // Ação do botão
        botaoCalcular.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                calcularEPlotar();
            }
        });
    }

    private String getEquacoesHTML() {
        return "<html><body style='font-family: sans-serif;'>" +
                "<h3>Equações Diferenciais do Modelo:</h3>" +
                "<p>dU/dt = a &middot; G + b &middot; I - c &middot; U</p>" +
                "<p>dG/dt = d &middot; G - e &middot; U + f &middot; I</p>" +
                "<p>dI/dt = g &middot; U - h &middot; I</p>" +
                "</body></html>";
    }

    private void calcularEPlotar() {
        // Leitura e validação dos inputs
        double a, b, c, d, e, f, g, h, G0, I0, U0;
        int tempo;

        try {
            a = Double.parseDouble(campoA.getText().replace(",", "."));
            b = Double.parseDouble(campoB.getText().replace(",", "."));
            c = Double.parseDouble(campoC.getText().replace(",", "."));
            d = Double.parseDouble(campoD.getText().replace(",", "."));
            e = Double.parseDouble(campoE.getText().replace(",", "."));
            f = Double.parseDouble(campoF.getText().replace(",", "."));
            g = Double.parseDouble(campoGCoef.getText().replace(",", "."));
            h = Double.parseDouble(campoH.getText().replace(",", "."));
            G0 = Double.parseDouble(campoG0.getText().replace(",", "."));
            I0 = Double.parseDouble(campoI0.getText().replace(",", "."));
            U0 = Double.parseDouble(campoU0.getText().replace(",", "."));
            tempo = Integer.parseInt(campoTempo.getText());

            if (c <= 0 || d <= 0 || e <= 0 || f <= 0 || g <= 0 || h <= 0) {
                JOptionPane.showMessageDialog(this, "Os coeficientes c, d, e, f, g e h devem ser positivos.",
                        "Erro de Entrada", JOptionPane.ERROR_MESSAGE);
                return;
            }

            if (tempo <= 0) {
                JOptionPane.showMessageDialog(this, "O tempo de simulação deve ser positivo.",
                        "Erro de Entrada", JOptionPane.ERROR_MESSAGE);
                return;
            }

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Por favor, insira valores numéricos válidos.",
                    "Erro de Entrada", JOptionPane.ERROR_MESSAGE);
            return;
        }

        // Parâmetros do modelo
        // Equações:
        // dU/dt = a*G + b*I - c*U
        // dG/dt = d*G - e*U + f*I
        // dI/dt = g*U - h*I

        // Método de Euler para resolver o sistema de ODEs
        double passo = 0.01; // Passo de integração (anos)
        int passos = (int) (tempo / passo);
        double t = 0.0;

        double U = U0;
        double G = G0;
        double I = I0;

        // Series para os gráficos
        XYSeries seriesU = new XYSeries("Taxa de Desemprego (U)");
        XYSeries seriesG = new XYSeries("Crescimento do PIB (G)");
        XYSeries seriesI = new XYSeries("Inflação (I)");

        seriesU.add(t, U);
        seriesG.add(t, G);
        seriesI.add(t, I);

        for (int i = 0; i < passos; i++) {
            // Cálculo das derivadas
            double dUdt = a * G + b * I - c * U;
            double dGdt = d * G - e * U + f * I;
            double dIdt = g * U - h * I;

            // Atualização das variáveis usando Euler
            U += dUdt * passo;
            G += dGdt * passo;
            I += dIdt * passo;
            t += passo;

            seriesU.add(t, U);
            seriesG.add(t, G);
            seriesI.add(t, I);
        }

        // Dataset para os gráficos
        XYSeriesCollection datasetU = new XYSeriesCollection();
        datasetU.addSeries(seriesU);

        XYSeriesCollection datasetG = new XYSeriesCollection();
        datasetG.addSeries(seriesG);

        XYSeriesCollection datasetI = new XYSeriesCollection();
        datasetI.addSeries(seriesI);

        // Criação dos gráficos
        JFreeChart chartU = ChartFactory.createXYLineChart(
                "Taxa de Desemprego ao Longo do Tempo",
                "Tempo (anos)",
                "Taxa de Desemprego (%)",
                datasetU
        );

        JFreeChart chartG = ChartFactory.createXYLineChart(
                "Crescimento do PIB ao Longo do Tempo",
                "Tempo (anos)",
                "Crescimento do PIB (%)",
                datasetG
        );

        JFreeChart chartI = ChartFactory.createXYLineChart(
                "Inflação ao Longo do Tempo",
                "Tempo (anos)",
                "Inflação (%)",
                datasetI
        );

        // Adiciona os gráficos aos painéis
        painelGraficoU.removeAll();
        ChartPanel chartPanelU = new ChartPanel(chartU);
        painelGraficoU.add(chartPanelU, BorderLayout.CENTER);
        painelGraficoU.revalidate();
        painelGraficoU.repaint();

        painelGraficoG.removeAll();
        ChartPanel chartPanelG = new ChartPanel(chartG);
        painelGraficoG.add(chartPanelG, BorderLayout.CENTER);
        painelGraficoG.revalidate();
        painelGraficoG.repaint();

        painelGraficoI.removeAll();
        ChartPanel chartPanelI = new ChartPanel(chartI);
        painelGraficoI.add(chartPanelI, BorderLayout.CENTER);
        painelGraficoI.revalidate();
        painelGraficoI.repaint();

        // Exibição do resultado em uma mensagem
        JOptionPane.showMessageDialog(this,
                String.format("Simulação concluída para %d anos.", tempo),
                "Resultado",
                JOptionPane.INFORMATION_MESSAGE);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            ModeloDesempregoDiferencialGUI gui = new ModeloDesempregoDiferencialGUI();
            gui.setVisible(true);
        });
    }
}
