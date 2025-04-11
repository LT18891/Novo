import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Configuração para reproduzir os resultados
torch.manual_seed(42)
np.random.seed(42)

# --- 1. Geração de Dados Sintéticos Internos ---

# Número de amostras (dias, por exemplo)
num_amostras = 100

# Gerando datas
datas = pd.date_range(start="2025-01-01", periods=num_amostras, freq="D")

# Dados sintéticos: valores aleatórios com distribuição normal ou uniforme
preco_petroleo = np.random.normal(loc=70, scale=10, size=num_amostras)      # Preço do petróleo
indice_bolsa = np.random.normal(loc=3000, scale=200, size=num_amostras)       # Índice de bolsa
volume_negociado = np.random.randint(10000, 50000, size=num_amostras)         # Volume negociado

# Criação do DataFrame
dados = pd.DataFrame({
    "data": datas,
    "preco_petroleo": preco_petroleo,
    "indice_bolsa": indice_bolsa,
    "volume_negociado": volume_negociado
})

# Garante que os dados estejam ordenados por data
dados = dados.sort_values("data")

# --- 2. Pré-processamento: Seleção de variáveis e normalização ---

# Variáveis de entrada (features) e variável de saída (target)
variaveis_entrada = ["indice_bolsa", "volume_negociado"]
variavel_saida = "preco_petroleo"

scaler_X = StandardScaler()
scaler_y = StandardScaler()

# Normalizando as features e o target
X = scaler_X.fit_transform(dados[variaveis_entrada].values)
y = scaler_y.fit_transform(dados[[variavel_saida]].values)

# --- 3. Criação do Dataset Customizado com Janela Deslizante (Sliding Window) ---

class DadosPetroleoDataset(Dataset):
    def __init__(self, entradas, saidas, tamanho_janela=10):
        self.entradas = entradas
        self.saidas = saidas
        self.tamanho_janela = tamanho_janela

    def __len__(self):
        # Total de amostras = número total de pontos menos o tamanho da janela
        return len(self.entradas) - self.tamanho_janela

    def __getitem__(self, idx):
        # Define a sequência de entrada e a saída correspondente (o próximo ponto)
        seq_x = self.entradas[idx: idx + self.tamanho_janela]
        seq_y = self.saidas[idx + self.tamanho_janela]
        return torch.tensor(seq_x, dtype=torch.float32), torch.tensor(seq_y, dtype=torch.float32)

# Tamanho da janela deslizante
tamanho_janela = 10

# Criação do dataset e dataloader
dataset = DadosPetroleoDataset(X, y, tamanho_janela=tamanho_janela)
dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

# --- 4. Definição da Rede Neural com PyTorch ---

class RedePrevisaoPetroleo(nn.Module):
    def __init__(self, n_features, tamanho_oculto, n_camadas, dropout=0.2):
        super(RedePrevisaoPetroleo, self).__init__()
        # LSTM para capturar a dependência temporal
        self.lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=tamanho_oculto,
            num_layers=n_camadas,
            batch_first=True,
            dropout=dropout
        )
        # Camada linear para converter a saída da LSTM na previsão final
        self.fc = nn.Linear(tamanho_oculto, 1)
    
    def forward(self, x):
        # x shape: (batch_size, tamanho_janela, n_features)
        out_lstm, _ = self.lstm(x)
        # Seleciona a última saída da sequência da LSTM
        ultima_saida = out_lstm[:, -1, :]
        out = self.fc(ultima_saida)
        return out

# Configurações do modelo
n_features = len(variaveis_entrada)
tamanho_oculto = 64       # Número de neurônios na camada LSTM
n_camadas = 2             # Número de camadas LSTM

modelo = RedePrevisaoPetroleo(n_features, tamanho_oculto, n_camadas)
print(modelo)

# --- 5. Configuração do Treinamento ---

criterio = nn.MSELoss()  # Função de perda para regressão
otimizador = torch.optim.Adam(modelo.parameters(), lr=0.001)
n_epocas = 50

historico_loss = []  # Para armazenar a perda por época

# Loop de treinamento
modelo.train()
for epoca in range(n_epocas):
    loss_epoca = 0.0
    for sequencia, alvo in dataloader:
        otimizador.zero_grad()        # Zera os gradientes
        saida_pred = modelo(sequencia)
        loss = criterio(saida_pred, alvo)
        loss.backward()
        otimizador.step()
        loss_epoca += loss.item()
    loss_media = loss_epoca / len(dataloader)
    historico_loss.append(loss_media)
    print(f'Época {epoca+1}/{n_epocas} - Loss: {loss_media:.4f}')

# --- 6. Visualização do Treinamento ---

plt.figure(figsize=(10, 5))
plt.plot(historico_loss, label='Loss de Treinamento')
plt.xlabel('Épocas')
plt.ylabel('MSE Loss')
plt.title('Evolução do Erro Durante o Treinamento')
plt.legend()
plt.show()

# --- 7. Exemplo de Previsão ---

modelo.eval()
with torch.no_grad():
    # Utiliza as últimas "tamanho_janela" amostras para a previsão
    entrada_teste = torch.tensor(X[-tamanho_janela:], dtype=torch.float32).unsqueeze(0)  # adiciona dimensão de batch
    previsao_normalizada = modelo(entrada_teste)
    # Converte de volta para a escala original
    previsao = scaler_y.inverse_transform(previsao_normalizada.numpy())
    print("Previsão do preço do petróleo:", previsao[0][0])