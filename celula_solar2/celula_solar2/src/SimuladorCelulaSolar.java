import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;


public class SimuladorCelulaSolar extends JFrame {

    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	//======================= VARIÁVEIS DE INTERFACE ============================
    private JTextField campoIrradiancia;
    private JTextField campoArea;
    private JTextField campoEficienciaInicial;
    private JTextField campoComprimentoOnda;   // nm
    private JTextField campoEnergiaFoton;      // eV opcional
    private JTextField campoTemperatura;       // K
    private JTextField campoVoc;               // V
    private JTextField campoIsc;               // A
    private JTextField campoFF;                // fator de forma (0-1)
    private JTextField campoEg;                // gap (eV)
    private JTextField campoDopagem;           // cm^-3 doping
    private JTextField campoMassaEletron;      // massa efetiva do elétron (em unidades da massa do elétron)
    private JTextField campoMassaBuraco;       // massa efetiva do buraco
    private JTextField campoN0;                // densidade intrínseca (cm^-3) ou similar
    private JTextField campoCoefAbsorcao;      // coeficiente de absorção simplificado
    private JTextArea  areaResultados;         // área grande para mostrar resultados detalhados

    private JLabel labelResultado;
    private JPanel painelAnimacao;
    private PainelBandas painelBandas;

    //======================= VARIÁVEIS FÍSICAS E CONSTANTES ====================
    private double irradiancia; // W/m²
    private double area; // m²
    private double eficienciaInicial; // fração
    private double comprimentoOnda; // m
    private double energiaFotonEv;   // eV
    private double temperatura;      // K
    private double Voc;              // V
    private double Isc;              // A
    private double FF;               // fator de forma
    private double Eg;               // eV gap
    private double doping;           // cm^-3
    private double me;               // massa efetiva do elétron (em m_e)
    private double mh;               // massa efetiva do buraco
    private double N0;               // densidade intrínseca (cm^-3) ou nível base
    private double alpha;            // coeficiente de absorção (simplificado)
    
    // Constantes físicas
    private static final double h = 6.62607015e-34; // Const. Planck (J*s)
    private static final double c = 3e8;             // Velocidade da luz (m/s)
    private static final double q = 1.602176634e-19; // Carga do elétron (C)
    private static final double kB = 1.380649e-23;   // Constante de Boltzmann (J/K)
    private static final double eV_J = 1.602176634e-19; // J por eV
    private static final double m0 = 9.10938356e-31; // massa do elétron livre (kg)

    // Para animação
    private Timer timer;
    private int numeroParticulas = 30; // número de elétrons/buracos representados
    private List<Particula> particulas;
    private double probBaseSalto = 0.01; // probabilidade base de salto
    
    // Alturas das bandas no painel de animação
    private int alturaValencia = 200;
    private int alturaConducao = 50;

    //======================= CLASSES INTERNAS DE APOIO =========================
    
    // Classe para representar uma partícula (elétron ou buraco)
    private class Particula {
        double x;
        double y;
        double vx;
        double vy;
        boolean isEletron; // true: elétron, false: buraco
        
        Particula(boolean isEletron) {
            this.isEletron = isEletron;
            this.x = Math.random() * 600;
            if (isEletron) {
                // Elétron começa na banda de valência ou condução dependendo de algo
                this.y = (Math.random() < 0.5) ? alturaValencia - 5 : alturaConducao - 5;
            } else {
                // Buraco começa próximo à valência, mas em posição aleatória
                this.y = alturaValencia + 15; 
            }
            this.vx = (Math.random() - 0.5) * 2;
            this.vy = 0;
        }
    }

    // Painel de animação principal
    private class PainelAnimacao extends JPanel {
        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);

            // Desenhar bandas
            g.setColor(Color.LIGHT_GRAY);
            g.fillRect(0, alturaConducao, getWidth(), 10); // banda de condução
            g.fillRect(0, alturaValencia, getWidth(), 10); // banda de valência

            // Desenhar particulas: elétrons (vermelhos), buracos (azuis)
            for (Particula p : particulas) {
                if (p.isEletron) {
                    g.setColor(Color.RED);
                } else {
                    g.setColor(Color.BLUE);
                }
                g.fillOval((int) p.x, (int) p.y, 8, 8);
            }

