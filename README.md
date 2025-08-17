# Layla VIP Telegram Bot

Este repositório contém um bot simples de Telegram configurado com três botões:
1) Pix (PushinPay) — Brasil
2) Cartão/PayPal (Ko-fi) — Internacional
3) Canal de Prévias — Telegram

## Variáveis de ambiente (arquivo .env)
- BOT_TOKEN
- CANAL_PREVIAS
- (Opcional) CANAL_VIP
- PIX_URL
- KOFI_URL

## Executar localmente (Windows)
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Deploy (Render | Background Worker)
- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py`
- Defina as mesmas variáveis de ambiente no painel do Render.
