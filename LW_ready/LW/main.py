import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load .env (locally). On Render, use environment variables.
load_dotenv()

BOT_TOKEN      = os.getenv("BOT_TOKEN")
CANAL_PREVIAS  = os.getenv("CANAL_PREVIAS", "https://t.me/laylaweberoficial")
# Accept both names, prefers PIX_URL; falls back to PUSHINPAY_URL
PIX_URL        = os.getenv("PIX_URL") or os.getenv("PUSHINPAY_URL")
KOFI_URL       = os.getenv("KOFI_URL")

WELCOME_MSG = (
    "😈 *Entre nós… já sei o que você veio buscar…* 😏🔥\n\n"
    "Escolha abaixo como deseja acessar:\n\n"
    "1️⃣ Pagamento via *Pix* (PushinPay)\n"
    "2️⃣ Pagamento via *Cartão/PayPal Internacional* (Ko-fi)\n"
    "3️⃣ Acesso ao grupo de prévias\n\n"
    "---\n"
    "*EN*\n"
    "Choose how you want to proceed:\n"
    "1️⃣ *Pix* (Brazil)\n"
    "2️⃣ *Card/PayPal* (Ko-fi, international)\n"
    "3️⃣ *Previews* channel\n"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    if PIX_URL:
        keyboard.append([InlineKeyboardButton("💳 Pagar via Pix (Brasil)", url=PIX_URL)])
    if KOFI_URL:
        keyboard.append([InlineKeyboardButton("🌎 Cartão/PayPal (Ko-fi)", url=KOFI_URL)])
    keyboard.append([InlineKeyboardButton("👀 Grupo de prévias", url=CANAL_PREVIAS)])

    await update.message.reply_text(
        WELCOME_MSG,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN não encontrado. Defina no .env ou nas variáveis de ambiente.")
    if not (PIX_URL and KOFI_URL):
        logger.warning("Atenção: PIX_URL/PUSHINPAY_URL e/ou KOFI_URL não definidos; verifique seu .env.")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    logger.info("Bot inicializado. Aguardando mensagens...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()