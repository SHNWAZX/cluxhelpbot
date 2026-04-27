# ============================================================
# db.py — MongoDB (Motor async) data layer
# All SQL removed; everything uses MongoDB collections.
# ============================================================
import motor.motor_asyncio
import logging
from config import MONGO_URI, DB_NAME

logger = logging.getLogger(__name__)

_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db      = _client[DB_NAME]

logger.info("✅ MongoDB connected to database: %s", DB_NAME)

# ════════════════════════════════════════════════════════════
# 👤 Users
# ════════════════════════════════════════════════════════════

async def add_user(user_id: int, first_name: str):
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"first_name": first_name}},
        upsert=True,
    )

async def get_all_users():
    return [doc["user_id"] async for doc in db.users.find({}, {"user_id": 1})]

async def get_user_count() -> int:
    return await db.users.count_documents({})

# ════════════════════════════════════════════════════════════
# 🟢 Welcome
# ════════════════════════════════════════════════════════════

async def set_welcome_message(chat_id: int, text: str):
    await db.welcome.update_one({"chat_id": chat_id}, {"$set": {"message": text}}, upsert=True)

async def get_welcome_message(chat_id: int):
    doc = await db.welcome.find_one({"chat_id": chat_id})
    return doc.get("message") if doc else None

async def set_welcome_status(chat_id: int, status: bool):
    await db.welcome.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def get_welcome_status(chat_id: int) -> bool:
    doc = await db.welcome.find_one({"chat_id": chat_id})
    return bool(doc.get("enabled", True)) if doc else True

# ════════════════════════════════════════════════════════════
# 🔒 Locks
# ════════════════════════════════════════════════════════════

async def set_lock(chat_id: int, lock_type: str, status: bool):
    await db.locks.update_one(
        {"chat_id": chat_id},
        {"$set": {f"locks.{lock_type}": status}},
        upsert=True,
    )

async def get_locks(chat_id: int) -> dict:
    doc = await db.locks.find_one({"chat_id": chat_id})
    return doc.get("locks", {}) if doc else {}

# ════════════════════════════════════════════════════════════
# ⚠️ Warns
# ════════════════════════════════════════════════════════════

async def add_warn(chat_id: int, user_id: int) -> int:
    doc = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id})
    count = doc.get("count", 0) + 1 if doc else 1
    await db.warns.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": count}},
        upsert=True,
    )
    return count

async def get_warns(chat_id: int, user_id: int) -> int:
    doc = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id})
    return doc.get("count", 0) if doc else 0

async def reset_warns(chat_id: int, user_id: int):
    await db.warns.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": 0}},
        upsert=True,
    )

# ════════════════════════════════════════════════════════════
# 📝 Notes
# ════════════════════════════════════════════════════════════

async def save_note(chat_id: int, name: str, text: str):
    await db.notes.update_one(
        {"chat_id": chat_id, "name": name.lower()},
        {"$set": {"text": text}},
        upsert=True,
    )

async def get_note(chat_id: int, name: str):
    return await db.notes.find_one({"chat_id": chat_id, "name": name.lower()})

async def delete_note(chat_id: int, name: str) -> bool:
    result = await db.notes.delete_one({"chat_id": chat_id, "name": name.lower()})
    return result.deleted_count > 0

async def get_all_notes(chat_id: int):
    return [doc async for doc in db.notes.find({"chat_id": chat_id})]

# ════════════════════════════════════════════════════════════
# 📜 Rules
# ════════════════════════════════════════════════════════════

async def set_rules(chat_id: int, text: str):
    await db.rules.update_one({"chat_id": chat_id}, {"$set": {"text": text}}, upsert=True)

async def get_rules(chat_id: int):
    doc = await db.rules.find_one({"chat_id": chat_id})
    return doc.get("text", "") if doc else ""

async def clear_rules(chat_id: int):
    await db.rules.delete_one({"chat_id": chat_id})

