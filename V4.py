import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np
import pandas as pd
from datetime import datetime
import math

# Biblioteca para "hover" com anotações
import mplcursors

# ============================== CONFIGURAÇÕES ==============================

URL_API = "https://api.coingecko.com/api/v3/simple/price"
PARAMETROS_API = {
    'ids': 'bitcoin',
    'vs_currencies': 'usd,brl,eur'  # Traz USD, BRL e EUR
}

INTERVALO_ATUALIZACAO = 20000  # 20 segundos (em milissegundos)

# ============================== CLASSE PRINCIPAL ==============================

class AplicacaoBitcoin:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Monitor de Preço do Bitcoin")
        self.raiz.geometry("1200x900")

        # Variáveis de controle
        self.ativos = False
        
        # DataFrame com colunas para tempo, USD, BRL, EUR
        self.df = pd.DataFrame(columns=['Tempo', 'USD', 'BRL', 'EUR'])
        
        # Lista para registrar as operações de compra/venda (exemplo fictício)
        self.compras_vendas = []

        # Configurar a interface
        self.configurar_gui()

    def configurar_gui(self):
        """Configura toda a interface gráfica (Tkinter)."""
        # ============ FRAME DE CONTROLES SUPERIOR ============
        frame_controles = ttk.Frame(self.raiz)
        frame_controles.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.botao_iniciar = ttk.Button(
            frame_controles, text="Iniciar Monitoramento", 
            command=self.iniciar_monitoramento
        )
        self.botao_iniciar.pack(side=tk.LEFT, padx=5)

        self.botao_parar = ttk.Button(
            frame_controles, text="Parar Monitoramento", 
            command=self.parar_monitoramento, state=tk.DISABLED
        )
        self.botao_parar.pack(side=tk.LEFT, padx=5)

        self.botao_relatorio = ttk.Button(
            frame_controles, text="Gerar Relatório", 
            command=self.gerar_relatorio, state=tk.DISABLED
        )
        self.botao_relatorio.pack(side=tk.LEFT, padx=5)

        # Botões de compra e venda (exemplo)
        self.botao_comprar = ttk.Button(frame_controles, text="Comprar BTC", command=self.comprar_btc)
        self.botao_comprar.pack(side=tk.LEFT, padx=5)

        self.botao_vender = ttk.Button(frame_controles, text="Vender BTC", command=self.vender_btc)
        self.botao_vender.pack(side=tk.LEFT, padx=5)

        # ============ FRAME PARA O GRÁFICO PRINCIPAL ============
        frame_grafico = ttk.Frame(self.raiz)
        frame_grafico.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Cria a figura e o Axes do matplotlib
        self.figura = plt.Figure(figsize=(10, 6), facecolor='black')
        self.ax = self.figura.add_subplot(111, facecolor='black')

        # Título e rótulos
        self.ax.set_title("Preço do Bitcoin em Tempo Real (USD, BRL, EUR)", 
                          fontsize=16, color='white')
        self.ax.set_xlabel("Tempo", fontsize=12, color='white')
        self.ax.set_ylabel("Preço", fontsize=12, color='white')

        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')

        # Canvas do Tkinter para o gráfico
        self.canvas = FigureCanvasTkAgg(self.figura, master=frame_grafico)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # ============ FRAME DE ESTATÍSTICAS ============
        frame_estatisticas = ttk.Frame(self.raiz)
        frame_estatisticas.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Labels para cada moeda
        # -- USD --
        self.label_media_usd = ttk.Label(frame_estatisticas, text="Média (USD): N/A", font=('Arial', 12))
        self.label_media_usd.pack(side=tk.LEFT, padx=10)

        self.label_max_usd = ttk.Label(frame_estatisticas, text="Máx (USD): N/A", font=('Arial', 12))
        self.label_max_usd.pack(side=tk.LEFT, padx=10)

        self.label_min_usd = ttk.Label(frame_estatisticas, text="Mín (USD): N/A", font=('Arial', 12))
        self.label_min_usd.pack(side=tk.LEFT, padx=10)

        # -- BRL --
        self.label_media_brl = ttk.Label(frame_estatisticas, text="Média (BRL): N/A", font=('Arial', 12))
        self.label_media_brl.pack(side=tk.LEFT, padx=10)

        self.label_max_brl = ttk.Label(frame_estatisticas, text="Máx (BRL): N/A", font=('Arial', 12))
        self.label_max_brl.pack(side=tk.LEFT, padx=10)

        self.label_min_brl = ttk.Label(frame_estatisticas, text="Mín (BRL): N/A", font=('Arial', 12))
        self.label_min_brl.pack(side=tk.LEFT, padx=10)

        # -- EUR --
        self.label_media_eur = ttk.Label(frame_estatisticas, text="Média (EUR): N/A", font=('Arial', 12))
        self.label_media_eur.pack(side=tk.LEFT, padx=10)

        self.label_max_eur = ttk.Label(frame_estatisticas, text="Máx (EUR): N/A", font=('Arial', 12))
        self.label_max_eur.pack(side=tk.LEFT, padx=10)

        self.label_min_eur = ttk.Label(frame_estatisticas, text="Mín (EUR): N/A", font=('Arial', 12))
        self.label_min_eur.pack(side=tk.LEFT, padx=10)

        # ============ FRAME DE STATUS ============
        frame_status = ttk.Frame(self.raiz)
        frame_status.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.label_status = ttk.Label(frame_status, text="Status: Parado", foreground="red", font=('Arial', 12))
        self.label_status.pack(side=tk.LEFT, padx=5)

    # ============================== FUNÇÕES DE COMPRA E VENDA (EXEMPLO) ==============================
    def comprar_btc(self):
        """Exemplo fictício de operação de compra."""
        if not self.df.empty:
            ultimo_usd = self.df['USD'].iloc[-1]
            self.compras_vendas.append({"Tipo": "Compra", "Preço": ultimo_usd, "Tempo": datetime.now()})
            messagebox.showinfo("Compra", f"Compra realizada a ${ultimo_usd:.2f}")
        else:
            messagebox.showwarning("Aviso", "Nenhum dado disponível para realizar compra.")

    def vender_btc(self):
        """Exemplo fictício de operação de venda."""
        if not self.df.empty:
            ultimo_usd = self.df['USD'].iloc[-1]
            self.compras_vendas.append({"Tipo": "Venda", "Preço": ultimo_usd, "Tempo": datetime.now()})
            messagebox.showinfo("Venda", f"Venda realizada a ${ultimo_usd:.2f}")
        else:
            messagebox.showwarning("Aviso", "Nenhum dado disponível para realizar venda.")

    # ============================== MONITORAMENTO DE PREÇOS ==============================
    def iniciar_monitoramento(self):
        """Inicia o monitoramento (animação) e bloqueia os botões adequados."""
        if not self.ativos:
            self.ativos = True
            self.botao_iniciar.config(state=tk.DISABLED)
            self.botao_parar.config(state=tk.NORMAL)
            self.botao_relatorio.config(state=tk.DISABLED)
            self.label_status.config(text="Status: Monitorando...", foreground="green")

            # Inicia a animação do matplotlib para atualizar o gráfico
            self.anim = animation.FuncAnimation(
                self.figura, self.atualizar_grafico, 
                interval=INTERVALO_ATUALIZACAO, blit=False
            )
            # Força uma atualização inicial imediata
            self.atualizar_grafico(None)

    def parar_monitoramento(self):
        """Para o monitoramento (animação) e libera os botões adequados."""
        if self.ativos:
            self.ativos = False
            self.botao_iniciar.config(state=tk.NORMAL)
            self.botao_parar.config(state=tk.DISABLED)
            self.botao_relatorio.config(state=tk.NORMAL)
            self.label_status.config(text="Status: Parado", foreground="red")

            # Para a animação
            if hasattr(self, 'anim'):
                self.anim.event_source.stop()

    def atualizar_grafico(self, frame):
        """Captura os preços da API, atualiza df e redesenha o gráfico com USD, BRL, EUR."""
        if not self.ativos:
            return

        try:
            resposta = requests.get(URL_API, params=PARAMETROS_API, timeout=10)
            resposta.raise_for_status()
            dados = resposta.json()

            # Obter preços
            preco_usd = dados['bitcoin']['usd']
            preco_brl = dados['bitcoin']['brl']
            preco_eur = dados['bitcoin']['eur']

            # Atualiza DataFrame
            tempo_atual = datetime.now().strftime('%H:%M:%S')
            nova_linha = pd.DataFrame({
                'Tempo': [tempo_atual],
                'USD': [preco_usd],
                'BRL': [preco_brl],
                'EUR': [preco_eur]
            })
            self.df = pd.concat([self.df, nova_linha], ignore_index=True)

            # Limita para os últimos 200 pontos
            if len(self.df) > 200:
                self.df = self.df.iloc[-200:].reset_index(drop=True)

            # ================= Calcula indicadores para USD =================
            self.calcular_rsi(column='USD', periodo=14)
            self.calcular_macd(column='USD', span_short=12, span_long=26, span_signal=9)

            # ================= Desenha as linhas =================
            self.ax.clear()
            self.ax.set_facecolor('black')
            self.ax.set_title("Preço do Bitcoin em Tempo Real (USD, BRL, EUR)", 
                              fontsize=16, color='white')
            self.ax.set_xlabel("Tempo", fontsize=12, color='white')
            self.ax.set_ylabel("Preço", fontsize=12, color='white')
            self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')

            x_values = range(len(self.df))

            # Plot das 3 linhas (USD, BRL, EUR) - cada uma com cor diferente
            line_usd, = self.ax.plot(x_values, self.df['USD'], color='cyan',  label='USD')
            line_brl, = self.ax.plot(x_values, self.df['BRL'], color='lime',  label='BRL')
            line_eur, = self.ax.plot(x_values, self.df['EUR'], color='orange', label='EUR')

            # Ajuste dos eixos
            self.ax.set_xlim(0, len(self.df) - 1 if len(self.df) > 1 else 1)

            # Para ficar visualmente adequado, pegamos min e max entre as 3 colunas
            precios_min = min(self.df['USD'].min(), self.df['BRL'].min(), self.df['EUR'].min())
            precios_max = max(self.df['USD'].max(), self.df['BRL'].max(), self.df['EUR'].max())
            self.ax.set_ylim(precios_min * 0.99, precios_max * 1.01)

            # Ajusta os rótulos do eixo X com o tempo
            passo = max(1, len(self.df)//10)
            indices_ticks = list(range(0, len(self.df), passo))
            self.ax.set_xticks(indices_ticks)
            self.ax.set_xticklabels(self.df['Tempo'].iloc[indices_ticks], 
                                    rotation=45, ha='right', color='white')

            # Legenda
            self.ax.legend(loc='upper left', fontsize=10, facecolor='gray')

            # ================= RSI em eixo secundário (apenas USD) =================
            if 'RSI_USD' in self.df.columns:
                ax2 = self.ax.twinx()
                ax2.set_ylim(0, 100)
                ax2.plot(x_values, self.df['RSI_USD'], color='yellow', label='RSI(14) USD')
                ax2.tick_params(axis='y', colors='yellow')
                ax2.set_ylabel('RSI (USD)', color='yellow')
                ax2.axhline(30, color='white', linestyle='--', linewidth=0.8)
                ax2.axhline(70, color='white', linestyle='--', linewidth=0.8)

            # ================= MACD em histograma (apenas USD) =================
            if 'MACD_USD' in self.df.columns and 'Signal_USD' in self.df.columns:
                # Exemplo: desenhar barras sobre o mesmo Axes principal
                macd_vals = self.df['MACD_USD']
                signal_vals = self.df['Signal_USD']
                for i, (macd, signal) in enumerate(zip(macd_vals, signal_vals)):
                    hist = macd - signal
                    if hist >= 0:
                        self.ax.bar(i, hist, color='magenta', width=0.8, bottom=signal)
                    else:
                        self.ax.bar(i, hist, color='red', width=0.8, bottom=signal)

            # ================= Habilitar "hover" com mplcursors =================
            # Precisamos recriar o cursor sempre que redesenhamos (ou podemos criar só uma vez).
            # Aqui, passamos como "targets" as 3 linhas.
            cursor = mplcursors.cursor([line_usd, line_brl, line_eur], hover=True)

            @cursor.connect("add")
            def on_add(sel):
                # sel.target é um (x, y) no sistema de coordenadas do gráfico
                xdata, ydata = sel.target
                # Precisamos converter xdata em índice aproximado para buscar no df
                idx = int(round(xdata))
                if idx >= 0 and idx < len(self.df):
                    # Checamos qual linha foi selecionada
                    linha_nome = sel.artist.get_label()  # 'USD', 'BRL' ou 'EUR'
                    # Formata mensagem
                    valor = self.df[linha_nome].iloc[idx]
                    tempo = self.df['Tempo'].iloc[idx]
                    sel.annotation.set_text(f"{linha_nome}\nTempo: {tempo}\nPreço: {valor:.2f}")
                    sel.annotation.set_backgroundcolor('gray')
                else:
                    sel.annotation.set_text("")

            # Desenha o canvas atualizado
            self.canvas.draw()

            # ================= Atualiza estatísticas (USD, BRL, EUR) =================
            self.atualizar_estatisticas()

            # Atualiza status
            self.label_status.config(
                text=(
                    f"Status: Monitorando... "
                    f"Último USD: ${preco_usd:.2f}  |  "
                    f"Último BRL: R${preco_brl:.2f}  |  "
                    f"Último EUR: €{preco_eur:.2f}"
                ),
                foreground="green"
            )

        except requests.exceptions.RequestException as e:
            self.label_status.config(text=f"Erro ao obter dados: {e}", foreground="red")

    # ============================== ESTATÍSTICAS ==============================
    def atualizar_estatisticas(self):
        """Atualiza as estatísticas (média, máx, mín) para cada moeda."""
        if self.df.empty:
            return

        # USD
        media_usd = self.df['USD'].mean()
        max_usd = self.df['USD'].max()
        min_usd = self.df['USD'].min()
        self.label_media_usd.config(text=f"Média (USD): {media_usd:.2f}")
        self.label_max_usd.config(text=f"Máx (USD): {max_usd:.2f}")
        self.label_min_usd.config(text=f"Mín (USD): {min_usd:.2f}")

        # BRL
        media_brl = self.df['BRL'].mean()
        max_brl = self.df['BRL'].max()
        min_brl = self.df['BRL'].min()
        self.label_media_brl.config(text=f"Média (BRL): {media_brl:.2f}")
        self.label_max_brl.config(text=f"Máx (BRL): {max_brl:.2f}")
        self.label_min_brl.config(text=f"Mín (BRL): {min_brl:.2f}")

        # EUR
        media_eur = self.df['EUR'].mean()
        max_eur = self.df['EUR'].max()
        min_eur = self.df['EUR'].min()
        self.label_media_eur.config(text=f"Média (EUR): {media_eur:.2f}")
        self.label_max_eur.config(text=f"Máx (EUR): {max_eur:.2f}")
        self.label_min_eur.config(text=f"Mín (EUR): {min_eur:.2f}")

    # ============================== CÁLCULOS DE INDICADORES ==============================
    def calcular_rsi(self, column='USD', periodo=14):
        """
        Cálculo simplificado de RSI (Relative Strength Index) para a coluna indicada.
        Salva no DataFrame como 'RSI_<column>'.
        """
        if len(self.df) < periodo:
            return  # dados insuficientes

        df = self.df.copy()
        df['Diff'] = df[column].diff()
        df['Gain'] = df['Diff'].clip(lower=0)
        df['Loss'] = -1 * df['Diff'].clip(upper=0)

        df['AvgGain'] = df['Gain'].rolling(window=periodo, min_periods=periodo).mean()
        df['AvgLoss'] = df['Loss'].rolling(window=periodo, min_periods=periodo).mean()

        # Evita divisão por zero
        df['RS'] = df['AvgGain'] / df['AvgLoss'].replace(0, np.nan)
        df['RSI'] = 100 - (100 / (1 + df['RS']))

        self.df[f'RSI_{column}'] = df['RSI']

    def calcular_macd(self, column='USD', span_short=12, span_long=26, span_signal=9):
        """
        Cálculo simplificado de MACD (Moving Average Convergence Divergence).
        Salva no DataFrame como 'MACD_<column>' e 'Signal_<column>'.
        """
        if len(self.df) < span_long:
            return  # dados insuficientes

        df = self.df.copy()
        df['EMA_short'] = df[column].ewm(span=span_short, adjust=False).mean()
        df['EMA_long'] = df[column].ewm(span=span_long, adjust=False).mean()
        df['MACD'] = df['EMA_short'] - df['EMA_long']
        df['Signal'] = df['MACD'].ewm(span=span_signal, adjust=False).mean()

        self.df[f'MACD_{column}'] = df['MACD']
        self.df[f'Signal_{column}'] = df['Signal']

    # ============================== GERAÇÃO DE RELATÓRIO ==============================
    def gerar_relatorio(self):
        """
        Gera um relatório em nova janela (com histograma e curva normal) do preço em USD
        e oferece opção de salvar em arquivo.
        """
        if self.df.empty:
            messagebox.showwarning("Aviso", "Nenhum dado para gerar relatório.")
            return

        # Janela para exibir o relatório
        janela_relatorio = Toplevel(self.raiz)
        janela_relatorio.title("Relatório de Preços (USD)")
        janela_relatorio.geometry("800x600")

        # Para o relatório, usaremos apenas a coluna USD como exemplo
        df_usd = self.df[['Tempo', 'USD']].copy()
        media = df_usd['USD'].mean()
        maximo = df_usd['USD'].max()
        minimo = df_usd['USD'].min()
        volatilidade = df_usd['USD'].std()
        qtd_pontos = len(df_usd)

        # ================= Criação do histograma + curva normal =================
        fig_rel = plt.Figure(figsize=(8, 5), dpi=100)
        ax_rel = fig_rel.add_subplot(111)
        ax_rel.set_title("Distribuição dos Preços em USD (Histograma + Normal)", fontsize=12)

        # Histograma (normalizado)
        n, bins, patches = ax_rel.hist(df_usd['USD'], bins=15, density=True, alpha=0.6, color='gray')

        # Curva normal (com base em média e desvio padrão)
        if not math.isnan(media) and not math.isnan(volatilidade) and volatilidade != 0:
            x = np.linspace(minimo, maximo, 100)
            y = (1 / (np.sqrt(2 * np.pi) * volatilidade)) * np.exp(-0.5 * ((x - media) / volatilidade)**2)
            ax_rel.plot(x, y, 'r--', linewidth=2)

        ax_rel.set_xlabel("Preço (USD)")
        ax_rel.set_ylabel("Frequência (normalizada)")

        canvas_rel = FigureCanvasTkAgg(fig_rel, master=janela_relatorio)
        canvas_rel.draw()
        canvas_rel.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Texto com estatísticas
        texto_relatorio = (
            f"Relatório de Preços do Bitcoin (USD)\n"
            f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Total de Pontos: {qtd_pontos}\n"
            f"Média (USD): {media:.2f}\n"
            f"Máximo (USD): {maximo:.2f}\n"
            f"Mínimo (USD): {minimo:.2f}\n"
            f"Volatilidade (Desvio Padrão): {volatilidade:.2f}\n\n"
            f"Operações de Compra/Venda (fictício):\n"
        )

        # Lista de compras e vendas
        for op in self.compras_vendas:
            texto_relatorio += (
                f" - {op['Tipo']} em {op['Tempo'].strftime('%Y-%m-%d %H:%M:%S')}"
                f" a ${op['Preço']:.2f}\n"
            )

        texto_relatorio += "\nDados Detalhados (USD):\n"
        texto_relatorio += df_usd.to_string(index=False)

        # Exibir texto em widget Text
        label_texto = tk.Text(janela_relatorio, wrap=tk.WORD)
        label_texto.insert(tk.END, texto_relatorio)
        label_texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Botão para salvar em arquivo
        def salvar_arquivo():
            caminho_arquivo = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivo de Texto", "*.txt")],
                title="Salvar Relatório"
            )
            if caminho_arquivo:
                try:
                    with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
                        arquivo.write(texto_relatorio)
                    messagebox.showinfo("Sucesso", f"Relatório salvo em: {caminho_arquivo}")
                except Exception as e:
                    messagebox.showerror("Erro", f"Não foi possível salvar o relatório: {e}")

        botao_salvar = ttk.Button(
            janela_relatorio, text="Salvar Relatório em Arquivo", command=salvar_arquivo
        )
        botao_salvar.pack(side=tk.BOTTOM, pady=10)


# ============================== EXECUÇÃO DO PROGRAMA ==============================

if __name__ == "__main__":
    raiz = tk.Tk()
    app = AplicacaoBitcoin(raiz)
    raiz.mainloop()
