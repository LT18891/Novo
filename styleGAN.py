import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

# ------------------------------------------------------------
# Configurações
# ------------------------------------------------------------
dim_latente = 512  # Dimensão do espaço latente z e w
resolucao_imagem = 64  # Exemplo: saída 64x64 (StyleGAN original vai até 1024x1024)
filtros_iniciais = 512
canal_final = 3     # Imagem RGB
dim_intermediaria = 512

# ------------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------------
def equalized_lr_dense(units):
    # Camada Dense com Equalized Learning Rate (simplificado)
    return layers.Dense(units, kernel_initializer='he_normal')

def equalized_lr_conv(filters, kernel_size, **kwargs):
    # Camada Conv com Equalized LR (simplificada)
    return layers.Conv2D(filters, kernel_size, padding='same', kernel_initializer='he_normal', **kwargs)

def adain(x, y):
    # AdaIN simplificado
    # x: [N,H,W,C], y: [N, 2C] contendo [scale, bias]
    shape = tf.shape(x)
    mean, var = tf.nn.moments(x, axes=[1,2], keepdims=True)
    x_norm = (x - mean) / tf.sqrt(var + 1e-8)
    scale = y[:, :shape[3]]
    bias = y[:, shape[3]:]
    scale = tf.reshape(scale, [-1,1,1,shape[3]])
    bias = tf.reshape(bias, [-1,1,1,shape[3]])
    return x_norm * scale + bias

class StyleMod(layers.Layer):
    # Aplica o estilo (w) numa camada convolucional via AdaIN
    def __init__(self, canais):
        super().__init__()
        self.canais = canais
        self.dense = layers.Dense(self.canais*2)
    def call(self, x, w):
        style = self.dense(w)
        return adain(x, style)

def bloco_estilo(x, w, filtros, upsample=True):
    # Bloco da rede de síntese: 
    # opicionalmente faz upsample, convolução, estilo, etc.
    if upsample:
        x = layers.UpSampling2D(interpolation='nearest')(x)
    x = equalized_lr_conv(filtros, 3)(x)
    x = StyleMod(filtros)(x, w)
    x = tf.nn.relu(x)
    x = equalized_lr_conv(filtros, 3)(x)
    x = StyleMod(filtros)(x, w)
    x = tf.nn.relu(x)
    return x

# ------------------------------------------------------------
# Rede de Mapeamento (Mapping Network)
# Transforma z (Gaussiano) em w, removendo correlações e simplificando o espaço.
# ------------------------------------------------------------
def construir_rede_mapeamento(dim_latente=dim_latente, num_camadas=8):
    entrada_z = layers.Input(shape=(dim_latente,))
    x = entrada_z
    for _ in range(num_camadas):
        x = layers.Dense(dim_latente, activation='relu')(x)
    # Saída é w
    saida_w = x
    return models.Model(entrada_z, saida_w, name="MappingNetwork")

# ------------------------------------------------------------
# Rede de Síntese (Synthesis Network)
# Começa com uma const inicial e vai crescendo até a resolução desejada.
# ------------------------------------------------------------
def construir_rede_sintese(resolucao=resolucao_imagem, canais_finais=3):
    # Calcula quantos blocos são necessários
    # Ex: resolucao=64 --> resoluções: 4,8,16,32,64 (5 passos)
    # Começa em 4x4
    etapas = int(np.log2(resolucao)) - 2  # para 64: log2(64)=6, -2=4 etapas depois do 4x4

    entrada_w = layers.Input(shape=(dim_latente,))

    # Inicialização: const 4x4
    x = tf.zeros((tf.shape(entrada_w)[0], 4, 4, filtros_iniciais)) # Constante aprendível
    x = tf.Variable(tf.random.normal([1,4,4,filtros_iniciais]), trainable=True) + x

    # Primeiro estilo
    x = StyleMod(filtros_iniciais)(x, entrada_w)
    x = tf.nn.relu(x)
    x = equalized_lr_conv(filtros_iniciais, 3)(x)
    x = StyleMod(filtros_iniciais)(x, entrada_w)
    x = tf.nn.relu(x)

    filtros = filtros_iniciais
    for i in range(etapas):
        filtros = max(filtros // 2, 32) # Diminuir numero de filtros a cada etapa
        x = bloco_estilo(x, entrada_w, filtros, upsample=True)

    # Camada final para gerar imagem
    imagem = equalized_lr_conv(canais_finais, 1, activation='tanh')(x)
    return models.Model(entrada_w, imagem, name="SynthesisNetwork")

# ------------------------------------------------------------
# Discriminador (Simplificado StyleGAN)
# Inverso da rede de síntese: a partir da imagem vai reduzindo até 4x4
# ------------------------------------------------------------
def construir_discriminador(resolucao=resolucao_imagem, canais=3):
    entrada_img = layers.Input(shape=(resolucao, resolucao, canais))
    x = entrada_img

    # Número de etapas iguais ao gerador
    etapas = int(np.log2(resolucao)) - 2
    filtros = max(filtros_iniciais // (2**(etapas)), 32)

    # Blocos inversos
    for i in range(etapas):
        x = equalized_lr_conv(filtros, 3)(x)
        x = tf.nn.leaky_relu(x, 0.2)
        x = equalized_lr_conv(filtros, 3)(x)
        x = tf.nn.leaky_relu(x, 0.2)
        x = layers.AveragePooling2D()(x)
        filtros = min(filtros * 2, filtros_iniciais)

    # Agora estamos em ~4x4
    x = equalized_lr_conv(filtros_iniciais, 3)(x)
    x = tf.nn.leaky_relu(x, 0.2)
    x = layers.Flatten()(x)
    x = layers.Dense(1)(x)  # Saída escalar
    return models.Model(entrada_img, x, name="Discriminator")

# ------------------------------------------------------------
# Montagem do StyleGAN
# ------------------------------------------------------------
mapping_network = construir_rede_mapeamento()
synthesis_network = construir_rede_sintese()
discriminator = construir_discriminador()

# Exemplo de Forward Pass:
z_amostra = np.random.randn(1, dim_latente).astype('float32')
w_amostra = mapping_network.predict(z_amostra, verbose=0)
img_sintetizada = synthesis_network.predict(w_amostra, verbose=0)

print("Forma da imagem sintetizada:", img_sintetizada.shape)  # Deve ser (1,64,64,3)

# ------------------------------------------------------------
# Compilando a Rede Adversária (Treinamento simplificado)
# Aqui apenas ilustramos o setup, o loop de treinamento seria complexo.
# ------------------------------------------------------------
discriminator.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(0.0001, 0.0, 0.99))
# Ao treinar o gerador, congelamos o discriminador
discriminator.trainable = False
entrada_z = layers.Input(shape=(dim_latente,))
w = mapping_network(entrada_z)
img_fake = synthesis_network(w)
valido = discriminator(img_fake)
gan = models.Model(entrada_z, valido, name="StyleGAN")
gan.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(0.0001, 0.0, 0.99))

print("Modelos construídos com sucesso!")
