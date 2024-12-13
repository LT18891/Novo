import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import numpy as np
from scipy.integrate import odeint
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use("TkAgg")

def demanda(t):
    # Normalizada para um intervalo menor
    return 10 + 5 * np.sin(0.1 * t)

def oferta(t):
    return 8 + 3 * np.cos(0.1 * t)

def mercado(t):
    return 1.0 + 0.05 * np.sin(0.05 * t)

def externos(t):
    return 2.0 + 0.2 * np.cos(0.05 * t)

def intervencao(t):
    return 0.5 + 0.1 * np.sin(0.02 * t)

def sistema_variaveis(Y, t, alpha, beta, gamma, delta, epsilon, zeta_, iota_, theta_, kappa, lambd, Lmax, xi,
                     D_values, S_values, M_values, E_values, N_values,
                     RP_values, RZ_values, RL_values, T_vals):
    P, Z, L = Y
    D_t = np.interp(t, T_vals, D_values)
    S_t = np.interp(t, T_vals, S_values)
    M_t = np.interp(t, T_vals, M_values)
    E_t = np.interp(t, T_vals, E_values)
    N_t = np.interp(t, T_vals, N_values)
    RP_t = np.interp(t, T_vals, RP_values)
    RZ_t = np.interp(t, T_vals, RZ_values)
    RL_t = np.interp(t, T_vals, RL_values)
    
    dPdt = alpha * D_t * Z - beta * S_t * L + gamma * M_t * P**2 - delta * E_t * P * Z + RP_t
    dZdt = epsilon * (M_t - N_t)*Z - zeta_ * Z**2 + iota_ * P + RZ_t * theta_
    dLdt = kappa * L * (1 - L/Lmax) - lambd * P * L + RL_t * xi
    return [dPdt, dZdt, dLdt]

def salvar_figura():
    filename = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
    if filename:
        fig.savefig(filename)
        messagebox.showinfo("Sucesso", f"Figura salva em {filename}")

def salvar_figura_ZL():
    filename = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
    if filename:
        fig_ZL.savefig(filename)
        messagebox.showinfo("Sucesso", f"Figura salva em {filename}")

def mostrar_resultados(P, Z, L, t_max, T_vals):
    top = tk.Toplevel(root)
    top.title("Resultados da Simulação")
    frame_top = ttk.Frame(top, padding="10 10 10 10")
    frame_top.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))

    fig_res, ax_res = plt.subplots(figsize=(6,4))
    ax_res.plot(T_vals, P, label='P', color='blue')
    ax_res.plot(T_vals, Z, label='Z', color='orange')
    ax_res.plot(T_vals, L, label='L', color='green')
    ax_res.set_xlabel('Tempo')
    ax_res.set_ylabel('Valores')
    ax_res.set_title('Resultados da Simulação')
    ax_res.legend(loc='upper left')
    canvas_res = FigureCanvasTkAgg(fig_res, master=frame_top)
    canvas_res.draw()
    canvas_res.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)

    ultimo_preco = P[-1]
    ttk.Label(frame_top, text=f"Preço final após {t_max} unidades de tempo: {ultimo_preco:.8f} USD").grid(row=1, column=0, padx=10, pady=10)

