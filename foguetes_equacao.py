#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otimização de Trajetória de Foguetes via DDP/iLQR (Plano 2D)
Autor: Luiz Tiago Wilcke

Resumo:
- Estados: x = [px, py, vx, vy, m]  (posição horizontal/vertical, velocidades, massa)
- Controles: u = [sigma, alpha]     (sigma = fração de empuxo [0..1], alpha = ângulo em rad)
- Dinâmica discreta (passo de tempo dt):
    px_{k+1} = px + vx*dt
    py_{k+1} = py + vy*dt
    v  = [vx, vy]
    T  = sigma*Tmax * [cos(alpha), sin(alpha)]
    D  = 1/2 * rho(py) * Cd * Aref * ||v|| * v   (força de arrasto, direção oposta a v)
    g  = mu/(R_T + py)^2
    a  = (T - D)/m - [0, g]
    vx_{k+1} = vx + a_x * dt
    vy_{k+1} = vy + a_y * dt
    m_{k+1}  = m - (sigma*Tmax)/(Isp*g0) * dt

- Custo:
  • Etapa (running): penaliza uso de empuxo (sigma^2), saturação de sigma, ângulo agressivo,
    *dynamic pressure* q = 1/2 rho ||v||^2 excedendo q_max (penalidade suave), e proximidade do solo.
  • Terminal: penaliza erro para alvo (px, py, velocidade horizontal/vertical) e recompensa massa final.

- Método:
  • iLQR/DDP com linearização/quadricização local da dinâmica e custo
  • Retropassagem Riccati (ganhos K, kff), avanço com line-search e regularização LM.
  • Limites simples nos controles: sigma∈[0,1], alpha∈[alpha_min, alpha_max] com projeção.

Observação:
- Este é um "esqueleto de pesquisa" (nível PhD): modular, extensível para restrições duras
  (via penalidades aumentadas) e múltiplos estágios (boostback, reentrada etc.).
