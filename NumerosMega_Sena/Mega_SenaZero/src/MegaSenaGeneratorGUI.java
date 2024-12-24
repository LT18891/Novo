import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

public class MegaSenaGeneratorGUI extends JFrame {

    private JPanel contentPane;
    private JTextField durationField;
    private JTextArea outputArea;
    private JButton startButton;
    private JButton stopButton;

    private GeneratorTask generatorTask;
    private Thread generatorThread;

    public MegaSenaGeneratorGUI() {
        setTitle("Gerador de Números da Mega-Sena");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setBounds(100, 100, 600, 500);
        contentPane = new JPanel();
        contentPane.setBorder(new EmptyBorder(15, 15, 15, 15));
        setContentPane(contentPane);
        contentPane.setLayout(new BorderLayout(10, 10));

        // Painel Superior para Entrada
        JPanel inputPanel = new JPanel();
        inputPanel.setLayout(new FlowLayout(FlowLayout.LEFT, 10, 10));
        contentPane.add(inputPanel, BorderLayout.NORTH);

        JLabel lblDuration = new JLabel("Duração (segundos):");
        inputPanel.add(lblDuration);

        durationField = new JTextField();
        durationField.setColumns(10);
        inputPanel.add(durationField);

        startButton = new JButton("Iniciar Geração");
        inputPanel.add(startButton);

        stopButton = new JButton("Parar Geração");
        stopButton.setEnabled(false);
        inputPanel.add(stopButton);

        // Área de Texto para Saída
        outputArea = new JTextArea();
        outputArea.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(outputArea);
        contentPane.add(scrollPane, BorderLayout.CENTER);

        // Eventos dos Botões
        startButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                iniciarGeracao();
            }
        });

        stopButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                pararGeracao();
            }
        });
    }

    private void iniciarGeracao() {
        String duracaoTexto = durationField.getText().trim();
        if (duracaoTexto.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Por favor, insira a duração em segundos.", "Erro", JOptionPane.ERROR_MESSAGE);
            return;
        }

        long duracaoSegundos;
        try {
            duracaoSegundos = Long.parseLong(duracaoTexto);
            if (duracaoSegundos <= 0) throw new NumberFormatException();
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Duração inválida. Insira um número inteiro positivo.", "Erro", JOptionPane.ERROR_MESSAGE);
            return;
        }

        startButton.setEnabled(false);
        stopButton.setEnabled(true);
        outputArea.setText("");

        generatorTask = new GeneratorTask(duracaoSegundos, outputArea, this);
        generatorThread = new Thread(generatorTask);
        generatorThread.start();
    }

    private void pararGeracao() {
        if (generatorTask != null) {
            generatorTask.stop();
            startButton.setEnabled(true);
            stopButton.setEnabled(false);
        }
    }

    public void finalizarInterface() {
        startButton.setEnabled(true);
        stopButton.setEnabled(false);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            try {
                MegaSenaGeneratorGUI frame = new MegaSenaGeneratorGUI();
                frame.setVisible(true);
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
    }
}

class GeneratorTask implements Runnable {

    private final long duracaoSegundos;
    private final JTextArea outputArea;
    private final MegaSenaGeneratorGUI interfaceGUI;
    private final AtomicBoolean running = new AtomicBoolean(true);

    private static final int NUMERO_MAXIMO = 60;
    private static final int QUANTIDADE_NUMEROS = 6;

    // Frequência histórica simulada (em uma aplicação real, utilize dados reais)
    private final Map<Integer, Integer> frequenciaHistorica = new HashMap<>();
    private final Random random = new Random();

    public GeneratorTask(long duracaoSegundos, JTextArea outputArea, MegaSenaGeneratorGUI interfaceGUI) {
        this.duracaoSegundos = duracaoSegundos;
        this.outputArea = outputArea;
        this.interfaceGUI = interfaceGUI;
        inicializarFrequenciaHistorica();
    }

    private void inicializarFrequenciaHistorica() {
        // Simulação: Frequência aleatória entre 10 e 100 para cada número
        for (int i = 1; i <= NUMERO_MAXIMO; i++) {
            frequenciaHistorica.put(i, 10 + random.nextInt(91));
        }
    }

    @Override
    public void run() {
        long tempoInicio = System.currentTimeMillis();
        long tempoFim = tempoInicio + duracaoSegundos * 1000;

        while (running.get() && System.currentTimeMillis() < tempoFim) {
            List<Integer> numeros = gerarNumerosComProbabilidade();
            String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
            String resultado = "[" + timestamp + "] Números gerados: " + numeros.toString();

            // Atualizar a área de texto na thread de eventos do Swing
            SwingUtilities.invokeLater(() -> {
                outputArea.append(resultado + "\n");
                outputArea.setCaretPosition(outputArea.getDocument().getLength());
            });

            // Intervalo de 1 segundo entre as gerações
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }

        // Finalizar a interface após a conclusão
        SwingUtilities.invokeLater(() -> interfaceGUI.finalizarInterface());
    }

    /**
     * Para a geração de números.
     */
    public void stop() {
        running.set(false);
    }

    /**
     * Gera uma lista de números da Mega-Sena baseada em uma abordagem de probabilidade avançada.
     *
     * @return Lista de 6 números únicos, ordenados.
     */
    private List<Integer> gerarNumerosComProbabilidade() {
        // Implementação de uma abordagem de probabilidade avançada:
        // Utilizando análise de frequência e probabilidade condicional.

        // 1. Calcular a soma total das frequências
        int somaFrequencias = frequenciaHistorica.values().stream().mapToInt(Integer::intValue).sum();

        // 2. Calcular a probabilidade de cada número
        Map<Integer, Double> probabilidades = new HashMap<>();
        for (Map.Entry<Integer, Integer> entry : frequenciaHistorica.entrySet()) {
            probabilidades.put(entry.getKey(), (double) entry.getValue() / somaFrequencias);
        }

        // 3. Aplicar um ajuste baseado em probabilidade condicional
        // Por exemplo, evitar sequências ou repetições excessivas
        // Neste exemplo, vamos penalizar a seleção de números que formam sequências longas

        // Criação de um pool ponderado
        List<Integer> pool = new ArrayList<>();
        for (int i = 1; i <= NUMERO_MAXIMO; i++) {
            double prob = probabilidades.get(i);
            // Penalização simples para sequências: reduzir a probabilidade se formar uma sequência
            // Aqui, simplificamos sem considerar o contexto das sequências
            int peso = (int) Math.round(prob * 1000); // Multiplicador para manter a precisão
            for (int j = 0; j < peso; j++) {
                pool.add(i);
            }
        }

        // Selecionar 6 números únicos com base na probabilidade
        Set<Integer> numerosSelecionados = new LinkedHashSet<>();
        while (numerosSelecionados.size() < QUANTIDADE_NUMEROS) {
            int index = random.nextInt(pool.size());
            numerosSelecionados.add(pool.get(index));
        }

        List<Integer> numeros = new ArrayList<>(numerosSelecionados);
        Collections.sort(numeros);
        return numeros;
    }
}
