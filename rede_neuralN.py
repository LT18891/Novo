# Autor: Luiz Tiago Wilcke
# Rede Neural para Aprender a Escrever — Ensemble (MoE) com múltiplos especialistas
# - Especialistas: Transformer, LSTM e CNN causal
# - Mistura por rede de porteiros (gating) causal via convoluções 1D
# - Avaliação estatística: Perda, Perplexidade, AIC, BIC (ensemble e por especialista)
# - Treinamento conjunto fim-a-fim com label smoothing, dropout, AdamW, warmup + cosseno, clip de gradiente
# - Geração com temperatura, top-k, top-p e penalidade de repetição; opção de MC Dropout

import math, os, argparse, time, random
from dataclasses import dataclass
from typing import List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

# =========================
# Utilidades e configuração
# =========================

@dataclass
class Configuracao:
    caminho_corpus: str = "corpus.txt"
    caminho_modelo: str = "modelo_moe.pt"

    # Tokenização nível de caractere (robusta, zero dependências)
    minusculizar: bool = False
    remover_quebras_excessivas: bool = True

    # Arquitetura base
    dim_modelo: int = 512
    num_cabecas: int = 8
    num_camadas_tx: int = 8      # camadas do Transformer
    num_camadas_lstm: int = 2
    canais_cnn: int = 512
    pilha_cnn_blocos: int = 6
    kernel_cnn: int = 3
    taxa_dropout: float = 0.2
    comprimento_contexto: int = 256

    # Gating (porteiro)
    dim_gating: int = 256

    # Treinamento
    tamanho_lote: int = 64
    passos_treino: int = 8000
    passos_avaliacao: int = 400
    taxa_aprendizado: float = 3e-4
    aquecimento_passos: int = 800
    suavizacao_rotulo: float = 0.05
    peso_decay: float = 0.01
    clip_grad: float = 1.0
    proporcao_validacao: float = 0.05
    semente: int = 123

    # Geração
    temperatura: float = 0.9
    top_k: int = 40
    top_p: float = 0.95
    penalidade_repeticao: float = 1.1
    max_novos_tokens: int = 400
    amostras_mc_dropout: int = 0   # >0 ativa ensemble bayesiano por MC Dropout


def definir_semente(seed=123):
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

# ==============
# Tokenização
# ==============

class TokenizadorChar:
    def __init__(self, texto):
        chars = sorted(list(set(texto)))
        self.vocab = chars
        self.tok2id = {ch:i for i,ch in enumerate(self.vocab)}
        self.id2tok = {i:ch for ch,i in self.tok2id.items()}

    @property
    def tamanho_vocab(self):
        return len(self.vocab)

    def codificar(self, s: str) -> torch.Tensor:
        return torch.tensor([self.tok2id[c] for c in s if c in self.tok2id], dtype=torch.long)

    def decodificar(self, ids: List[int]) -> str:
        return "".join([self.id2tok[int(i)] for i in ids])


def carregar_texto(cfg: Configuracao) -> str:
    assert os.path.exists(cfg.caminho_corpus), f"Não encontrei {cfg.caminho_corpus}"
    texto = open(cfg.caminho_corpus, "r", encoding="utf-8").read()
    if cfg.minusculizar:
        texto = texto.lower()
    if cfg.remover_quebras_excessivas:
        texto = "\n".join(l.strip() for l in texto.splitlines() if l.strip() != "")
    return texto


def preparar_dados(ids: torch.Tensor, proporcao_validacao=0.05) -> Tuple[torch.Tensor, torch.Tensor]:
    n = len(ids)
    nval = int(n*proporcao_validacao)
    ids_treino = ids[:-nval] if nval>0 else ids
    ids_val = ids[-nval:] if nval>0 else ids[-min(5000, n):]
    return ids_treino, ids_val


def lotes_aleatorios(dados: torch.Tensor, tam_lote: int, comp_ctx: int, dispositivo: str):
    ix = torch.randint(low=0, high=len(dados)-comp_ctx-1, size=(tam_lote,))
    x = torch.stack([dados[i:i+comp_ctx] for i in ix]).to(dispositivo)
    y = torch.stack([dados[i+1:i+comp_ctx+1] for i in ix]).to(dispositivo)
    return x, y

