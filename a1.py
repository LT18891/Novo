import torch
import torch.nn as nn
import torch.optim as optim
import random
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm  # Barra de progresso
import math
import os

# =========================
# CLASSE DE VOCABULÁRIO
# =========================
class Vocabulário:
    def __init__(self, min_freq=1):
        self.palavra2indice = {}
        self.indice2palavra = {}
        self.contador = 0
        self.ocorrencias = {}
        self.min_freq = min_freq
        # Tokens especiais
        self.adicionar_palavra("<pad>")
        self.adicionar_palavra("<sos>")
        self.adicionar_palavra("<eos>")
        self.adicionar_palavra("<unk>")
    
    def adicionar_palavra(self, palavra):
        if palavra not in self.palavra2indice:
            self.palavra2indice[palavra] = self.contador
            self.indice2palavra[self.contador] = palavra
            self.contador += 1
            self.ocorrencias[palavra] = 1
        else:
            self.ocorrencias[palavra] += 1
            
    def construir_vocabulario(self, frases):
        for frase in frases:
            for palavra in frase.split():
                self.adicionar_palavra(palavra.lower())
        # Remover palavras com frequência abaixo do mínimo (exceto tokens especiais)
        palavras_para_remover = []
        for palavra, freq in self.ocorrencias.items():
            if freq < self.min_freq and palavra not in ["<pad>", "<sos>", "<eos>", "<unk>"]:
                palavras_para_remover.append(palavra)
        for palavra in palavras_para_remover:
            indice = self.palavra2indice.pop(palavra)
            self.indice2palavra.pop(indice)
        # Reindexar as palavras restantes
        novas_palavras = sorted(self.palavra2indice.items(), key=lambda x: x[1])
        self.palavra2indice = {}
        self.indice2palavra = {}
        self.contador = 0
        for palavra, _ in novas_palavras:
            self.palavra2indice[palavra] = self.contador
            self.indice2palavra[self.contador] = palavra
            self.contador += 1

# =========================
# FUNÇÃO DE PRE-PROCESSAMENTO
# =========================
def tensorizar_frase(frase, vocabulário):
    # Adiciona tokens de início e fim
    indices = [vocabulário.palavra2indice.get("<sos>")]
    for palavra in frase.split():
        idx = vocabulário.palavra2indice.get(palavra.lower(), vocabulário.palavra2indice.get("<unk>"))
        indices.append(idx)
    indices.append(vocabulário.palavra2indice.get("<eos>"))
    return torch.tensor(indices, dtype=torch.long)

# =========================
# CONJUNTO DE DADOS PARA O CHATBOT
# =========================
class ConjuntoDadosChat(Dataset):
    def __init__(self, pares, vocabulário):
        self.pares = pares  # Lista de tuplas (entrada, resposta)
        self.vocabulário = vocabulário
        self.dados = []
        for entrada, resposta in pares:
            tensor_entrada = tensorizar_frase(entrada, vocabulário)
            tensor_resposta = tensorizar_frase(resposta, vocabulário)
            self.dados.append((tensor_entrada, tensor_resposta))
    
    def __len__(self):
        return len(self.dados)
    
    def __getitem__(self, idx):
        return self.dados[idx]

# Função para preencher (pad) as sequências dentro de um batch
def pad_collate(batch):
    entradas, respostas = zip(*batch)
    entradas_padded = torch.nn.utils.rnn.pad_sequence(entradas, padding_value=vocab.palavra2indice["<pad>"])
    respostas_padded = torch.nn.utils.rnn.pad_sequence(respostas, padding_value=vocab.palavra2indice["<pad>"])
    return entradas_padded, respostas_padded

# =========================
# MODELO – CODIFICADOR (Encoder)
# =========================
class Codificador(nn.Module):
    def __init__(self, tamanho_vocab, tamanho_emb, tamanho_oculto, num_camadas=2, dropout=0.5):
        super(Codificador, self).__init__()
        self.embedding = nn.Embedding(tamanho_vocab, tamanho_emb)
        # GRU bidirecional; a saída terá dimensão tamanho_oculto*2
        self.rnn = nn.GRU(tamanho_emb, tamanho_oculto, num_layers=num_camadas, dropout=dropout, bidirectional=True)
        self.dropout = nn.Dropout(dropout)
        self.tamanho_oculto = tamanho_oculto
    def forward(self, entrada):
        # entrada: [comprimento_seq, batch_size]
        emb = self.dropout(self.embedding(entrada))
        saida, ocultos = self.rnn(emb)
        return saida, ocultos

