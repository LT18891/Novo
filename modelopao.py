import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

def simular():
    """Lê os parâmetros da interface, simula o modelo (com α = 1) e plota o resultado."""
    try:
        alpha = float(entry_alpha.get())
        tau = float(entry_tau.get())
        lambda_val = float(entry_lambda.get())
        a = float(entry_a.get())
        b = float(entry_b.get())
        c = float(entry_c.get())
        d = float(entry_d.get())
        p0 = float(entry_p0.get())
        I_val = float(entry_I.get())
        T = float(entry_T.get())
        dt = float(entry_dt.get())
    except ValueError:
        messagebox.showerror("Erro", "Verifique os valores de entrada!")
        return

    if alpha != 1.0:
        messagebox.showwarning("Aviso", "Simulação implementada apenas para α = 1.0 (derivada clássica).")
        return

    # Definindo os passos e criando os arrays de tempo e preço
    n_steps = int(T/dt) + 1
    t_values = np.linspace(0, T, n_steps)
    p_values = np.zeros(n_steps)
    p_values[0] = p0

    # Método de Euler com atraso:
    for i in range(1, n_steps):
        t = t_values[i]
        # Se t-tau for negativo, usamos o valor inicial p0 (função histórica constante)
        if t - tau < 0:
            p_delay = p0
        else:
            idx_delay = int((t - tau) / dt)
            p_delay = p_values[idx_delay]
        # Equação diferencial: p'(t) = λ * [(a - b·p(t-τ)) - (c + d·p(t))] + I
        dp_dt = lambda_val * ((a - b * p_delay) - (c + d * p_values[i-1])) + I_val
        p_values[i] = p_values[i-1] + dt * dp_dt

    # Atualiza o gráfico
    fig.clear()
    ax = fig.add_subplot(111)
    ax.plot(t_values, p_values, label="Preço do Pão")
    ax.set_xlabel("Tempo")
    ax.set_ylabel("Preço")
    ax.set_title("Simulação do Modelo de Preço do Pão")
    ax.legend()
    canvas.draw()

def exibir_modelo():
    """Exibe uma janela com as equações renderizadas e uma explicação do modelo."""
    win_modelo = tk.Toplevel(root)
    win_modelo.title("Detalhes do Modelo")
    
    # Frame para a figura com a equação (usando Matplotlib)
    frame_fig = tk.Frame(win_modelo)
    frame_fig.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
    
    # Aumentamos um pouco o tamanho da figura para acomodar melhor a equação e o texto
    fig_modelo = plt.Figure(figsize=(6, 4))
    ax_modelo = fig_modelo.add_subplot(111)
    ax_modelo.axis('off')
    
    # Texto com a equação em notação matemática (MathText do Matplotlib)
    eq_text = r"$D_t^\alpha p(t) = \lambda \left[ (a - b\,p(t-\tau)) - (c + d\,p(t)) \right] + I(t)$"
    # Ajuste para a fórmula ficar no topo (y=0.8)
    ax_modelo.text(0.5, 0.8, eq_text,
                   horizontalalignment='center', 
                   fontsize=16, 
                   transform=ax_modelo.transAxes)
    
    # Texto explicando os símbolos, um pouco mais abaixo (y=0.4)
    ax_modelo.text(0.5, 0.4,
                   "Onde:\n"
                   "  p(t) = preço do pão no tempo t\n"
                   "  α = ordem da derivada (memória do sistema)\n"
                   "  λ = taxa de ajuste\n"
                   "  a, b = parâmetros da demanda\n"
                   "  c, d = parâmetros da oferta\n"
                   "  τ = atraso na percepção de preço\n"
                   "  I(t) = influências externas",
                   horizontalalignment='center',
                   fontsize=10, 
                   transform=ax_modelo.transAxes)
    
    canvas_modelo = FigureCanvasTkAgg(fig_modelo, master=frame_fig)
    canvas_modelo.draw()
    canvas_modelo.get_tk_widget().pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
    
    # Frame para a explicação adicional em texto (no próprio Tkinter)
    frame_txt = tk.Frame(win_modelo)
    frame_txt.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    txt_explicacao = tk.Text(frame_txt, wrap=tk.WORD)
    explicacao = (
        "Este modelo descreve a dinâmica do preço do pão considerando:\n"
        "- Efeito de memória (derivada fracionária de ordem α),\n"
        "- Atraso na percepção do preço (p(t-τ)),\n"
        "- Diferença entre demanda e oferta, onde a demanda depende do preço passado "
        "e a oferta do preço atual,\n"
        "- Influências externas representadas por I(t).\n\n"
        "A simulação atual utiliza α = 1, ou seja, a derivada clássica, e foi resolvida "
        "por meio do método de Euler com atraso."
    )
    txt_explicacao.insert(tk.END, explicacao)
    txt_explicacao.config(state=tk.DISABLED)
    txt_explicacao.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Criação da janela principal
root = tk.Tk()
root.title("Calculadora do Modelo de Preço do Pão - Autor: Luiz Tiago Wilcke")

# Frame para os parâmetros de entrada
frame_inputs = tk.Frame(root)
frame_inputs.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

# Lista de rótulos e valores padrão (em português)
labels = [
    "Ordem da Derivada (α):",
    "Atraso (τ):",
    "Taxa de Ajuste (λ):",
    "Parâmetro Demanda (a):",
    "Coeficiente Demanda (b):",
    "Parâmetro Oferta (c):",
    "Coeficiente Oferta (d):",
    "Condição Inicial (p0):",
    "Influência Externa (I):",
    "Tempo Total (T):",
    "Passo (dt):"
]
valores_padrao = ["1.0", "1.0", "1.0", "100", "1.0", "20", "0.5", "50", "0", "50", "0.1"]

entries = []
for i, texto in enumerate(labels):
    lbl = tk.Label(frame_inputs, text=texto)
    lbl.grid(row=i, column=0, sticky="w", padx=5, pady=2)
    ent = tk.Entry(frame_inputs)
    ent.grid(row=i, column=1, padx=5, pady=2)
    ent.insert(0, valores_padrao[i])
    entries.append(ent)

# Atribuindo cada entrada a uma variável
entry_alpha = entries[0]
entry_tau = entries[1]
entry_lambda = entries[2]
entry_a = entries[3]
entry_b = entries[4]
entry_c = entries[5]
entry_d = entries[6]
entry_p0 = entries[7]
entry_I = entries[8]
entry_T = entries[9]
entry_dt = entries[10]

# Botão para simulação
btn_simular = tk.Button(root, text="Simular", command=simular)
btn_simular.pack(side=tk.TOP, pady=5)

# Botão para exibir os detalhes do modelo
btn_modelo = tk.Button(root, text="Exibir Modelo", command=exibir_modelo)
btn_modelo.pack(side=tk.TOP, pady=5)

# Frame para a plotagem
frame_plot = tk.Frame(root)
frame_plot.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Criação da figura do Matplotlib para a simulação
fig = plt.Figure(figsize=(6, 4))
ax = fig.add_subplot(111)
ax.set_xlabel("Tempo")
ax.set_ylabel("Preço")
ax.set_title("Simulação do Modelo de Preço do Pão")
canvas = FigureCanvasTkAgg(fig, master=frame_plot)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Legenda na janela com o nome do autor
lbl_autor = tk.Label(root, text="Autor: Luiz Tiago Wilcke", font=("Arial", 10, "italic"))
lbl_autor.pack(side=tk.BOTTOM, pady=5)

root.mainloop()
