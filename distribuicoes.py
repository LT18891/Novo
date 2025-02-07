import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import norm, binom, poisson, expon, uniform, gamma, beta, chi2, t, f

# Dicionário com as distribuições, seus parâmetros (nome, valor padrão e tipo)
# e o tipo (discreta ou contínua)
distribuicoes = {
    "Normal": {
        "func": norm,
        "parametros": [("média", 0, float), ("desvio", 1, float)],
        "tipo": "continua"
    },
    "Binomial": {
        "func": binom,
        "parametros": [("número de ensaios", 10, int), ("probabilidade de sucesso", 0.5, float)],
        "tipo": "discreta"
    },
    "Poisson": {
        "func": poisson,
        "parametros": [("lambda", 5, float)],
        "tipo": "discreta"
    },
    "Exponencial": {
        "func": expon,
        "parametros": [("taxa", 1, float)],  # lembrando que scale = 1/taxa
        "tipo": "continua"
    },
    "Uniforme": {
        "func": uniform,
        "parametros": [("início", 0, float), ("fim", 1, float)],
        "tipo": "continua"
    },
    "Gamma": {
        "func": gamma,
        "parametros": [("forma", 2, float), ("escala", 1, float)],
        "tipo": "continua"
    },
    "Beta": {
        "func": beta,
        "parametros": [("alfa", 2, float), ("beta", 2, float)],
        "tipo": "continua"
    },
    "Qui-quadrado": {
        "func": chi2,
        "parametros": [("graus de liberdade", 2, int)],
        "tipo": "continua"
    },
    "t de Student": {
        "func": t,
        "parametros": [("graus de liberdade", 10, int)],
        "tipo": "continua"
    },
    "F de Snedecor": {
        "func": f,
        "parametros": [("graus de liberdade 1", 5, int), ("graus de liberdade 2", 10, int)],
        "tipo": "continua"
    }
}

# Criação da janela principal
janela = tk.Tk()
janela.title("Distribuições Probabilísticas")

# Variável que guarda a distribuição selecionada
variavel_distribuicao = tk.StringVar(value=list(distribuicoes.keys())[0])

# --- Frame para seleção da distribuição ---
frame_selecao = tk.Frame(janela)
frame_selecao.pack(pady=5)

label_selecao = tk.Label(frame_selecao, text="Selecione a Distribuição:")
label_selecao.pack(side=tk.LEFT, padx=5)

menu_distribuicao = ttk.OptionMenu(
    frame_selecao,
    variavel_distribuicao,
    list(distribuicoes.keys())[0],
    *list(distribuicoes.keys()),
    command=lambda _: atualizar_campos()  # atualiza os campos de parâmetros quando muda
)
menu_distribuicao.pack(side=tk.LEFT, padx=5)

# --- Frame para entrada dos parâmetros ---
frame_parametros = tk.Frame(janela)
frame_parametros.pack(pady=5)

# Dicionário que armazenará os widgets de entrada (Entry)
entradas = {}

def atualizar_campos():
    """Atualiza os campos de entrada de parâmetros conforme a distribuição selecionada."""
    # Remove widgets antigos do frame de parâmetros
    for widget in frame_parametros.winfo_children():
        widget.destroy()
    entradas.clear()
    
    distrib_selecionada = variavel_distribuicao.get()
    parametros = distribuicoes[distrib_selecionada]["parametros"]
    
    # Cria um label e um campo de entrada para cada parâmetro
    for i, (nome_param, valor_padrao, tipo_param) in enumerate(parametros):
        lbl = tk.Label(frame_parametros, text=nome_param + ":")
        lbl.grid(row=i, column=0, padx=5, pady=2, sticky="e")
        ent = tk.Entry(frame_parametros)
        ent.grid(row=i, column=1, padx=5, pady=2)
        ent.insert(0, str(valor_padrao))
        entradas[nome_param] = (ent, tipo_param)

# --- Frame para o botão de calcular ---
frame_calcular = tk.Frame(janela)
frame_calcular.pack(pady=5)

# --- Frame para a plotagem ---
frame_plot = tk.Frame(janela)
frame_plot.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Label para exibir informações (ex.: média e variância)
label_info = tk.Label(janela, text="", font=("Arial", 10))
label_info.pack(pady=5)

