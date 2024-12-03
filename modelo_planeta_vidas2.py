import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Função para calcular a probabilidade de vida
def calcular_probabilidade(R, fp, ne, fl, fi, fc, L):
    """
    Calcula a probabilidade de vida em outros planetas usando a Equação de Drake.

    Parâmetros:
    R (float): Taxa de formação de estrelas adequadas por ano.
    fp (float): Fração dessas estrelas que possuem sistemas planetários.
    ne (float): Número de planetas, por sistema planetário, que podem suportar vida.
    fl (float): Fração desses planetas onde a vida realmente surge.
    fi (float): Fração dos planetas com vida que desenvolvem inteligência.
    fc (float): Fração dos planetas com civilizações capazes de comunicação.
    L (float): Tempo de duração dessas civilizações.

    Retorna:
    float: Número esperado de civilizações comunicativas na galáxia.
    """
    return R * fp * ne * fl * fi * fc * L

# Função para realizar a simulação de Monte Carlo
def monte_carlo_simulation(params, iterations):
    """
    Realiza uma simulação de Monte Carlo para estimar a distribuição de N.

    Parâmetros:
    params (dict): Dicionário contendo as distribuições de cada parâmetro.
    iterations (int): Número de iterações da simulação.

    Retorna:
    np.ndarray: Array com os valores calculados de N para cada iteração.
    """
    # Para distribuição LogNormal, se mean_log e sigma_log são os parâmetros da normal subjacente
    R = np.random.lognormal(mean=params['R']['mean_log'], sigma=params['R']['sigma'], size=iterations)
    L = np.random.lognormal(mean=params['L']['mean_log'], sigma=params['L']['sigma'], size=iterations)
    
    # Distribuições Uniforme
    fp = np.random.uniform(low=params['fp']['min'], high=params['fp']['max'], size=iterations)
    ne = np.random.uniform(low=params['ne']['min'], high=params['ne']['max'], size=iterations)
    
    # Distribuições Beta
    fl = np.random.beta(a=params['fl']['a'], b=params['fl']['b'], size=iterations)
    fi = np.random.beta(a=params['fi']['a'], b=params['fi']['b'], size=iterations)
    fc = np.random.beta(a=params['fc']['a'], b=params['fc']['b'], size=iterations)

    # Calcular N para cada iteração
    N = calcular_probabilidade(R, fp, ne, fl, fi, fc, L)
    return N

# Função para gerar o gráfico
def gerar_grafico():
    try:
        iterations = int(entry_iterations.get())
        if iterations <= 0:
            raise ValueError("O número de iterações deve ser positivo.")

        # Definir as distribuições para cada parâmetro
        params = {
            'R': {
                'mean_log': float(entries_distribuicao['R (estrelas/ano)']['mean'].get()),
                'sigma': float(entries_distribuicao['R (estrelas/ano)']['sigma'].get())
            },
            'fp': {
                'min': float(entries_distribuicao['fp']['min'].get()),
                'max': float(entries_distribuicao['fp']['max'].get())
            },
            'ne': {
                'min': float(entries_distribuicao['ne']['min'].get()),
                'max': float(entries_distribuicao['ne']['max'].get())
            },
            'fl': {
                'a': float(entries_distribuicao['fl']['a'].get()),
                'b': float(entries_distribuicao['fl']['b'].get())
            },
            'fi': {
                'a': float(entries_distribuicao['fi']['a'].get()),
                'b': float(entries_distribuicao['fi']['b'].get())
            },
            'fc': {
                'a': float(entries_distribuicao['fc']['a'].get()),
                'b': float(entries_distribuicao['fc']['b'].get())
            },
            'L': {
                'mean_log': float(entries_distribuicao['L (anos)']['mean'].get()),
                'sigma': float(entries_distribuicao['L (anos)']['sigma'].get())
            }
        }

        # Validar os parâmetros
        for key, value in params.items():
            if key in ['R', 'L'] and value['sigma'] <= 0:
                raise ValueError(f"Sigma para {key} deve ser positivo.")
            if key in ['fp', 'ne'] and value['max'] < value['min']:
                raise ValueError(f"Max deve ser maior ou igual a Min para {key}.")
            if key in ['fl', 'fi', 'fc'] and (value['a'] <= 0 or value['b'] <= 0):
                raise ValueError(f"Os parâmetros 'a' e 'b' para {key} devem ser positivos.")

        # Realizar a simulação
        N = monte_carlo_simulation(params, iterations)

        # Estatísticas
        mean_N = np.mean(N)
        median_N = np.median(N)
        percentile_5 = np.percentile(N, 5)
        percentile_95 = np.percentile(N, 95)

        # Preparar o gráfico
        fig.clear()
        ax = fig.add_subplot(111)
        ax.hist(N, bins=50, color='skyblue', edgecolor='black')
        ax.set_xlabel('Número de Civilizações Comunicativas (N)')
        ax.set_ylabel('Frequência')
        ax.set_title('Distribuição de N via Simulação de Monte Carlo')

        # Adicionar linhas para estatísticas
        ax.axvline(mean_N, color='red', linestyle='dashed', linewidth=1.5, label=f'Média: {mean_N:.2f}')
        ax.axvline(median_N, color='green', linestyle='dashed', linewidth=1.5, label=f'Mediana: {median_N:.2f}')
        ax.axvline(percentile_5, color='orange', linestyle='dotted', linewidth=1.5, label=f'5º Percentil: {percentile_5:.2f}')
        ax.axvline(percentile_95, color='orange', linestyle='dotted', linewidth=1.5, label=f'95º Percentil: {percentile_95:.2f}')

        ax.legend()

        canvas.draw()

        # Mostrar estatísticas em uma caixa de mensagem
        stats_message = (
            f"Número de Simulações: {iterations}\n"
            f"Média de N: {mean_N:.2f}\n"
            f"Mediana de N: {median_N:.2f}\n"
            f"5º Percentil de N: {percentile_5:.2f}\n"
            f"95º Percentil de N: {percentile_95:.2f}"
        )
        messagebox.showinfo("Estatísticas da Simulação", stats_message)

    except ValueError as ve:
        messagebox.showerror("Erro", f"Entrada inválida: {ve}")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