def resolver_e_plotar():
    try:
        alpha = float(entry_alpha.get())
        beta = float(entry_beta.get())
        gamma = float(entry_gamma.get())
        delta = float(entry_delta.get())
        epsilon = float(entry_epsilon.get())
        zeta_ = float(entry_zeta.get())
        iota_ = float(entry_iota.get())
        theta_ = float(entry_theta.get())
        kappa = float(entry_kappa.get())
        lambd = float(entry_lambda.get())
        Lmax = float(entry_Lmax.get())
        xi = float(entry_xi.get())
        P0 = float(entry_P0.get())
        Z0 = float(entry_Z0.get())
        L0 = float(entry_L0.get())
        t_max = float(entry_t_max.get())
        num_points = int(entry_num_points.get())
        seed_val = entry_seed.get()
        if seed_val.strip() == '':
            seed_val = None
        else:
            seed_val = int(seed_val)
        T_vals = np.linspace(0, t_max, num_points)
        D_values = np.array([demanda(t) for t in T_vals])
        S_values = np.array([oferta(t) for t in T_vals])
        M_values = np.array([mercado(t) for t in T_vals])
        E_values = np.array([externos(t) for t in T_vals])
        N_values = np.array([intervencao(t) for t in T_vals])
        if seed_val is not None:
            np.random.seed(seed_val)
        RP_values = np.random.normal(0, 1, size=num_points)*float(entry_noiseP.get())
        RZ_values = np.random.normal(0, 1, size=num_points)*float(entry_noiseZ.get())
        RL_values = np.random.normal(0, 1, size=num_points)*float(entry_noiseL.get())
        Y0 = [P0, Z0, L0]

        args = (alpha, beta, gamma, delta,
                epsilon, zeta_, iota_, theta_,
                kappa, lambd, Lmax, xi,
                D_values, S_values, M_values, E_values, N_values,
                RP_values, RZ_values, RL_values, T_vals)

        # Ajuste de tolerâncias para maior estabilidade
        Y = odeint(sistema_variaveis, Y0, T_vals, args=args, atol=1e-9, rtol=1e-9)
        P = Y[:,0]
        Z = Y[:,1]
        L = Y[:,2]
        ax.clear()
        ax.plot(T_vals, P, label='Preço (P)', color='blue')
        ax.set_xlabel('Tempo')
        ax.set_ylabel('Preço (USD)')
        ax.set_title('Previsão do Preço do Bitcoin')
        ax.legend(loc='upper left')
        canvas.draw()
        ax_ZL.clear()
        ax_ZL.plot(T_vals, Z, label='Sentimento (Z)', color='orange')
        ax_ZL.plot(T_vals, L, label='Liquidez (L)', color='green')
        ax_ZL.set_xlabel('Tempo')
        ax_ZL.set_ylabel('Valor (adimensional)')
        ax_ZL.set_title('Sentimento e Liquidez ao longo do tempo')
        ax_ZL.legend(loc='upper left')
        canvas_ZL.draw()
        ultimo_preco = P[-1]
        label_resultado.config(text=f"Preço previsto após {t_max} unidades de tempo: {ultimo_preco:.8f} USD")
        mostrar_resultados(P, Z, L, t_max, T_vals)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

root = tk.Tk()
root.title("Modelo Preditivo do Preço do Bitcoin - Complexo (Parâmetros Ajustados)")

main_canvas = tk.Canvas(root)
main_canvas.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
scrollbar = tk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
frame_container = ttk.Frame(main_canvas)
frame_container.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
main_canvas.create_window((0,0), window=frame_container, anchor="nw")
main_canvas.configure(yscrollcommand=scrollbar.set)

notebook = ttk.Notebook(frame_container)
notebook.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))

param_frame = ttk.Frame(notebook, padding="10 10 10 10")
notebook.add(param_frame, text="Parâmetros do Modelo")

plot_frame = ttk.Frame(notebook, padding="10 10 10 10")
notebook.add(plot_frame, text="Gráficos")

plot_frame_ZL = ttk.Frame(notebook, padding="10 10 10 10")
notebook.add(plot_frame_ZL, text="Sentimento e Liquidez")

extra_frame = ttk.Frame(frame_container, padding="10 10 10 10")
extra_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

equation_frame = ttk.Frame(frame_container, padding="10 10 10 10")
equation_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

equation_fig, equation_ax = plt.subplots(figsize=(6,3))
equation_ax.axis('off')
equation_text = (r"$\frac{dP}{dt} = \alpha D(t)Z(t) - \beta S(t)L(t) + \gamma M(t) P(t)^2 - \delta E(t) P(t)Z(t) + R_P(t)$"+"\n"+
                 r"$\frac{dZ}{dt} = \varepsilon (M(t)-N(t)) Z(t) - \zeta Z(t)^2 + \iota P(t) + \theta R_Z(t)$"+"\n"+
                 r"$\frac{dL}{dt} = \kappa L(t)\left(1 - \frac{L(t)}{L_{max}}\right) - \lambda P(t)L(t) + \xi R_L(t)$")
equation_ax.text(0.5, 0.5, equation_text, horizontalalignment='center', verticalalignment='center', fontsize=12)
equation_canvas = FigureCanvasTkAgg(equation_fig, master=equation_frame)
equation_canvas.draw()
equation_canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)

