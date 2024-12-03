import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
import threading

# -------------------------------
# Função para executar a simulação
# -------------------------------
def executar_simulacao():
    try:
        # Desativar o botão de execução durante a simulação
        botao_simular.config(state=tk.DISABLED)
        # Obter valores de entrada
        N = int(entry_pontos_malha.get())
        L = float(entry_comprimento.get())
        num_camadas = int(entry_num_camadas.get())

        camadas = []
        for i in range(num_camadas):
            camada = {}
            camada['inicio'] = float(camadas_entries[i]['inicio'].get())
            camada['fim'] = float(camadas_entries[i]['fim'].get())
            camada['V'] = float(camadas_entries[i]['V'].get())
            camada['m'] = float(camadas_entries[i]['m'].get())
            camadas.append(camada)

        dopagem = float(entry_dopagem.get())
        tolerancia = float(entry_tolerancia.get())
        max_iteracoes = int(entry_max_iter.get())

        # Realizar a simulação em uma thread separada para não congelar a GUI
        thread = threading.Thread(target=simulacao, args=(N, L, num_camadas, camadas, dopagem, tolerancia, max_iteracoes))
        thread.start()

    except ValueError as ve:
        messagebox.showerror("Erro de Entrada", f"Por favor, insira valores válidos.\nDetalhes: {ve}")
        botao_simular.config(state=tk.NORMAL)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")
        botao_simular.config(state=tk.NORMAL)

