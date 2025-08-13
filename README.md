# Go 19×19 — Autor: Luiz Tiago Wilcke

> **Autoria confirmada:** Este projeto foi desenvolvido por **Luiz Tiago Wilcke**.  
> O arquivo `index.html` traz o nome do autor no título e na interface do jogo.

## Visão geral
Jogo de **Go 19×19** totalmente funcional, feito em **HTML + CSS + JavaScript**.  
Você joga de **brancas**; a IA joga de **pretas** e realiza jogadas com **MCTS/UCT** (Monte Carlo Tree Search) e heurísticas:
capturas imediatas, fuga/pressão de *atari*, evitar suicídio e evitar preencher olhos próprios; *rollout* semi-aleatório com
viés posicional.

## Como executar
1. Baixe o ZIP deste repositório ou da pasta gerada.
2. Extraia os arquivos.
3. Abra `index.html` em qualquer navegador moderno (Chrome, Edge, Firefox). Não precisa de servidor.

## Controles
- **Clique** em uma interseção vazia para jogar com **brancas**.
- **Passar**: botão *Passar* (duas passadas consecutivas encerram a partida).
- **Nova partida**: reinicia o jogo.
- **Pontuar**: mostra a pontuação por **área (regras chinesas)** com **komi 6.5** para brancas.

## Ajustes da IA
- **Tempo da IA (ms)**: orçamento de busca/rollouts.
- **Exploração UCT (c)**: controla exploração vs. exploração na UCT (padrão 1.20).

## Regras implementadas
- Tamanho: **19×19**.
- **Ko simples** (não repete a posição anterior).
- **Suicídio proibido** (exceto quando captura).
- **Pontuação por área**; **komi 6.5** para brancas.

## Estrutura
```
go19x19-ltw/
├─ index.html   # jogo completo
└─ README.md    # este arquivo
```

## Publicar no GitHub
```bash
git init
git add .
git commit -m "Go 19x19 — Autor: Luiz Tiago Wilcke (MCTS/UCT)"
git branch -M main
git remote add origin https://github.com/<seu-usuario>/<seu-repo>.git
git push -u origin main
```

## Créditos
- **Autor**: Luiz Tiago Wilcke
- Tabuleiro desenhado em **CSS**, pedras com gradientes e relevo, grid 19×19.
- IA: **MCTS/UCT** em JavaScript com heurísticas de captura/atari/olhos e *rollouts* semi-aleatórios.

---
© 2025 Luiz Tiago Wilcke. Todos os direitos reservados.
