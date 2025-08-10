# Bruxinha vs Demônios (Pygame)

Projeto completo gerado automaticamente (sprites pixel‑art procedurais + código).

## Como rodar
1. Instale o Python 3.10+ e o Pygame:
   ```
   pip install pygame
   ```
2. Execute:
   ```
   python jogo.py
   ```

## Controles
- A/D ou ←/→ : mover
- W/↑/Espaço : pular
- J ou Z      : atirar
- ESC         : sair

## Notas
- Os sprites foram gerados por código (Pillow) e salvos em `assets/`.
- O jogo usa superfícies com mistura de alpha para criar iluminação/ sombras, partículas,
  câmera com *easing* + *shake* e animações baseadas em tempo (delta‑time).
