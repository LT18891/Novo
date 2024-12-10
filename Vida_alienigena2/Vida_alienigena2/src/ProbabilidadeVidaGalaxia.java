import javax.swing.*;
import java.awt.*;
import java.awt.geom.*;
import java.awt.event.*;
import java.math.RoundingMode;
import java.text.DecimalFormat;
import java.util.Random;
import java.util.ArrayList;
import java.util.List;

/**
 * Autor: Luiz Tiago Wilcke
 * 
 * Modelo de Probabilidade de Vida na Via Láctea utilizando Equação Diferencial Estocástica e Simulação de Monte Carlo.
 */
public class ProbabilidadeVidaGalaxia extends JFrame {

    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	public ProbabilidadeVidaGalaxia() {
        setTitle("Probabilidade de Vida na Via Láctea - Simulação Avançada");
        setSize(1600, 1000);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        // Adiciona o painel personalizado
        add(new PainelModelo());

        setVisible(true);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new ProbabilidadeVidaGalaxia());
    }
}

class PainelModelo extends JPanel {
    // Campos de entrada para as variáveis
    private JTextField campoAlphaMedia;
    private JTextField campoAlphaDesvio;

    private JTextField campoBetaMedia;
    private JTextField campoBetaDesvio;

    private JTextField campoGammaMedia;
    private JTextField campoGammaDesvio;

    private JTextField campoSigmaMedia;
    private JTextField campoSigmaDesvio;

    private JTextField campoNumeroSimulacoes;

    // Label para exibir o resultado
    private JTextArea areaResultado;

    // Lista para armazenar estrelas
    private List<Star> stars;

    // Número total de estrelas na galáxia
    private static final int NUMERO_ESTRELAS = 10000;

    // Parâmetros da Equação Diferencial Estocástica
    private double alpha; // Taxa de surgimento de civilizações
    private double beta;  // Taxa de extinção de civilizações devido à competição
    private double gamma; // Taxa de extinção devido a interações complexas
    private double sigma; // Intensidade do ruído estocástico

    // Número de simulações (iterações temporais)
    private int numeroSimulacoes;

    // Tempo total da simulação
    private double tempoTotal = 10000.0; // anos

    // Incremento de tempo
    private double deltaT = 1.0; // anos

    public PainelModelo() {
        setLayout(new BorderLayout());

        // Inicializar lista de estrelas
        stars = new ArrayList<>();
        gerarEstrelas();

        // Painel de entrada e cálculo
        JPanel painelEntrada = criarPainelEntrada();
        add(painelEntrada, BorderLayout.WEST);

        // Painel de desenho e resultados
        JPanel painelCentro = new JPanel(new BorderLayout());
        PainelDesenho painelDesenho = new PainelDesenho(stars);
        painelCentro.add(painelDesenho, BorderLayout.CENTER);

        // Painel de resultados
        JPanel painelResultados = criarPainelResultados();
        painelCentro.add(painelResultados, BorderLayout.SOUTH);

        add(painelCentro, BorderLayout.CENTER);
    }

