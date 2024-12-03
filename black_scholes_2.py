import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math
from scipy.stats import norm

# Função para calcular a distribuição cumulativa normal usando scipy
def distribuicao_normal(x):
    return norm.cdf(x)

# Função para calcular a fórmula de Black-Scholes para Call e Put
def black_scholes(S, K, T, r, sigma, q):
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    N_d1 = distribuicao_normal(d1)
    N_d2 = distribuicao_normal(d2)
    N_neg_d1 = distribuicao_normal(-d1)
    N_neg_d2 = distribuicao_normal(-d2)
    
    # Preço da Opção Call
    call = S * math.exp(-q * T) * N_d1 - K * math.exp(-r * T) * N_d2
    
    # Preço da Opção Put
    put = K * math.exp(-r * T) * N_neg_d2 - S * math.exp(-q * T) * N_neg_d1
    
    return round(call, 8), round(put, 8)

# Funções para calcular as Gregas
def calcular_greeks(S, K, T, r, sigma, q):
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    delta_call = math.exp(-q * T) * distribuicao_normal(d1)
    delta_put = math.exp(-q * T) * (distribuicao_normal(d1) - 1)
    gamma = (distribuicao_normal(d1)) / (S * sigma * math.sqrt(T))
    theta_call = (- (S * sigma * math.exp(-q * T) * distribuicao_normal(d1)) / (2 * math.sqrt(T))
                  - r * K * math.exp(-r * T) * distribuicao_normal(d2)
                  + q * S * math.exp(-q * T) * distribuicao_normal(d1))
    theta_put = (- (S * sigma * math.exp(-q * T) * distribuicao_normal(d1)) / (2 * math.sqrt(T))
                 + r * K * math.exp(-r * T) * distribuicao_normal(-d2)
                 - q * S * math.exp(-q * T) * distribuicao_normal(-d1))
    vega = S * math.sqrt(T) * math.exp(-q * T) * distribuicao_normal(d1)
    rho_call = K * T * math.exp(-r * T) * distribuicao_normal(d2)
    rho_put = -K * T * math.exp(-r * T) * distribuicao_normal(-d2)
    
    return {
        'Delta Call': round(delta_call, 8),
        'Delta Put': round(delta_put, 8),
        'Gamma': round(gamma, 8),
        'Theta Call': round(theta_call, 8),
        'Theta Put': round(theta_put, 8),
        'Vega': round(vega, 8),
        'Rho Call': round(rho_call, 8),
        'Rho Put': round(rho_put, 8)
    }

# Função para plotar os gráficos
def plotar_black_scholes():
    try:
        S = float(entrada_S.get())
        K = float(entrada_K.get())
        T = float(entrada_T.get())
        r = float(entrada_r.get())
        sigma = float(entrada_sigma.get())
        q = float(entrada_q.get())
    except ValueError:
        messagebox.showerror("Entrada Inválida", "Por favor, insira valores numéricos válidos.")
        return

    # Gerar uma gama de preços do ativo subjacente
    S_values = np.linspace(S * 0.5, S * 1.5, 400)
    call_prices = []
    put_prices = []
    deltas_call = []
    deltas_put = []
    gammas = []
    thetas_call = []
    thetas_put = []
    vegas = []
    rhos_call = []
    rhos_put = []
    
    for s in S_values:
        call, put = black_scholes(s, K, T, r, sigma, q)
        call_prices.append(call)
        put_prices.append(put)
        
        greeks = calcular_greeks(s, K, T, r, sigma, q)
        deltas_call.append(greeks['Delta Call'])
        deltas_put.append(greeks['Delta Put'])
        gammas.append(greeks['Gamma'])
        thetas_call.append(greeks['Theta Call'])
        thetas_put.append(greeks['Theta Put'])
        vegas.append(greeks['Vega'])
        rhos_call.append(greeks['Rho Call'])
        rhos_put.append(greeks['Rho Put'])
    
    # Limpar a figura anterior
    fig.clear()
    
    # Criar subplots
    ax1 = fig.add_subplot(2, 1, 1)
    ax1.plot(S_values, call_prices, label='Call', color='blue')
    ax1.plot(S_values, put_prices, label='Put', color='red')
    ax1.set_xlabel('Preço do Ativo Subjacente (S)')
    ax1.set_ylabel('Preço da Opção')
    ax1.set_title('Preços das Opções Call e Put')
    ax1.legend()
    ax1.grid(True)
    
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.plot(S_values, deltas_call, label='Delta Call', color='cyan')
    ax2.plot(S_values, deltas_put, label='Delta Put', color='magenta')
    ax2.plot(S_values, gammas, label='Gamma', color='green')
    ax2.plot(S_values, thetas_call, label='Theta Call', color='orange')
    ax2.plot(S_values, thetas_put, label='Theta Put', color='purple')
    ax2.plot(S_values, vegas, label='Vega', color='brown')
    ax2.plot(S_values, rhos_call, label='Rho Call', color='grey')
    ax2.plot(S_values, rhos_put, label='Rho Put', color='black')
    ax2.set_xlabel('Preço do Ativo Subjacente (S)')
    ax2.set_ylabel('Valor das Gregas')
    ax2.set_title('Gregas das Opções')
    ax2.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax2.grid(True)
    
    plt.tight_layout()
    canvas.draw()

