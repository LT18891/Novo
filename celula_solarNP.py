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
            camada['alpha'] = float(camadas_entries[i]['alpha'].get())  # Coeficiente de absorção (m^-1)
            camadas.append(camada)

        dopagem_p = float(entry_dopagem_p.get())  # Dopagem aceitadora (P)
        dopagem_n = float(entry_dopagem_n.get())  # Dopagem doadora (N)
        tolerancia = float(entry_tolerancia.get())
        max_iteracoes = int(entry_max_iter.get())

        # Obter espectro de luz
        espectro = []
        for espectro_entry in espectro_entries:
            wl = float(espectro_entry['wl'].get())  # Comprimento de onda (nm)
            intensity = float(espectro_entry['intensity'].get())  # Intensidade (W/m^2)
            espectro.append({'wl': wl, 'intensity': intensity})

        # Realizar a simulação em uma thread separada para não congelar a GUI
        thread = threading.Thread(target=simulacao, args=(N, L, num_camadas, camadas, dopagem_p, dopagem_n, tolerancia, max_iteracoes, espectro))
        thread.start()

    except ValueError as ve:
        messagebox.showerror("Erro de Entrada", f"Por favor, insira valores válidos.\nDetalhes: {ve}")
        botao_simular.config(state=tk.NORMAL)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")
        botao_simular.config(state=tk.NORMAL)

