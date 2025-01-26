import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from scipy.integrate import odeint
import io

# Autor: Luiz Tiago Wilcke

class PlaceholderEntry(tk.Entry):
    """Classe para criar entradas com placeholder."""
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']
        self.has_placeholder = False
        
        self._mostrar_placeholder()
        
        self.bind("<FocusIn>", self.foco_entrando)
        self.bind("<FocusOut>", self.foco_saindo)

    def _mostrar_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color
        self.has_placeholder = True

    def foco_entrando(self, event):
        if self.has_placeholder:
            self.delete(0, tk.END)
            self['fg'] = self.default_fg_color
            self.has_placeholder = False

    def foco_saindo(self, event):
        if not self.get():
            self._mostrar_placeholder()

    def get_value(self):
        if self.has_placeholder:
            return None
        try:
            return float(self.get())
        except ValueError:
            return None

class ModeloAcao:
    def __init__(self, preco_inicial, taxa_crescimento, capacidade, perturbacao):
        self.preco_inicial = preco_inicial
        self.taxa_crescimento = taxa_crescimento
        self.capacidade = capacidade
        self.perturbacao = perturbacao

    def equacao_diferencial(self, preco, tempo):
        # Modelo de crescimento logístico com perturbação
        dpreco_dt = self.taxa_crescimento * preco * (1 - preco / self.capacidade) + self.perturbacao * np.sin(tempo)
        return dpreco_dt

    def prever_precos(self, tempo_total, pontos):
        tempo = np.linspace(0, tempo_total, pontos)
        preco = odeint(self.equacao_diferencial, self.preco_inicial, tempo)
        return tempo, preco.flatten()

class AplicacaoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Previsão de Preço de Ações")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        self.estilo = ttk.Style()
        self.estilo.theme_use('clam')  # Tema mais moderno

        self.criar_widgets()

    def criar_widgets(self):
        # Frame para parâmetros de entrada
        frame_entrada = ttk.Frame(self.root, padding="20")
        frame_entrada.pack(side=tk.TOP, fill=tk.X)

        # Título da seção
        ttk.Label(frame_entrada, text="Parâmetros do Modelo", font=("Helvetica", 16, "bold")).grid(column=0, row=0, columnspan=2, pady=10)

        # Preço Inicial
        ttk.Label(frame_entrada, text="Preço Inicial:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.entry_preco_inicial = PlaceholderEntry(frame_entrada, placeholder="Ex: 100.0")
        self.entry_preco_inicial.grid(column=1, row=1, pady=5, sticky=tk.EW)

        # Taxa de Crescimento
        ttk.Label(frame_entrada, text="Taxa de Crescimento (r):").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.entry_taxa_crescimento = PlaceholderEntry(frame_entrada, placeholder="Ex: 0.05")
        self.entry_taxa_crescimento.grid(column=1, row=2, pady=5, sticky=tk.EW)

        # Capacidade de Mercado
        ttk.Label(frame_entrada, text="Capacidade de Mercado (K):").grid(column=0, row=3, sticky=tk.W, pady=5)
        self.entry_capacidade = PlaceholderEntry(frame_entrada, placeholder="Ex: 1000.0")
        self.entry_capacidade.grid(column=1, row=3, pady=5, sticky=tk.EW)

        # Perturbação (Amplitude)
        ttk.Label(frame_entrada, text="Perturbação (A):").grid(column=0, row=4, sticky=tk.W, pady=5)
        self.entry_perturbacao = PlaceholderEntry(frame_entrada, placeholder="Ex: 50.0")
        self.entry_perturbacao.grid(column=1, row=4, pady=5, sticky=tk.EW)

        # Tempo Total
        ttk.Label(frame_entrada, text="Tempo Total:").grid(column=0, row=5, sticky=tk.W, pady=5)
        self.entry_tempo_total = PlaceholderEntry(frame_entrada, placeholder="Ex: 100.0")
        self.entry_tempo_total.grid(column=1, row=5, pady=5, sticky=tk.EW)

        # Pontos de Tempo
        ttk.Label(frame_entrada, text="Pontos de Tempo:").grid(column=0, row=6, sticky=tk.W, pady=5)
        self.entry_pontos = PlaceholderEntry(frame_entrada, placeholder="Ex: 1000")
        self.entry_pontos.grid(column=1, row=6, pady=5, sticky=tk.EW)

        # Configurar expansão das colunas
        frame_entrada.columnconfigure(1, weight=1)

        # Botão para executar a previsão
        self.botao_prever = ttk.Button(frame_entrada, text="Prever Preço das Ações", command=self.prever)
        self.botao_prever.grid(column=0, row=7, columnspan=2, pady=20)

        # Separator
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', pady=10)

        # Frame para exibir a fórmula
        frame_formula = ttk.Frame(self.root, padding="20")
        frame_formula.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        ttk.Label(frame_formula, text="Modelo de Equação Diferencial:", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Renderizar a fórmula usando matplotlib
        self.renderizar_formula(frame_formula)

        # Botão para mostrar a explicação
        self.botao_explicacao = ttk.Button(self.root, text="Explicação do Modelo", command=self.mostrar_explicacao)
        self.botao_explicacao.pack(pady=10)

    def renderizar_formula(self, parent):
        formula = r"$\frac{dP}{dt} = rP\left(1 - \frac{P}{K}\right) + A \sin(t)$"
        fig = plt.figure(figsize=(8, 1))
        fig.text(0.5, 0.5, formula, fontsize=20, ha='center', va='center')
        plt.axis('off')

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
        buf.seek(0)
        img = Image.open(buf)
        self.img_formula = ImageTk.PhotoImage(img)
        label_formula = ttk.Label(parent, image=self.img_formula)
        label_formula.pack()
        plt.close(fig)

    def mostrar_explicacao(self):
        explicacao = (
            "Modelo de Previsão de Preço de Ações:\n\n"
            "A equação diferencial utilizada é uma variação da equação logística, "
            "que modela o crescimento de uma população com capacidade de mercado limitada.\n\n"
            "Neste modelo:\n"
            "- P(t): Preço das ações no tempo t.\n"
            "- r: Taxa de crescimento intrínseca das ações.\n"
            "- K: Capacidade de mercado (limite superior do preço das ações).\n"
            "- A: Amplitude da perturbação.\n\n"
            "A perturbação representada pelo termo A*sin(t) modela oscilações periódicas no preço das ações, "
            "como flutuações de mercado ou eventos externos."
        )
        messagebox.showinfo("Explicação do Modelo", explicacao)

    def prever(self):
        try:
            # Obter valores das entradas
            preco_inicial = self.entry_preco_inicial.get_value()
            taxa_crescimento = self.entry_taxa_crescimento.get_value()
            capacidade = self.entry_capacidade.get_value()
            perturbacao = self.entry_perturbacao.get_value()
            tempo_total = self.entry_tempo_total.get_value()
            pontos = self.entry_pontos.get_value()

            # Atribuir valores padrão se None
            if preco_inicial is None:
                preco_inicial = 100.0
            if taxa_crescimento is None:
                taxa_crescimento = 0.05
            if capacidade is None:
                capacidade = 1000.0
            if perturbacao is None:
                perturbacao = 50.0
            if tempo_total is None:
                tempo_total = 100.0
            if pontos is None:
                pontos = 1000

            # Validar entradas
            if preco_inicial <= 0 or taxa_crescimento <= 0 or capacidade <= 0 or pontos <= 0:
                raise ValueError("Todos os valores devem ser positivos.")

            modelo = ModeloAcao(preco_inicial, taxa_crescimento, capacidade, perturbacao)
            tempo, preco = modelo.prever_precos(tempo_total, pontos)

            # Plotar o resultado
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(tempo, preco, label='Preço das Ações', color='blue')
            ax.set_xlabel('Tempo')
            ax.set_ylabel('Preço')
            ax.set_title('Previsão do Preço das Ações')
            ax.legend()
            ax.grid(True)

            # Estilizar o gráfico
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # Exibir a plotagem em uma nova janela
            plot_window = tk.Toplevel(self.root)
            plot_window.title("Resultado da Previsão")
            plot_window.geometry("800x600")
            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            plt.close(fig)

        except ValueError as ve:
            messagebox.showerror("Entrada Inválida", f"Por favor, insira valores válidos nos campos.\nErro: {ve}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado:\n{e}")

def main():
    root = tk.Tk()
    app = AplicacaoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