# ════════════════════════════════════════════════════════════
# 🚫 Blacklist
# ════════════════════════════════════════════════════════════

async def add_blacklist_word(chat_id: int, word: str):
    await db.blacklist.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"words": word.lower()}},
        upsert=True,
    )

async def remove_blacklist_word(chat_id: int, word: str) -> bool:
    result = await db.blacklist.update_one(
        {"chat_id": chat_id},
        {"$pull": {"words": word.lower()}},
    )
    return result.modified_count > 0

async def get_blacklist(chat_id: int):
    doc = await db.blacklist.find_one({"chat_id": chat_id})
    return doc.get("words", []) if doc else []

# ════════════════════════════════════════════════════════════
# 💬 AFK
# ════════════════════════════════════════════════════════════

async def set_afk(user_id: int, reason: str = ""):
    await db.afk.update_one(
        {"user_id": user_id},
        {"$set": {"is_afk": True, "reason": reason}},
        upsert=True,
    )

async def rm_afk(user_id: int) -> bool:
    doc = await db.afk.find_one({"user_id": user_id})
    if doc and doc.get("is_afk"):
        await db.afk.update_one({"user_id": user_id}, {"$set": {"is_afk": False, "reason": ""}})
        return True
    return False

async def is_afk(user_id: int) -> bool:
    doc = await db.afk.find_one({"user_id": user_id})
    return bool(doc and doc.get("is_afk"))

async def get_afk_reason(user_id: int) -> str:
    doc = await db.afk.find_one({"user_id": user_id})
    return doc.get("reason", "") if doc else ""

# ════════════════════════════════════════════════════════════
# 🌊 Antiflood
# ════════════════════════════════════════════════════════════

async def set_flood_limit(chat_id: int, limit: int):
    await db.antiflood.update_one({"chat_id": chat_id}, {"$set": {"limit": limit}}, upsert=True)

async def get_flood_limit(chat_id: int) -> int:
    doc = await db.antiflood.find_one({"chat_id": chat_id})
    return doc.get("limit", 0) if doc else 0

# In-memory flood tracker (resets on restart – acceptable for flood control)
_flood_tracker: dict = {}

async def update_flood(chat_id: int, user_id) -> bool:
    """Returns True if the user should be banned for flooding."""
    limit = await get_flood_limit(chat_id)
    if limit == 0:
        return False
    if user_id is None:
        _flood_tracker.pop(chat_id, None)
        return False
    key = (chat_id, user_id)
    _flood_tracker[key] = _flood_tracker.get(key, 0) + 1
    if _flood_tracker[key] >= limit:
        _flood_tracker[key] = 0
        return True
    return False

async def reset_flood(chat_id: int, user_id: int):
    _flood_tracker.pop((chat_id, user_id), None)

# ════════════════════════════════════════════════════════════
# ℹ️ User Bio / Info
# ════════════════════════════════════════════════════════════

async def set_user_bio(user_id: int, bio: str):
    await db.userinfo.update_one({"user_id": user_id}, {"$set": {"bio": bio}}, upsert=True)

async def get_user_bio(user_id: int) -> str:
    doc = await db.userinfo.find_one({"user_id": user_id})
    return doc.get("bio", "") if doc else ""

async def set_user_me(user_id: int, info: str):
    await db.userinfo.update_one({"user_id": user_id}, {"$set": {"me": info}}, upsert=True)

async def get_user_me(user_id: int) -> str:
    doc = await db.userinfo.find_one({"user_id": user_id})
    return doc.get("me", "") if doc else ""

# ════════════════════════════════════════════════════════════
# 🧹 Group Cleanup
# ════════════════════════════════════════════════════════════

async def clear_group_data(chat_id: int):
    for col in [db.welcome, db.locks, db.notes, db.rules, db.blacklist, db.antiflood]:
        await col.delete_one({"chat_id": chat_id})
    await db.warns.delete_many({"chat_id": chat_id})
