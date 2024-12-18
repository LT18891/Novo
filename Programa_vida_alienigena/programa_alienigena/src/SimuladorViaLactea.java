import javax.swing.*;
import javax.swing.border.TitledBorder;
import java.awt.*;
import java.awt.event.*;
import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.Random;
import java.util.concurrent.atomic.AtomicBoolean;
import java.io.*;
import java.util.ArrayList;
import java.util.List;


public class SimuladorViaLactea extends JFrame {

    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	// Componentes da interface gráfica
    private JTextField campoAlfa;
    private JTextField campoPMedio;
    private JTextField campoSigma;
    private JTextField campoDt;
    private JTextField campoNumeroEstrelas;
    private JButton botaoIniciar;
    private JButton botaoPausar;
    private JButton botaoResetar;
    private JButton botaoSalvar;
    private JButton botaoCarregar;
    private JButton botaoVerResultados; // Novo botão para ver resultados
    private JanelaResultados janelaResultados; // Nova janela para resultados
    private PainelGalaxia painelGalaxia;
    private PainelEstatisticas painelEstatisticas;

    // Objeto de simulação
    private Simulacao simulacao;
    private Thread threadSimulacao;
    private AtomicBoolean simulando;

    public SimuladorViaLactea() {
        setTitle("Simulador da Via Láctea e Probabilidade de Vida");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1400, 800);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout());

        simulando = new AtomicBoolean(false);

        // Painel de controle
        JPanel painelControle = new JPanel();
        painelControle.setLayout(new GridLayout(9, 2, 10, 10));
        painelControle.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        // Campos de entrada
        painelControle.add(new JLabel("Alfa (α):"));
        campoAlfa = new JTextField("0.1");
        painelControle.add(campoAlfa);

        painelControle.add(new JLabel("P_médio (Pₘ):"));
        campoPMedio = new JTextField("0.3");
        painelControle.add(campoPMedio);

        painelControle.add(new JLabel("Sigma (σ):"));
        campoSigma = new JTextField("0.05");
        painelControle.add(campoSigma);

        painelControle.add(new JLabel("Dt (Δt):"));
        campoDt = new JTextField("0.1");
        painelControle.add(campoDt);

        painelControle.add(new JLabel("Número de Estrelas:"));
        campoNumeroEstrelas = new JTextField("200");
        painelControle.add(campoNumeroEstrelas);

        // Botões de controle
        botaoIniciar = new JButton("Iniciar Simulação");
        painelControle.add(botaoIniciar);

        botaoPausar = new JButton("Pausar Simulação");
        botaoPausar.setEnabled(false);
        painelControle.add(botaoPausar);

        botaoResetar = new JButton("Resetar Simulação");
        botaoResetar.setEnabled(false);
        painelControle.add(botaoResetar);

        botaoSalvar = new JButton("Salvar Configuração");
        painelControle.add(botaoSalvar);

        botaoCarregar = new JButton("Carregar Configuração");
        painelControle.add(botaoCarregar);
        
        // Novo botão para ver resultados
        botaoVerResultados = new JButton("Ver Resultados");
        botaoVerResultados.setEnabled(false);
        painelControle.add(botaoVerResultados);

        // Área de resultados (não mais necessária aqui, pois estará na nova janela)
        // Removido: JTextArea areaResultados;
        // Removido: JScrollPane scrollResultados;

        add(painelControle, BorderLayout.WEST);

        // Painel gráfico da galáxia
        painelGalaxia = new PainelGalaxia();
        painelGalaxia.setPreferredSize(new Dimension(800, 600));

        // Painel de estatísticas
        painelEstatisticas = new PainelEstatisticas();
        painelEstatisticas.setPreferredSize(new Dimension(600, 200));

        // Painéis combinados
        JPanel painelDireito = new JPanel();
        painelDireito.setLayout(new BorderLayout());
        painelDireito.add(painelGalaxia, BorderLayout.CENTER);
        painelDireito.add(painelEstatisticas, BorderLayout.SOUTH);

        add(painelDireito, BorderLayout.CENTER);

        // Ações dos botões
        botaoIniciar.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                iniciarSimulacao();
            }
        });

        botaoPausar.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                pausarSimulacao();
            }
        });

        botaoResetar.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                resetarSimulacao();
            }
        });

        botaoSalvar.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                salvarConfiguracao();
            }
        });

        botaoCarregar.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                carregarConfiguracao();
            }
        });

        // Ação do novo botão para ver resultados
        botaoVerResultados.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                if (janelaResultados == null) {
                    janelaResultados = new JanelaResultados();
                }
                janelaResultados.atualizarResultados(simulacao);
                janelaResultados.setVisible(true);
            }
        });
    }

    /**
     * Inicia a simulação com os parâmetros fornecidos pelo usuário.
     */
    private void iniciarSimulacao() {
        try {
            // Ler e validar os parâmetros de entrada
            BigDecimal alfa = new BigDecimal(campoAlfa.getText());
            BigDecimal pMedio = new BigDecimal(campoPMedio.getText());
            BigDecimal sigma = new BigDecimal(campoSigma.getText());
            BigDecimal dt = new BigDecimal(campoDt.getText());
            int numeroEstrelas = Integer.parseInt(campoNumeroEstrelas.getText());

            // Desabilitar campos de entrada durante a simulação
            desabilitarCampos(true);

            // Criar e iniciar a simulação
            simulacao = new Simulacao(alfa, pMedio, sigma, dt, numeroEstrelas);
            simulacao.inicializar();

            simulando.set(true);

            // Iniciar thread da simulação
            threadSimulacao = new Thread(new Runnable() {
                @Override
                public void run() {
                    while (simulando.get()) {
                        simulacao.executarPasso();
                        atualizarInterface();
                        try {
                            Thread.sleep(100); // Tempo entre passos (ms)
                        } catch (InterruptedException ex) {
                            Thread.currentThread().interrupt();
                        }
                    }
                }
            });
            threadSimulacao.start();

            botaoIniciar.setEnabled(false);
            botaoPausar.setEnabled(true);
            botaoResetar.setEnabled(true);
            botaoVerResultados.setEnabled(true); // Habilitar botão de ver resultados

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Por favor, insira valores numéricos válidos nos campos.", "Erro de Entrada", JOptionPane.ERROR_MESSAGE);
        }
    }

    /**
     * Pausa ou retoma a simulação.
     */
    private void pausarSimulacao() {
        if (simulando.get()) {
            simulando.set(false);
            botaoPausar.setText("Retomar Simulação");
        } else {
            simulando.set(true);
            threadSimulacao = new Thread(new Runnable() {
                @Override
                public void run() {
                    while (simulando.get()) {
                        simulacao.executarPasso();
                        atualizarInterface();
                        try {
                            Thread.sleep(100); // Tempo entre passos (ms)
                        } catch (InterruptedException ex) {
                            Thread.currentThread().interrupt();
                        }
                    }
                }
            });
            threadSimulacao.start();
            botaoPausar.setText("Pausar Simulação");
        }
    }

    /**
     * Reseta a simulação para o estado inicial.
     */
    private void resetarSimulacao() {
        simulando.set(false);
        try {
            if (threadSimulacao != null) {
                threadSimulacao.join();
            }
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
        }

        if (simulacao != null) {
            simulacao.resetar();
            atualizarInterface();
        }

        // Limpar resultados na janela de resultados
        if (janelaResultados != null) {
            janelaResultados.limparResultados();
        }
        painelEstatisticas.resetar();

        botaoIniciar.setEnabled(true);
        botaoPausar.setEnabled(false);
        botaoPausar.setText("Pausar Simulação");
        botaoResetar.setEnabled(false);
        botaoVerResultados.setEnabled(false); // Desabilitar botão de ver resultados
        desabilitarCampos(false);
    }

    /**
     * Atualiza a interface gráfica com os dados da simulação.
     */
    private void atualizarInterface() {
        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {
                // Atualizar janela de resultados se estiver aberta
                if (janelaResultados != null && janelaResultados.isVisible()) {
                    janelaResultados.atualizarResultados(simulacao);
                }

                // Atualizar painel da galáxia
                painelGalaxia.setEstrelas(simulacao.getPosXEstrelas(), simulacao.getPosYEstrelas(), simulacao.getProbabilidades());

                // Atualizar painel de estatísticas
                painelEstatisticas.atualizar(simulacao.getMediaP(), simulacao.getVarianciaP());
            }
        });
    }

    /**
     * Desabilita ou habilita os campos de entrada.
     *
     * @param desabilitar true para desabilitar, false para habilitar
     */
    private void desabilitarCampos(boolean desabilitar) {
        campoAlfa.setEnabled(!desabilitar);
        campoPMedio.setEnabled(!desabilitar);
        campoSigma.setEnabled(!desabilitar);
        campoDt.setEnabled(!desabilitar);
        campoNumeroEstrelas.setEnabled(!desabilitar);
        botaoSalvar.setEnabled(!desabilitar);
        botaoCarregar.setEnabled(!desabilitar);
    }

    /**
     * Salva a configuração atual em um arquivo.
     */
    private void salvarConfiguracao() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("Salvar Configuração");
        int userSelection = fileChooser.showSaveDialog(this);
        if (userSelection == JFileChooser.APPROVE_OPTION) {
            File arquivo = fileChooser.getSelectedFile();
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(arquivo))) {
                writer.write(campoAlfa.getText() + "\n");
                writer.write(campoPMedio.getText() + "\n");
                writer.write(campoSigma.getText() + "\n");
                writer.write(campoDt.getText() + "\n");
                writer.write(campoNumeroEstrelas.getText() + "\n");
                JOptionPane.showMessageDialog(this, "Configuração salva com sucesso!", "Sucesso", JOptionPane.INFORMATION_MESSAGE);
            } catch (IOException ex) {
                JOptionPane.showMessageDialog(this, "Erro ao salvar configuração.", "Erro", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    /**
     * Carrega uma configuração de um arquivo.
     */
    private void carregarConfiguracao() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("Carregar Configuração");
        int userSelection = fileChooser.showOpenDialog(this);
        if (userSelection == JFileChooser.APPROVE_OPTION) {
            File arquivo = fileChooser.getSelectedFile();
            try (BufferedReader reader = new BufferedReader(new FileReader(arquivo))) {
                campoAlfa.setText(reader.readLine());
                campoPMedio.setText(reader.readLine());
                campoSigma.setText(reader.readLine());
                campoDt.setText(reader.readLine());
                campoNumeroEstrelas.setText(reader.readLine());
                JOptionPane.showMessageDialog(this, "Configuração carregada com sucesso!", "Sucesso", JOptionPane.INFORMATION_MESSAGE);
            } catch (IOException ex) {
                JOptionPane.showMessageDialog(this, "Erro ao carregar configuração.", "Erro", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    /**
     * Classe que representa a simulação estocástica.
     */
    private class Simulacao {
        private BigDecimal alfa;
        private BigDecimal pMedio;
        private BigDecimal sigma;
        private BigDecimal dt;
        private int numeroEstrelas;

        private BigDecimal[] probVidaPlanetas;
        private double[] posXEstrelas;
        private double[] posYEstrelas;

        private Random gerador;

        // Contexto de matemática para precisão
        private MathContext mc = new MathContext(15, RoundingMode.HALF_UP);

        private int passoAtual;
        private List<Double> historicoMedia;
        private List<Double> historicoVariancia;

        public Simulacao(BigDecimal alfa, BigDecimal pMedio, BigDecimal sigma, BigDecimal dt, int numeroEstrelas) {
            this.alfa = alfa;
            this.pMedio = pMedio;
            this.sigma = sigma;
            this.dt = dt;
            this.numeroEstrelas = numeroEstrelas;

            probVidaPlanetas = new BigDecimal[numeroEstrelas];
            posXEstrelas = new double[numeroEstrelas];
            posYEstrelas = new double[numeroEstrelas];
            gerador = new Random();

            passoAtual = 0;
            historicoMedia = new ArrayList<>();
            historicoVariancia = new ArrayList<>();
        }

        /**
         * Inicializa as posições das estrelas e as probabilidades iniciais.
         */
        public void inicializar() {
            Dimension size = painelGalaxia.getPreferredSize();
            double centerX = size.width / 2.0;
            double centerY = size.height / 2.0;
            double maxRaio = size.width / 2.5;

            for (int i = 0; i < numeroEstrelas; i++) {
                // Distribuir estrelas de forma aproximadamente elíptica para simular Via Láctea
                double angulo = 2 * Math.PI * gerador.nextDouble();
                double raio = maxRaio * gerador.nextDouble();
                posXEstrelas[i] = centerX + Math.cos(angulo) * raio;
                posYEstrelas[i] = centerY + Math.sin(angulo) * (raio / 1.5);

                // Probabilidade inicial de vida (valor entre 0 e 1)
                probVidaPlanetas[i] = new BigDecimal(gerador.nextDouble(), mc);
            }

            atualizarEstatisticas();
        }

        /**
         * Executa um passo da simulação para todas as estrelas.
         */
        public void executarPasso() {
            for (int i = 0; i < numeroEstrelas; i++) {
                BigDecimal P = probVidaPlanetas[i];
                // Incremento de Wiener (dW)
                double dW = gerador.nextGaussian() * Math.sqrt(dt.doubleValue());
                BigDecimal dW_bd = new BigDecimal(dW, mc);

                // Calcular dP = alfa*(P_medio - P)*dt + sigma*dW
                BigDecimal termo1 = alfa.multiply(pMedio.subtract(P, mc), mc).multiply(dt, mc);
                BigDecimal termo2 = sigma.multiply(dW_bd, mc);
                BigDecimal dP = termo1.add(termo2, mc);

                // Atualizar P
                P = P.add(dP, mc);

                // Limitar P entre 0 e 1
                if (P.compareTo(BigDecimal.ZERO) < 0) {
                    P = BigDecimal.ZERO;
                }
                if (P.compareTo(BigDecimal.ONE) > 0) {
                    P = BigDecimal.ONE;
                }

                // Arredondar para 10 casas decimais
                P = P.setScale(10, RoundingMode.HALF_UP);
                probVidaPlanetas[i] = P;
            }

            passoAtual++;
            atualizarEstatisticas();
        }

        /**
         * Atualiza as estatísticas de média e variância.
         */
        private void atualizarEstatisticas() {
            double soma = 0.0;
            for (BigDecimal P : probVidaPlanetas) {
                soma += P.doubleValue();
            }
            double media = soma / numeroEstrelas;

            double somaQuadrados = 0.0;
            for (BigDecimal P : probVidaPlanetas) {
                somaQuadrados += Math.pow(P.doubleValue() - media, 2);
            }
            double variancia = somaQuadrados / numeroEstrelas;

            historicoMedia.add(media);
            historicoVariancia.add(variancia);
        }

        /**
         * Reseta a simulação para o estado inicial.
         */
        public void resetar() {
            for (int i = 0; i < numeroEstrelas; i++) {
                probVidaPlanetas[i] = BigDecimal.ZERO;
                posXEstrelas[i] = 0.0;
                posYEstrelas[i] = 0.0;
            }
            passoAtual = 0;
            historicoMedia.clear();
            historicoVariancia.clear();
        }

        public BigDecimal[] getProbabilidades() {
            return probVidaPlanetas;
        }

        public double[] getPosXEstrelas() {
            return posXEstrelas;
        }

        public double[] getPosYEstrelas() {
            return posYEstrelas;
        }

        public int getPassoAtual() {
            return passoAtual;
        }

        public double getMediaP() {
            if (historicoMedia.isEmpty()) return 0.0;
            return historicoMedia.get(historicoMedia.size() - 1);
        }

        public double getVarianciaP() {
            if (historicoVariancia.isEmpty()) return 0.0;
            return historicoVariancia.get(historicoVariancia.size() - 1);
        }
    }

    /**
     * Painel que desenha a representação gráfica da Via Láctea com as estrelas coloridas.
     */
    private class PainelGalaxia extends JPanel {

        private double[] posXEstrelas;
        private double[] posYEstrelas;
        private BigDecimal[] probVidaPlanetas;

        public PainelGalaxia() {
            setBackground(Color.BLACK);
            posXEstrelas = new double[0];
            posYEstrelas = new double[0];
            probVidaPlanetas = new BigDecimal[0];
        }

        /**
         * Define as estrelas a serem desenhadas.
         *
         * @param posX X das estrelas
         * @param posY Y das estrelas
         * @param probabilidades Probabilidade de vida em cada planeta
         */
        public synchronized void setEstrelas(double[] posX, double[] posY, BigDecimal[] probabilidades) {
            this.posXEstrelas = posX;
            this.posYEstrelas = posY;
            this.probVidaPlanetas = probabilidades;
            repaint();
        }

        @Override
        protected synchronized void paintComponent(Graphics g) {
            super.paintComponent(g);

            if (posXEstrelas.length == 0) {
                return; // Nada para desenhar
            }

            Graphics2D g2d = (Graphics2D) g.create();

            // Antialiasing para melhor qualidade gráfica
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            // Desenhar o fundo da galáxia
            desenharFundoGalaxia(g2d);

            // Desenhar as estrelas
            for (int i = 0; i < posXEstrelas.length; i++) {
                BigDecimal P = probVidaPlanetas[i];
                double prob = P.doubleValue();

                // Cor da estrela varia de acordo com a probabilidade de vida
                Color cor = interpolarCores(Color.WHITE, Color.GREEN, (float) prob);
                g2d.setColor(cor);

                // Tamanho da estrela varia ligeiramente com a probabilidade
                int tamanho = (int) (2 + prob * 4);
                // Garantir que as coordenadas estejam dentro do painel
                int x = (int) posXEstrelas[i];
                int y = (int) posYEstrelas[i];
                if (x < 0) x = 0;
                if (y < 0) y = 0;
                if (x > getWidth() - tamanho) x = getWidth() - tamanho;
                if (y > getHeight() - tamanho) y = getHeight() - tamanho;
                g2d.fillOval(x, y, tamanho, tamanho);
            }

            g2d.dispose();
        }

        /**
         * Desenha um fundo elíptico suavizado no centro para simular a concentração de estrelas.
         */
        private void desenharFundoGalaxia(Graphics2D g2d) {
            // Gradiente radial do centro
            int cx = getWidth() / 2;
            int cy = getHeight() / 2;
            float[] dist = {0f, 1f};
            Color[] cores = {new Color(30, 30, 30), new Color(0, 0, 0)};
            RadialGradientPaint paint = new RadialGradientPaint(cx, cy, (float) (Math.min(getWidth(), getHeight()) / 2.0), dist, cores);
            g2d.setPaint(paint);
            g2d.fillRect(0, 0, getWidth(), getHeight());
        }

        /**
         * Interpola linearmente entre duas cores (c1 e c2) dado um fator t entre 0 e 1.
         */
        private Color interpolarCores(Color c1, Color c2, float t) {
            t = Math.max(0f, Math.min(1f, t)); // Garantir que t esteja entre 0 e 1
            int r = (int) (c1.getRed() + t * (c2.getRed() - c1.getRed()));
            int g = (int) (c1.getGreen() + t * (c2.getGreen() - c1.getGreen()));
            int b = (int) (c1.getBlue() + t * (c2.getBlue() - c1.getBlue()));
            return new Color(r, g, b);
        }
    }

    /**
     * Painel que exibe gráficos em tempo real das estatísticas das probabilidades de vida.
     */
    private class PainelEstatisticas extends JPanel {

        private List<Double> historicoMedia;
        private List<Double> historicoVariancia;

        public PainelEstatisticas() {
            historicoMedia = new ArrayList<>();
            historicoVariancia = new ArrayList<>();
            setBackground(Color.DARK_GRAY);
            setBorder(BorderFactory.createTitledBorder(BorderFactory.createLineBorder(Color.BLACK), "Estatísticas", TitledBorder.CENTER, TitledBorder.TOP, new Font("Arial", Font.BOLD, 12), Color.WHITE));
        }

        /**
         * Atualiza os dados das estatísticas.
         *
         * @param media Média atual
         * @param variancia Variância atual
         */
        public synchronized void atualizar(double media, double variancia) {
            historicoMedia.add(media);
            historicoVariancia.add(variancia);
            repaint();
        }

        /**
         * Reseta os dados das estatísticas.
         */
        public synchronized void resetar() {
            historicoMedia.clear();
            historicoVariancia.clear();
            repaint();
        }

        @Override
        protected synchronized void paintComponent(Graphics g) {
            super.paintComponent(g);

            if (historicoMedia.isEmpty()) {
                return; // Nada para desenhar
            }

            Graphics2D g2d = (Graphics2D) g.create();

            // Antialiasing para melhor qualidade gráfica
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            // Definir dimensões do gráfico
            int margem = 40;
            int largura = getWidth() - 2 * margem;
            int altura = getHeight() - 2 * margem;

            // Desenhar eixos
            g2d.setColor(Color.WHITE);
            g2d.drawLine(margem, margem, margem, margem + altura); // Eixo Y
            g2d.drawLine(margem, margem + altura, margem + largura, margem + altura); // Eixo X

            // Determinar o máximo para escalonamento
            double maxY = 1.0; // Probabilidades variam entre 0 e 1
            int numPontos = historicoMedia.size();
            double passoX = (double) largura / (historicoMedia.size() > 1 ? historicoMedia.size() - 1 : 1);

            // Desenhar linha da média
            g2d.setColor(Color.GREEN);
            for (int i = 0; i < historicoMedia.size() - 1; i++) {
                int x1 = margem + (int) (i * passoX);
                int y1 = margem + altura - (int) (historicoMedia.get(i) * altura);
                int x2 = margem + (int) ((i + 1) * passoX);
                int y2 = margem + altura - (int) (historicoMedia.get(i + 1) * altura);
                g2d.drawLine(x1, y1, x2, y2);
            }

            // Desenhar linha da variância
            g2d.setColor(Color.RED);
            for (int i = 0; i < historicoVariancia.size() - 1; i++) {
                int x1 = margem + (int) (i * passoX);
                int y1 = margem + altura - (int) (historicoVariancia.get(i) * altura);
                int x2 = margem + (int) ((i + 1) * passoX);
                int y2 = margem + altura - (int) (historicoVariancia.get(i + 1) * altura);
                g2d.drawLine(x1, y1, x2, y2);
            }

            // Legenda
            g2d.setColor(Color.GREEN);
            g2d.drawString("Média P", margem + 10, margem + 15);
            g2d.setColor(Color.RED);
            g2d.drawString("Variância P", margem + 80, margem + 15);

            g2d.dispose();
        }
    }

    /**
     * Janela que exibe os resultados da simulação.
     */
    private class JanelaResultados extends JFrame {

        private JTextArea areaResultados;

        public JanelaResultados() {
            setTitle("Resultados da Simulação");
            setSize(500, 600);
            setLocationRelativeTo(SimuladorViaLactea.this);
            setLayout(new BorderLayout());

            areaResultados = new JTextArea();
            areaResultados.setEditable(false);
            JScrollPane scrollResultados = new JScrollPane(areaResultados);
            scrollResultados.setBorder(BorderFactory.createTitledBorder("Resultados da Simulação"));

            add(scrollResultados, BorderLayout.CENTER);
        }

        /**
         * Atualiza os resultados na janela.
         *
         * @param simulacao Objeto da simulação
         */
        public void atualizarResultados(Simulacao simulacao) {
            if (simulacao == null) {
                areaResultados.setText("Nenhuma simulação em andamento.");
                return;
            }

            StringBuilder sb = new StringBuilder();
            sb.append(String.format("Passo da Simulação: %d\n", simulacao.getPassoAtual()));
            sb.append(String.format("Média P: %.10f\n", simulacao.getMediaP()));
            sb.append(String.format("Variância P: %.10f\n\n", simulacao.getVarianciaP()));
            sb.append("Probabilidades de Vida em Cada Estrela:\n");
            BigDecimal[] probabilidades = simulacao.getProbabilidades();
            for (int i = 0; i < probabilidades.length; i++) {
                sb.append(String.format("Estrela %d: P = %.10f\n", i + 1, probabilidades[i].doubleValue()));
            }

            areaResultados.setText(sb.toString());
        }

        /**
         * Limpa os resultados na janela.
         */
        public void limparResultados() {
            areaResultados.setText("");
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            SimuladorViaLactea simulador = new SimuladorViaLactea();
            simulador.setVisible(true);
        });
    }
}
