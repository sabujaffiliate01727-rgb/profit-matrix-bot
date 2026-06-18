"""
Profit Matrix — Telegram welcome / channel-join bot.

What it does:
  /start  → asks the user to pick a language (বাংলা / English)
  then    → shows a welcome message in that language + a button to JOIN
            your channel "Profit Matrix"
  (optional) verifies that the user actually joined before saying "welcome in"

Built with the plain Telegram Bot API (long-polling via getUpdates) + requests,
so the only dependencies are `requests` and `python-dotenv`.

Run:  py bot.py
Stop: Ctrl + C
"""
import json
import logging
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests
from dotenv import load_dotenv
import os

load_dotenv()

# ── Config (from .env) ─────────────────────────────────────────────────────────
BOT_TOKEN       = os.getenv("BOT_TOKEN", "").strip()
# Public link people tap to open the channel, e.g. https://t.me/ProfitMatrix
# or an invite link https://t.me/+xxxxxxxx
CHANNEL_URL     = os.getenv("CHANNEL_URL", "https://t.me/ProfitMatrix").strip()
# @username of the channel (public channels only) — used to VERIFY membership.
# Leave empty if your channel is private or you don't want verification.
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "").strip()
# If "true", the bot checks that the user joined before welcoming them in.
# Requires: the bot must be an ADMIN of the channel, and CHANNEL_USERNAME set.
REQUIRE_JOIN    = os.getenv("REQUIRE_JOIN", "false").strip().lower() == "true"
BRAND           = os.getenv("BRAND", "Profit Matrix").strip()

API = f"https://api.telegram.org/bot{BOT_TOKEN}"