def simulacao(N, L, num_camadas, camadas, dopagem_p, dopagem_n, tolerancia, max_iteracoes, espectro):
    try:
        # Atualizar barra de progresso
        progresso['value'] = 0
        root.update_idletasks()

        # Constantes físicas
        hbar = 1.0545718e-34        # Constante de Planck reduzida (J.s)
        q = 1.60217662e-19          # Carga elementar (C)
        epsilon_0 = 8.854187817e-12  # Permissividade do vácuo (F/m)

        # Conversão de unidades
        eV_to_J = q
        J_to_eV = 1 / q

        # Discretização do espaço
        dx = L / (N - 1)
        x = np.linspace(0, L, N)

        # Inicialização dos vetores de potencial de banda e massa efetiva
        V_banda = np.zeros(N)  # Potencial de banda inicial
        m_star = np.zeros(N)   # Massa efetiva inicial
        alpha = np.zeros(N)    # Coeficiente de absorção inicial

        # Definição das camadas
        for camada in camadas:
            inicio = camada['inicio']
            fim = camada['fim']
            V = camada['V'] * eV_to_J  # Converter eV para Joules
            m = camada['m'] * 9.10938356e-31  # Converter unidades para kg
            a = camada['alpha']  # Coeficiente de absorção (m^-1)
            indices = np.where((x >= inicio) & (x < fim))[0]
            V_banda[indices] = V
            m_star[indices] = m
            alpha[indices] = a

        # Caso alguma posição não tenha sido definida em alguma camada
        m_star[m_star == 0] = 0.067 * 9.10938356e-31  # Valor padrão (por exemplo, GaAs)
        alpha[alpha == 0] = 1e5  # Valor padrão de absorção (ajuste conforme necessário)

        # Definir dopagem para junção p-n
        N_A = np.ones(N) * dopagem_p  # Dopagem aceitadora (P)
        N_D = np.ones(N) * dopagem_n  # Dopagem doadora (N)

        # Inicialização do potencial
        V_potencial = V_banda.copy()

        # Inicializar geração de portadores devido à absorção de luz
        G = np.zeros(N)  # Geração de portadores (m^-3.s^-1)

        # Calcular G baseado no espectro de luz
        for luz in espectro:
            wl = luz['wl'] * 1e-9  # Converter nm para m
            intensity = luz['intensity']  # Intensidade (W/m^2)
            # Energia dos fótons
            E_photon = (hbar * 3e8) / wl  # E = ħω = hc/λ
            # Geração de portadores (simplificado)
            G += alpha * intensity / E_photon  # G ~ α * I / E_photon

        # Parâmetros de iteração
        convergiu = False
        for iteracao in range(max_iteracoes):
            # Atualizar barra de progresso
            progresso['value'] = (iteracao / max_iteracoes) * 100
            root.update_idletasks()

            # Construção do Hamiltoniano
            # Calcula a diagonal principal
            diagonal = (hbar**2) / (m_star * dx**2) + V_potencial  # Tamanho: (N,)

            # Calcula as diagonais secundárias usando a média das massas efetivas entre pontos adjacentes
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
            rho = q * (N_D - N_A)  # Carga devido à dopagem
            for i in range(num_estados):
                rho -= q * np.abs(psi[:, i])**2  # Carga dos elétrons (elétrons negativos)
                # Nota: Para uma simulação completa, incluir lacunas também

            # Adicionar geração de portadores devido à absorção de luz
            rho += q * G * dx  # Simplificação: Geração proporcional à absorção

            # Resolução da Equação de Poisson
            poisson_diag = -2 / dx**2 * np.ones(N)
            poisson_off = 1 / dx**2 * np.ones(N - 1)
            A = diags([poisson_off, poisson_diag, poisson_off], offsets=[-1, 0, 1]).tocsc()

            # Vetor de carga
            b = -rho / epsilon_0

            # Condições de contorno (V = V_built-in nas fronteiras)
            # Aqui, assumimos que o potencial nas fronteiras é o potencial de barreira
            V_built_in = 0.67  # Volts
            V_built_in_J = V_built_in * eV_to_J
            b[0] += (hbar**2) / (m_star[0] * dx**2) * V_built_in_J
            b[-1] += (hbar**2) / (m_star[-1] * dx**2) * V_built_in_J

            # Condições de contorno (V=V_built_in nas fronteiras)
            A = A[1:-1, 1:-1]
            b = b[1:-1]

            # Resolução para V interior
            V_interior = np.linalg.solve(A.toarray(), b)

            # Atualizar o potencial
            V_novo = np.zeros(N)
            V_novo[1:-1] = V_interior
            V_novo[0] = V_built_in_J  # Condição de contorno
            V_novo[-1] = V_built_in_J  # Condição de contorno

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
        plt.figure(figsize=(14, 8))

        # Plot do potencial elétrico
        plt.subplot(2, 2, 1)
        plt.plot(x, V_potencial_eV, label='Potencial Elétrico')
        plt.plot(x, V_banda_eV, label='Potencial de Banda', linestyle='--')
        plt.xlabel('Posição (m)')
        plt.ylabel('Energia (eV)')
        plt.title('Distribuição do Potencial na Célula Fotovoltaica')
        plt.legend()
        plt.grid(True)

        # Plot das funções de onda dos primeiros estados
        plt.subplot(2, 2, 2)
        for i in range(num_estados):
            plt.plot(x, np.abs(psi[:, i])**2 + E_eV[i], label=f'Estado {i + 1} (E={E_eV[i]:.2f} eV)')
        plt.xlabel('Posição (m)')
        plt.ylabel('Densidade de Probabilidade + Energia (eV)')
        plt.title('Funções de Onda dos Estados Eletrônicos')
        plt.legend()
        plt.grid(True)

        # Plot do espectro de absorção
        plt.subplot(2, 2, 3)
        for luz in espectro:
            plt.plot(luz['wl'], luz['intensity'], 'o-', label=f'{luz["wl"]} nm')
        plt.xlabel('Comprimento de Onda (nm)')
        plt.ylabel('Intensidade (W/m²)')
        plt.title('Espectro de Luz Incidente')
        plt.legend()
        plt.grid(True)

        # Plot da geração de portadores
        plt.subplot(2, 2, 4)
        plt.plot(x, G, label='Geração de Portadores (G)')
        plt.xlabel('Posição (m)')
        plt.ylabel('Geração de Portadores (m⁻³.s⁻¹)')
        plt.title('Geração de Portadores devido à Absorção de Luz')
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.show()

        # Interpretação dos Resultados
        interpretacao = (
            "\nInterpretação dos Resultados:\n"
            "1. **Potencial Elétrico:** Mostra a distribuição do potencial ao longo da célula fotovoltaica, incluindo o potencial de barreira da junção p-n.\n"
            "2. **Funções de Onda:** Indicam as regiões onde os elétrons estão mais provavelmente localizados nos primeiros estados eletrônicos.\n"
            "3. **Espectro de Luz Incidente:** Visualiza os diferentes comprimentos de onda e intensidades de luz que estão sendo absorvidos pelo semicondutor.\n"
            "4. **Geração de Portadores:** Mostra a taxa de geração de elétrons e lacunas devido à absorção de luz em cada posição da célula fotovoltaica.\n"
            "5. **Convergência:** A convergência do potencial indica que o equilíbrio entre a distribuição de carga e o potencial elétrico foi alcançado.\n"
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
root.minsize(800, 800)

# Scrollbar para camadas e espectro se houver muitas
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

        ttk.Label(sub_frame, text="Coeficiente de absorção (m⁻¹):").grid(row=4, column=0, sticky="w", pady=2)
        alpha = ttk.Entry(sub_frame)
        alpha.insert(0, "1e5")
        alpha.grid(row=4, column=1, pady=2)

        camadas_entries.append({'inicio': inicio, 'fim': fim, 'V': V, 'm': m, 'alpha': alpha})

# Inicializar camadas
camadas_entries = []
atualizar_camadas()

# Botão para atualizar camadas
botao_atualizar = ttk.Button(frame_camadas, text="Atualizar Camadas", command=atualizar_camadas)
botao_atualizar.grid(row=0, column=0, columnspan=2, pady=5)

# Parâmetros de Dopagem e Iteração
frame_dopagem = ttk.LabelFrame(scrollable_frame, text="Dopagem e Iteração")
frame_dopagem.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

ttk.Label(frame_dopagem, text="Concentração de dopantes aceitadores (N_A) [m⁻³]:").grid(row=0, column=0, sticky="w", pady=2)
entry_dopagem_p = ttk.Entry(frame_dopagem)
entry_dopagem_p.insert(0, "1e24")
entry_dopagem_p.grid(row=0, column=1, pady=2)

ttk.Label(frame_dopagem, text="Concentração de dopantes doadores (N_D) [m⁻³]:").grid(row=1, column=0, sticky="w", pady=2)
entry_dopagem_n = ttk.Entry(frame_dopagem)
entry_dopagem_n.insert(0, "1e24")
entry_dopagem_n.grid(row=1, column=1, pady=2)

ttk.Label(frame_dopagem, text="Tolerância para convergência:").grid(row=2, column=0, sticky="w", pady=2)
entry_tolerancia = ttk.Entry(frame_dopagem)
entry_tolerancia.insert(0, "1e-5")
entry_tolerancia.grid(row=2, column=1, pady=2)

ttk.Label(frame_dopagem, text="Número máximo de iterações:").grid(row=3, column=0, sticky="w", pady=2)
entry_max_iter = ttk.Entry(frame_dopagem)
entry_max_iter.insert(0, "100")
entry_max_iter.grid(row=3, column=1, pady=2)

# Frame para Espectro de Luz
frame_espectro = ttk.LabelFrame(scrollable_frame, text="Espectro de Luz Incidente")
frame_espectro.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

def adicionar_espectro():
    sub_frame = ttk.Frame(frame_espectro)
    sub_frame.pack(pady=2, fill='x', expand=True)

    ttk.Label(sub_frame, text="Comprimento de Onda (nm):").grid(row=0, column=0, sticky="w", pady=2)
    wl_entry = ttk.Entry(sub_frame, width=10)
    wl_entry.insert(0, "600")
    wl_entry.grid(row=0, column=1, pady=2, padx=5)

    ttk.Label(sub_frame, text="Intensidade (W/m²):").grid(row=0, column=2, sticky="w", pady=2)
    intensity_entry = ttk.Entry(sub_frame, width=10)
    intensity_entry.insert(0, "1e3")
    intensity_entry.grid(row=0, column=3, pady=2, padx=5)

    espectro_entries.append({'wl': wl_entry, 'intensity': intensity_entry})

    # Botão para remover espectro
    botao_remover = ttk.Button(sub_frame, text="Remover", command=lambda: remover_espectro(sub_frame))
    botao_remover.grid(row=0, column=4, padx=5)

def remover_espectro(sub_frame):
    for i, entry in enumerate(espectro_entries):
        if entry['wl'].master == sub_frame:
            espectro_entries.pop(i)
            break
    sub_frame.destroy()

# Inicializar espectro com um comprimento de onda padrão
espectro_entries = []
adicionar_espectro()

# Botão para adicionar mais espectros
botao_adicionar_espectro = ttk.Button(frame_espectro, text="Adicionar Espectro", command=adicionar_espectro)
botao_adicionar_espectro.pack(pady=5)

# Barra de Progresso
frame_progresso = ttk.Frame(scrollable_frame)
frame_progresso.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

progresso = ttk.Progressbar(frame_progresso, orient="horizontal", length=400, mode="determinate")
progresso.pack(pady=5)

# Botão de Simulação
botao_simular = ttk.Button(scrollable_frame, text="Iniciar Simulação", command=executar_simulacao)
botao_simular.grid(row=5, column=0, padx=10, pady=10)

# Vincular atualização das camadas ao mudar o número de camadas
def on_num_camadas_change(event):
    atualizar_camadas()

entry_num_camadas.bind("<Return>", on_num_camadas_change)
entry_num_camadas.bind("<FocusOut>", on_num_camadas_change)

# Iniciar a interface gráfica
root.mainloop()
