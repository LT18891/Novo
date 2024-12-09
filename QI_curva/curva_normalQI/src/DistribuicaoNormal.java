import javax.swing.*;
import java.awt.*;

public class DistribuicaoNormal extends JPanel {

    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	// Parâmetros da distribuição normal
    private final double media = 100.0;           // Média (µ)
    private final double desvioPadrao = 15.0;     // Desvio padrão (σ)
    private final double minX = 40.0;            // Valor mínimo do eixo X
    private final double maxX = 160.0;           // Valor máximo do eixo X
    private final int pontos = 500;             // Número de pontos para plotar a curva

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2d = (Graphics2D) g;

        // Configurações do gráfico
        int largura = getWidth();
        int altura = getHeight();
        int margem = 60;

        // Eixos do gráfico
        g2d.setColor(Color.BLACK);
        g2d.drawLine(margem, altura - margem, largura - margem, altura - margem); // Eixo X
        g2d.drawLine(margem, margem, margem, altura - margem); // Eixo Y

        // Labels dos eixos
        g2d.drawString("QI", largura / 2, altura - 20);
        g2d.drawString("Densidade de Probabilidade", 10, altura / 2);

        // Escala
        double escalaX = (largura - 2 * margem) / (maxX - minX);
        double escalaY = (altura - 2 * margem) / 0.04; // Altura máxima baseada na densidade máxima da normal

        // Plotar a curva
        g2d.setColor(Color.BLUE);
        double passo = (maxX - minX) / pontos;
        for (int i = 0; i < pontos; i++) {
            double x1 = minX + i * passo;
            double x2 = minX + (i + 1) * passo;
            double y1 = densidadeNormal(x1, media, desvioPadrao);
            double y2 = densidadeNormal(x2, media, desvioPadrao);

            int px1 = (int) (margem + (x1 - minX) * escalaX);
            int py1 = (int) (altura - margem - y1 * escalaY);
            int px2 = (int) (margem + (x2 - minX) * escalaX);
            int py2 = (int) (altura - margem - y2 * escalaY);

            g2d.drawLine(px1, py1, px2, py2);
        }

        // Adicionar a equação no gráfico
        g2d.setColor(Color.RED);
        g2d.drawString("f(x) = 1/(σ√2π) * e^(-(x-µ)² / 2σ²)", margem, margem - 10);

        // Linhas verticais para a média e desvios padrão
        desenharLinhaVertical(g2d, largura, altura, margem, media, escalaX, "Média (µ)", Color.BLACK);
        desenharLinhaVertical(g2d, largura, altura, margem, media + desvioPadrao, escalaX, "+1σ", Color.GREEN);
        desenharLinhaVertical(g2d, largura, altura, margem, media - desvioPadrao, escalaX, "-1σ", Color.GREEN);
        desenharLinhaVertical(g2d, largura, altura, margem, media + 2 * desvioPadrao, escalaX, "+2σ", Color.ORANGE);
        desenharLinhaVertical(g2d, largura, altura, margem, media - 2 * desvioPadrao, escalaX, "-2σ", Color.ORANGE);
        desenharLinhaVertical(g2d, largura, altura, margem, media + 3 * desvioPadrao, escalaX, "+3σ", Color.RED);
        desenharLinhaVertical(g2d, largura, altura, margem, media - 3 * desvioPadrao, escalaX, "-3σ", Color.RED);
    }

    // Método para desenhar uma linha vertical no gráfico
    private void desenharLinhaVertical(Graphics2D g2d, int largura, int altura, int margem, double valor, double escalaX, String label, Color cor) {
        g2d.setColor(cor);
        int x = (int) (margem + (valor - minX) * escalaX);
        g2d.drawLine(x, margem, x, altura - margem);
        g2d.drawString(label, x - 20, margem - 10);
    }

    // Função para calcular a densidade de probabilidade
    public double densidadeNormal(double x, double media, double desvioPadrao) {
        double expoente = -Math.pow(x - media, 2) / (2 * Math.pow(desvioPadrao, 2));
        return (1 / (desvioPadrao * Math.sqrt(2 * Math.PI))) * Math.exp(expoente);
    }

    // Método principal
    public static void main(String[] args) {
        JFrame frame = new JFrame("Distribuição Normal (QI)");
        DistribuicaoNormal painel = new DistribuicaoNormal();
        frame.add(painel);
        frame.setSize(900, 600);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);
    }
}
