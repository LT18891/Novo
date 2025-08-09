#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculadora de Preço do Petróleo — Modelo Estatístico Avançado (Brent)
Autor: Luiz Tiago Wilcke

Descrição geral
---------------
Modelo híbrido para previsão do preço do petróleo (US$/bbl) combinando:
1) Componente estrutural "normal" (P_normal) com variáveis fundamentais;
2) Componente de "superciclo" (P_super), ponderado por um regime (logístico);
3) Termo de correção de equilíbrio de longo prazo (ECM);
4) Termo AR(2) para capturar persistência de choques/resíduos recentes.

Interface em Tkinter, com:
- Abas: Calculadora | Equações | Sobre
- Entradas em português, botões de calcular/limpar
- Renderização de equações com Matplotlib (MathText compatível)
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox

# ---------- Matplotlib embutido no Tkinter (render das equações) ----------
import matplotlib
matplotlib.use("TkAgg")  # backend adequado para Tkinter

from matplotlib import rcParams
rcParams["mathtext.fontset"] = "dejavusans"   # bom suporte a unicode
rcParams["font.family"] = "DejaVu Sans"

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------- PARÂMETROS PADRÃO DO MODELO ------------------------
# Coeficientes do regime (índice de aperto S e peso w)
GAMMAS = {
    "g0": -0.20,   # constante do índice S
    "g1":  0.50,   # demanda - oferta (mbpd)
    "g2":  0.30,   # -capacidade ociosa (mbpd)  (entra com sinal negativo no S)
    "g3":  0.25,   # risco geopolítico (0..10)
    "g4":  0.15,   # backwardation (proxy via -min(0, slope))
}
# Coeficientes do componente NORMAL (P_normal)
BETAS = {
    "b0": 10.0,    # constante
    "b1": 12.0,    # ln(demanda_global)
    "b2": 10.0,    # -ln(estoques_ocde_dias)
    "b3":  6.0,    # -ln(indice_dolar)
    "b4":  1.0,    # -taxa_juros_eua (%)
    "b5":  0.7,    # slope_curva (US$/bbl, 12m - spot)
    "b6":  0.03,   # posicao_especulativa (mil contratos)
    "b7":  0.6,    # custo_marginal (US$/bbl)
}

# Coeficientes do componente SUPERCICLO (P_super)
THETAS = {
    "t0":  5.0,    # constante
    "t1":  9.0,    # razão demanda/oferta (adimensional), escalada
    "t2":  1.1,    # conveniência (conv = -slope se slope<0, senão 0)
    "t3":  0.8,    # custo_marginal
    "t4":  2.0,    # risco geopolítico
}

# Equilíbrio de longo prazo (P_lr) e correção (ECM)
DELTAS = {
    "d0":  8.0,
    "d1": 14.0,    # ln(demanda_global)
    "d2": 11.0,    # -ln(estoques_ocde_dias)
    "d3":  0.7,    # ln(custo_marginal)
}
KAPPA = 0.35       # peso da correção (proximidade ao equilíbrio de longo prazo)

# Dinâmica de ruído AR(2)
PHI1 = 0.45
PHI2 = 0.20

# Valores iniciais (sensatos para 2024/2025)
DEFAULTS = {
    "demanda_global":       103.0,  # mbpd
    "oferta_global":        103.0,  # mbpd
    "estoques_ocde_dias":   60.0,   # dias de cobertura
    "indice_dolar":         100.0,  # DXY
    "taxa_juros_eua":       5.50,   # %
    "slope_curva":          -2.0,   # US$/bbl (12m - spot); negativo = backwardation
    "risco_geopolitico":    3.0,    # 0..10
    "posicao_especulativa": 300.0,  # mil contratos líquidos (CFTC)
    "capacidade_ociosa":    2.5,    # mbpd (OPEP+)
    "custo_marginal":       55.0,   # US$/bbl (marginal global)
    "erro_ar_1":            0.0,    # último resíduo (US$)
    "erro_ar_2":            0.0,    # penúltimo resíduo (US$)
}

