import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.text.DecimalFormat;

public class SimuladorCelulaSolar extends JFrame {

    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	// Variáveis em português
    private JTextField campoIrradiancia;
    private JTextField campoArea;
    private JTextField campoEficiencia;
    private JTextField campoComprimentoOnda; // em nm
    private JTextField campoEnergiaFoton; // pode ser calculada ou inserida
    private JTextField campoTemperatura; // em K
    private JTextField campoVoc; // Tensão de circuito aberto (V)
    private JTextField campoIsc; // Corrente de curto-circuito (A)
    private JTextField campoFF;  // Fator de forma (0 a 1)
    private JTextField campoEg;  // Gap do material (eV)
    
    private JLabel labelResultado;
    private JPanel painelAnimacao;

    private double irradiancia; // W/m²
    private double area; // m²
    private double eficienciaEntrada; // fração (ex: 0.20 = 20%)
    private double comprimentoOnda; // m
    private double energiaFoton; // eV (opcional)
    private double temperatura; // K
    private double Voc; // V
    private double Isc; // A
    private double FF;  // fator de forma
    private double Eg;  // Gap em eV
    
    // Constantes físicas
    private static final double h = 6.62607015e-34; // Constante de Planck (J.s)
    private static final double c = 3e8; // Velocidade da luz (m/s)
    private static final double eV = 1.602176634e-19; // 1 eV em Joules
    private static final double q = 1.602176634e-19; // Carga do elétron (C)
    private static final double kB = 1.380649e-23; // Constante de Boltzmann (J/K)
    
    // Para animação
    private Timer timer;
    private double[] posicoesEletrons;
    private double[] velocidadesEletrons;
    private int numeroEletrons = 20;
    private int alturaValencia = 150;
    private int alturaConducao = 50;
    
    // Ajuste da probabilidade de salto depende da relação entre energia do fóton e Eg
    private double probBaseSalto = 0.01; // probabilidade base
    
    public SimuladorCelulaSolar() {
        super("Simulação de Célula Solar (Fotovoltaica)");
        
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());
        
        // Painel superior com autor e título
        JPanel painelAutor = new JPanel();
        JLabel labelAutor = new JLabel("Autor: Luiz Tiago Wilcke");
        labelAutor.setForeground(Color.BLUE);
        painelAutor.add(labelAutor);
        add(painelAutor, BorderLayout.NORTH);
        
        // Painel central com campos de entrada
        JPanel painelCentral = new JPanel(new GridLayout(13, 2, 5, 5));
        
        painelCentral.add(new JLabel("Irradiância (W/m²):"));
        campoIrradiancia = new JTextField("1000");
        painelCentral.add(campoIrradiancia);
        
        painelCentral.add(new JLabel("Área da Célula (m²):"));
        campoArea = new JTextField("1");
        painelCentral.add(campoArea);
        
        painelCentral.add(new JLabel("Eficiência inicial (0 a 1):"));
        campoEficiencia = new JTextField("0.2");
        painelCentral.add(campoEficiencia);
        
        painelCentral.add(new JLabel("Comprimento de onda (nm):"));
        campoComprimentoOnda = new JTextField("500");
        painelCentral.add(campoComprimentoOnda);
        
        painelCentral.add(new JLabel("Energia do fóton (eV) (opcional):"));
        campoEnergiaFoton = new JTextField("");
        painelCentral.add(campoEnergiaFoton);
        
        painelCentral.add(new JLabel("Temperatura (K):"));
        campoTemperatura = new JTextField("300");
        painelCentral.add(campoTemperatura);
        
        painelCentral.add(new JLabel("Tensão de circuito aberto (Voc) [V]:"));
        campoVoc = new JTextField("0.7");
        painelCentral.add(campoVoc);
        
        painelCentral.add(new JLabel("Corrente de curto-circuito (Isc) [A]:"));
        campoIsc = new JTextField("0.03");
        painelCentral.add(campoIsc);
        
