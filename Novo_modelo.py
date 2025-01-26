import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import io

# Autor: Luiz Tiago Wilcke

class PlaceholderEntry(tk.Entry):
    """Classe para criar entradas com placeholder."""
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']
        
        self.bind("<FocusIn>", self.foco_entrando)
        self.bind("<FocusOut>", self.foco_saindo)
        
        self._mostrar_placeholder()

    def _mostrar_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foco_entrando(self, event):
        if self['fg'] == self.placeholder_color:
            self.delete(0, tk.END)
            self['fg'] = self.default_fg_color

    def foco_saindo(self, event):
        if not self.get():
            self._mostrar_placeholder()

class ModeloAcaoSDE:
    def __init__(self, preco_inicial, taxa_crescimento, capacidade, volatilidade, tempo_total, pontos):
        self.preco_inicial = preco_inicial
        self.taxa_crescimento = taxa_crescimento
        self.capacidade = capacidade
        self.volatilidade = volatilidade
        self.tempo_total = tempo_total
        self.pontos = pontos

    def prever_precos(self):
        dt = self.tempo_total / self.pontos
        tempo = np.linspace(0, self.tempo_total, self.pontos)
        preco = np.zeros(self.pontos)
        preco[0] = self.preco_inicial

        for i in range(1, self.pontos):
            P = preco[i-1]
            dP_det = self.taxa_crescimento * P * (1 - P / self.capacidade) * dt
            dP_stoc = self.volatilidade * P * np.sqrt(dt) * np.random.normal()
            preco[i] = P + dP_det + dP_stoc

        return tempo, preco

class AplicacaoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Previsão de Preço de Ações (SDE)")
        self.root.geometry("900x800")
        self.root.resizable(False, False)
        self.estilo = ttk.Style()
        self.estilo.theme_use('default')  # Usar tema padrão para compatibilidade

        self.criar_widgets()

    def criar_widgets(self):
        # Frame para parâmetros de entrada
        frame_entrada = ttk.Frame(self.root, padding="20")
        frame_entrada.pack(side=tk.TOP, fill=tk.X)

        # Título da seção
        ttk.Label(frame_entrada, text="Parâmetros do Modelo (SDE)", font=("Helvetica", 16, "bold")).grid(column=0, row=0, columnspan=2, pady=10)

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

        # Volatilidade (σ)
        ttk.Label(frame_entrada, text="Volatilidade (σ):").grid(column=0, row=4, sticky=tk.W, pady=5)
        self.entry_volatilidade = PlaceholderEntry(frame_entrada, placeholder="Ex: 0.1")
        self.entry_volatilidade.grid(column=1, row=4, pady=5, sticky=tk.EW)

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
        self.botao_prever = ttk.Button(frame_entrada, text="Prever Preço das Ações (SDE)", command=self.prever)
        self.botao_prever.grid(column=0, row=7, columnspan=2, pady=20)

        # Separator
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x', pady=10)

        # Frame para exibir a fórmula
        frame_formula = ttk.Frame(self.root, padding="20")
        frame_formula.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        ttk.Label(frame_formula, text="Modelo de Equação Diferencial Estocástica:", font=("Helvetica", 16, "bold")).pack(pady=10)

        # Renderizar a fórmula usando matplotlib
        self.renderizar_formula(frame_formula)

        # Botão para mostrar a explicação
        self.botao_explicacao = ttk.Button(self.root, text="Explicação do Modelo", command=self.mostrar_explicacao)
        self.botao_explicacao.pack(pady=10)

        # Legenda do Autor
        ttk.Label(self.root, text="Autor: Luiz Tiago Wilcke", font=("Helvetica", 10, "italic")).pack(side=tk.BOTTOM, pady=10)

    def renderizar_formula(self, parent):
        formula = r"$dP = rP\left(1 - \frac{P}{K}\right)dt + \sigma P dW_t$"
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
            "Modelo de Previsão de Preço de Ações (Equação Diferencial Estocástica):\n\n"
            "A equação diferencial estocástica utilizada é uma variação da equação logística, "
            "que incorpora a aleatoriedade do mercado através de um termo de difusão.\n\n"
            "Neste modelo:\n"
            "- P(t): Preço das ações no tempo t.\n"
            "- r: Taxa de crescimento intrínseca das ações.\n"
            "- K: Capacidade de mercado (limite superior do preço das ações).\n"
            "- σ: Volatilidade das ações.\n"
            "- dW_t: Incremento de um processo de Wiener (movimento browniano).\n\n"
            "O termo de difusão σP dW_t modela a volatilidade dos preços das ações, representando as flutuações "
            "aleatórias que ocorrem devido a fatores internos e externos ao mercado."
        )
        messagebox.showinfo("Explicação do Modelo", explicacao)

    def prever(self):
        try:
            # Obter valores das entradas
            preco_inicial_str = self.entry_preco_inicial.get()
            taxa_crescimento_str = self.entry_taxa_crescimento.get()
            capacidade_str = self.entry_capacidade.get()
            volatilidade_str = self.entry_volatilidade.get()
            tempo_total_str = self.entry_tempo_total.get()
            pontos_str = self.entry_pontos.get()

            # Remover placeholders se presentes
            preco_inicial = float(preco_inicial_str) if preco_inicial_str and preco_inicial_str != self.entry_preco_inicial.placeholder else 100.0
            taxa_crescimento = float(taxa_crescimento_str) if taxa_crescimento_str and taxa_crescimento_str != self.entry_taxa_crescimento.placeholder else 0.05
            capacidade = float(capacidade_str) if capacidade_str and capacidade_str != self.entry_capacidade.placeholder else 1000.0
            volatilidade = float(volatilidade_str) if volatilidade_str and volatilidade_str != self.entry_volatilidade.placeholder else 0.1
            tempo_total = float(tempo_total_str) if tempo_total_str and tempo_total_str != self.entry_tempo_total.placeholder else 100.0
            pontos = int(pontos_str) if pontos_str and pontos_str != self.entry_pontos.placeholder else 1000

            # Validar entradas
            if preco_inicial <= 0 or taxa_crescimento <= 0 or capacidade <= 0 or volatilidade < 0 or pontos <= 0:
                raise ValueError

            modelo = ModeloAcaoSDE(preco_inicial, taxa_crescimento, capacidade, volatilidade, tempo_total, pontos)
            tempo, preco = modelo.prever_precos()

            # Plotar o resultado
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(tempo, preco, label='Preço das Ações (SDE)', color='green')
            ax.set_xlabel('Tempo')
            ax.set_ylabel('Preço')
            ax.set_title('Previsão do Preço das Ações (Equação Diferencial Estocástica)')
            ax.legend()
            ax.grid(True)

            # Estilizar o gráfico
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            # Exibir a plotagem em uma nova janela
            plot_window = tk.Toplevel(self.root)
            plot_window.title("Resultado da Previsão (SDE)")
            plot_window.geometry("800x600")
            canvas = FigureCanvasTkAgg(fig, master=plot_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            plt.close(fig)

        except ValueError:
            messagebox.showerror("Entrada Inválida", "Por favor, insira valores válidos nos campos. Certifique-se de que os números sejam positivos e que os campos estejam preenchidos corretamente.")

def main():
    root = tk.Tk()
    app = AplicacaoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
