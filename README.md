# 🤖 Group Manager Bot

A powerful, fully-featured Telegram group manager bot built with **Pyrogram** and **MongoDB (Motor)**.
Merged from **NomadeHelpBot** and **Rose-Bot**, re-architected to be SQL-free and Render-ready.

---

## ✨ Features

| Module | Commands |
|---|---|
| 👋 Welcome | `/setwelcome`, `/welcome on/off` |
| 🔒 Locks | `/lock`, `/unlock`, `/locks` |
| ⚔️ Moderation | `/ban`, `/unban`, `/kick`, `/mute`, `/unmute`, `/warn`, `/warns`, `/resetwarns`, `/promote`, `/demote`, `/purge` |
| 📝 Notes | `/save`, `/get`, `/notes`, `/clear`, `#notename` |
| 📜 Rules | `/rules`, `/setrules`, `/clearrules` |
| 🚫 Blacklist | `/addblacklist`, `/rmblacklist`, `/blacklist` |
| 😴 AFK | `/afk`, `brb` |
| 🌊 Anti-Flood | `/setflood`, `/flood` |
| ℹ️ User Info | `/id`, `/info`, `/bio`, `/setbio`, `/me`, `/setme` |
| 🛠 Misc | `/ping`, `/admins`, `/chatid`, `/invite`, `/del` |
| 📡 Owner | `/broadcast`, `/stats` |

---

## 🚀 Deploy on Render

1. Fork/upload this repo to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your GitHub repo
4. Set environment variables (see `.env` file for the full list)
5. Deploy — the bot starts automatically!

The built-in health endpoint (`/health`) keeps Render happy with zero extra config.

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `API_ID` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | From [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | ✅ | From [@BotFather](https://t.me/BotFather) |
| `MONGO_URI` | ✅ | MongoDB Atlas connection string |
| `DB_NAME` | ✅ | Database name (default: `BotDB`) |
| `OWNER_ID` | ✅ | Your Telegram user ID |
| `BOT_USERNAME` | ✅ | Your bot's username (without @) |
| `SUDO_USERS` | ❌ | Space-separated extra owner IDs |
| `SUPPORT_GROUP` | ❌ | Link to your support group |
| `UPDATE_CHANNEL` | ❌ | Link to your updates channel |
| `START_IMAGE` | ❌ | URL of the start/help image |
| `PORT` | ❌ | Web server port (default: `8000`) |

---

## 🛠 Local Setup

```bash
git clone <your-repo>
cd group-manager-bot
pip install -r requirements.txt
cp .env .env.local    # fill in your values
python main.py
```

---

## 📦 Stack

- **Pyrogram 2.0.106** — Telegram MTProto client
- **Motor 3.4.0** — Async MongoDB driver
- **aiohttp 3.9.5** — Render health server
- **Python 3.11**

---

## 📄 License

MIT
