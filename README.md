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

The welcome text uses the **Profit Matrix** community voice ("we"). Edit the
`WELCOME` block to change wording, brand, or tone.

---

## Deploy free 24/7 on Koyeb

The bot only runs while it's running somewhere. Koyeb's free tier keeps it
online 24/7 without your PC. It builds from the included `Dockerfile`.

### 1. Put the code on GitHub
This folder is already a git repo with a safe `.gitignore` (your `.env` and
token are **never** uploaded). Create an empty repo on github.com, then:
```
git remote add origin https://github.com/<your-username>/profit-matrix-bot.git
git push -u origin main
```

### 2. Create the Koyeb service
1. Sign up at https://app.koyeb.com (GitHub login is easiest)
2. **Create Service → GitHub →** pick your `profit-matrix-bot` repo
3. Koyeb detects the `Dockerfile` automatically
4. **Service type: Worker** (this bot has no website/port)
5. **Instance: Free**
6. Open **Environment variables** and add (do NOT put them in the repo):
   - `BOT_TOKEN` → your token  *(mark as Secret)*
   - `CHANNEL_URL` → `https://t.me/ProfitMatrixpm`
   - `CHANNEL_USERNAME` → `@ProfitMatrixpm`
   - `REQUIRE_JOIN` → `true`
   - `BRAND` → `Profit Matrix`
7. **Deploy**. When logs show `Bot online: @...`, it's live 24/7. ✅

> Note: Koyeb's disk is ephemeral, so `users.json` (saved languages) resets on
> redeploys. Harmless — users just pick their language again on next `/start`.

### Updating later
Edit code → `git commit -am "update" && git push` → Koyeb auto-redeploys.
