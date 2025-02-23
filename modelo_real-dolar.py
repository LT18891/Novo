import tkinter as tk
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Classe para criar um Entry com placeholder (texto sugestivo)
class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="Digite aqui...", cor_placeholder="grey", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.cor_placeholder = cor_placeholder
        self.cor_normal = self['fg']
        self.bind("<FocusIn>", self.foco_entrada)
        self.bind("<FocusOut>", self.foco_saida)
        self.foco_saida()

    def foco_entrada(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self['fg'] = self.cor_normal

    def foco_saida(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self['fg'] = self.cor_placeholder

# Função para renderizar o modelo e exibi-lo em uma nova janela
def renderizar_modelo():
    # Dicionário para armazenar os valores informados (usa defaults se o usuário não alterar)
    parametros = {}
    for chave, entrada in entradas.items():
        valor_texto = entrada.get()
        if valor_texto == placeholders[chave]:
            parametros[chave] = defaults[chave]
        else:
            try:
                parametros[chave] = float(valor_texto)
            except:
                parametros[chave] = defaults[chave]

    # Desempacota os parâmetros para formatação
    alfa    = parametros['alfa']
    beta    = parametros['beta']
    gama    = parametros['gama']
    delta   = parametros['delta']
    epsilon = parametros['epsilon']
    zeta    = parametros['zeta']
    eta     = parametros['eta']
    teta    = parametros['teta']
    iota    = parametros['iota']
    kappa   = parametros['kappa']
    lam     = parametros['lambda']
    x0      = parametros['x0']
    y0      = parametros['y0']
    mu      = parametros['mu']
    nu      = parametros['nu']
    xi      = parametros['xi']
    omicron = parametros['omicron']

    # Texto do modelo com uma equação diferencial adicional (w)
    modelo_texto = f"""
Modelo Matemático Avançado para Desvalorização do Real
--------------------------------------------------------------

Sistema de Equações Diferenciais:

  dx/dt = {alfa}·x + {beta}·y - {gama}·x²·z + {delta}·sen(z)
  dy/dt = {epsilon}·(x - {x0}) - {zeta}·y² + {eta}·cos(x)
  dz/dt = {teta}·(y - {y0}) + {iota}·x·z - {kappa}·z³ + {lam}·ln(1 + x²)
  dw/dt = {mu}·x·y - {nu}·w + {xi}·sen(z·w) + {omicron}·ln(1 + |x·y|)

Variáveis:
  x(t) = Taxa de Câmbio (reais por dólar)
  y(t) = Pressão Especulativa no Mercado
  z(t) = Fluxo de Capital Internacional
  w(t) = Volatilidade ou Incerteza do Mercado

Descrição do Modelo:
  - A equação de x(t) incorpora efeitos lineares ({alfa}·x) e a influência da pressão especulativa ({beta}·y),
    com um efeito não linear (-{gama}·x²·z) acentuado pelo fluxo de capital e modulado por oscilações ({delta}·sen(z)).
  - A equação de y(t) ajusta a taxa de câmbio para um valor de equilíbrio ({x0}) com amortecimento não linear (-{zeta}·y²)
    e ciclos via {eta}·cos(x).
  - Em dz/dt, o ajuste é impulsionado pela diferença em relação ao equilíbrio de y ({y0}), efeitos multiplicativos ({iota}·x·z)
    e termos que modelam saturação e amortecimento ({kappa}·z³ e {lam}·ln(1+x²)).
  - A nova equação para w(t) introduz uma dinâmica avançada:
      • {mu}·x·y acentua a interação entre taxa de câmbio e pressão especulativa,
      • -{nu}·w representa amortecimento da volatilidade,
      • {xi}·sen(z·w) modela oscilações complexas no produto fluxo-volatilidade,
      • {omicron}·ln(1+|x·y|) limita o impacto através de um efeito logarítmico.

Este sistema, altamente não linear e acoplado, busca capturar os múltiplos feedbacks do mercado,
possivelmente explicando a desvalorização do real frente ao dólar em cenários complexos.
    """

    # Cria uma nova janela para exibir as equações renderizadas
    janela_eq = tk.Toplevel(janela)
    janela_eq.title("Equações do Modelo")
    txt_eq = tk.Text(janela_eq, wrap=tk.WORD, width=90, height=20)
    txt_eq.pack(padx=10, pady=10)
    txt_eq.insert(tk.END, modelo_texto)
    txt_eq.config(state=tk.DISABLED)

# Função para integrar o sistema e exibir resultados numéricos e plotagem
def calcular_e_plotar():
    # Coleta os parâmetros
    parametros = {}
    for chave, entrada in entradas.items():
        valor_texto = entrada.get()
        if valor_texto == placeholders[chave]:
            parametros[chave] = defaults[chave]
        else:
            try:
                parametros[chave] = float(valor_texto)
            except:
                parametros[chave] = defaults[chave]

    # Desempacota os parâmetros
    alfa    = parametros['alfa']
    beta    = parametros['beta']
    gama    = parametros['gama']
    delta   = parametros['delta']
    epsilon = parametros['epsilon']
    zeta    = parametros['zeta']
    eta     = parametros['eta']
    teta    = parametros['teta']
    iota    = parametros['iota']
    kappa   = parametros['kappa']
    lam     = parametros['lambda']
    x_eq    = parametros['x0']
    y_eq    = parametros['y0']
    mu      = parametros['mu']
    nu      = parametros['nu']
    xi      = parametros['xi']
    omicron = parametros['omicron']

    # Define o sistema de equações diferenciais avançado
    def sistema(t, u):
        x, y, z, w = u
        dx_dt = alfa * x + beta * y - gama * (x**2) * z + delta * math.sin(z)
        dy_dt = epsilon * (x - x_eq) - zeta * (y**2) + eta * math.cos(x)
        dz_dt = teta * (y - y_eq) + iota * x * z - kappa * (z**3) + lam * math.log(1 + x**2)
        dw_dt = mu * x * y - nu * w + xi * math.sin(z * w) + omicron * math.log(1 + abs(x * y))
        return [dx_dt, dy_dt, dz_dt, dw_dt]

    # Condições iniciais definidas (pode ser ajustado conforme a necessidade)
    u0 = [3.0, 0.0, 0.5, 0.1]
    t_inicial = 0
    t_final = 10
    t_eval = np.linspace(t_inicial, t_final, 1000)

    # Integração do sistema
    sol = solve_ivp(sistema, [t_inicial, t_final], u0, t_eval=t_eval, method='RK45')

    # Obtem os resultados finais com 4 dígitos de precisão
    x_final = sol.y[0, -1]
    y_final = sol.y[1, -1]
    z_final = sol.y[2, -1]
    w_final = sol.y[3, -1]
    resultados_texto = (
        f"Resultado Final em t = {t_final}:\n\n"
        f"x(t_final) = {x_final:.4f}\n"
        f"y(t_final) = {y_final:.4f}\n"
        f"z(t_final) = {z_final:.4f}\n"
        f"w(t_final) = {w_final:.4f}\n"
    )

    # Janela para exibir os resultados numéricos
    janela_result = tk.Toplevel(janela)
    janela_result.title("Resultado Numérico")
    txt_result = tk.Text(janela_result, wrap=tk.WORD, width=40, height=10)
    txt_result.pack(padx=10, pady=10)
    txt_result.insert(tk.END, resultados_texto)
    txt_result.config(state=tk.DISABLED)

    # Criação de uma nova janela para a plotagem
    janela_plot = tk.Toplevel(janela)
    janela_plot.title("Gráfico do Sistema")
    
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(sol.t, sol.y[0], label='x(t)', color='blue')
    ax.plot(sol.t, sol.y[1], label='y(t)', color='red')
    ax.plot(sol.t, sol.y[2], label='z(t)', color='green')
    ax.plot(sol.t, sol.y[3], label='w(t)', color='purple')
    ax.set_xlabel("Tempo (t)")
    ax.set_ylabel("Valor")
    ax.set_title("Evolução das Variáveis do Sistema")
    ax.legend()
    ax.grid(True)
    
    # Integra o gráfico na janela Tkinter
    canvas = FigureCanvasTkAgg(fig, master=janela_plot)
    canvas.draw()
    canvas.get_tk_widget().pack(padx=10, pady=10)

# Janela principal
janela = tk.Tk()
janela.title("Modelo Matemático para Desvalorização do Real")

# Dicionários com valores padrão e textos de placeholder para cada parâmetro
defaults = {
    'alfa': 0.1,
    'beta': 0.05,
    'gama': 0.02,
    'delta': 0.3,
    'epsilon': 0.15,
    'zeta': 0.1,
    'eta': 0.2,
    'teta': 0.05,
    'iota': 0.03,
    'kappa': 0.01,
    'lambda': 0.07,
    'x0': 3.5,    # Valor de equilíbrio para x(t)
    'y0': 0.0,    # Valor de equilíbrio para y(t)
    'mu': 0.04,
    'nu': 0.03,
    'xi': 0.02,
    'omicron': 0.01
}

placeholders = {
    'alfa': "alfa (ex: 0.1)",
    'beta': "beta (ex: 0.05)",
    'gama': "gama (ex: 0.02)",
    'delta': "delta (ex: 0.3)",
    'epsilon': "epsilon (ex: 0.15)",
    'zeta': "zeta (ex: 0.1)",
    'eta': "eta (ex: 0.2)",
    'teta': "teta (ex: 0.05)",
    'iota': "iota (ex: 0.03)",
    'kappa': "kappa (ex: 0.01)",
    'lambda': "lambda (ex: 0.07)",
    'x0': "x0 (ex: 3.5)",
    'y0': "y0 (ex: 0.0)",
    'mu': "mu (ex: 0.04)",
    'nu': "nu (ex: 0.03)",
    'xi': "xi (ex: 0.02)",
    'omicron': "omicron (ex: 0.01)"
}

entradas = {}

# Frame para os parâmetros do modelo
frame_param = tk.Frame(janela)
frame_param.pack(padx=10, pady=10)

tk.Label(frame_param, text="Insira os parâmetros do modelo:").grid(row=0, column=0, columnspan=2, pady=(0,10))

# Criação dos campos de entrada para cada parâmetro
linha = 1
for chave in defaults:
    tk.Label(frame_param, text=chave + ":").grid(row=linha, column=0, sticky="e", padx=5, pady=2)
    entrada = PlaceholderEntry(frame_param, placeholder=placeholders[chave], width=25)
    entrada.grid(row=linha, column=1, padx=5, pady=2)
    entradas[chave] = entrada
    linha += 1

# Botões para renderizar o modelo e para calcular/plotar a solução
btn_render = tk.Button(janela, text="Renderizar Modelo", command=renderizar_modelo)
btn_render.pack(pady=(10, 5))

btn_calc_plot = tk.Button(janela, text="Calcular e Plotar", command=calcular_e_plotar)
btn_calc_plot.pack(pady=(0, 10))

# Área de texto na janela principal (opcional – pode servir de log ou instrução)
texto_modelo = tk.Text(janela, wrap=tk.WORD, width=80, height=10)
texto_modelo.pack(padx=10, pady=10)
texto_modelo.insert(tk.END, "O sistema de equações será renderizado em uma nova janela ao clicar em 'Renderizar Modelo'.")
texto_modelo.config(state=tk.DISABLED)

janela.mainloop()