def simulacao(N, L, num_camadas, camadas, dopagem, tolerancia, max_iteracoes):
    try:
        # Atualizar barra de progresso
        progresso['value'] = 0
        root.update_idletasks()

        # Constantes físicas
        hbar = 1.0545718e-34        # Constante de Planck reduzida (J.s)
        q = 1.60217662e-19          # Carga elementar (C)
        epsilon_0 = 8.854187817e-12  # Permissividade do vácuo (F/m)

        # Discretização do espaço
        dx = L / (N - 1)
        x = np.linspace(0, L, N)

        # Inicialização dos vetores de potencial de banda e massa efetiva
        V_banda = np.zeros(N)  # Potencial de banda inicial
        m_star = np.zeros(N)   # Massa efetiva inicial

        # Definição das camadas
        for camada in camadas:
            inicio = camada['inicio']
            fim = camada['fim']
            V = camada['V'] * q  # Converter eV para Joules
            m = camada['m'] * 9.10938356e-31  # Converter unidades para kg
            indices = np.where((x >= inicio) & (x < fim))[0]
            V_banda[indices] = V
            m_star[indices] = m

        # Caso alguma posição não tenha sido definida em alguma camada
        m_star[m_star == 0] = 0.067 * 9.10938356e-31  # Valor padrão (por exemplo, GaAs)

        # Definir dopagem
        N_D = np.ones(N) * dopagem
        N_A = np.zeros(N)  # Assumindo sem dopantes aceitadores

        # Inicialização do potencial
        V_potencial = V_banda.copy()

        # Parâmetros de iteração
        convergiu = False
        for iteracao in range(max_iteracoes):
            # Atualizar barra de progresso
            progresso['value'] = (iteracao / max_iteracoes) * 100
            root.update_idletasks()

            # Construção do Hamiltoniano
            # Calcula a diagonal principal
            diagonal = (hbar**2) / (m_star * dx**2) + V_potencial  # Tamanho: (N,)

            # Correção: Calcula as diagonais secundárias usando a média das massas efetivas entre pontos adjacentes
            m_star_off_diag = (m_star[:-1] + m_star[1:]) / 2  # Tamanho: (N-1,)
            off_diagonal = - (hbar**2) / (2 * m_star_off_diag * dx**2)  # Tamanho: (N-1,)

            # Construção do Hamiltoniano usando diagonais de tamanhos compatíveis
            H = diags([off_diagonal, diagonal, off_diagonal], offsets=[-1, 0, 1]).tocsc()

            # Resolução de autovalores e autovetores (os menores valores de E)
            num_estados = 10  # Número de estados a considerar
            E, psi = eigsh(H, k=num_estados, which='SA')

            # Normalização das funções de onda
            for i in range(num_estados):
                norm = np.sqrt(np.sum(np.abs(psi[:, i])**2) * dx)
                psi[:, i] /= norm

            # Cálculo da densidade de carga
            rho = np.zeros(N)
            for i in range(num_estados):
                rho += q * np.abs(psi[:, i])**2  # Carga dos elétrons

            # Adicionar dopagem
            rho += q * (N_D - N_A)

            # Resolução da Equação de Poisson
            poisson_diag = -2 / dx**2 * np.ones(N)
            poisson_off = 1 / dx**2 * np.ones(N - 1)
            A = diags([poisson_off, poisson_diag, poisson_off], offsets=[-1, 0, 1]).tocsc()

            # Vetor de carga
            b = -rho / epsilon_0

            # Condições de contorno (V=0 nas fronteiras)
            A = A[1:-1, 1:-1]
            b = b[1:-1]

            # Resolução para V interior
            V_interior = np.linalg.solve(A.toarray(), b)

            # Atualizar o potencial
            V_novo = np.zeros(N)
            V_novo[1:-1] = V_interior
            V_novo[0] = 0.0  # Condição de contorno
            V_novo[-1] = 0.0  # Condição de contorno

            # Verificar convergência
            delta_V = np.max(np.abs(V_novo - V_potencial))
            print(f'Iteração {iteracao + 1}: ΔV = {delta_V:.5e} J')
            if delta_V < tolerancia:
                convergiu = True
                print('Convergência atingida.')
                break
            V_potencial = V_novo.copy()

        # Atualizar barra de progresso para 100%
        progresso['value'] = 100
        root.update_idletasks()

        if not convergiu:
            messagebox.showwarning("Aviso", "Máximo de iterações alcançado sem convergência.")

        # Conversão de Energia para eV
        E_eV = E / q
        V_potencial_eV = V_potencial / q
        V_banda_eV = V_banda / q

        # Plotagem dos Resultados
        plt.figure(figsize=(12, 6))

        # Plot do potencial elétrico
        plt.subplot(1, 2, 1)
        plt.plot(x, V_potencial_eV, label='Potencial Elétrico')
        plt.plot(x, V_banda_eV, label='Potencial de Banda', linestyle='--')
        plt.xlabel('Posição (m)')
        plt.ylabel('Energia (eV)')
        plt.title('Distribuição do Potencial na Célula Fotovoltaica')
        plt.legend()
        plt.grid(True)

        # Plot das funções de onda dos primeiros estados
        plt.subplot(1, 2, 2)
        for i in range(num_estados):
            plt.plot(x, np.abs(psi[:, i])**2 + E_eV[i], label=f'Estado {i + 1} (E={E_eV[i]:.2f} eV)')
        plt.xlabel('Posição (m)')
        plt.ylabel('Densidade de Probabilidade + Energia (eV)')
        plt.title('Funções de Onda dos Estados Eletrônicos')
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.show()

        # Interpretação dos Resultados
        interpretacao = (
            "\nInterpretação dos Resultados:\n"
            "1. O gráfico do potencial elétrico mostra a distribuição do potencial ao longo da célula fotovoltaica, incluindo o potencial de banda definido para cada camada.\n"
            "2. As funções de onda dos estados eletrônicos indicam as regiões onde os elétrons estão mais provavelmente localizados. Estados com energias mais baixas estão mais próximos do fundo do potencial.\n"
            "3. A convergência do potencial indica que o equilíbrio entre a distribuição de carga e o potencial elétrico foi alcançado, refletindo uma distribuição estável de portadores de carga na célula fotovoltaica.\n"
            "4. A diferença entre o potencial elétrico e o potencial de banda pode fornecer informações sobre a formação de regiões de depleção e acumulação de carga nas interfaces das camadas.\n"
        )

        # Exibir a interpretação em uma janela de mensagem
        messagebox.showinfo("Interpretação dos Resultados", interpretacao)

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro durante a simulação: {e}")
    finally:
        # Reativar o botão de simulação
        botao_simular.config(state=tk.NORMAL)
        # Resetar a barra de progresso
        progresso['value'] = 0
        root.update_idletasks()

# -------------------------------
# Interface Gráfica com Tkinter
# -------------------------------
root = tk.Tk()
root.title("Simulador Schrödinger-Poisson para Célula Fotovoltaica")

# Definir o tamanho mínimo da janela
root.minsize(600, 600)

# Scrollbar para camadas se houver muitas
canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Parâmetros Gerais
frame_geral = ttk.LabelFrame(scrollable_frame, text="Parâmetros Gerais")
frame_geral.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

ttk.Label(frame_geral, text="Número de pontos de malha (N):").grid(row=0, column=0, sticky="w", pady=2)
entry_pontos_malha = ttk.Entry(frame_geral)
entry_pontos_malha.insert(0, "1000")
entry_pontos_malha.grid(row=0, column=1, pady=2)

ttk.Label(frame_geral, text="Comprimento total da célula (m):").grid(row=1, column=0, sticky="w", pady=2)
entry_comprimento = ttk.Entry(frame_geral)
entry_comprimento.insert(0, "1e-6")
entry_comprimento.grid(row=1, column=1, pady=2)

