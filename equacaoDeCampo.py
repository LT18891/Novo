import tkinter as tk
from tkinter import ttk, messagebox
import math
import locale

# Configurar locale para garantir o ponto decimal
locale.setlocale(locale.LC_ALL, 'C')


class SimulacaoCampoEinstein(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configurações iniciais da janela
        self.title("Simulação das Equações de Campo de Einstein")
        self.geometry("1600x900")
        self.minsize(1200, 700)  # Tamanho mínimo para evitar que os componentes fiquem muito pequenos
        self.resizable(True, True)  # Permitir redimensionamento

        # Inicialização das variáveis físicas com valores padrão
        self.massa_sol = 1.989e30          # Massa do Sol em kg
        self.massa_terra = 5.972e24        # Massa da Terra em kg
        self.distancia_inicial = 1.496e11  # Distância inicial em metros (1 AU)
        self.G = 6.67430e-11               # Constante gravitacional
        self.c = 299792458                 # Velocidade da luz em m/s

        # Escala para converter metros em pixels (1 AU = 400 pixels inicialmente)
        self.escala_distancia = 400 / self.distancia_inicial  # pixels/meter
        self.escala_curvatura = 1.0e-2  # pixels/meter

        # Variáveis de animação
        self.pos_x = self.distancia_inicial  # Posição X em metros
        self.pos_y = 0                        # Posição Y em metros
        self.vel_x = 0                        # Velocidade X em m/s
        self.vel_y = math.sqrt(self.G * self.massa_sol / self.distancia_inicial) * 0.8  # Velocidade Y em m/s (ajustada para órbita elíptica)
        self.trajetoria_terra = []            # Lista para armazenar a trajetória da Terra

        # Criar os painéis da interface
        self.criar_painel_entrada()
        self.criar_painel_desenho()
        self.criar_painel_informacoes()

        # Iniciar a animação
        self.after_id = None
        self.iniciar_animacao()

    def criar_painel_entrada(self):
        painel_entrada = ttk.Frame(self)
        painel_entrada.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(painel_entrada, text="Entrada de Variáveis", font=("Serif", 16, "bold")).pack(pady=10)

        # Massa do Sol
        self.campo_massa_sol = self.criar_campo_entrada(painel_entrada, "Massa do Sol (kg):", f"{self.massa_sol:.10e}")

        # Massa da Terra
        self.campo_massa_terra = self.criar_campo_entrada(painel_entrada, "Massa da Terra (kg):", f"{self.massa_terra:.10e}")

        # Distância
        self.campo_distancia = self.criar_campo_entrada(painel_entrada, "Distância (m):", f"{self.distancia_inicial:.10e}")

        # Constante G
        self.campo_constante_g = self.criar_campo_entrada(painel_entrada, "Constante G (m³ kg⁻¹ s⁻²):", f"{self.G:.10e}")

        # Velocidade da Luz
        self.campo_velocidade_luz = self.criar_campo_entrada(painel_entrada, "Velocidade da Luz (m/s):", f"{self.c:.10e}")

        # Botão para atualizar a simulação
        botao_atualizar = ttk.Button(painel_entrada, text="Atualizar Simulação", command=self.atualizar_simulacao)
        botao_atualizar.pack(pady=20)

    def criar_campo_entrada(self, parent, texto, valor_inicial):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        label = ttk.Label(frame, text=texto, width=25, anchor='w')
        label.pack(side=tk.LEFT, padx=5)

        entry = ttk.Entry(frame, width=20)
        entry.insert(0, valor_inicial)
        entry.pack(side=tk.RIGHT, padx=5)

        return entry

    def criar_painel_desenho(self):
        painel_desenho = ttk.Frame(self)
        painel_desenho.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(painel_desenho, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def criar_painel_informacoes(self):
        painel_info = ttk.Frame(self)
        painel_info.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(painel_info, text="Informações", font=("Serif", 16, "bold")).pack(pady=10)

        # Equações
        painel_equacoes = ttk.LabelFrame(painel_info, text="Equações de Campo de Einstein", padding=10)
        painel_equacoes.pack(fill=tk.X, pady=10)

        eq_texto = "G₍μν₎ + Λg₍μν₎ = (8πG / c⁴) T₍μν₎"
        ttk.Label(painel_equacoes, text=eq_texto, font=("Serif", 14)).pack()

        # Explicação
        painel_explicacao = ttk.LabelFrame(painel_info, text="Sobre o Programa", padding=10)
        painel_explicacao.pack(fill=tk.BOTH, expand=True, pady=10)

        explicacao_texto = (
            "Esta aplicação simula a curvatura do espaço-tempo causada por objetos massivos, como o Sol e a Terra.\n\n"
            "Insira os valores de massa e distância para visualizar como a curvatura do espaço-tempo é afetada.\n\n"
            "A animação mostra a Terra orbitando o Sol, representando a deformação do espaço-tempo.\n\n"
            "Fórmulas Utilizadas:\n"
            "• Velocidade Angular (ω): ω = √(G * M / R³)\n"
            "• Curvatura do Espaço-Tempo (K): K = G * massa / c²"
        )
        texto_explicacao = tk.Text(painel_explicacao, wrap=tk.WORD, height=15, bg="#F0F0F0")
        texto_explicacao.insert(tk.END, explicacao_texto)
        texto_explicacao.config(state=tk.DISABLED)
        texto_explicacao.pack(fill=tk.BOTH, expand=True)

        # Informações Numéricas
        painel_numeros = ttk.LabelFrame(painel_info, text="Dados da Simulação", padding=10)
        painel_numeros.pack(fill=tk.X, pady=10)

        self.label_posicao = ttk.Label(painel_numeros, text="Posição X: 0 m\nPosição Y: 0 m")
        self.label_posicao.pack(anchor='w', padx=5, pady=5)

        self.label_velocidade = ttk.Label(painel_numeros, text="Velocidade X: 0 m/s\nVelocidade Y: 0 m/s")
        self.label_velocidade.pack(anchor='w', padx=5, pady=5)

        # Autor
        painel_autor = ttk.LabelFrame(painel_info, text="Autor", padding=10)
        painel_autor.pack(fill=tk.X, pady=10)

        ttk.Label(painel_autor, text="Luiz Tiago Wilcke", font=("Serif", 14)).pack()

    def atualizar_simulacao(self):
        try:
            massa_sol = float(self.campo_massa_sol.get())
            massa_terra = float(self.campo_massa_terra.get())
            distancia = float(self.campo_distancia.get())
            G = float(self.campo_constante_g.get())
            c = float(self.campo_velocidade_luz.get())

            # Validar entradas
            if massa_sol <= 0 or massa_terra <= 0 or distancia <= 0 or G <= 0 or c <= 0:
                self.mostrar_alerta("Erro", "Todos os valores devem ser positivos.")
                return

            # Atualizar parâmetros na simulação
            self.massa_sol = massa_sol
            self.massa_terra = massa_terra
            self.distancia_inicial = distancia
            self.G = G
            self.c = c

            # Atualizar escala de distância para caber no canvas
            # Mantemos uma escala dinâmica baseada na distância inicial e no tamanho do canvas
            largura_canvas = self.canvas.winfo_width()
            altura_canvas = self.canvas.winfo_height()
            self.escala_distancia = min(largura_canvas, altura_canvas) / (4 * self.distancia_inicial)  # 4 AU cabem no canvas

            # Reinicializar física com novos parâmetros
            self.pos_x = self.distancia_inicial
            self.pos_y = 0
            self.vel_x = 0
            self.vel_y = math.sqrt(self.G * self.massa_sol / self.distancia_inicial) * 0.8
            self.trajetoria_terra.clear()

            # Atualizar labels de dados numéricos
            self.atualizar_labels()

            # Redesenhar
            self.canvas.delete("all")

        except ValueError:
            self.mostrar_alerta("Erro de Formato", "Por favor, insira valores numéricos válidos com até 10 dígitos de precisão.")

    def mostrar_alerta(self, titulo, mensagem):
        messagebox.showerror(titulo, mensagem)

    def iniciar_animacao(self):
        delta_t = 1e4  # Intervalo de tempo em segundos (aproximadamente 2,74 horas)
        self.animar_orbita(delta_t)

    def animar_orbita(self, delta_t):
        # Calcula a distância atual da Terra ao Sol
        r = math.sqrt(self.pos_x ** 2 + self.pos_y ** 2)

        # Evitar divisão por zero
        if r == 0:
            a_x = 0
            a_y = 0
        else:
            # Calcula a aceleração devido à gravidade
            a_x = -self.G * self.massa_sol * self.pos_x / (r ** 3)
            a_y = -self.G * self.massa_sol * self.pos_y / (r ** 3)

        # Atualiza a velocidade da Terra
        self.vel_x += a_x * delta_t
        self.vel_y += a_y * delta_t

        # Atualiza a posição da Terra
        self.pos_x += self.vel_x * delta_t
        self.pos_y += self.vel_y * delta_t

        # Adiciona a posição atual à trajetória
        self.trajetoria_terra.append((self.pos_x, self.pos_y))

        # Atualiza labels de dados numéricos
        self.atualizar_labels()

        # Atualiza a simulação gráfica
        self.desenhar_simulacao()

        # Agendar a próxima atualização
        self.after_id = self.after(50, lambda: self.animar_orbita(delta_t))  # Atualização a cada 50 ms

    def atualizar_labels(self):
        pos_texto = f"Posição X: {self.pos_x:.2e} m\nPosição Y: {self.pos_y:.2e} m"
        vel_texto = f"Velocidade X: {self.vel_x:.2e} m/s\nVelocidade Y: {self.vel_y:.2e} m/s"
        self.label_posicao.config(text=pos_texto)
        self.label_velocidade.config(text=vel_texto)

    def desenhar_simulacao(self):
        self.canvas.delete("all")

        # Centro do canvas (posição do Sol)
        centro_x = self.canvas.winfo_width() / 2
        centro_y = self.canvas.winfo_height() / 2

        # Desenhar a malha de espaço-tempo
        self.desenhar_malha_espaco_tempo(centro_x, centro_y)

        # Desenhar o Sol
        raio_sol_pixel = 30
        self.canvas.create_oval(
            centro_x - raio_sol_pixel, centro_y - raio_sol_pixel,
            centro_x + raio_sol_pixel, centro_y + raio_sol_pixel,
            fill="yellow"
        )

        # Desenhar a trajetória da Terra
        if len(self.trajetoria_terra) > 1:
            pontos = []
            for p in self.trajetoria_terra:
                x = p[0] * self.escala_distancia + centro_x
                y = p[1] * self.escala_distancia + centro_y
                pontos.append((x, y))
            self.canvas.create_line(pontos, fill="white")

        # Calcular posição da Terra em pixels
        terra_x = self.pos_x * self.escala_distancia + centro_x
        terra_y = self.pos_y * self.escala_distancia + centro_y

        # Desenhar a Terra
        raio_terra_pixel = 15
        self.canvas.create_oval(
            terra_x - raio_terra_pixel, terra_y - raio_terra_pixel,
            terra_x + raio_terra_pixel, terra_y + raio_terra_pixel,
            fill="blue"
        )

        # Desenhar a curvatura do espaço-tempo ao redor do Sol
        curvatura_sol = self.calcular_curvatura(self.massa_sol)
        self.canvas.create_oval(
            centro_x - curvatura_sol, centro_y - curvatura_sol,
            centro_x + curvatura_sol, centro_y + curvatura_sol,
            outline="#FF0000", width=2
        )

        # Desenhar a curvatura do espaço-tempo ao redor da Terra
        curvatura_terra = self.calcular_curvatura(self.massa_terra)
        self.canvas.create_oval(
            terra_x - curvatura_terra, terra_y - curvatura_terra,
            terra_x + curvatura_terra, terra_y + curvatura_terra,
            outline="#FF0000", width=2
        )

        # Desenhar seta indicando a direção do movimento da Terra
        self.desenhar_seta(terra_x, terra_y)

    def desenhar_seta(self, x, y):
        velocidade = math.sqrt(self.vel_x ** 2 + self.vel_y ** 2)
        if velocidade == 0:
            return

        angulo_velocidade = math.atan2(self.vel_y, self.vel_x)
        tamanho_seta = 20
        seta_angulo = angulo_velocidade

        x2 = x + tamanho_seta * math.cos(seta_angulo)
        y2 = y + tamanho_seta * math.sin(seta_angulo)

        # Desenhar linha da seta
        self.canvas.create_line(x, y, x2, y2, fill="white", width=2)

        # Desenhar a ponta da seta
        ponta_seta = [
            (x2, y2),
            (x2 - 5 * math.cos(seta_angulo - math.pi / 6), y2 - 5 * math.sin(seta_angulo - math.pi / 6)),
            (x2 - 5 * math.cos(seta_angulo + math.pi / 6), y2 - 5 * math.sin(seta_angulo + math.pi / 6)),
            (x2, y2)
        ]
        self.canvas.create_polygon(ponta_seta, fill="white")

    def desenhar_malha_espaco_tempo(self, centro_x, centro_y):
        linhas = 50
        colunas = 50
        espacamento_x = self.canvas.winfo_width() / colunas
        espacamento_y = self.canvas.winfo_height() / linhas

        # Desenhar linhas verticais
        for i in range(colunas + 1):
            x = i * espacamento_x
            self.canvas.create_line(x, 0, x, self.canvas.winfo_height(), fill="#A9A9A9", width=1)

        # Desenhar linhas horizontais
        for i in range(linhas + 1):
            y = i * espacamento_y
            self.canvas.create_line(0, y, self.canvas.winfo_width(), y, fill="#A9A9A9", width=1)

    def calcular_curvatura(self, massa):
        # Fórmula simplificada para a curvatura: K = G * massa / c^2
        K = (self.G * massa) / (self.c ** 2)
        # Para visualização, multiplicar por uma escala
        escala_visual = self.escala_curvatura * 1e9  # Ajuste para tornar visível
        return K * escala_visual

    def on_closing(self):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.destroy()


if __name__ == "__main__":
    app = SimulacaoCampoEinstein()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
