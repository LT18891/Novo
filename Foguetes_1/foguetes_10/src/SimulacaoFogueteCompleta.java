import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.text.DecimalFormat;
import java.util.Locale;

public class SimulacaoFogueteCompleta extends JPanel {

    // Constantes físicas
    private static final double G0 = 9.81; // Aceleração da gravidade (m/s²)
    private static final double DT = 0.1;  // Passo de tempo da simulação (s)

    // Variáveis físicas (em português)
    private double massaSeca;        // massa seca do foguete (sem combustível)
    private double massaInicial;     // massa total inicial (massa seca + combustível)
    private double massaCombustivel; // massa de combustível
    private double impulsoEspecifico; // Isp (s)
    private double vazaoMassa;       // taxa de queima do combustível (kg/s)
    private double coefArrasto;      // Coeficiente de arrasto (C_d)
    private double areaFrontal;      // Área frontal do foguete (m²)

    // Estados do foguete
    private double tempo;        // tempo da simulação (s)
    private double velocidade;   // velocidade vertical (m/s)
    private double altura;       // altura do foguete (m)
    private double massaAtual;   // massa atual do foguete
    private boolean emSimulacao; // controla se a simulação está rodando
    private boolean pausado;     // estado de pausa

    // Componentes da UI
    private JTextField campoMassaSeca, campoMassaInicial, campoIsp, campoVazaoMassa, campoCd, campoArea;
    private JLabel labelResultados, labelEquacoes;
    private JButton botaoIniciar, botaoPausar, botaoReiniciar;
    private JPanel painelDesenho;

    private Timer timerAnimacao;

    public SimulacaoFogueteCompleta() {
        setLayout(new BorderLayout());

        // Painel de entrada de dados
        JPanel painelEntrada = new JPanel(new GridLayout(7,2,5,5));

        painelEntrada.setBorder(BorderFactory.createTitledBorder("Parâmetros de Entrada"));

        painelEntrada.add(new JLabel("Massa seca (kg):"));
        campoMassaSeca = new JTextField("1000");
        painelEntrada.add(campoMassaSeca);

        painelEntrada.add(new JLabel("Massa total inicial (kg):"));
        campoMassaInicial = new JTextField("2000");
        painelEntrada.add(campoMassaInicial);

        painelEntrada.add(new JLabel("Impulso Específico (s):"));
        campoIsp = new JTextField("300");
        painelEntrada.add(campoIsp);

        painelEntrada.add(new JLabel("Vazão de massa (kg/s):"));
        campoVazaoMassa = new JTextField("10");
        painelEntrada.add(campoVazaoMassa);

        painelEntrada.add(new JLabel("Coef. de Arrasto (C_d):"));
        campoCd = new JTextField("0.5");
        painelEntrada.add(campoCd);

        painelEntrada.add(new JLabel("Área frontal (m²):"));
        campoArea = new JTextField("1");
        painelEntrada.add(campoArea);

        // Botões de controle
        botaoIniciar = new JButton("Iniciar");
        botaoPausar = new JButton("Pausar");
        botaoReiniciar = new JButton("Reiniciar");

        JPanel painelBotoes = new JPanel(new FlowLayout(FlowLayout.LEFT));
        painelBotoes.add(botaoIniciar);
        painelBotoes.add(botaoPausar);
        painelBotoes.add(botaoReiniciar);

        // Painel de cima (entradas + botões)
        JPanel painelTopo = new JPanel(new BorderLayout());
        painelTopo.add(painelEntrada, BorderLayout.CENTER);
        painelTopo.add(painelBotoes, BorderLayout.SOUTH);

        add(painelTopo, BorderLayout.NORTH);

        // Painel de resultados e equações
        JPanel painelInfo = new JPanel(new BorderLayout());
        painelInfo.setBorder(BorderFactory.createTitledBorder("Informações"));

        labelEquacoes = new JLabel("<html><h3>Equações Utilizadas:</h3>"
                + "<p><b>Equação do Foguete (Tsiolkovsky):</b><br>"
                + "Δv = Isp * g0 * ln(m_inicial / m_final)</p>"
                + "<p><b>Forças:</b><br>F_empuxo = Isp * g0 * (dm/dt)<br>"
                + "F_gravidade = m * g<br>"
                + "F_arrasto = (1/2) * ρ(altitude) * C_d * A * v²</p>"
                + "<p>Densidade do ar (simples): ρ = 1.225 * exp(-altura/8400)</p>"
                + "</html>");

        labelResultados = new JLabel("Resultados: ");

        painelInfo.add(labelEquacoes, BorderLayout.NORTH);
        painelInfo.add(labelResultados, BorderLayout.SOUTH);

        add(painelInfo, BorderLayout.SOUTH);

        // Painel de desenho do foguete
        painelDesenho = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);

