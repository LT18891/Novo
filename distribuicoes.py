import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
import numpy as np

def limpar_canvas(canvas):
    canvas.figure.clf()
    canvas.draw()

def plotar_distribuicao(x, y, canvas, titulo="Distribuição", xlabel="x", ylabel="Probabilidade/Densidade"):
    fig = canvas.figure
    fig.clf()
    ax = fig.add_subplot(111)
    ax.plot(x, y, 'b-', lw=2)
    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    canvas.draw()

def verificar_parametro_float(valor_str, nome_parametro):
    try:
        return float(valor_str)
    except:
        raise ValueError(nome_parametro+" inválido")

def verificar_parametro_inteiro(valor_str, nome_parametro):
    try:
        return int(valor_str)
    except:
        raise ValueError(nome_parametro+" inválido")

def gerar_dominio_continuo(inicio, fim, num=500):
    return np.linspace(inicio, fim, num)

def fatorial_inteiro(n):
    return math.factorial(n)

def combinacao(n, k):
    return math.factorial(n)/(math.factorial(k)*math.factorial(n-k))

def gamma_func(x):
    return math.gamma(x)

def pdf_normal(x, mu, sigma):
    res = []
    for xi in x:
        v1 = 1/(sigma*math.sqrt(2*math.pi))
        v2 = ((xi - mu)/sigma)**2
        v3 = math.exp(-0.5*v2)
        res.append(v1*v3)
    return np.array(res)

def pmf_binomial(k, n, p):
    return combinacao(n,k)*(p**k)*((1-p)**(n-k))

def pmf_poisson(k, lam):
    return (lam**k)*math.exp(-lam)/fatorial_inteiro(k)

def pdf_uniforme(x, a, b):
    res = []
    largura = b - a
    for xi in x:
        if xi >= a and xi <= b:
            res.append(1.0/largura)
        else:
            res.append(0.0)
    return np.array(res)

def pdf_exponencial(x, lam):
    res = []
    for xi in x:
        if xi >= 0:
            res.append(lam*math.exp(-lam*xi))
        else:
            res.append(0.0)
    return np.array(res)

def pdf_gama(x, k, theta):
    res = []
    coef = 1/( (theta**k)*gamma_func(k) )
    for xi in x:
        if xi>=0:
            v = coef*(xi**(k-1))*math.exp(-xi/theta)
            res.append(v)
        else:
            res.append(0.0)
    return np.array(res)

def beta_func(a,b):
    return gamma_func(a)*gamma_func(b)/gamma_func(a+b)

def pdf_beta(x, alpha, beta_p):
    res = []
    coef = 1/beta_func(alpha,beta_p)
    for xi in x:
        if xi>=0 and xi<=1:
            v = coef*(xi**(alpha-1))*((1-xi)**(beta_p-1))
            res.append(v)
        else:
            res.append(0.0)
    return np.array(res)

def pdf_chi2(x, df):
    res = []
    coef = 1/( (2**(df/2))*gamma_func(df/2) )
    for xi in x:
        if xi>=0:
            v = coef*(xi**((df/2)-1))*math.exp(-xi/2)
            res.append(v)
        else:
            res.append(0.0)
    return np.array(res)

def pmf_bernoulli(x, p):
    res = []
    for xi in x:
        if xi==0:
            res.append((1-p))
        elif xi==1:
            res.append(p)
        else:
            res.append(0.0)
    return np.array(res)

def pmf_geometrica(x, p):
    res = []
    for xi in x:
        if xi>=1:
            val = ((1-p)**(xi-1))*p
            res.append(val)
        else:
            res.append(0.0)
    return np.array(res)