# Função para mostrar a explicação
def mostrar_explicacao():
    mensagem = (
        "Este programa simula a equação de Black-Scholes para precificação de opções financeiras.\n\n"
        "Parâmetros de entrada:\n"
        "- Preço do Ativo Subjacente (S)\n"
        "- Preço de Exercício da Opção (K)\n"
        "- Tempo até o Vencimento (T) em anos\n"
        "- Taxa Livre de Risco (r)\n"
        "- Volatilidade do Ativo (sigma)\n"
        "- Yield de Dividendos (q)\n\n"
        "Após inserir os valores, clique em 'Plotar' para visualizar o preço das opções Call e Put, bem como suas Gregas em função do preço do ativo subjacente."
    )
    messagebox.showinfo("Explicação do Programa", mensagem)

# Criar a janela principal
janela = tk.Tk()
janela.title("Simulação Avançada da Equação de Black-Scholes")
janela.geometry("1000x800")

# Legenda em azul com o nome do autor
legenda = tk.Label(janela, text="Autor: Luiz Tiago Wilcke", font=("Arial", 14), fg="blue")
legenda.pack(pady=10)

# Renderizar a equação de Black-Scholes usando matplotlib
fig_eq = plt.Figure(figsize=(6, 1), dpi=100)
ax_eq = fig_eq.add_subplot(111)
ax_eq.axis('off')
equacao = r'$C = S e^{-qT} N(d_1) - K e^{-rT} N(d_2)$' + "\n" + r'$P = K e^{-rT} N(-d_2) - S e^{-qT} N(-d_1)$'
ax_eq.text(0.5, 0.5, equacao, horizontalalignment='center', verticalalignment='center', fontsize=16)
canvas_eq = FigureCanvasTkAgg(fig_eq, master=janela)
canvas_eq.draw()
canvas_eq.get_tk_widget().pack()

# Frame para os campos de entrada
frame_entrada = tk.Frame(janela)
frame_entrada.pack(pady=20)

# Função para criar um rótulo e uma entrada
def criar_campo(parent, texto, row):
    rotulo = tk.Label(parent, text=texto, font=("Arial", 12))
    rotulo.grid(row=row, column=0, padx=10, pady=5, sticky='e')
    entrada = tk.Entry(parent, font=("Arial", 12))
    entrada.grid(row=row, column=1, padx=10, pady=5)
    return entrada

# Campos de entrada com variáveis em português
entrada_S = criar_campo(frame_entrada, "Preço do Ativo (S):", 0)
entrada_K = criar_campo(frame_entrada, "Preço de Exercício (K):", 1)
entrada_T = criar_campo(frame_entrada, "Tempo até Vencimento (T) em anos:", 2)
entrada_r = criar_campo(frame_entrada, "Taxa Livre de Risco (r):", 3)
entrada_sigma = criar_campo(frame_entrada, "Volatilidade (sigma):", 4)
entrada_q = criar_campo(frame_entrada, "Yield de Dividendos (q):", 5)

# Botão para plotar o gráfico
botao_plotar = tk.Button(janela, text="Plotar", font=("Arial", 12), command=plotar_black_scholes)
botao_plotar.pack(pady=10)

# Botão para mostrar a explicação
botao_explicacao = tk.Button(janela, text="Explicação", font=("Arial", 12), command=mostrar_explicacao)
botao_explicacao.pack(pady=5)

# Frame para o gráfico
frame_grafico = tk.Frame(janela)
frame_grafico.pack(fill=tk.BOTH, expand=True)

fig = plt.Figure(figsize=(10, 8), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Iniciar a aplicação
janela.mainloop()