                // Desenhar o foguete
                Graphics2D g2 = (Graphics2D) g;
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

                int larguraPainel = getWidth();
                int alturaPainel = getHeight();

                // Transformar altura do foguete em posição no painel
                // Suponhamos: 1 pixel = 1 m (pode ser ajustado se altitude ficar grande)
                // Caso a altitude fique muito grande, pode-se fazer um scaling logarítmico.
                // Aqui vamos manter simples: se altitude > alturaPainel/2, apenas o foguete sai do topo.
                
                // Base do "chão"
                int yBase = alturaPainel - 50; 
                // posição do foguete
                int yFoguete = (int)(yBase - altura);

                // Desenhar terreno/base
                g2.setColor(new Color(139,69,19));
                g2.fillRect(0, yBase, larguraPainel, alturaPainel - yBase);

                // Desenhar foguete
                // Dimensões do foguete em pixels
                int larguraFoguete = 20;
                int alturaFoguete = 60;
                int xFoguete = larguraPainel/2 - larguraFoguete/2;

                // Corpo do foguete
                g2.setColor(Color.GRAY);
                g2.fillRect(xFoguete, yFoguete - alturaFoguete, larguraFoguete, alturaFoguete - 10);

                // Cone da ponta
                Polygon cone = new Polygon();
                cone.addPoint(xFoguete, yFoguete - alturaFoguete);
                cone.addPoint(xFoguete + larguraFoguete, yFoguete - alturaFoguete);
                cone.addPoint(xFoguete + larguraFoguete/2, yFoguete - alturaFoguete - 10);
                g2.setColor(Color.RED);
                g2.fillPolygon(cone);

                // Aletas
                int aletaAltura = 10;
                int aletaLargura = 8;
                g2.setColor(Color.BLUE);
                // Aleta esquerda
                Polygon aletaEsq = new Polygon();
                aletaEsq.addPoint(xFoguete, yFoguete - 10);
                aletaEsq.addPoint(xFoguete - aletaLargura, yFoguete);
                aletaEsq.addPoint(xFoguete, yFoguete);
                g2.fillPolygon(aletaEsq);

                // Aleta direita
                Polygon aletaDir = new Polygon();
                aletaDir.addPoint(xFoguete + larguraFoguete, yFoguete - 10);
                aletaDir.addPoint(xFoguete + larguraFoguete + aletaLargura, yFoguete);
                aletaDir.addPoint(xFoguete + larguraFoguete, yFoguete);
                g2.fillPolygon(aletaDir);

                // Chama do motor se ainda houver empuxo
                if (massaCombustivel > 0 && emSimulacao && !pausado) {
                    g2.setColor(Color.ORANGE);
                    g2.fillOval(xFoguete, yFoguete, larguraFoguete, 15);
                }

