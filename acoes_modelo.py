import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import io

# Definição do modelo de equação diferencial
def modelo_equacao_diferencial(t, P, dP_dt, a, b, c, d):
    d2P_dt2 = -a * dP_dt - b * P - c * P**2 + d
    return d2P_dt2

# Método de Runge-Kutta de quarta ordem com verificação de limite
def runge_kutta(f, t0, P0, dP_dt0, h, n, a, b, c, d, limite=1e12):
    t = t0
    P = P0
    dP_dt = dP_dt0
    historico_t = [t]
    historico_P = [P]
    historico_dP_dt = [dP_dt]
    
    for i in range(n):
        try:
            # Cálculo dos coeficientes de Runge-Kutta
            k1 = f(t, P, dP_dt, a, b, c, d)
            l1 = dP_dt

            k2 = f(t + h/2, P + h*l1/2, dP_dt + h*k1/2, a, b, c, d)
            l2 = dP_dt + h*k1/2

            k3 = f(t + h/2, P + h*l2/2, dP_dt + h*k2/2, a, b, c, d)
            l3 = dP_dt + h*k2/2

            k4 = f(t + h, P + h*l3, dP_dt + h*k3, a, b, c, d)
            l4 = dP_dt + h*k3

            # Atualização de P e dP_dt
            P += (h/6)*(l1 + 2*l2 + 2*l3 + l4)
            dP_dt += (h/6)*(k1 + 2*k2 + 2*k3 + k4)
            t += h

            # Verificação de limites para evitar overflow
            if abs(P) > limite:
                raise OverflowError(f"Valor de P(t) excedeu o limite de {limite} na iteração {i}.")

            historico_t.append(t)
            historico_P.append(P)
            historico_dP_dt.append(dP_dt)
        except OverflowError as oe:
            messagebox.showerror("Erro de Overflow", str(oe))
            break
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
            break
    
    return np.array(historico_t), np.array(historico_P), np.array(historico_dP_dt)

# Função para renderizar equações usando matplotlib e retornar uma imagem Tkinter
def renderizar_equacao(equacao):
    fig, ax = plt.subplots(figsize=(8, 1.5))
    ax.text(0.5, 0.5, equacao, fontsize=14, ha='center', va='center')
    ax.axis('off')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)
    img = Image.open(buf)
    img_tk = ImageTk.PhotoImage(img)
    plt.close(fig)
    return img_tk

# Função para calcular e plotar
def calcular_e_plotar():
    try:
        # Obtenção dos parâmetros da interface
        a = float(entrada_a.get())
        b = float(entrada_b.get())
        c = float(entrada_c.get())
        d_param = float(entrada_d.get())
        P0 = float(entrada_P0.get())
        dP_dt0 = float(entrada_dP_dt0.get())
        t0 = float(entrada_t0.get())
        tf = float(entrada_tf.get())
        h = float(entrada_h.get())
        
        # Verificação de parâmetros válidos
        if h <= 0:
            messagebox.showerror("Erro de Passo", "O passo de integração (h) deve ser positivo.")
            return
        if tf <= t0:
            messagebox.showerror("Erro de Tempo", "O tempo final (tf) deve ser maior que o tempo inicial (t0).")
            return

        n = int((tf - t0)/h)
        
        # Resolução da equação diferencial
        t, P, dP_dt = runge_kutta(modelo_equacao_diferencial, t0, P0, dP_dt0, h, n, a, b, c, d_param)
        
        if len(t) == 0:
            # Se a simulação foi interrompida devido a overflow
            return
        
        # Limpeza do texto de resultados
        texto_resultado.config(state='normal')
        texto_resultado.delete(1.0, tk.END)
        
        # Formatação dos resultados com 20 dígitos após a vírgula
        for tempo, preco in zip(t, P):
            texto_resultado.insert(tk.END, f"t = {tempo:.20f}, P(t) = {preco:.20f}\n")
        
        texto_resultado.config(state='disabled')
        
        # Plotagem
        figura.clear()
        ax = figura.add_subplot(111)
        ax.plot(t, P, label='Preço das Ações P(t)')
        ax.set_xlabel('Tempo (t)')
        ax.set_ylabel('Preço das Ações P(t)')
        ax.set_title('Evolução do Preço das Ações ao Longo do Tempo')
        ax.legend()
        ax.grid(True)
        canvas.draw()
        
    except ValueError:
        messagebox.showerror("Erro de Entrada", "Por favor, insira valores numéricos válidos.")

# Função para limpar o texto ao focar
def on_entry_click(event, entry, default_text):
    if entry.get() == default_text:
        entry.delete(0, tk.END)
        entry.config(foreground='black')

# Função para restaurar o texto se estiver vazio
def on_focusout(event, entry, default_text):
    if entry.get() == '':
        entry.insert(0, default_text)
        entry.config(foreground='grey')

# Criação da interface gráfica
janela = tk.Tk()
janela.title("Previsão de Preço das Ações - Equação Diferencial Complexa")
janela.geometry("900x700")  # Definindo um tamanho inicial adequado

# Criação do Notebook (abas)
notebook = ttk.Notebook(janela)
notebook.pack(expand=True, fill='both')

# Abas
aba_explicacao = ttk.Frame(notebook, padding="10")
aba_simulacao = ttk.Frame(notebook, padding="10")

notebook.add(aba_explicacao, text="Explicação do Modelo")
notebook.add(aba_simulacao, text="Simulação")

### **1. Configuração da Aba de Explicação**