ttk.Label(param_frame, text="Parâmetros de P(t):").grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W)
ttk.Label(param_frame, text="Alpha (α):").grid(row=1, column=0, sticky=tk.W)
entry_alpha = ttk.Entry(param_frame, width=20)
entry_alpha.grid(row=1, column=1, sticky=(tk.W, tk.E))
entry_alpha.insert(0, "0.001")  # valor reduzido
ttk.Label(param_frame, text="Beta (β):").grid(row=2, column=0, sticky=tk.W)
entry_beta = ttk.Entry(param_frame, width=20)
entry_beta.grid(row=2, column=1, sticky=(tk.W, tk.E))
entry_beta.insert(0, "0.001")
ttk.Label(param_frame, text="Gamma (γ):").grid(row=3, column=0, sticky=tk.W)
entry_gamma = ttk.Entry(param_frame, width=20)
entry_gamma.grid(row=3, column=1, sticky=(tk.W, tk.E))
entry_gamma.insert(0, "0.001")
ttk.Label(param_frame, text="Delta (δ):").grid(row=4, column=0, sticky=tk.W)
entry_delta = ttk.Entry(param_frame, width=20)
entry_delta.grid(row=4, column=1, sticky=(tk.W, tk.E))
entry_delta.insert(0, "0.001")

ttk.Label(param_frame, text="Parâmetros de Z(t):").grid(row=5, column=0, columnspan=2, pady=5, sticky=tk.W)
ttk.Label(param_frame, text="Epsilon (ε):").grid(row=6, column=0, sticky=tk.W)
entry_epsilon = ttk.Entry(param_frame, width=20)
entry_epsilon.grid(row=6, column=1, sticky=(tk.W, tk.E))
entry_epsilon.insert(0, "0.001")
ttk.Label(param_frame, text="Zeta (ζ):").grid(row=7, column=0, sticky=tk.W)
entry_zeta = ttk.Entry(param_frame, width=20)
entry_zeta.grid(row=7, column=1, sticky=(tk.W, tk.E))
entry_zeta.insert(0, "0.001")
ttk.Label(param_frame, text="Iota (ι):").grid(row=8, column=0, sticky=tk.W)
entry_iota = ttk.Entry(param_frame, width=20)
entry_iota.grid(row=8, column=1, sticky=(tk.W, tk.E))
entry_iota.insert(0, "0.001")
ttk.Label(param_frame, text="Theta (θ):").grid(row=9, column=0, sticky=tk.W)
entry_theta = ttk.Entry(param_frame, width=20)
entry_theta.grid(row=9, column=1, sticky=(tk.W, tk.E))
entry_theta.insert(0, "0.1")

ttk.Label(param_frame, text="Parâmetros de L(t):").grid(row=10, column=0, columnspan=2, pady=5, sticky=tk.W)
ttk.Label(param_frame, text="Kappa (κ):").grid(row=11, column=0, sticky=tk.W)
entry_kappa = ttk.Entry(param_frame, width=20)
entry_kappa.grid(row=11, column=1, sticky=(tk.W, tk.E))
entry_kappa.insert(0, "0.01")
ttk.Label(param_frame, text="Lambda (λ):").grid(row=12, column=0, sticky=tk.W)
entry_lambda = ttk.Entry(param_frame, width=20)
entry_lambda.grid(row=12, column=1, sticky=(tk.W, tk.E))
entry_lambda.insert(0, "0.001")
ttk.Label(param_frame, text="L_max:").grid(row=13, column=0, sticky=tk.W)
entry_Lmax = ttk.Entry(param_frame, width=20)
entry_Lmax.grid(row=13, column=1, sticky=(tk.W, tk.E))
entry_Lmax.insert(0, "100")
ttk.Label(param_frame, text="Xi (ξ):").grid(row=14, column=0, sticky=tk.W)
entry_xi = ttk.Entry(param_frame, width=20)
entry_xi.grid(row=14, column=1, sticky=(tk.W, tk.E))
entry_xi.insert(0, "0.001")