            // Desenhar fótons (setas amarelas caindo de cima)
            g.setColor(Color.YELLOW);
            for (int x = 50; x < getWidth(); x += 100) {
                g.drawLine(x, 0, x, alturaConducao - 10);
                g.drawLine(x, alturaConducao - 10, x - 5, alturaConducao - 5);
                g.drawLine(x, alturaConducao - 10, x + 5, alturaConducao - 5);
            }

            // Mostra talvez uma legenda
            g.setColor(Color.BLACK);
            g.drawString("Elétrons (vermelho) e Buracos (azul)", 10, getHeight() - 10);
        }
    }

    // Painel para mostrar banda e nível de Fermi (meramente ilustrativo)
    private class PainelBandas extends JPanel {
        private double fermiLevel = 0.0; // nível de fermi relativo
        private double EgLocal = 1.1;    // gap local (pode ser atualizado)
        
        @Override
        protected void paintComponent(Graphics g) {
            super.paintComponent(g);
            
            int w = getWidth();
            int h = getHeight();
            
            // Desenhar fundo
            g.setColor(Color.WHITE);
            g.fillRect(0, 0, w, h);
            
            // Desenhar banda de valência (uma caixa)
            g.setColor(Color.PINK);
            g.fillRect(50, h/2 + 50, w - 100, 20);
            g.setColor(Color.BLACK);
            g.drawString("Banda de Valência", 60, h/2 + 45);
            
            // Desenhar banda de condução
            g.setColor(Color.CYAN);
            g.fillRect(50, h/2 - 50, w - 100, 20);
            g.setColor(Color.BLACK);
            g.drawString("Banda de Condução", 60, h/2 - 55);
            
            // Desenhar gap
            g.setColor(Color.BLACK);
            g.drawLine(50, h/2 - 30, 50, h/2 + 30);
            g.drawString("Eg = " + new DecimalFormat("0.00").format(EgLocal) + " eV", 60, h/2);
            
            // Desenhar nível de Fermi (linha pontilhada)
            g.setColor(Color.MAGENTA);
            int fermiPos = h/2; 
            g.drawLine(50, fermiPos, w - 50, fermiPos);
            g.drawString("Nível de Fermi (aprox.)", 60, fermiPos - 5);
            
            // Desenhar dopantes como pontos verdes se doping > 0
            g.setColor(Color.GREEN.darker());
            int numDopantes = (int)Math.min(50, doping/1e16); // número simbólico
            for (int i = 0; i < numDopantes; i++) {
                int dx = 60 + (int)(Math.random()*(w-120));
                int dy = h/2 + 60 + (int)(Math.random()*40);
                g.fillOval(dx, dy, 5, 5);
            }
            g.drawString("Dopantes (verdes), nº simbólico: " + numDopantes, 60, h - 20);
        }
        
        public void setEg(double Eg) {
            this.EgLocal = Eg;
            repaint();
        }
    }

    //======================= CONSTRUTOR E INTERFACE ============================
    public SimuladorCelulaSolar() {
        super("Simulação de Célula Solar (Fotovoltaica) - Avançado");
        
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());

        // Painel superior com autor e título
        JPanel painelAutor = new JPanel();
        JLabel labelAutor = new JLabel("Autor: Luiz Tiago Wilcke");
        labelAutor.setForeground(Color.BLUE);
        painelAutor.add(labelAutor);
        add(painelAutor, BorderLayout.NORTH);
        
        // Painel central com parâmetros
        JPanel painelCentral = new JPanel(new GridLayout(16, 2, 5, 5));
        
        painelCentral.add(new JLabel("Irradiância (W/m²):"));
        campoIrradiancia = new JTextField("1000");
        painelCentral.add(campoIrradiancia);
        
        painelCentral.add(new JLabel("Área da Célula (m²):"));
        campoArea = new JTextField("1");
        painelCentral.add(campoArea);
        
        painelCentral.add(new JLabel("Eficiência inicial (0 a 1):"));
        campoEficienciaInicial = new JTextField("0.2");
        painelCentral.add(campoEficienciaInicial);
        
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
        
        painelCentral.add(new JLabel("Fator de forma (FF) (0-1):"));
        campoFF = new JTextField("0.8");
        painelCentral.add(campoFF);

        painelCentral.add(new JLabel("Gap do material (Eg) [eV]:"));
        campoEg = new JTextField("1.1");
        painelCentral.add(campoEg);
        
        painelCentral.add(new JLabel("Dopagem (cm^-3):"));
        campoDopagem = new JTextField("1e16");
        painelCentral.add(campoDopagem);
        
        painelCentral.add(new JLabel("Massa efetiva do elétron (m*/m0):"));
        campoMassaEletron = new JTextField("0.3");
        painelCentral.add(campoMassaEletron);
        
        painelCentral.add(new JLabel("Massa efetiva do buraco (m*/m0):"));
        campoMassaBuraco = new JTextField("0.5");
        painelCentral.add(campoMassaBuraco);
        
        painelCentral.add(new JLabel("Densidade intrínseca (N0) [cm^-3]:"));
        campoN0 = new JTextField("1e10");
        painelCentral.add(campoN0);
        
        painelCentral.add(new JLabel("Coef. Absorção (alpha) [1/m]:"));
        campoCoefAbsorcao = new JTextField("1e6");
        painelCentral.add(campoCoefAbsorcao);
        
        JButton botaoCalcular = new JButton("Calcular");
        painelCentral.add(botaoCalcular);
        
        labelResultado = new JLabel("Resultado rápido:");
        painelCentral.add(labelResultado);
        
        add(painelCentral, BorderLayout.CENTER);
        
        // Painel à direita para equações
        JPanel painelEquacoes = new JPanel(new BorderLayout());
        JEditorPane editorEquacoes = new JEditorPane("text/html", "");
        editorEquacoes.setEditable(false);
        
        // Tentando "renderizar" fórmulas HTML simples
        // Nota: Para renderização de alta qualidade, seria necessário usar algo como MathJax ou JLaTeXMath.
        // Aqui usamos HTML básico com super/subscripts e caracteres especiais.
        editorEquacoes.setText("<html><h3>Equações Utilizadas</h3>"
                + "<p><b>Energia do fóton:</b><br>E<sub>f</sub> = h c / λ</p>"
                + "<p><b>Densidade de portadores:</b><br>n ~ N<sub>0</sub> exp(-E<sub>g</sub>/(k<sub>B</sub>T))</p>"
                + "<p><b>Corrente do diodo (modelo simplificado):</b><br>I = I<sub>0</sub>[exp(qV/(k<sub>B</sub>T))-1]</p>"
                + "<p><b>Potência saída:</b><br>P = I × V (no ponto de máxima potência)</p>"
                + "<p><b>Eficiência:</b><br>η = P<sub>máx</sub> / (Irradiância × Área)</p>"
                + "<p><b>Fator de forma (FF):</b><br>FF = (P<sub>máx</sub> / (I<sub>sc</sub> V<sub>oc</sub>))</p>"
                + "<p>As expressões são simplificadas e servem apenas para ilustração.</p>"
                + "</html>");
        painelEquacoes.add(new JScrollPane(editorEquacoes), BorderLayout.CENTER);
        
        add(painelEquacoes, BorderLayout.EAST);
        
        // Painel inferior com animações
        JPanel painelInferior = new JPanel(new BorderLayout());
        
        painelAnimacao = new PainelAnimacao();
        painelAnimacao.setPreferredSize(new Dimension(600, 300));
        painelInferior.add(painelAnimacao, BorderLayout.CENTER);
        
        painelBandas = new PainelBandas();
        painelBandas.setPreferredSize(new Dimension(400, 300));
        painelInferior.add(painelBandas, BorderLayout.EAST);
        
        add(painelInferior, BorderLayout.SOUTH);

        // Área de resultados detalhados
        areaResultados = new JTextArea(10, 80);
        areaResultados.setEditable(false);
        add(new JScrollPane(areaResultados), BorderLayout.WEST);

        // Ação do botão Calcular
        botaoCalcular.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                calcularResultados();
            }
        });
        
        // Inicializar animação
        initAnimacao();
        
        pack();
        setLocationRelativeTo(null);
        setVisible(true);
    }

    //======================= MÉTODOS DE CÁLCULO ===============================
    private void calcularResultados() {
        try {
            irradiancia = Double.parseDouble(campoIrradiancia.getText().trim());
            area = Double.parseDouble(campoArea.getText().trim());
            eficienciaInicial = Double.parseDouble(campoEficienciaInicial.getText().trim());
            double lambdaNm = Double.parseDouble(campoComprimentoOnda.getText().trim());
            comprimentoOnda = lambdaNm * 1e-9; // nm -> m
            temperatura = Double.parseDouble(campoTemperatura.getText().trim());
            Voc = Double.parseDouble(campoVoc.getText().trim());
            Isc = Double.parseDouble(campoIsc.getText().trim());
            FF = Double.parseDouble(campoFF.getText().trim());
            Eg = Double.parseDouble(campoEg.getText().trim());
            doping = Double.parseDouble(campoDopagem.getText().trim());
            me = Double.parseDouble(campoMassaEletron.getText().trim());
            mh = Double.parseDouble(campoMassaBuraco.getText().trim());
            N0 = Double.parseDouble(campoN0.getText().trim());
            alpha = Double.parseDouble(campoCoefAbsorcao.getText().trim());
            
            String energiaTexto = campoEnergiaFoton.getText().trim();
            double energiaJoules;
            if (energiaTexto.isEmpty()) {
                energiaJoules = h * c / comprimentoOnda;
            } else {
                double energiaFornecida = Double.parseDouble(energiaTexto);
                // Energia fornecida em eV, converter para Joules
                energiaJoules = energiaFornecida * eV_J;
            }
            
            energiaFotonEv = energiaJoules / eV_J;
            
            // Cálculo da densidade de portadores (muito simplificado)
            // Aproximação: n ~ N0 * exp(-Eg/(kB*T)/eV_J) 
            // (Precisaríamos converter Eg e kB*T em mesmas unidades)
            double kBT_eV = (kB * temperatura) / eV_J;
            double n = N0 * Math.exp(-Eg / (kBT_eV)); 
            
            // Ajuste da probabilidade de salto com base em Efóton e Eg
            ajustarProbabilidadeSalto(energiaFotonEv, Eg, doping, n);

            // Potência teórica inicial: P_out = Isc * Voc * FF
            double p_out = Isc * Voc * FF;

            // Eficiência resultante:
            double eficiencia = p_out / (irradiancia * area);
            
            // Vamos fazer também uma varredura simples I-V para obter Pmax (só para ilustrar)
            // Modelo simplificado do diodo: I = Isc - I0[exp(qV/(kBT))-1]
            // I0 estimado: I0 ~ Isc / (exp(qVoc/(kBT)) - 1)
            double I0 = Isc / (Math.exp((q*Voc)/(kB*temperatura))-1);
            
            double vMax = Voc; 
            double passos = 100;
            double passoV = vMax/passos;
            double pmax = 0;
            double vmp = 0, imp = 0;
            for (int i=0; i<=passos; i++) {
                double V = i*passoV;
                double I = Isc - I0*(Math.exp((q*V)/(kB*temperatura))-1);
                double P = V * I;
                if (P > pmax) {
                    pmax = P;
                    vmp = V;
                    imp = I;
                }
            }

            double FFcalc = pmax/(Isc*Voc);
            double eficienciaCalc = pmax/(irradiancia*area);

            // Montar resultado detalhado
            DecimalFormat df = new DecimalFormat("0.00000000");
            StringBuilder sb = new StringBuilder();
            sb.append("=== Resultados do Cálculo ===\n");
            sb.append("Irradiância: ").append(df.format(irradiancia)).append(" W/m²\n");
            sb.append("Área: ").append(df.format(area)).append(" m²\n");
            sb.append("Temperatura: ").append(temperatura).append(" K\n");
            sb.append("Voc: ").append(Voc).append(" V\n");
            sb.append("Isc: ").append(Isc).append(" A\n");
            sb.append("FF (informado): ").append(FF).append("\n");
            sb.append("Eg: ").append(Eg).append(" eV\n");
            sb.append("Dopagem: ").append(doping).append(" cm^-3\n");
            sb.append("Massa efetiva elétron: ").append(me).append(" m0\n");
            sb.append("Massa efetiva buraco: ").append(mh).append(" m0\n");
            sb.append("N0: ").append(N0).append(" cm^-3\n");
            sb.append("alpha: ").append(alpha).append(" 1/m\n");
            
            sb.append("Energia do fóton: ").append(df.format(energiaFotonEv)).append(" eV\n");
            sb.append("Densidade de portadores (aprox): ").append(df.format(n)).append(" cm^-3\n");
            
            sb.append("\nCálculo rápido (Isc*Voc*FF):\n");
            sb.append("P_out: ").append(df.format(p_out)).append(" W\n");
            sb.append("Eficiência inicial: ").append(df.format(eficiencia*100)).append(" %\n");
            
            sb.append("\nCálculo via varredura I-V:\n");
            sb.append("Pmax encontrado: ").append(df.format(pmax)).append(" W\n");
            sb.append("Vmp: ").append(df.format(vmp)).append(" V, Imp: ").append(df.format(imp)).append(" A\n");
            sb.append("FF (calculado): ").append(df.format(FFcalc)).append("\n");
            sb.append("Eficiência (calculada): ").append(df.format(eficienciaCalc*100)).append(" %\n");
            
            sb.append("\nCondição de absorção:\n");
            if (energiaFotonEv < Eg) {
                sb.append("Energia do fóton < Eg => poucos elétrons excitados.\n");
            } else {
                sb.append("Energia do fóton >= Eg => mais elétrons excitados.\n");
            }

            labelResultado.setText("<html>Resultado rápido:<br>P_out: " + df.format(p_out) + " W<br>Eficiência: "
                                    + df.format(eficiencia*100) + " %</html>");
            areaResultados.setText(sb.toString());
            
            // Atualizar painel de bandas
            painelBandas.setEg(Eg);

        } catch (NumberFormatException ex) {
            labelResultado.setText("Erro nos valores fornecidos.");
            areaResultados.setText("Erro nos valores fornecidos: " + ex.getMessage());
        }
    }

    private void ajustarProbabilidadeSalto(double Efoton, double Eg, double doping, double n) {
        // Ajustar probabilidade de salto na animação de acordo com parâmetros
        // Se Efoton < Eg, diminuir
        // Se Efoton >= Eg, aumentar
        double base = 0.01;
        if (Efoton < Eg) {
            base = 0.005;
        } else {
            base = 0.02;
        }
        
        // Considerar doping: quanto maior a dopagem, maior a prob de interações
        // mas também depende da densidade intrínseca n
        double factorDoping = 1.0 + Math.log10(doping/1e16+1)*0.01;
        double factorCarrier = 1.0 + Math.log10(n/1e10+1)*0.01;
        
        probBaseSalto = base * factorDoping * factorCarrier;
        if (probBaseSalto > 0.05) probBaseSalto = 0.05; // limita
    }

    //======================= ANIMAÇÃO =========================================
    private void initAnimacao() {
        particulas = new ArrayList<>();
        for (int i = 0; i < numeroParticulas; i++) {
            // Alternar entre elétron e buraco
            boolean isEletron = (i%2==0);
            particulas.add(new Particula(isEletron));
        }

        timer = new Timer(50, new ActionListener() {
            public void actionPerformed(ActionEvent e) {
                atualizarAnimacao();
            }
        });
        timer.start();
    }

    private void atualizarAnimacao() {
        // Atualizar posições das partículas
        for (Particula p : particulas) {
            p.x += p.vx;
            p.y += p.vy;
            
            // Limites laterais
            if (p.x < 0) p.x = 600;
            if (p.x > 600) p.x = 0;

            // Se for elétron, ele está em uma das bandas
            // Banda de condução: ~alturaConducao, banda de valência: ~alturaValencia
            // Se for buraco, fica abaixo da valência (mais embaixo)
            
            // Chance de saltar de banda:
            // Elétron: se na valência (y ~ alturaValencia - 5), pode saltar para condução (y ~ alturaConducao - 5)
            // ou vice-versa, dependendo da probabilidade
            if (p.isEletron) {
                if (Math.random() < probBaseSalto) {
                    if (Math.abs(p.y - (alturaValencia - 5)) < 10) {
                        // Salto valência -> condução
                        p.y = alturaConducao - 5;
                    } else {
                        // Salto condução -> valência
                        p.y = alturaValencia - 5;
                    }
                }
            } else {
                // Buracos permanecem próximos à valência, podemos deixá-los "vagar"
                // Sem saltos entre bandas para buracos neste modelo simplificado.
                if (p.y < alturaValencia + 15) {
                    p.y = alturaValencia + 15;
                }
                if (p.y > alturaValencia + 30) {
                    p.y = alturaValencia + 30;
                }
            }
        }
        
        painelAnimacao.repaint();
        painelBandas.repaint();
    }

    //======================= MAIN =============================================
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new SimuladorCelulaSolar();
        });
    }
}
