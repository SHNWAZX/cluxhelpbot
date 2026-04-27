# ============================================================
# handlers/rules.py — /rules, /setrules, /clearrules
# ============================================================
from pyrogram import Client, filters
from pyrogram.types import Message
from handlers.group_commands import is_admin
import db


def register_rules(app: Client):

    @app.on_message(filters.group & filters.command("rules"))
    async def rules_cmd(client, message: Message):
        text = await db.get_rules(message.chat.id)
        if not text:
            return await message.reply_text("📜 No rules have been set for this group.")
        await message.reply_text(f"📜 **Group Rules:**\n\n{text}")

    @app.on_message(filters.group & filters.command("setrules"))
    async def setrules_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ Usage: `/setrules <rules text>`")
        await db.set_rules(message.chat.id, parts[1])
        await message.reply_text("✅ Rules updated!")

    @app.on_message(filters.group & filters.command("clearrules"))
    async def clearrules_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        await db.clear_rules(message.chat.id)
        await message.reply_text("🗑 Rules cleared.")
