# LW Telegram Bot — Bilíngue (PT/EN)

Bot simples com 3 botões e mensagem bilíngue:

1. **Pix • Pay with Pix**
2. **Cartão/PayPal • Card/PayPal** (texto sem “Ko‑fi”, mas você usa a URL do Ko‑fi no `.env`)
3. **Grupo de prévias • Previews channel**

---

## 1) Requisitos
- Python 3.10+
- Uma conta de bot no Telegram (token do **@BotFather**)

---

## 2) Configuração do `.env`
Crie um arquivo chamado `.env` na pasta do projeto com os valores reais:

```env
BOT_TOKEN=8477222113:AAEJSxCflHY-N7z9vCETOnMV8biGjb5b9AM
CANAL_PREVIAS=https://t.me/laylaweberoficial
# Um dos dois abaixo (o código aceita os dois; se os dois existirem ele usa PIX_URL)
PIX_URL=https://app.pushinpay.com.br/service/pay/9F8C1DED-E749-434E-AA32-64F8B8044B5D
PUSHINPAY_URL=https://app.pushinpay.com.br/service/pay/9F8C1DED-E749-434E-AA32-64F8B8044B5D
# Link do checkout internacional (Ko‑fi/Stripe/qualquer outro)
KOFI_URL=https://ko-fi.com/s/2e0c36885a
```

> **Importante:** o `.env` não deve ir para o GitHub. Garanta que existe `.gitignore` com a linha `.env`.

---

## 3) Rodar localmente
```bat
cd C:\Users\rbgli\Desktop\LW
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Abra o Telegram e envie `/start` para o seu bot.

---

## 4) Publicar no GitHub
```bat
cd C:\Users\rbgli\Desktop\LW
git add .
git commit -m "bilingue: mensagem e botoes"
git push
```

---

## 5) Deploy no Render (24/7)

### Opção A — Blueprint (se você tem `render.yaml` no repo)
1. Render → **New + → Blueprint** → selecione `rbglinss/lw-telegram-bot` (`main`)  
2. Depois que criar o serviço (tipo **Worker**), adicione as **Environment Variables** em *Settings → Environment*:

```
BOT_TOKEN=8477222113:AAEJSxCflHY-N7z9vCETOnMV8biGjb5b9AM
CANAL_PREVIAS=https://t.me/laylaweberoficial
PIX_URL=https://app.pushinpay.com.br/service/pay/9F8C1DED-E749-434E-AA32-64F8B8044B5D
PUSHINPAY_URL=https://app.pushinpay.com.br/service/pay/9F8C1DED-E749-434E-AA32-64F8B8044B5D
KOFI_URL=https://ko-fi.com/s/2e0c36885a
```

3. **Build Command:** `pip install -r requirements.txt`  
   **Start Command:** `python main.py`  
4. Veja os **Logs**: “*Bot inicializado. Aguardando mensagens...*”.

### Opção B — Manual (Background Worker)
1. Render → **New + → Background Worker** → conecte ao repo e branch `main`  
2. **Build:** `pip install -r requirements.txt`  
   **Start:** `python main.py`  
3. Adicione as mesmas **Environment Variables** acima e salve.

---

## 6) Dicas & Troubleshooting
- Teste rápido das variáveis carregadas (no prompt com venv ativo):
  ```bat
  python -c "import os;from dotenv import load_dotenv;load_dotenv();print({k:bool(os.getenv(k)) for k in ['BOT_TOKEN','PIX_URL','PUSHINPAY_URL','KOFI_URL','CANAL_PREVIAS']})"
  ```
- Se o token estiver errado, `https://api.telegram.org/botSEU_TOKEN/getMe` não retorna `"ok": true`.
- Só rode **uma instância** por vez (local **ou** Render) durante testes.
- Se mudar o código e fizer `git push`, com **Auto Deploy ON** o Render redeploya sozinho.
