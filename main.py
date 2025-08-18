import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Load env vars
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PIX_URL = os.getenv("PIX_URL") or os.getenv("PUSHINPAY_URL")
KOFI_URL = os.getenv("KOFI_URL")
CANAL_PREVIAS = os.getenv("CANAL_PREVIAS", "https://t.me/laylaweberoficial")

# Bilingual welcome
START_MESSAGE = (
    "😈 *Entre nós... já sei o que você veio buscar...* 😏🔥\n"
    "*(EN) Between us... I already know what you came for...* 😏🔥\n\n"
    "Escolha abaixo sua forma de acesso:\n"
    "*(EN) Choose your access method below:*"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    if PIX_URL:
        keyboard.append([InlineKeyboardButton("1️⃣ Pagamento via Pix | Pay with Pix", url=PIX_URL)])
    if KOFI_URL:
        keyboard.append([InlineKeyboardButton("2️⃣ Pagamento via Cartão/PayPal Internacional | Pay with Card/PayPal", url=KOFI_URL)])
    keyboard.append([InlineKeyboardButton("3️⃣ Acesso ao grupo de prévias | Access preview group", url=CANAL_PREVIAS)])
    await update.message.reply_text(START_MESSAGE, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN não encontrado. Crie o .env ou defina no ambiente." )
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot inicializado. Aguardando mensagens...")
    app.run_polling()

if __name__ == "__main__":
    main()
