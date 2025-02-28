import tkinter as tk
from tkinter import ttk
from decimal import Decimal, getcontext
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def calcular_pi(precisao: int, iteracoes: int) -> Decimal:
    getcontext().prec = precisao + 2  # margem extra para arredondamento
    soma = Decimal(0)
    for k in range(iteracoes):
        # Cálculo de cada termo da série de Chudnovsky
        termo_num = Decimal(math.factorial(6 * k)) * (Decimal(13591409) + Decimal(545140134) * k)
        termo_den = (Decimal(math.factorial(3 * k)) *
                     (Decimal(math.factorial(k)) ** 3) *
                     Decimal((-640320) ** (3 * k)))
        soma += termo_num / termo_den
    pi = Decimal(426880) * Decimal(10005).sqrt() / soma
    return +pi  # O operador '+' aplica o arredondamento atual

def atualizar_calculo():
    try:
        precisao_desejada = int(entrada_precisao.get())
    except ValueError:
        resultado_label.config(text="Por favor, insira um número inteiro para a precisão.")
        return
    # Cada termo da série contribui com cerca de 14 dígitos
    iteracoes = precisao_desejada // 14 + 1
    pi_calculado = calcular_pi(precisao_desejada, iteracoes)
    # Formata o resultado para exibir os dígitos desejados
    pi_str = str(pi_calculado)[:precisao_desejada + 2]
    resultado_label.config(text=f"π calculado: {pi_str}")

# Configuração da janela principal do tkinter
janela = tk.Tk()
janela.title("Cálculo de π com a fórmula de Chudnovsky")

# Frame para renderizar a fórmula
frame_formula = ttk.Frame(janela)
frame_formula.pack(padx=10, pady=10)

# Cria a figura do matplotlib com a fórmula em LaTeX (sem \, e \displaystyle)
figura = plt.Figure(figsize=(8, 2), dpi=100)
ax = figura.add_subplot(111)
ax.axis('off')
formula_latex = r"$\pi = \frac{426880\sqrt{10005}}{\sum_{k=0}^{\infty} \frac{(6k)! (13591409+545140134k)}{(3k)! (k!)^3 (-640320)^{3k}}}$"
ax.text(0.5, 0.5, formula_latex, horizontalalignment='center',
        verticalalignment='center', fontsize=14)
canvas_formula = FigureCanvasTkAgg(figura, master=frame_formula)
canvas_formula.draw()
canvas_formula.get_tk_widget().pack()

# Rótulo com explicação da fórmula
explicacao = (
    "Esta é a fórmula de Chudnovsky para o cálculo de π.\n"
    "Ela utiliza uma série infinita que converge rapidamente, \n"
    "sendo que cada termo da soma adiciona aproximadamente 14 dígitos de precisão."
)
label_explicacao = ttk.Label(janela, text=explicacao, justify="center")
label_explicacao.pack(padx=10, pady=10)

# Frame para entrada de precisão e botão de cálculo
frame_controle = ttk.Frame(janela)
frame_controle.pack(padx=10, pady=10)

label_precisao = ttk.Label(frame_controle, text="Digite o número de dígitos desejados:")
label_precisao.grid(row=0, column=0, padx=5, pady=5)

entrada_precisao = ttk.Entry(frame_controle, width=10)
entrada_precisao.grid(row=0, column=1, padx=5, pady=5)
entrada_precisao.insert(0, "50")  # Valor padrão: 50 dígitos

botao_calcular = ttk.Button(frame_controle, text="Calcular π", command=atualizar_calculo)
botao_calcular.grid(row=0, column=2, padx=5, pady=5)

resultado_label = ttk.Label(janela, text="π calculado: ")
resultado_label.pack(padx=10, pady=10)

janela.mainloop()
