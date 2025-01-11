import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib
from PIL import Image, ImageTk
import io
import pandas as pd

# Autor: Luiz Tiago Wilcke (versão adaptada com processo de saltos)

class ModeloDolarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modelo Estocástico Avançado para o Preço do Dólar")
        self.root.geometry("800x800")
        self.create_widgets()
        self.simulations = []

    def create_widgets(self):
        # Notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Aba de Simulação
        self.simulation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.simulation_tab, text='Simulação')

        # Aba de Resultados
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text='Resultados')

        # Aba de Gráficos
        self.plots_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.plots_tab, text='Gráficos')

        # ------------------- ABA DE SIMULAÇÃO -------------------
        # Frame para os coeficientes
        coef_frame = ttk.LabelFrame(self.simulation_tab, text="Coeficientes do Modelo")
        coef_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Valores padrão para coeficientes (incluindo novos parâmetros de salto)
        coef_defaults = {
            "α (Taxa de Juros):": "0.1",
            "β (Inflação):": "0.05",
            "γ (Constante):": "1.0",
            "δ (Reversão à Média):": "0.01",
            "θ (Amplitude de Choque):": "0.1",
            "ω (Frequência de Choque):": "0.05",
            "σ (Volatilidade):": "0.2",
            "κ (Exponente de Volatilidade):": "1.0",
            "λ (Taxa de Salto):": "0.02",
            "μ_j (Média do Log-Salto):": "0.0",
            "σ_j (Volatilidade do Log-Salto):": "0.1",
        }

        self.coef_entries = {}
        for idx, (label, default) in enumerate(coef_defaults.items()):
            ttk.Label(coef_frame, text=label).grid(row=idx, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(coef_frame)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            entry.insert(0, default)
            self.coef_entries[label] = entry

        # Frame para as variáveis de entrada
        var_frame = ttk.LabelFrame(self.simulation_tab, text="Variáveis de Entrada")
        var_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Valores padrão para variáveis de entrada
        var_defaults = {
            "Taxa de Juros (%):": "5.0",
            "Inflação (%):": "3.0",
            "Preço Inicial do Dólar (USD):": "5.0",
            "Período de Simulação (dias):": "365",
            "Número de Simulações:": "1000"
        }

        self.var_entries = {}
        for idx, (label, default) in enumerate(var_defaults.items()):
            ttk.Label(var_frame, text=label).grid(row=idx, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(var_frame)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            entry.insert(0, default)
            self.var_entries[label] = entry

        # Botões de Simulação
        buttons_frame = ttk.Frame(self.simulation_tab)
        buttons_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        sim_button = ttk.Button(buttons_frame, text="Simular Preço do Dólar", command=self.simular_preco)
        sim_button.grid(row=0, column=0, padx=5, pady=5)

        export_button = ttk.Button(buttons_frame, text="Exportar Resultados", command=self.exportar_resultados)
        export_button.grid(row=0, column=1, padx=5, pady=5)

        # Frame para exibir a equação
        eq_frame = ttk.LabelFrame(self.simulation_tab, text="Equação do Modelo")
        eq_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.eq_canvas = tk.Canvas(eq_frame, width=700, height=110)
        self.eq_canvas.pack(padx=5, pady=5)

        # ------------------- ABA DE RESULTADOS -------------------
        # (Inicialmente vazia, preenchida após a simulação)

        # ------------------- ABA DE GRÁFICOS -------------------
        # Botão para gerar o gráfico na aba de Gráficos
        plot_button = ttk.Button(self.plots_tab, text="Gerar Plot da Simulação", command=self.plot_simulacao)
        plot_button.pack(pady=10)

        # Janela de Resultados Numéricos (Toplevel separado, caso queira)
        self.results_window = None

    def simular_preco(self):
        try:
            # Obter coeficientes
            alpha = float(self.coef_entries["α (Taxa de Juros):"].get())
            beta = float(self.coef_entries["β (Inflação):"].get())
            gamma = float(self.coef_entries["γ (Constante):"].get())
            delta = float(self.coef_entries["δ (Reversão à Média):"].get())
            theta = float(self.coef_entries["θ (Amplitude de Choque):"].get())
            omega = float(self.coef_entries["ω (Frequência de Choque):"].get())
            sigma = float(self.coef_entries["σ (Volatilidade):"].get())
            kappa = float(self.coef_entries["κ (Exponente de Volatilidade):"].get())

            # Novos coeficientes para o processo de salto
            lambd = float(self.coef_entries["λ (Taxa de Salto):"].get())      # intensidade do Poisson
            mu_j  = float(self.coef_entries["μ_j (Média do Log-Salto):"].get())
            sigma_j = float(self.coef_entries["σ_j (Volatilidade do Log-Salto):"].get())

            # Obter variáveis de entrada
            juros = float(self.var_entries["Taxa de Juros (%):"].get())
            inflacao = float(self.var_entries["Inflação (%):"].get())
            S0 = float(self.var_entries["Preço Inicial do Dólar (USD):"].get())
            T = int(self.var_entries["Período de Simulação (dias):"].get())
            num_simulations = int(self.var_entries["Número de Simulações:"].get())

            # Tempo de simulação
            dt = 1  # passo de 1 dia
            N = T
            t = np.linspace(0, T, N+1)

            # Inicializar array para preços
            S = np.zeros((num_simulations, N+1))
            S[:, 0] = S0

            # Simulação utilizando o método de Euler-Maruyama + Jump-Diffusion
            for i in range(1, N+1):
                dW = np.random.normal(0, np.sqrt(dt), num_simulations)
                # Drift
                drift = ((alpha * juros) + (beta * inflacao) + gamma
                         - (delta * S[:, i-1]) + theta * np.sin(omega * t[i-1])) * S[:, i-1] * dt
                # Difusão
                diffusion = sigma * (S[:, i-1] ** kappa) * dW

                # Processo de salto (Poisson) - número de saltos em dt
                jump_counts = np.random.poisson(lam=lambd * dt, size=num_simulations)
                
                # Para cada simulação, se jump_counts > 0, gerar o(s) salto(s) e aplicar
                jump_factor = np.ones(num_simulations)  # fator multiplicativo devido aos saltos
                for sim_idx in range(num_simulations):
                    if jump_counts[sim_idx] > 0:
                        # Gerar 'jump_counts[sim_idx]' saltos (normal log)
                        # Para dt pequeno, tipicamente 0 ou 1 salto, mas permite mais
                        jumps = np.random.normal(mu_j, sigma_j, size=jump_counts[sim_idx])
                        # Cada salto multiplica S(t) por exp(jumps)
                        jump_factor[sim_idx] = np.prod(np.exp(jumps))

                # Atualiza o preço com drift + difusão + salto
                S[:, i] = S[:, i-1] + drift + diffusion
                S[:, i] *= jump_factor  # aplica o fator de salto (multiplicativo)

            self.t = t
            self.S = S

            # Salvar simulações para futuras análises
            self.simulations = S

            # Exibir resultado na aba de Resultados
            self.exibir_resultados()

            # Renderizar a equação em LaTeX (agora com o termo de salto incluído)
            eq_latex = (
                r"$\frac{dS(t)}{dt} = \bigl(\alpha \times \text{Taxa\_Juros} + \beta \times \text{Inflação} + \gamma - \delta \times S(t) + \theta \times \sin(\omega t)\bigr) S(t)"
                r"\;+\;\sigma\,S(t)^{\kappa}\,\frac{dW(t)}{dt}"
                r"\;+\; S(t)\,\bigl(e^J - 1\bigr)\,dN(t),"
                r"\text{ onde } J \sim \mathcal{N}(\mu_j,\sigma_j^2)\text{ e }N(t)\text{ é Poisson}(\lambda).$"
            )
            self.render_equation(" ".join(eq_latex))

            messagebox.showinfo("Simulação Concluída",
                                f"Simulação concluída para {num_simulations} caminhos de {T} dias (Jump-Diffusion).")

        except ValueError:
            messagebox.showerror("Entrada Inválida", "Por favor, insira valores numéricos válidos.")

    def render_equation(self, equation):
        # Renderiza a equação LaTeX usando matplotlib e exibe no Canvas
        fig = plt.figure(figsize=(8, 2))
        text = fig.text(0.5, 0.5, equation, fontsize=13, ha='center', va='center')

        # Remover eixos
        plt.axis('off')

        # Salvar a figura em um buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=200)
        buf.seek(0)
        img = Image.open(buf)

        # Converter para ImageTk
        img_tk = ImageTk.PhotoImage(img)

        # Limpar o canvas anterior
        self.eq_canvas.delete("all")

        # Adicionar a imagem ao canvas
        self.eq_canvas.create_image(350, 50, image=img_tk)
        self.eq_canvas.image = img_tk  # Manter a referência

        plt.close(fig)

    def exibir_resultados(self):
        # Fecha a janela anterior se existir
        if self.results_window and tk.Toplevel.winfo_exists(self.results_window):
            self.results_window.destroy()

        self.results_window = tk.Toplevel(self.root)
        self.results_window.title("Resultados Numéricos")
        self.results_window.geometry("600x400")

        # Calculando estatísticas
        mean = np.mean(self.S, axis=0)
        median = np.median(self.S, axis=0)
        std_dev = np.std(self.S, axis=0)
        max_val = np.max(self.S, axis=0)
        min_val = np.min(self.S, axis=0)

        # Criar DataFrame para exibir
        data = {
            "Dia": self.t,
            "Média": mean,
            "Mediana": median,
            "Desvio Padrão": std_dev,
            "Máximo": max_val,
            "Mínimo": min_val
        }
        df = pd.DataFrame(data)

        # Exibir no Treeview
        tree = ttk.Treeview(self.results_window, 
                            columns=("Dia", "Média", "Mediana", "Desvio Padrão", "Máximo", "Mínimo"), 
                            show='headings')
        tree.pack(expand=True, fill='both')

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor='center')

        # Inserir dados
        for _, row in df.iterrows():
            tree.insert("", "end", values=tuple(row))

        # Botão para fechar a janela
        close_button = ttk.Button(self.results_window, text="Fechar", command=self.results_window.destroy)
        close_button.pack(pady=5)

    def plot_simulacao(self):
        """Exibe o gráfico de algumas trajetórias da simulação diretamente na aba de Gráficos."""
        try:
            # Verifica se existe resultado de simulação
            if not self.simulations.any():
                messagebox.showerror("Simulação Não Realizada", "Por favor, realize uma simulação primeiro.")
                return

            # Limpa a aba de Gráficos antes de desenhar
            for widget in self.plots_tab.winfo_children():
                widget.destroy()

            # Recria o botão de gerar plot (opcional, caso queira manter na aba)
            plot_button = ttk.Button(self.plots_tab, text="Gerar Plot da Simulação", command=self.plot_simulacao)
            plot_button.pack(pady=10)

            # Frame que conterá o gráfico
            plot_frame = ttk.Frame(self.plots_tab)
            plot_frame.pack(expand=True, fill='both')

            # Criar figura
            fig, ax = plt.subplots(figsize=(8,6))

            # Plotar algumas simulações (limite de 10 para visualização)
            num_to_plot = min(10, self.simulations.shape[0])
            for i in range(num_to_plot):
                ax.plot(self.t, self.simulations[i], lw=0.8, alpha=0.7,
                        label=f'Simulação {i+1}' if i == 0 else None)

            # Plotar média
            mean = np.mean(self.simulations, axis=0)
            ax.plot(self.t, mean, color='black', linewidth=2, label='Média')

            ax.set_xlabel('Tempo (dias)')
            ax.set_ylabel('Preço do Dólar (USD)')
            ax.set_title('Simulações do Preço do Dólar - Jump-Diffusion')
            ax.legend()
            ax.grid(True)

            # Exibir a figura no Tkinter (na aba de Gráficos)
            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True, fill='both')

            # Botões adicionais para análises (histograma, distribuição)
            analysis_frame = ttk.Frame(self.plots_tab)
            analysis_frame.pack(pady=10)

            plot_hist_button = ttk.Button(analysis_frame, text="Histograma Final", command=self.plot_histograma)
            plot_hist_button.grid(row=0, column=0, padx=5)

            plot_distribution_button = ttk.Button(analysis_frame, text="Distribuição Final", command=self.plot_distribuicao)
            plot_distribution_button.grid(row=0, column=1, padx=5)

        except Exception as e:
            messagebox.showerror("Erro na Plotagem", f"Ocorreu um erro ao plotar a simulação:\n{e}")

    def plot_histograma(self):
        """Abre um Toplevel com o histograma dos preços finais."""
        try:
            # Criar uma nova janela para o histograma
            hist_window = tk.Toplevel(self.root)
            hist_window.title("Histograma dos Preços Finais")
            hist_window.geometry("600x400")

            # Preços finais
            finais = self.simulations[:, -1]

            fig, ax = plt.subplots(figsize=(6,4))
            ax.hist(finais, bins=30, color='skyblue', edgecolor='black')
            ax.set_xlabel('Preço do Dólar (USD)')
            ax.set_ylabel('Frequência')
            ax.set_title('Histograma dos Preços Finais')

            # Exibir a figura no Tkinter
            canvas = FigureCanvasTkAgg(fig, master=hist_window)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True, fill='both')

            # Botão para fechar
            close_button = ttk.Button(hist_window, text="Fechar", command=hist_window.destroy)
            close_button.pack(pady=5)

        except Exception as e:
            messagebox.showerror("Erro na Plotagem", f"Ocorreu um erro ao plotar o histograma:\n{e}")

    def plot_distribuicao(self):
        """Abre um Toplevel com o boxplot (distribuição) dos preços finais."""
        try:
            dist_window = tk.Toplevel(self.root)
            dist_window.title("Distribuição dos Preços Finais")
            dist_window.geometry("600x400")

            # Preços finais
            finais = self.simulations[:, -1]

            fig, ax = plt.subplots(figsize=(6,4))
            ax.boxplot(finais, vert=False)
            ax.set_xlabel('Preço do Dólar (USD)')
            ax.set_title('Distribuição dos Preços Finais')

            canvas = FigureCanvasTkAgg(fig, master=dist_window)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True, fill='both')

            close_button = ttk.Button(dist_window, text="Fechar", command=dist_window.destroy)
            close_button.pack(pady=5)

        except Exception as e:
            messagebox.showerror("Erro na Plotagem", f"Ocorreu um erro ao plotar a distribuição:\n{e}")

    def exportar_resultados(self):
        try:
            if not self.simulations.any():
                messagebox.showerror("Simulação Não Realizada", "Por favor, realize uma simulação primeiro.")
                return

            # Selecionar o local para salvar
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Salvar Resultados"
            )

            if file_path:
                # Criar DataFrame com as simulações
                df = pd.DataFrame(self.simulations, columns=[f'Dia {int(day)}' for day in self.t])
                df.insert(0, 'Simulação', [f'Simulação {i+1}' for i in range(self.simulations.shape[0])])

                # Salvar em CSV
                df.to_csv(file_path, index=False)
                messagebox.showinfo("Exportação Concluída",
                                    f"Resultados exportados com sucesso para {file_path}")

        except Exception as e:
            messagebox.showerror("Erro na Exportação", f"Ocorreu um erro ao exportar os resultados:\n{e}")

def main():
    root = tk.Tk()
    app = ModeloDolarApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