# ---------------------------- CÁLCULOS DO MODELO ---------------------------

def indice_aperto_regime(demanda, oferta, capacidade_ociosa, risco, slope):
    """
    Índice de aperto S para o regime:
        S = g0 + g1*(demanda - oferta) - g2*(capacidade_ociosa) + g3*(risco)
            + g4*backwardation
        backwardation = max(0, -slope)
    """
    backwardation = max(0.0, -slope)
    S = (GAMMAS["g0"]
         + GAMMAS["g1"] * (demanda - oferta)
         - GAMMAS["g2"] * capacidade_ociosa
         + GAMMAS["g3"] * risco
         + GAMMAS["g4"] * backwardation)
    return S

def peso_regime(S):
    """Peso logístico w no regime de 'superciclo': w = 1 / (1 + e^{-S})."""
    try:
        return 1.0 / (1.0 + math.exp(-S))
    except OverflowError:
        return 1.0 if S > 0 else 0.0

def componente_normal(demanda, estoques_dias, indice_dolar, juros, slope, espec, custo):
    """
    P_normal = b0 + b1*ln(demanda) - b2*ln(estoques_dias) - b3*ln(indice_dolar)
               - b4*juros + b5*slope + b6*espec + b7*custo
    """
    if demanda <= 0 or estoques_dias <= 0 or indice_dolar <= 0 or custo <= 0:
        raise ValueError("Variáveis em log devem ser positivas (demanda, estoques, dólar, custo).")
    return (BETAS["b0"]
            + BETAS["b1"] * math.log(demanda)
            - BETAS["b2"] * math.log(estoques_dias)
            - BETAS["b3"] * math.log(indice_dolar)
            - BETAS["b4"] * juros
            + BETAS["b5"] * slope
            + BETAS["b6"] * espec
            + BETAS["b7"] * custo)

def componente_superciclo(demanda, oferta, slope, custo, risco):
    """
    P_super = t0 + t1*(demanda/oferta)*10 + t2*conv + t3*custo + t4*risco
      conv (conveniência) ≈ -slope se slope<0 (backwardation), senão 0.
    """
    if oferta <= 0:
        raise ValueError("Oferta deve ser positiva.")
    conv = -slope if slope < 0 else 0.0
    return (THETAS["t0"]
            + THETAS["t1"] * (demanda / oferta) * 10.0
            + THETAS["t2"] * conv
            + THETAS["t3"] * custo
            + THETAS["t4"] * risco)

def equilibrio_longo_prazo(demanda, estoques_dias, custo):
    """
    P_lr = d0 + d1*ln(demanda) - d2*ln(estoques_dias) + d3*ln(custo)
    """
    if demanda <= 0 or estoques_dias <= 0 or custo <= 0:
        raise ValueError("Variáveis em log devem ser positivas (demanda, estoques, custo).")
    return (DELTAS["d0"]
            + DELTAS["d1"] * math.log(demanda)
            - DELTAS["d2"] * math.log(estoques_dias)
            + DELTAS["d3"] * math.log(custo))

def previsao_preco(params):
    """
    Une todas as camadas:
      S -> w
      P = w*P_super + (1-w)*P_normal + kappa*(P_lr - P_normal) + AR(2)
    Retorna dicionário com decomposição.
    """
    demanda = params["demanda_global"]
    oferta = params["oferta_global"]
    estoques = params["estoques_ocde_dias"]
    dolar = params["indice_dolar"]
    juros = params["taxa_juros_eua"]
    slope = params["slope_curva"]
    risco = params["risco_geopolitico"]
    espec = params["posicao_especulativa"]
    cap_ocio = params["capacidade_ociosa"]
    custo = params["custo_marginal"]
    e1 = params["erro_ar_1"]
    e2 = params["erro_ar_2"]

    S = indice_aperto_regime(demanda, oferta, cap_ocio, risco, slope)
    w = peso_regime(S)
    Pn = componente_normal(demanda, estoques, dolar, juros, slope, espec, custo)
    Ps = componente_superciclo(demanda, oferta, slope, custo, risco)
    Plr = equilibrio_longo_prazo(demanda, estoques, custo)

    ecm = KAPPA * (Plr - Pn)
    ar = PHI1 * e1 + PHI2 * e2

    P = w * Ps + (1.0 - w) * Pn + ecm + ar

    return {
        "S": S,
        "w": w,
        "P_normal": Pn,
        "P_super": Ps,
        "P_lr": Plr,
        "ECM": ecm,
        "AR": ar,
        "P_previsto": P
    }

