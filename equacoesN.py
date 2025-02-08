import tkinter as tk
from tkinter import messagebox
import numpy as np
from cmath import sqrt

def formatar_numero(num, formato):
    """
    Formata um número (real ou complexo) de acordo com o formato escolhido:
    - "decimal": ponto fixo com 8 dígitos após a vírgula.
    - "cientifica": notação científica com 8 dígitos após a vírgula.
    """
    # Se o número for complexo, mas a parte imaginária for insignificante, mostra só a parte real.
    if isinstance(num, complex):
        if abs(num.imag) < 1e-10:
            num = num.real
        else:
            parte_real = num.real
            parte_imag = num.imag
            if formato == "decimal":
                return f"{parte_real:.8f} {'+' if parte_imag >= 0 else '-'} {abs(parte_imag):.8f}i"
            else:
                return f"{parte_real:.8e} {'+' if parte_imag >= 0 else '-'} {abs(parte_imag):.8e}i"
    # Se for número real:
    if formato == "decimal":
        return f"{num:.8f}"
    else:
        return f"{num:.8e}"

class CalculadoraEquacoes(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Resolução de Equações")
        self.geometry("600x650")
        
        # Variáveis de controle
        self.tipo_equacao = tk.StringVar(value="quadratica")  # "quadratica" ou "ngrau"
        self.formato = tk.StringVar(value="decimal")           # "decimal" ou "cientifica"
        
        self.criar_widgets()
    
    def criar_widgets(self):
        # --- Frame de Informações com as fórmulas e métodos ---
        frame_info = tk.LabelFrame(self, text="Informações e Métodos")
        frame_info.pack(fill="both", padx=10, pady=5)
        
        texto_info = (
            "Equação Quadrática:\n"
            "  Fórmula: ax² + bx + c = 0\n"
            "  Delta: Δ = b² - 4ac\n"
            "  Raízes: x = (-b ± √Δ) / (2a)\n\n"
            "Equação de Grau N:\n"
            "  Forma: aₙ xⁿ + aₙ₋₁ xⁿ⁻¹ + ... + a₁ x + a₀ = 0\n"
            "  Método: utiliza a função np.roots para encontrar as raízes."
        )
        lbl_info = tk.Label(frame_info, text=texto_info, justify="left", anchor="w")
        lbl_info.pack(fill="both", padx=5, pady=5)
        
        # --- Frame para escolher o tipo de equação ---
        frame_tipo = tk.LabelFrame(self, text="Tipo de Equação")
        frame_tipo.pack(fill="x", padx=10, pady=5)
        
        rb_quadratica = tk.Radiobutton(frame_tipo, text="Equação Quadrática", 
                                       variable=self.tipo_equacao, value="quadratica", 
                                       command=self.atualizar_entrada)
        rb_quadratica.pack(side="left", padx=5, pady=5)
        
        rb_ngrau = tk.Radiobutton(frame_tipo, text="Equação de Grau N", 
                                  variable=self.tipo_equacao, value="ngrau", 
                                  command=self.atualizar_entrada)
        rb_ngrau.pack(side="left", padx=5, pady=5)
        
        # --- Frame para escolher a formatação dos resultados ---
        frame_formato = tk.LabelFrame(self, text="Opções de Formatação")
        frame_formato.pack(fill="x", padx=10, pady=5)
        
        rb_decimal = tk.Radiobutton(frame_formato, text="Decimal", 
                                    variable=self.formato, value="decimal")
        rb_decimal.pack(side="left", padx=5, pady=5)
        
        rb_cientifica = tk.Radiobutton(frame_formato, text="Notação Científica", 
                                       variable=self.formato, value="cientifica")
        rb_cientifica.pack(side="left", padx=5, pady=5)
        
        # --- Frame para entrada dos coeficientes ---
        self.frame_entrada = tk.LabelFrame(self, text="Entrada dos Coeficientes")
        self.frame_entrada.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.atualizar_entrada()  # Inicializa os campos de entrada conforme o tipo selecionado.
        
        # --- Botão para realizar o cálculo ---
        btn_calcular = tk.Button(self, text="Calcular", command=self.calcular_equacao)
        btn_calcular.pack(pady=10)
        
        # --- Label para exibir os resultados ---
        self.label_resultado = tk.Label(self, text="Resultado:", anchor="w", justify="left")
        self.label_resultado.pack(fill="both", padx=10, pady=5)
    
    def atualizar_entrada(self):
        """
        Atualiza os campos de entrada de coeficientes conforme o tipo de equação escolhido.
        """
        # Limpa os widgets do frame de entrada
        for widget in self.frame_entrada.winfo_children():
            widget.destroy()
        
        if self.tipo_equacao.get() == "quadratica":
            # Entradas para os coeficientes a, b e c da equação ax² + bx + c = 0
            tk.Label(self.frame_entrada, text="Coeficiente a:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            self.entrada_a = tk.Entry(self.frame_entrada)
            self.entrada_a.grid(row=0, column=1, padx=5, pady=5)
            
            tk.Label(self.frame_entrada, text="Coeficiente b:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            self.entrada_b = tk.Entry(self.frame_entrada)
            self.entrada_b.grid(row=1, column=1, padx=5, pady=5)
            
            tk.Label(self.frame_entrada, text="Coeficiente c:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
            self.entrada_c = tk.Entry(self.frame_entrada)
            self.entrada_c.grid(row=2, column=1, padx=5, pady=5)
        else:
            # Entradas para equação de grau n:
            tk.Label(self.frame_entrada, text="Grau da equação (n):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            self.entrada_grau = tk.Entry(self.frame_entrada)
            self.entrada_grau.grid(row=0, column=1, padx=5, pady=5)
            
            tk.Label(self.frame_entrada, text="Coeficientes (separados por vírgula ou ';'):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            self.entrada_coef = tk.Entry(self.frame_entrada, width=40)
            self.entrada_coef.grid(row=1, column=1, padx=5, pady=5)
            
            exemplo = "Exemplo: para 2x³ + 0x² - 4x + 5, insira: 2, 0, -4, 5"
            tk.Label(self.frame_entrada, text=exemplo).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    
    def calcular_equacao(self):
        """
        Realiza o cálculo das raízes da equação de acordo com o modo selecionado e exibe o resultado.
        """
        try:
            if self.tipo_equacao.get() == "quadratica":
                # Leitura dos coeficientes (permitindo vírgula como separador decimal)
                a = float(self.entrada_a.get().replace(',', '.'))
                b = float(self.entrada_b.get().replace(',', '.'))
                c = float(self.entrada_c.get().replace(',', '.'))
                
                if a == 0:
                    messagebox.showerror("Erro", "O coeficiente 'a' não pode ser zero em uma equação quadrática.")
                    return
                
                delta = b**2 - 4*a*c
                raiz_delta = sqrt(delta)
                x1 = (-b + raiz_delta) / (2*a)
                x2 = (-b - raiz_delta) / (2*a)
                raizes = [x1, x2]
            else:
                # Equação de grau n:
                grau = int(self.entrada_grau.get())
                texto_coef = self.entrada_coef.get()
                # Permite separar os coeficientes por vírgula ou ponto e vírgula
                if ";" in texto_coef:
                    lista_coef = texto_coef.split(";")
                else:
                    lista_coef = texto_coef.split(",")
                
                lista_coef = [s.strip() for s in lista_coef if s.strip() != ""]
                coeficientes = []
                for s in lista_coef:
                    s_formatado = s.replace(',', '.')
                    coeficientes.append(float(s_formatado))
                
                if len(coeficientes) != grau + 1:
                    messagebox.showerror("Erro", "Número de coeficientes deve ser igual a (grau + 1).")
                    return
                
                # Utiliza a função do NumPy para encontrar as raízes
                raizes = np.roots(coeficientes)
            
            # Formata as raízes conforme a opção escolhida
            resultado_formatado = ""
            for i, raiz in enumerate(raizes, start=1):
                resultado_formatado += f"Raiz {i}: {formatar_numero(raiz, self.formato.get())}\n"
            
            self.label_resultado.config(text="Resultado:\n" + resultado_formatado)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular a equação:\n{e}")

if __name__ == "__main__":
    app = CalculadoraEquacoes()
    app.mainloop()