# ==============================
# Camadas e especialistas (NNs)
# ==============================

class AtençãoMultiCabeças(nn.Module):
    def __init__(self, dim, num_cabecas, dropout, comp_ctx):
        super().__init__()
        assert dim % num_cabecas == 0
        self.num_cabecas = num_cabecas
        self.dim_cabeca = dim // num_cabecas
        self.qkv = nn.Linear(dim, 3*dim, bias=False)
        self.proj = nn.Linear(dim, dim, bias=False)
        self.dropout = nn.Dropout(dropout)
        self.register_buffer("mascara", torch.tril(torch.ones(comp_ctx, comp_ctx)).unsqueeze(0).unsqueeze(0))

    def forward(self, x):
        B, T, C = x.shape
        qkv = self.qkv(x)
        q, k, v = qkv.split(C, dim=2)
        q = q.view(B, T, self.num_cabecas, self.dim_cabeca).transpose(1,2)
        k = k.view(B, T, self.num_cabecas, self.dim_cabeca).transpose(1,2)
        v = v.view(B, T, self.num_cabecas, self.dim_cabeca).transpose(1,2)
        att = (q @ k.transpose(-2, -1)) / math.sqrt(self.dim_cabeca)
        att = att.masked_fill(self.mascara[:,:,:T,:T]==0, float('-inf'))
        att = F.softmax(att, dim=-1)
        att = self.dropout(att)
        out = att @ v
        out = out.transpose(1,2).contiguous().view(B, T, C)
        return self.proj(out)

class BlocoTransformer(nn.Module):
    def __init__(self, dim, num_cabecas, dropout, comp_ctx):
        super().__init__()
        self.ln1 = nn.LayerNorm(dim)
        self.attn = AtençãoMultiCabeças(dim, num_cabecas, dropout, comp_ctx)
        self.ln2 = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(
            nn.Linear(dim, 4*dim), nn.GELU(), nn.Linear(4*dim, dim), nn.Dropout(dropout)
        )
    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x

class EspecialistaTransformer(nn.Module):
    def __init__(self, dim, num_cabecas, num_camadas, dropout, comp_ctx):
        super().__init__()
        self.blocos = nn.ModuleList([BlocoTransformer(dim, num_cabecas, dropout, comp_ctx) for _ in range(num_camadas)])
        self.ln = nn.LayerNorm(dim)
    def forward(self, e):  # e: (B,T,C)
        x = e
        for b in self.blocos:
            x = b(x)
        return self.ln(x)  # (B,T,C)

class EspecialistaLSTM(nn.Module):
    def __init__(self, dim, num_camadas, dropout):
        super().__init__()
        self.lstm = nn.LSTM(input_size=dim, hidden_size=dim, num_layers=num_camadas, batch_first=True, dropout=dropout)
        self.ln = nn.LayerNorm(dim)
    def forward(self, e):
        x, _ = self.lstm(e)
        return self.ln(x)

class CausalConv1d(nn.Module):
    def __init__(self, canais_in, canais_out, kernel):
        super().__init__()
        self.kernel = kernel
        self.conv = nn.Conv1d(canais_in, canais_out, kernel_size=kernel)
    def forward(self, x):  # x: (B,C,T)
        pad = (self.kernel-1, 0)
        x = F.pad(x, pad)
        return self.conv(x)

class BlocoCNN(nn.Module):
    def __init__(self, canais, kernel, dropout):
        super().__init__()
        self.conv1 = CausalConv1d(canais, canais, kernel)
        self.conv2 = CausalConv1d(canais, canais, kernel)
        self.dropout = nn.Dropout(dropout)
        self.act = nn.GELU()
        self.ln = nn.LayerNorm(canais)
    def forward(self, x):  # x: (B,T,C)
        y = x.transpose(1,2)
        y = self.act(self.conv1(y))
        y = self.dropout(self.act(self.conv2(y)))
        y = y.transpose(1,2)
        return self.ln(x + y)

