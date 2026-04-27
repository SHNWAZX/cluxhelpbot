# ============================================================
# handlers/start.py — /start, /help, broadcast, stats
# ============================================================
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto,
)
from config import BOT_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL, START_IMAGE, OWNER_ID
import db


def register_start(app: Client):

    # ── helpers ──────────────────────────────────────────────

    async def send_start_menu(target, user_name: str):
        text = (
            f"✨ Hello **{user_name}**! ✨\n\n"
            "👋 I am your **Group Manager Bot** 🤖\n\n"
            "**Features:**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "• Smart Anti-Spam & Link Shield\n"
            "• Adaptive Lock System\n"
            "• Anti-Flood Protection\n"
            "• Notes & Rules System\n"
            "• Word Blacklist\n"
            "• AFK System\n"
            "• User Bio & Info\n"
            "• Full Moderation Suite\n"
            "• And much more!\n"
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚒️ Add to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
            [
                InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP),
                InlineKeyboardButton("📢 Updates", url=UPDATE_CHANNEL),
            ],
            [InlineKeyboardButton("📚 Help", callback_data="help_main")],
        ])
        if hasattr(target, "text") and target.text:
            if START_IMAGE:
                await target.reply_photo(START_IMAGE, caption=text, reply_markup=buttons)
            else:
                await target.reply_text(text, reply_markup=buttons)
        else:
            if START_IMAGE:
                media = InputMediaPhoto(media=START_IMAGE, caption=text)
                await target.edit_media(media=media, reply_markup=buttons)
            else:
                await target.edit_text(text, reply_markup=buttons)

    async def send_help_menu(msg):
        text = (
            "📚 **Help Menu** — Choose a category:\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👋 Greetings",   callback_data="help_greetings"),
                InlineKeyboardButton("🔒 Locks",       callback_data="help_locks"),
            ],
            [
                InlineKeyboardButton("⚔️ Moderation",  callback_data="help_mod"),
                InlineKeyboardButton("📝 Notes",       callback_data="help_notes"),
            ],
            [
                InlineKeyboardButton("📜 Rules",       callback_data="help_rules"),
                InlineKeyboardButton("🚫 Blacklist",   callback_data="help_blacklist"),
            ],
            [
                InlineKeyboardButton("😴 AFK",         callback_data="help_afk"),
                InlineKeyboardButton("🌊 AntiFlood",   callback_data="help_flood"),
            ],
            [
                InlineKeyboardButton("ℹ️ User Info",   callback_data="help_userinfo"),
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="help_back")],
        ])
        if START_IMAGE:
            media = InputMediaPhoto(media=START_IMAGE, caption=text)
            await msg.edit_media(media=media, reply_markup=buttons)
        else:
            await msg.edit_text(text, reply_markup=buttons)

    HELP_TEXTS = {
        "help_greetings": (
            "👋 **Welcome System**\n━━━━━━━━━━━━━━━━━━━━\n\n"
            "• `/setwelcome <text>` — Set a custom welcome message\n"
            "• `/welcome on` — Enable welcome messages\n"
            "• `/welcome off` — Disable welcome messages\n\n"
            "**Placeholders:** `{first_name}` `{username}` `{mention}` `{title}`"
        ),
        "help_locks": (
            "🔒 **Locks System**\n━━━━━━━━━━━━━━━━━━━━\n\n"
            "• `/lock <type>` — Enable a lock\n"
            "• `/unlock <type>` — Disable a lock\n"
            "• `/locks` — Show active locks\n\n"
            "**Types:** `url` `sticker` `media` `username` `forward` `gif` `voice`"
        ),
        "help_mod": (
            "⚔️ **Moderation**\n━━━━━━━━━━━━━━━━━━━━\n\n"
            "• `/kick` — Kick a user\n"
            "• `/ban` — Ban a user\n"
            "• `/unban` — Unban a user\n"
            "• `/mute` — Mute a user\n"
            "• `/unmute` — Unmute a user\n"
            "• `/warn` — Warn a user (3 = mute)\n"
            "• `/warns` — View warnings\n"
            "• `/resetwarns` — Reset warnings\n"
            "• `/promote` — Promote to admin\n"
            "• `/demote` — Demote from admin\n"
            "• `/purge` — Delete messages"
        ),
        "help_notes": (
            "📝 **Notes**\n━━━━━━━━━━━━━━━━━━━━\n\n"
            "• `/save <name> <text>` — Save a note\n"
            "• `/get <name>` or `#name` — Get a note\n"
            "• `/notes` — List all notes\n"
            "• `/clear <name>` — Delete a note"
        ),
        "help_rules": (
            "📜 **Rules**\n━━━━━━━━━━━━━━━━━━━━\n\n"
            "• `/rules` — Show group rules\n"
            "• `/setrules <text>` — Set rules (admin)\n"
            "• `/clearrules` — Clear rules (admin)"
        ),
        "help_blacklist": (
            "🚫 **Word Blacklist**\n━━━━━━━━━━━━━━━━━━━━\n\n"
            "• `/addblacklist <word>` — Add word(s) to blacklist\n"
            "• `/rmblacklist <word>` — Remove word(s)\n"
            "• `/blacklist` — View blacklisted words\n\n"
            "_Note: Admins are exempt from blacklist._"
        ),
        "help_afk": (
            "😴 **AFK System**\n━━━━━━━━━━━━━━━━━━━━\n\n"
            "• `/afk <reason>` — Mark yourself as AFK\n"
            "• `brb <reason>` — Same as /afk\n\n"
            "_Mentioning an AFK user shows their reason._\n"
            "_Sending any message removes AFK status._"
        ),
        "help_flood": (
            "🌊 **Anti-Flood**\n━━━━━━━━━━━━━━━━━━━━\n\n"
            "• `/setflood <number>` — Set message limit (admin)\n"
            "• `/setflood off` — Disable anti-flood\n"
            "• `/flood` — Show current flood limit"
        ),
        "help_userinfo": (
            "ℹ️ **User Info**\n━━━━━━━━━━━━━━━━━━━━\n\n"
            "• `/id` — Get your or replied user's ID\n"
            "• `/info` — Get info about a user\n"
            "• `/setme <text>` — Set your about info\n"
            "• `/me` — View your about info\n"
            "• `/setbio <text>` — Set someone's bio (reply)\n"
            "• `/bio` — View a user's bio"
        ),
    }

    # ── /start ────────────────────────────────────────────────

    @app.on_message(filters.private & filters.command("start"))
    async def start_cmd(client, message):
        user = message.from_user
        await db.add_user(user.id, user.first_name)
        await send_start_menu(message, user.first_name)

    # ── callbacks ─────────────────────────────────────────────

    @app.on_callback_query(filters.regex("^help_main$"))
    async def help_main_cb(client, cq):
        await send_help_menu(cq.message)
        await cq.answer()

    @app.on_callback_query(filters.regex("^help_back$"))
    async def help_back_cb(client, cq):
        await send_start_menu(cq.message, cq.from_user.first_name)
        await cq.answer()

    @app.on_callback_query(filters.regex("^help_"))
    async def help_detail_cb(client, cq):
        key = cq.data
        text = HELP_TEXTS.get(key)
        if not text:
            await cq.answer("Unknown section.", show_alert=True)
            return
        back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help_main")]])
        if START_IMAGE:
            media = InputMediaPhoto(media=START_IMAGE, caption=text)
            await cq.message.edit_media(media=media, reply_markup=back_btn)
        else:
            await cq.message.edit_text(text, reply_markup=back_btn)
        await cq.answer()

    # ── /broadcast ────────────────────────────────────────────

    @app.on_message(filters.private & filters.command("broadcast"))
    async def broadcast_cmd(client, message):
        if message.from_user.id != OWNER_ID:
            return await message.reply_text("❌ Owner only.")
        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to a message to broadcast it.")
        text_to_send = message.reply_to_message.text or message.reply_to_message.caption
        if not text_to_send:
            return await message.reply_text("⚠️ Replied message has no text.")
        users = await db.get_all_users()
        status = await message.reply_text(f"📡 Broadcasting to {len(users)} users...")
        sent, failed = 0, 0
        for uid in users:
            try:
                await client.send_message(uid, text_to_send)
                sent += 1
            except Exception:
                failed += 1
        await status.edit_text(f"✅ Done!\n\n• Sent: {sent}\n• Failed: {failed}")

    # ── /stats ────────────────────────────────────────────────

    @app.on_message(filters.private & filters.command("stats"))
    async def stats_cmd(client, message):
        if message.from_user.id != OWNER_ID:
            return await message.reply_text("❌ Owner only.")
        count = await db.get_user_count()
        await message.reply_text(f"📊 **Bot Stats**\n\n👤 Total users: **{count}**")
