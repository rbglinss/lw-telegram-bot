import asyncio
import logging
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

# -------------------------
# ENV
# -------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")

CANAL_PREVIAS = os.getenv("CANAL_PREVIAS")
PIX_URL = os.getenv("PIX_URL") or os.getenv("PUSHINPAY_URL")
CARD_URL = os.getenv("CARD_URL")  # Ko-fi (internacional)

# Grupo VIP (tem que ser um GRUPO, não canal)
VIP_GROUP_ID = os.getenv("VIP_GROUP_ID")  # ex: -1001234567890

# Segurança do webhook (use um token longo)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# Admins que podem usar comandos de suporte
ADMIN_IDS = os.getenv("ADMIN_IDS", "")  # ex: "123,456"

# Porta para rodar (Render Web Service)
PORT = int(os.getenv("PORT", "10000"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN não definido.")
if not CANAL_PREVIAS:
    raise RuntimeError("CANAL_PREVIAS não definido.")
if not VIP_GROUP_ID:
    raise RuntimeError("VIP_GROUP_ID não definido (ID do grupo VIP).")
if not WEBHOOK_SECRET:
    raise RuntimeError("WEBHOOK_SECRET não definido (protege seus webhooks).")

VIP_GROUP_ID_INT = int(VIP_GROUP_ID)

ADMIN_ID_SET = set()
for x in ADMIN_IDS.split(","):
    x = x.strip()
    if x.isdigit():
        ADMIN_ID_SET.add(int(x))

# -------------------------
# LOG
# -------------------------
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("laylabot")

# -------------------------
# DB (SQLite)
# -------------------------
DB_PATH = os.getenv("DB_PATH", "data.db")


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db():
    conn = db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              email TEXT NOT NULL,
              source TEXT NOT NULL,
              status TEXT NOT NULL,
              paid_at TEXT NOT NULL,
              expires_at TEXT NOT NULL,
              meta TEXT
            );
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_payments_email_status
            ON payments(email, status);
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memberships (
              user_id INTEGER PRIMARY KEY,
              email TEXT NOT NULL,
              added_at TEXT NOT NULL,
              expires_at TEXT NOT NULL
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def dt_to_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def iso_to_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def normalize_email(email: str) -> str:
    return email.strip().lower()


def upsert_payment(email: str, source: str, status: str, days: int = 30, meta: Optional[str] = None):
    email = normalize_email(email)
    paid_at = now_utc()
    expires_at = paid_at + timedelta(days=days)

    conn = db()
    try:
        conn.execute(
            """
            INSERT INTO payments (email, source, status, paid_at, expires_at, meta)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (email, source, status, dt_to_iso(paid_at), dt_to_iso(expires_at), meta),
        )
        conn.commit()
    finally:
        conn.close()


def get_active_payment(email: str) -> Optional[dict]:
    email = normalize_email(email)
    conn = db()
    try:
        cur = conn.execute(
            """
            SELECT id, email, source, status, paid_at, expires_at
            FROM payments
            WHERE email = ? AND status = 'paid'
            ORDER BY id DESC
            LIMIT 1;
            """,
            (email,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "email": row[1],
            "source": row[2],
            "status": row[3],
            "paid_at": row[4],
            "expires_at": row[5],
        }
    finally:
        conn.close()


def set_membership(user_id: int, email: str, expires_at_iso: str):
    conn = db()
    try:
        conn.execute(
            """
            INSERT INTO memberships (user_id, email, added_at, expires_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
              email=excluded.email,
              expires_at=excluded.expires_at;
            """,
            (user_id, normalize_email(email), dt_to_iso(now_utc()), expires_at_iso),
        )
        conn.commit()
    finally:
        conn.close()


def get_expired_memberships(limit: int = 200):
    conn = db()
    try:
        cur = conn.execute(
            """
            SELECT user_id, expires_at
            FROM memberships
            WHERE expires_at <= ?
            LIMIT ?;
            """,
            (dt_to_iso(now_utc()), limit),
        )
        return cur.fetchall()
    finally:
        conn.close()


def delete_membership(user_id: int):
    conn = db()
    try:
        conn.execute("DELETE FROM memberships WHERE user_id = ?;", (user_id,))
        conn.commit()
    finally:
        conn.close()


# -------------------------
# Telegram UI
# -------------------------
WELCOME_PT = (
    "Olá! Eu sou o LaylaWeberBot.\n\n"
    "Escolha uma opção abaixo ou envie /links para ver os atalhos.\n"
    "Para acesso VIP, efetue o pagamento e depois use /vip."
)
WELCOME_EN = (
    "Hi! I'm LaylaWeberBot.\n\n"
    "Choose an option below or type /links to see shortcuts.\n"
    "For VIP access, complete payment and then use /vip."
)


def make_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    if PIX_URL:
        buttons.append([InlineKeyboardButton("1) Pagamento via Pix", url=PIX_URL)])
    if CARD_URL:
        buttons.append([InlineKeyboardButton("2) Cartão/PayPal (Ko-fi)", url=CARD_URL)])
    buttons.append([InlineKeyboardButton("3) Grupo de prévias", url=CANAL_PREVIAS)])
    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"{WELCOME_PT}\n\n{WELCOME_EN}"
    await update.effective_chat.send_message(
        text=text, reply_markup=make_keyboard()
    )


async def links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message(
        text="Atalhos:\n/vip  , liberar acesso VIP (após pagamento)\n/links  , ver botões",
        reply_markup=make_keyboard(),
    )


# -------------------------
# VIP flow (no bot)
# -------------------------
VIP_PROMPT = (
    "Para liberar o VIP, envie seu e-mail usado no pagamento.\n"
    "Exemplo: seuemail@gmail.com"
)


async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["vip_waiting_email"] = True
    await update.effective_chat.send_message(VIP_PROMPT)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "").strip()

    if context.user_data.get("vip_waiting_email"):
        context.user_data["vip_waiting_email"] = False

        email = normalize_email(txt)
        if not EMAIL_RE.match(email):
            await update.effective_chat.send_message("E-mail inválido. Envie novamente com /vip.")
            return

        pay = get_active_payment(email)
        if not pay:
            await update.effective_chat.send_message(
                "Não encontrei pagamento aprovado para esse e-mail.\n"
                "Confirme se usou o mesmo e-mail da compra e tente /vip novamente."
            )
            return

        expires_at = iso_to_dt(pay["expires_at"])
        if expires_at <= now_utc():
            await update.effective_chat.send_message(
                "Seu acesso aparece como expirado. Se você renovou hoje, aguarde 2 minutos e tente /vip."
            )
            return

        user_id = update.effective_user.id

        # 1) cria link 1 uso, expira em 10 minutos (evita repasse)
        expire_link_at = int((now_utc() + timedelta(minutes=10)).timestamp())
        invite = await context.bot.create_chat_invite_link(
            chat_id=VIP_GROUP_ID_INT,
            member_limit=1,
            expire_date=expire_link_at,
            creates_join_request=False,
            name=f"vip_{user_id}",
        )

        # 2) registra no banco, 30 dias a partir do pagamento
        set_membership(user_id=user_id, email=email, expires_at_iso=pay["expires_at"])

        await update.effective_chat.send_message(
            "Seu acesso VIP está liberado.\n\n"
            "Clique no link abaixo para entrar (uso único e expira em 10 min):\n"
            f"{invite.invite_link}\n\n"
            "Se der erro, envie /vip novamente."
        )
        return

    # fallback simples
    await start(update, context)


# -------------------------
# Remoção automática após expirar
# -------------------------
async def kick_expired_memberships(context: ContextTypes.DEFAULT_TYPE):
    rows = get_expired_memberships(limit=200)
    if not rows:
        return

    for (user_id, _) in rows:
        try:
            # tenta banir e desbanir para efetivar remoção
            await context.bot.ban_chat_member(chat_id=VIP_GROUP_ID_INT, user_id=user_id)
            await context.bot.unban_chat_member(chat_id=VIP_GROUP_ID_INT, user_id=user_id)
        except Exception as e:
            log.warning(f"Falha ao remover user_id={user_id}: {e}")
        finally:
            delete_membership(user_id)


# -------------------------
# Webhook de pagamento (unifica tudo)
# Você pode usar Kirvano, PushinPay, Ko-fi via Make/n8n e mandar pra cá.
# -------------------------
api = FastAPI()


@api.post("/payment")
async def payment_webhook(
    request: Request,
    x_webhook_secret: str = Header(default=""),
):
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="unauthorized")

    data = await request.json()

    # Esperado (padronizado via Make/n8n):
    # {
    #   "email": "buyer@email.com",
    #   "status": "paid",
    #   "source": "kirvano|pushinpay|kofi",
    #   "days": 30,
    #   "meta": "opcional"
    # }
    email = normalize_email(str(data.get("email", "")).strip())
    status = str(data.get("status", "")).strip().lower()
    source = str(data.get("source", "")).strip().lower() or "unknown"
    days = int(data.get("days", 30))
    meta = str(data.get("meta", "")) if data.get("meta") is not None else None

    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="invalid email")
    if status not in {"paid", "refunded", "chargeback"}:
        raise HTTPException(status_code=400, detail="invalid status")

    if status == "paid":
        upsert_payment(email=email, source=source, status="paid", days=days, meta=meta)
        return {"ok": True, "saved": True}

    # statuses negativos (opcional): registra como não pago
    upsert_payment(email=email, source=source, status=status, days=0, meta=meta)
    return {"ok": True, "saved": True}


@api.get("/health")
async def health():
    return {"ok": True}


# -------------------------
# Start everything
# -------------------------
def build_bot_app() -> Application:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("links", links))
    app.add_handler(CommandHandler("vip", vip))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # job de expiração (roda a cada 10 min)
    app.job_queue.run_repeating(kick_expired_memberships, interval=600, first=60)

    return app


async def run_bot_polling(app: Application):
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    log.info("Bot rodando em polling.")
    # mantém vivo
    while True:
        await asyncio.sleep(3600)


async def run_api():
    import uvicorn

    config = uvicorn.Config(
        api,
        host="0.0.0.0",
        port=PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)
    log.info(f"API rodando em :{PORT}")
    await server.serve()


async def main():
    init_db()
    bot_app = build_bot_app()
    await asyncio.gather(
        run_bot_polling(bot_app),
        run_api(),
    )


if __name__ == "__main__":
    asyncio.run(main())