class EspecialistaCNN(nn.Module):
    def __init__(self, canais, kernel, blocos, dropout):
        super().__init__()
        self.seq = nn.Sequential(*[BlocoCNN(canais, kernel, dropout) for _ in range(blocos)])
        self.ln = nn.LayerNorm(canais)
    def forward(self, e):
        x = self.seq(e)
        return self.ln(x)

class RedeGatingCausal(nn.Module):
    """Gera pesos por passo temporal (B,T,E) de forma causal a partir das embeddings."""
    def __init__(self, dim_in, dim_oculto, num_experts, dropout):
        super().__init__()
        self.conv1 = CausalConv1d(dim_in, dim_oculto, kernel=3)
        self.conv2 = CausalConv1d(dim_oculto, num_experts, kernel=3)
        self.dropout = nn.Dropout(dropout)
        self.act = nn.GELU()
    def forward(self, e):  # e: (B,T,C)
        y = e.transpose(1,2)  # (B,C,T)
        y = self.act(self.conv1(y))
        y = self.dropout(self.conv2(y))  # (B,E,T)
        y = y.transpose(1,2)  # (B,T,E)
        pesos = F.softmax(y, dim=-1)
        return pesos

# ================================
# Modelo Ensemble (MoE) completo
# ================================

class EnsembleMoE(nn.Module):
    def __init__(self, tamanho_vocab, cfg: Configuracao):
        super().__init__()
        self.cfg = cfg
        self.tamanho_vocab = tamanho_vocab
        C = cfg.dim_modelo
        T = cfg.comprimento_contexto
        self.emb_tok = nn.Embedding(tamanho_vocab, C)
        self.emb_pos = nn.Embedding(T, C)
        self.dropout = nn.Dropout(cfg.taxa_dropout)

        # Especialistas
        self.tx = EspecialistaTransformer(C, cfg.num_cabecas, cfg.num_camadas_tx, cfg.taxa_dropout, T)
        self.lstm = EspecialistaLSTM(C, cfg.num_camadas_lstm, cfg.taxa_dropout)
        self.cnn = EspecialistaCNN(cfg.canais_cnn, cfg.kernel_cnn, cfg.pilha_cnn_blocos, cfg.taxa_dropout)
        self.especialistas = [self.tx, self.lstm, self.cnn]
        self.num_experts = len(self.especialistas)

        # Decoder compartilhado + weight tying
        self.decoder = nn.Linear(C, tamanho_vocab, bias=False)
        self.decoder.weight = self.emb_tok.weight

        # Gating
        self.gate = RedeGatingCausal(C, cfg.dim_gating, self.num_experts, cfg.taxa_dropout)

        # Camada final de normalização (opcional)
        self.ln_final = nn.LayerNorm(C)

    def embeddings(self, idx):
        B, T = idx.shape
        pos = torch.arange(0, T, dtype=torch.long, device=idx.device).unsqueeze(0)
        e = self.emb_tok(idx) + self.emb_pos(pos)
        return self.dropout(e)

    def logits_por_especialista(self, e):
        h_tx = self.tx(e)
        h_lstm = self.lstm(e)
        h_cnn = self.cnn(e)
        h_tx = self.ln_final(h_tx)
        h_lstm = self.ln_final(h_lstm)
        h_cnn = self.ln_final(h_cnn)
        logits_tx = self.decoder(h_tx)
        logits_lstm = self.decoder(h_lstm)
        logits_cnn = self.decoder(h_cnn)
        return [logits_tx, logits_lstm, logits_cnn]

    def mistura_log_probs(self, logits_lista, pesos):
        # logits_lista: list de (B,T,V); pesos: (B,T,E)
        # Converte para log-prob, mistura p = Σ_e w_e * softmax(logits_e)
        log_probs = [F.log_softmax(lg, dim=-1) for lg in logits_lista]  # lista de (B,T,V)
        log_probs_stack = torch.stack(log_probs, dim=2)  # (B,T,E,V)
        log_pesos = torch.log(pesos.clamp_min(1e-8)).unsqueeze(-1)      # (B,T,E,1)
        mistura_log_probs = torch.logsumexp(log_probs_stack + log_pesos, dim=2)  # (B,T,V)
        return mistura_log_probs

    def forward(self, idx, alvos=None):
        e = self.embeddings(idx)
        logits_lista = self.logits_por_especialista(e)
        pesos = self.gate(e)  # (B,T,E)
        log_probs_mix = self.mistura_log_probs(logits_lista, pesos)

        perda = None
        perdas_especialistas = None
        if alvos is not None:
            perda = ce_mistura_label_smoothing(log_probs_mix, alvos, self.cfg.suavizacao_rotulo)
            # perdas individuais (diagnóstico)
            perdas_especialistas = []
            for lg in logits_lista:
                lp = F.log_softmax(lg, dim=-1)
                perdas_especialistas.append(ce_label_smoothing_de_logprobs(lp, alvos, self.cfg.suavizacao_rotulo))
            perdas_especialistas = torch.stack(perdas_especialistas)  # (E,)
        return log_probs_mix, perda, perdas_especialistas, pesos

