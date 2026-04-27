# ============================================================
# handlers/notes.py — Save, get, list, delete notes
# ============================================================
from pyrogram import Client, filters
from pyrogram.types import Message
import db


def register_notes(app: Client):

    @app.on_message(filters.group & filters.command("save"))
    async def save_note(client, message: Message):
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            return await message.reply_text("⚙️ Usage: `/save <name> <text>`")
        name, text = parts[1], parts[2]
        await db.save_note(message.chat.id, name, text)
        await message.reply_text(f"✅ Note `{name}` saved!")

    @app.on_message(filters.group & filters.command("get"))
    async def get_note_cmd(client, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ Usage: `/get <name>`")
        note = await db.get_note(message.chat.id, parts[1].lower())
        if not note:
            return await message.reply_text(f"❌ No note named `{parts[1]}`.")
        await message.reply_text(note["text"])

    # Also trigger notes with #notename
    @app.on_message(filters.group & filters.regex(r"^#(\w+)"))
    async def hashtag_note(client, message: Message):
        name = message.matches[0].group(1)
        note = await db.get_note(message.chat.id, name.lower())
        if note:
            await message.reply_text(note["text"])

    @app.on_message(filters.group & filters.command("notes"))
    async def list_notes(client, message: Message):
        notes = await db.get_all_notes(message.chat.id)
        if not notes:
            return await message.reply_text("📝 No notes saved in this group.")
        names = "\n".join(f"• `#{n['name']}`" for n in notes)
        await message.reply_text(f"📝 **Saved Notes:**\n{names}")

    @app.on_message(filters.group & filters.command("clear"))
    async def clear_note(client, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ Usage: `/clear <name>`")
        deleted = await db.delete_note(message.chat.id, parts[1].lower())
        if deleted:
            await message.reply_text(f"🗑 Note `{parts[1]}` deleted.")
        else:
            await message.reply_text(f"❌ No note named `{parts[1]}`.")
