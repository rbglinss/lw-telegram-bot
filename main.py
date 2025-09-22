import logging
import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

BOT_TOKEN     = os.getenv("BOT_TOKEN")
CANAL_PREVIAS = os.getenv("CANAL_PREVIAS")
PIX_URL       = os.getenv("PIX_URL") or os.getenv("PUSHINPAY_URL")
CARD_URL      = os.getenv("CARD_URL")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN não definido.")
if not CANAL_PREVIAS:
    raise RuntimeError("CANAL_PREVIAS não definido.")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
log = logging.getLogger("laylabot")

WELCOME_PT = (
    "😈 *Entre nós… já sei o que você veio buscar…* 😏🔥\n\n"
    "Escolha abaixo sua forma de acesso:"
)
WELCOME_EN = (
    "😈 *Between us… I already know what you came for…* 😏🔥\n\n"
    "Choose your access method below:"
)

def make_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    if PIX_URL:
        buttons.append([InlineKeyboardButton("1️⃣ Pagamento via Pix | Pay with Pix", url=PIX_URL)])
    if CARD_URL:
        buttons.append([InlineKeyboardButton("2️⃣ Pagamento via Cartão/PayPal Internacional | Pay with Card/PayPal", url=CARD_URL)])
    buttons.append([InlineKeyboardButton("3️⃣ Acesso ao grupo de prévias | Access preview group", url=CANAL_PREVIAS)])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"{WELCOME_PT}\n\n{WELCOME_EN}"
    await update.effective_chat.send_message(text=text, reply_markup=make_keyboard(), parse_mode="Markdown")

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))

    log.info("Iniciando bot em long polling (Render Background Worker)...")
    await app.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
