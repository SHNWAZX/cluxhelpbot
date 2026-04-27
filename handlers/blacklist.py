# ============================================================
# handlers/blacklist.py — Word blacklist with auto-delete
# ============================================================
from pyrogram import Client, filters
from pyrogram.types import Message
from handlers.group_commands import is_admin
import db


def register_blacklist(app: Client):

    @app.on_message(filters.group & filters.command("addblacklist"))
    async def add_blacklist(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ Usage: `/addblacklist <word1> [word2] ...`")
        words = parts[1].lower().split()
        for word in words:
            await db.add_blacklist_word(message.chat.id, word)
        await message.reply_text(f"✅ Added **{len(words)}** word(s) to blacklist.")

    @app.on_message(filters.group & filters.command("rmblacklist"))
    async def rm_blacklist(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ Usage: `/rmblacklist <word>`")
        removed = await db.remove_blacklist_word(message.chat.id, parts[1].lower())
        if removed:
            await message.reply_text(f"✅ `{parts[1]}` removed from blacklist.")
        else:
            await message.reply_text(f"❌ `{parts[1]}` not found in blacklist.")

    @app.on_message(filters.group & filters.command("blacklist"))
    async def list_blacklist(client, message: Message):
        words = await db.get_blacklist(message.chat.id)
        if not words:
            return await message.reply_text("🚫 No blacklisted words in this group.")
        listed = "\n".join(f"• `{w}`" for w in words)
        await message.reply_text(f"🚫 **Blacklisted Words:**\n{listed}")

    @app.on_message(filters.group & ~filters.service, group=2)
    async def enforce_blacklist(client, message: Message):
        if not message.from_user or not message.text:
            return
        if await is_admin(client, message.chat.id, message.from_user.id):
            return
        words = await db.get_blacklist(message.chat.id)
        if not words:
            return
        msg_lower = message.text.lower()
        for word in words:
            if word in msg_lower:
                try:
                    await message.delete()
                    await client.send_message(
                        message.chat.id,
                        f"⚠️ Message by [{message.from_user.first_name}](tg://user?id={message.from_user.id}) "
                        f"deleted — contained blacklisted word.",
                    )
                except Exception:
                    pass
                return