# ----------------------------- INTERFACE TKINTER ----------------------------

class CalculadoraPetroleo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora — Preço do Petróleo (Brent) | Autor: Luiz Tiago Wilcke")
        self.geometry("980x740")
        self.minsize(920, 660)
        self._build_ui()

    # ---------- UI ----------
    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.frame_calc = ttk.Frame(notebook)
        self.frame_eq = ttk.Frame(notebook)
        self.frame_sobre = ttk.Frame(notebook)

        notebook.add(self.frame_calc, text="Calculadora")
        notebook.add(self.frame_eq, text="Equações")
        notebook.add(self.frame_sobre, text="Sobre")

        self._build_calc_tab()
        self._build_equations_tab()
        self._build_about_tab()

    def _build_calc_tab(self):
        # Esquerda: entradas
        left = ttk.Frame(self.frame_calc, padding=10)
        left.pack(side="left", fill="y")

        self.vars = {}
        entradas = [
            ("demanda_global",       "Demanda global (mbpd)", DEFAULTS["demanda_global"]),
            ("oferta_global",        "Oferta global (mbpd)",  DEFAULTS["oferta_global"]),
            ("estoques_ocde_dias",   "Estoques OCDE (dias)",  DEFAULTS["estoques_ocde_dias"]),
            ("indice_dolar",         "Índice do Dólar (DXY)", DEFAULTS["indice_dolar"]),
            ("taxa_juros_eua",       "Taxa de juros EUA (%)", DEFAULTS["taxa_juros_eua"]),
            ("slope_curva",          "Slope da curva (12m-spot, US$/bbl)", DEFAULTS["slope_curva"]),
            ("risco_geopolitico",    "Risco geopolítico (0–10)", DEFAULTS["risco_geopolitico"]),
            ("posicao_especulativa", "Posição especulativa (mil contratos)", DEFAULTS["posicao_especulativa"]),
            ("capacidade_ociosa",    "Capacidade ociosa OPEP+ (mbpd)", DEFAULTS["capacidade_ociosa"]),
            ("custo_marginal",       "Custo marginal global (US$/bbl)", DEFAULTS["custo_marginal"]),
            ("erro_ar_1",            "Erro AR t-1 (US$)", DEFAULTS["erro_ar_1"]),
            ("erro_ar_2",            "Erro AR t-2 (US$)", DEFAULTS["erro_ar_2"]),
        ]

        for key, label, val in entradas:
            ttk.Label(left, text=label).pack(anchor="w", pady=(6, 0))
            sv = tk.StringVar(value=str(val))
            self.vars[key] = sv
            ttk.Entry(left, textvariable=sv, width=26).pack(anchor="w")

        btns = ttk.Frame(left)
        btns.pack(anchor="w", pady=12)
        ttk.Button(btns, text="Calcular preço", command=self.on_calcular).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Limpar", command=self.on_limpar).grid(row=0, column=1)

        # Direita: resultados e gráfico de decomposição
        right = ttk.Frame(self.frame_calc, padding=10)
        right.pack(side="left", fill="both", expand=True)

        # Saída textual
        self.txt = tk.Text(right, height=14, wrap="word")
        self.txt.pack(fill="x", pady=(0, 10))
        self.txt.configure(state="disabled")

        # Gráfico (barras) de decomposição
        fig = Figure(figsize=(6.6, 3.8), dpi=120)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Decomposição da previsão (US$/bbl)")
        self.ax.set_ylabel("US$/bbl")

        self.canvas_fig = FigureCanvasTkAgg(fig, master=right)
        self.canvas_fig.get_tk_widget().pack(fill="both", expand=True)

        self._plot_placeholder()

    def _plot_placeholder(self):
        self.ax.clear()
        self.ax.set_title("Decomposição da previsão (US$/bbl)")
        self.ax.set_ylabel("US$/bbl")
        self.ax.bar(["P_normal", "P_super", "ECM", "AR", "P_final"], [0, 0, 0, 0, 0])
        self.canvas_fig.draw_idle()

    def _build_equations_tab(self):
        # Figura com as equações renderizadas (mathtext seguro para o backend do Matplotlib)
        fig = Figure(figsize=(8.6, 9.6), dpi=120)
        ax = fig.add_subplot(111)
        ax.axis("off")

        y = 0.98
        dy_header = 0.06
        dy_line = 0.055

        def header(txt):
            nonlocal y
            # Cabeçalho como TEXTO normal (pode usar acento aqui)
            ax.text(0.02, y, txt, va="top", fontsize=16, fontweight="bold")
            y -= dy_header

        def line_math(tex):
            nonlocal y
            # Linhas em modo matemático: sem acentos e sem \text / \begin{cases}
            ax.text(0.02, y, rf"${tex}$", va="top", fontsize=13)
            y -= dy_line

        # Camada de regime
        header("Camada de Regime")
        line_math(r"S = g_0 + g_1\,(Demanda-Oferta) - g_2\,CapOciosa + g_3\,Risco + g_4\,\max(0,-Slope)")
        line_math(r"w = \frac{1}{1 + e^{-S}}")

        # Componente Normal
        header("Componente Normal")
        line_math(r"P_{\mathrm{normal}} = b_0 + b_1\ln(Demanda) - b_2\ln(Estoques) - b_3\ln(IndiceDolar) - b_4\,Juros")
        line_math(r"\qquad +\ b_5\,Slope + b_6\,PosicaoEspec + b_7\,CustoMarginal")

        # Componente Superciclo
        header("Componente Superciclo")
        # Evitamos \begin{cases}: descrevemos as duas condições em linhas separadas
        line_math(r"Conv = -Slope \quad (Slope<0)")
        line_math(r"Conv = 0 \quad (Slope \geq 0)")
        line_math(r"P_{\mathrm{super}} = t_0 + t_1\cdot 10\cdot \frac{Demanda}{Oferta} + t_2\,Conv + t_3\,CustoMarginal + t_4\,Risco")

        # Equilíbrio de Longo Prazo (Cointegração)
        header("Equilíbrio de Longo Prazo (Cointegração)")
        line_math(r"P_{LR} = d_0 + d_1\ln(Demanda) - d_2\ln(Estoques) + d_3\ln(CustoMarginal)")
        line_math(r"ECM = \kappa\,(P_{LR} - P_{\mathrm{normal}})")

        # Ruído AR(2)
        header("Ruído AR(2)")
        line_math(r"AR = \phi_1\,\varepsilon_{t-1} + \phi_2\,\varepsilon_{t-2}")

        # Preço Previsto
        header("Preço Previsto")
        line_math(r"P = w\,P_{\mathrm{super}} + (1-w)\,P_{\mathrm{normal}} + ECM + AR")

        self.eq_canvas = FigureCanvasTkAgg(fig, master=self.frame_eq)
        self.eq_canvas.get_tk_widget().pack(fill="both", expand=True)
        self.eq_canvas.draw()  # garante o desenho das fórmulas

    def _build_about_tab(self):
        txt = tk.Text(self.frame_sobre, wrap="word")
        txt.pack(fill="both", expand=True, padx=10, pady=10)
        txt.insert("1.0",
                   "Calculadora do modelo de preço do petróleo (Brent)\n"
                   "Autor: Luiz Tiago Wilcke\n\n"
                   "Este app implementa um modelo híbrido com regime logístico, camada "
                   "estrutural baseada em fundamentos (demanda, estoques, dólar, juros, "
                   "inclinação da curva, especulação e custo marginal), componente de "
                   "superciclo (capacidade ociosa, conveniência e risco) e um termo de "
                   "correção ao equilíbrio de longo prazo (ECM), além de AR(2) para a "
                   "persistência de choques.\n\n"
                   "Aba Calculadora: insira variáveis e veja a decomposição e o preço previsto.\n"
                   "Aba Equações: formulação matemática renderizada.")
        txt.configure(state="disabled")

    # ---------- callbacks ----------
    def _leitura_params(self):
        vals = {}
        try:
            for k, sv in self.vars.items():
                vals[k] = float(sv.get())
        except ValueError:
            raise ValueError("Verifique se todos os campos numéricos foram preenchidos corretamente.")
        return vals

    def on_calcular(self):
        try:
            p = self._leitura_params()
            res = previsao_preco(p)
            self._atualiza_texto(res)
            self._atualiza_grafico(res)
        except Exception as e:
            messagebox.showerror("Erro no cálculo", str(e))

    def on_limpar(self):
        for k, sv in self.vars.items():
            sv.set("")
        self._plot_placeholder()
        self._set_texto("")

    def _set_texto(self, conteudo):
        self.txt.configure(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", conteudo)
        self.txt.configure(state="disabled")

    def _atualiza_texto(self, res):
        txt = []
        txt.append("==== Resultado da Previsão ====\n")
        txt.append(f"Índice de aperto (S): {res['S']:.3f}")
        txt.append(f"Peso de regime (w): {res['w']:.3f}\n")

        txt.append(f"P_normal (estrutural): {res['P_normal']:.2f} US$/bbl")
        txt.append(f"P_super (superciclo): {res['P_super']:.2f} US$/bbl")
        txt.append(f"P_LR (equilíbrio longo prazo): {res['P_lr']:.2f} US$/bbl")
        txt.append(f"ECM (correção): {res['ECM']:.2f} US$/bbl")
        txt.append(f"AR(2): {res['AR']:.2f} US$/bbl\n")

        txt.append(f"Preço previsto (Brent): {res['P_previsto']:.2f} US$/bbl\n")

        txt.append("Interpretação rápida:\n")
        txt.append("- Quanto maior (Demanda - Oferta) e o risco geopolítico, maior o peso do regime (w).\n")
        txt.append("- Backwardation (slope < 0) eleva o componente de superciclo via conveniência.\n")
        txt.append("- Dólar forte e juros altos tendem a pressionar P_normal para baixo.\n")
        txt.append("- O ECM aproxima a previsão do equilíbrio estimado por fundamentais.")
        self._set_texto("\n".join(txt))

    def _atualiza_grafico(self, res):
        self.ax.clear()
        self.ax.set_title("Decomposição da previsão (US$/bbl)")
        self.ax.set_ylabel("US$/bbl")

        barras = ["P_normal", "P_super", "ECM", "AR", "P_final"]
        valores = [res["P_normal"], res["P_super"], res["ECM"], res["AR"], res["P_previsto"]]
        self.ax.bar(barras, valores)
        for i, v in enumerate(valores):
            self.ax.text(i, v + (1.5 if v >= 0 else -1.5), f"{v:.1f}",
                         ha="center", va="bottom" if v >= 0 else "top")
        self.canvas_fig.draw_idle()

# ------------------------------- MAIN --------------------------------------

def main():
    app = CalculadoraPetroleo()
    app.mainloop()

if __name__ == "__main__":
    main()
