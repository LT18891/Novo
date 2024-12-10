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
    private JTextField campoG;
    private JTextField campoI;
    private JTextField campoU0;
    private JTextField campoTempo;

    private JButton botaoCalcular;
    private JPanel painelGraficoPIB;
    private JPanel painelGraficoInflacao;

    public ModeloDesempregoDiferencialGUI() {
        super("Modelo de Previsão de Desemprego com Equação Diferencial");

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

        JLabel labelG = new JLabel("Crescimento do PIB (G):");
        gbc.gridx = 0;
        gbc.gridy = 3;
        painelEntrada.add(labelG, gbc);

        campoG = new JTextField("2.0", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoG, gbc);

        JLabel labelI = new JLabel("Inflação (I):");
        gbc.gridx = 0;
        gbc.gridy = 4;
        painelEntrada.add(labelI, gbc);

        campoI = new JTextField("3.0", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoI, gbc);

        JLabel labelU0 = new JLabel("Desemprego Inicial (U₀):");
        gbc.gridx = 0;
        gbc.gridy = 5;
        painelEntrada.add(labelU0, gbc);

        campoU0 = new JTextField("5.0", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoU0, gbc);

        JLabel labelTempo = new JLabel("Tempo de Simulação (anos):");
        gbc.gridx = 0;
        gbc.gridy = 6;
        painelEntrada.add(labelTempo, gbc);

        campoTempo = new JTextField("10", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoTempo, gbc);

        // Botão de calcular
        botaoCalcular = new JButton("Calcular e Plotar");
        gbc.gridx = 0;
        gbc.gridy = 7;
        gbc.gridwidth = 2;
        gbc.anchor = GridBagConstraints.CENTER;
        painelEntrada.add(botaoCalcular, gbc);

        painelPrincipal.add(painelEntrada, BorderLayout.NORTH);

        // Painéis dos gráficos
        painelGraficoPIB = new JPanel(new BorderLayout());
        painelGraficoInflacao = new JPanel(new BorderLayout());

        JPanel painelGraficos = new JPanel(new GridBagLayout());
        GridBagConstraints gbcGraficos = new GridBagConstraints();
        gbcGraficos.insets = new Insets(5, 5, 5, 5);
        gbcGraficos.gridx = 0;
        gbcGraficos.gridy = 0;
        gbcGraficos.weightx = 1.0;
        gbcGraficos.weighty = 1.0;
        gbcGraficos.fill = GridBagConstraints.BOTH;
        painelGraficos.add(painelGraficoPIB, gbcGraficos);

        gbcGraficos.gridx = 1;
        painelGraficos.add(painelGraficoInflacao, gbcGraficos);

        painelPrincipal.add(painelGraficos, BorderLayout.CENTER);

        setContentPane(painelPrincipal);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1000, 600);
        setLocationRelativeTo(null);

        // Ação do botão
        botaoCalcular.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                calcularEPlotar();
            }
        });
    }

    private void calcularEPlotar() {
        // Leitura e validação dos inputs
        double a, b, c, G, I, U0;
        int tempo;

        try {
            a = Double.parseDouble(campoA.getText().replace(",", "."));
            b = Double.parseDouble(campoB.getText().replace(",", "."));
            c = Double.parseDouble(campoC.getText().replace(",", "."));
            G = Double.parseDouble(campoG.getText().replace(",", "."));
            I = Double.parseDouble(campoI.getText().replace(",", "."));
            U0 = Double.parseDouble(campoU0.getText().replace(",", "."));
            tempo = Integer.parseInt(campoTempo.getText());

            if (c <= 0) {
                JOptionPane.showMessageDialog(this, "O coeficiente c deve ser positivo.",
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
        // Equação: dU/dt = a*G + b*I - c*U
        // Solução: U(t) = (a*G + b*I)/c + (U0 - (a*G + b*I)/c) * e^(-c*t)

        // Coeficiente para a solução analítica
        double U_eq = (a * G + b * I) / c;

        // Series para os gráficos
        XYSeries seriesPIB = new XYSeries("Desemprego vs Crescimento do PIB");
        XYSeries seriesInflacao = new XYSeries("Desemprego vs Inflação");

        // Variáveis para variação
        double passo = 0.1; // Passo para variação das variáveis
        int pontos = 100;

        // Variação do Crescimento do PIB (mantendo I constante)
        double G_min = G - 5;
        double G_max = G + 5;

        for (int i = 0; i <= pontos; i++) {
            double G_var = G_min + i * (G_max - G_min) / pontos;
            double U = (a * G_var + b * I) / c;
            seriesPIB.add(G_var, U);
        }

        // Variação da Inflação (mantendo G constante)
        double I_min = I - 5;
        double I_max = I + 5;

        for (int i = 0; i <= pontos; i++) {
            double I_var = I_min + i * (I_max - I_min) / pontos;
            double U = (a * G + b * I_var) / c;
            seriesInflacao.add(I_var, U);
        }

        // Dataset para os gráficos
        XYSeriesCollection datasetPIB = new XYSeriesCollection();
        datasetPIB.addSeries(seriesPIB);

        XYSeriesCollection datasetInflacao = new XYSeriesCollection();
        datasetInflacao.addSeries(seriesInflacao);

        // Criação dos gráficos
        JFreeChart chartPIB = ChartFactory.createXYLineChart(
                "Relação entre Desemprego e Crescimento do PIB",
                "Crescimento do PIB (%)",
                "Taxa de Desemprego (%)",
                datasetPIB
        );

        JFreeChart chartInflacao = ChartFactory.createXYLineChart(
                "Relação entre Desemprego e Inflação",
                "Inflação (%)",
                "Taxa de Desemprego (%)",
                datasetInflacao
        );

        // Adiciona os gráficos aos painéis
        painelGraficoPIB.removeAll();
        ChartPanel chartPanelPIB = new ChartPanel(chartPIB);
        painelGraficoPIB.add(chartPanelPIB, BorderLayout.CENTER);
        painelGraficoPIB.revalidate();
        painelGraficoPIB.repaint();

        painelGraficoInflacao.removeAll();
        ChartPanel chartPanelInflacao = new ChartPanel(chartInflacao);
        painelGraficoInflacao.add(chartPanelInflacao, BorderLayout.CENTER);
        painelGraficoInflacao.revalidate();
        painelGraficoInflacao.repaint();

        // Exibição do resultado em uma mensagem
        JOptionPane.showMessageDialog(this,
                String.format("Taxa de Desemprego de Equilíbrio: %.2f%%", U_eq),
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