        painelCentral.add(new JLabel("Fator de forma (FF) (0 a 1):"));
        campoFF = new JTextField("0.8");
        painelCentral.add(campoFF);

        painelCentral.add(new JLabel("Gap do material (Eg) [eV]:"));
        campoEg = new JTextField("1.1");
        painelCentral.add(campoEg);
        
        JButton botaoCalcular = new JButton("Calcular");
        painelCentral.add(botaoCalcular);
        
        labelResultado = new JLabel("Resultado:");
        painelCentral.add(labelResultado);
        
        add(painelCentral, BorderLayout.CENTER);
        
        // Painel para exibir equações
        JPanel painelEquacoes = new JPanel(new BorderLayout());
        JEditorPane editorEquacoes = new JEditorPane("text/html", "");
        editorEquacoes.setEditable(false);
        // Adicionar algumas equações mais completas
        editorEquacoes.setText("<html><h3>Equações Utilizadas</h3>"
                + "<p><b>Potência saída a partir de parâmetros da célula:</b><br>"
                + "P_out = Isc × Voc × FF</p>"
                + "<p><b>Eficiência:</b><br>"
                + "η = P_out / (Irradiância × Área)</p>"
                + "<p><b>Energia do fóton:</b><br>"
                + "E_f = h × c / λ</p>"
                + "<p>Se E_f &gt; Eg, fótons podem excitar elétrons da banda de valência para condução.</p>"
                + "<p>h: Const. Planck, c: velocidade da luz, λ: comprimento de onda, Eg: gap do semicondutor.</p>"
                + "</html>");
        painelEquacoes.add(new JScrollPane(editorEquacoes), BorderLayout.CENTER);
        add(painelEquacoes, BorderLayout.EAST);
        
        // Painel de animação
        painelAnimacao = new PainelAnimacao();
        painelAnimacao.setPreferredSize(new Dimension(600, 300));
        add(painelAnimacao, BorderLayout.SOUTH);
        
