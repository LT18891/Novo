import tkinter as tk
import tkinter as tk
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.integrate import solve_ivp

k0 = 1e-3
alfa = 2.5
beta = 0.2
gamma = 0.1
p = 1.5
q = 4.0
a_const = 1e-2
b_const = 1e-2
c_const = 1e-3
d_const = 1e-3
e_const = 1e-4
r_exp = 3.5
X_crit = 0.7

janela_equacoes = None
janela_evolucao = None

def sistema_ode(t, variaveis, k, p, q, a, b, c, d, e, r):
    X, T, L = variaveis
    dX_dt = -k * (X ** p) * (T ** q)
    dT_dt = a * (1 - T) + b * (1 - X) + c * (L - 1)
    dL_dt = d * (T ** r) - e * L
    return [dX_dt, dT_dt, dL_dt]

def evento_fim(t, variaveis, *args):
    return variaveis[0] - X_crit
evento_fim.terminal = True
evento_fim.direction = -1

def criar_janela_equacoes():
    global janela_equacoes, figura_ode, eixo_ode, figura_k, eixo_k, canvas_ode, canvas_k
    if janela_equacoes is None or not tk.Toplevel.winfo_exists(janela_equacoes):
        janela_equacoes = tk.Toplevel(root)
        janela_equacoes.title("Equações do Sistema")
        figura_ode, eixo_ode = plt.subplots(figsize=(6, 2))
        eixo_ode.axis('off')
        canvas_ode = FigureCanvasTkAgg(figura_ode, master=janela_equacoes)
        canvas_ode.get_tk_widget().pack(pady=5)
        figura_k, eixo_k = plt.subplots(figsize=(6, 2))
        eixo_k.axis('off')
        canvas_k = FigureCanvasTkAgg(figura_k, master=janela_equacoes)
        canvas_k.get_tk_widget().pack(pady=5)

def criar_janela_evolucao():
    global janela_evolucao, figura_evolucao, eixo_evolucao, canvas_evolucao
    if janela_evolucao is None or not tk.Toplevel.winfo_exists(janela_evolucao):
        janela_evolucao = tk.Toplevel(root)
        janela_evolucao.title("Evolução do Sistema")
        figura_evolucao, eixo_evolucao = plt.subplots(figsize=(6, 4))
        canvas_evolucao = FigureCanvasTkAgg(figura_evolucao, master=janela_evolucao)
        canvas_evolucao.get_tk_widget().pack(pady=5)

def atualizar_figuras(k_valor):
    criar_janela_equacoes()
    equacao_ode = (r'$\frac{dX}{dt} = - k\,X^{p}\,T^{q}$' + "\n" +
                   r'$\frac{dT}{dt} = a\,(1-T) + b\,(1-X) + c\,(L-1)$' + "\n" +
                   r'$\frac{dL}{dt} = d\,T^{r} - e\,L$')
    eixo_ode.clear()
    eixo_ode.axis('off')
    eixo_ode.text(0.5, 0.5, equacao_ode, horizontalalignment='center', verticalalignment='center', fontsize=14)
    canvas_ode.draw()
    equacao_k = (r'$k = k_0\,M^{\alpha}\,e^{-\beta\,(\text{metalicidade}-1)}\,(1+\gamma\,(\text{rotacao}-1))$' + "\n" +
                 r'$k = ' + f'{k_valor:.2e}' + '$')
    eixo_k.clear()
    eixo_k.axis('off')
    eixo_k.text(0.5, 0.5, equacao_k, horizontalalignment='center', verticalalignment='center', fontsize=14)
    canvas_k.draw()

def plotar_evolucao(sol):
    criar_janela_evolucao()
    t_vals = sol.t
    X_vals, T_vals, L_vals = sol.y
    eixo_evolucao.clear()
    eixo_evolucao.plot(t_vals, X_vals, label='X (Hidrogênio)')
    eixo_evolucao.plot(t_vals, T_vals, label='T (Temperatura)')
    eixo_evolucao.plot(t_vals, L_vals, label='L (Luminosidade)')
    eixo_evolucao.set_xlabel('Tempo (Gyr)')
    eixo_evolucao.set_ylabel('Valores normalizados')
    eixo_evolucao.legend()
    canvas_evolucao.draw()

def calcular_tempo_vida():
    try:
        massa = float(entrada_massa.get())
        metalicidade = float(entrada_metalicidade.get())
        rotacao = float(entrada_rotacao.get())
        k = k0 * (massa ** alfa) * math.exp(-beta * (metalicidade - 1)) * (1 + gamma * (rotacao - 1))
        condicoes_iniciais = [1.0, 1.0, 1.0]
        sol = solve_ivp(sistema_ode, [0, 1e10], condicoes_iniciais, args=(k, p, q, a_const, b_const, c_const, d_const, e_const, r_exp), events=evento_fim, dense_output=True)
        if sol.t_events[0].size > 0:
            tempo_vida = sol.t_events[0][0]
            label_resultado.config(text=f"Tempo de vida: {tempo_vida:.10f} Gyr")
        else:
            label_resultado.config(text="Evento não detectado. Ajuste os parâmetros.")
        atualizar_figuras(k)
        plotar_evolucao(sol)
    except Exception as erro:
        label_resultado.config(text="Erro: verifique os valores informados.")
        print("Erro:", erro)

root = tk.Tk()
root.title("Calculadora Avançada do Tempo de Vida de Estrelas")
frame_entradas = tk.Frame(root)
frame_entradas.pack(padx=10, pady=10)
label_massa = tk.Label(frame_entradas, text="Massa (em massas solares):")
label_massa.grid(row=0, column=0, padx=5, pady=5, sticky="e")
entrada_massa = tk.Entry(frame_entradas, width=15)
entrada_massa.grid(row=0, column=1, padx=5, pady=5)
entrada_massa.insert(0, "1.0")
label_metalicidade = tk.Label(frame_entradas, text="Metallicidade (1 = solar):")
label_metalicidade.grid(row=1, column=0, padx=5, pady=5, sticky="e")
entrada_metalicidade = tk.Entry(frame_entradas, width=15)
entrada_metalicidade.grid(row=1, column=1, padx=5, pady=5)
entrada_metalicidade.insert(0, "1.0")
label_rotacao = tk.Label(frame_entradas, text="Fator de rotação (1 = médio):")
label_rotacao.grid(row=2, column=0, padx=5, pady=5, sticky="e")
entrada_rotacao = tk.Entry(frame_entradas, width=15)
entrada_rotacao.grid(row=2, column=1, padx=5, pady=5)
entrada_rotacao.insert(0, "1.0")
botao_calcular = tk.Button(root, text="Calcular", command=calcular_tempo_vida)
botao_calcular.pack(pady=10)
label_resultado = tk.Label(root, text="Insira os valores e clique em Calcular")
label_resultado.pack(pady=10)
root.mainloop()
