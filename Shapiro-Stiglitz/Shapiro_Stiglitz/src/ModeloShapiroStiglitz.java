import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

// Modelo Shapiro-Stiglitz Simplificado
// w >= b + ((r + s)/q)*((1-e)/e)

public class ModeloShapiroStiglitz extends JFrame {
    
    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	// Componentes da interface
    private JTextField campoBeneficioDesemprego;
    private JTextField campoTaxaDesconto;
    private JTextField campoTaxaSeparacao;
    private JTextField campoProbMonitoramento;
    private JTextField campoEsforco;
    
    private JButton botaoCalcular;
    private JLabel labelResultado;

    public ModeloShapiroStiglitz() {
        super("Modelo Shapiro-Stiglitz");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());
        
        // Painel de parâmetros
        JPanel painelParametros = new JPanel(new GridLayout(6, 2, 5, 5));
        
        painelParametros.add(new JLabel("Benefício do Desemprego (b):"));
        campoBeneficioDesemprego = new JTextField("0.2");
        painelParametros.add(campoBeneficioDesemprego);
        
        painelParametros.add(new JLabel("Taxa de Desconto (r):"));
        campoTaxaDesconto = new JTextField("0.05");
        painelParametros.add(campoTaxaDesconto);
        
        painelParametros.add(new JLabel("Taxa de Separação (s):"));
        campoTaxaSeparacao = new JTextField("0.02");
        painelParametros.add(campoTaxaSeparacao);
        
        painelParametros.add(new JLabel("Probabilidade de Detecção (q):"));
        campoProbMonitoramento = new JTextField("0.3");
        painelParametros.add(campoProbMonitoramento);
        
        painelParametros.add(new JLabel("Nível de Esforço (e):"));
        campoEsforco = new JTextField("0.8");
        painelParametros.add(campoEsforco);
        
        botaoCalcular = new JButton("Calcular Salário de Eficiência");
        painelParametros.add(new JLabel());
        painelParametros.add(botaoCalcular);
        
        add(painelParametros, BorderLayout.NORTH);
        
        // Painel de resultado
        JPanel painelResultado = new JPanel(new FlowLayout());
        labelResultado = new JLabel("Resultado aparecerá aqui");
        painelResultado.add(labelResultado);
        add(painelResultado, BorderLayout.CENTER);
        
        // Ação do botão
        botaoCalcular.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                calcularSalario();
            }
        });
        
        // Ajustar tamanho e exibir
        setSize(600, 300);
        setLocationRelativeTo(null);
        setVisible(true);
    }
    
    private void calcularSalario() {
        try {
            double b = Double.parseDouble(campoBeneficioDesemprego.getText().trim());
            double r = Double.parseDouble(campoTaxaDesconto.getText().trim());
            double s = Double.parseDouble(campoTaxaSeparacao.getText().trim());
            double q = Double.parseDouble(campoProbMonitoramento.getText().trim());
            double e = Double.parseDouble(campoEsforco.getText().trim());
            
            // Verificar limites básicos
            if(e <= 0 || e >= 1) {
                labelResultado.setText("Erro: o esforço (e) deve estar entre 0 e 1.");
                return;
            }
            if(q <= 0 || q > 1) {
                labelResultado.setText("Erro: a probabilidade (q) deve estar entre 0 e 1.");
                return;
            }
            
            // Fórmula do salário que evita a ociosidade
            double salario = b + ((r + s) / q) * ((1 - e) / e);
            
            labelResultado.setText(String.format("Salário de Eficiência (w): %.4f", salario));
            
        } catch (NumberFormatException ex) {
            labelResultado.setText("Erro: certifique-se de que todos os campos são numéricos.");
        }
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new ModeloShapiroStiglitz());
    }
}