    private JPanel criarPainelEntrada() {
        JPanel painel = new JPanel();
        painel.setLayout(new GridBagLayout());
        painel.setPreferredSize(new Dimension(400, 1000));
        painel.setBackground(new Color(30, 30, 30));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(8, 8, 8, 8);
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.anchor = GridBagConstraints.NORTHWEST;

        JLabel titulo = new JLabel("Parâmetros da Simulação (SDE)");
        titulo.setForeground(Color.WHITE);
        titulo.setFont(new Font("Arial", Font.BOLD, 16));
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.gridwidth = 2;
        painel.add(titulo, gbc);

        gbc.gridwidth = 1;

        // Alpha (α) - Taxa de Surgimento de Civilizações
        JLabel labelAlpha = new JLabel("α (surgimento civilizações):");
        labelAlpha.setForeground(Color.WHITE);
        gbc.gridx = 0;
        gbc.gridy = 1;
        painel.add(labelAlpha, gbc);

        campoAlphaMedia = new JTextField("0.1");
        gbc.gridx = 1;
        painel.add(campoAlphaMedia, gbc);

        JLabel labelAlphaDesvio = new JLabel("Desvio:");
        labelAlphaDesvio.setForeground(Color.WHITE);
        gbc.gridx = 0;
        gbc.gridy = 2;
        painel.add(labelAlphaDesvio, gbc);

        campoAlphaDesvio = new JTextField("0.02");
        gbc.gridx = 1;
        painel.add(campoAlphaDesvio, gbc);

        // Beta (β) - Taxa de Extinção de Civilizações
        JLabel labelBeta = new JLabel("β (extinção civilizações):");
        labelBeta.setForeground(Color.WHITE);
        gbc.gridx = 0;
        gbc.gridy = 3;
        painel.add(labelBeta, gbc);

        campoBetaMedia = new JTextField("0.05");
        gbc.gridx = 1;
        painel.add(campoBetaMedia, gbc);

        JLabel labelBetaDesvio = new JLabel("Desvio:");
        labelBetaDesvio.setForeground(Color.WHITE);
        gbc.gridx = 0;
        gbc.gridy = 4;
        painel.add(labelBetaDesvio, gbc);

        campoBetaDesvio = new JTextField("0.01");
        gbc.gridx = 1;
        painel.add(campoBetaDesvio, gbc);

        // Gamma (γ) - Taxa de Interação (não-linear)
        JLabel labelGamma = new JLabel("γ (interação civilizações):");
        labelGamma.setForeground(Color.WHITE);
        gbc.gridx = 0;
        gbc.gridy = 5;
        painel.add(labelGamma, gbc);

        campoGammaMedia = new JTextField("0.0001");
        gbc.gridx = 1;
        painel.add(campoGammaMedia, gbc);

        JLabel labelGammaDesvio = new JLabel("Desvio:");
        labelGammaDesvio.setForeground(Color.WHITE);
        gbc.gridx = 0;
        gbc.gridy = 6;
        painel.add(labelGammaDesvio, gbc);

        campoGammaDesvio = new JTextField("0.00002");
        gbc.gridx = 1;
        painel.add(campoGammaDesvio, gbc);

        // Sigma (σ) - Intensidade do Ruído Estocástico
        JLabel labelSigma = new JLabel("σ (intensidade do ruído):");
        labelSigma.setForeground(Color.WHITE);
        gbc.gridx = 0;
        gbc.gridy = 7;
        painel.add(labelSigma, gbc);

        campoSigmaMedia = new JTextField("0.01");
        gbc.gridx = 1;
        painel.add(campoSigmaMedia, gbc);

        JLabel labelSigmaDesvio = new JLabel("Desvio:");
        labelSigmaDesvio.setForeground(Color.WHITE);
        gbc.gridx = 0;
        gbc.gridy = 8;
        painel.add(labelSigmaDesvio, gbc);

        campoSigmaDesvio = new JTextField("0.002");
        gbc.gridx = 1;
        painel.add(campoSigmaDesvio, gbc);

        // Número de Simulações
        JLabel labelSimulacoes = new JLabel("Número de Simulações:");
        labelSimulacoes.setForeground(Color.WHITE);
        gbc.gridx = 0;
        gbc.gridy = 9;
        painel.add(labelSimulacoes, gbc);

        campoNumeroSimulacoes = new JTextField("10000");
        gbc.gridx = 1;
        painel.add(campoNumeroSimulacoes, gbc);

        // Botão Executar Simulação
        JButton botaoCalcular = new JButton("Executar Simulação");
        botaoCalcular.setBackground(new Color(70, 130, 180));
        botaoCalcular.setForeground(Color.WHITE);
        botaoCalcular.setFocusPainted(false);
        gbc.gridx = 0;
        gbc.gridy = 10;
        gbc.gridwidth = 2;
        painel.add(botaoCalcular, gbc);

        // Ação do botão Calcular
        botaoCalcular.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                executarSimulacao();
            }
        });

        return painel;
    }

    private JPanel criarPainelResultados() {
        JPanel painel = new JPanel();
        painel.setLayout(new BorderLayout());
        painel.setPreferredSize(new Dimension(400, 400));
        painel.setBackground(new Color(20, 20, 20));

        JLabel titulo = new JLabel("Resultados da Simulação");
        titulo.setForeground(Color.GREEN);
        titulo.setFont(new Font("Arial", Font.BOLD, 16));
        titulo.setHorizontalAlignment(SwingConstants.CENTER);
        painel.add(titulo, BorderLayout.NORTH);

        areaResultado = new JTextArea();
        areaResultado.setEditable(false);
        areaResultado.setForeground(Color.WHITE);
        areaResultado.setBackground(new Color(20, 20, 20));
        areaResultado.setFont(new Font("Monospaced", Font.PLAIN, 14));
        areaResultado.setLineWrap(true);
        areaResultado.setWrapStyleWord(true);
        JScrollPane scroll = new JScrollPane(areaResultado);
        painel.add(scroll, BorderLayout.CENTER);

        return painel;
    }

    /**
     * Gera as estrelas para o desenho da Via Láctea.
     * Cada estrela é associada a um objeto Star que contém suas propriedades.
     */
    private void gerarEstrelas() {
        stars.clear();
        int centroX = 800; // Ajustar conforme o tamanho da janela
        int centroY = 500; // Ajustar conforme o tamanho da janela
        double tamanhoGalaxia = 400; // Raio da galáxia

        // Parâmetros para braços espirais
        int numeroBrasos = 4;
        double anguloEntreBrasos = 2 * Math.PI / numeroBrasos;

        Random rand = new Random();

        for (int i = 0; i < NUMERO_ESTRELAS; i++) {
            // Seleciona aleatoriamente um braço
            int braco = rand.nextInt(numeroBrasos);
            double anguloBase = braco * anguloEntreBrasos;

            // Distribuição radial com maior densidade perto do centro
            double raio = rand.nextDouble() * tamanhoGalaxia;

            // Distribuição angular com espiral e dispersão
            double angulo = anguloBase + (raio / tamanhoGalaxia) * 6 * Math.PI + rand.nextGaussian() * 0.3;

            // Coordenadas cartesianas
            double x = centroX + raio * Math.cos(angulo);
            double y = centroY + raio * Math.sin(angulo);

            // Variar o tamanho e cor das estrelas
            double tamanho = 1 + rand.nextDouble() * 2;
            Color cor = gerarCorEstrela();

            stars.add(new Star(x, y, tamanho, cor));
        }
    }

    /**
     * Gera uma cor aleatória para uma estrela, simulando diferentes tipos estelares.
     * @return Cor da estrela
     */
    private Color gerarCorEstrela() {
        // Tipos de estrelas: Azul, Branco, Amarelo, Laranja, Vermelho
        Random rand = new Random();
        int tipo = rand.nextInt(5);
        switch (tipo) {
            case 0:
                return new Color(155, 176, 255); // Azul
            case 1:
                return new Color(255, 255, 255); // Branco
            case 2:
                return new Color(255, 255, 155); // Amarelo
            case 3:
                return new Color(255, 200, 100); // Laranja
            case 4:
                return new Color(255, 150, 150); // Vermelho
            default:
                return Color.WHITE;
        }
    }

    /**
     * Executa a simulação resolvendo a Equação Diferencial Estocástica de Lotka-Volterra.
     * Após a simulação, destaca as estrelas com alta probabilidade de abrigar vida.
     */
    private void executarSimulacao() {
        try {
            // Obter valores das entradas
            alpha = Double.parseDouble(campoAlphaMedia.getText());
            double alphaDesvio = Double.parseDouble(campoAlphaDesvio.getText());

            beta = Double.parseDouble(campoBetaMedia.getText());
            double betaDesvio = Double.parseDouble(campoBetaDesvio.getText());

            gamma = Double.parseDouble(campoGammaMedia.getText());
            double gammaDesvio = Double.parseDouble(campoGammaDesvio.getText());

            sigma = Double.parseDouble(campoSigmaMedia.getText());
            double sigmaDesvio = Double.parseDouble(campoSigmaDesvio.getText());

            numeroSimulacoes = Integer.parseInt(campoNumeroSimulacoes.getText());

            // Inicializar resultados da simulação
            List<Double> resultadosN = new ArrayList<>();

            // Inicializar N
            double N = 0.0;

            // Instância de Random para geração de números aleatórios
            Random rand = new Random();

            // Simulação temporal usando Euler-Maruyama para SDE
            for (int i = 0; i < numeroSimulacoes; i++) {
                // Tempo atual
                double t = i * deltaT;

                // Termo determinístico
                double deterministic = (alpha * N - beta * Math.pow(N, 2) - gamma * Math.pow(N, 3)) * deltaT;

                // Termo estocástico (ruído branco)
                double stochastic = sigma * Math.sqrt(deltaT) * rand.nextGaussian();

                // Atualizar N
                N += deterministic + stochastic;

                // Garantir que N não seja negativo
                N = Math.max(N, 0.0);

                resultadosN.add(N);
            }

            // Processar resultados e destacar estrelas
            processarResultados(resultadosN);

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Por favor, insira valores numéricos válidos.", "Erro de Entrada", JOptionPane.ERROR_MESSAGE);
        }
    }

    /**
     * Processa os resultados da simulação e destaca as estrelas com alta probabilidade de abrigar vida.
     * @param resultadosN Lista dos valores de N ao longo do tempo.
     */
    private void processarResultados(List<Double> resultadosN) {
        // Calcular estatísticas básicas
        double soma = 0.0;
        double somaQuadrado = 0.0;
        double minimo = Double.MAX_VALUE;
        double maximo = Double.MIN_VALUE;

        for (double valor : resultadosN) {
            soma += valor;
            somaQuadrado += valor * valor;
            if (valor < minimo) minimo = valor;
            if (valor > maximo) maximo = valor;
        }

        double media = soma / resultadosN.size();

        double variancia = (somaQuadrado / resultadosN.size()) - (media * media);
        double desvioPadrao = Math.sqrt(variancia);

        // Ordenar resultados para cálculo de percentis
        List<Double> sortedResultados = new ArrayList<>(resultadosN);
        sortedResultados.sort(null);

        double mediana = sortedResultados.get(sortedResultados.size() / 2);
        double p5 = sortedResultados.get((int) (0.05 * sortedResultados.size()));
        double p95 = sortedResultados.get((int) (0.95 * sortedResultados.size()));

        // Definir um limiar para destacar estrelas (ex: N > média)
        double limiar = media;

        // Calcula a proporção de estrelas a serem destacadas
        double proporcaoHabitaveis = Normalizar(media, minimo, maximo);

        // Número de estrelas a destacar
        int numeroHabitaveis = (int) (NUMERO_ESTRELAS * proporcaoHabitaveis);

        // Shuffle das estrelas para seleção aleatória
        List<Star> shuffledStars = new ArrayList<>(stars);
        java.util.Collections.shuffle(shuffledStars, new Random());

        // Destacar as primeiras 'numeroHabitaveis' estrelas
        for (int i = 0; i < NUMERO_ESTRELAS; i++) {
            if (i < numeroHabitaveis) {
                shuffledStars.get(i).setHabitable(true);
            } else {
                shuffledStars.get(i).setHabitable(false);
            }
        }

        // Atualizar o painel de desenho
        repaint();

        // Formatar resultados com 10 dígitos de precisão
        DecimalFormat df = new DecimalFormat("#.##########");
        df.setRoundingMode(RoundingMode.HALF_UP);

        // Exibir resultados
        StringBuilder sb = new StringBuilder();
        sb.append("Parâmetros da Equação Diferencial Estocástica:\n");
        sb.append("α (surgimento): ").append(df.format(alpha)).append("\n");
        sb.append("β (extinção por competição): ").append(df.format(beta)).append("\n");
        sb.append("γ (extinção por interações complexas): ").append(df.format(gamma)).append("\n");
        sb.append("σ (intensidade do ruído): ").append(df.format(sigma)).append("\n\n");

        sb.append("Estatísticas de N:\n");
        sb.append("Número de Simulações: ").append(resultadosN.size()).append("\n");
        sb.append("Média de N: ").append(df.format(media)).append("\n");
        sb.append("Mediana de N: ").append(df.format(mediana)).append("\n");
        sb.append("Desvio Padrão de N: ").append(df.format(desvioPadrao)).append("\n");
        sb.append("Mínimo de N: ").append(df.format(minimo)).append("\n");
        sb.append("Máximo de N: ").append(df.format(maximo)).append("\n");
        sb.append("5º Percentil de N: ").append(df.format(p5)).append("\n");
        sb.append("95º Percentil de N: ").append(df.format(p95)).append("\n");
        sb.append("Proporção de Estrelas Habitáveis: ").append(String.format("%.2f%%", proporcaoHabitaveis * 100)).append("\n");

        areaResultado.setText(sb.toString());
    }

    /**
     * Normaliza um valor dentro de um intervalo.
     * @param valor Valor a ser normalizado
     * @param minimo Valor mínimo do intervalo
     * @param maximo Valor máximo do intervalo
     * @return Valor normalizado entre 0 e 1
     */
    private double Normalizar(double valor, double minimo, double maximo) {
        if (maximo == minimo) {
            return 0.0;
        }
        return (valor - minimo) / (maximo - minimo);
    }
}