class AplicacaoDistribuicoes:
    def __init__(self, master):
        self.master = master
        master.title("Super Calculadora de Distribuições Probabilísticas")
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill='both', expand=True)
        self.frame_normal = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_normal, text="Normal")
        self._inicializar_normal()
        self.frame_binomial = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_binomial, text="Binomial")
        self._inicializar_binomial()
        self.frame_poisson = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_poisson, text="Poisson")
        self._inicializar_poisson()
        self.frame_uniforme = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_uniforme, text="Uniforme")
        self._inicializar_uniforme()
        self.frame_exponencial = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_exponencial, text="Exponencial")
        self._inicializar_exponencial()
        self.frame_gama = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_gama, text="Gama")
        self._inicializar_gama()
        self.frame_beta = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_beta, text="Beta")
        self._inicializar_beta()
        self.frame_chi2 = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_chi2, text="Qui-Quadrado")
        self._inicializar_chi2()
        self.frame_bernoulli = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_bernoulli, text="Bernoulli")
        self._inicializar_bernoulli()
        self.frame_geometrica = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_geometrica, text="Geométrica")
        self._inicializar_geometrica()

    def _inicializar_normal(self):
        frame = self.frame_normal
        label_titulo = tk.Label(frame, text="Distribuição Normal", font=("Arial", 16, "bold"))
        label_titulo.pack(pady=10)
        param_frame = tk.Frame(frame)
        param_frame.pack(pady=5)
        tk.Label(param_frame, text="Média (μ):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.mu_normal = tk.Entry(param_frame)
        self.mu_normal.insert(0, "0")
        self.mu_normal.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(param_frame, text="Desvio Padrão (σ):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.sigma_normal = tk.Entry(param_frame)
        self.sigma_normal.insert(0, "1")
        self.sigma_normal.grid(row=1, column=1, padx=5, pady=5)
        plot_frame = tk.Frame(frame)
        plot_frame.pack(fill='both', expand=True)
        fig = Figure(figsize=(5,4), dpi=100)
        self.canvas_normal = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas_normal.draw()
        self.canvas_normal.get_tk_widget().pack(fill='both', expand=True)
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Plotar Distribuição Normal", command=self.plotar_normal).pack()

    def _inicializar_binomial(self):
        frame = self.frame_binomial
        label_titulo = tk.Label(frame, text="Distribuição Binomial", font=("Arial", 16, "bold"))
        label_titulo.pack(pady=10)
        param_frame = tk.Frame(frame)
        param_frame.pack(pady=5)
        tk.Label(param_frame, text="n (inteiro):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.n_binomial = tk.Entry(param_frame)
        self.n_binomial.insert(0, "10")
        self.n_binomial.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(param_frame, text="p (0<p<1):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.p_binomial = tk.Entry(param_frame)
        self.p_binomial.insert(0, "0.5")
        self.p_binomial.grid(row=1, column=1, padx=5, pady=5)
        plot_frame = tk.Frame(frame)
        plot_frame.pack(fill='both', expand=True)
        fig = Figure(figsize=(5,4), dpi=100)
        self.canvas_binomial = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas_binomial.draw()
        self.canvas_binomial.get_tk_widget().pack(fill='both', expand=True)
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Plotar Distribuição Binomial", command=self.plotar_binomial).pack()

    def _inicializar_poisson(self):
        frame = self.frame_poisson
        label_titulo = tk.Label(frame, text="Distribuição Poisson", font=("Arial", 16, "bold"))
        label_titulo.pack(pady=10)
        param_frame = tk.Frame(frame)
        param_frame.pack(pady=5)
        tk.Label(param_frame, text="λ (lambda>0):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.lam_poisson = tk.Entry(param_frame)
        self.lam_poisson.insert(0, "2")
        self.lam_poisson.grid(row=0, column=1, padx=5, pady=5)
        plot_frame = tk.Frame(frame)
        plot_frame.pack(fill='both', expand=True)
        fig = Figure(figsize=(5,4), dpi=100)
        self.canvas_poisson = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas_poisson.draw()
        self.canvas_poisson.get_tk_widget().pack(fill='both', expand=True)
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Plotar Distribuição Poisson", command=self.plotar_poisson).pack()

    def _inicializar_uniforme(self):
        frame = self.frame_uniforme
        label_titulo = tk.Label(frame, text="Distribuição Uniforme", font=("Arial", 16, "bold"))
        label_titulo.pack(pady=10)
        param_frame = tk.Frame(frame)
        param_frame.pack(pady=5)
        tk.Label(param_frame, text="a:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.a_uniforme = tk.Entry(param_frame)
        self.a_uniforme.insert(0, "0")
        self.a_uniforme.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(param_frame, text="b:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.b_uniforme = tk.Entry(param_frame)
        self.b_uniforme.insert(0, "1")
        self.b_uniforme.grid(row=1, column=1, padx=5, pady=5)
        plot_frame = tk.Frame(frame)
        plot_frame.pack(fill='both', expand=True)
        fig = Figure(figsize=(5,4), dpi=100)
        self.canvas_uniforme = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas_uniforme.draw()
        self.canvas_uniforme.get_tk_widget().pack(fill='both', expand=True)
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Plotar Distribuição Uniforme", command=self.plotar_uniforme).pack()

    def _inicializar_exponencial(self):
        frame = self.frame_exponencial
        label_titulo = tk.Label(frame, text="Distribuição Exponencial", font=("Arial", 16, "bold"))
        label_titulo.pack(pady=10)
        param_frame = tk.Frame(frame)
        param_frame.pack(pady=5)
        tk.Label(param_frame, text="λ (lambda>0):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.lam_exponencial = tk.Entry(param_frame)
        self.lam_exponencial.insert(0, "1")
        self.lam_exponencial.grid(row=0, column=1, padx=5, pady=5)
        plot_frame = tk.Frame(frame)
        plot_frame.pack(fill='both', expand=True)
        fig = Figure(figsize=(5,4), dpi=100)
        self.canvas_exponencial = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas_exponencial.draw()
        self.canvas_exponencial.get_tk_widget().pack(fill='both', expand=True)
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Plotar Distribuição Exponencial", command=self.plotar_exponencial).pack()

    def _inicializar_gama(self):
        frame = self.frame_gama
        label_titulo = tk.Label(frame, text="Distribuição Gama", font=("Arial", 16, "bold"))
        label_titulo.pack(pady=10)
        param_frame = tk.Frame(frame)
        param_frame.pack(pady=5)
        tk.Label(param_frame, text="Forma (k):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.shape_gama = tk.Entry(param_frame)
        self.shape_gama.insert(0, "2")
        self.shape_gama.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(param_frame, text="Escala (θ):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.scale_gama = tk.Entry(param_frame)
        self.scale_gama.insert(0, "2")
        self.scale_gama.grid(row=1, column=1, padx=5, pady=5)
        plot_frame = tk.Frame(frame)
        plot_frame.pack(fill='both', expand=True)
        fig = Figure(figsize=(5,4), dpi=100)
        self.canvas_gama = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas_gama.draw()
        self.canvas_gama.get_tk_widget().pack(fill='both', expand=True)
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Plotar Distribuição Gama", command=self.plotar_gama).pack()

    def _inicializar_beta(self):
        frame = self.frame_beta
        label_titulo = tk.Label(frame, text="Distribuição Beta", font=("Arial", 16, "bold"))
        label_titulo.pack(pady=10)
        param_frame = tk.Frame(frame)
        param_frame.pack(pady=5)
        tk.Label(param_frame, text="α:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.alpha_beta = tk.Entry(param_frame)
        self.alpha_beta.insert(0, "2")
        self.alpha_beta.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(param_frame, text="β:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.beta_beta = tk.Entry(param_frame)
        self.beta_beta.insert(0, "5")
        self.beta_beta.grid(row=1, column=1, padx=5, pady=5)
        plot_frame = tk.Frame(frame)
        plot_frame.pack(fill='both', expand=True)
        fig = Figure(figsize=(5,4), dpi=100)
        self.canvas_beta = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas_beta.draw()
        self.canvas_beta.get_tk_widget().pack(fill='both', expand=True)
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Plotar Distribuição Beta", command=self.plotar_beta).pack()

    def _inicializar_chi2(self):
        frame = self.frame_chi2
        label_titulo = tk.Label(frame, text="Distribuição Qui-Quadrado", font=("Arial", 16, "bold"))
        label_titulo.pack(pady=10)
        param_frame = tk.Frame(frame)
        param_frame.pack(pady=5)
        tk.Label(param_frame, text="df:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.df_chi2 = tk.Entry(param_frame)
        self.df_chi2.insert(0, "4")
        self.df_chi2.grid(row=0, column=1, padx=5, pady=5)
        plot_frame = tk.Frame(frame)
        plot_frame.pack(fill='both', expand=True)
        fig = Figure(figsize=(5,4), dpi=100)
        self.canvas_chi2 = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas_chi2.draw()
        self.canvas_chi2.get_tk_widget().pack(fill='both', expand=True)
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Plotar Distribuição Qui-Quadrado", command=self.plotar_chi2).pack()

    def _inicializar_bernoulli(self):
        frame = self.frame_bernoulli
        label_titulo = tk.Label(frame, text="Distribuição Bernoulli", font=("Arial", 16, "bold"))
        label_titulo.pack(pady=10)
        param_frame = tk.Frame(frame)
        param_frame.pack(pady=5)
        tk.Label(param_frame, text="p:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.p_bernoulli = tk.Entry(param_frame)
        self.p_bernoulli.insert(0, "0.3")
        self.p_bernoulli.grid(row=0, column=1, padx=5, pady=5)
        plot_frame = tk.Frame(frame)
        plot_frame.pack(fill='both', expand=True)
        fig = Figure(figsize=(5,4), dpi=100)
        self.canvas_bernoulli = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas_bernoulli.draw()
        self.canvas_bernoulli.get_tk_widget().pack(fill='both', expand=True)
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Plotar Distribuição Bernoulli", command=self.plotar_bernoulli).pack()

    def _inicializar_geometrica(self):
        frame = self.frame_geometrica
        label_titulo = tk.Label(frame, text="Distribuição Geométrica", font=("Arial", 16, "bold"))
        label_titulo.pack(pady=10)
        param_frame = tk.Frame(frame)
        param_frame.pack(pady=5)
        tk.Label(param_frame, text="p:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.p_geometrica = tk.Entry(param_frame)
        self.p_geometrica.insert(0, "0.2")
        self.p_geometrica.grid(row=0, column=1, padx=5, pady=5)
        plot_frame = tk.Frame(frame)
        plot_frame.pack(fill='both', expand=True)
        fig = Figure(figsize=(5,4), dpi=100)
        self.canvas_geometrica = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas_geometrica.draw()
        self.canvas_geometrica.get_tk_widget().pack(fill='both', expand=True)
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Plotar Distribuição Geométrica", command=self.plotar_geometrica).pack()

    def plotar_normal(self):
        try:
            mu = verificar_parametro_float(self.mu_normal.get(), "μ")
            sigma = verificar_parametro_float(self.sigma_normal.get(), "σ")
            if sigma<=0:
                raise ValueError("σ>0")
            x = gerar_dominio_continuo(mu-4*sigma, mu+4*sigma, 500)
            y = pdf_normal(x, mu, sigma)
            plotar_distribuicao(x, y, self.canvas_normal, "Distribuição Normal", "x", "f(x)")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def plotar_binomial(self):
        try:
            n = verificar_parametro_inteiro(self.n_binomial.get(), "n")
            p = verificar_parametro_float(self.p_binomial.get(), "p")
            if n<=0:
                raise ValueError("n>0")
            if p<=0 or p>=1:
                raise ValueError("0<p<1")
            x = np.arange(0, n+1)
            y = []
            for k in x:
                y.append(pmf_binomial(k,n,p))
            y = np.array(y)
            plotar_distribuicao(x, y, self.canvas_binomial, "Distribuição Binomial", "k", "P(X=k)")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def plotar_poisson(self):
        try:
            lam = verificar_parametro_float(self.lam_poisson.get(), "λ")
            if lam<=0:
                raise ValueError("λ>0")
            max_x = int(lam+4*math.sqrt(lam)+10)
            if max_x<20:
                max_x=20
            x = np.arange(0, max_x)
            y = []
            for k in x:
                y.append(pmf_poisson(k,lam))
            y = np.array(y)
            plotar_distribuicao(x, y, self.canvas_poisson, "Distribuição Poisson", "k", "P(X=k)")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def plotar_uniforme(self):
        try:
            a = verificar_parametro_float(self.a_uniforme.get(), "a")
            b = verificar_parametro_float(self.b_uniforme.get(), "b")
            if b<=a:
                raise ValueError("b>a")
            x = gerar_dominio_continuo(a-(b-a)*0.1, b+(b-a)*0.1, 500)
            y = pdf_uniforme(x, a, b)
            plotar_distribuicao(x, y, self.canvas_uniforme, "Distribuição Uniforme", "x", "f(x)")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def plotar_exponencial(self):
        try:
            lam = verificar_parametro_float(self.lam_exponencial.get(), "λ")
            if lam<=0:
                raise ValueError("λ>0")
            x = gerar_dominio_continuo(0,5/lam,500)
            y = pdf_exponencial(x, lam)
            plotar_distribuicao(x, y, self.canvas_exponencial, "Distribuição Exponencial", "x", "f(x)")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def plotar_gama(self):
        try:
            shape = verificar_parametro_float(self.shape_gama.get(), "k")
            scale = verificar_parametro_float(self.scale_gama.get(), "θ")
            if shape<=0:
                raise ValueError("k>0")
            if scale<=0:
                raise ValueError("θ>0")
            max_x = shape*scale*5
            x = gerar_dominio_continuo(0,max_x,500)
            y = pdf_gama(x, shape, scale)
            plotar_distribuicao(x, y, self.canvas_gama, "Distribuição Gama", "x", "f(x)")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def plotar_beta(self):
        try:
            alpha = verificar_parametro_float(self.alpha_beta.get(), "α")
            beta_p = verificar_parametro_float(self.beta_beta.get(), "β")
            if alpha<=0 or beta_p<=0:
                raise ValueError("α>0 e β>0")
            x = gerar_dominio_continuo(0,1,500)
            y = pdf_beta(x, alpha, beta_p)
            plotar_distribuicao(x, y, self.canvas_beta, "Distribuição Beta", "x", "f(x)")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def plotar_chi2(self):
        try:
            df_val = verificar_parametro_float(self.df_chi2.get(), "df")
            if df_val<=0:
                raise ValueError("df>0")
            max_x = df_val + 4*math.sqrt(df_val)
            x = gerar_dominio_continuo(0,max_x,500)
            y = pdf_chi2(x, df_val)
            plotar_distribuicao(x, y, self.canvas_chi2, "Distribuição Qui-Quadrado", "x", "f(x)")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def plotar_bernoulli(self):
        try:
            p = verificar_parametro_float(self.p_bernoulli.get(), "p")
            if p<=0 or p>=1:
                raise ValueError("0<p<1")
            x = np.array([0,1])
            y = pmf_bernoulli(x,p)
            plotar_distribuicao(x, y, self.canvas_bernoulli, "Distribuição Bernoulli", "x", "P(X=x)")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def plotar_geometrica(self):
        try:
            p = verificar_parametro_float(self.p_geometrica.get(), "p")
            if p<=0 or p>=1:
                raise ValueError("0<p<1")
            x = np.arange(1,21)
            y = pmf_geometrica(x,p)
            plotar_distribuicao(x, y, self.canvas_geometrica, "Distribuição Geométrica", "x", "P(X=x)")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacaoDistribuicoes(root)
    root.mainloop()
