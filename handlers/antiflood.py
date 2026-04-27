# ============================================================
# handlers/antiflood.py — Anti-flood protection
# ============================================================
from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from handlers.group_commands import is_admin
import db


def register_antiflood(app: Client):

    @app.on_message(filters.group & filters.command("setflood"))
    async def setflood_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ Usage: `/setflood <number>` or `/setflood off`")
        arg = parts[1].lower()
        if arg == "off":
            await db.set_flood_limit(message.chat.id, 0)
            return await message.reply_text("✅ Anti-flood **disabled**.")
        if not arg.isdigit() or int(arg) < 2:
            return await message.reply_text("⚠️ Please provide a number ≥ 2.")
        limit = int(arg)
        await db.set_flood_limit(message.chat.id, limit)
        await message.reply_text(f"✅ Anti-flood set to **{limit}** messages.")

    @app.on_message(filters.group & filters.command("flood"))
    async def flood_cmd(client, message: Message):
        limit = await db.get_flood_limit(message.chat.id)
        if limit == 0:
            await message.reply_text("🌊 Anti-flood is currently **disabled**.")
        else:
            await message.reply_text(f"🌊 Anti-flood limit: **{limit}** messages.")

    @app.on_message(filters.group & ~filters.service, group=4)
    async def enforce_flood(client, message: Message):
        if not message.from_user:
            return
        if await is_admin(client, message.chat.id, message.from_user.id):
            await db.reset_flood(message.chat.id, message.from_user.id)
            return
        should_ban = await db.update_flood(message.chat.id, message.from_user.id)
        if should_ban:
            try:
                await client.restrict_chat_member(
                    message.chat.id,
                    message.from_user.id,
                    ChatPermissions(can_send_messages=False),
                )
                await message.reply_text(
                    f"🌊 **{message.from_user.first_name}** was muted for flooding!"
                )
            except Exception:
                pass
