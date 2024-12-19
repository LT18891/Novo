import tkinter as tk
from tkinter import messagebox
import requests
import time
import threading
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Intervalo de atualização em segundos
UPDATE_INTERVAL = 5
DATA_LENGTH = 100  # Quantidade de pontos a manter no histórico

class CryptoBotGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Robô de Investimento em Bitcoin")

        # Frame principal
        self.frame = tk.Frame(self.master, bg="#2c3e50")
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.prices = []
        self.times = []

        # Criação do título
        self.title_label = tk.Label(self.frame, text="Robô de Investimento em Bitcoin", 
                                    font=("Arial", 16), fg="white", bg="#2c3e50")
        self.title_label.pack(pady=10)

        # Criação do frame do gráfico
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Preço BTC/USDT (Tempo Real)")
        self.ax.set_xlabel("Tempo")
        self.ax.set_ylabel("Preço (USDT)")
        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=10)

        # Frame de botões
        self.button_frame = tk.Frame(self.frame, bg="#2c3e50")
        self.button_frame.pack(pady=10)

        self.buy_button = tk.Button(self.button_frame, text="Comprar 0.001 BTC", command=self.buy, bg="#4ca1af", fg="white", bd=0, padx=10, pady=5)
        self.buy_button.grid(row=0, column=0, padx=5)

        self.sell_button = tk.Button(self.button_frame, text="Vender 0.001 BTC", command=self.sell, bg="#e74c3c", fg="white", bd=0, padx=10, pady=5)
        self.sell_button.grid(row=0, column=1, padx=5)

        # Label de status
        self.status_label = tk.Label(self.frame, text="Aguardando dados...", fg="white", bg="#2c3e50", font=("Arial", 10))
        self.status_label.pack(pady=5)

        # Inicializar gráfico
        self.line, = self.ax.plot([], [], color='cyan', label="Preço BTC")
        self.sma10_line, = self.ax.plot([], [], color='yellow', label="SMA10")
        self.sma30_line, = self.ax.plot([], [], color='magenta', label="SMA30")
        self.ax.legend()

        # Iniciar a thread de atualização
        self.running = True
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()

    def fetch_price(self):
        # Obtém o preço atual do Bitcoin via API da Binance
        url = "https://api.binance.com/api/v3/ticker/price"
        params = {"symbol": "BTCUSDT"}
        try:
            r = requests.get(url, params=params, timeout=5)
            data = r.json()
            price = float(data["price"])
            return price
        except Exception as e:
            print("Erro ao obter preço:", e)
            return None

    def update_loop(self):
        # Loop para atualização periódica do preço
        while self.running:
            price = self.fetch_price()
            if price is not None:
                current_time = datetime.now().strftime("%H:%M:%S")
                self.prices.append(price)
                self.times.append(current_time)

                # Limitar o tamanho da lista
                if len(self.prices) > DATA_LENGTH:
                    self.prices.pop(0)
                    self.times.pop(0)

                # Atualizar o gráfico e a estratégia
                self.update_chart()
                self.run_strategy()

                # Atualizar label de status
                self.set_status(f"Último preço: {price:.2f} USDT | Atualizado: {current_time}")

            time.sleep(UPDATE_INTERVAL)

    def update_chart(self):
        if not self.prices:
            return

        # Atualizar dados do gráfico
        self.line.set_xdata(range(len(self.prices)))
        self.line.set_ydata(self.prices)

        # Calcular SMA de 10 e 30 períodos se possível
        prices_arr = np.array(self.prices)
        if len(prices_arr) >= 30:
            sma10 = self.simple_moving_average(prices_arr, 10)
            sma30 = self.simple_moving_average(prices_arr, 30)
            # Ajustar tamanho dos arrays
            x_vals = range(len(prices_arr))
            self.sma10_line.set_xdata(x_vals[9:])  # SMA10 só começa após 10 pontos
            self.sma10_line.set_ydata(sma10)
            self.sma30_line.set_xdata(x_vals[29:]) # SMA30 só começa após 30 pontos
            self.sma30_line.set_ydata(sma30)
        else:
            self.sma10_line.set_xdata([])
            self.sma10_line.set_ydata([])
            self.sma30_line.set_xdata([])
            self.sma30_line.set_ydata([])

        # Ajustar limites do gráfico
        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw()

    def simple_moving_average(self, data, period):
        return np.convolve(data, np.ones(period)/period, mode='valid')

    def run_strategy(self):
        # Estratégia simples: compra se SMA10 cruza acima da SMA30, vende se cruza abaixo
        if len(self.prices) < 30:
            return

        prices_arr = np.array(self.prices)
        sma10 = self.simple_moving_average(prices_arr, 10)
        sma30 = self.simple_moving_average(prices_arr, 30)

        # Checar cruzamentos
        if len(sma10) >= 2 and len(sma30) >= 2:
            # Últimos dois valores das SMAs
            prev_sma10 = sma10[-2]
            prev_sma30 = sma30[-2]
            curr_sma10 = sma10[-1]
            curr_sma30 = sma30[-1]

            # Sinal de compra
            if prev_sma10 < prev_sma30 and curr_sma10 > curr_sma30:
                print("Sinal de COMPRA detectado pela estratégia.")
                # Aqui você poderia chamar self.buy() automaticamente
                
            # Sinal de venda
            if prev_sma10 > prev_sma30 and curr_sma10 < curr_sma30:
                print("Sinal de VENDA detectado pela estratégia.")
                # Aqui você poderia chamar self.sell() automaticamente

    def buy(self):
        # Aqui você implementaria a lógica de compra real usando a API da exchange
        # Este é um exemplo simulado
        print("Compra de 0.001 BTC executada (simulação).")
        messagebox.showinfo("Compra", "Compra simulada de 0.001 BTC realizada.")

    def sell(self):
        # Aqui você implementaria a lógica de venda real usando a API da exchange
        # Este é um exemplo simulado
        print("Venda de 0.001 BTC executada (simulação).")
        messagebox.showinfo("Venda", "Venda simulada de 0.001 BTC realizada.")

    def set_status(self, text):
        self.status_label.config(text=text)

    def on_closing(self):
        self.running = False
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoBotGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
