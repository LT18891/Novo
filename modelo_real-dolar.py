#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelo estocástico avançado para a desvalorização do Real – interface Tkinter.

Autor: LT
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.integrate import solve_ivp


# ---------------------------------------------------------------------------
# Entry com placeholder
# ---------------------------------------------------------------------------
class PlaceholderEntry(tk.Entry):
    def __init__(self, master, placeholder, color="grey", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._ph = placeholder
        self._ph_color = color
        self._normal_fg = self["fg"]
        self.bind("<FocusIn>", self._on_in)
        self.bind("<FocusOut>", self._on_out)
        self._on_out()

    def _on_in(self, *_):
        if self.get() == self._ph:
            self.delete(0, tk.END)
            self["fg"] = self._normal_fg

    def _on_out(self, *_):
        if not self.get():
            self.insert(0, self._ph)
            self["fg"] = self._ph_color


# ---------------------------------------------------------------------------
# Parâmetros padrão e estruturas auxiliares
# ---------------------------------------------------------------------------
defaults = {
    'α': 0.10, 'β': 0.05, 'γ': 0.02, 'δ': 0.30,
    'ε': 0.15, 'ζ': 0.10, 'η': 0.20, 'θ': 0.05,
    'ι': 0.03, 'κ': 0.01, 'λ': 0.07, 'x0': 3.50,
    'y0': 0.00, 'μ': 0.04, 'ν': 0.03, 'ξ': 0.02,
    'ο': 0.01   # omicron
}

placeholders = {k: f"{k} (padrão {v})" for k, v in defaults.items()}
vars_entry: dict[str, PlaceholderEntry] = {}


# ---------------------------------------------------------------------------
# Leitura segura dos parâmetros
# ---------------------------------------------------------------------------
def _param(sym: str) -> float:
    txt = vars_entry[sym].get()
    if txt == placeholders[sym]:
        return defaults[sym]
    try:
        return float(txt)
    except ValueError:
        messagebox.showwarning(
            "Entrada inválida",
            f"Valor inválido para {sym}. Usando padrão {defaults[sym]:.4f}."
        )
        vars_entry[sym].delete(0, tk.END)
        vars_entry[sym].insert(0, str(defaults[sym]))
        return defaults[sym]


# ---------------------------------------------------------------------------
# Renderização das equações
# ---------------------------------------------------------------------------
def renderizar_equacoes() -> None:
    p = {s: _param(s) for s in defaults}

    eq = [
        rf"\frac{{dx}}{{dt}} = {p['α']}x + {p['β']}y - {p['γ']}x^2 z + {p['δ']}\sin(z)",
        rf"\frac{{dy}}{{dt}} = {p['ε']}(x - {p['x0']}) - {p['ζ']}y^2 + {p['η']}\cos(x)",
        rf"\frac{{dz}}{{dt}} = {p['θ']}(y - {p['y0']}) + {p['ι']}xz - {p['κ']}z^3 + {p['λ']}\ln(1+x^2)",
        rf"\frac{{dw}}{{dt}} = {p['μ']}xy - {p['ν']}w + {p['ξ']}\sin(zw) + {p['ο']}\ln(1+|xy|)"
    ]

    win = tk.Toplevel(janela)
    win.title("Equações – LT")

    fig = plt.Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    ax.axis("off")
    for i, e in enumerate(eq):
        ax.text(0.02, 0.9 - i * 0.22, f"${e}$", ha="left", fontsize=12)

    FigureCanvasTkAgg(fig, master=win).get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


# ---------------------------------------------------------------------------
# Simulação numérica e gráfico
# ---------------------------------------------------------------------------
def simular_e_plotar() -> None:
    α, β, γ, δ = _param('α'), _param('β'), _param('γ'), _param('δ')
    ε, ζ, η, θ = _param('ε'), _param('ζ'), _param('η'), _param('θ')
    ι, κ, λ = _param('ι'), _param('κ'), _param('λ')
    x0, y0 = _param('x0'), _param('y0')
    μ, ν, ξ, ο = _param('μ'), _param('ν'), _param('ξ'), _param('ο')

    def sistema(_, u):
        x, y, z, w = u
        dx = α*x + β*y - γ*x**2*z + δ*math.sin(z)
        dy = ε*(x - x0) - ζ*y**2 + η*math.cos(x)
        dz = θ*(y - y0) + ι*x*z - κ*z**3 + λ*math.log(1 + x**2)
        dw = μ*x*y - ν*w + ξ*math.sin(z*w) + ο*math.log(1 + abs(x*y))
        return [dx, dy, dz, dw]

    t_eval = np.linspace(0, 10, 600)
    sol = solve_ivp(sistema, [0, 10], [3.0, 0.0, 0.5, 0.1], t_eval=t_eval)

    win = tk.Toplevel(janela)
    win.title("Evolução – LT")

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(sol.t, sol.y.T)
    ax.set_xlabel("Tempo (t)")
    ax.set_ylabel("Valor")
    ax.legend(["x", "y", "z", "w"])
    ax.grid(True)

    FigureCanvasTkAgg(fig, master=win).get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)


# ---------------------------------------------------------------------------
# Interface gráfica principal
# ---------------------------------------------------------------------------
janela = tk.Tk()
janela.title("Modelo Desvalorização do Real – LT")

frm = ttk.Frame(janela, padding=10)
frm.pack()

for row, simb in enumerate(defaults):
    ttk.Label(frm, text=f"{simb}:").grid(row=row, column=0, sticky="e", padx=4, pady=2)
    ent = PlaceholderEntry(frm, placeholders[simb], width=12)
    ent.grid(row=row, column=1, padx=4, pady=2)
    vars_entry[simb] = ent

btn_box = ttk.Frame(frm)
btn_box.grid(row=len(defaults), column=0, columnspan=2, pady=(8, 0))
ttk.Button(btn_box, text="Renderizar Equações", command=renderizar_equacoes).pack(side="left", padx=5)
ttk.Button(btn_box, text="Simular e Plotar",    command=simular_e_plotar).pack(side="left", padx=5)

ttk.Label(janela, text="© LT", anchor="e").pack(fill="x", padx=5, pady=(0, 5))

janela.mainloop()
