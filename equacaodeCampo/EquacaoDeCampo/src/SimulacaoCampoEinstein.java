import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.DecimalFormat;
import java.text.DecimalFormatSymbols;
import java.util.Locale;
import java.util.ArrayList;
import java.util.List;
import java.awt.geom.Point2D;

public class SimulacaoCampoEinstein extends JFrame {

    // Campos de entrada
    private JTextField campoMassaSol;
    private JTextField campoMassaTerra;
    private JTextField campoDistancia;
    private JTextField campoConstanteG;
    private JTextField campoVelocidadeLuz;

    // Área de desenho para a simulação gráfica
    private DesenhoSimulacao desenhoSimulacao;

    // DecimalFormat para 10 dígitos de precisão
    private DecimalFormat df;

    // Variáveis para simulação
    private double massaSol = 1.989e30; // Massa do Sol em kg
    private double massaTerra = 5.972e24; // Massa da Terra em kg
    private double distanciaInicial = 1.496e8; // Distância inicial entre Sol e Terra em metros (reduzida para visualização)
    private double G = 6.67430e-11; // Constante gravitacional
    private double c = 299792458; // Velocidade da luz em m/s

    // Variáveis de animação
    private Timer animacao;
    private List<Point2D.Double> trajetoriaTerra; // Lista para armazenar a trajetória da Terra

    // Variáveis físicas da Terra
    private double posX; // Posição X da Terra em metros
    private double posY; // Posição Y da Terra em metros
    private double velX; // Velocidade X da Terra em m/s
    private double velY; // Velocidade Y da Terra em m/s

    public SimulacaoCampoEinstein() {
        // Configuração do DecimalFormat
        df = new DecimalFormat("#.##########", DecimalFormatSymbols.getInstance(Locale.US));

        // Título do programa
        setTitle("Simulação das Equações de Campo de Einstein");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1600, 900);
        setLayout(new BorderLayout());

        // Seção de entrada de variáveis
        JPanel painelEntrada = criarPainelEntrada();

        // Área de desenho para a simulação gráfica
        desenhoSimulacao = new DesenhoSimulacao();
        desenhoSimulacao.setPreferredSize(new Dimension(1200, 800));

        // Inicializar a lista de trajetória
        trajetoriaTerra = new ArrayList<>();
        desenhoSimulacao.setTrajetoria(trajetoriaTerra);

        // Seção de equações e explicação
        JPanel painelLateral = criarPainelLateral();

        // Adicionando ao layout principal
        add(painelEntrada, BorderLayout.WEST);
        add(painelLateral, BorderLayout.EAST);
        add(desenhoSimulacao, BorderLayout.CENTER);

        // Inicializar posições e velocidades da Terra
        inicializarFisica();