                // Desenhar algumas linhas de referência
                g2.setColor(Color.LIGHT_GRAY);
                for (int i = 0; i < alturaPainel; i += 100) {
                    g2.drawLine(0, i, larguraPainel, i);
                }
            }
        };

        painelDesenho.setBackground(Color.CYAN);
        add(painelDesenho, BorderLayout.CENTER);

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
                pausarOuContinuar();
            }
        });

        botaoReiniciar.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                reiniciarSimulacao();
            }
        });

        // Timer para atualização da animação
        timerAnimacao = new Timer((int)(DT*1000), new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                if (emSimulacao && !pausado) {
                    atualizarEstado();
                    painelDesenho.repaint();
                    atualizarResultados();
                }
            }
        });
    }

    private void iniciarSimulacao() {
        try {
            // Ler valores dos campos
            massaSeca = Double.parseDouble(campoMassaSeca.getText());
            massaInicial = Double.parseDouble(campoMassaInicial.getText());
            impulsoEspecifico = Double.parseDouble(campoIsp.getText());
            vazaoMassa = Double.parseDouble(campoVazaoMassa.getText());
            coefArrasto = Double.parseDouble(campoCd.getText());
            areaFrontal = Double.parseDouble(campoArea.getText());

            // Verificação básica
            if (massaInicial < massaSeca) {
                JOptionPane.showMessageDialog(this, "Massa inicial deve ser maior que massa seca.", "Erro", JOptionPane.ERROR_MESSAGE);
                return;
            }

            // Estado inicial
            tempo = 0.0;
            velocidade = 0.0;
            altura = 0.0;
            massaCombustivel = massaInicial - massaSeca;
            massaAtual = massaInicial;
            emSimulacao = true;
            pausado = false;

            timerAnimacao.start();
            atualizarResultados();

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Insira valores numéricos válidos.", "Erro", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void pausarOuContinuar() {
        if (!emSimulacao) return;
        pausado = !pausado;
        if (pausado) {
            botaoPausar.setText("Continuar");
        } else {
            botaoPausar.setText("Pausar");
        }
    }

    private void reiniciarSimulacao() {
        emSimulacao = false;
        pausado = false;
        timerAnimacao.stop();
        // Restaurar estado inicial nos campos e variáveis
        altura = 0.0;
        velocidade = 0.0;
        tempo = 0.0;
        massaAtual = 0.0;
        massaCombustivel = 0.0;
        painelDesenho.repaint();
        atualizarResultados();
        botaoPausar.setText("Pausar");
    }

    private void atualizarEstado() {
        // Enquanto houver combustível, há empuxo
        double F_empuxo = 0.0;
        double massaQueimada = 0.0;

        if (massaCombustivel > 0) {
            // Queima de combustível neste intervalo de tempo
            massaQueimada = vazaoMassa * DT;
            if (massaQueimada > massaCombustivel) {
                massaQueimada = massaCombustivel;
            }
            massaCombustivel -= massaQueimada;
            massaAtual = massaSeca + massaCombustivel;

            F_empuxo = impulsoEspecifico * G0 * (massaQueimada/DT);
        } else {
            // Sem combustível
            massaAtual = massaSeca; 
        }

        // Força da gravidade
        double F_gravidade = massaAtual * G0;

        // Densidade do ar variando com altitude (modelo exponencial simplificado)
        // ρ = 1.225 * exp(-altura/8400)
        double densidadeAr = 1.225 * Math.exp(-altura/8400.0);

        // Força de arrasto
        double F_arrasto = 0.5 * densidadeAr * coefArrasto * areaFrontal * velocidade * velocidade;
        // Direção do arrasto
        F_arrasto *= Math.signum(velocidade);

        // Força resultante = F_empuxo - mg - arrasto (arrasto é contra o sentido do movimento)
        double F_res = F_empuxo - F_gravidade - Math.abs(F_arrasto);

        if (velocidade < 0) {
            // Se velocidade negativa (caindo), arrasto aponta para cima
            // Já aplicamos abs acima e subtraímos, mas na verdade neste caso:
            // Quando descendo, F_arrasto aponta para cima, então a resultante ficaria:
            // F_res = F_empuxo - mg + arrasto  (porque arrasto seria contra o movimento negativo)
            // Ajustaremos aqui:
            F_res = F_empuxo - F_gravidade + Math.abs(F_arrasto);
        }

        // Aceleração
        double a = F_res / massaAtual;

        // Atualizar velocidade e posição
        velocidade += a * DT;
        altura += velocidade * DT;
        tempo += DT;

        // Se o foguete cair abaixo da base, parar simulação
        if (altura <= 0 && tempo > 0 && velocidade <= 0) {
            altura = 0;
            emSimulacao = false;
        }
    }

    private void atualizarResultados() {
        DecimalFormat df = new DecimalFormat("#.##########"); // 10 dígitos de precisão
        df.setDecimalSeparatorAlwaysShown(false);
        df.setGroupingUsed(false);

        String texto = "<html><b>Resultados:</b><br>" +
                "Tempo (s): " + df.format(tempo) + "<br>" +
                "Altura (m): " + df.format(altura) + "<br>" +
                "Velocidade (m/s): " + df.format(velocidade) + "<br>" +
                "Massa Atual (kg): " + df.format(massaAtual) + "<br>" +
                "Combustível Restante (kg): " + df.format(massaCombustivel) + "<br>" +
                (emSimulacao ? (pausado ? "<i>Simulação Pausada</i>" : "<i>Simulação em Andamento</i>") : "<i>Simulação Encerrada</i>") +
                "</html>";
        labelResultados.setText(texto);
    }

    public static void main(String[] args) {
        Locale.setDefault(Locale.US);
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("Simulação de Lançamento de Foguete - Completa");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setSize(900,700);
            frame.setLocationRelativeTo(null);
            frame.add(new SimulacaoFogueteCompleta());
            frame.setVisible(true);
        });
    }
}
