# ============================================================
# handlers/userinfo.py — /id, /info, /bio, /setbio, /me, /setme
# ============================================================
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from handlers.group_commands import is_admin
import db


def register_userinfo(app: Client):

    @app.on_message(filters.command("id"))
    async def id_cmd(client, message: Message):
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user
        else:
            user = message.from_user
        lines = [f"👤 **{user.first_name}**", f"• ID: `{user.id}`"]
        if user.username:
            lines.append(f"• Username: @{user.username}")
        if message.chat.id != user.id:
            lines.append(f"\n💬 **Chat ID:** `{message.chat.id}`")
        await message.reply_text("\n".join(lines))

    @app.on_message(filters.command("info"))
    async def info_cmd(client, message: Message):
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user
        else:
            user = message.from_user
        bio  = await db.get_user_bio(user.id)
        me   = await db.get_user_me(user.id)
        lines = [
            f"ℹ️ **User Info**",
            f"• Name: [{user.first_name}](tg://user?id={user.id})",
            f"• ID: `{user.id}`",
        ]
        if user.username:
            lines.append(f"• Username: @{user.username}")
        if bio:
            lines.append(f"• Bio: {bio}")
        if me:
            lines.append(f"• About: {me}")
        if message.chat.id < 0:
            try:
                member = await client.get_chat_member(message.chat.id, user.id)
                status_map = {
                    ChatMemberStatus.OWNER: "👑 Owner",
                    ChatMemberStatus.ADMINISTRATOR: "⚙️ Admin",
                    ChatMemberStatus.MEMBER: "👤 Member",
                    ChatMemberStatus.RESTRICTED: "🔇 Restricted",
                    ChatMemberStatus.LEFT: "🚶 Left",
                    ChatMemberStatus.BANNED: "🚫 Banned",
                }
                lines.append(f"• Status: {status_map.get(member.status, 'Unknown')}")
            except Exception:
                pass
        await message.reply_text("\n".join(lines))

    @app.on_message(filters.command("setbio"))
    async def setbio_cmd(client, message: Message):
        if message.chat.id > 0:
            # Private: set own bio
            parts = message.text.split(maxsplit=1)
            if len(parts) < 2:
                return await message.reply_text("⚙️ Usage: `/setbio <text>`")
            await db.set_user_bio(message.from_user.id, parts[1])
            return await message.reply_text("✅ Your bio has been set!")
        # Group: admin sets bio of replied user
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to a user to set their bio.")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ Usage: `/setbio <text>` (reply to user)")
        target = message.reply_to_message.from_user
        await db.set_user_bio(target.id, parts[1])
        await message.reply_text(f"✅ Bio for **{target.first_name}** set!")

    @app.on_message(filters.command("bio"))
    async def bio_cmd(client, message: Message):
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user
        else:
            user = message.from_user
        bio = await db.get_user_bio(user.id)
        if bio:
            await message.reply_text(f"ℹ️ **{user.first_name}'s bio:**\n{bio}")
        else:
            await message.reply_text(f"ℹ️ **{user.first_name}** has no bio set.")

    @app.on_message(filters.command("setme"))
    async def setme_cmd(client, message: Message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("⚙️ Usage: `/setme <about text>`")
        await db.set_user_me(message.from_user.id, parts[1])
        await message.reply_text("✅ Your about info has been saved!")

    @app.on_message(filters.command("me"))
    async def me_cmd(client, message: Message):
        info = await db.get_user_me(message.from_user.id)
        if info:
            await message.reply_text(f"👤 **About you:**\n{info}")
        else:
            await message.reply_text("ℹ️ You haven't set any about info yet. Use `/setme <text>`.")