class PainelDesenho extends JPanel {
    // Variáveis para exibir as equações
    private String equacao = "Equação Diferencial Estocástica de Lotka-Volterra:\n" +
            "dN = (αN - βN² - γN³)dt + σdW";

    private String[] descricoes = {
            "Onde:",
            "N  = Número de civilizações detectáveis",
            "α  = Taxa de surgimento de civilizações",
            "β  = Taxa de extinção por competição",
            "γ  = Taxa de extinção por interações complexas",
            "σ  = Intensidade do ruído estocástico",
            "dW = Incremento de um processo de Wiener (ruído branco)"
    };

    // Lista de estrelas para desenhar
    private List<Star> stars;
    private Random rand;

    public PainelDesenho(List<Star> stars) {
        this.stars = stars;
        setBackground(Color.BLACK);
        rand = new Random();
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        // Converter para Graphics2D
        Graphics2D g2d = (Graphics2D) g;

        // Antialiasing para melhor qualidade
        g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

        // Desenhar as estrelas
        desenharEstrelas(g2d);

        // Desenhar as equações
        desenharEquacoes(g2d);
    }

    /**
     * Desenha as estrelas na galáxia, destacando aquelas que podem abrigar vida.
     * @param g2d Contexto gráfico
     */
    private void desenharEstrelas(Graphics2D g2d) {
        for (Star estrela : stars) {
            if (estrela.isHabitable()) {
                // Estrela habitável destacada em verde com halo
                g2d.setColor(new Color(0, 255, 0));
                g2d.fill(new Ellipse2D.Double(estrela.getX(), estrela.getY(), estrela.getTamanho(), estrela.getTamanho()));

                // Adicionar halo
                g2d.setStroke(new BasicStroke(1));
                g2d.setColor(new Color(0, 255, 0, 128)); // Verde com transparência
                g2d.draw(new Ellipse2D.Double(estrela.getX() - 2, estrela.getY() - 2, estrela.getTamanho() + 4, estrela.getTamanho() + 4));
            } else {
                // Estrela normal
                g2d.setColor(estrela.getCor());
                g2d.fill(new Ellipse2D.Double(estrela.getX(), estrela.getY(), estrela.getTamanho(), estrela.getTamanho()));
            }
        }
    }