ttk.Label(frame_geral, text="Número de camadas:").grid(row=2, column=0, sticky="w", pady=2)
entry_num_camadas = ttk.Entry(frame_geral)
entry_num_camadas.insert(0, "2")
entry_num_camadas.grid(row=2, column=1, pady=2)

# Frame para camadas
frame_camadas = ttk.LabelFrame(scrollable_frame, text="Propriedades das Camadas")
frame_camadas.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

def atualizar_camadas():
    # Limpar camadas anteriores
    for widget in frame_camadas.winfo_children():
        widget.destroy()
    try:
        num_camadas = int(entry_num_camadas.get())
    except:
        num_camadas = 1

    camadas_entries.clear()
    try:
        L = float(entry_comprimento.get())
        N = int(entry_pontos_malha.get())
    except:
        L = 1e-6
        N = 1000

    layer_width = L / num_camadas

    for i in range(num_camadas):
        sub_frame = ttk.LabelFrame(frame_camadas, text=f"Camada {i + 1}")
        sub_frame.grid(row=i, column=0, padx=5, pady=5, sticky="ew")

        ttk.Label(sub_frame, text="Posição inicial (m):").grid(row=0, column=0, sticky="w", pady=2)
        inicio = ttk.Entry(sub_frame)
        inicio_valor = i * layer_width
        inicio.insert(0, f"{inicio_valor:.2e}")
        inicio.grid(row=0, column=1, pady=2)

        ttk.Label(sub_frame, text="Posição final (m):").grid(row=1, column=0, sticky="w", pady=2)
        fim = ttk.Entry(sub_frame)
        fim_valor = (i + 1) * layer_width
        fim.insert(0, f"{fim_valor:.2e}")
        fim.grid(row=1, column=1, pady=2)

        ttk.Label(sub_frame, text="Potencial de banda (eV):").grid(row=2, column=0, sticky="w", pady=2)
        V = ttk.Entry(sub_frame)
        V_default = "1.0" if i % 2 == 0 else "0.0"
        V.insert(0, V_default)
        V.grid(row=2, column=1, pady=2)

        ttk.Label(sub_frame, text="Massa efetiva (m0):").grid(row=3, column=0, sticky="w", pady=2)
        m = ttk.Entry(sub_frame)
        m.insert(0, "0.067")
        m.grid(row=3, column=1, pady=2)

        camadas_entries.append({'inicio': inicio, 'fim': fim, 'V': V, 'm': m})

# Inicializar camadas
camadas_entries = []
atualizar_camadas()

# Botão para atualizar camadas
botao_atualizar = ttk.Button(frame_camadas, text="Atualizar Camadas", command=atualizar_camadas)
botao_atualizar.grid(row=0, column=0, columnspan=2, pady=5)

# Parâmetros de Dopagem e Iteração
frame_dopagem = ttk.LabelFrame(scrollable_frame, text="Dopagem e Iteração")
frame_dopagem.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

ttk.Label(frame_dopagem, text="Concentração de dopantes doadores (N_D) [m⁻³]:").grid(row=0, column=0, sticky="w", pady=2)
entry_dopagem = ttk.Entry(frame_dopagem)
entry_dopagem.insert(0, "1e24")
entry_dopagem.grid(row=0, column=1, pady=2)

ttk.Label(frame_dopagem, text="Tolerância para convergência:").grid(row=1, column=0, sticky="w", pady=2)
entry_tolerancia = ttk.Entry(frame_dopagem)
entry_tolerancia.insert(0, "1e-5")
entry_tolerancia.grid(row=1, column=1, pady=2)

ttk.Label(frame_dopagem, text="Número máximo de iterações:").grid(row=2, column=0, sticky="w", pady=2)
entry_max_iter = ttk.Entry(frame_dopagem)
entry_max_iter.insert(0, "100")
entry_max_iter.grid(row=2, column=1, pady=2)

# Barra de Progresso
frame_progresso = ttk.Frame(scrollable_frame)
frame_progresso.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

progresso = ttk.Progressbar(frame_progresso, orient="horizontal", length=400, mode="determinate")
progresso.pack(pady=5)

# Botão de Simulação
botao_simular = ttk.Button(scrollable_frame, text="Iniciar Simulação", command=executar_simulacao)
botao_simular.grid(row=4, column=0, padx=10, pady=10)

# Vincular atualização das camadas ao mudar o número de camadas
def on_num_camadas_change(event):
    atualizar_camadas()

entry_num_camadas.bind("<Return>", on_num_camadas_change)
entry_num_camadas.bind("<FocusOut>", on_num_camadas_change)

# Iniciar a interface gráfica
root.mainloop()
