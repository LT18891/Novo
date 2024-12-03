import tkinter as tk
from tkinter import messagebox
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Importação correta

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', default=None, **kwargs):
        super().__init__(master, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_color = self['fg']
        self.default = default if default is not None else ''

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        if not self.get():
            self.insert(0, self.placeholder)
            self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

# Função que define o sistema de equações de primeira ordem
def equacoes_diferenciais(t, y, p, q, a, b, c, d, e):
    R, dR_dt = y
    d2R_dt2 = a * np.exp(b * t) + c * np.cos(d * t) + (e * R**2) / (1 + R**2) - p * dR_dt - q * R
    return [dR_dt, d2R_dt2]

# Função para calcular R(t) e plotar em uma nova janela
def calcular():
    try:
        # Função para obter valores, tratando placeholders
        def obter_valor(entry, valor_default=0.0):
            texto = entry.get()
            if texto == entry.placeholder and entry['fg'] == 'grey':
                return valor_default
            return float(texto)

        p = obter_valor(entrada_p, 0.5)
        q = obter_valor(entrada_q, 1.2)
        a = obter_valor(entrada_a, 0.3)
        b = obter_valor(entrada_b, 0.1)
        c = obter_valor(entrada_c, 0.4)
        d = obter_valor(entrada_d, 0.2)
        e = obter_valor(entrada_e, 0.05)
        R0 = obter_valor(entrada_R0, 4.0)
        dR0 = obter_valor(entrada_dR0, 0.0)
        t_final = obter_valor(entrada_t, 50.0)

        # Resolver a equação diferencial
        solucao = solve_ivp(
            equacoes_diferenciais, 
            [0, t_final], 
            [R0, dR0], 
            args=(p, q, a, b, c, d, e), 
            dense_output=True
        )
        t_vals = np.linspace(0, t_final, 500)
        R_vals, dR_vals = solucao.sol(t_vals)

        resultado_label.config(text=f"Valor do Real em t={t_final}: {R_vals[-1]:.4f}")

        # Criar uma nova janela para o gráfico
        janela_plot = tk.Toplevel(janela)
        janela_plot.title("Gráfico da Solução")

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(t_vals, R_vals, label='R(t)', color='blue')
        ax.set_xlabel('Tempo (t)')
        ax.set_ylabel('Valor do Real (R)')
        ax.set_title('Solução da Equação Diferencial Complexa')
        ax.legend()
        fig.tight_layout()

        # Integrar o gráfico na nova janela Tkinter
        canvas = FigureCanvasTkAgg(fig, master=janela_plot)  # Uso correto de FigureCanvasTkAgg
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Botão para fechar a janela do gráfico
        botao_fechar = tk.Button(janela_plot, text="Fechar", command=janela_plot.destroy)
        botao_fechar.pack(pady=10)

    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira valores válidos.")

# Criar a janela principal
janela = tk.Tk()
janela.title("Calculadora da Taxa de Câmbio Dólar/Real - Equação Complexa")

# Configurar o grid
for i in range(16):
    janela.rowconfigure(i, pad=5)
for i in range(2):
    janela.columnconfigure(i, pad=5)

# Criar os campos de entrada com placeholders
tk.Label(janela, text="Coeficiente p (amortecimento):").grid(row=0, column=0, sticky='e')
entrada_p = PlaceholderEntry(janela, placeholder="Ex: 0.5")
entrada_p.grid(row=0, column=1)

tk.Label(janela, text="Coeficiente q (rigidez):").grid(row=1, column=0, sticky='e')
entrada_q = PlaceholderEntry(janela, placeholder="Ex: 1.2")
entrada_q.grid(row=1, column=1)

tk.Label(janela, text="Coeficiente a:").grid(row=2, column=0, sticky='e')
entrada_a = PlaceholderEntry(janela, placeholder="Ex: 0.3")
entrada_a.grid(row=2, column=1)

tk.Label(janela, text="Coeficiente b:").grid(row=3, column=0, sticky='e')
entrada_b = PlaceholderEntry(janela, placeholder="Ex: 0.1")
entrada_b.grid(row=3, column=1)

tk.Label(janela, text="Coeficiente c:").grid(row=4, column=0, sticky='e')
entrada_c = PlaceholderEntry(janela, placeholder="Ex: 0.4")
entrada_c.grid(row=4, column=1)

tk.Label(janela, text="Coeficiente d:").grid(row=5, column=0, sticky='e')
entrada_d = PlaceholderEntry(janela, placeholder="Ex: 0.2")
entrada_d.grid(row=5, column=1)

tk.Label(janela, text="Coeficiente e:").grid(row=6, column=0, sticky='e')
entrada_e = PlaceholderEntry(janela, placeholder="Ex: 0.05")
entrada_e.grid(row=6, column=1)

tk.Label(janela, text="Valor Inicial R₀:").grid(row=7, column=0, sticky='e')
entrada_R0 = PlaceholderEntry(janela, placeholder="Ex: 4.0")
entrada_R0.grid(row=7, column=1)

tk.Label(janela, text="Valor Inicial dR₀/dt:").grid(row=8, column=0, sticky='e')
entrada_dR0 = PlaceholderEntry(janela, placeholder="Ex: 0.0")
entrada_dR0.grid(row=8, column=1)

tk.Label(janela, text="Tempo t:").grid(row=9, column=0, sticky='e')
entrada_t = PlaceholderEntry(janela, placeholder="Ex: 50.0")
entrada_t.grid(row=9, column=1)

# Botão de cálculo
botao_calcular = tk.Button(janela, text="Calcular", command=calcular)
botao_calcular.grid(row=10, column=0, columnspan=2, pady=10)

# Label para mostrar o resultado
resultado_label = tk.Label(janela, text="Valor do Real em t=: ")
resultado_label.grid(row=11, column=0, columnspan=2, pady=5)

# Área para exibir a equação (mantida na janela principal)
fig_eq, ax_eq = plt.subplots(figsize=(5, 2))
fig_eq.patch.set_visible(False)
ax_eq.axis('off')
equacao = r"$\frac{d^2R}{dt^2} + p \cdot \frac{dR}{dt} + q \cdot R = a \cdot e^{b \cdot t} + c \cdot \cos(d \cdot t) + \frac{e \cdot R^2}{1 + R^2}$"
ax_eq.text(0.5, 0.5, equacao, fontsize=12, ha='center', va='center')
canvas_eq = FigureCanvasTkAgg(fig_eq, master=janela)  # Uso correto de FigureCanvasTkAgg
canvas_eq.draw()
canvas_eq.get_tk_widget().grid(row=12, column=0, columnspan=2, pady=10)

# Legenda do autor
autor_label = tk.Label(janela, text="Autor: Luiz Tiago Wilcke", fg="blue")
autor_label.grid(row=13, column=0, columnspan=2, pady=5)

# Pequena explicação
explicacao = (
    "Esta calculadora utiliza uma equação diferencial complexa de segunda ordem para estimar a "
    "taxa de câmbio do dólar em relação ao real. Insira os coeficientes p, q, a, b, c, d, e, "
    "o valor inicial R₀, a derivada inicial dR₀/dt e o tempo t para calcular o valor projetado. "
    "A solução é plotada graficamente em uma nova janela."
)
tk.Label(janela, text=explicacao, wraplength=500, justify="left").grid(row=14, column=0, columnspan=2, padx=10, pady=10)

# Iniciar o loop da interface
janela.mainloop()
