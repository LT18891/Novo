#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulação Completa do Átomo de Hidrogênio – Resolução Numérica da Equação de Schrödinger (SI)

Este programa resolve a equação de Schrödinger completa para o átomo de hidrogênio
utilizando o método de diferenças finitas. São consideradas todas as constantes físicas (m_e, ℏ, e, ε₀)
e o termo centrífugo para estados com número quântico angular l.

A equação considerada é:

  - (ℏ²/(2 m_e)) ∇²ψ(r) - [Z e²/(4πε₀ r)] ψ(r) = E ψ(r)

Após separação de variáveis, com
  ψ(r,θ,φ) = u(r)/r · Yₗᵐ(θ,φ),
a equação radial torna-se:

  - (ℏ²/(2 m_e)) u''(r) + [ (ℏ² l(l+1))/(2m_e r²) - Z e²/(4πε₀ r) ] u(r) = E u(r).

O programa permite ajustar os parâmetros da malha, constantes físicas e
opções avançadas via interface gráfica.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SimulacaoHidrogenioCompleta:
    def __init__(self, master):
        self.master = master
        master.title("Simulação Completa do Átomo de Hidrogênio - Equação de Schrödinger")
        
        # --- Frame para os parâmetros gerais ---
        self.frame_parametros = tk.Frame(master)
        self.frame_parametros.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # --- Frame para parâmetros da malha e do átomo ---
        self.frame_malha = tk.LabelFrame(self.frame_parametros, text="Parâmetros da Malha e Átomo")
        self.frame_malha.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # r_min (ponto inicial, em metros)
        tk.Label(self.frame_malha, text="r_min (m):").grid(row=0, column=0, sticky="e")
        self.entry_rmin = tk.Entry(self.frame_malha, width=12)
        self.entry_rmin.insert(0, f"{1e-11:.5e}")
        self.entry_rmin.grid(row=0, column=1, padx=5, pady=2)
        
        # r_max (ponto final, em metros)
        tk.Label(self.frame_malha, text="r_max (m):").grid(row=0, column=2, sticky="e")
        self.entry_rmax = tk.Entry(self.frame_malha, width=12)
        self.entry_rmax.insert(0, f"{1e-9:.5e}")
        self.entry_rmax.grid(row=0, column=3, padx=5, pady=2)
        
        # Número de pontos da malha
        tk.Label(self.frame_malha, text="N (pontos):").grid(row=0, column=4, sticky="e")
        self.entry_N = tk.Entry(self.frame_malha, width=8)
        self.entry_N.insert(0, "1000")
        self.entry_N.grid(row=0, column=5, padx=5, pady=2)
        
        # Número atômico Z
        tk.Label(self.frame_malha, text="Z:").grid(row=1, column=0, sticky="e")
        self.entry_Z = tk.Entry(self.frame_malha, width=8)
        self.entry_Z.insert(0, f"{1:.5e}")
        self.entry_Z.grid(row=1, column=1, padx=5, pady=2)
        
        # Número quântico angular l
        tk.Label(self.frame_malha, text="l (número quântico):").grid(row=1, column=2, sticky="e")
        self.entry_l = tk.Entry(self.frame_malha, width=8)
        self.entry_l.insert(0, "0")
        self.entry_l.grid(row=1, column=3, padx=5, pady=2)
        
        # Índice do estado a visualizar (0 para o fundamental)
        tk.Label(self.frame_malha, text="Índice do estado (0 para fundamental):").grid(row=1, column=4, sticky="e")
        self.entry_estado = tk.Entry(self.frame_malha, width=8)
        self.entry_estado.insert(0, "0")
        self.entry_estado.grid(row=1, column=5, padx=5, pady=2)
        
        # --- Frame para as constantes físicas (SI) ---
        self.frame_constantes = tk.LabelFrame(self.frame_parametros, text="Constantes Físicas (SI)")
        self.frame_constantes.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Massa do elétron (m_e)
        tk.Label(self.frame_constantes, text="m_e (kg):").grid(row=0, column=0, sticky="e")
        self.entry_me = tk.Entry(self.frame_constantes, width=15)
        self.entry_me.insert(0, f"{9.10938356e-31:.5e}")
        self.entry_me.grid(row=0, column=1, padx=5, pady=2)
        
        # Constante de Planck reduzida (ℏ)
        tk.Label(self.frame_constantes, text="ℏ (J·s):").grid(row=0, column=2, sticky="e")
        self.entry_hbar = tk.Entry(self.frame_constantes, width=15)
        self.entry_hbar.insert(0, f"{1.0545718e-34:.5e}")
        self.entry_hbar.grid(row=0, column=3, padx=5, pady=2)
        
        # Carga elementar (e)
        tk.Label(self.frame_constantes, text="e (C):").grid(row=1, column=0, sticky="e")
        self.entry_e = tk.Entry(self.frame_constantes, width=15)
        self.entry_e.insert(0, f"{1.60217662e-19:.5e}")
        self.entry_e.grid(row=1, column=1, padx=5, pady=2)
        
        # Permissividade do vácuo (ε₀)
        tk.Label(self.frame_constantes, text="ε₀ (F/m):").grid(row=1, column=2, sticky="e")
        self.entry_epsilon0 = tk.Entry(self.frame_constantes, width=15)
        self.entry_epsilon0.insert(0, f"{8.854187817e-12:.5e}")
        self.entry_epsilon0.grid(row=1, column=3, padx=5, pady=2)
        
        # --- Botão para iniciar o cálculo ---
        self.botao_calcular = tk.Button(self.frame_parametros, text="Calcular", command=self.calcular)
        self.botao_calcular.pack(side=tk.TOP, padx=10, pady=5)
        
        # --- Frame para exibição dos gráficos e fórmulas ---
        self.frame_plot = tk.Frame(master)
        self.frame_plot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # --- Frame para exibição do passo a passo e logs ---
        self.frame_texto = tk.Frame(master)
        self.frame_texto.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.texto_passos = scrolledtext.ScrolledText(self.frame_texto, width=50, height=40, font=("Consolas", 10))
        self.texto_passos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # --- Exibição inicial das fórmulas via Matplotlib ---
        self.fig_formula, self.ax_formula = plt.subplots(figsize=(6, 8))
        self.ax_formula.axis('off')
        formula_text = r"""
Equação de Schrödinger (SI):

$\displaystyle -\frac{\hbar^2}{2m_e}\nabla^2\psi(\mathbf{r})
-\frac{Ze^2}{4\pi\epsilon_0\,r}\psi(\mathbf{r})
= E\psi(\mathbf{r})$

Separação de variáveis:
$\displaystyle \psi(r,\theta,\phi)=\frac{u(r)}{r}\,Y_{l}^{m}(\theta,\phi)$

Equação radial:
$\displaystyle -\frac{\hbar^2}{2m_e}\frac{d^2u}{dr^2}
+\left[\frac{\hbar^2l(l+1)}{2m_er^2}-\frac{Ze^2}{4\pi\epsilon_0\,r}\right]u(r)
= Eu(r)$

Discretização (diferenças finitas):
$\displaystyle u''(r_i)\approx \frac{u_{i+1}-2u_i+u_{i-1}}{\Delta r^2}$

Constantes Físicas (SI):
- $m_e=9.10938\times10^{-31}$ kg
- $\hbar=1.05457\times10^{-34}$ J·s
- $e=1.60218\times10^{-19}$ C
- $\epsilon_0=8.85419\times10^{-12}$ F/m
- Raio de Bohr: $a_0=5.29177\times10^{-11}$ m
- Energia de Rydberg: $Ry=13.6057$ eV
        """
        self.ax_formula.text(0.05, 0.5, formula_text, fontsize=12, va='center')
        self.canvas_formula = FigureCanvasTkAgg(self.fig_formula, master=self.frame_plot)
        self.canvas_formula.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def calcular(self):
        """Procedimento para discretizar a equação, montar a matriz Hamiltoniana completa
        (com constantes físicas) e resolver o problema de autovalores."""
        try:
            r_min      = float(self.entry_rmin.get())
            r_max      = float(self.entry_rmax.get())
            N          = int(self.entry_N.get())
            Z          = float(self.entry_Z.get())
            l_quantum  = int(self.entry_l.get())
            estado_ind = int(self.entry_estado.get())
            m_e        = float(self.entry_me.get())
            hbar       = float(self.entry_hbar.get())
            e_charge   = float(self.entry_e.get())
            epsilon0   = float(self.entry_epsilon0.get())
        except ValueError:
            self.texto_passos.insert(tk.END, "Erro: Verifique os valores de entrada.\n")
            return
        
        # Criação da malha radial
        r = np.linspace(r_min, r_max, N)
        dr = r[1] - r[0]
        
        # Constante cinética: K = ℏ²/(2m_e)
        K = hbar**2 / (2 * m_e)
        
        # Potencial Coulombiano: V(r) = -Z*e²/(4πε₀r)
        V = - Z * e_charge**2 / (4 * np.pi * epsilon0 * r)
        
        # Termo centrífugo: L(r) = K * l(l+1)/r²
        L_term = K * l_quantum * (l_quantum + 1) / (r**2)
        
        # Construção da matriz Hamiltoniana
        # A equação discretizada:
        #    -K (u[i+1]-2u[i]+u[i-1])/dr² + [K*l(l+1)/r[i]² + V[i]] u[i] = E u[i]
        H = np.zeros((N, N))
        diag    = (2*K/(dr**2)) + L_term + V    # elementos diagonais
        off_diag = -K/(dr**2) * np.ones(N-1)       # elementos off-diagonais
        
        # Monta a matriz
        np.fill_diagonal(H, diag)
        idx = np.arange(N-1)
        H[idx, idx+1] = off_diag
        H[idx+1, idx] = off_diag
        
        # Resolução do problema de autovalores
        autovalores, autovetores = np.linalg.eigh(H)
        
        # Verifica se o índice do estado é válido
        if estado_ind < 0 or estado_ind >= len(autovalores):
            self.texto_passos.insert(tk.END, "Erro: Índice do estado fora do intervalo.\n")
            return
        
        energia = autovalores[estado_ind]
        u = autovetores[:, estado_ind]
        
        # Normaliza u(r) de forma que ∫|u(r)|² dr = 1
        norma = np.trapz(u**2, r)
        u = u / np.sqrt(norma)
        
        # Calcula a função de onda radial R(r) = u(r)/r
        R = u / r
        
        # Converte a energia de Joules para elétron-volts (1 eV = 1.60217662e-19 J)
        energia_eV = energia / e_charge
        
        # Atualização do relatório de passos
        self.texto_passos.delete(1.0, tk.END)
        relatorio = ""
        relatorio += "Passo 1: Definição da malha radial\n"
        relatorio += f"  r_min = {r_min:.5e} m, r_max = {r_max:.5e} m, N = {N}\n"
        relatorio += f"  Δr = {dr:.5e} m\n\n"
        relatorio += "Passo 2: Parâmetros atômicos\n"
        relatorio += f"  Z = {Z:.5e}\n"
        relatorio += f"  Número quântico l = {l_quantum}\n"
        relatorio += f"  Estado selecionado (índice) = {estado_ind}\n\n"
        relatorio += "Passo 3: Constantes físicas utilizadas\n"
        relatorio += f"  m_e = {m_e:.5e} kg\n"
        relatorio += f"  ℏ = {hbar:.5e} J·s\n"
        relatorio += f"  e = {e_charge:.5e} C\n"
        relatorio += f"  ε₀ = {epsilon0:.5e} F/m\n\n"
        relatorio += "Passo 4: Construção da matriz Hamiltoniana\n"
        relatorio += "  Diagonal: 2K/Δr² + K*l(l+1)/r² - Z*e²/(4πε₀r)\n"
        relatorio += "  Off-diagonais: -K/Δr²\n\n"
        relatorio += "Passo 5: Resolução do problema de autovalores\n"
        relatorio += f"  Energia selecionada: {energia:.8e} J = {energia_eV:.8e} eV\n\n"
        relatorio += "Passo 6: Normalização da função u(r)\n"
        relatorio += f"  Norma calculada: {norma:.8e}\n\n"
        relatorio += "Passo 7: Cálculo da função radial R(r) = u(r)/r\n"
        self.texto_passos.insert(tk.END, relatorio)
        
        # --- Plot dos resultados ---
        # Vamos plotar u(r) (função auxiliar) e, em outro subplot, R(r) e V(r)
        fig, ax = plt.subplots(2, 1, figsize=(7, 8), sharex=True)
        
        # Gráfico de u(r)
        ax[0].plot(r, u, label="u(r)", color="blue")
        ax[0].set_ylabel("u(r)")
        ax[0].legend(loc="upper right")
        ax[0].grid(True)
        
        # Gráfico de R(r) e do potencial V(r)
        ax[1].plot(r, R, label="R(r)", color="green")
        ax[1].plot(r, V, label="V(r)", color="red", linestyle="--")
        ax[1].set_xlabel("r (m)")
        ax[1].set_ylabel("Amplitude")
        ax[1].legend(loc="upper right")
        ax[1].grid(True)
        ax[1].set_title(f"Energia: {energia:.8e} J   ({energia_eV:.8e} eV)")
        
        # Atualiza a área de plot: remove o widget antigo e insere o novo
        for widget in self.frame_plot.winfo_children():
            widget.destroy()
        self.canvas_resultado = FigureCanvasTkAgg(fig, master=self.frame_plot)
        self.canvas_resultado.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas_resultado.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulacaoHidrogenioCompleta(root)
    root.mainloop()
