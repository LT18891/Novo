# Autor: Luiz Tiago Wilcke

import warnings
warnings.filterwarnings('ignore')  # Suprimir todos os warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from scipy.integrate import odeint

# 1. Dados sintéticos semanais (2018–2022) com exógenas
np.random.seed(42)
semanas_por_ano = 52
anos = 5
n = semanas_por_ano * anos
datas = pd.date_range(start='2018-01-01', periods=n, freq='W-SUN')

temperatura = 20 + 10 * np.sin(2 * np.pi * np.arange(n) / semanas_por_ano) + 2 * np.random.randn(n)
umidade     = 0.7 + 0.2 * np.cos(2 * np.pi * np.arange(n) / semanas_por_ano) + 0.05 * np.random.randn(n)
incidencia  = (
    100
    + 30 * np.sin(2 * np.pi * np.arange(n) / semanas_por_ano)
    + 0.5 * temperatura
    - 10 * umidade
    + 15 * np.random.randn(n)
)

df = pd.DataFrame({
    'incidencia': incidencia,
    'temperatura': temperatura,
    'umidade': umidade
}, index=datas)
df.index.freq = 'W-SUN'

# 2. Split treino (4 anos) / teste (1 ano)
treino = df.iloc[:semanas_por_ano * 4]
teste  = df.iloc[semanas_por_ano * 4:]

# 3. SARIMAX sazonal com exógenas
exog_treino = treino[['temperatura', 'umidade']]
exog_teste  = teste[['temperatura', 'umidade']]

modelo_sarimax = SARIMAX(
    treino['incidencia'],
    order=(1, 0, 1),
    seasonal_order=(1, 1, 1, semanas_por_ano),
    exog=exog_treino,
    enforce_stationarity=False,
    enforce_invertibility=False,
    simple_differencing=True
)

resultado_sarimax = modelo_sarimax.fit(
    disp=False,
    method='lbfgs',
    maxiter=200,
    tol=1e-8
)

pre_sarimax = resultado_sarimax.get_forecast(
    steps=len(teste),
    exog=exog_teste
).predicted_mean

# 4. Random Forest TS com lags
def criar_lags(df, coluna, lags):
    for lag in lags:
        df[f'{coluna}_lag{lag}'] = df[coluna].shift(lag)
    return df

lags = [1, 52]
df_lags = criar_lags(df.copy(), 'incidencia', lags).dropna()

# Ajustar split para lags
offset = max(lags)
treino_lags = df_lags.iloc[:semanas_por_ano * 4 - offset]
teste_lags  = df_lags.iloc[semanas_por_ano * 4 - offset:]

X_treino = treino_lags.drop(columns=['incidencia'])
y_treino = treino_lags['incidencia']
X_teste  = teste_lags.drop(columns=['incidencia'])
y_teste  = teste_lags['incidencia']

rf = RandomForestRegressor(n_estimators=200, random_state=42)
rf.fit(X_treino, y_treino)
pre_rf = rf.predict(X_teste)

# 5. Ensemble simples
pre_ensemble = (pre_sarimax.values + pre_rf) / 2

# 6. Métricas
def mostrar_metricas(nome, obs, prev):
    rmse = np.sqrt(mean_squared_error(obs, prev))
    mape = mean_absolute_percentage_error(obs, prev) * 100
    print(f'{nome} — RMSE: {rmse:.2f}, MAPE: {mape:.2f}%')

mostrar_metricas('SARIMAX+Exógenas', teste['incidencia'], pre_sarimax)
mostrar_metricas('RandomForest TS', y_teste, pre_rf)
mostrar_metricas('Ensemble', teste['incidencia'], pre_ensemble)

# 7. Plot comparativo
plt.figure(figsize=(10, 6))
teste['incidencia'].plot(label='Observado')
pre_sarimax.plot(label='SARIMAX', linestyle='-')
plt.plot(teste_lags.index, pre_rf, label='RandomForest', linestyle='--')
plt.plot(teste.index, pre_ensemble, label='Ensemble', linestyle=':')
plt.title('Previsão de Incidência de Gripe')
plt.xlabel('Data')
plt.ylabel('Casos Semanais')
plt.legend()
plt.show()

# 8. SEIR sazonal com vacinação
def seir_sazonal_vacina(y, t, beta0, sigma, gamma, amp, taxa_vac):
    S, E, I, R = y
    beta = beta0 * (1 + amp * np.sin(2 * np.pi * t / semanas_por_ano))
    return (
        -beta * S * I / N - taxa_vac * S,
         beta * S * I / N - sigma * E,
         sigma * E - gamma * I,
         gamma * I + taxa_vac * S
    )

N = 600_000
I0 = max(df['incidencia'].iloc[0], 1)
E0, R0 = 10, 0
S0 = N - I0 - E0 - R0
y0 = (S0, E0, I0, R0)
t  = np.arange(n)

beta0, sigma, gamma = 0.4, 1/2, 1/10
amp, taxa_vac = 0.3, 1e-4

sol = odeint(seir_sazonal_vacina, y0, t, args=(beta0, sigma, gamma, amp, taxa_vac))
_, _, infectados_seir, _ = sol.T

plt.figure(figsize=(10, 5))
plt.plot(df.index, infectados_seir, label='Infectados (SEIR)')
plt.title('Simulação SEIR Sazonal com Vacinação')
plt.xlabel('Data')
plt.ylabel('Nº Infectados')
plt.legend()
plt.show()