# =========================
# MODELO – DECODIFICADOR COM MULTI-HEAD ATTENTION
# =========================
class Decodificador(nn.Module):
    def __init__(self, tamanho_vocab, tamanho_emb, tamanho_oculto, num_heads=4, dropout=0.5):
        super(Decodificador, self).__init__()
        self.embedding = nn.Embedding(tamanho_vocab, tamanho_emb)
        self.dropout = nn.Dropout(dropout)
        self.tamanho_oculto = tamanho_oculto
        # Utiliza o módulo MultiheadAttention (a dimensão da atenção será tamanho_oculto*2, pois o encoder é bidirecional)
        self.multihead_attn = nn.MultiheadAttention(embed_dim=tamanho_oculto*2, num_heads=num_heads, dropout=dropout)
        # A entrada para o GRU será a concatenação do embedding e do vetor de contexto da atenção
        self.rnn = nn.GRU(tamanho_emb + tamanho_oculto*2, tamanho_oculto, num_layers=2, dropout=dropout)
        # Camada fully-connected para gerar as probabilidades do próximo token
        self.fc_out = nn.Linear(tamanho_oculto + tamanho_oculto*2 + tamanho_emb, tamanho_vocab)
    def forward(self, entrada, oculto, saida_codificador):
        # entrada: [batch_size] – token atual (índice)
        entrada = entrada.unsqueeze(0)  # [1, batch_size]
        emb = self.dropout(self.embedding(entrada))  # [1, batch_size, tamanho_emb]
        batch_size = saida_codificador.shape[1]
        seq_len = saida_codificador.shape[0]
        # Utiliza o último estado oculto do decoder como consulta para a atenção
        consulta = oculto[-1].unsqueeze(0)  # [1, batch_size, tamanho_oculto]
        # Para que a dimensão da consulta seja compatível com a chave/valor (tamanho_oculto*2), fazemos uma projeção simples
        proj_consulta = consulta.repeat(seq_len, 1, 2)  # Nota: esta projeção é apenas ilustrativa
        attn_output, attn_weights = self.multihead_attn(query=proj_consulta, key=saida_codificador, value=saida_codificador)
        # Agregamos a saída da atenção (por exemplo, fazendo uma média ao longo do tempo)
        contexto = attn_output.mean(dim=0).unsqueeze(0)  # [1, batch_size, tamanho_oculto*2]
        # Concatena o embedding com o vetor de contexto e passa para a GRU
        rnn_input = torch.cat((emb, contexto), dim=2)  # [1, batch_size, tamanho_emb + tamanho_oculto*2]
        saida, oculto = self.rnn(rnn_input, oculto)
        emb = emb.squeeze(0)         # [batch_size, tamanho_emb]
        saida = saida.squeeze(0)     # [batch_size, tamanho_oculto]
        contexto = contexto.squeeze(0)  # [batch_size, tamanho_oculto*2]
        # Gera a distribuição sobre o vocabulário combinando a saída do GRU, o contexto e o embedding
        saida_final = self.fc_out(torch.cat((saida, contexto, emb), dim=1))
        return saida_final, oculto, attn_weights