def calcular():
    """Obtém os valores dos parâmetros, calcula a função (PDF ou PMF) e plota o gráfico."""
    distrib_selecionada = variavel_distribuicao.get()
    parametros_def = distribuicoes[distrib_selecionada]["parametros"]
    valores = []
    
    # Obtém os valores digitados e converte para o tipo adequado
    for nome_param, _, tipo_param in parametros_def:
        ent, _ = entradas[nome_param]
        try:
            valor = tipo_param(ent.get())
        except ValueError:
            messagebox.showerror("Erro", f"Valor inválido para {nome_param}")
            return
        valores.append(valor)
    
    # Inicializa variáveis para x, y e informações
    x = None
    y = None
    info_texto = ""
    
    # Cada distribuição é tratada individualmente:
    if distrib_selecionada == "Normal":
        media, desvio = valores
        x_min = norm.ppf(0.001, loc=media, scale=desvio)
        x_max = norm.ppf(0.999, loc=media, scale=desvio)
        x = np.linspace(x_min, x_max, 400)
        y = norm.pdf(x, loc=media, scale=desvio)
        info_texto = f"Média: {media}, Variância: {desvio**2}"
        
    elif distrib_selecionada == "Binomial":
        n, p = valores
        x = np.arange(0, n+1)
        y = binom.pmf(x, n, p)
        info_texto = f"Esperança: {n*p}, Variância: {n*p*(1-p)}"
        
    elif distrib_selecionada == "Poisson":
        lam = valores[0]
        max_x = int(lam + 4 * np.sqrt(lam)) if lam > 0 else 10
        x = np.arange(0, max_x+1)
        y = poisson.pmf(x, lam)
        info_texto = f"Esperança: {lam}, Variância: {lam}"
        
    elif distrib_selecionada == "Exponencial":
        taxa = valores[0]
        if taxa <= 0:
            messagebox.showerror("Erro", "A taxa deve ser maior que zero.")
            return
        escala = 1.0 / taxa
        x_min = expon.ppf(0.001, scale=escala)
        x_max = expon.ppf(0.999, scale=escala)
        x = np.linspace(x_min, x_max, 400)
        y = expon.pdf(x, scale=escala)
        info_texto = f"Esperança: {escala}, Variância: {escala**2}"
        
    elif distrib_selecionada == "Uniforme":
        inicio, fim = valores
        if fim <= inicio:
            messagebox.showerror("Erro", "O valor de 'fim' deve ser maior que 'início'.")
            return
        x = np.linspace(inicio, fim, 400)
        y = uniform.pdf(x, loc=inicio, scale=fim - inicio)
        info_texto = f"Esperança: {(inicio+fim)/2}, Variância: {(fim-inicio)**2/12}"
        
    elif distrib_selecionada == "Gamma":
        forma, escala = valores
        if forma <= 0 or escala <= 0:
            messagebox.showerror("Erro", "Forma e escala devem ser maiores que zero.")
            return
        x_min = gamma.ppf(0.001, forma, scale=escala)
        x_max = gamma.ppf(0.999, forma, scale=escala)
        x = np.linspace(x_min, x_max, 400)
        y = gamma.pdf(x, forma, scale=escala)
        info_texto = f"Esperança: {forma * escala}, Variância: {forma * escala**2}"
        
    elif distrib_selecionada == "Beta":
        alfa, beta_val = valores
        if alfa <= 0 or beta_val <= 0:
            messagebox.showerror("Erro", "Alfa e beta devem ser maiores que zero.")
            return
        x = np.linspace(0, 1, 400)
        y = beta.pdf(x, alfa, beta_val)
        info_texto = (f"Esperança: {alfa/(alfa+beta_val)}, "
                      f"Variância: {alfa * beta_val / (((alfa+beta_val)**2) * (alfa+beta_val+1))}")
        
    elif distrib_selecionada == "Qui-quadrado":
        gl = valores[0]
        if gl <= 0:
            messagebox.showerror("Erro", "Graus de liberdade devem ser maiores que zero.")
            return
        x_min = chi2.ppf(0.001, gl)
        x_max = chi2.ppf(0.999, gl)
        x = np.linspace(x_min, x_max, 400)
        y = chi2.pdf(x, gl)
        info_texto = f"Esperança: {gl}, Variância: {2 * gl}"
        
    elif distrib_selecionada == "t de Student":
        gl = valores[0]
        if gl <= 0:
            messagebox.showerror("Erro", "Graus de liberdade devem ser maiores que zero.")
            return
        x_min = t.ppf(0.001, gl)
        x_max = t.ppf(0.999, gl)
        x = np.linspace(x_min, x_max, 400)
        y = t.pdf(x, gl)
        var = gl/(gl-2) if gl > 2 else "Indefinida"
        info_texto = f"Esperança: 0, Variância: {var}"
        
    elif distrib_selecionada == "F de Snedecor":
        gl1, gl2 = valores
        if gl1 <= 0 or gl2 <= 0:
            messagebox.showerror("Erro", "Graus de liberdade devem ser maiores que zero.")
            return
        x_min = f.ppf(0.001, gl1, gl2)
        x_max = f.ppf(0.999, gl1, gl2)
        x = np.linspace(x_min, x_max, 400)
        y = f.pdf(x, gl1, gl2)
        media_f = gl2/(gl2-2) if gl2 > 2 else "Indefinida"
        info_texto = f"Esperança: {media_f}"
        
    else:
        messagebox.showerror("Erro", "Distribuição não implementada.")
        return

    # Cria a figura para a plotagem
    figura = plt.Figure(figsize=(5, 4), dpi=100)
    eixo = figura.add_subplot(111)
    
    # Para distribuições discretas, usamos stem; para contínuas, plotamos uma linha
    if distribuicoes[distrib_selecionada]["tipo"] == "discreta":
        eixo.stem(x, y, basefmt=" ")
    else:
        eixo.plot(x, y)
    
    eixo.set_title(distrib_selecionada)
    eixo.set_xlabel("x")
    eixo.set_ylabel("Probabilidade" if distribuicoes[distrib_selecionada]["tipo"] == "discreta" else "Densidade")
    
    # Atualiza a área de plotagem (limpa widgets antigos)
    for widget in frame_plot.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(figura, master=frame_plot)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Exibe as informações (média, variância, etc.)
    label_info.config(text=info_texto)

# Botão para acionar o cálculo e a plotagem
botao_calcular = tk.Button(frame_calcular, text="Calcular", command=calcular)
botao_calcular.pack()

# Inicializa os campos de parâmetros para a distribuição padrão
atualizar_campos()

# Inicia o loop principal da interface
janela.mainloop()