# ======================================
# Perdas (label smoothing em log-probs)
# ======================================

def ce_label_smoothing_de_logprobs(log_probs, alvos, suavizacao=0.1):
    # log_probs: (B,T,V) ; alvos: (B,T)
    nll = -log_probs.gather(dim=-1, index=alvos.unsqueeze(-1)).squeeze(-1)  # (B,T)
    perda_suave = -log_probs.mean(dim=-1)                                   # (B,T)
    perda = (1.0 - suavizacao)*nll + suavizacao*perda_suave
    return perda.mean()


def ce_mistura_label_smoothing(log_probs_mix, alvos, suavizacao=0.1):
    return ce_label_smoothing_de_logprobs(log_probs_mix, alvos, suavizacao)

# ==============================
# Otimizador + agendador (LR)
# ==============================

def criar_otimizador_e_lr(modelo: EnsembleMoE, cfg: Configuracao):
    otimizador = torch.optim.AdamW(modelo.parameters(), lr=cfg.taxa_aprendizado, weight_decay=cfg.peso_decay)
    def lr_lambda(passo):
        if passo < cfg.aquecimento_passos:
            return (passo + 1) / cfg.aquecimento_passos
        progresso = (passo - cfg.aquecimento_passos) / max(1, cfg.passos_treino - cfg.aquecimento_passos)
        return 0.5 * (1.0 + math.cos(math.pi * progresso))
    agendador = torch.optim.lr_scheduler.LambdaLR(otimizador, lr_lambda)
    return otimizador, agendador

# =====================
# Avaliação estatística
# =====================