# =========================
# MODELO SEQ2SEQ
# =========================
class Seq2Seq(nn.Module):
    def __init__(self, codificador, decodificador, dispositivo):
        super(Seq2Seq, self).__init__()
        self.codificador = codificador
        self.decodificador = decodificador
        self.dispositivo = dispositivo
        # Verifica se o tamanho oculto do encoder e do decoder são compatíveis
        assert codificador.tamanho_oculto == decodificador.tamanho_oculto, "Tamanhos ocultos incompatíveis"
    def forward(self, entrada, alvo, professor_forcing=0.5):
        # entrada: [comprimento_seq, batch_size]
        # alvo: [comprimento_seq_alvo, batch_size]
        batch_size = alvo.shape[1]
        max_len = alvo.shape[0]
        tamanho_vocab = self.decodificador.embedding.num_embeddings
        saidas = torch.zeros(max_len, batch_size, tamanho_vocab).to(self.dispositivo)
        
        # Codificação
        saida_codificador, ocultos_codificador = self.codificador(entrada)
        # Combina as saídas das duas direções do encoder
        num_layers = ocultos_codificador.size(0) // 2
        oculto_decodificador_lista = []
        for i in range(num_layers):
            oculto_decodificador_lista.append(ocultos_codificador[2*i] + ocultos_codificador[2*i+1])
        oculto_decodificador = torch.stack(oculto_decodificador_lista)
        
        # Inicialmente, a entrada para o decoder é o token <sos>
        entrada_decodificador = alvo[0, :]
        for t in range(1, max_len):
            saida, oculto_decodificador, _ = self.decodificador(entrada_decodificador, oculto_decodificador, saida_codificador)
            saidas[t] = saida
            # Teacher forcing: com certa probabilidade usa o token real do alvo na próxima etapa
            usar_professor = random.random() < professor_forcing
            entrada_decodificador = alvo[t] if usar_professor else saida.argmax(1)
        return saidas

# =========================
# FUNÇÃO DE BEAM SEARCH PARA DECODIFICAÇÃO
# =========================
def beam_search_decoding(modelo, tensor_entrada, vocabulário, beam_width=3, max_len=20):
    modelo.eval()
    with torch.no_grad():
        saida_codificador, ocultos_codificador = modelo.codificador(tensor_entrada)
        num_layers = ocultos_codificador.size(0) // 2
        oculto_decodificador_lista = []
        for i in range(num_layers):
            oculto_decodificador_lista.append(ocultos_codificador[2*i] + ocultos_codificador[2*i+1])
        oculto_decodificador = torch.stack(oculto_decodificador_lista)
        
        # Cada item na lista: (sequência de índices, score acumulado, estado oculto atual)
        sequencias = [([vocabulário.palavra2indice["<sos>"]], 0.0, oculto_decodificador)]
        
        for _ in range(max_len):
            novas_sequencias = []
            for seq, score, oculto in sequencias:
                if seq[-1] == vocabulário.palavra2indice["<eos>"]:
                    novas_sequencias.append((seq, score, oculto))
                    continue
                entrada_decodificador = torch.tensor([seq[-1]], device=modelo.dispositivo)
                saida, novo_oculto, _ = modelo.decodificador(entrada_decodificador, oculto, saida_codificador)
                log_probs = torch.log_softmax(saida, dim=1)
                topk = torch.topk(log_probs, beam_width, dim=1)
                valores, indices = topk.values.squeeze(0), topk.indices.squeeze(0)
                for i in range(beam_width):
                    novo_seq = seq + [indices[i].item()]
                    novo_score = score + valores[i].item()
                    novas_sequencias.append((novo_seq, novo_score, novo_oculto))
            sequencias = sorted(novas_sequencias, key=lambda x: x[1], reverse=True)[:beam_width]
            # Se todas as sequências já terminaram com <eos>, encerra a busca
            if all(seq[-1] == vocabulário.palavra2indice["<eos>"] for seq, _, _ in sequencias):
                break
        melhor_seq = sequencias[0][0]
        return melhor_seq

# =========================
# FUNÇÃO DE TREINAMENTO COM SCHEDULER
# =========================
def treinar(modelo, otimizador, criterio, iterador, dispositivo, professor_forcing_inicial=1.0, decaimento_forcing=0.95):
    modelo.train()
    perda_total = 0
    professor_forcing = professor_forcing_inicial
    for entrada, alvo in tqdm(iterador, desc="Treinamento", leave=False):
        entrada = entrada.to(dispositivo)
        alvo = alvo.to(dispositivo)
        otimizador.zero_grad()
        saidas = modelo(entrada, alvo, professor_forcing)
        # Ignora o primeiro token (<sos>) para o cálculo da perda
        saidas = saidas[1:].view(-1, saidas.shape[-1])
        alvo_reshaped = alvo[1:].view(-1)
        perda = criterio(saidas, alvo_reshaped)
        perda.backward()
        torch.nn.utils.clip_grad_norm_(modelo.parameters(), 1)
        otimizador.step()
        perda_total += perda.item()
        professor_forcing *= decaimento_forcing  # Decaimento gradual do teacher forcing
    return perda_total / len(iterador)

