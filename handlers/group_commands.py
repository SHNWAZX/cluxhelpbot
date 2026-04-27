# ============================================================
# handlers/group_commands.py — Full moderation + welcome + locks
# ============================================================
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, ChatMemberUpdated, ChatPermissions, ChatPrivileges
from pyrogram.enums import ChatMemberStatus
import db

logger = logging.getLogger(__name__)

DEFAULT_WELCOME = "👋 Welcome {mention} to **{title}**!"

VALID_LOCKS = ["url", "sticker", "media", "username", "forward", "gif", "voice"]


# ── Helpers ───────────────────────────────────────────────────

async def is_admin(client, chat_id, user_id) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


async def resolve_target(client, message: Message):
    """Return target User from reply or username/id argument."""
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return None
    arg = parts[1].strip()
    try:
        return await client.get_users(arg if arg.startswith("@") else int(arg))
    except Exception:
        return None


async def safe_action(action_coro, message: Message, success_text: str, fail_prefix: str):
    try:
        await action_coro
        await message.reply_text(success_text)
    except Exception as e:
        await message.reply_text(f"❌ {fail_prefix}: {e}")


# ── Registration ───────────────────────────────────────────────

def register_group_commands(app: Client):

    # ── Welcome event ─────────────────────────────────────────

    @app.on_chat_member_updated()
    async def on_member_join(client: Client, cmu: ChatMemberUpdated):
        if not cmu.new_chat_member:
            return
        if cmu.new_chat_member.status != ChatMemberStatus.MEMBER:
            return
        if not await db.get_welcome_status(cmu.chat.id):
            return
        user = cmu.new_chat_member.user
        tmpl = await db.get_welcome_message(cmu.chat.id) or DEFAULT_WELCOME
        try:
            text = tmpl.format(
                username=f"@{user.username}" if user.username else user.first_name,
                first_name=user.first_name,
                mention=f"[{user.first_name}](tg://user?id={user.id})",
                title=cmu.chat.title,
            )
        except (KeyError, ValueError):
            text = DEFAULT_WELCOME.format(
                mention=f"[{user.first_name}](tg://user?id={user.id})",
                title=cmu.chat.title,
            )
        try:
            await client.send_message(cmu.chat.id, text)
        except Exception as e:
            logger.error("Welcome send failed: %s", e)

    # ── /welcome toggle ──────────────────────────────────────

    @app.on_message(filters.group & filters.command("welcome"))
    async def welcome_toggle(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in ("on", "off"):
            return await message.reply_text("⚙️ Usage: `/welcome on` or `/welcome off`")
        enabled = parts[1].lower() == "on"
        await db.set_welcome_status(message.chat.id, enabled)
        await message.reply_text("✅ Welcome messages **enabled**." if enabled else "⚠️ Welcome messages **disabled**.")

    # ── /setwelcome ───────────────────────────────────────────

    @app.on_message(filters.group & filters.command("setwelcome"))
    async def set_welcome(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text(
                "📝 Usage: `/setwelcome <message>`\n\n"
                "Placeholders: `{first_name}` `{username}` `{mention}` `{title}`"
            )
        await db.set_welcome_message(message.chat.id, parts[1])
        await message.reply_text("✅ Welcome message saved!")

    # ── /lock / /unlock / /locks ──────────────────────────────

    @app.on_message(filters.group & filters.command("lock"))
    async def lock_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in VALID_LOCKS:
            return await message.reply_text(f"⚙️ Usage: `/lock <type>`\nTypes: `{'` `'.join(VALID_LOCKS)}`")
        await db.set_lock(message.chat.id, parts[1].lower(), True)
        await message.reply_text(f"🔒 **{parts[1].lower()}** locked.")

    @app.on_message(filters.group & filters.command("unlock"))
    async def unlock_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or parts[1].lower() not in VALID_LOCKS:
            return await message.reply_text(f"⚙️ Usage: `/unlock <type>`\nTypes: `{'` `'.join(VALID_LOCKS)}`")
        await db.set_lock(message.chat.id, parts[1].lower(), False)
        await message.reply_text(f"🔓 **{parts[1].lower()}** unlocked.")

    @app.on_message(filters.group & filters.command("locks"))
    async def locks_list(client, message: Message):
        locks = await db.get_locks(message.chat.id)
        if not locks:
            return await message.reply_text("🔓 No locks set.")
        lines = "\n".join(f"• `{k}`: {'🔒 ON' if v else '🔓 OFF'}" for k, v in locks.items())
        await message.reply_text(f"**Active Locks:**\n{lines}")

    # ── Enforce locks ─────────────────────────────────────────

    @app.on_message(filters.group & ~filters.service, group=1)
    async def enforce_locks(client, message: Message):
        if not message.from_user:
            return
        if await is_admin(client, message.chat.id, message.from_user.id):
            return
        locks = await db.get_locks(message.chat.id)
        if not locks:
            return
        try:
            if locks.get("url") and message.text:
                entities = message.entities or []
                for ent in entities:
                    if ent.type.name in ("URL", "TEXT_LINK"):
                        return await message.delete()
                if "t.me/" in message.text.lower():
                    return await message.delete()
            if locks.get("sticker") and message.sticker:
                return await message.delete()
            if locks.get("media") and (message.photo or message.video or message.document):
                return await message.delete()
            if locks.get("gif") and message.animation:
                return await message.delete()
            if locks.get("voice") and message.voice:
                return await message.delete()
            if locks.get("username") and message.text and "@" in message.text:
                return await message.delete()
            if locks.get("forward") and message.forward_date:
                return await message.delete()
        except Exception:
            pass

    # ── /kick ─────────────────────────────────────────────────

    @app.on_message(filters.group & filters.command("kick"))
    async def kick_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        user = await resolve_target(client, message)
        if not user:
            return await message.reply_text("⚠️ Reply to a user or provide @username/ID.")
        if await is_admin(client, message.chat.id, user.id):
            return await message.reply_text("⚠️ Cannot kick an admin.")
        if user.id == message.from_user.id:
            return await message.reply_text("⚠️ You can't kick yourself.")
        try:
            await client.ban_chat_member(message.chat.id, user.id)
            await client.unban_chat_member(message.chat.id, user.id)
            await message.reply_text(f"👢 **{user.first_name}** has been kicked.")
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")

    # ── /ban ──────────────────────────────────────────────────

    @app.on_message(filters.group & filters.command("ban"))
    async def ban_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        user = await resolve_target(client, message)
        if not user:
            return await message.reply_text("⚠️ Reply to a user or provide @username/ID.")
        if await is_admin(client, message.chat.id, user.id):
            return await message.reply_text("⚠️ Cannot ban an admin.")
        if user.id == message.from_user.id:
            return await message.reply_text("⚠️ You can't ban yourself.")
        try:
            await client.ban_chat_member(message.chat.id, user.id)
            await message.reply_text(f"🚫 **{user.first_name}** has been banned.")
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")

    # ── /unban ────────────────────────────────────────────────

    @app.on_message(filters.group & filters.command("unban"))
    async def unban_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        user = await resolve_target(client, message)
        if not user:
            return await message.reply_text("⚠️ Reply to a user or provide @username/ID.")
        try:
            await client.unban_chat_member(message.chat.id, user.id)
            await message.reply_text(f"✅ **{user.first_name}** has been unbanned.")
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")

    # ── /mute ─────────────────────────────────────────────────

    @app.on_message(filters.group & filters.command("mute"))
    async def mute_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        user = await resolve_target(client, message)
        if not user:
            return await message.reply_text("⚠️ Reply to a user or provide @username/ID.")
        if await is_admin(client, message.chat.id, user.id):
            return await message.reply_text("⚠️ Cannot mute an admin.")
        try:
            await client.restrict_chat_member(
                message.chat.id, user.id,
                ChatPermissions(can_send_messages=False),
            )
            await message.reply_text(f"🔇 **{user.first_name}** has been muted.")
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")

    # ── /unmute ───────────────────────────────────────────────

    @app.on_message(filters.group & filters.command("unmute"))
    async def unmute_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        user = await resolve_target(client, message)
        if not user:
            return await message.reply_text("⚠️ Reply to a user or provide @username/ID.")
        try:
            await client.restrict_chat_member(
                message.chat.id, user.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )
            await message.reply_text(f"🔊 **{user.first_name}** has been unmuted.")
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")

    # ── /warn / /warns / /resetwarns ──────────────────────────

    @app.on_message(filters.group & filters.command("warn"))
    async def warn_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        user = await resolve_target(client, message)
        if not user:
            return await message.reply_text("⚠️ Reply to a user or provide @username/ID.")
        if await is_admin(client, message.chat.id, user.id):
            return await message.reply_text("⚠️ Cannot warn an admin.")
        count = await db.add_warn(message.chat.id, user.id)
        if count >= 3:
            try:
                await client.restrict_chat_member(
                    message.chat.id, user.id,
                    ChatPermissions(can_send_messages=False),
                )
            except Exception:
                pass
            await message.reply_text(f"🚫 **{user.first_name}** reached 3/3 warns and has been muted.")
        else:
            await message.reply_text(f"⚠️ **{user.first_name}** warned: **{count}/3**.")

    @app.on_message(filters.group & filters.command("warns"))
    async def warns_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        user = await resolve_target(client, message)
        if not user:
            return await message.reply_text("⚠️ Reply to a user or provide @username/ID.")
        count = await db.get_warns(message.chat.id, user.id)
        await message.reply_text(f"⚠️ **{user.first_name}** has **{count}/3** warnings.")

    @app.on_message(filters.group & filters.command("resetwarns"))
    async def resetwarns_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        user = await resolve_target(client, message)
        if not user:
            return await message.reply_text("⚠️ Reply to a user or provide @username/ID.")
        await db.reset_warns(message.chat.id, user.id)
        await message.reply_text(f"✅ **{user.first_name}**'s warnings have been reset.")

    # ── /promote / /demote ────────────────────────────────────

    @app.on_message(filters.group & filters.command("promote"))
    async def promote_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        user = await resolve_target(client, message)
        if not user:
            return await message.reply_text("⚠️ Reply to a user or provide @username/ID.")
        try:
            await client.promote_chat_member(
                message.chat.id, user.id,
                privileges=ChatPrivileges(
                    can_manage_chat=True,
                    can_delete_messages=True,
                    can_restrict_members=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                    can_manage_video_chats=True,
                    can_promote_members=False,
                    is_anonymous=False,
                ),
            )
            await message.reply_text(f"✅ **{user.first_name}** has been promoted.")
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")

    @app.on_message(filters.group & filters.command("demote"))
    async def demote_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        user = await resolve_target(client, message)
        if not user:
            return await message.reply_text("⚠️ Reply to a user or provide @username/ID.")
        try:
            await client.promote_chat_member(
                message.chat.id, user.id,
                privileges=ChatPrivileges(
                    can_manage_chat=False, can_delete_messages=False,
                    can_restrict_members=False, can_invite_users=False,
                    can_pin_messages=False, can_manage_video_chats=False,
                    can_promote_members=False, is_anonymous=False,
                ),
            )
            await message.reply_text(f"✅ **{user.first_name}** has been demoted.")
        except Exception as e:
            await message.reply_text(f"❌ Failed: {e}")

    # ── /purge ────────────────────────────────────────────────

    @app.on_message(filters.group & filters.command("purge"))
    async def purge_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ Admins only.")
        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to the first message you want to delete.")
        start_id = message.reply_to_message.id
        end_id   = message.id
        ids = list(range(start_id, end_id + 1))
        deleted = 0
        for i in range(0, len(ids), 100):
            try:
                await client.delete_messages(message.chat.id, ids[i:i+100])
                deleted += min(100, len(ids) - i)
            except Exception:
                pass
        notice = await message.reply_text(f"🗑 Purged **{deleted}** messages.")
        await notice.delete(delay=5)
