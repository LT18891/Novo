import javax.swing.*;
import java.awt.*;
import org.jfree.chart.*;
import org.jfree.chart.plot.XYPlot;
import org.jfree.data.xy.*;
import java.text.DecimalFormat;
import java.util.Random;

public class PrevisaoBitcoinAprimorada extends JFrame {
    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	// Variáveis em português
    private double precoInicial = 20000.000000; // Preço inicial do Bitcoin
    private double taxaReversao = 0.1; // Taxa de reversão à média (mu)
    private double precoMedia = 25000.000000; // Preço médio (P_média)
    private double volatilidade = 0.25; // Volatilidade (sigma)
    private double expoenteVolatilidade = 1.0; // Expoente da volatilidade (gamma)
    private int numeroDias = 365; // Número de dias para simulação
    private double deltaT = 1.0 / 365; // Incremento de tempo (1 dia)

    private XYSeries seriePreco;
    private DecimalFormat df = new DecimalFormat("#.######");

    // Componentes da interface
    private XYSeriesCollection dataset;
    private JFreeChart grafico;
    private ChartPanel painelGrafico;
    private JLabel labelResultado;

    // Componentes de entrada
    private JTextField campoPrecoInicial;
    private JTextField campoTaxaReversao;
    private JTextField campoPrecoMedia;
    private JTextField campoVolatilidade;
    private JTextField campoExpoenteVolatilidade;
    private JTextField campoNumeroDias;

    public PrevisaoBitcoinAprimorada(String titulo) {
        super(titulo);
        seriePreco = new XYSeries("Preço do Bitcoin");

        // Cria o painel com abas
        JTabbedPane abas = new JTabbedPane();

        // Aba de Parâmetros
        JPanel painelParametros = criarPainelParametros();
        abas.addTab("Parâmetros", painelParametros);

        // Aba do Gráfico
        JPanel painelGraficoTab = criarPainelGrafico();
        abas.addTab("Gráfico", painelGraficoTab);

        // Aba da Equação
        JPanel painelEquacao = criarPainelEquacao();
        abas.addTab("Equação", painelEquacao);

        // Aba da Explicação
        JPanel painelExplicacao = criarPainelExplicacao();
        abas.addTab("Explicação", painelExplicacao);

        // Aba da Legenda
        JPanel painelLegenda = criarPainelLegenda();
        abas.addTab("Autor", painelLegenda);

        setContentPane(abas);

        // Executa a simulação com valores padrão ao iniciar
        simularPrecoBitcoin();
        atualizarGrafico();
    }

