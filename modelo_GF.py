import tkinter as tk
from tkinter import Toplevel, Text, Scrollbar
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def calcular_probabilidade():
    try:
        idade = float(entry_idade.get())
    except:
        idade = 37
    try:
        mercado_local = float(entry_mercado_local.get())
    except:
        mercado_local = 0.6
    try:
        atratividade = float(entry_atratividade.get())
    except:
        atratividade = 0.3
    try:
        status_economico = float(entry_status_economico.get())
    except:
        status_economico = 0.4
    x1 = idade - 30
    beta0 = -2
    beta1 = -0.15
    beta2 = 0.8
    beta3 = 1.2
    beta4 = 0.5
    logit = beta0 + beta1*x1 + beta2*mercado_local + beta3*atratividade + beta4*status_economico
    prob = 1/(1+np.exp(-logit))
    label_probabilidade.config(text=f"Probabilidade Calculada: {prob:.3f}")

def simular_distribuicao():
    try:
        idade = float(entry_idade.get())
    except:
        idade = 37
    try:
        mercado_local = float(entry_mercado_local.get())
    except:
        mercado_local = 0.6
    try:
        atratividade = float(entry_atratividade.get())
    except:
        atratividade = 0.3
    try:
        status_economico = float(entry_status_economico.get())
    except:
        status_economico = 0.4
    x1 = idade - 30
    n = 10000
    beta0_amostra = np.random.normal(-2, 0.5, n)
    beta1_amostra = np.random.normal(-0.15, 0.05, n)
    beta2_amostra = np.random.normal(0.8, 0.2, n)
    beta3_amostra = np.random.normal(1.2, 0.3, n)
    beta4_amostra = np.random.normal(0.5, 0.1, n)
    logit_amostra = beta0_amostra + beta1_amostra*x1 + beta2_amostra*mercado_local + beta3_amostra*atratividade + beta4_amostra*status_economico
    return 1/(1+np.exp(-logit_amostra))

def mostrar_distribuicao():
    probabilidades = simular_distribuicao()
    janela_hist = Toplevel(janela)
    janela_hist.title("Distribuição das Probabilidades")
    figura = plt.Figure(figsize=(6, 4), dpi=100)
    ax = figura.add_subplot(111)
    ax.hist(probabilidades, bins=50, density=True, alpha=0.7, color='blue')
    ax.set_xlabel('Probabilidade')
    ax.set_ylabel('Densidade')
    ax.set_title('Distribuição das Probabilidades (Monte Carlo)')
    canvas = FigureCanvasTkAgg(figura, master=janela_hist)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

def mostrar_explicacao():
    explicacao = (
        "O modelo utiliza regressão logística para estimar a chance de conseguir uma namorada. "
        "A função logística é definida por p = 1 / (1 + exp(-z)), onde z = beta0 + beta1*x1 + beta2*mercado_local + "
        "beta3*atratividade + beta4*status_economico. Os coeficientes beta determinam o peso de cada fator: "
        "idade ajustada (x1 = idade - 30), mercado local, atratividade e status econômico. O modelo é estendido com uma "
        "simulação Monte Carlo, onde cada coeficiente é amostrado de uma distribuição normal, gerando uma distribuição de "
        "probabilidades. A média dessa distribuição reflete a probabilidade estimada, considerando a incerteza dos parâmetros."
    )
    janela_explicacao = Toplevel(janela)
    janela_explicacao.title("Explicação do Modelo")
    texto = Text(janela_explicacao, wrap="word", width=80, height=10)
    texto.insert("1.0", explicacao)
    texto.config(state="disabled")
    scrollbar = Scrollbar(janela_explicacao, command=texto.yview)
    texto['yscrollcommand'] = scrollbar.set
    texto.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def limpar_campos():
    entry_idade.delete(0, tk.END)
    entry_mercado_local.delete(0, tk.END)
    entry_atratividade.delete(0, tk.END)
    entry_status_economico.delete(0, tk.END)
    label_probabilidade.config(text="Probabilidade Calculada:")

janela = tk.Tk()
janela.title("Modelo Probabilístico de Relacionamento")
frame_inputs = tk.Frame(janela)
frame_inputs.pack(pady=10)
label_idade = tk.Label(frame_inputs, text="Idade:")
label_idade.grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_idade = tk.Entry(frame_inputs)
entry_idade.grid(row=0, column=1, padx=5, pady=5)
entry_idade.insert(0, "37")
label_mercado = tk.Label(frame_inputs, text="Mercado Local (0-1):")
label_mercado.grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_mercado_local = tk.Entry(frame_inputs)
entry_mercado_local.grid(row=1, column=1, padx=5, pady=5)
entry_mercado_local.insert(0, "0.6")
label_atratividade = tk.Label(frame_inputs, text="Atratividade (0-1):")
label_atratividade.grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_atratividade = tk.Entry(frame_inputs)
entry_atratividade.grid(row=2, column=1, padx=5, pady=5)
entry_atratividade.insert(0, "0.3")
label_status = tk.Label(frame_inputs, text="Status Econômico (0-1):")
label_status.grid(row=3, column=0, padx=5, pady=5, sticky="e")
entry_status_economico = tk.Entry(frame_inputs)
entry_status_economico.grid(row=3, column=1, padx=5, pady=5)
entry_status_economico.insert(0, "0.4")
botao_calcular = tk.Button(janela, text="Calcular Probabilidade", command=calcular_probabilidade, font=("Arial", 12))
botao_calcular.pack(pady=5)
label_probabilidade = tk.Label(janela, text="Probabilidade Calculada:", font=("Arial", 14))
label_probabilidade.pack(pady=10)
botao_hist = tk.Button(janela, text="Mostrar Distribuição", command=mostrar_distribuicao, font=("Arial", 12))
botao_hist.pack(pady=5)
botao_explicacao = tk.Button(janela, text="Explicar Modelo", command=mostrar_explicacao, font=("Arial", 12))
botao_explicacao.pack(pady=5)
botao_limpar = tk.Button(janela, text="Limpar Campos", command=limpar_campos, font=("Arial", 12))
botao_limpar.pack(pady=5)
janela.mainloop()
