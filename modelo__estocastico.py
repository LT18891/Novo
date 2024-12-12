import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use('Agg')  # backend para não abrir janela do matplotlib fora do Tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk

def simular_ede(P0, V0, Y0, mu, kappa_V, theta_V, xi_V,
                kappa_Y, theta_Y, xi_Y,
                rho_PV, rho_PY, rho_VY,
                T, N, M):
    dt = T / N
    t = np.linspace(0, T, N+1)
    
    P = np.zeros((M, N+1))
    V = np.zeros((M, N+1))
    Y = np.zeros((M, N+1))
    
    P[:,0] = P0
    V[:,0] = V0
    Y[:,0] = Y0
    
    # Matriz de correlação
    corr_matrix = np.array([
        [1.0,    rho_PV, rho_PY],
        [rho_PV, 1.0,    rho_VY],
        [rho_PY, rho_VY, 1.0   ]
    ])
    
    # Fator de Cholesky para incrementos correlacionados
    L = np.linalg.cholesky(corr_matrix)
    
    for i in range(1, N+1):
        Z = np.random.normal(0, 1, (M,3))
        dW = Z @ L.T * np.sqrt(dt)
        
        dW1 = dW[:,0]
        dW2 = dW[:,1]
        dW3 = dW[:,2]
        
        # Atualiza V(t)
        V[:,i] = V[:,i-1] + kappa_V*(theta_V - V[:,i-1])*dt + xi_V*np.sqrt(np.maximum(V[:,i-1],0))*dW2
        V[:,i] = np.maximum(V[:,i], 0)
        
        # Atualiza Y(t)
        Y[:,i] = Y[:,i-1] + kappa_Y*(theta_Y - Y[:,i-1])*dt + xi_Y*dW3
        
        # Atualiza P(t)
        P[:,i] = P[:,i-1] + (mu - Y[:,i-1])*P[:,i-1]*dt + np.sqrt(np.maximum(V[:,i-1],0))*P[:,i-1]*dW1
    
    return t, P, V, Y

