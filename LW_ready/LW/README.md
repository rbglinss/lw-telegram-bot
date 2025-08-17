# LW Telegram Bot (Pix + Ko-fi)

Bot simples em Python com três botões: Pix (PushinPay), Ko-fi (cartão/PayPal) e canal de prévias.

## Arquivos
- `main.py` — código do bot
- `requirements.txt` — dependências
- `.env` — **já preenchido com seus valores reais** (NÃO COMMITAR)
- `.env.example` — modelo vazio (para o GitHub)
- `.gitignore` — evita subir `.env`

## Rodando localmente (Windows)
```bat
cd C:\Users\rbgli\Desktop\LW
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## GitHub (repositório rbglinss/lw-telegram-bot)
```bat
cd C:\Users\rbgli\Desktop\LW
git init
git add .
git commit -m "Bot LW - inicial"
git branch -M main
git remote add origin https://github.com/rbglinss/lw-telegram-bot.git
git push -u origin main
```

## Render (Background Worker 24/7)
- **Build:** `pip install -r requirements.txt`
- **Start:** `python main.py`
- **Environment Variables:**
  - `BOT_TOKEN=8477222113:AAEJSxCflHY-N7z9vCETOnMV8biGjb5b9AM`
  - `CANAL_PREVIAS=https://t.me/laylaweberoficial`
  - `PIX_URL=https://app.pushinpay.com.br/service/pay/9F8C1DED-E749-434E-AA32-64F8B8044B5D`
  - `KOFI_URL=https://ko-fi.com/s/2e0c36885a`
```

## Observações
- No `.env`, o código aceita **PIX_URL** e também **PUSHINPAY_URL** como alternativa.
- Nunca suba o `.env` para o GitHub.
