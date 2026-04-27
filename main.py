# ============================================================
# main.py — Entry point (Pyrogram + Render-ready webhook)
# ============================================================
import asyncio
import logging
from aiohttp import web
from pyrogram import Client
from config import (
    API_ID, API_HASH, BOT_TOKEN,
    PORT, WEBHOOK, WEBHOOK_URL,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app = Client(
    "group_manager_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# ── Register all handlers ────────────────────────────────────
from handlers import register_all_handlers
register_all_handlers(app)

# ── Render keep-alive HTTP server ────────────────────────────
async def health(request):
    return web.Response(text="OK")

async def run_web_server():
    """Lightweight HTTP server so Render marks the service healthy."""
    server = web.Application()
    server.router.add_get("/", health)
    server.router.add_get("/health", health)
    runner = web.AppRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logger.info("✅ Health server running on port %s", PORT)

async def main():
    logger.info("🚀 Starting bot...")
    await run_web_server()
    async with app:
        logger.info("✅ Bot is running (long-polling)...")
        await asyncio.Event().wait()   # run forever

if __name__ == "__main__":
    asyncio.run(main())