ttk.Label(param_frame, text="Condições Iniciais:").grid(row=15, column=0, columnspan=2, pady=5, sticky=tk.W)
ttk.Label(param_frame, text="P₀ (Preço inicial):").grid(row=16, column=0, sticky=tk.W)
entry_P0 = ttk.Entry(param_frame, width=20)
entry_P0.grid(row=16, column=1, sticky=(tk.W, tk.E))
entry_P0.insert(0, "1.0")  # valor reduzido
ttk.Label(param_frame, text="Z₀ (Sentimento inicial):").grid(row=17, column=0, sticky=tk.W)
entry_Z0 = ttk.Entry(param_frame, width=20)
entry_Z0.grid(row=17, column=1, sticky=(tk.W, tk.E))
entry_Z0.insert(0, "1.0")
ttk.Label(param_frame, text="L₀ (Liquidez inicial):").grid(row=18, column=0, sticky=tk.W)
entry_L0 = ttk.Entry(param_frame, width=20)
entry_L0.grid(row=18, column=1, sticky=(tk.W, tk.E))
entry_L0.insert(0, "10.0")

ttk.Label(param_frame, text="Tempo de Simulação:").grid(row=19, column=0, columnspan=2, pady=5, sticky=tk.W)
ttk.Label(param_frame, text="Tempo Máximo (t_max):").grid(row=20, column=0, sticky=tk.W)
entry_t_max = ttk.Entry(param_frame, width=20)
entry_t_max.grid(row=20, column=1, sticky=(tk.W, tk.E))
entry_t_max.insert(0, "10")  # menor tempo
ttk.Label(param_frame, text="Número de Pontos:").grid(row=21, column=0, sticky=tk.W)
entry_num_points = ttk.Entry(param_frame, width=20)
entry_num_points.grid(row=21, column=1, sticky=(tk.W, tk.E))
entry_num_points.insert(0, "200")

ttk.Label(param_frame, text="Parâmetros de Ruído:").grid(row=22, column=0, columnspan=2, pady=5, sticky=tk.W)
ttk.Label(param_frame, text="Desvio Ruído P:").grid(row=23, column=0, sticky=tk.W)
entry_noiseP = ttk.Entry(param_frame, width=20)
entry_noiseP.grid(row=23, column=1, sticky=(tk.W, tk.E))
entry_noiseP.insert(0, "0.1")
ttk.Label(param_frame, text="Desvio Ruído Z:").grid(row=24, column=0, sticky=tk.W)
entry_noiseZ = ttk.Entry(param_frame, width=20)
entry_noiseZ.grid(row=24, column=1, sticky=(tk.W, tk.E))
entry_noiseZ.insert(0, "0.01")
ttk.Label(param_frame, text="Desvio Ruído L:").grid(row=25, column=0, sticky=tk.W)
entry_noiseL = ttk.Entry(param_frame, width=20)
entry_noiseL.grid(row=25, column=1, sticky=(tk.W, tk.E))
entry_noiseL.insert(0, "0.1")
ttk.Label(param_frame, text="Semente Aleatória:").grid(row=26, column=0, sticky=tk.W)
entry_seed = ttk.Entry(param_frame, width=20)
entry_seed.grid(row=26, column=1, sticky=(tk.W, tk.E))
entry_seed.insert(0, "")

ttk.Button(param_frame, text="Prever Preço", command=resolver_e_plotar).grid(row=27, column=0, columnspan=2, pady=10)
label_resultado = ttk.Label(param_frame, text="Preço previsto após t_max: -- USD")
label_resultado.grid(row=28, column=0, columnspan=2)

fig, ax = plt.subplots(figsize=(6,4))
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)
ttk.Button(plot_frame, text="Salvar Figura P", command=salvar_figura).grid(row=1, column=0, pady=5)

fig_ZL, ax_ZL = plt.subplots(figsize=(6,4))
canvas_ZL = FigureCanvasTkAgg(fig_ZL, master=plot_frame_ZL)
canvas_ZL.draw()
canvas_ZL.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)
ttk.Button(plot_frame_ZL, text="Salvar Figura Z/L", command=salvar_figura_ZL).grid(row=1, column=0, pady=5)

ttk.Label(extra_frame, text="Modelo Complexo de Previsão do Preço do Bitcoin - Ajustado").grid(row=0, column=0, sticky=tk.W)

for child in param_frame.winfo_children():
    child.grid_configure(padx=5, pady=5)
for child in plot_frame.winfo_children():
    child.grid_configure(padx=5, pady=5)
for child in plot_frame_ZL.winfo_children():
    child.grid_configure(padx=5, pady=5)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.mainloop()