# Conteúdo da aba de explicação
explicacao_texto = (
    "## Modelo de Equação Diferencial para Previsão de Preço das Ações\n\n"
    "O modelo utilizado para prever o preço das ações \( P(t) \) é baseado em uma equação diferencial de segunda ordem com termos lineares e não lineares. A equação é definida da seguinte forma:\n\n"
)

# Renderização da equação diferencial
equacao1 = r"$\frac{d^2P}{dt^2} + a \frac{dP}{dt} + b P + c P^2 = d$"

# Descrição adicional
descricao = (
    "\nOnde:\n\n"
    "- \( P(t) \): Preço da ação no tempo \( t \).\n"
    "- \( a \): Coeficiente de amortecimento, representando a taxa de decaimento da variação do preço.\n"
    "- \( b \): Coeficiente linear, relacionado à força de mercado proporcional ao preço atual.\n"
    "- \( c \): Coeficiente não linear, capturando efeitos de crescimento acelerado ou desacelerado do preço.\n"
    "- \( d \): Força externa constante, representando influências externas no preço das ações.\n\n"
    "### Solução Numérica com Método de Runge-Kutta de Quarta Ordem\n\n"
    "Para resolver a equação diferencial, utilizamos o método de Runge-Kutta de quarta ordem, que é um método numérico eficiente para obter aproximações das soluções de equações diferenciais ordinárias (EDOs). Esse método é escolhido por sua precisão e estabilidade em comparação com métodos de ordem inferior.\n\n"
    "A solução numérica nos permite prever a evolução do preço das ações ao longo do tempo, considerando os parâmetros definidos."
)

# Adicionando os elementos à aba de explicação
label_explicacao = tk.Label(aba_explicacao, text=explicacao_texto, justify='left', font=("Helvetica", 12), wraplength=800, anchor='w')
label_explicacao.pack(anchor='w')

# Renderizar e adicionar a equação
img_equacao1 = renderizar_equacao(equacao1)
label_equacao1 = tk.Label(aba_explicacao, image=img_equacao1)
label_equacao1.image = img_equacao1  # Manter uma referência para evitar coleta de lixo
label_equacao1.pack(pady=10)

# Adicionar a descrição adicional
label_descricao = tk.Label(aba_explicacao, text=descricao, justify='left', font=("Helvetica", 12), wraplength=800)
label_descricao.pack(anchor='w', pady=10)

#### **2. Configuração da Aba de Simulação**

# Conteúdo da aba de simulação

# Frame para entradas
frame_entradas = ttk.Frame(aba_simulacao, padding="10")
frame_entradas.pack(side=tk.TOP, fill='x')

# Parâmetros da equação diferencial com valores padrão
parametros = [
    ("a:", "0.1"),
    ("b:", "0.5"),
    ("c:", "0.001"),  # Reduzido de 0.01 para maior estabilidade
    ("d:", "10"),
    ("P₀ (Preço Inicial):", "100.0"),
    ("dP/dt₀ (Variação Inicial):", "0.0"),
    ("t₀ (Tempo Inicial):", "0.0"),
    ("tf (Tempo Final):", "10.0"),
    ("h (Passo de Integração):", "0.001")  # Reduzido de 0.01 para maior precisão
]

entradas = {}

for i, (label_text, default) in enumerate(parametros):
    ttk.Label(frame_entradas, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
    entrada = ttk.Entry(frame_entradas, foreground='grey', width=20)
    entrada.grid(row=i, column=1, sticky=tk.E, pady=2, padx=5)
    entrada.insert(0, default)
    
    # Bind events para simular placeholder
    entrada.bind("<FocusIn>", lambda e, ent=entrada, txt=default: on_entry_click(e, ent, txt))
    entrada.bind("<FocusOut>", lambda e, ent=entrada, txt=default: on_focusout(e, ent, txt))
    
    entradas[label_text] = entrada

# Atribuição das entradas às variáveis correspondentes
entrada_a = entradas["a:"]
entrada_b = entradas["b:"]
entrada_c = entradas["c:"]
entrada_d = entradas["d:"]
entrada_P0 = entradas["P₀ (Preço Inicial):"]
entrada_dP_dt0 = entradas["dP/dt₀ (Variação Inicial):"]
entrada_t0 = entradas["t₀ (Tempo Inicial):"]
entrada_tf = entradas["tf (Tempo Final):"]
entrada_h = entradas["h (Passo de Integração):"]

# Botão de cálculo
botao_calcular = ttk.Button(aba_simulacao, text="Calcular e Plotar", command=calcular_e_plotar)
botao_calcular.pack(pady=10)

# Frame para resultados e plotagem
frame_resultados_plotagem = ttk.Frame(aba_simulacao, padding="10")
frame_resultados_plotagem.pack(fill='both', expand=True)

# Texto para resultados com barra de rolagem
scrollbar = ttk.Scrollbar(frame_resultados_plotagem, orient=tk.VERTICAL)
texto_resultado = tk.Text(frame_resultados_plotagem, width=80, height=10, state='disabled', yscrollcommand=scrollbar.set)
scrollbar.config(command=texto_resultado.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
texto_resultado.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Plotagem com matplotlib
figura, ax = plt.subplots(figsize=(6,4))
canvas = FigureCanvasTkAgg(figura, master=frame_resultados_plotagem)
canvas.draw()
canvas.get_tk_widget().pack(fill='both', expand=True, pady=10)

# Executar a interface
janela.mainloop()