USERS_FILE = Path(__file__).with_name("users.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("profit-matrix-bot")


# ── Messages (edit these freely) ───────────────────────────────────────────────
# Brand voice = "Profit Matrix" community ("আমরা" / "we").
WELCOME = {
    "bn": (
        "🔥 <b>Profit Matrix-এ আপনাকে স্বাগতম!</b>\n\n"
        "আমরা Profit Matrix — ৫+ বছরের অভিজ্ঞতাসম্পন্ন একটি Quotex Trading কমিউনিটি। "
        "আপনি যদি Quotex Leaderboard ফলো করে থাকেন, তাহলে নিশ্চয়ই আমাদের নাম "
        "সেখানে দেখতে পেয়েছেন।\n\n"
        "আমাদের FREE কমিউনিটিতে যোগ দিন এবং স্মার্টভাবে ট্রেড করতে যা দরকার সব পাবেন 👇\n"
        "✅ ফ্রি মার্কেট অ্যানালাইসিস\n"
        "✅ ট্রেডিং গাইডলাইন ও শিক্ষা\n"
        "✅ Quotex Leaderboard স্ট্র্যাটেজি\n"
        "✅ রিস্ক ম্যানেজমেন্ট টিপস\n"
        "✅ আমাদের বাস্তব ট্রেডিং অভিজ্ঞতা থেকে এক্সক্লুসিভ ইনসাইট\n\n"
        "এটি Profit Matrix-এর সবচেয়ে বড় ট্রেডিং কমিউনিটি — যেখানে ট্রেডাররা একসাথে শেখে, "
        "বাড়ে এবং রিয়েল রেজাল্ট অর্জন করে 🚀\n\n"
        "আজই Profit Matrix Family-এর অংশ হয়ে যান 👇"
    ),
    "en": (
        "🔥 <b>Welcome to Profit Matrix!</b>\n\n"
        "We're Profit Matrix — a Quotex trading community with 5+ years of experience. "
        "If you follow the Quotex Leaderboard, you've surely seen our name there.\n\n"
        "Join our FREE community and get everything you need to trade smart 👇\n"
        "✅ Free market analysis\n"
        "✅ Trading guidelines & education\n"
        "✅ Quotex Leaderboard strategies\n"
        "✅ Risk management tips\n"
        "✅ Exclusive insights from our real trading experience\n\n"
        "This is Profit Matrix's biggest trading community — where traders learn, grow "
        "and achieve real results together 🚀\n\n"
        "Become part of the Profit Matrix Family today 👇"
    ),
}

# Small honest risk note. Remove if you don't want it — but most ad platforms
# (and Telegram) expect trading content to carry a disclaimer.
DISCLAIMER = {
    "bn": "\n\n⚠️ <i>ট্রেডিং-এ ঝুঁকি আছে; অতীতের ফলাফল ভবিষ্যতের নিশ্চয়তা নয়। শুধু শিক্ষামূলক উদ্দেশ্যে।</i>",
    "en": "\n\n⚠️ <i>Trading involves risk; past results don't guarantee future returns. Educational purposes only.</i>",
}

CHOOSE_LANG = (
    "🌐 <b>Please select your language / আপনার ভাষা বেছে নিন</b> 👇"
)

JOINED_OK = {
    "bn": (
        f"✅ <b>ধন্যবাদ! আপনি এখন {BRAND} ফ্যামিলির অংশ।</b>\n\n"
        "চ্যানেলে নিয়মিত মার্কেট আপডেট, অ্যানালাইসিস ও শিক্ষামূলক পোস্ট পাবেন। "
        "স্মার্টভাবে শিখুন, রিস্ক ম্যানেজ করুন 🚀"
    ),
    "en": (
        f"✅ <b>Thank you! You're now part of the {BRAND} family.</b>\n\n"
        "You'll get regular market updates, analysis and educational posts in the "
        "channel. Learn smart, manage your risk 🚀"
    ),
}

NOT_JOINED = {
    "bn": (
        "❗️ মনে হচ্ছে আপনি এখনো চ্যানেলে জয়েন করেননি।\n\n"
        "নিচের <b>Join</b> বাটনে ক্লিক করে চ্যানেলে জয়েন করুন, তারপর আবার "
        "<b>✅ আমি জয়েন করেছি</b> বাটনে চাপুন।"
    ),
    "en": (
        "❗️ Looks like you haven't joined the channel yet.\n\n"
        "Tap the <b>Join</b> button below, then press <b>✅ I've Joined</b> again."
    ),
}

BTN = {
    "join":   {"bn": f"📢 {BRAND} চ্যানেলে জয়েন করুন", "en": f"📢 Join {BRAND}"},
    "verify": {"bn": "✅ আমি জয়েন করেছি",              "en": "✅ I've Joined"},
    "lang":   {"bn": "🌐 ভাষা পরিবর্তন",                "en": "🌐 Change Language"},
}


# ── Tiny user store (remembers each user's language) ────────────────────────────
def load_users() -> dict:
    if USERS_FILE.exists():
        try:
            return json.loads(USERS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_users(users: dict) -> None:
    try:
        USERS_FILE.write_text(json.dumps(users, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    except Exception as e:
        logger.warning(f"Could not save users: {e}")


users = load_users()


def set_lang(user_id: int, lang: str) -> None:
    users[str(user_id)] = {"lang": lang}
    save_users(users)


def get_lang(user_id: int) -> str:
    return users.get(str(user_id), {}).get("lang", "en")


# ── Telegram API helpers ────────────────────────────────────────────────────────
def send(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML",
               "disable_web_page_preview": True}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(f"{API}/sendMessage", json=payload, timeout=15)
    except Exception as e:
        logger.warning(f"send failed: {e}")


def answer_callback(callback_id, text=""):
    try:
        requests.post(f"{API}/answerCallbackQuery",
                      json={"callback_query_id": callback_id, "text": text},
                      timeout=10)
    except Exception:
        pass


def get_updates(offset=0):
    try:
        r = requests.get(f"{API}/getUpdates",
                         params={"offset": offset, "timeout": 30}, timeout=35)
        return r.json().get("result", [])
    except Exception as e:
        logger.warning(f"getUpdates failed: {e}")
        return []


def is_member(user_id: int) -> bool:
    """True if the user is in the channel. Needs the bot to be a channel admin."""
    if not CHANNEL_USERNAME:
        return True  # verification not configured → don't block anyone
    chat = CHANNEL_USERNAME if CHANNEL_USERNAME.startswith("@") else f"@{CHANNEL_USERNAME}"
    try:
        r = requests.get(f"{API}/getChatMember",
                         params={"chat_id": chat, "user_id": user_id}, timeout=10)
        data = r.json()
        if not data.get("ok"):
            logger.warning(f"getChatMember not ok: {data.get('description')}")
            return False
        status = data["result"]["status"]
        return status in ("member", "administrator", "creator")
    except Exception as e:
        logger.warning(f"is_member failed: {e}")
        return False


# ── Keyboards ───────────────────────────────────────────────────────────────────
def lang_keyboard():
    return {"inline_keyboard": [[
        {"text": "🇧🇩 বাংলা",   "callback_data": "lang_bn"},
        {"text": "🇬🇧 English", "callback_data": "lang_en"},
    ]]}


def welcome_keyboard(lang: str):
    rows = [[{"text": BTN["join"][lang], "url": CHANNEL_URL}]]
    if REQUIRE_JOIN and CHANNEL_USERNAME:
        rows.append([{"text": BTN["verify"][lang], "callback_data": "verify"}])
    rows.append([{"text": BTN["lang"][lang], "callback_data": "change_lang"}])
    return {"inline_keyboard": rows}


# ── Flow ──────────────────────────────────────────────────────────────────────
def show_language_picker(chat_id):
    send(chat_id, CHOOSE_LANG, reply_markup=lang_keyboard())


def show_welcome(chat_id, lang: str):
    text = WELCOME[lang] + DISCLAIMER[lang]
    send(chat_id, text, reply_markup=welcome_keyboard(lang))


def handle_message(msg):
    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip()
    if text.startswith("/start"):
        show_language_picker(chat_id)
    elif text.startswith("/help"):
        send(chat_id, "Send /start to choose your language and join the channel. "
                      "/start দিন — ভাষা বেছে নিয়ে চ্যানেলে জয়েন করুন।")
    else:
        # any other text → guide them back to /start
        show_language_picker(chat_id)


def handle_callback(cb):
    data    = cb.get("data", "")
    cb_id   = cb["id"]
    user_id = cb["from"]["id"]
    chat_id = cb["message"]["chat"]["id"]

    if data == "lang_bn":
        set_lang(user_id, "bn")
        answer_callback(cb_id, "বাংলা নির্বাচিত হয়েছে ✅")
        show_welcome(chat_id, "bn")

    elif data == "lang_en":
        set_lang(user_id, "en")
        answer_callback(cb_id, "English selected ✅")
        show_welcome(chat_id, "en")

    elif data == "change_lang":
        answer_callback(cb_id)
        show_language_picker(chat_id)

    elif data == "verify":
        lang = get_lang(user_id)
        if is_member(user_id):
            answer_callback(cb_id, "✅")
            send(chat_id, JOINED_OK[lang])
        else:
            answer_callback(cb_id)
            send(chat_id, NOT_JOINED[lang], reply_markup=welcome_keyboard(lang))

    else:
        answer_callback(cb_id)


# ── Tiny health web server (for cloud hosts like Render + an uptime pinger) ─────
class _Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Profit Matrix bot is alive ✅".encode("utf-8"))

    def do_HEAD(self):
        # Uptime monitors (e.g. UptimeRobot) ping with HEAD — answer 200.
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

    def log_message(self, *args):
        pass  # keep logs clean


def start_health_server():
    """Open an HTTP port so a host (Render) sees the service is up and an
    uptime pinger can keep it awake. Only runs when PORT is set (i.e. on a host)."""
    port = int(os.getenv("PORT", "0"))
    if not port:
        return
    srv = HTTPServer(("0.0.0.0", port), _Health)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    logger.info(f"Health server listening on :{port}")


# ── Main loop ───────────────────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN is missing. Copy .env.example to .env and put your "
              "token from @BotFather.")
        sys.exit(1)

    # Quick sanity check / show who we are
    try:
        me = requests.get(f"{API}/getMe", timeout=10).json()
        if me.get("ok"):
            logger.info(f"Bot online: @{me['result']['username']}")
        else:
            logger.error(f"getMe failed: {me}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Cannot reach Telegram: {e}")
        sys.exit(1)

    logger.info(f"Channel: {CHANNEL_URL} | verify={REQUIRE_JOIN and bool(CHANNEL_USERNAME)}")
    start_health_server()  # no-op locally; opens a port on a cloud host
    logger.info("Listening for /start ... (Ctrl+C to stop)")

    offset = 0
    while True:
        try:
            for update in get_updates(offset):
                offset = update["update_id"] + 1
                if "message" in update:
                    handle_message(update["message"])
                elif "callback_query" in update:
                    handle_callback(update["callback_query"])
        except KeyboardInterrupt:
            logger.info("Stopped.")
            break
        except Exception as e:
            logger.warning(f"loop error: {e}")
            time.sleep(3)


if __name__ == "__main__":
    main()
