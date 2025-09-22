# LaylaBot — Versão Worker (Render)

Bot Telegram bilíngue (PT/EN) com botões:
1) Pix (PushinPay)
2) Cartão/PayPal (opcional, se definir CARD_URL)
3) Canal de prévias

## Variáveis de Ambiente (Render → Settings → Environment)
- BOT_TOKEN   (obrigatório)
- CANAL_PREVIAS  (obrigatório)
- PIX_URL     (obrigatório)
- CARD_URL    (opcional)

## Start/Build Commands (Render – Background Worker)
- Build: `pip install -r requirements.txt`
- Start: `python main.py`