"""

import numpy as np

# --------------------------
# Constantes físicas/globais
# --------------------------
g0 = 9.80665                 # gravidade ao nível do mar (m/s^2)
R_T = 6371e3                 # raio médio da Terra (m)
mu  = 3.986004418e14         # GM da Terra (m^3/s^2)

# Atmosfera: densidade ISA simplificada com escala
rho0 = 1.225                 # kg/m^3 ao nível do mar
Hesc = 8500.0                # escala (m)

def densidade_atmosfera(alt):
    """Densidade ~ rho0 * exp(-alt/Hesc), alt >= 0."""
    alt = np.maximum(0.0, alt)
    return rho0 * np.exp(-alt / Hesc)

# --------------------------
# Modelo do foguete
# --------------------------
class Foguete2D:
    def __init__(self, Tmax, Isp, Cd, Aref,
                 alpha_min=np.deg2rad(-10.0), alpha_max=np.deg2rad(85.0)):
        self.Tmax = float(Tmax)       # empuxo máximo (N)
        self.Isp  = float(Isp)        # impulso específico (s)
        self.Cd   = float(Cd)         # coef. de arrasto
        self.Aref = float(Aref)       # área de referência (m^2)
        self.alpha_min = float(alpha_min)
        self.alpha_max = float(alpha_max)

    def projetar_controle(self, u):
        """Aplica limites simples: sigma em [0,1], alpha em [alpha_min, alpha_max]."""
        sigma = np.clip(u[0], 0.0, 1.0)
        alpha = np.clip(u[1], self.alpha_min, self.alpha_max)
        return np.array([sigma, alpha])

    def dinamica(self, x, u, dt):
        """Avança a dinâmica pelo método de Euler (discretização simples, estável com dt pequeno)."""
        px, py, vx, vy, m = x
        sigma, alpha = self.projetar_controle(u)

        v = np.array([vx, vy])
        vnorm = np.linalg.norm(v) + 1e-12
        rho = densidade_atmosfera(py)
        D_vec = 0.5 * rho * self.Cd * self.Aref * vnorm * v   # direção +v; subtrair depois
        g = mu / (R_T + py)**2

        T_vec = sigma * self.Tmax * np.array([np.cos(alpha), np.sin(alpha)])
        a_vec = (T_vec - D_vec) / max(m, 1e-6) + np.array([0.0, -g])

        # Integração explícita (poderia usar semi-implícita/Runge-Kutta)
        pxn = px + vx*dt
        pyn = max(0.0, py + vy*dt)  # sem perfurar o solo
        vxn = vx + a_vec[0]*dt
        vyn = vy + a_vec[1]*dt
        mdot = (sigma * self.Tmax) / (self.Isp * g0)
        mn  = max(1.0, m - mdot*dt)  # evita massa <= 0

        return np.array([pxn, pyn, vxn, vyn, mn])

    def linearizar(self, x, u, dt, eps=1e-6):
        """
        Lineariza por diferenças: x_{k+1} ≈ f + A dx + B du.
        Retorna f, A, B.
        """
        f0 = self.dinamica(x, u, dt)
        n = x.size; m = u.size
        A = np.zeros((n, n))
        B = np.zeros((n, m))

        # Derivadas por diferenças finitas
        for i in range(n):
            dx = np.zeros(n); dx[i] = eps
            A[:, i] = (self.dinamica(x + dx, u, dt) - f0) / eps
        for j in range(m):
            du = np.zeros(m); du[j] = eps
            B[:, j] = (self.dinamica(x, u + du, dt) - f0) / eps
        return f0, A, B

# --------------------------
# Funções de custo
# --------------------------
class Custo:
    def __init__(self, foguete: Foguete2D, pesos):
        """
        pesos: dict com chaves:
          w_sigma, w_alpha, w_sigma_lim, w_q, w_chao, w_terminal_pos, w_terminal_vel, w_terminal_m
          q_max, alpha_ref
        """
        self.f = foguete
        # parâmetros
        self.w_sigma      = pesos.get("w_sigma", 1e-3)
        self.w_alpha      = pesos.get("w_alpha", 1e-4)
        self.w_sigma_lim  = pesos.get("w_sigma_lim", 1e-2)
        self.w_q          = pesos.get("w_q", 1e-5)
        self.q_max        = pesos.get("q_max", 40e3)  # Pa
        self.w_chao       = pesos.get("w_chao", 1e-1)
        self.alpha_ref    = pesos.get("alpha_ref", np.deg2rad(0.0))

        self.w_term_pos   = pesos.get("w_terminal_pos", np.array([1e-5, 1e-5]))
        self.w_term_vel   = pesos.get("w_terminal_vel", np.array([5e-5, 5e-5]))
        self.w_term_m     = pesos.get("w_terminal_m", 5e-2)  # recompensa (sinal negativo)

    def custo_etapa(self, x, u, dt):
        """
        Custo instantâneo l(x,u) ~ penalidades quadráticas (e softplus para q).
        """
        px, py, vx, vy, m = x
        sigma, alpha = self.f.projetar_controle(u)
        vnorm = np.hypot(vx, vy)
        rho = densidade_atmosfera(py)
        q = 0.5 * rho * vnorm**2   # dynamic pressure

        # penalidades
        l_sigma = self.w_sigma * sigma**2
        l_alpha = self.w_alpha * (alpha - self.alpha_ref)**2
        l_lim   = self.w_sigma_lim * (np.maximum(0.0, sigma - 1.0)**2 + np.maximum(0.0, -sigma)**2)

        excedente_q = np.maximum(0.0, q - self.q_max)
        l_q = self.w_q * excedente_q**2

        l_chao = self.w_chao * (np.maximum(0.0, -py)**2)

        # custo final da etapa (multiplica dt para integral)
        return dt * (l_sigma + l_alpha + l_lim + l_q + l_chao)

    def custo_terminal(self, x, alvo_pos, alvo_vel):
        """
        Custo terminal phi(x_T): penaliza erro em posição/velocidade; recompensa massa restante.
        """
        px, py, vx, vy, m = x
        dx = np.array([px - alvo_pos[0], py - alvo_pos[1]])
        dv = np.array([vx - alvo_vel[0], vy - alvo_vel[1]])
        custo_pos = self.w_term_pos * (dx**2)
        custo_vel = self.w_term_vel * (dv**2)
        recompensa_m = - self.w_term_m * m  # queremos massa grande -> custo reduz

        return custo_pos.sum() + custo_vel.sum() + recompensa_m

    # Aproximações quadráticas para DDP (por diferenças finitas)
    def quadricizar_etapa(self, f, x, u, dt, eps=1e-6):
        """
        Retorna l, lx, lu, lxx, luu, lux (aprox. por diferenças).
        f = foguete para consistência de projeção de limites.
        """
        l0 = self.custo_etapa(x, u, dt)
        n = x.size; m = u.size
        lx = np.zeros(n); lu = np.zeros(m)
        lxx = np.zeros((n, n)); luu = np.zeros((m, m)); lux = np.zeros((m, n))

        # gradientes
        for i in range(n):
            dx = np.zeros(n); dx[i] = eps
            lx[i] = (self.custo_etapa(x+dx, u, dt) - l0) / eps
        for j in range(m):
            du = np.zeros(m); du[j] = eps
            lu[j] = (self.custo_etapa(x, u+du, dt) - l0) / eps

        # hessianas simétricas por diferenças de gradiente
        for i in range(n):
            dx = np.zeros(n); dx[i] = eps
            lxi = np.zeros(n)
            for k in range(n):
                dk = np.zeros(n); dk[k] = eps
                lxi[k] = (self.custo_etapa(x+dx+dk, u, dt) - self.custo_etapa(x+dx, u, dt)
                          - self.custo_etapa(x+dk, u, dt) + l0) / (eps*eps)
            lxx[:, i] = lxi
        for j in range(m):
            du = np.zeros(m); du[j] = eps
            luj = np.zeros(m)
            for k in range(m):
                dk = np.zeros(m); dk[k] = eps
                luj[k] = (self.custo_etapa(x, u+du+dk, dt) - self.custo_etapa(x, u+du, dt)
                          - self.custo_etapa(x, u+dk, dt) + l0) / (eps*eps)
            luu[:, j] = luj
            # lux
            for i in range(n):
                dx = np.zeros(n); dx[i] = eps
                lux[j, i] = (self.custo_etapa(x+dx, u+du, dt) - self.custo_etapa(x+dx, u, dt)
                             - self.custo_etapa(x, u+du, dt) + l0) / (eps*eps)

        # simetrizar
        lxx = 0.5*(lxx + lxx.T)
        luu = 0.5*(luu + luu.T)
        return l0, lx, lu, lxx, luu, lux

    def quadricizar_terminal(self, x, alvo_pos, alvo_vel, eps=1e-6):
        phi0 = self.custo_terminal(x, alvo_pos, alvo_vel)
        n = x.size
        px = np.zeros(n); Hx = np.zeros((n, n))
        for i in range(n):
            dx = np.zeros(n); dx[i] = eps
            px[i] = (self.custo_terminal(x+dx, alvo_pos, alvo_vel) - phi0) / eps
        for i in range(n):
            dx = np.zeros(n); dx[i] = eps
            Hxi = np.zeros(n)
            for k in range(n):
                dk = np.zeros(n); dk[k] = eps
                Hxi[k] = (self.custo_terminal(x+dx+dk, alvo_pos, alvo_vel)
                          - self.custo_terminal(x+dx, alvo_pos, alvo_vel)
                          - self.custo_terminal(x+dk, alvo_pos, alvo_vel)
                          + phi0) / (eps*eps)
            Hx[:, i] = Hxi
        Hx = 0.5*(Hx + Hx.T)
        return phi0, px, Hx

# --------------------------
# iLQR / DDP
# --------------------------
class iLQR:
    def __init__(self, foguete: Foguete2D, custo: Custo, dt, N,
                 lambda_ini=1.0, lambda_max=1e6, fator_up=10.0, fator_dn=0.5):
        self.f = foguete
        self.c = custo
        self.dt = float(dt)
        self.N = int(N)
        # parâmetros de Levenberg–Marquardt
        self.lmbda = lambda_ini
        self.lmbda_max = lambda_max
        self.fac_up = fator_up
        self.fac_dn = fator_dn

    def rolar(self, x0, U):
        """Integra a dinâmica para sequência de controles U (N passos)."""
        X = [x0.copy()]
        for k in range(self.N):
            X.append(self.f.dinamica(X[-1], U[k], self.dt))
        return np.array(X), np.array(U)

    def custo_total(self, X, U, alvo_pos, alvo_vel):
        total = 0.0
        for k in range(self.N):
            total += self.c.custo_etapa(X[k], U[k], self.dt)
        total += self.c.custo_terminal(X[-1], alvo_pos, alvo_vel)
        return total

    def backward_pass(self, X, U, alvo_pos, alvo_vel, reg):
        """
        Passo para trás (Riccati). Retorna listas K,kff e melhoria de custo modelada.
        """
        n = X.shape[1]; m = U.shape[1]
        K_list = [np.zeros((m, n)) for _ in range(self.N)]
        kff_list = [np.zeros(m) for _ in range(self.N)]

        # terminal
        phi0, Vx, Vxx = self.c.quadricizar_terminal(X[-1], alvo_pos, alvo_vel)
        dV = 0.0  # modelo

        for k in range(self.N-1, -1, -1):
            xk = X[k]; uk = U[k]
            f0, Ak, Bk = self.f.linearizar(xk, uk, self.dt)

            l0, lx, lu, lxx, luu, lux = self.c.quadricizar_etapa(self.f, xk, uk, self.dt)

            # Q-terms
            Qx  = lx + Ak.T @ Vx
            Qu  = lu + Bk.T @ Vx
            Qxx = lxx + Ak.T @ Vxx @ Ak
            Quu = luu + Bk.T @ Vxx @ Bk
            Qux = lux + Bk.T @ Vxx @ Ak

            # regularização LM
            Quu_reg = Quu + reg * np.eye(m)

            # Resolver Quu * kff = -Qu  (preferir solve simétrico)
            try:
                kff = -np.linalg.solve(Quu_reg, Qu)
                K   = -np.linalg.solve(Quu_reg, Qux)
            except np.linalg.LinAlgError:
                return None  # falha

            # atualização de V
            dV += 0.5 * kff.T @ Quu @ kff + kff.T @ Qu

            Vx  = Qx + K.T @ Quu @ kff + K.T @ Qu + Qux.T @ kff
            Vxx = Qxx + K.T @ Quu @ K + K.T @ Qux + Qux.T @ K
            # simetrizar
            Vxx = 0.5*(Vxx + Vxx.T)

            K_list[k] = K
            kff_list[k] = kff

        return K_list, kff_list, dV

    def forward_line_search(self, X, U, K_list, kff_list, x0, alvo_pos, alvo_vel):
        """
        Avanço com busca em linha sobre escalas do feedforward.
        """
        alfas = 0.5 ** np.arange(0, 10)  # 1.0, 0.5, 0.25, ...
        J0 = self.custo_total(X, U, alvo_pos, alvo_vel)
        melhor_J = np.inf
        melhor_par = None

        for a in alfas:
            Xn = [x0.copy()]
            Un = []
            for k in range(self.N):
                xk = Xn[-1]
                du = kff_list[k]*a + K_list[k] @ (xk - X[k])
                uk = self.f.projetar_controle(U[k] + du)
                Un.append(uk)
                Xn.append(self.f.dinamica(xk, uk, self.dt))
            Xn = np.array(Xn); Un = np.array(Un)
            Jn = self.custo_total(Xn, Un, alvo_pos, alvo_vel)
            if Jn < melhor_J:
                melhor_J = Jn
                melhor_par = (Xn, Un, a)
        return melhor_par, J0, melhor_J

    def otimizar(self, x0, U_ini, alvo_pos, alvo_vel, max_iter=100, tol=1e-4, verbose=True):
        X, U = self.rolar(x0, U_ini)
        J = self.custo_total(X, U, alvo_pos, alvo_vel)
        if verbose:
            print(f"[iLQR] J_inicial = {J:.6e}")

        for it in range(1, max_iter+1):
            # backward
            out = self.backward_pass(X, U, alvo_pos, alvo_vel, reg=self.lmbda)
            if out is None:
                self.lmbda = min(self.lmbda * self.fac_up, self.lmbda_max)
                if verbose:
                    print(f"  Backward falhou, aumentando lambda -> {self.lmbda:.3e}")
                continue
            K_list, kff_list, dV_model = out

            # forward
            melhor, J0, Jcand = self.forward_line_search(X, U, K_list, kff_list, X[0], alvo_pos, alvo_vel)
            if melhor is None:
                self.lmbda = min(self.lmbda * self.fac_up, self.lmbda_max)
                if verbose:
                    print(f"  Forward falhou, aumentando lambda -> {self.lmbda:.3e}")
                continue

            Xn, Un, alpha_usado = melhor
            reducao_real = J0 - Jcand
            reducao_modelo = max(1e-12, -dV_model)
            rho = reducao_real / reducao_modelo

            if verbose:
                print(f"[Iter {it:02d}] J={Jcand:.6e}  ΔJ_real={reducao_real:.3e}  ρ={rho:.3f}  α={alpha_usado:.3f}  λ={self.lmbda:.2e}")

            # aceitar/piorar
            if reducao_real > 0:
                X, U, J = Xn, Un, Jcand
                # reduzir lambda se o modelo previu bem
                if rho > 0.25:
                    self.lmbda = max(1e-8, self.lmbda * self.fac_dn)
            else:
                self.lmbda = min(self.lmbda * self.fac_up, self.lmbda_max)

            if reducao_real / (abs(J0) + 1e-12) < tol:
                if verbose:
                    print("Convergência atingida.")
                break

        return X, U, J

# --------------------------
# Exemplo executável
# --------------------------
def exemplo_padrao():
    # Configuração do foguete (valores plausíveis)
    Tmax = 1.8e6        # N (ex.: ~Merlin 1D SL ~845 kN; aqui mais alto)
    Isp  = 300.0        # s (nível do mar ~280-300 s)
    Cd   = 0.3          # coeficiente de arrasto
    Aref = 3.14         # m^2 (diâmetro ~2 m)

    foguete = Foguete2D(Tmax=Tmax, Isp=Isp, Cd=Cd, Aref=Aref)

    # Horizonte e discretização
    dt = 0.5            # s
    N  = 240            # ~120 s de queima

    # Estado inicial (plataforma)
    px0, py0 = 0.0, 0.0
    vx0, vy0 = 0.0, 0.0
    m0       = 1.5e5    # kg (massa inicial)
    x0 = np.array([px0, py0, vx0, vy0, m0])

    # Alvo terminal: “suborbital agressivo” (100 km e 2000 m/s horizontal)
    alvo_pos = np.array([150e3, 100e3])       # 150 km horizontal, 100 km altitude
    alvo_vel = np.array([2000.0, 100.0])      # 2 km/s horizontal, pequena vertical

    # Pesos do custo
    pesos = {
        "w_sigma": 1e-4,
        "w_alpha": 1e-6,
        "w_sigma_lim": 1e-2,
        "w_q": 5e-6,
        "q_max": 45e3,                   # limite de dynamic pressure (Pa)
        "w_chao": 1e-2,
        "alpha_ref": np.deg2rad(0.0),
        "w_terminal_pos": np.array([1e-8, 2e-8]),
        "w_terminal_vel": np.array([4e-8, 4e-8]),
        "w_terminal_m": 5e-2
    }
    custo = Custo(foguete, pesos)

    # iLQR
    ilqr = iLQR(foguete, custo, dt=dt, N=N)

    # Chute inicial de controles: queima retilínea subindo e *pitch-over* leve
    sigma_ini = np.clip(np.linspace(1.0, 0.6, N), 0.0, 1.0)
    alpha_ini = np.deg2rad(np.clip(np.linspace(85.0, 5.0, N), foguete.alpha_min*180/np.pi, foguete.alpha_max*180/np.pi))
    U_ini = np.vstack([sigma_ini, alpha_ini]).T

    # Otimizar
    X_opt, U_opt, J_final = ilqr.otimizar(x0, U_ini, alvo_pos, alvo_vel, max_iter=60, tol=5e-4, verbose=True)

    # Relatório final
    print("\n=== Relatório Final ===")
    print(f"Custo final J = {J_final:.6e}")
    print(f"Posição final (px, py) = ({X_opt[-1,0]:.1f} m, {X_opt[-1,1]:.1f} m)")
    print(f"Velocidade final (vx, vy) = ({X_opt[-1,2]:.1f} m/s, {X_opt[-1,3]:.1f} m/s)")
    print(f"Massa final = {X_opt[-1,4]:.1f} kg")
    print(f"Dynamic pressure máx. (aprox): {calcular_qmax(X_opt):.1f} Pa")

    # Dicas de pós-processamento: salve CSV para plotar em outro lugar
    try:
        import csv
        with open("trajetoria_otima.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t","px","py","vx","vy","m","sigma","alpha_deg","q_Pa"])
            for k in range(N+1):
                t = k*dt
                if k < N:
                    sigma, alpha = U_opt[k]
                else:
                    sigma, alpha = U_opt[-1]
                vnorm = np.hypot(X_opt[k,2], X_opt[k,3])
                rho = densidade_atmosfera(X_opt[k,1])
                q = 0.5 * rho * vnorm**2
                w.writerow([t, X_opt[k,0], X_opt[k,1], X_opt[k,2], X_opt[k,3], X_opt[k,4],
                            sigma, np.rad2deg(alpha), q])
        print("Arquivo salvo: trajetoria_otima.csv")
    except Exception as e:
        print("Não consegui salvar CSV (sem problema). Erro:", e)

def calcular_qmax(X):
    qmax = 0.0
    for k in range(X.shape[0]):
        vx, vy = X[k,2], X[k,3]
        v = np.hypot(vx, vy)
        rho = densidade_atmosfera(X[k,1])
        q = 0.5 * rho * v*v
        qmax = max(qmax, q)
    return qmax

if __name__ == "__main__":
    exemplo_padrao()
