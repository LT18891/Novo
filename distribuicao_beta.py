import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy.stats import beta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def calcular_e_plotar():
    try:
        alfa = float(entry_alfa.get())
        beta_param = float(entry_beta.get())
        pontos = int(entry_pontos.get())
    except ValueError:
        messagebox.showerror("Erro de Entrada", "Por favor, insira valores numéricos válidos para α, β e pontos.")
        return

    # Validação dos parâmetros
    if alfa <= 0 or beta_param <= 0:
        messagebox.showerror("Erro de Validação", "Os valores de α e β devem ser maiores que zero.")
        return
    if pontos <= 0:
        messagebox.showerror("Erro de Validação", "O número de pontos deve ser um inteiro positivo.")
        return

    # Gerando valores de x no intervalo [0, 1]
    x = np.linspace(0, 1, pontos)
    
    # Calculando a função de densidade de probabilidade da distribuição Beta
    y = beta.pdf(x, alfa, beta_param)

    # Cálculo de algumas estatísticas
    media = beta.mean(alfa, beta_param)
    variancia = beta.var(alfa, beta_param)
    if alfa > 1 and beta_param > 1:
        moda = (alfa - 1) / (alfa + beta_param - 2)
        moda_str = f"{moda:.4f}"
    else:
        moda_str = "Indefinida"

    # Atualizando as estatísticas na interface
    label_media_valor.config(text=f"{media:.4f}")
    label_variancia_valor.config(text=f"{variancia:.4f}")
    label_moda_valor.config(text=moda_str)

    # Plotando a distribuição Beta
    fig.clear()
    ax = fig.add_subplot(111)
    ax.plot(x, y, 'b-', label=f'Beta({alfa}, {beta_param})')
    ax.fill_between(x, y, color='skyblue', alpha=0.4)
    ax.set_title('Distribuição Beta para Participação de Mercado')
    ax.set_xlabel('Participação de Mercado')
    ax.set_ylabel('Densidade de Probabilidade')
    ax.legend()
    ax.grid(True)
    canvas.draw()

# Configuração da Janela Principal
janela = tk.Tk()
janela.title("Distribuição Beta - Participação de Mercado")
janela.geometry("800x600")
janela.resizable(False, False)

# Frame para Entrada de Dados
frame_entrada = ttk.LabelFrame(janela, text="Parâmetros da Distribuição Beta")
frame_entrada.pack(fill="x", padx=10, pady=10)

# Campo para α (Alfa)
label_alfa = ttk.Label(frame_entrada, text="α (alfa):")
label_alfa.grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_alfa = ttk.Entry(frame_entrada)
entry_alfa.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# Campo para β (Beta)
label_beta = ttk.Label(frame_entrada, text="β (beta):")
label_beta.grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_beta = ttk.Entry(frame_entrada)
entry_beta.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Campo para Número de Pontos
label_pontos = ttk.Label(frame_entrada, text="Número de Pontos:")
label_pontos.grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_pontos = ttk.Entry(frame_entrada)
entry_pontos.grid(row=2, column=1, padx=5, pady=5, sticky="w")
entry_pontos.insert(0, "1000")  # Valor padrão

# Botão para Calcular e Plotar
botao_calcular = ttk.Button(frame_entrada, text="Calcular e Plotar", command=calcular_e_plotar)
botao_calcular.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

# Frame para Exibição de Estatísticas
frame_estatisticas = ttk.LabelFrame(janela, text="Estatísticas da Distribuição Beta")
frame_estatisticas.pack(fill="x", padx=10, pady=10)

# Média
label_media = ttk.Label(frame_estatisticas, text="Média:")
label_media.grid(row=0, column=0, padx=5, pady=5, sticky="e")
label_media_valor = ttk.Label(frame_estatisticas, text="N/A")
label_media_valor.grid(row=0, column=1, padx=5, pady=5, sticky="w")

# Variância
label_variancia = ttk.Label(frame_estatisticas, text="Variância:")
label_variancia.grid(row=1, column=0, padx=5, pady=5, sticky="e")
label_variancia_valor = ttk.Label(frame_estatisticas, text="N/A")
label_variancia_valor.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Moda
label_moda = ttk.Label(frame_estatisticas, text="Moda:")
label_moda.grid(row=2, column=0, padx=5, pady=5, sticky="e")
label_moda_valor = ttk.Label(frame_estatisticas, text="N/A")
label_moda_valor.grid(row=2, column=1, padx=5, pady=5, sticky="w")

# Frame para Plotagem
frame_plot = ttk.LabelFrame(janela, text="Gráfico da Distribuição Beta")
frame_plot.pack(fill="both", expand=True, padx=10, pady=10)

# Configuração do Gráfico Matplotlib
fig, ax = plt.subplots(figsize=(6,4))
canvas = FigureCanvasTkAgg(fig, master=frame_plot)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True)

# Iniciar a Aplicação
janela.mainloop()
