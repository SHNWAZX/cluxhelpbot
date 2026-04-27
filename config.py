# ============================================================
# config.py — Centralised configuration loader
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv()

# ── Required ──────────────────────────────────────────────
API_ID      = int(os.getenv("API_ID", 0))
API_HASH    = os.getenv("API_HASH", "")
BOT_TOKEN   = os.getenv("BOT_TOKEN", "")
MONGO_URI   = os.getenv("MONGO_URI", "")
DB_NAME     = os.getenv("DB_NAME", "BotDB")

# ── Owner / sudo ──────────────────────────────────────────
OWNER_ID    = int(os.getenv("OWNER_ID", 0))
_sudo_raw   = os.getenv("SUDO_USERS", "")
SUDO_USERS  = set(int(x) for x in _sudo_raw.split() if x.isdigit())
SUDO_USERS.add(OWNER_ID)

# ── Bot meta ──────────────────────────────────────────────
BOT_USERNAME   = os.getenv("BOT_USERNAME", "MyGroupBot")
SUPPORT_GROUP  = os.getenv("SUPPORT_GROUP", "https://t.me/")
UPDATE_CHANNEL = os.getenv("UPDATE_CHANNEL", "https://t.me/")
START_IMAGE    = os.getenv("START_IMAGE", "")

# ── Render / Webhook ──────────────────────────────────────
PORT        = int(os.getenv("PORT", 8000))
WEBHOOK     = os.getenv("WEBHOOK", "False").lower() == "true"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
