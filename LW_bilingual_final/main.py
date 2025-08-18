import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CANAL_PREVIAS = os.getenv("CANAL_PREVIAS", "https://t.me/laylaweberoficial")
CANAL_VIP = os.getenv("CANAL_VIP", "https://t.me/+8hLKmZ6JQbQwYWEx")
PIX_URL = os.getenv("PUSHINPAY_URL")

WELCOME_MSG = (
    "😈 *Entre nós… já sei o que você veio buscar…* 😏🔥\n\n"
    "Escolha abaixo sua forma de acesso:"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("1️⃣ Pagamento via Pix | Pay with Pix", url=PIX_URL)],
        [InlineKeyboardButton("2️⃣ Pagamento via Cartão/PayPal Internacional | Pay with Card/PayPal", url="https://paymentwall.com")],
        [InlineKeyboardButton("3️⃣ Acesso ao grupo de prévias | Access preview group", url=CANAL_PREVIAS)],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(WELCOME_MSG, parse_mode="Markdown", reply_markup=reply_markup)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