@torch.no_grad()
def avaliar(modelo: EnsembleMoE, dados_val: torch.Tensor, cfg: Configuracao, dispositivo: str):
    modelo.eval()
    total_tokens = 0
    soma_perda_mix = 0.0
    soma_perdas_esp = torch.zeros(modelo.num_experts, device=dispositivo)

    passos = max(1, len(dados_val) // (cfg.tamanho_lote * cfg.comprimento_contexto))
    for _ in range(passos):
        x, y = lotes_aleatorios(dados_val, cfg.tamanho_lote, cfg.comprimento_contexto, dispositivo)
        log_probs_mix, perda, perdas_especialistas, _ = modelo(x, y)
        B, T = x.shape
        total_tokens += B*T
        soma_perda_mix += float(perda.item()) * B * T
        soma_perdas_esp += perdas_especialistas * (B*T)

    perda_media_mix = soma_perda_mix / max(1, total_tokens)
    ppl_mix = math.exp(min(20, perda_media_mix))
    k = sum(p.numel() for p in modelo.parameters())
    N = total_tokens
    loglik = -N * perda_media_mix
    AIC = 2*k - 2*loglik
    BIC = math.log(max(1, N)) * k - 2*loglik

    perdas_esp_medias = (soma_perdas_esp / max(1, total_tokens)).tolist()
    ppls_especialistas = [math.exp(min(20, p)) for p in perdas_esp_medias]

    return {
        'perda_mix': perda_media_mix,
        'ppl_mix': ppl_mix,
        'AIC_mix': AIC,
        'BIC_mix': BIC,
        'N': N,
        'perdas_especialistas': perdas_esp_medias,
        'ppls_especialistas': ppls_especialistas
    }

# ===============
# Rotina treino
# ===============

def treinar_modelo(cfg: Configuracao):
    dispositivo = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Treinando em: {dispositivo}")

    texto = carregar_texto(cfg)
    tok = TokenizadorChar(texto)
    ids = tok.codificar(texto)
    ids_treino, ids_val = preparar_dados(ids, cfg.proporcao_validacao)
    ids_treino = ids_treino.to(dispositivo)
    ids_val = ids_val.to(dispositivo)

    modelo = EnsembleMoE(tok.tamanho_vocab, cfg).to(dispositivo)
    otimizador, agendador = criar_otimizador_e_lr(modelo, cfg)

    melhor_val = float('inf')
    paciencia, paciencia_max = 0, 10

    inicio = time.time()
    modelo.train()
    for passo in range(cfg.passos_treino):
        x, y = lotes_aleatorios(ids_treino, cfg.tamanho_lote, cfg.comprimento_contexto, dispositivo)
        _, perda, perdas_espec, _ = modelo(x, y)

        otimizador.zero_grad(set_to_none=True)
        perda.backward()
        nn.utils.clip_grad_norm_(modelo.parameters(), cfg.clip_grad)
        otimizador.step()
        agendador.step()

        if (passo+1) % 50 == 0:
            txt = f"Passo {passo+1}/{cfg.passos_treino} - perda={perda.item():.4f} | esp=" + \
                  ",".join(f"{p.item():.3f}" for p in perdas_espec)
            print(txt)

        if (passo+1) % cfg.passos_avaliacao == 0 or passo == cfg.passos_treino-1:
            m = avaliar(modelo, ids_val, cfg, dispositivo)
            print(f"[VAL] passo={passo+1} perda_mix={m['perda_mix']:.4f} | ppl={m['ppl_mix']:.2f} | AIC={m['AIC_mix']:.0f} | BIC={m['BIC_mix']:.0f}")
            print(f"      especialistas perda={['%.3f'%p for p in m['perdas_especialistas']]} | ppl={['%.1f'%p for p in m['ppls_especialistas']]}")
            if m['perda_mix'] < melhor_val - 1e-4:
                melhor_val = m['perda_mix']
                paciencia = 0
                torch.save({
                    'estado_modelo': modelo.state_dict(),
                    'vocab': tok.vocab,
                    'cfg': cfg.__dict__,
                }, cfg.caminho_modelo)
                print(f"✔ Modelo salvo em {cfg.caminho_modelo}")
            else:
                paciencia += 1
                if paciencia >= paciencia_max:
                    print("⏹ Early stopping (sem melhora suficiente).")
                    break

    fim = time.time()
    print(f"Tempo total: {(fim - inicio):.1f}s")
    return tok

# ==============
# Geração
# ==============

@torch.no_grad()
def filtrar_top_k_top_p(probs, top_k=0, top_p=1.0):
    if top_k > 0:
        v, _ = torch.topk(probs, k=min(top_k, probs.size(-1)))
        min_topk = v[0, -1]
        probs = torch.where(probs >= min_topk, probs, torch.zeros_like(probs))
    if top_p < 1.0:
        ordenado, indices = torch.sort(probs, descending=True)
        cumul = torch.cumsum(ordenado, dim=-1)
        mascara = cumul <= top_p
        mascara[..., 0] = True
        filtrado = torch.zeros_like(probs)
        filtrado[0, indices[0, mascara[0]]] = probs[0, indices[0, mascara[0]]]
        probs = filtrado
    probs = probs / probs.sum(dim=-1, keepdim=True)
    return probs

@torch.no_grad()
def gerar_texto(modelo: EnsembleMoE, tok: TokenizadorChar, prompt: str, cfg: Configuracao, dispositivo: str, mc_dropout_passes: int = 0):
    # Ativa dropout para MC se solicitado
    treino_original = modelo.training
    if mc_dropout_passes > 0:
        modelo.train()
    else:
        modelo.eval()

    ids = tok.codificar(prompt).to(dispositivo)
    if ids.numel() == 0:
        ids = torch.zeros((1,1), dtype=torch.long, device=dispositivo)
    else:
        ids = ids[-cfg.comprimento_contexto:].unsqueeze(0)

    repeticao_mem = {}

    for _ in range(cfg.max_novos_tokens):
        idx_cond = ids[:, -cfg.comprimento_contexto:]
        e = modelo.embeddings(idx_cond)
        logits_lista = modelo.logits_por_especialista(e)
        pesos = modelo.gate(e)  # (B,T,E)
        log_probs_mix = modelo.mistura_log_probs(logits_lista, pesos)
        log_probs = log_probs_mix[:, -1, :]  # (1,V)

        # MC Dropout: média por passes
        if mc_dropout_passes > 0:
            acum = log_probs.clone()
            for _m in range(mc_dropout_passes-1):
                e = modelo.embeddings(idx_cond)
                logits_lista = modelo.logits_por_especialista(e)
                pesos = modelo.gate(e)
                lp = modelo.mistura_log_probs(logits_lista, pesos)[:, -1, :]
                acum += lp
            log_probs = acum / mc_dropout_passes

        # penalidade de repetição
        lp = log_probs.clone()
        for i, cont in repeticao_mem.items():
            if cont > 0:
                lp[0, i] /= cfg.penalidade_repeticao

        # temperatura
        lp = lp / max(1e-8, cfg.temperatura)
        probs = torch.softmax(lp, dim=-1)
        probs = filtrar_top_k_top_p(probs, cfg.top_k, cfg.top_p)
        idx_prox = torch.multinomial(probs, num_samples=1)
        ids = torch.cat([ids, idx_prox], dim=1)
        i = int(idx_prox.item())
        repeticao_mem[i] = repeticao_mem.get(i, 0) + 1

    if not treino_original:
        modelo.eval()
    return tok.decodificar(ids[0].tolist())

# ==============
# Checkpoint IO
# ==============

def carregar_modelo(cfg: Configuracao, dispositivo: str):
    ckpt = torch.load(cfg.caminho_modelo, map_location=dispositivo)
    vocab = ckpt['vocab']
    tok = TokenizadorChar("".join(vocab))
    tok.vocab = vocab
    tok.tok2id = {ch:i for i,ch in enumerate(vocab)}
    tok.id2tok = {i:ch for ch,i in tok.tok2id.items()}
    modelo = EnsembleMoE(len(vocab), cfg).to(dispositivo)
    modelo.load_state_dict(ckpt['estado_modelo'])
    return modelo, tok

# ======
# CLI
# ======

CFG = Configuracao()

def main():
    parser = argparse.ArgumentParser(description="Rede Neural MoE (Transformer+LSTM+CNN) para aprender a escrever")
    parser.add_argument("--treinar", action="store_true", help="Treinar a partir de corpus.txt")
    parser.add_argument("--gerar", type=str, default=None, help="Prompt inicial para gerar texto")
    parser.add_argument("--max_tokens", type=int, default=None, help="Sobrescreve o tamanho máximo de geração")
    parser.add_argument("--mc", type=int, default=0, help="Passes MC Dropout na geração (0 desliga)")
    args = parser.parse_args()

    definir_semente(CFG.semente)
    dispositivo = 'cuda' if torch.cuda.is_available() else 'cpu'

    tok = None
    if args.treinar:
        tok = treinar_modelo(CFG)

    if args.gerar is not None:
        if not os.path.exists(CFG.caminho_modelo) and not args.treinar:
            raise SystemExit("Você precisa treinar primeiro (ou fornecer um modelo salvo).")
        if tok is None:
            modelo, tok = carregar_modelo(CFG, dispositivo)
        else:
            modelo, _ = carregar_modelo(CFG, dispositivo)

        if args.max_tokens is not None:
            CFG.max_novos_tokens = args.max_tokens
        if args.mc is not None:
            CFG.amostras_mc_dropout = args.mc

        texto = gerar_texto(modelo, tok, args.gerar, CFG, dispositivo, mc_dropout_passes=CFG.amostras_mc_dropout)
        print("\n================= GERADO =================\n")
        print(texto)
        print("\n==========================================\n")

if __name__ == "__main__":
    main()