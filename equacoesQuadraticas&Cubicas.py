import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import cmath

# Função para resolver equação quadrática
def resolver_equacao_quadratica(a, b, c):
    discriminante = b**2 - 4*a*c
    raiz1 = (-b + cmath.sqrt(discriminante)) / (2*a)
    raiz2 = (-b - cmath.sqrt(discriminante)) / (2*a)
    return discriminante, raiz1, raiz2

# Função para resolver equação cúbica
def resolver_equacao_cubica(a, b, c, d):
    # Normaliza os coeficientes
    a0 = b / a
    a1 = c / a
    a2 = d / a

    # Fórmula de Cardano para resolver equações cúbicas
    p = a1 - a0**2 / 3
    q = (2 * a0**3) / 27 - (a0 * a1) / 3 + a2

    discriminante = (q / 2)**2 + (p / 3)**3

    if discriminante > 0:
        u = cmath.sqrt(q / 2 + discriminante)
        v = cmath.sqrt(q / 2 - discriminante)
        raiz1 = u + v - a0 / 3
        raiz2 = -(u + v) / 2 - a0 / 3 + (u - v) * cmath.sqrt(3) * 1j / 2
        raiz3 = -(u + v) / 2 - a0 / 3 - (u - v) * cmath.sqrt(3) * 1j / 2
    elif discriminante == 0:
        u = cmath.sqrt(q / 2)
        raiz1 = u + u - a0 / 3
        raiz2 = -u - u / 2 - a0 / 3
        raiz3 = raiz2
    else:
        r = cmath.sqrt(-(p**3) / 27)
        phi = cmath.acos(-q / (2 * r))
        raiz1 = 2 * cmath.pow(r, 1/3) * cmath.cos(phi / 3) - a0 / 3
        raiz2 = 2 * cmath.pow(r, 1/3) * cmath.cos((phi + 2*cmath.pi) / 3) - a0 / 3
        raiz3 = 2 * cmath.pow(r, 1/3) * cmath.cos((phi + 4*cmath.pi) / 3) - a0 / 3

    return discriminante, raiz1, raiz2, raiz3

# Função para lidar com a resolução
def resolver():
    tipo = tipo_equacao.get()
    resultado_texto.delete(1.0, tk.END)  # Limpa o texto anterior

    try:
        if tipo == "Quadrática":
            a = float(entry_a.get())
            b = float(entry_b.get())
            c = float(entry_c.get())

            if a == 0:
                messagebox.showerror("Erro", "O coeficiente 'a' não pode ser zero em uma equação quadrática.")
                return

            delta, raiz1, raiz2 = resolver_equacao_quadratica(a, b, c)

            resultado = f"Discriminante (Δ): {delta}\n"
            if delta > 0:
                resultado += f"Duplas raízes reais:\nRaiz 1: {raiz1.real}\nRaiz 2: {raiz2.real}"
            elif delta == 0:
                resultado += f"Duas raízes reais e iguais:\nRaiz 1 = Raiz 2: {raiz1.real}"
            else:
                resultado += f"Raízes complexas:\nRaiz 1: {raiz1}\nRaiz 2: {raiz2}"

        elif tipo == "Cúbica":
            a = float(entry_a.get())
            b = float(entry_b.get())
            c = float(entry_c.get())
            d = float(entry_d.get())

            if a == 0:
                messagebox.showerror("Erro", "O coeficiente 'a' não pode ser zero em uma equação cúbica.")
                return

            delta, raiz1, raiz2, raiz3 = resolver_equacao_cubica(a, b, c, d)

            resultado = f"Discriminante: {delta}\n"
            resultado += f"Raiz 1: {raiz1}\nRaiz 2: {raiz2}\nRaiz 3: {raiz3}"

        resultado_texto.insert(tk.END, resultado)

    except ValueError:
        messagebox.showerror("Erro de Entrada", "Por favor, insira valores numéricos válidos para os coeficientes.")

# Função para limpar os campos
def limpar():
    entry_a.delete(0, tk.END)
    entry_b.delete(0, tk.END)
    entry_c.delete(0, tk.END)
    entry_d.delete(0, tk.END)
    resultado_texto.delete(1.0, tk.END)

# Configuração da Interface Gráfica
root = tk.Tk()
root.title("Resolutor de Equações")
root.geometry("500x500")
root.resizable(False, False)

# Seleção do tipo de equação
tipo_equacao = tk.StringVar(value="Quadrática")

frame_tipo = ttk.LabelFrame(root, text="Tipo de Equação")
frame_tipo.pack(padx=10, pady=10, fill="x")

radio_quadratica = ttk.Radiobutton(frame_tipo, text="Quadrática (ax² + bx + c = 0)", variable=tipo_equacao, value="Quadrática")
radio_quadratica.pack(anchor="w", padx=10, pady=5)

radio_cubica = ttk.Radiobutton(frame_tipo, text="Cúbica (ax³ + bx² + cx + d = 0)", variable=tipo_equacao, value="Cúbica")
radio_cubica.pack(anchor="w", padx=10, pady=5)

# Campos para coeficientes
frame_coeficientes = ttk.LabelFrame(root, text="Coeficientes")
frame_coeficientes.pack(padx=10, pady=10, fill="both", expand=True)

# Coeficiente a
label_a = ttk.Label(frame_coeficientes, text="a:")
label_a.grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_a = ttk.Entry(frame_coeficientes)
entry_a.grid(row=0, column=1, padx=10, pady=5, sticky="w")

# Coeficiente b
label_b = ttk.Label(frame_coeficientes, text="b:")
label_b.grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_b = ttk.Entry(frame_coeficientes)
entry_b.grid(row=1, column=1, padx=10, pady=5, sticky="w")

# Coeficiente c
label_c = ttk.Label(frame_coeficientes, text="c:")
label_c.grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_c = ttk.Entry(frame_coeficientes)
entry_c.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Coeficiente d (apenas para cúbica)
label_d = ttk.Label(frame_coeficientes, text="d:")
label_d.grid(row=3, column=0, padx=10, pady=5, sticky="e")
entry_d = ttk.Entry(frame_coeficientes)
entry_d.grid(row=3, column=1, padx=10, pady=5, sticky="w")

# Função para mostrar ou esconder o campo d
def atualizar_campos(*args):
    tipo = tipo_equacao.get()
    if tipo == "Quadrática":
        label_d.grid_remove()
        entry_d.grid_remove()
    else:
        label_d.grid()
        entry_d.grid()

tipo_equacao.trace("w", atualizar_campos)
atualizar_campos()

# Botões de ação
frame_botoes = ttk.Frame(root)
frame_botoes.pack(padx=10, pady=10)

botao_resolver = ttk.Button(frame_botoes, text="Resolver", command=resolver)
botao_resolver.pack(side="left", padx=10)

botao_limpar = ttk.Button(frame_botoes, text="Limpar", command=limpar)
botao_limpar.pack(side="left", padx=10)

# Área para exibir resultados
frame_resultado = ttk.LabelFrame(root, text="Resultado")
frame_resultado.pack(padx=10, pady=10, fill="both", expand=True)

resultado_texto = tk.Text(frame_resultado, height=10, wrap="word")
resultado_texto.pack(padx=10, pady=10, fill="both", expand=True)

# Iniciar a interface
root.mainloop()