# Configuração da interface gráfica
root = tk.Tk()
root.title("Probabilidade de Vida em Outros Planetas - Simulação de Monte Carlo")
root.geometry("1200x800")

# Criar um frame para os inputs com scroll
canvas_frame = tk.Canvas(root, borderwidth=0)
frame_inputs = ttk.Frame(canvas_frame, padding="10")
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas_frame.yview)
canvas_frame.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas_frame.pack(side="left", fill="both", expand=True)
canvas_frame.create_window((0, 0), window=frame_inputs, anchor="nw")

def on_frame_configure(event):
    canvas_frame.configure(scrollregion=canvas_frame.bbox("all"))

frame_inputs.bind("<Configure>", on_frame_configure)

# Número de iterações
ttk.Label(frame_inputs, text="Número de Simulações:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
entry_iterations = ttk.Entry(frame_inputs, width=20)
entry_iterations.grid(row=0, column=1, pady=5, padx=5)
entry_iterations.insert(0, "10000")  # Valor padrão

# Lista de parâmetros e suas distribuições
parametros = [
    # (Nome, Tipo de Distribuição, Descrição)
    ("R (estrelas/ano)", "LogNormal", "Taxa de formação de estrelas adequadas por ano."),
    ("fp", "Uniforme", "Fração dessas estrelas que possuem sistemas planetários."),
    ("ne", "Uniforme", "Número de planetas, por sistema planetário, que podem suportar vida."),
    ("fl", "Beta", "Fração desses planetas onde a vida realmente surge."),
    ("fi", "Beta", "Fração dos planetas com vida que desenvolvem inteligência."),
    ("fc", "Beta", "Fração dos planetas com civilizações capazes de comunicação."),
    ("L (anos)", "LogNormal", "Tempo de duração dessas civilizações.")
]

# Função para criar os campos de distribuição
def criar_campos_distribuicao(frame, parametros):
    entries = {}
    row = 1
    for param, dist, desc in parametros:
        # Título do parâmetro
        ttk.Label(frame, text=param, font=('Helvetica', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)

        if dist == "LogNormal":
            # Parâmetros: mean_log e sigma
            ttk.Label(frame, text="Média do log:").grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
            entry_mean = ttk.Entry(frame, width=10)
            entry_mean.grid(row=row, column=2, pady=2, padx=5)
            entry_mean.insert(0, "1")  # Valor padrão

            ttk.Label(frame, text="Sigma:").grid(row=row, column=3, sticky=tk.W, pady=2, padx=5)
            entry_sigma = ttk.Entry(frame, width=10)
            entry_sigma.grid(row=row, column=4, pady=2, padx=5)
            entry_sigma.insert(0, "0.5")  # Valor padrão

            entries[param] = {'mean': entry_mean, 'sigma': entry_sigma}

        elif dist == "Uniforme":
            # Parâmetros: min e max
            ttk.Label(frame, text="Min:").grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
            entry_min = ttk.Entry(frame, width=10)
            entry_min.grid(row=row, column=2, pady=2, padx=5)
            default_min = "1" if param == "ne" else "0.1"
            entry_min.insert(0, default_min)  # Valor padrão

            ttk.Label(frame, text="Max:").grid(row=row, column=3, sticky=tk.W, pady=2, padx=5)
            entry_max = ttk.Entry(frame, width=10)
            entry_max.grid(row=row, column=4, pady=2, padx=5)
            default_max = "5" if param == "ne" else "1"
            entry_max.insert(0, default_max)  # Valor padrão

            entries[param] = {'min': entry_min, 'max': entry_max}

        elif dist == "Beta":
            # Parâmetros: a e b
            ttk.Label(frame, text="Alpha (a):").grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
            entry_a = ttk.Entry(frame, width=10)
            entry_a.grid(row=row, column=2, pady=2, padx=5)
            entry_a.insert(0, "2")  # Valor padrão

            ttk.Label(frame, text="Beta (b):").grid(row=row, column=3, sticky=tk.W, pady=2, padx=5)
            entry_b = ttk.Entry(frame, width=10)
            entry_b.grid(row=row, column=4, pady=2, padx=5)
            entry_b.insert(0, "5")  # Valor padrão

            entries[param] = {'a': entry_a, 'b': entry_b}

        row += 1

    return entries

# Criar os campos de distribuição
entries_distribuicao = criar_campos_distribuicao(frame_inputs, parametros)

# Botão para gerar o gráfico
botao_plot = ttk.Button(root, text="Calcular e Plotar", command=gerar_grafico)
botao_plot.pack(pady=10)

# Criar uma figura para o Matplotlib
fig = plt.Figure(figsize=(12,6), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Iniciar a interface
root.mainloop()