# =========================
# FUNÇÕES PARA SALVAR E CARREGAR O MODELO
# =========================
def salvar_modelo(modelo, caminho="modelo_chatbot.pth"):
    torch.save(modelo.state_dict(), caminho)
    print("Modelo salvo em:", caminho)

def carregar_modelo(modelo, caminho="modelo_chatbot.pth"):
    if os.path.exists(caminho):
        modelo.load_state_dict(torch.load(caminho))
        print("Modelo carregado com sucesso.")
    else:
        print("Arquivo de modelo não encontrado.")

# =========================
# BLOCO PRINCIPAL
# =========================
if __name__ == "__main__":
    dispositivo = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Definindo alguns pares de conversa mais complexos
    pares_conversa = [
        ("olá, tudo bem?", "olá, estou bem, como posso ajudar?"),
        ("qual é o seu nome?", "eu sou um chatbot avançado."),
        ("me conte uma piada", "por que o robô atravessou a estrada? para recarregar a bateria!"),
        ("o que você pode fazer?", "posso conversar e ajudar com informações diversas."),
        ("adeus", "até logo, foi bom conversar com você."),
    ]
    
    # Construir o vocabulário a partir das frases
    vocabulário = Vocabulário(min_freq=1)
    for entrada, resposta in pares_conversa:
        vocabulário.construir_vocabulario([entrada, resposta])
    
    # Variável global para uso na função de colate (padding)
    global vocab
    vocab = vocabulário
    tamanho_vocab = vocabulário.contador
    tamanho_emb = 128
    tamanho_oculto = 256
    
    # Criar conjunto de dados e DataLoader
    conjunto_dados = ConjuntoDadosChat(pares_conversa, vocabulário)
    dataloader = DataLoader(conjunto_dados, batch_size=2, shuffle=True, collate_fn=pad_collate)
    
    # Instanciar os módulos: codificador, decodificador e o modelo seq2seq
    codificador = Codificador(tamanho_vocab, tamanho_emb, tamanho_oculto, num_camadas=2, dropout=0.5).to(dispositivo)
    decodificador = Decodificador(tamanho_vocab, tamanho_emb, tamanho_oculto, num_heads=4, dropout=0.5).to(dispositivo)
    modelo = Seq2Seq(codificador, decodificador, dispositivo).to(dispositivo)
    
    otimizador = optim.Adam(modelo.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(otimizador, mode='min', factor=0.5, patience=2, verbose=True)
    criterio = nn.CrossEntropyLoss(ignore_index=vocabulário.palavra2indice["<pad>"])
    
    num_epocas = 20
    melhor_perda = math.inf
    for epoca in range(num_epocas):
        perda_epoca = treinar(modelo, otimizador, criterio, dataloader, dispositivo, professor_forcing_inicial=1.0, decaimento_forcing=0.99)
        scheduler.step(perda_epoca)
        print(f"Época {epoca+1} - Perda: {perda_epoca:.4f}")
        if perda_epoca < melhor_perda:
            melhor_perda = perda_epoca
            salvar_modelo(modelo)
    
    # =========================
    # FUNÇÃO DE RESPOSTA (INFERÊNCIA) UTILIZANDO BEAM SEARCH
    # =========================
    def responder(frase, beam_width=3):
        modelo.eval()
        with torch.no_grad():
            tensor_entrada = tensorizar_frase(frase, vocabulário).unsqueeze(1).to(dispositivo)  # [comprimento_seq, 1]
            indices_seq = beam_search_decoding(modelo, tensor_entrada, vocabulário, beam_width=beam_width, max_len=20)
            # Converter os índices em palavras, ignorando <sos> e <eos>
            palavras = [vocabulário.indice2palavra[idx] for idx in indices_seq if idx not in (vocabulário.palavra2indice["<sos>"], vocabulário.palavra2indice["<eos>"])]
            return " ".join(palavras)
    
    # Loop de interação com o usuário
    print("\nDigite 'sair' para encerrar a conversa.\n")
    while True:
        entrada_usuario = input("Você: ")
        if entrada_usuario.lower() == "sair":
            break
        resposta_chatbot = responder(entrada_usuario, beam_width=3)
        print("Chatbot:", resposta_chatbot)
