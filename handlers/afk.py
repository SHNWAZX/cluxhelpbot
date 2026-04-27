# ============================================================
# handlers/afk.py — AFK system (from Rose-Bot, MongoDB version)
# ============================================================
from pyrogram import Client, filters
from pyrogram.types import Message
import db


def register_afk(app: Client):

    @app.on_message(filters.group & (filters.command("afk") | filters.regex(r"^(?i)brb\b")))
    async def go_afk(client, message: Message):
        user = message.from_user
        parts = message.text.split(maxsplit=1)
        reason = parts[1] if len(parts) > 1 else ""
        await db.set_afk(user.id, reason)
        text = f"😴 **{user.first_name}** is now AFK."
        if reason:
            text += f"\n📝 Reason: {reason}"
        await message.reply_text(text)

    @app.on_message(filters.group & ~filters.service, group=3)
    async def check_afk(client, message: Message):
        if not message.from_user:
            return

        user = message.from_user

        # Remove AFK if the AFK user sends a message (not an /afk command)
        if not (message.text and message.text.startswith("/afk")):
            was_afk = await db.rm_afk(user.id)
            if was_afk:
                try:
                    await message.reply_text(
                        f"👋 Welcome back **{user.first_name}**! AFK status removed."
                    )
                except Exception:
                    pass

        # Notify if someone mentions an AFK user
        entities = message.entities or []
        for ent in entities:
            if ent.type.name == "MENTION":
                username = message.text[ent.offset + 1: ent.offset + ent.length]
                try:
                    mentioned = await client.get_users(username)
                    if await db.is_afk(mentioned.id):
                        reason = await db.get_afk_reason(mentioned.id)
                        txt = f"😴 **{mentioned.first_name}** is AFK."
                        if reason:
                            txt += f"\n📝 Reason: {reason}"
                        await message.reply_text(txt)
                except Exception:
                    pass

        # Also check text_mention entities
        for ent in entities:
            if ent.type.name == "TEXT_MENTION" and ent.user:
                if await db.is_afk(ent.user.id):
                    reason = await db.get_afk_reason(ent.user.id)
                    txt = f"😴 **{ent.user.first_name}** is AFK."
                    if reason:
                        txt += f"\n📝 Reason: {reason}"
                    await message.reply_text(txt)
