import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.Random;

public class ModeloEstocastico {
    
    // Método Euler–Maruyama para a SDE
    // dP = r*P*(1-P/K)*dt + sigma*P*dW
    // P_{n+1} = P_n + r*P_n*(1-P_n/K)*dt + sigma*P_n*sqrt(dt)*Z, Z~N(0,1)
    private static double[] eulerMaruyama(double r, double K, double sigma, double P0, double t_final, int n_steps) {
        double dt = t_final / n_steps;
        double[] P_values = new double[n_steps+1];
        P_values[0] = P0;
        Random rand = new Random();
        
        for (int i = 0; i < n_steps; i++) {
            double P = P_values[i];
            double dW = Math.sqrt(dt)*rand.nextGaussian();
            double P_next = P + r*P*(1-P/K)*dt + sigma*P*dW;
            if (P_next < 0) {
                P_next = 0.0;
            }
            P_values[i+1] = P_next;
        }
        
        return P_values;
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("Modelo Estocástico de Crescimento Populacional");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setSize(1200, 800); // tamanho grande da janela
            
            // Painel principal
            frame.setLayout(new BorderLayout());
            
            // Painel de entrada de parâmetros (top)
            JPanel painelEntrada = new JPanel(new GridBagLayout());
            painelEntrada.setBorder(BorderFactory.createTitledBorder("Parâmetros do Modelo"));
            GridBagConstraints c = new GridBagConstraints();
            c.insets = new Insets(5,5,5,5);
            c.anchor = GridBagConstraints.LINE_END;
            
            JLabel label_r = new JLabel("r (taxa de crescimento):");
            JLabel label_K = new JLabel("K (capacidade de suporte):");
            JLabel label_sigma = new JLabel("σ (intensidade do ruído):");
            JLabel label_P0 = new JLabel("P0 (população inicial):");
            JLabel label_tfinal = new JLabel("Tempo final:");
            JLabel label_nsteps = new JLabel("Número de passos:");
            
            JTextField field_r = new JTextField("0.1", 10);
            JTextField field_K = new JTextField("1e6", 10);
            JTextField field_sigma = new JTextField("0.05", 10);
            JTextField field_P0 = new JTextField("1e4", 10);
            JTextField field_tfinal = new JTextField("100", 10);
            JTextField field_nsteps = new JTextField("1000", 10);
            
            JButton botaoCalcular = new JButton("Calcular");
            
            c.gridx=0; c.gridy=0; painelEntrada.add(label_r,c);
            c.gridx=1; c.gridy=0; c.anchor=GridBagConstraints.LINE_START; painelEntrada.add(field_r,c);
            c.gridx=0; c.gridy=1; c.anchor=GridBagConstraints.LINE_END; painelEntrada.add(label_K,c);
            c.gridx=1; c.gridy=1; c.anchor=GridBagConstraints.LINE_START; painelEntrada.add(field_K,c);
            c.gridx=0; c.gridy=2; c.anchor=GridBagConstraints.LINE_END; painelEntrada.add(label_sigma,c);
            c.gridx=1; c.gridy=2; c.anchor=GridBagConstraints.LINE_START; painelEntrada.add(field_sigma,c);
            c.gridx=0; c.gridy=3; c.anchor=GridBagConstraints.LINE_END; painelEntrada.add(label_P0,c);
            c.gridx=1; c.gridy=3; c.anchor=GridBagConstraints.LINE_START; painelEntrada.add(field_P0,c);
            c.gridx=0; c.gridy=4; c.anchor=GridBagConstraints.LINE_END; painelEntrada.add(label_tfinal,c);
            c.gridx=1; c.gridy=4; c.anchor=GridBagConstraints.LINE_START; painelEntrada.add(field_tfinal,c);
            c.gridx=0; c.gridy=5; c.anchor=GridBagConstraints.LINE_END; painelEntrada.add(label_nsteps,c);
            c.gridx=1; c.gridy=5; c.anchor=GridBagConstraints.LINE_START; painelEntrada.add(field_nsteps,c);
            
            c.gridx=0; c.gridy=6; c.gridwidth=2; c.anchor=GridBagConstraints.CENTER;
            painelEntrada.add(botaoCalcular,c);
            
            frame.add(painelEntrada, BorderLayout.NORTH);
            
            // Painel de texto e equações (LEFT)
            JPanel painelTexto = new JPanel();
            painelTexto.setLayout(new BoxLayout(painelTexto, BoxLayout.Y_AXIS));
            painelTexto.setBorder(BorderFactory.createTitledBorder("Informações do Modelo"));
            
            String equacao = "Equação do Modelo Estocástico (Logístico):\n\n"
                    + "dP_t = r P_t (1 - P_t/K) dt + σ P_t dW_t\n";
            
            JLabel labelEq = new JLabel("<html><pre>"+equacao.replace("\n", "<br>")+"</pre></html>");
            labelEq.setFont(new Font("Arial", Font.PLAIN, 14));
            
            String explicacao = "Este modelo considera o crescimento populacional sob influência de incertezas ambientais,\n"
                    + "representadas como ruído multiplicativo. A dinâmica é descrita por uma equação diferencial\n"
                    + "estocástica (SDE), onde o termo aleatório dW_t introduz variação estocástica na evolução\n"
                    + "da população.\n\n"
                    + "Use os campos acima para ajustar os parâmetros e clique em 'Calcular'.\n";
            JLabel labelExp = new JLabel("<html><pre>"+explicacao.replace("\n", "<br>")+"</pre></html>");
            
            JLabel labelValores = new JLabel("Exemplos de valores de P(t):\n");
            labelValores.setFont(new Font("Courier", Font.PLAIN, 12));
            
            painelTexto.add(labelEq);
            painelTexto.add(Box.createVerticalStrut(10));
            painelTexto.add(labelExp);
            painelTexto.add(Box.createVerticalStrut(10));
            painelTexto.add(labelValores);
            
            // Painel do gráfico (CENTER)
            // Inicialmente vazio, será atualizado após "Calcular"
            XYSeries series = new XYSeries("População");
            XYSeriesCollection dataset = new XYSeriesCollection(series);
            JFreeChart chart = ChartFactory.createXYLineChart(
                    "Crescimento Populacional Estocástico",
                    "Tempo (t)",
                    "População (P(t))",
                    dataset,
                    PlotOrientation.VERTICAL,
                    true,
                    true,
                    false
            );
            
            // Ajustar opções do gráfico
            chart.getXYPlot().setDomainGridlinesVisible(true);
            chart.getXYPlot().setRangeGridlinesVisible(true);
            
            ChartPanel chartPanel = new ChartPanel(chart);
            chartPanel.setPreferredSize(new Dimension(800, 600));
            
            JSplitPane splitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, painelTexto, chartPanel);
            splitPane.setDividerLocation(400);
            