    private JPanel criarPainelParametros() {
        JPanel painel = new JPanel();
        painel.setLayout(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();

        // Labels e campos de entrada
        JLabel labelPrecoInicial = new JLabel("Preço Inicial (USD):");
        campoPrecoInicial = new JTextField("20000.000000", 15);
        campoPrecoInicial.setToolTipText("Valor padrão: 20000.000000");

        JLabel labelTaxaReversao = new JLabel("Taxa de Reversão (μ):");
        campoTaxaReversao = new JTextField("0.1", 15);
        campoTaxaReversao.setToolTipText("Valor padrão: 0.1");

        JLabel labelPrecoMedia = new JLabel("Preço Médio (USD):");
        campoPrecoMedia = new JTextField("25000.000000", 15);
        campoPrecoMedia.setToolTipText("Valor padrão: 25000.000000");

        JLabel labelVolatilidade = new JLabel("Volatilidade (σ):");
        campoVolatilidade = new JTextField("0.25", 15);
        campoVolatilidade.setToolTipText("Valor padrão: 0.25");

        JLabel labelExpoenteVolatilidade = new JLabel("Expoente da Volatilidade (γ):");
        campoExpoenteVolatilidade = new JTextField("1.0", 15);
        campoExpoenteVolatilidade.setToolTipText("Valor padrão: 1.0");

        JLabel labelNumeroDias = new JLabel("Número de Dias:");
        campoNumeroDias = new JTextField("365", 15);
        campoNumeroDias.setToolTipText("Valor padrão: 365");

        // Botão de Simulação
        JButton botaoSimular = new JButton("Simular");
        botaoSimular.addActionListener(e -> {
            if (validarEntradas()) {
                atualizarVariaveis();
                simularPrecoBitcoin();
                atualizarGrafico();
                atualizarResultado();
                JOptionPane.showMessageDialog(this, "Simulação concluída com sucesso!", "Sucesso", JOptionPane.INFORMATION_MESSAGE);
            }
        });

        // Layout dos componentes
        gbc.insets = new Insets(10, 10, 10, 10);
        gbc.anchor = GridBagConstraints.WEST;

        gbc.gridx = 0;
        gbc.gridy = 0;
        painel.add(labelPrecoInicial, gbc);

        gbc.gridx = 1;
        painel.add(campoPrecoInicial, gbc);

        gbc.gridx = 0;
        gbc.gridy = 1;
        painel.add(labelTaxaReversao, gbc);

        gbc.gridx = 1;
        painel.add(campoTaxaReversao, gbc);

        gbc.gridx = 0;
        gbc.gridy = 2;
        painel.add(labelPrecoMedia, gbc);

        gbc.gridx = 1;
        painel.add(campoPrecoMedia, gbc);

        gbc.gridx = 0;
        gbc.gridy = 3;
        painel.add(labelVolatilidade, gbc);

        gbc.gridx = 1;
        painel.add(campoVolatilidade, gbc);

        gbc.gridx = 0;
        gbc.gridy = 4;
        painel.add(labelExpoenteVolatilidade, gbc);

        gbc.gridx = 1;
        painel.add(campoExpoenteVolatilidade, gbc);

        gbc.gridx = 0;
        gbc.gridy = 5;
        painel.add(labelNumeroDias, gbc);

        gbc.gridx = 1;
        painel.add(campoNumeroDias, gbc);

        gbc.gridx = 1;
        gbc.gridy = 6;
        gbc.anchor = GridBagConstraints.CENTER;
        painel.add(botaoSimular, gbc);

        return painel;
    }

    private JPanel criarPainelGrafico() {
        JPanel painel = new JPanel(new BorderLayout());

        // Cria o dataset e o gráfico
        dataset = new XYSeriesCollection();
        dataset.addSeries(seriePreco);

        grafico = ChartFactory.createXYLineChart(
                "Previsão do Preço do Bitcoin",
                "Dias",
                "Preço (USD)",
                dataset
        );

        // Configurações do painel gráfico
        painelGrafico = new ChartPanel(grafico);
        painelGrafico.setPreferredSize(new Dimension(800, 600));
        painel.add(painelGrafico, BorderLayout.CENTER);

        // Label para resultado numérico
        labelResultado = new JLabel();
        labelResultado.setHorizontalAlignment(SwingConstants.CENTER);
        painel.add(labelResultado, BorderLayout.SOUTH);

        return painel;
    }

    private JPanel criarPainelEquacao() {
        JPanel painel = new JPanel();
        painel.setLayout(new BorderLayout());

        // Utiliza HTML para renderizar a equação
        String equacao = "<html><body style='font-size: 16px;'>" +
                "<p><b>Modelo Matemático:</b></p>" +
                "<p>&nbsp;&nbsp;&nbsp;&nbsp;<i>dP(t)</i> = &mu; (<i>P<sub>média</sub></i> - <i>P(t)</i>) dt + &sigma; <i>P(t)</i><sup>&gamma;</sup> dW(t)</p>" +
                "</body></html>";

        JLabel labelEquacao = new JLabel(equacao);
        labelEquacao.setHorizontalAlignment(SwingConstants.CENTER);
        painel.add(labelEquacao, BorderLayout.CENTER);

        return painel;
    }

    private JPanel criarPainelExplicacao() {
        JPanel painel = new JPanel();
        painel.setLayout(new BorderLayout());

        String explicacao = "<html><body style='font-size: 14px; padding: 10px;'>" +
                "<h2>Explicação do Modelo</h2>" +
                "<p>O modelo utilizado para a previsão do preço do Bitcoin é uma Equação Diferencial Estocástica (EDE) que incorpora tanto a tendência de reversão à média quanto a volatilidade dependente do preço.</p>" +
                "<p><b>Termos da Equação:</b></p>" +
                "<ul>" +
                "<li><i>dP(t)</i>: Variação do preço do Bitcoin no tempo <i>t</i>.</li>" +
                "<li><i>&mu; (P<sub>média</sub> - P(t)) dt</i>: Termo de reversão à média, onde <i>&mu;</i> é a taxa de reversão e <i>P<sub>média</sub></i> é o preço médio alvo.</li>" +
                "<li><i>&sigma; P(t)<sup>&gamma;</sup> dW(t)</i>: Termo de volatilidade, onde <i>&sigma;</i> é a volatilidade, <i>&gamma;</i> ajusta a dependência da volatilidade em relação ao preço, e <i>dW(t)</i> é o processo de Wiener que introduz a aleatoriedade.</li>" +
                "</ul>" +
                "<p>Este modelo permite capturar a tendência do preço a retornar a um valor médio, além de permitir que a volatilidade varie com o preço, proporcionando uma dinâmica mais realista para a previsão do Bitcoin.</p>" +
                "</body></html>";

        JLabel labelExplicacao = new JLabel(explicacao);
        JScrollPane scrollExplicacao = new JScrollPane(labelExplicacao);
        painel.add(scrollExplicacao, BorderLayout.CENTER);

        return painel;
    }

    private JPanel criarPainelLegenda() {
        JPanel painel = new JPanel();
        painel.setLayout(new BorderLayout());

        String legenda = "<html><body style='font-size: 14px; text-align: center; color: blue;'>" +
                "<p><b>Autor:</b> Luiz Tiago Wilcke</p>" +
                "</body></html>";

        JLabel labelLegenda = new JLabel(legenda);
        labelLegenda.setHorizontalAlignment(SwingConstants.CENTER);
        painel.add(labelLegenda, BorderLayout.CENTER);

        return painel;
    }

    private void simularPrecoBitcoin() {
        seriePreco.clear(); // Limpa a série antes de simular
        double P = precoInicial;
        seriePreco.add(0, P);
        Random random = new Random();

        for (int dia = 1; dia <= numeroDias; dia++) {
            double dW = random.nextGaussian() * Math.sqrt(deltaT);
            // Modelo de Ornstein-Uhlenbeck Estendido
            P = P + taxaReversao * (precoMedia - P) * deltaT + volatilidade * Math.pow(P, expoenteVolatilidade) * dW;
            // Adiciona o preço à série
            seriePreco.add(dia, P);
        }
    }

    private void atualizarGrafico() {
        dataset.removeAllSeries();
        dataset.addSeries(seriePreco);
        grafico.getXYPlot().getRangeAxis().setAutoRange(true); // Ajusta o eixo Y automaticamente
    }

    private void atualizarResultado() {
        double precoFinal = seriePreco.getY(numeroDias).doubleValue();
        labelResultado.setText("Preço final do Bitcoin após " + numeroDias + " dias: $" + df.format(precoFinal));
    }

    private boolean validarEntradas() {
        try {
            double pi = Double.parseDouble(campoPrecoInicial.getText());
            double tr = Double.parseDouble(campoTaxaReversao.getText());
            double pm = Double.parseDouble(campoPrecoMedia.getText());
            double v = Double.parseDouble(campoVolatilidade.getText());
            double ev = Double.parseDouble(campoExpoenteVolatilidade.getText());
            int nd = Integer.parseInt(campoNumeroDias.getText());

            if (pi <= 0 || tr < 0 || pm <= 0 || v < 0 || ev < 0 || nd <= 0) {
                JOptionPane.showMessageDialog(this, "Por favor, insira valores positivos e válidos para todas as variáveis.", "Erro de Validação", JOptionPane.ERROR_MESSAGE);
                return false;
            }
        } catch (NumberFormatException e) {
            JOptionPane.showMessageDialog(this, "Por favor, insira valores numéricos válidos.", "Erro de Formato", JOptionPane.ERROR_MESSAGE);
            return false;
        }
        return true;
    }

    private void atualizarVariaveis() {
        precoInicial = Double.parseDouble(campoPrecoInicial.getText());
        taxaReversao = Double.parseDouble(campoTaxaReversao.getText());
        precoMedia = Double.parseDouble(campoPrecoMedia.getText());
        volatilidade = Double.parseDouble(campoVolatilidade.getText());
        expoenteVolatilidade = Double.parseDouble(campoExpoenteVolatilidade.getText());
        numeroDias = Integer.parseInt(campoNumeroDias.getText());
        deltaT = 1.0 / numeroDias;
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            PrevisaoBitcoinAprimorada exemplo = new PrevisaoBitcoinAprimorada("Modelo de Previsão do Bitcoin");
            exemplo.setSize(1000, 800);
            exemplo.setLocationRelativeTo(null);
            exemplo.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            exemplo.setVisible(true);
        });
    }
}