    /**
     * Desenha a equação diferencial e suas descrições na interface.
     * @param g2d Contexto gráfico
     */
    private void desenharEquacoes(Graphics2D g2d) {
        g2d.setColor(Color.CYAN);
        g2d.setFont(new Font("Arial", Font.BOLD, 14));
        int startX = 20;
        int startY = 20;
        int linha = 18;

        g2d.drawString("Modelo Matemático:", startX, startY);
        g2d.setFont(new Font("Arial", Font.PLAIN, 14));
        g2d.drawString(equacao, startX, startY + linha);
        g2d.drawString("", startX, startY + 2 * linha);

        g2d.setFont(new Font("Arial", Font.BOLD, 14));
        for (int i = 0; i < descricoes.length; i++) {
            g2d.drawString(descricoes[i], startX, startY + (3 + i) * linha);
        }
    }
}

/**
 * Classe para representar uma estrela.
 */
class Star {
    private double x, y;
    private double tamanho;
    private Color cor;
    private boolean habitable;

    public Star(double x, double y, double tamanho, Color cor) {
        this.x = x;
        this.y = y;
        this.tamanho = tamanho;
        this.cor = cor;
        this.habitable = false; // Inicialmente, nenhuma estrela é habitável
    }

    public double getX() {
        return x;
    }

    public double getY() {
        return y;
    }

    public double getTamanho() {
        return tamanho;
    }

    public Color getCor() {
        return cor;
    }

    public boolean isHabitable() {
        return habitable;
    }

    public void setHabitable(boolean habitable) {
        this.habitable = habitable;
    }
}
