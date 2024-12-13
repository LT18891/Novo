import tkinter as tk
from tkinter import ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def resolver_modelo_simplificado(s, alpha, n, delta, k0, T, dt):
    # EDO: dk/dt = s*k^alpha - (n+delta)*k
    # Vamos usar RK4 para resolver numericamente
    t_values = np.arange(0, T+dt, dt)
    k_values = np.zeros_like(t_values)
    k_values[0] = k0

    def f(k):
        return s*(k**alpha) - (n+delta)*k

    for i in range(len(t_values)-1):
        k = k_values[i]
        k1 = f(k)
        k2 = f(k + dt*k1/2)
        k3 = f(k + dt*k2/2)
        k4 = f(k + dt*k3)
        k_values[i+1] = k + (dt/6)*(k1 + 2*k2 + 2*k3 + k4)

    # Estado estacionário
    k_estrela = (s/(n+delta))**(1/(1-alpha))
    return t_values, k_values, k_estrela

def atualizar_plot():
    # Obter valores do usuário
    s = float(entry_taxa_poupanca.get().replace(',', '.'))
    alpha = float(entry_alfa.get().replace(',', '.'))
    n = float(entry_taxa_crescimento_populacao.get().replace(',', '.'))
    delta = float(entry_taxa_depreciacao.get().replace(',', '.'))
    k0 = float(entry_condicao_inicial.get().replace(',', '.'))
    T = float(entry_tempo_final.get().replace(',', '.'))
    dt = float(entry_passo.get().replace(',', '.'))

    t_values, k_values, k_estrela = resolver_modelo_simplificado(s, alpha, n, delta, k0, T, dt)

    # Atualizar o gráfico
    ax.clear()
    ax.plot(t_values, k_values, label='k(t)')
    ax.axhline(y=k_estrela, color='r', linestyle='--', label='k* (estado estacionário)')
    ax.set_xlabel('Tempo (anos)')
    ax.set_ylabel('Capital por Trabalhador (k)')
    ax.set_title('Evolução do capital por trabalhador')
    ax.legend()
    canvas.draw()

    # Atualizar resultado numérico com 10 dígitos de precisão
    resultado_str = f"k(T) = {k_values[-1]:.10f}\n" \
                    f"k* = {k_estrela:.10f}"
    label_resultado.config(text=resultado_str)

# Criação da janela principal
root = tk.Tk()
root.title("Modelo de Crescimento Econômico (Solow)")

# Frame de entrada de dados
frame_inputs = ttk.Frame(root)
frame_inputs.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

label_info = ttk.Label(frame_inputs, text="Insira os parâmetros do modelo:")
label_info.pack()

label_taxa_poupanca = ttk.Label(frame_inputs, text="Taxa de poupança (s):")
label_taxa_poupanca.pack()
entry_taxa_poupanca = ttk.Entry(frame_inputs)
entry_taxa_poupanca.insert(0, "0,20")
entry_taxa_poupanca.pack()

label_alfa = ttk.Label(frame_inputs, text="Alfa (α):")
label_alfa.pack()
entry_alfa = ttk.Entry(frame_inputs)
entry_alfa.insert(0, "0,3333333333")
entry_alfa.pack()

label_taxa_crescimento_populacao = ttk.Label(frame_inputs, text="Taxa crescimento pop. (n):")
label_taxa_crescimento_populacao.pack()
entry_taxa_crescimento_populacao = ttk.Entry(frame_inputs)
entry_taxa_crescimento_populacao.insert(0, "0,01")
entry_taxa_crescimento_populacao.pack()

label_taxa_depreciacao = ttk.Label(frame_inputs, text="Taxa depreciação (δ):")
label_taxa_depreciacao.pack()
entry_taxa_depreciacao = ttk.Entry(frame_inputs)
entry_taxa_depreciacao.insert(0, "0,05")
entry_taxa_depreciacao.pack()

label_condicao_inicial = ttk.Label(frame_inputs, text="Condição inicial k(0):")
label_condicao_inicial.pack()
entry_condicao_inicial = ttk.Entry(frame_inputs)
entry_condicao_inicial.insert(0, "1")
entry_condicao_inicial.pack()

label_tempo_final = ttk.Label(frame_inputs, text="Tempo final (T):")
label_tempo_final.pack()
entry_tempo_final = ttk.Entry(frame_inputs)
entry_tempo_final.insert(0, "50")
entry_tempo_final.pack()

label_passo = ttk.Label(frame_inputs, text="Passo (dt):")
label_passo.pack()
entry_passo = ttk.Entry(frame_inputs)
entry_passo.insert(0, "0,1")
entry_passo.pack()

button_calcular = ttk.Button(frame_inputs, text="Calcular", command=atualizar_plot)
button_calcular.pack(pady=5)

label_resultado = ttk.Label(frame_inputs, text="Resultado aparecerá aqui")
label_resultado.pack(pady=5)

# Frame para a plotagem
frame_plot = ttk.Frame(root)
frame_plot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

fig = Figure(figsize=(5,4), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=frame_plot)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Frame para exibir fórmulas
frame_formulas = ttk.Frame(root)
frame_formulas.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

label_formulas_titulo = ttk.Label(frame_formulas, text="Fórmulas Utilizadas:")
label_formulas_titulo.pack()

# Criar uma figura com as fórmulas
fig_formulas = Figure(figsize=(3,3), dpi=100)
axf = fig_formulas.add_subplot(111)
axf.axis('off')
axf.text(0.05,0.9, r'$Y = K^{\alpha} L^{1-\alpha}$', fontsize=12, va='top')
axf.text(0.05,0.7, r'$k = \frac{K}{L}$', fontsize=12, va='top')
axf.text(0.05,0.5, r'$\frac{dk}{dt} = s k^{\alpha} - (n+\delta) k$', fontsize=12, va='top')
axf.text(0.05,0.3, r'$k^{*} = \left(\frac{s}{n+\delta}\right)^{\frac{1}{1-\alpha}}$', fontsize=12, va='top')

canvas_formulas = FigureCanvasTkAgg(fig_formulas, master=frame_formulas)
canvas_formulas_widget = canvas_formulas.get_tk_widget()
canvas_formulas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

root.mainloop()
