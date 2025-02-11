import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.Iterator;

public class ZePalitoCompleto extends JPanel implements ActionListener, KeyListener {
    
    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	// Constantes da tela e do jogo
    final int LARGURA_JOGO = 800;
    final int ALTURA_JOGO = 600;
    final int CHAO = 500; // posição do chão (y)
    
    Timer temporizador;
    Personagem jogador;
    ArrayList<Inimigo> inimigos;
    int pontuacao = 0;
    boolean jogoAcabado = false;
    boolean vitoria = false;
    
    public ZePalitoCompleto() {
        // Inicializa o jogador
        jogador = new Personagem(100, CHAO - 80, 50, 80);
        
        // Cria alguns inimigos (Zé Palitos)
        inimigos = new ArrayList<>();
        inimigos.add(new Inimigo(600, CHAO - 80, 50, 80));
        inimigos.add(new Inimigo(700, CHAO - 80, 50, 80));
        inimigos.add(new Inimigo(500, CHAO - 80, 50, 80));
        
        // Inicia o timer (~60 FPS)
        temporizador = new Timer(16, this);
        temporizador.start();
        
        // Configura os eventos do teclado
        addKeyListener(this);
        setFocusable(true);
        setFocusTraversalKeysEnabled(false);
    }
    
    @Override
    public void paintComponent(Graphics g) {
        super.paintComponent(g);
        // Desenha o fundo
        g.setColor(Color.LIGHT_GRAY);
        g.fillRect(0, 0, LARGURA_JOGO, ALTURA_JOGO);
        
        // Desenha o chão
        g.setColor(new Color(100, 50, 0));
        g.fillRect(0, CHAO, LARGURA_JOGO, ALTURA_JOGO - CHAO);
        
        // Desenha o jogador (Zé Palito)
        jogador.desenhar(g);
        
        // Desenha os inimigos (Zé Palitos)
        for (Inimigo inimigo : inimigos) {
            inimigo.desenhar(g);
        }
        
        // HUD: vida e pontuação
        g.setColor(Color.BLACK);
        g.setFont(new Font("Arial", Font.BOLD, 20));
        g.drawString("Vida: " + jogador.vida, 10, 25);
        g.drawString("Pontuação: " + pontuacao, 10, 50);
        
        // Mensagens de fim de jogo
        if (jogoAcabado) {
            g.setColor(Color.RED);
            g.setFont(new Font("Arial", Font.BOLD, 50));
            g.drawString("GAME OVER", LARGURA_JOGO / 2 - 150, ALTURA_JOGO / 2);
        } else if (vitoria) {
            g.setColor(Color.BLUE);
            g.setFont(new Font("Arial", Font.BOLD, 50));
            g.drawString("VOCÊ VENCEU!", LARGURA_JOGO / 2 - 180, ALTURA_JOGO / 2);
        }
    }
    
    @Override
    public void actionPerformed(ActionEvent e) {
        if (!jogoAcabado && !vitoria) {
            // Atualiza o jogador e os inimigos
            jogador.atualizar();
            for (Inimigo inimigo : inimigos) {
                inimigo.atualizar();
            }
            
            // Verifica colisão entre jogador e inimigos (para dano)
            for (Inimigo inimigo : inimigos) {
                if (jogador.getBounds().intersects(inimigo.getBounds())) {
                    if (jogador.tempoRecuperacao == 0) {
                        jogador.vida -= 10;
                        jogador.tempoRecuperacao = 30; // frames de invulnerabilidade
                    }
                }
            }
            
            // Se o jogador estiver atacando, verifica colisão com inimigos
            if (jogador.atacando) {
                Rectangle areaAtaque = jogador.getAreaAtaque();
                Iterator<Inimigo> it = inimigos.iterator();
                while (it.hasNext()) {
                    Inimigo inimigo = it.next();
                    if (areaAtaque.intersects(inimigo.getBounds())) {
                        inimigo.vida -= 20;
                        if (inimigo.vida <= 0) {
                            it.remove();
                            pontuacao += 100;
                        }
                    }
                }
            }
            
            // Atualiza o cooldown de dano do jogador
            if (jogador.tempoRecuperacao > 0) {
                jogador.tempoRecuperacao--;
            }
            
            // Verifica fim de jogo
            if (jogador.vida <= 0) {
                jogoAcabado = true;
                temporizador.stop();
            }
            if (inimigos.isEmpty()) {
                vitoria = true;
                temporizador.stop();
            }
        }
        repaint();
    }
    
    // Tratamento de eventos do teclado
    @Override
    public void keyPressed(KeyEvent e) {
        int codigo = e.getKeyCode();
        if (codigo == KeyEvent.VK_LEFT) {
            jogador.velocidadeX = -5;
            jogador.direcao = -1;
        } else if (codigo == KeyEvent.VK_RIGHT) {
            jogador.velocidadeX = 5;
            jogador.direcao = 1;
        } else if (codigo == KeyEvent.VK_UP) {
            if (!jogador.pulando) {
                jogador.velocidadeY = -15;
                jogador.pulando = true;
            }
        } else if (codigo == KeyEvent.VK_SPACE) {
            if (!jogador.atacando) {
                jogador.atacando = true;
                jogador.tempoAtaque = 15; // duração do ataque (em frames)
            }
        }
    }
    