            frame.add(splitPane, BorderLayout.CENTER);
            
            // Ação do botão calcular
            botaoCalcular.addActionListener(new ActionListener() {
                @Override
                public void actionPerformed(ActionEvent e) {
                    try {
                        double r = Double.parseDouble(field_r.getText());
                        double K = Double.parseDouble(field_K.getText());
                        double sigma = Double.parseDouble(field_sigma.getText());
                        double P0 = Double.parseDouble(field_P0.getText());
                        double t_final = Double.parseDouble(field_tfinal.getText());
                        int n_steps = Integer.parseInt(field_nsteps.getText());
                        
                        double[] P_values = eulerMaruyama(r, K, sigma, P0, t_final, n_steps);
                        double dt = t_final / n_steps;
                        
                        // Atualizar dados do gráfico
                        series.clear();
                        for (int i = 0; i <= n_steps; i++) {
                            double t = i*dt;
                            series.add(t, P_values[i]);
                        }
                        
                        // Atualizar valores amostrais
                        double[] amostrasTempo = {0, t_final*0.25, t_final*0.5, t_final*0.75, t_final};
                        StringBuilder sb = new StringBuilder("Exemplos de valores de P(t):\n");
                        for (double tempoAmostra : amostrasTempo) {
                            int idx = (int)Math.round((tempoAmostra/dt));
                            if (idx < 0) idx=0;
                            if (idx > n_steps) idx=n_steps;
                            sb.append(String.format("P(%.2f) = %.5e%n", idx*dt, P_values[idx]));
                        }
                        labelValores.setText("<html><pre>"+sb.toString().replace("\n", "<br>")+"</pre></html>");
                        
                    } catch (NumberFormatException ex) {
                        JOptionPane.showMessageDialog(frame, "Por favor, insira valores numéricos válidos.", "Erro", JOptionPane.ERROR_MESSAGE);
                    }
                }
            });
            
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
        });
    }
}
