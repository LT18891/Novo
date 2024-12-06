import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.constants import hbar
from scipy.sparse import diags
from scipy.sparse.linalg import eigs

# Configurar o backend do matplotlib
matplotlib.use("TkAgg")

class SchrödingerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador da Equação de Schrödinger")
        self.root.geometry("900x700")
        
        # Legenda do Autor na Parte Superior em Azul
        self.render_autor()
        
        # Renderizar a Equação de Schrödinger
        self.render_equacao()
        
        # Criar campos de entrada
        self.criar_campos()
        
        # Botão para executar a simulação
        self.botao_simular = ttk.Button(self.root, text="Simular", command=self.simular)
        self.botao_simular.pack(pady=10)
        
        # Área para plotagem dos resultados
        self.criar_area_plot()
        
    def render_autor(self):
        # Criar e configurar o label do autor
        self.label_autor_topo = ttk.Label(self.root, text="Autor: Luiz Tiago Wilcke", font=("Arial", 12), foreground="blue")
        self.label_autor_topo.pack(pady=5)
    
    def render_equacao(self):
        # Utilizar matplotlib para renderizar a equação
        fig, ax = plt.subplots(figsize=(8, 1))
        ax.text(0.5, 0.5, r"$i\hbar \frac{\partial \psi}{\partial t} = -\frac{\hbar^2}{2m} \frac{\partial^2 \psi}{\partial x^2} + V(x)\psi$", 
                horizontalalignment='center', verticalalignment='center', fontsize=20)
        ax.axis('off')
        self.canvas_eq = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas_eq.draw()
        self.canvas_eq.get_tk_widget().pack(pady=10)
    
    def criar_campos(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=10)
        
        # Massa
        ttk.Label(frame, text="Massa da Partícula (kg):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.entrada_massa = ttk.Entry(frame)
        self.entrada_massa.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_massa.insert(0, "9.10938356e-31")  # Massa do elétron
        
        # Constante de Planck reduzida (ħ)
        ttk.Label(frame, text="Constante de Planck Reduzida (ħ) (J·s):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.entrada_hbar = ttk.Entry(frame)
        self.entrada_hbar.grid(row=1, column=1, padx=5, pady=5)
        self.entrada_hbar.insert(0, str(hbar))
        
        # Potencial (V0)
        ttk.Label(frame, text="Altura do Potencial V0 (J):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        self.entrada_V0 = ttk.Entry(frame)
        self.entrada_V0.grid(row=2, column=1, padx=5, pady=5)
        self.entrada_V0.insert(0, "1e-18")
        
        # Largura do Potencial (a)
        ttk.Label(frame, text="Largura do Potencial (m):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        self.entrada_a = ttk.Entry(frame)
        self.entrada_a.grid(row=3, column=1, padx=5, pady=5)
        self.entrada_a.insert(0, "1e-10")
        
        # Número de Pontos
        ttk.Label(frame, text="Número de Pontos (N):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        self.entrada_N = ttk.Entry(frame)
        self.entrada_N.grid(row=4, column=1, padx=5, pady=5)
        self.entrada_N.insert(0, "1000")
        
        # Comprimento do Espaço (L)
        ttk.Label(frame, text="Comprimento do Espaço (m):").grid(row=5, column=0, padx=5, pady=5, sticky=tk.E)
        self.entrada_L = ttk.Entry(frame)
        self.entrada_L.grid(row=5, column=1, padx=5, pady=5)
        self.entrada_L.insert(0, "1e-8")
        
    def criar_area_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(8,5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)
    
    def simular(self):
        try:
            # Obter valores das entradas
            massa = float(self.entrada_massa.get())
            hbar_val = float(self.entrada_hbar.get())
            V0 = float(self.entrada_V0.get())
            a = float(self.entrada_a.get())
            N = int(self.entrada_N.get())
            L = float(self.entrada_L.get())
            
            # Definir o espaço
            x = np.linspace(-L/2, L/2, N)
            dx = x[1] - x[0]
            
            # Definir o potencial V(x)
            V = np.zeros(N)
            V[np.abs(x) <= a/2] = V0
            
            # Construir a matriz Hamiltoniana usando diferenças finitas
            diagonal = np.full(N, 2.0)
            off_diagonal = np.full(N-1, -1.0)
            laplacian = diags([off_diagonal, diagonal, off_diagonal], offsets=[-1,0,1]) / dx**2
            H = (-hbar_val**2 / (2 * massa)) * laplacian + diags(V)
            
            # Calcular os autovalores e autovetores
            num_autovalores = 4  # Número de estados a considerar
            eigvals, eigvecs = eigs(H, k=num_autovalores, which='SM')
            idx = eigvals.argsort()
            eigvals = eigvals[idx].real
            eigvecs = eigvecs[:,idx].real
            
            # Plotar os estados de energia
            self.ax.clear()
            for n in range(num_autovalores):
                self.ax.plot(x, eigvecs[:,n] + eigvals[n], label=f"Estado {n+1}")
            self.ax.plot(x, V, color='black', label="Potencial V(x)")
            self.ax.set_xlabel("x (m)")
            self.ax.set_ylabel("Energia (J)")
            self.ax.set_title("Autofunções e Autovalores")
            self.ax.legend()
            self.ax.grid(True)
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro durante a simulação:\n{e}")

def main():
    root = tk.Tk()
    app = SchrödingerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
