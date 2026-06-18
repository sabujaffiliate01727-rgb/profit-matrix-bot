# Profit Matrix — Telegram Join Bot

A simple public Telegram bot that:

1. On `/start`, asks the user to pick a language — **🇧🇩 বাংলা / 🇬🇧 English**
2. Shows a welcome message in that language
3. Gives a button to **join your channel (Profit Matrix)**
4. (Optional) verifies the user actually joined before welcoming them in

It remembers each user's language in `users.json`. Built on the plain Telegram
Bot API — only needs `requests` + `python-dotenv`.

---

## Setup (5 steps)

### 1. Make the bot
- Open Telegram → search **@BotFather** → send `/newbot`
- Choose a name and a username (must end in `bot`, e.g. `ProfitMatrixJoinBot`)
- BotFather gives you a **token** like `123456:ABC...`

### 2. Configure
- In this folder, copy `.env.example` → `.env`
- Open `.env` and fill in:
  - `BOT_TOKEN` = the token from BotFather
  - `CHANNEL_URL` = your channel link (e.g. `https://t.me/ProfitMatrix` or an invite link `https://t.me/+xxxx`)

### 3. Run
Double-click **`start_bot.bat`** (it installs requirements and starts the bot).

Or from a terminal:
```
py -m pip install -r requirements.txt
py bot.py
```

You should see `Bot online: @YourBotUsername`. Now open your bot in Telegram and
send `/start`. ✅

### 4. (Optional) "Verify they joined" mode
If you want the bot to **check** that a user really joined before welcoming them:
- Set `CHANNEL_USERNAME=@YourChannel` and `REQUIRE_JOIN=true` in `.env`
- Add your **bot as an ADMIN** of the channel (it can't read membership otherwise)
- A `✅ I've Joined` button will appear; tapping it checks membership.

> Note: membership verification works for **public** channels with a `@username`.
> For private channels, keep `REQUIRE_JOIN=false` and just use the invite link.

### 5. Keep it running 24/7 (optional)
The bot only responds while `bot.py` is running. To keep it always on, run it on
a small server (Railway / a VPS) the same way you run your other bots.

---

## Editing the messages
All text lives near the top of `bot.py`:
- `WELCOME` — the main message (Bangla + English)
- `DISCLAIMER` — the small risk note (delete if you don't want it)
- `JOINED_OK` / `NOT_JOINED` — verification replies
- `BTN` — button labels

The welcome text currently says **"AlveeFx"** (from your sample). If your persona
is different, just replace `AlveeFx` in the `WELCOME` block with **Profit Matrix**
or your own name.