    @Override
    public void keyReleased(KeyEvent e) {
        int codigo = e.getKeyCode();
        if (codigo == KeyEvent.VK_LEFT || codigo == KeyEvent.VK_RIGHT) {
            jogador.velocidadeX = 0;
        }
    }
    
    @Override
    public void keyTyped(KeyEvent e) {
        // Não utilizado
    }
    
    // Método para desenhar um Zé Palito (stick figure) com base em uma área delimitadora
    private void desenharZePalito(Graphics g, int x, int y, int largura, int altura, Color cor) {
        g.setColor(cor);
        // Define o diâmetro da cabeça (1/3 do menor valor entre largura e altura)
        int diametroCabeca = Math.min(largura, altura) / 3;
        int centroX = x + largura / 2;
        int topoCabeca = y;
        // Cabeça
        g.drawOval(centroX - diametroCabeca / 2, topoCabeca, diametroCabeca, diametroCabeca);
        // Corpo: linha vertical do final da cabeça até 60% da altura total
        int corpoInicioY = y + diametroCabeca;
        int corpoFimY = y + (int) (altura * 0.6);
        g.drawLine(centroX, corpoInicioY, centroX, corpoFimY);
        // Braços: partindo de um ponto logo abaixo da cabeça
        int bracoY = corpoInicioY + 10;
        g.drawLine(centroX, bracoY, x, bracoY + 10);         // braço esquerdo
        g.drawLine(centroX, bracoY, x + largura, bracoY + 10); // braço direito
        // Pernas: partindo do final do corpo até a base do personagem
        int baseY = y + altura;
        int pernaEsqX = x + (int)(largura * 0.3);
        int pernaDirX = x + (int)(largura * 0.7);
        g.drawLine(centroX, corpoFimY, pernaEsqX, baseY);
        g.drawLine(centroX, corpoFimY, pernaDirX, baseY);
    }
    
    // Classe que representa o personagem principal (Zé Palito)
    class Personagem {
        int x, y, largura, altura;
        int vida = 100;
        int direcao = 1; // 1 para direita, -1 para esquerda
        double velocidadeX = 0, velocidadeY = 0;
        boolean pulando = false;
        boolean atacando = false;
        int tempoAtaque = 0;      // duração do ataque
        int tempoRecuperacao = 0; // cooldown para receber dano
        
        public Personagem(int x, int y, int largura, int altura) {
            this.x = x;
            this.y = y;
            this.largura = largura;
            this.altura = altura;
        }
        
        public void atualizar() {
            x += velocidadeX;
            y += velocidadeY;
            
            // Aplica gravidade se estiver pulando
            if (pulando) {
                velocidadeY += 0.7;
            }
            // Verifica se atingiu o chão
            if (y >= CHAO - altura) {
                y = CHAO - altura;
                velocidadeY = 0;
                pulando = false;
            }
            // Limita o movimento dentro da tela
            if (x < 0) x = 0;
            if (x > LARGURA_JOGO - largura) x = LARGURA_JOGO - largura;
            
            // Atualiza o tempo de ataque
            if (atacando) {
                tempoAtaque--;
                if (tempoAtaque <= 0) {
                    atacando = false;
                }
            }
        }
        
        public void desenhar(Graphics g) {
            // Desenha o Zé Palito do jogador com cor verde
            desenharZePalito(g, x, y, largura, altura, Color.GREEN);
            // Se estiver atacando, desenha a área de ataque
            if (atacando) {
                g.setColor(new Color(255, 0, 0, 128));
                Rectangle area = getAreaAtaque();
                g.fillRect(area.x, area.y, area.width, area.height);
            }
        }
        
        public Rectangle getBounds() {
            return new Rectangle(x, y, largura, altura);
        }
        
        // Retorna a área de ataque (à frente do personagem)
        public Rectangle getAreaAtaque() {
            int larguraAtaque = 20;
            int alturaAtaque = altura;
            int xAtaque;
            if (direcao == 1) {
                xAtaque = x + largura;
            } else {
                xAtaque = x - larguraAtaque;
            }
            return new Rectangle(xAtaque, y, larguraAtaque, alturaAtaque);
        }
    }
    
    // Classe que representa um inimigo (também um Zé Palito)
    class Inimigo {
        int x, y, largura, altura;
        int vida = 50;
        double velocidadeX = 2; // velocidade de movimentação
        
        public Inimigo(int x, int y, int largura, int altura) {
            this.x = x;
            this.y = y;
            this.largura = largura;
            this.altura = altura;
        }
        
        public void atualizar() {
            // Move-se em direção ao jogador
            if (jogador.x > x) {
                x += velocidadeX;
            } else if (jogador.x < x) {
                x -= velocidadeX;
            }
            // Garante que o inimigo esteja no chão
            if (y < CHAO - altura) {
                y = CHAO - altura;
            }
        }
        
        public void desenhar(Graphics g) {
            // Desenha o Zé Palito inimigo com cor magenta
            desenharZePalito(g, x, y, largura, altura, Color.MAGENTA);
        }
        
        public Rectangle getBounds() {
            return new Rectangle(x, y, largura, altura);
        }
    }
    
    public static void main(String[] args) {
        JFrame janela = new JFrame("Zé Palito");
        ZePalitoCompleto jogo = new ZePalitoCompleto();
        janela.add(jogo);
        janela.setSize(jogo.LARGURA_JOGO, jogo.ALTURA_JOGO);
        janela.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        janela.setResizable(false);   
        janela.setLocationRelativeTo(null);
        janela.setVisible(true);
    }
}

