# ============================================================
# handlers/misc.py — /ping, /admins, /chatid, /invite, /del
# ============================================================
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from handlers.group_commands import is_admin


def register_misc(app: Client):

    @app.on_message(filters.command("ping"))
    async def ping_cmd(client, message: Message):
        start = time.monotonic()
        msg = await message.reply_text("🏓 Pong!")
        ms = (time.monotonic() - start) * 1000
        await msg.edit_text(f"🏓 Pong! `{ms:.1f}ms`")

    @app.on_message(filters.group & filters.command("admins"))
    async def admins_cmd(client, message: Message):
        admins = []
        async for member in client.get_chat_members(
            message.chat.id, filter="administrators"
        ):
            if not member.user.is_bot:
                tag = f"@{member.user.username}" if member.user.username else member.user.first_name
                role = "👑 Owner" if member.status == ChatMemberStatus.OWNER else "⚙️ Admin"
                admins.append(f"{role}: [{tag}](tg://user?id={member.user.id})")
        if admins:
            await message.reply_text("**Group Admins:**\n" + "\n".join(admins))
        else:
            await message.reply_text("No admins found.")

    @app.on_message(filters.group & filters.command("chatid"))
    async def chatid_cmd(client, message: Message):
        await message.reply_text(f"💬 Chat ID: `{message.chat.id}`")

    @app.on_message(filters.group & filters.command("invite"))
    async def invite_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        try:
            link = await client.export_chat_invite_link(message.chat.id)
            await message.reply_text(f"🔗 Invite link:\n{link}")
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")

    @app.on_message(filters.group & filters.command("del"))
    async def del_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to the message you want to delete.")
        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")