        // Iniciar a animação
        iniciarAnimacao();
    }

    /**
     * Inicializa as posições e velocidades da Terra com base nos parâmetros fornecidos.
     */
    private void inicializarFisica() {
        posX = distanciaInicial;
        posY = 0;
        // Velocidade perpendicular para uma órbita elíptica
        velX = 0;
        velY = Math.sqrt(G * massaSol / distanciaInicial) * 0.8; // Fator < 1 para órbita elíptica
    }

    /**
     * Cria o painel de entrada de variáveis.
     */
    private JPanel criarPainelEntrada() {
        JPanel painelEntrada = new JPanel();
        painelEntrada.setLayout(new BoxLayout(painelEntrada, BoxLayout.Y_AXIS));
        painelEntrada.setBorder(BorderFactory.createTitledBorder("Entrada de Variáveis"));
        painelEntrada.setPreferredSize(new Dimension(350, 0));

        // Campo de massa do Sol
        JPanel painelMassaSol = new JPanel(new FlowLayout(FlowLayout.LEFT));
        JLabel rotuloMassaSol = new JLabel("Massa do Sol (kg):");
        campoMassaSol = new JTextField(df.format(massaSol), 15);
        painelMassaSol.add(rotuloMassaSol);
        painelMassaSol.add(campoMassaSol);

        // Campo de massa da Terra
        JPanel painelMassaTerra = new JPanel(new FlowLayout(FlowLayout.LEFT));
        JLabel rotuloMassaTerra = new JLabel("Massa da Terra (kg):");
        campoMassaTerra = new JTextField(df.format(massaTerra), 15);
        painelMassaTerra.add(rotuloMassaTerra);
        painelMassaTerra.add(campoMassaTerra);

        // Campo de distância
        JPanel painelDistancia = new JPanel(new FlowLayout(FlowLayout.LEFT));
        JLabel rotuloDistancia = new JLabel("Distância (m):");
        campoDistancia = new JTextField(df.format(distanciaInicial), 15);
        painelDistancia.add(rotuloDistancia);
        painelDistancia.add(campoDistancia);

        // Campo da constante gravitacional G
        JPanel painelConstanteG = new JPanel(new FlowLayout(FlowLayout.LEFT));
        JLabel rotuloConstanteG = new JLabel("Constante G (m³ kg⁻¹ s⁻²):");
        campoConstanteG = new JTextField(df.format(G), 15);
        painelConstanteG.add(rotuloConstanteG);
        painelConstanteG.add(campoConstanteG);

        // Campo da velocidade da luz c
        JPanel painelVelocidadeLuz = new JPanel(new FlowLayout(FlowLayout.LEFT));
        JLabel rotuloVelocidadeLuz = new JLabel("Velocidade da Luz (m/s):");
        campoVelocidadeLuz = new JTextField(df.format(c), 15);
        painelVelocidadeLuz.add(rotuloVelocidadeLuz);
        painelVelocidadeLuz.add(campoVelocidadeLuz);

        // Botão para atualizar a simulação
        JButton botaoAtualizar = new JButton("Atualizar Simulação");
        botaoAtualizar.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                atualizarSimulacao();
            }
        });

        // Adicionando todos os componentes ao painel de entrada
        painelEntrada.add(painelMassaSol);
        painelEntrada.add(painelMassaTerra);
        painelEntrada.add(painelDistancia);
        painelEntrada.add(painelConstanteG);
        painelEntrada.add(painelVelocidadeLuz);
        painelEntrada.add(Box.createRigidArea(new Dimension(0, 10)));
        painelEntrada.add(botaoAtualizar);

        return painelEntrada;
    }

    /**
     * Cria o painel lateral que contém equações, explicação e autor.
     */
    private JPanel criarPainelLateral() {
        JPanel painelLateral = new JPanel();
        painelLateral.setLayout(new BoxLayout(painelLateral, BoxLayout.Y_AXIS));
        painelLateral.setBorder(BorderFactory.createTitledBorder("Informações"));
        painelLateral.setPreferredSize(new Dimension(350, 0));

        // Seção de equações
        JPanel painelEquacoes = new JPanel();
        painelEquacoes.setLayout(new BoxLayout(painelEquacoes, BoxLayout.Y_AXIS));
        painelEquacoes.setBorder(BorderFactory.createTitledBorder("Equações de Campo de Einstein"));
        painelEquacoes.setPreferredSize(new Dimension(300, 200));

        JLabel rotuloEquacoes = new JLabel("<html><div style='text-align: center;'>"
                + "G<sub>μν</sub> + Λg<sub>μν</sub> = "
                + "(8πG / c<sup>4</sup>) T<sub>μν</sub>"
                + "</div></html>");
        rotuloEquacoes.setFont(new Font("Serif", Font.BOLD, 18));
        painelEquacoes.add(rotuloEquacoes);

        // Seção de explicação com fórmulas matemáticas
        JPanel painelExplicacao = new JPanel();
        painelExplicacao.setLayout(new BoxLayout(painelExplicacao, BoxLayout.Y_AXIS));
        painelExplicacao.setBorder(BorderFactory.createTitledBorder("Sobre o Programa"));
        painelExplicacao.setPreferredSize(new Dimension(300, 300));

        // Uso de HTML para renderizar fórmulas
        JTextPane areaExplicacao = new JTextPane();
        areaExplicacao.setContentType("text/html");
        areaExplicacao.setText("<html>"
                + "<body style='font-family: serif; font-size: 14px;'>"
                + "<p>Esta aplicação simula a curvatura do espaço-tempo causada por objetos massivos, como o Sol e a Terra.</p>"
                + "<p>Insira os valores de massa e distância para visualizar como a curvatura do espaço-tempo é afetada.</p>"
                + "<p>A animação mostra a Terra orbitando o Sol, representando a deformação do espaço-tempo.</p>"
                + "<h3>Fórmulas Utilizadas:</h3>"
                + "<ul>"
                + "<li><b>Velocidade Angular (ω):</b> <br>"
                + "ω = √(G * M / R³)</li>"
                + "<li><b>Curvatura do Espaço-Tempo (K):</b> <br>"
                + "K = G * massa / c²</li>"
                + "</ul>"
                + "</body></html>");
        areaExplicacao.setEditable(false);
        areaExplicacao.setBackground(new Color(240, 240, 240));
        painelExplicacao.add(areaExplicacao);

        // Seção do autor
        JPanel painelAutor = new JPanel();
        painelAutor.setLayout(new BoxLayout(painelAutor, BoxLayout.Y_AXIS));
        painelAutor.setBorder(BorderFactory.createTitledBorder("Autor"));
        painelAutor.setPreferredSize(new Dimension(300, 100));

        JLabel rotuloAutor = new JLabel("Luiz Tiago Wilcke");
        rotuloAutor.setFont(new Font("Serif", Font.PLAIN, 16));
        painelAutor.add(rotuloAutor);

        // Adicionando seções ao painel lateral
        painelLateral.add(painelEquacoes);
        painelLateral.add(Box.createRigidArea(new Dimension(0, 10)));
        painelLateral.add(painelExplicacao);
        painelLateral.add(Box.createRigidArea(new Dimension(0, 10)));
        painelLateral.add(painelAutor);

        return painelLateral;
    }

    /**
     * Atualiza os parâmetros da simulação com base nas entradas do usuário.
     */
    private void atualizarSimulacao() {
        try {
            massaSol = Double.parseDouble(campoMassaSol.getText());
            massaTerra = Double.parseDouble(campoMassaTerra.getText());
            distanciaInicial = Double.parseDouble(campoDistancia.getText());
            G = Double.parseDouble(campoConstanteG.getText());
            c = Double.parseDouble(campoVelocidadeLuz.getText());

            // Validar entradas
            if (massaSol <= 0 || massaTerra <= 0 || distanciaInicial <= 0 || G <= 0 || c <= 0) {
                mostrarAlerta("Erro", "Todos os valores devem ser positivos.");
                return;
            }

            // Atualizar parâmetros na simulação
            desenhoSimulacao.atualizarParametros(massaSol, massaTerra, distanciaInicial, G, c);
            inicializarFisica(); // Reinicializar física com novos parâmetros
            trajetoriaTerra.clear(); // Limpar a trajetória anterior

        } catch (NumberFormatException e) {
            mostrarAlerta("Erro de Formato", "Por favor, insira valores numéricos válidos com até 10 dígitos de precisão.");
        }
    }

    /**
     * Exibe um alerta com o título e a mensagem fornecidos.
     *
     * @param titulo   Título do alerta.
     * @param mensagem Mensagem do alerta.
     */
    private void mostrarAlerta(String titulo, String mensagem) {
        JOptionPane.showMessageDialog(this, mensagem, titulo, JOptionPane.ERROR_MESSAGE);
    }

    /**
     * Inicia a animação da Terra orbitando o Sol.
     */
    private void iniciarAnimacao() {
        // delta_t em segundos (aproximadamente 60 FPS)
        final double delta_t = 1.0 / 60.0;

        animacao = new Timer(16, new ActionListener() { // Aproximadamente 60 FPS
            @Override
            public void actionPerformed(ActionEvent e) {
                animarOrbita(delta_t);
            }
        });
        animacao.start();
    }

    /**
     * Anima a Terra orbitando o Sol e atualiza a representação do espaço-tempo.
     *
     * @param delta_t Intervalo de tempo em segundos.
     */
    private void animarOrbita(double delta_t) {
        // Calcula a distância atual da Terra ao Sol
        double r = Math.sqrt(posX * posX + posY * posY);

        // Calcula a aceleração devido à gravidade
        double aX = -G * massaSol * posX / Math.pow(r, 3);
        double aY = -G * massaSol * posY / Math.pow(r, 3);

        // Atualiza a velocidade da Terra
        velX += aX * delta_t;
        velY += aY * delta_t;

        // Atualiza a posição da Terra
        posX += velX * delta_t;
        posY += velY * delta_t;

        // Adiciona a posição atual à trajetória
        trajetoriaTerra.add(new Point2D.Double(posX, posY));

        // Atualiza a simulação gráfica
        desenhoSimulacao.setPosicaoTerra(posX, posY);
        desenhoSimulacao.repaint();
    }

    /**
     * Classe interna para desenhar a simulação gráfica.
     */
    private class DesenhoSimulacao extends JPanel {

        private double massaSol;
        private double massaTerra;
        private double distancia;
        private double G;
        private double c;
        private double posX;
        private double posY;

        private List<Point2D.Double> trajetoriaTerra; // Lista para armazenar a trajetória da Terra

        // Escalas para representação
        private final double escalaDistancia = 1.0e-6; // pixels/meter
        private final double escalaCurvatura = 1.0e-2; // pixels/meter

        public DesenhoSimulacao() {
            // Inicializa com os valores da classe externa
            this.massaSol = massaSol;
            this.massaTerra = massaTerra;
            this.distancia = distanciaInicial;
            this.G = G;
            this.c = c;
            this.posX = posX;
            this.posY = posY;
            this.trajetoriaTerra = new ArrayList<>();
        }

        /**
         * Define a trajetória da Terra.
         */
        public void setTrajetoria(List<Point2D.Double> trajetoriaTerra) {
            this.trajetoriaTerra = trajetoriaTerra;
        }

        /**
         * Atualiza os parâmetros da simulação.
         */
        public void atualizarParametros(double massaSol, double massaTerra, double distancia, double G, double c) {
            this.massaSol = massaSol;
            this.massaTerra = massaTerra;
            this.distancia = distancia;
            this.G = G;
            this.c = c;
            repaint();
        }

        /**
         * Atualiza a posição da Terra na simulação gráfica.
         */
        public void setPosicaoTerra(double posX, double posY) {
            this.posX = posX;
            this.posY = posY;
        }

        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            desenharSimulacao((Graphics2D) g);
        }

        /**
         * Desenha a simulação gráfica da curvatura do espaço-tempo e a órbita da Terra.
         */
        private void desenharSimulacao(Graphics2D g2d) {
            // Habilitar antialiasing para melhor qualidade gráfica
            g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            // Limpar o fundo
            g2d.setColor(Color.BLACK);
            g2d.fillRect(0, 0, getWidth(), getHeight());

            // Centro do canvas (posição do Sol)
            double centroX = getWidth() / 2.0;
            double centroY = getHeight() / 2.0;

            // Desenhar a malha de espaço-tempo
            desenharMalhaEspacoTempo(g2d, centroX, centroY);

            // Desenhar o Sol
            double raioSolPixel = 30;
            g2d.setColor(Color.YELLOW);
            g2d.fillOval((int) (centroX - raioSolPixel), (int) (centroY - raioSolPixel),
                    (int) (raioSolPixel * 2), (int) (raioSolPixel * 2));

            // Desenhar a trajetória da Terra
            if (trajetoriaTerra.size() > 1) {
                g2d.setColor(Color.WHITE);
                for (int i = 1; i < trajetoriaTerra.size(); i++) {
                    Point2D.Double p1 = trajetoriaTerra.get(i - 1);
                    Point2D.Double p2 = trajetoriaTerra.get(i);
                    int x1 = (int) (p1.x * escalaDistancia + centroX);
                    int y1 = (int) (p1.y * escalaDistancia + centroY);
                    int x2 = (int) (p2.x * escalaDistancia + centroX);
                    int y2 = (int) (p2.y * escalaDistancia + centroY);
                    g2d.drawLine(x1, y1, x2, y2);
                }
            }

            // Calcular posição da Terra em pixels
            int terraX = (int) (posX * escalaDistancia + centroX);
            int terraY = (int) (posY * escalaDistancia + centroY);

            // Desenhar a Terra
            double raioTerraPixel = 15;
            g2d.setColor(Color.BLUE);
            g2d.fillOval(terraX - (int) raioTerraPixel, terraY - (int) raioTerraPixel,
                    (int) (raioTerraPixel * 2), (int) (raioTerraPixel * 2));

            // Desenhar a curvatura do espaço-tempo ao redor do Sol
            double curvaturaSol = calcularCurvatura(massaSol);
            g2d.setColor(new Color(255, 0, 0, 100)); // Vermelho semi-transparente
            g2d.setStroke(new BasicStroke(2));
            g2d.drawOval((int) (centroX - curvaturaSol), (int) (centroY - curvaturaSol),
                    (int) (curvaturaSol * 2), (int) (curvaturaSol * 2));

            // Desenhar a curvatura do espaço-tempo ao redor da Terra
            double curvaturaTerra = calcularCurvatura(massaTerra);
            g2d.setColor(new Color(255, 0, 0, 100)); // Vermelho semi-transparente
            g2d.drawOval((int) (terraX - curvaturaTerra), (int) (terraY - curvaturaTerra),
                    (int) (curvaturaTerra * 2), (int) (curvaturaTerra * 2));

            // Adicionar seta indicando a direção do movimento da Terra
            desenharSeta(g2d, terraX, terraY);
        }

        /**
         * Desenha uma seta indicando a direção do movimento da Terra.
         */
        private void desenharSeta(Graphics2D g2d, double x, double y) {
            // Calcula o ângulo da velocidade atual
            double velocidade = Math.sqrt(velX * velX + velY * velY);
            if (velocidade == 0) return;

            double anguloVelocidade = Math.atan2(velY, velX);

            int tamanhoSeta = 20;
            double setaAngulo = anguloVelocidade;

            int x1 = (int) x;
            int y1 = (int) y;
            int x2 = (int) (x1 + tamanhoSeta * Math.cos(setaAngulo));
            int y2 = (int) (y1 + tamanhoSeta * Math.sin(setaAngulo));

            g2d.setColor(Color.WHITE);
            g2d.setStroke(new BasicStroke(2));
            g2d.drawLine(x1, y1, x2, y2);

            // Desenhar a ponta da seta
            Polygon seta = new Polygon();
            seta.addPoint(x2, y2);
            seta.addPoint((int) (x2 - 5 * Math.cos(setaAngulo - Math.PI / 6)),
                    (int) (y2 - 5 * Math.sin(setaAngulo - Math.PI / 6)));
            seta.addPoint((int) (x2 - 5 * Math.cos(setaAngulo + Math.PI / 6)),
                    (int) (y2 - 5 * Math.sin(setaAngulo + Math.PI / 6)));
            seta.addPoint(x2, y2);
            g2d.fill(seta);
        }

        /**
         * Desenha a malha de espaço-tempo.
         */
        private void desenharMalhaEspacoTempo(Graphics2D g2d, double centroX, double centroY) {
            // Parâmetros da malha
            int linhas = 50;
            int colunas = 50;
            double espacamentoX = getWidth() / (double) colunas;
            double espacamentoY = getHeight() / (double) linhas;

            // Desenhar linhas verticais
            g2d.setColor(new Color(169, 169, 169, 100)); // Cinza semi-transparente
            g2d.setStroke(new BasicStroke(1));
            for (int i = 0; i <= colunas; i++) {
                double x = i * espacamentoX;
                g2d.drawLine((int) x, 0, (int) x, getHeight());
            }

            // Desenhar linhas horizontais
            for (int i = 0; i <= linhas; i++) {
                double y = i * espacamentoY;
                g2d.drawLine(0, (int) y, getWidth(), (int) y);
            }
        }

        /**
         * Calcula uma representação simplificada da curvatura do espaço-tempo baseada na massa.
         *
         * @param massa Massa do corpo em kg.
         * @return Raio da curvatura representada em pixels.
         */
        private double calcularCurvatura(double massa) {
            // Fórmula simplificada para a curvatura: K = G * massa / c^2
            double K = (G * massa) / (c * c);

            // Escala para converter a curvatura em pixels
            return K * escalaCurvatura;
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            SimulacaoCampoEinstein simulacao = new SimulacaoCampoEinstein();
            simulacao.setVisible(true);
        });
    }
}
