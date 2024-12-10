import java.awt.BorderLayout;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.net.URL;

import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
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
import org.jfree.data.category.DefaultCategoryDataset;

public class ModeloPoissonGUI extends JFrame {
    private static final long serialVersionUID = 1L;
    private JTextField campoLambda;
    private JTextField campoNMax;
    private JButton botaoCalcular;
    private JPanel painelGrafico;

    public ModeloPoissonGUI() {
        super("Modelo de Falências - Distribuição de Poisson");

        // Painel principal com BorderLayout
        JPanel painelPrincipal = new JPanel(new BorderLayout(10, 10));
        painelPrincipal.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        // Painel de entrada com GridBagLayout
        JPanel painelEntrada = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5); // Espaçamento entre componentes
        gbc.anchor = GridBagConstraints.WEST;

        // Label e campo para λ
        JLabel labelLambda = new JLabel("Valor de λ (taxa média): ");
        gbc.gridx = 0;
        gbc.gridy = 0;
        painelEntrada.add(labelLambda, gbc);

        campoLambda = new JTextField("2.0", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoLambda, gbc);

        // Label e campo para n máximo
        JLabel labelN = new JLabel("Número máximo de falências (n): ");
        gbc.gridx = 0;
        gbc.gridy = 1;
        painelEntrada.add(labelN, gbc);

        campoNMax = new JTextField("10", 10);
        gbc.gridx = 1;
        painelEntrada.add(campoNMax, gbc);

        // Botão de calcular
        botaoCalcular = new JButton("Calcular e Plotar");
        gbc.gridx = 0;
        gbc.gridy = 2;
        gbc.gridwidth = 2;
        gbc.anchor = GridBagConstraints.CENTER;
        painelEntrada.add(botaoCalcular, gbc);

        painelPrincipal.add(painelEntrada, BorderLayout.NORTH);

        // Painel do gráfico
        painelGrafico = new JPanel(new BorderLayout());
        painelPrincipal.add(painelGrafico, BorderLayout.CENTER);

        // Painel da fórmula
        JPanel painelFormula = new JPanel(new BorderLayout());

        // Carrega a imagem da fórmula (certifique-se de que "poisson_formula.png" está no classpath)
        URL imgURL = getClass().getResource("/poisson_formula.png");
        if (imgURL != null) {
            JLabel formulaLabel = new JLabel(new ImageIcon(imgURL));
            painelFormula.add(formulaLabel, BorderLayout.CENTER);
        } else {
            // Caso não encontre a imagem, mostramos apenas texto
            JLabel formulaLabel = new JLabel("Fórmula: P(X=k) = (λ^k e^{-λ}) / k!");
            painelFormula.add(formulaLabel, BorderLayout.CENTER);
        }

        painelPrincipal.add(painelFormula, BorderLayout.SOUTH);

        setContentPane(painelPrincipal);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        // Ação do botão
        botaoCalcular.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                calcularEPlotar();
            }
        });

        // Ajusta o tamanho da janela
        setSize(500, 600);
        setLocationRelativeTo(null);
    }

    private void calcularEPlotar() {
        double lambda;
        int nMax;

        try {
            lambda = Double.parseDouble(campoLambda.getText().replace(",", "."));
            nMax = Integer.parseInt(campoNMax.getText());
            if (lambda <= 0 || nMax < 0) {
                JOptionPane.showMessageDialog(this, "Valores inválidos. λ deve ser positivo e n >= 0.",
                        "Erro de Entrada", JOptionPane.ERROR_MESSAGE);
                return;
            }
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Por favor, insira valores válidos.",
                    "Erro de Entrada", JOptionPane.ERROR_MESSAGE);
            return;
        }

        DefaultCategoryDataset dataset = new DefaultCategoryDataset();
        for (int k = 0; k <= nMax; k++) {
            double p = poissonProbability(k, lambda);
            dataset.addValue(p, "Probabilidade", String.valueOf(k));
        }

        JFreeChart chart = ChartFactory.createBarChart(
                "Distribuição de Poisson (Falências)",
                "Número de falências (k)",
                "Probabilidade",
                dataset
        );

        painelGrafico.removeAll();
        ChartPanel chartPanel = new ChartPanel(chart);
        painelGrafico.add(chartPanel, BorderLayout.CENTER);
        painelGrafico.revalidate();
        painelGrafico.repaint();
    }

    private double poissonProbability(int k, double lambda) {
        return (Math.pow(lambda, k) * Math.exp(-lambda)) / fatorial(k);
    }

    private double fatorial(int n) {
        if (n <= 1) return 1.0;
        double fat = 1.0;
        for (int i = 2; i <= n; i++) {
            fat *= i;
        }
        return fat;
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            ModeloPoissonGUI gui = new ModeloPoissonGUI();
            gui.setVisible(true);
        });
    }
}