        // Ação do botão Calcular
        botaoCalcular.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                try {
                    irradiancia = Double.parseDouble(campoIrradiancia.getText().trim());
                    area = Double.parseDouble(campoArea.getText().trim());
                    eficienciaEntrada = Double.parseDouble(campoEficiencia.getText().trim());
                    comprimentoOnda = Double.parseDouble(campoComprimentoOnda.getText().trim()) * 1e-9; // nm para m
                    temperatura = Double.parseDouble(campoTemperatura.getText().trim());
                    Voc = Double.parseDouble(campoVoc.getText().trim());
                    Isc = Double.parseDouble(campoIsc.getText().trim());
                    FF = Double.parseDouble(campoFF.getText().trim());
                    Eg = Double.parseDouble(campoEg.getText().trim()); // eV
                    
                    String energiaTexto = campoEnergiaFoton.getText().trim();
                    double energiaJoules;
                    if(energiaTexto.isEmpty()) {
                        // Calcular E = h*c/λ
                        energiaJoules = h * c / (comprimentoOnda);
                    } else {
                        double energiaFornecida = Double.parseDouble(energiaTexto);
                        // Energia fornecida em eV, converter para Joules
                        energiaJoules = energiaFornecida * eV;
                    }
                    
                    double energiaCalculadaeV = energiaJoules / eV;
                    
                    // Potência de saída realista baseada em Isc, Voc, FF
                    double p_out_real = Isc * Voc * FF;
                    
                    // Eficiência real a partir desses parâmetros
                    double eficienciaReal = p_out_real / (irradiancia * area);
                    
                    // Compare energia do fóton com gap
                    String absorcaoMsg;
                    if (energiaCalculadaeV < Eg) {
                        absorcaoMsg = "Energia do fóton < Eg: poucos elétrons excitados.";
                    } else {
                        absorcaoMsg = "Energia do fóton >= Eg: mais elétrons excitados.";
                    }
                    
                    // Formatar saída com 8 dígitos
                    DecimalFormat df = new DecimalFormat("0.00000000");
                    String resultado = "<html>"
                                     + "Potência saída (Isc×Voc×FF): " + df.format(p_out_real) + " W<br>"
                                     + "Eficiência: " + df.format(eficienciaReal * 100) + " %<br>"
                                     + "Energia do fóton: " + df.format(energiaCalculadaeV) + " eV<br>"
                                     + absorcaoMsg
                                     + "</html>";
                    labelResultado.setText(resultado);
                    
                    // Ajustar a probabilidade de salto com base em Eg
                    ajustarProbabilidadeSalto(energiaCalculadaeV, Eg);
                    
                } catch (NumberFormatException ex) {
                    labelResultado.setText("Erro nos valores fornecidos.");
                }
            }
        });
        
        // Inicializar animação
        initAnimacao();
        
        pack();
        setLocationRelativeTo(null);
        setVisible(true);
    }
    
    private void ajustarProbabilidadeSalto(double Efoton, double Eg) {
        // Se Efoton < Eg, probabilidade menor que a base
        // Se Efoton >= Eg, probabilidade maior
        if (Efoton < Eg) {
            probBaseSalto = 0.005; // menos transições
        } else {
            probBaseSalto = 0.02; // mais transições
        }
    }
    
    private void initAnimacao() {
        posicoesEletrons = new double[numeroEletrons];
        velocidadesEletrons = new double[numeroEletrons];
        for (int i = 0; i < numeroEletrons; i++) {
            posicoesEletrons[i] = Math.random() * 600;
            velocidadesEletrons[i] = (Math.random() - 0.5) * 2;
        }
        
        timer = new Timer(50, new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                atualizarAnimacao();
            }
        });
        timer.start();
    }
    
    private void atualizarAnimacao() {
        // Simula o movimento de "elétrons"
        // Elétrons com velocidade positiva estarão na banda de valência
        // Elétrons com velocidade negativa estarão na banda de condução
        // De forma arbitrária, um fóton pode fazê-los mudar de faixa (inverter o sinal da velocidade)
        
        for (int i = 0; i < numeroEletrons; i++) {
            posicoesEletrons[i] += velocidadesEletrons[i];
            if (posicoesEletrons[i] < 0) posicoesEletrons[i] = 600;
            if (posicoesEletrons[i] > 600) posicoesEletrons[i] = 0;
            
            // De vez em quando, um elétron "salta"
            if (Math.random() < probBaseSalto) {
                double temp = velocidadesEletrons[i];
                velocidadesEletrons[i] = -temp; // inverte velocidade, simulando interação com fóton
            }
        }
        
        painelAnimacao.repaint();
    }
    
    private class PainelAnimacao extends JPanel {
        
        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            
            // Desenhar bandas
            g.setColor(Color.LIGHT_GRAY);
            g.fillRect(0, alturaConducao, getWidth(), 10); // banda de condução
            g.fillRect(0, alturaValencia, getWidth(), 10); // banda de valência
            
            // Desenhar elétrons (círculos vermelhos)
            g.setColor(Color.RED);
            
            for (int i = 0; i < numeroEletrons; i++) {
                int y;
                if (velocidadesEletrons[i] > 0) {
                    y = alturaValencia - 5;
                } else {
                    y = alturaConducao - 5;
                }
                g.fillOval((int)posicoesEletrons[i], y, 10, 10);
            }
            
            // Desenhar fótons (setas amarelas caindo)
            g.setColor(Color.YELLOW);
            for (int x = 50; x < getWidth(); x += 100) {
                g.drawLine(x, 0, x, alturaConducao - 10);
                g.drawLine(x, alturaConducao - 10, x-5, alturaConducao - 5);
                g.drawLine(x, alturaConducao - 10, x+5, alturaConducao - 5);
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new SimuladorCelulaSolar();
        });
    }
}