def renderizar_formula():
    # Fórmulas simples suportadas pelo mathtext
    sistema_latex = (
        r"$dP(t) = (\mu - Y(t))P(t)dt + \sqrt{V(t)}P(t)dW_1(t)$" "\n"
        r"$dV(t) = \kappa_V(\theta_V - V(t))dt + \xi_V\sqrt{V(t)}dW_2(t)$" "\n"
        r"$dY(t) = \kappa_Y(\theta_Y - Y(t))dt + \xi_Y dW_3(t)$"
    )

    fig = plt.figure(figsize=(6, 2))
    fig.text(0.05, 0.5, sistema_latex, fontsize=12, va='center', ha='left')
    fig.savefig("formula_sistema.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    img = Image.open("formula_sistema.png")
    img = img.resize((500, 130), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    label_formula.config(image=img_tk)
    label_formula.image = img_tk

def executar_simulacao():
    try:
        P0 = float(entry_P0.get())
        V0 = float(entry_V0.get())
        Y0 = float(entry_Y0.get())
        mu = float(entry_mu.get())
        kappa_V = float(entry_kappa_V.get())
        theta_V = float(entry_theta_V.get())
        xi_V = float(entry_xi_V.get())
        kappa_Y = float(entry_kappa_Y.get())
        theta_Y = float(entry_theta_Y.get())
        xi_Y = float(entry_xi_Y.get())
        rho_PV = float(entry_rho_PV.get())
        rho_PY = float(entry_rho_PY.get())
        rho_VY = float(entry_rho_VY.get())
        T = float(entry_T.get())
        N = int(entry_N.get())
        M = int(entry_M.get())
    except ValueError:
        messagebox.showerror("Erro de Entrada", "Por favor, insira valores numéricos válidos.")
        return
    
    corr_matrix = np.array([
        [1.0,    rho_PV, rho_PY],
        [rho_PV, 1.0,    rho_VY],
        [rho_PY, rho_VY, 1.0   ]
    ])
    try:
        np.linalg.cholesky(corr_matrix)
    except np.linalg.LinAlgError:
        messagebox.showerror("Erro de Correlação", "A matriz de correlação não é definida positiva. Ajuste os valores de correlação.")
        return
    
    t, P, V, Y = simular_ede(P0, V0, Y0, mu, kappa_V, theta_V, xi_V,
                             kappa_Y, theta_Y, xi_Y,
                             rho_PV, rho_PY, rho_VY,
                             T, N, M)
    
    # Limpar subplots
    ax_price.cla()
    ax_vol.cla()
    ax_yield.cla()
    
    num_plot = min(M, 10)
    for i in range(num_plot):
        ax_price.plot(t, P[i], lw=0.8)
    ax_price.set_title("Simulações do Preço P(t)")
    ax_price.set_xlabel("Tempo")
    ax_price.set_ylabel("Preço (USD)")
    
    for i in range(num_plot):
        ax_vol.plot(t, V[i], lw=0.8)
    ax_vol.set_title("Simulações da Volatilidade V(t)")
    ax_vol.set_xlabel("Tempo")
    ax_vol.set_ylabel("Volatilidade")
    
    for i in range(num_plot):
        ax_yield.plot(t, Y[i], lw=0.8)
    ax_yield.set_title("Simulações do Yield de Conveniência Y(t)")
    ax_yield.set_xlabel("Tempo")
    ax_yield.set_ylabel("Yield")
    
    canvas.draw()
    
    P_final_mean = np.mean(P[:,-1])
    V_final_mean = np.mean(V[:,-1])
    Y_final_mean = np.mean(Y[:,-1])
    label_resultado.config(text=(
        f"Preço Final Médio: ${P_final_mean:.6f} USD\n"
        f"Volatilidade Final Média: {V_final_mean:.6f}\n"
        f"Yield Final Médio: {Y_final_mean:.6f}"
    ))

# Interface
root = tk.Tk()
root.title("Modelo Estocástico com Volatilidade e Yield de Conveniência")

frame_inputs = ttk.Frame(root, padding="10")
frame_inputs.grid(row=0, column=0, sticky="W")

# Valores padrão (placeholders)
default_values = {
    "P0": 100,
    "V0": 0.04,
    "Y0": 0.02,
    "mu": 0.05,
    "kappa_V": 2.0,
    "theta_V": 0.04,
    "xi_V": 0.3,
    "kappa_Y": 1.0,
    "theta_Y": 0.02,
    "xi_Y": 0.01,
    "rho_PV": 0.2,
    "rho_PY": 0.1,
    "rho_VY": 0.15,
    "T": 1.0,
    "N": 252,
    "M": 1000
}

# Entradas com valores padrões
ttk.Label(frame_inputs, text="Preço Inicial P₀ (USD):").grid(row=0, column=0, sticky="W")
entry_P0 = ttk.Entry(frame_inputs, width=20)
entry_P0.insert(0, str(default_values["P0"]))
entry_P0.grid(row=0, column=1, pady=5)

ttk.Label(frame_inputs, text="Volatilidade Inicial V₀:").grid(row=1, column=0, sticky="W")
entry_V0 = ttk.Entry(frame_inputs, width=20)
entry_V0.insert(0, str(default_values["V0"]))
entry_V0.grid(row=1, column=1, pady=5)

ttk.Label(frame_inputs, text="Yield Inicial Y₀:").grid(row=2, column=0, sticky="W")
entry_Y0 = ttk.Entry(frame_inputs, width=20)
entry_Y0.insert(0, str(default_values["Y0"]))
entry_Y0.grid(row=2, column=1, pady=5)

ttk.Label(frame_inputs, text="Taxa de Retorno μ:").grid(row=3, column=0, sticky="W")
entry_mu = ttk.Entry(frame_inputs, width=20)
entry_mu.insert(0, str(default_values["mu"]))
entry_mu.grid(row=3, column=1, pady=5)

ttk.Label(frame_inputs, text="κ_V:").grid(row=4, column=0, sticky="W")
entry_kappa_V = ttk.Entry(frame_inputs, width=20)
entry_kappa_V.insert(0, str(default_values["kappa_V"]))
entry_kappa_V.grid(row=4, column=1, pady=5)

ttk.Label(frame_inputs, text="θ_V:").grid(row=5, column=0, sticky="W")
entry_theta_V = ttk.Entry(frame_inputs, width=20)
entry_theta_V.insert(0, str(default_values["theta_V"]))
entry_theta_V.grid(row=5, column=1, pady=5)

ttk.Label(frame_inputs, text="ξ_V:").grid(row=6, column=0, sticky="W")
entry_xi_V = ttk.Entry(frame_inputs, width=20)
entry_xi_V.insert(0, str(default_values["xi_V"]))
entry_xi_V.grid(row=6, column=1, pady=5)

ttk.Label(frame_inputs, text="κ_Y:").grid(row=7, column=0, sticky="W")
entry_kappa_Y = ttk.Entry(frame_inputs, width=20)
entry_kappa_Y.insert(0, str(default_values["kappa_Y"]))
entry_kappa_Y.grid(row=7, column=1, pady=5)

ttk.Label(frame_inputs, text="θ_Y:").grid(row=8, column=0, sticky="W")
entry_theta_Y = ttk.Entry(frame_inputs, width=20)
entry_theta_Y.insert(0, str(default_values["theta_Y"]))
entry_theta_Y.grid(row=8, column=1, pady=5)

ttk.Label(frame_inputs, text="ξ_Y:").grid(row=9, column=0, sticky="W")
entry_xi_Y = ttk.Entry(frame_inputs, width=20)
entry_xi_Y.insert(0, str(default_values["xi_Y"]))
entry_xi_Y.grid(row=9, column=1, pady=5)

ttk.Label(frame_inputs, text="ρ_PV:").grid(row=10, column=0, sticky="W")
entry_rho_PV = ttk.Entry(frame_inputs, width=20)
entry_rho_PV.insert(0, str(default_values["rho_PV"]))
entry_rho_PV.grid(row=10, column=1, pady=5)

ttk.Label(frame_inputs, text="ρ_PY:").grid(row=11, column=0, sticky="W")
entry_rho_PY = ttk.Entry(frame_inputs, width=20)
entry_rho_PY.insert(0, str(default_values["rho_PY"]))
entry_rho_PY.grid(row=11, column=1, pady=5)

ttk.Label(frame_inputs, text="ρ_VY:").grid(row=12, column=0, sticky="W")
entry_rho_VY = ttk.Entry(frame_inputs, width=20)
entry_rho_VY.insert(0, str(default_values["rho_VY"]))
entry_rho_VY.grid(row=12, column=1, pady=5)

ttk.Label(frame_inputs, text="Tempo Total T:").grid(row=13, column=0, sticky="W")
entry_T = ttk.Entry(frame_inputs, width=20)
entry_T.insert(0, str(default_values["T"]))
entry_T.grid(row=13, column=1, pady=5)

ttk.Label(frame_inputs, text="Número de Passos N:").grid(row=14, column=0, sticky="W")
entry_N = ttk.Entry(frame_inputs, width=20)
entry_N.insert(0, str(default_values["N"]))
entry_N.grid(row=14, column=1, pady=5)

ttk.Label(frame_inputs, text="Número de Simulações M:").grid(row=15, column=0, sticky="W")
entry_M = ttk.Entry(frame_inputs, width=20)
entry_M.insert(0, str(default_values["M"]))
entry_M.grid(row=15, column=1, pady=5)

botao_simular = ttk.Button(frame_inputs, text="Simular", command=executar_simulacao)
botao_simular.grid(row=16, column=0, columnspan=2, pady=10)

frame_formula = ttk.Frame(root, padding="10")
frame_formula.grid(row=1, column=0, sticky="W")
ttk.Label(frame_formula, text="Fórmulas do Sistema de EDEs:").grid(row=0, column=0, sticky="W")
label_formula = ttk.Label(frame_formula)
label_formula.grid(row=1, column=0, pady=5)

frame_grafico = ttk.Frame(root, padding="10")
frame_grafico.grid(row=0, column=1, rowspan=2)

fig, (ax_price, ax_vol, ax_yield) = plt.subplots(3, 1, figsize=(6,8))
plt.tight_layout(pad=3.0)
canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
canvas.draw()
canvas.get_tk_widget().pack()

frame_resultado = ttk.Frame(root, padding="10")
frame_resultado.grid(row=2, column=0, columnspan=2, sticky="W")
label_resultado = ttk.Label(frame_resultado, text="Preço Final Médio: ...\nVolatilidade Final Média: ...\nYield Final Médio: ...", font=("Arial", 12))
label_resultado.grid(row=0, column=0, pady=5)

# Renderizar a fórmula ao iniciar
renderizar_formula()

root.mainloop()
