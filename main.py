#!/usr/bin/env python3
"""
Telegram Group Media Downloader Bot - single file edition. Powered by KD.

Setup:
    pip install "aiogram>=3.13,<4" aiosqlite yt-dlp      (ffmpeg required)
    open this file, fill BOT_TOKEN / OWNER_ID / OWNER_USERNAME / CHANNEL_LINK in the settings block
    python bot.py
Custom emoji IDs: edit CUSTOM_EMOJIS below ("CUSTOM EMOJI CONFIGURATION").
"""
from pathlib import Path
import html
import re
from urllib.parse import parse_qs, urlparse
import hashlib
import hmac
import time
from collections import deque
import asyncio
import logging
import shutil
from uuid import uuid4
import sys
from logging.handlers import RotatingFileHandler
from contextlib import suppress
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
import json
import aiosqlite
from dataclasses import dataclass
import threading
from urllib.parse import urlparse
import yt_dlp
from contextlib import asynccontextmanager
from aiogram.filters import Filter
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta, timezone
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ChatPermissions, Message
from aiogram.types import InlineKeyboardMarkup, Message, ReplyParameters
from aiogram.exceptions import TelegramForbiddenError, TelegramAPIError
from aiogram.types import InlineKeyboardMarkup
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError, TelegramRetryAfter
import importlib.metadata
import os
import sqlite3
from datetime import datetime
from aiogram.types import FSInputFile, InlineKeyboardMarkup, Message, ReplyParameters
from aiogram.types import InlineKeyboardButton as B
from aiogram.types import InlineKeyboardMarkup as KB
from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.filters import JOIN_TRANSITION, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated
from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# ======================================================================
# config/settings.py
# ======================================================================
# ╔══════════════════════════════════════════════════════════════════╗
# ║                  EDIT YOUR SETTINGS HERE                         ║
# ╚══════════════════════════════════════════════════════════════════╝
BOT_TOKEN = "8619783753:AAEu6LwZFjN_3-A68xa4IhbWvyeHYfetIdI"      # from @BotFather
OWNER_ID = 1630422629                          # your numeric Telegram user id
OWNER_NAME = "T10 メ KĐ~[𝖒𝖒]"
OWNER_USERNAME = "KD1948"              # without @
CHANNEL_LINK = "https://t.me/+WkU2G3uzfspiOTFl"

USE_CUSTOM_EMOJI = True
COOKIES_FILE = ""                             # optional cookies.txt path (Instagram/Facebook login content)
PROXY_URL = ""                                # optional proxy for downloads

DEFAULT_MAX_FILE_MB = 50
DEFAULT_DOWNLOAD_TIMEOUT = 300
DEFAULT_CONCURRENT = 3
DEFAULT_USER_COOLDOWN = 10
DEFAULT_GROUP_PER_MINUTE = 10
ENABLED_PLATFORMS = {"youtube", "instagram", "facebook", "twitter", "snapchat"}
# ────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "bot.db"
TEMP_DIR = BASE_DIR / "tmp"
LOG_DIR = BASE_DIR / "logs"


def validate_config() -> None:
    errors = []
    if not BOT_TOKEN or ":" not in BOT_TOKEN or "PASTE_YOUR" in BOT_TOKEN:
        errors.append("set BOT_TOKEN at the top of bot.py")
    if not OWNER_ID or OWNER_ID == 123456789:
        errors.append("set OWNER_ID (your numeric Telegram user id) at the top of bot.py")
    if errors:
        raise SystemExit("Configuration error: " + "; ".join(errors))

# ======================================================================
# config/emojis.py
# ======================================================================
CUSTOM_EMOJIS = {
    "welcome": "5359664288241829619",
    "download": "5372849966689566579",
    "audio": "",
    "success": "4958689671950369798",
    "error": "4958900559139570572",
    "search": "",
    "admin": "6237927637906364256",
    # extra slots used by captions / panels
    "warning": "4958526153955476488",
    "lock": "4956719506027185156",
    "gear": "5116414868357907335",
    "platform": "",
    "title": "",
    "duration": "",
    "size": "",
    "user": "",
    "thumb": "",
}

# ============================================================
# Plain-emoji fallbacks (shown when no custom id is configured)
# ============================================================
FALLBACKS = {
    "welcome": "🚀",
    "download": "📹",
    "audio": "🎵",
    "success": "✅",
    "error": "❌",
    "search": "🔎",
    "admin": "👑",
    "warning": "⚠️",
    "lock": "🔒",
    "gear": "⚙️",
    "platform": "🌐",
    "title": "📝",
    "duration": "⏱",
    "size": "💾",
    "user": "👤",
    "thumb": "🖼",
}

# ======================================================================
# config/meta.py
# ======================================================================
def _b(label, sections, default):
    return {"type": "bool", "label": label, "sections": sections, "default": "1" if default else "0"}


def _i(label, sections, default, lo, hi):
    return {"type": "int", "label": label, "sections": sections, "default": str(default), "min": lo, "max": hi}


def _s(label, sections, default="", hint=""):
    return {"type": "str", "label": label, "sections": sections, "default": default, "hint": hint}


PH = "placeholders: {display_name}"

META = {
    # welcome
    "welcome_enabled": _b("private welcome", ("welcome",), True),
    "welcome_text": _s("welcome text", ("welcome",), "Welcome to the group.", PH),
    "owner_username": _s("owner contact username", ("welcome", "bot"), OWNER_USERNAME, "without @"),
    "channel_link": _s("channel link", ("welcome", "bot"), CHANNEL_LINK, "https://t.me/yourchannel"),
    # force join
    "force_join_enabled": _b("force join", ("force",), False),
    "force_channels": _s("required channels", ("force",), "",
                         "comma separated: @channel  or  -100123456789|https://t.me/+invite"),
    "force_join_text": _s("force join message", ("force",),
                          "Join the required channel to use the downloader."),
    # downloads
    "plat_youtube": _b("youtube", ("dl",), "youtube" in ENABLED_PLATFORMS),
    "plat_instagram": _b("instagram", ("dl",), "instagram" in ENABLED_PLATFORMS),
    "plat_facebook": _b("facebook", ("dl",), "facebook" in ENABLED_PLATFORMS),
    "plat_twitter": _b("x / twitter", ("dl",), "twitter" in ENABLED_PLATFORMS),
    "plat_snapchat": _b("snapchat", ("dl",), "snapchat" in ENABLED_PLATFORMS),
    "audio_enabled": _b("audio button", ("dl",), True),
    "quality_buttons": _b("quality buttons", ("dl",), True),
    "thumbnail_enabled": _b("thumbnail button", ("dl",), True),
    "cache_enabled": _b("file cache", ("dl",), True),
    "max_links": _i("max links per message", ("dl",), 5, 1, 20),
    "max_file_mb": _i("max file size mb", ("dl",), DEFAULT_MAX_FILE_MB, 1, 2000),
    "download_timeout": _i("download timeout sec", ("dl",), DEFAULT_DOWNLOAD_TIMEOUT, 30, 3600),
    "concurrent_downloads": _i("concurrent downloads", ("dl",), DEFAULT_CONCURRENT, 1, 20),
    "user_cooldown": _i("user cooldown sec", ("dl",), DEFAULT_USER_COOLDOWN, 0, 3600),
    "group_per_minute": _i("group limit per min", ("dl",), DEFAULT_GROUP_PER_MINUTE, 0, 600),
    "temp_ttl_minutes": _i("temp file ttl min", ("dl",), 60, 5, 1440),
    "status_cleanup_seconds": _i("status cleanup sec", ("dl",), 2, 0, 60),
    # filters
    "filter_enabled": _b("telegram link filter", ("filters",), True),
    "filter_links": _b("detect links", ("filters",), True),
    "filter_usernames": _b("detect usernames", ("filters",), True),
    "filter_exempt_admins": _b("exempt admins", ("filters",), True),
    "filter_notice": _b("deletion notice", ("filters",), False),
    # warn + flood
    "warn_enabled": _b("warn system", ("spam",), True),
    "warn_limit": _i("warnings before action", ("spam",), 3, 1, 10),
    "warn_action": _s("warn action", ("spam",), "mute", "mute or ban"),
    "warn_mute_minutes": _i("warn mute minutes", ("spam",), 60, 1, 10080),
    "flood_enabled": _b("anti flood", ("spam",), True),
    "flood_limit": _i("flood: max link messages", ("spam",), 5, 2, 50),
    "flood_window": _i("flood: window sec", ("spam",), 30, 5, 600),
    "flood_mute_minutes": _i("flood mute minutes", ("spam",), 5, 1, 1440),
    # system
    "auto_update": _b("auto update yt-dlp", ("system",), True),
    "auto_update_hours": _i("update check hours", ("system",), 24, 1, 168),
    # maintenance
    "maintenance_enabled": _b("maintenance mode", ("maint",), False),
    "maintenance_text": _s("maintenance message", ("maint",),
                           "Bot is under maintenance. Please try again later."),
    "maintenance_bypass": _b("owner/admin bypass", ("maint",), True),
    # bot settings
    "bot_name": _s("bot name", ("bot",), "Media Downloader"),
    "owner_name": _s("owner name", ("bot",), OWNER_NAME),
    "msg_detecting": _s("status: detecting", ("bot",), "Detecting platform..."),
    "msg_detected": _s("status: detected", ("bot",), "{platform} link detected", "placeholders: {platform}"),
    "msg_preparing": _s("status: preparing", ("bot",), "Preparing..."),
    "msg_downloading": _s("status: downloading", ("bot",), "Downloading video..."),
    "msg_processing": _s("status: processing", ("bot",), "Processing..."),
    "msg_completed": _s("status: completed", ("bot",), "Completed"),
    "msg_audio": _s("status: audio", ("bot",), "Downloading audio..."),
}

# ======================================================================
# utils/formatting.py
# ======================================================================
_SC = str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")
_PLACEHOLDER = re.compile(r"(\{\w+\})")


def esc(text) -> str:
    return html.escape(str(text), quote=False)


def sc(text) -> str:
    """Small-caps + HTML escape. Never use on URLs, usernames or ids."""
    return esc(str(text).lower().translate(_SC))


def render_template(template: str, values: dict) -> str:
    """Small-cap the literal text, insert placeholder values untouched (already HTML)."""
    out = []
    for part in _PLACEHOLDER.split(template or ""):
        if _PLACEHOLDER.fullmatch(part) and part[1:-1] in values:
            out.append(str(values[part[1:-1]]))
        else:
            out.append(sc(part))
    return "".join(out)


def emoji_id(key: str) -> str:
    return CUSTOM_EMOJIS.get(key, "") if USE_CUSTOM_EMOJI else ""


def em(key: str) -> str:
    fb = FALLBACKS.get(key, "•")
    cid = emoji_id(key)
    return f'<tg-emoji emoji-id="{cid}">{fb}</tg-emoji>' if cid else fb


def mention(user_id: int, name: str) -> str:
    return f'<a href="tg://user?id={int(user_id)}">{esc(name or "user")}</a>'


def trim(text, limit: int) -> str:
    text = (text or "").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def fmt_size(n) -> str:
    n = float(n or 0)
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def fmt_duration(sec) -> str:
    sec = int(sec or 0)
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fmt_uptime(sec: float) -> str:
    d, r = divmod(int(sec), 86400)
    h, r = divmod(r, 3600)
    return f"{d}d {h}h {r // 60}m"


def bar(pct: int, width: int = 10) -> str:
    filled = round(width * max(0, min(100, pct)) / 100)
    return "▰" * filled + "▱" * (width - filled)

# ======================================================================
# utils/validators.py
# ======================================================================
URL_RE = re.compile(r"https?://[^\s<>\"']+", re.I)
TG_LINK_RE = re.compile(
    r"(?<![\w.@-])(?:(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me|telegram\.dog|telesco\.pe)(?:/[^\s]*)?"
    r"|tg://[^\s]+)",
    re.I,
)
USERNAME_RE = re.compile(r"(?<![\w.@/+-])@[A-Za-z][A-Za-z0-9_]{3,31}\b")


def extract_urls(text, entities) -> list[str]:
    urls = [u.rstrip(".,);]!?") for u in URL_RE.findall(text or "")]
    for e in entities or []:
        if e.type == "text_link" and e.url:
            urls.append(e.url)
    return urls


def has_telegram_link(text, entities) -> bool:
    if TG_LINK_RE.search(text or ""):
        return True
    return any(e.type == "text_link" and e.url and TG_LINK_RE.search(e.url) for e in entities or [])


def has_telegram_username(text, entities) -> bool:
    if USERNAME_RE.search(text or ""):
        return True
    return any(e.type in ("mention", "text_mention") for e in entities or [])


_TRACKING = {"fbclid", "igshid", "si", "feature", "ref", "s", "t", "pp"}


def canon_url(url: str) -> str:
    """Stable key for the same media (used for the file cache and de-duplication)."""
    u = urlparse(url)
    host = re.sub(r"^(www\.|m\.|mobile\.)", "", (u.hostname or "").lower())
    path, q = u.path.rstrip("/"), parse_qs(u.query)
    if host == "youtu.be":
        return "youtube:" + path.lstrip("/")
    if host.endswith("youtube.com"):
        if "v" in q:
            return "youtube:" + q["v"][0]
        parts = path.split("/")
        if len(parts) > 2 and parts[1] in ("shorts", "live", "embed"):
            return "youtube:" + parts[2]
    if host in ("twitter.com", "x.com"):
        host = "x.com"
    keep = sorted((k, v[0]) for k, v in q.items() if not k.startswith("utm_") and k not in _TRACKING)
    return f"{host}{path}" + ("?" + "&".join(f"{k}={v}" for k, v in keep) if keep else "")

# ======================================================================
# utils/security.py
# ======================================================================
_KEY = hashlib.sha256(("audio-cb:" + BOT_TOKEN).encode()).digest()


def sign(download_id: int, user_id: int) -> str:
    return hmac.new(_KEY, f"{download_id}:{user_id}".encode(), hashlib.sha256).hexdigest()[:12]


def verify(download_id: int, user_id: int, sig: str) -> bool:
    return hmac.compare_digest(sign(download_id, user_id), sig or "")

# ======================================================================
# utils/ratelimit.py
# ======================================================================
class RateLimiter:
    def __init__(self):
        self._user: dict[int, float] = {}
        self._group: dict[int, deque] = {}

    def allow(self, user_id: int, chat_id: int, cooldown: int, per_minute: int) -> bool:
        now = time.monotonic()
        if len(self._user) > 10000:
            self._user = {k: v for k, v in self._user.items() if now - v < 3600}
        last = self._user.get(user_id)
        if cooldown and last is not None and now - last < cooldown:
            return False
        q = self._group.setdefault(chat_id, deque())
        while q and now - q[0] > 60:
            q.popleft()
        if per_minute and len(q) >= per_minute:
            return False
        q.append(now)
        self._user[user_id] = now
        return True


class FloodGuard:
    """Counts link messages per user/chat in a sliding window."""

    def __init__(self):
        self._h: dict[tuple, deque] = {}

    def hit(self, chat_id: int, user_id: int, limit: int, window: int) -> bool:
        """Record one link message. True when the limit is exceeded."""
        now = time.monotonic()
        if len(self._h) > 5000:
            self._h = {k: q for k, q in self._h.items() if q and now - q[-1] < window}
        q = self._h.setdefault((chat_id, user_id), deque())
        while q and now - q[0] > window:
            q.popleft()
        q.append(now)
        return len(q) > limit

    def reset(self, chat_id: int, user_id: int) -> None:
        self._h.pop((chat_id, user_id), None)

# ======================================================================
# utils/cleanup.py
# ======================================================================
log = logging.getLogger(__name__)


def new_workdir():
    p = TEMP_DIR / uuid4().hex
    p.mkdir(parents=True, exist_ok=True)
    return p


def remove_dir(path) -> None:
    shutil.rmtree(path, ignore_errors=True)


def wipe_all() -> None:
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def sweep(ttl_minutes: int) -> None:
    cutoff = time.time() - ttl_minutes * 60
    for child in TEMP_DIR.iterdir():
        try:
            if child.stat().st_mtime < cutoff:
                shutil.rmtree(child, ignore_errors=True)
        except OSError:
            pass


async def sweeper(db) -> None:
    while True:
        await asyncio.sleep(600)
        try:
            await asyncio.to_thread(sweep, db.get_int("temp_ttl_minutes"))
        except Exception:
            log.exception("temp sweep failed")

# ======================================================================
# utils/logging.py
# ======================================================================
_TOKEN_RE = re.compile(r"\d{6,12}:[A-Za-z0-9_-]{30,}")


class RedactFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = _TOKEN_RE.sub("[redacted]", record.getMessage())
        if BOT_TOKEN:
            msg = msg.replace(BOT_TOKEN, "[redacted]")
        record.msg, record.args = msg, ()
        return True


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handlers = [
        logging.StreamHandler(sys.stdout),
        RotatingFileHandler(LOG_DIR / "bot.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"),
    ]
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    for h in handlers:
        h.setFormatter(fmt)
        h.addFilter(RedactFilter())
        root.addHandler(h)
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)

# ======================================================================
# utils/telegram.py
# ======================================================================
log = logging.getLogger(__name__)
ICON_SUPPORTED = "icon_custom_emoji_id" in InlineKeyboardButton.model_fields
_tasks: set = set()


async def try_delete(message: Message) -> bool:
    try:
        await message.delete()
        return True
    except TelegramAPIError:
        return False


def schedule_delete(bot: Bot, chat_id: int, message_id: int, delay: float) -> None:
    async def _run():
        if delay:
            await asyncio.sleep(delay)
        with suppress(TelegramAPIError):
            await bot.delete_message(chat_id, message_id)

    t = asyncio.create_task(_run())
    _tasks.add(t)
    t.add_done_callback(_tasks.discard)


async def safe_edit(bot: Bot, chat_id: int, message_id: int, text: str, kb: InlineKeyboardMarkup | None = None):
    try:
        await bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=kb)
    except TelegramBadRequest as e:
        if "not modified" not in str(e).lower():
            log.warning("edit failed: %s", e)
    except TelegramAPIError as e:
        log.warning("edit failed: %s", e)


def btn(text: str, key: str | None = None, **kw) -> InlineKeyboardButton:
    """Small-caps button; uses a custom emoji icon when the library/API supports it."""
    label = sc(text)
    if key:
        cid = emoji_id(key)
        if cid and ICON_SUPPORTED:
            kw["icon_custom_emoji_id"] = cid
        else:
            label = f"{FALLBACKS.get(key, '')} {label}".strip()
    return InlineKeyboardButton(text=label, **kw)


class Status:
    """One temporary message that is edited through the stages, then removed."""

    def __init__(self, bot: Bot, chat_id: int, thread_id=None, reply=None):
        self.bot, self.chat_id, self.thread_id, self.reply = bot, chat_id, thread_id, reply
        self.msg: Message | None = None
        self._last = None
        self.prefix = ""
        self._lock = asyncio.Lock()

    async def show(self, text: str) -> None:
        text = f"{self.prefix}{text}"
        async with self._lock:
            if text == self._last:
                return
            self._last = text
            try:
                if self.msg is None:
                    self.msg = await self.bot.send_message(
                        self.chat_id, text, message_thread_id=self.thread_id,
                        reply_parameters=self.reply, disable_notification=True,
                    )
                else:
                    await self.bot.edit_message_text(text, chat_id=self.chat_id, message_id=self.msg.message_id)
            except TelegramAPIError as e:
                log.debug("status update failed: %s", e)

    def delete_later(self, delay: float) -> None:
        if self.msg:
            schedule_delete(self.bot, self.chat_id, self.msg.message_id, delay)

# ======================================================================
# database/database.py
# ======================================================================
log = logging.getLogger(__name__)

SCHEMA_V1 = """
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    display_name TEXT,
    first_seen TEXT DEFAULT (datetime('now')),
    last_seen TEXT DEFAULT (datetime('now')),
    download_count INTEGER DEFAULT 0,
    blocked INTEGER DEFAULT 0,
    dm_ok INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS groups(
    chat_id INTEGER PRIMARY KEY,
    title TEXT,
    added_at TEXT DEFAULT (datetime('now')),
    enabled INTEGER DEFAULT 1,
    active INTEGER DEFAULT 1,
    settings TEXT DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS downloads(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, group_id INTEGER,
    platform TEXT, media_type TEXT, url TEXT,
    status TEXT DEFAULT 'pending', error_code TEXT,
    title TEXT, size INTEGER, duration INTEGER,
    audio_state INTEGER DEFAULT 0,
    ts TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_dl_ts ON downloads(ts);
CREATE INDEX IF NOT EXISTS idx_dl_user ON downloads(user_id);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
"""
# Add future schema changes as MIGRATIONS[2] = "ALTER TABLE ...;" etc.
SCHEMA_V2 = """
CREATE TABLE IF NOT EXISTS warns(
    chat_id INTEGER, user_id INTEGER, n INTEGER DEFAULT 0, updated TEXT DEFAULT (datetime('now')),
    PRIMARY KEY(chat_id, user_id)
);
CREATE TABLE IF NOT EXISTS cache(
    key TEXT, kind TEXT, quality INTEGER, file_id TEXT, file_type TEXT,
    title TEXT, duration INTEGER, size INTEGER, uploader TEXT, width INTEGER, height INTEGER,
    ts TEXT DEFAULT (datetime('now')),
    PRIMARY KEY(key, kind, quality)
);
"""
MIGRATIONS = {1: SCHEMA_V1, 2: SCHEMA_V2}
TOUCH_INTERVAL = 300


class Database:
    def __init__(self, path: Path):
        self.path = path
        self._db: aiosqlite.Connection | None = None
        self._lock = asyncio.Lock()
        self._cache: dict[str, str] = {}
        self._touched: dict[tuple, float] = {}

    # ---------- lifecycle ----------
    async def connect(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(self.path)
        self._db.row_factory = aiosqlite.Row
        await self._db.execute("PRAGMA journal_mode=WAL")
        cur = await self._db.execute("PRAGMA user_version")
        version = (await cur.fetchone())[0]
        for v in sorted(MIGRATIONS):
            if v > version:
                await self._db.executescript(MIGRATIONS[v])
                await self._db.execute(f"PRAGMA user_version={v}")
                await self._db.commit()
        self._cache = {k: m["default"] for k, m in META.items()}
        for row in await self._all("SELECT key, value FROM settings"):
            self._cache[row["key"]] = row["value"]
        log.info("database ready: %s", self.path)

    async def close(self) -> None:
        if self._db:
            await self._db.close()

    async def _exec(self, sql, params=()):
        async with self._lock:
            cur = await self._db.execute(sql, params)
            await self._db.commit()
            return cur.rowcount, cur.lastrowid

    async def _all(self, sql, params=()):
        async with self._lock:
            cur = await self._db.execute(sql, params)
            rows = await cur.fetchall()
            await cur.close()
            return rows

    async def _one(self, sql, params=()):
        rows = await self._all(sql, params)
        return rows[0] if rows else None

    # ---------- settings ----------
    def get(self, key: str) -> str:
        return self._cache.get(key, META.get(key, {}).get("default", ""))

    def get_bool(self, key: str) -> bool:
        return self.get(key) == "1"

    def get_int(self, key: str) -> int:
        try:
            return int(self.get(key))
        except ValueError:
            return int(META[key]["default"])

    async def set(self, key: str, value: str) -> None:
        self._cache[key] = value
        await self._exec(
            "INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )

    # ---------- users ----------
    def _due(self, kind, ident) -> bool:
        now = time.monotonic()
        last = self._touched.get((kind, ident))
        if last is not None and now - last < TOUCH_INTERVAL:
            return False
        self._touched[(kind, ident)] = now
        return True

    async def upsert_user(self, user_id: int, name: str) -> None:
        if not self._due("u", user_id):
            return
        await self._exec(
            "INSERT INTO users(user_id,display_name) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET "
            "display_name=excluded.display_name, last_seen=datetime('now')",
            (user_id, name or ""),
        )

    async def set_dm(self, user_id: int, ok: bool) -> None:
        await self._exec("UPDATE users SET dm_ok=? WHERE user_id=?", (int(ok), user_id))

    async def is_blocked(self, user_id: int) -> bool:
        row = await self._one("SELECT blocked FROM users WHERE user_id=?", (user_id,))
        return bool(row and row["blocked"])

    async def set_blocked(self, user_id: int, blocked: bool) -> None:
        await self._exec("UPDATE users SET blocked=? WHERE user_id=?", (int(blocked), user_id))

    async def get_user(self, user_id: int):
        return await self._one("SELECT * FROM users WHERE user_id=?", (user_id,))

    async def search_users(self, q: str, limit: int = 8):
        q = q.strip()
        if q.isdigit():
            return await self._all("SELECT * FROM users WHERE CAST(user_id AS TEXT) LIKE ? LIMIT ?", (f"{q}%", limit))
        return await self._all("SELECT * FROM users WHERE display_name LIKE ? LIMIT ?", (f"%{q}%", limit))

    async def recent_users(self, limit: int = 10):
        return await self._all("SELECT * FROM users ORDER BY last_seen DESC LIMIT ?", (limit,))

    async def count_users(self, blocked: bool = False) -> int:
        sql = "SELECT COUNT(*) c FROM users" + (" WHERE blocked=1" if blocked else "")
        return (await self._one(sql))["c"]

    async def bump_downloads(self, user_id: int) -> None:
        await self._exec("UPDATE users SET download_count=download_count+1 WHERE user_id=?", (user_id,))

    async def broadcast_users(self):
        return await self._all("SELECT user_id FROM users WHERE blocked=0 AND dm_ok=1")

    # ---------- groups ----------
    async def upsert_group(self, chat_id: int, title: str) -> None:
        if not self._due("g", chat_id):
            return
        await self._exec(
            "INSERT INTO groups(chat_id,title) VALUES(?,?) ON CONFLICT(chat_id) DO UPDATE SET "
            "title=excluded.title, active=1",
            (chat_id, title or ""),
        )

    async def get_group(self, chat_id: int):
        return await self._one("SELECT * FROM groups WHERE chat_id=?", (chat_id,))

    async def set_group_active(self, chat_id: int, active: bool) -> None:
        await self._exec("UPDATE groups SET active=? WHERE chat_id=?", (int(active), chat_id))

    async def set_group_enabled(self, chat_id: int, enabled: bool) -> None:
        await self._exec("UPDATE groups SET enabled=? WHERE chat_id=?", (int(enabled), chat_id))

    async def list_groups(self, limit: int = 20):
        return await self._all("SELECT * FROM groups ORDER BY added_at DESC LIMIT ?", (limit,))

    async def count_groups(self, active_only: bool = False) -> int:
        sql = "SELECT COUNT(*) c FROM groups" + (" WHERE active=1 AND enabled=1" if active_only else "")
        return (await self._one(sql))["c"]

    async def broadcast_groups(self):
        return await self._all("SELECT chat_id FROM groups WHERE active=1 AND enabled=1")

    @staticmethod
    def group_flag(row, key: str, default: bool = True) -> bool:
        try:
            return bool(json.loads(row["settings"] or "{}").get(key, default))
        except (TypeError, ValueError):
            return default

    async def set_group_flag(self, chat_id: int, key: str, value: bool) -> None:
        row = await self.get_group(chat_id)
        data = json.loads(row["settings"] or "{}") if row else {}
        data[key] = value
        await self._exec("UPDATE groups SET settings=? WHERE chat_id=?", (json.dumps(data), chat_id))

    # ---------- downloads ----------
    async def add_download(self, user_id, group_id, platform, media_type, url) -> int:
        _, rid = await self._exec(
            "INSERT INTO downloads(user_id,group_id,platform,media_type,url) VALUES(?,?,?,?,?)",
            (user_id, group_id, platform, media_type, url),
        )
        return rid

    async def finish_download(self, dl_id, status, error=None, title=None, size=None, duration=None) -> None:
        await self._exec(
            "UPDATE downloads SET status=?, error_code=?, title=?, size=?, duration=? WHERE id=?",
            (status, error, title, size, int(duration) if duration else None, dl_id),
        )

    async def get_download(self, dl_id: int):
        return await self._one("SELECT * FROM downloads WHERE id=?", (dl_id,))

    async def claim_audio(self, dl_id: int) -> bool:
        n, _ = await self._exec("UPDATE downloads SET audio_state=1 WHERE id=? AND audio_state=0", (dl_id,))
        return n == 1

    async def set_audio_state(self, dl_id: int, state: int) -> None:
        await self._exec("UPDATE downloads SET audio_state=? WHERE id=?", (state, dl_id))

    # ---------- statistics ----------
    @staticmethod
    def _where(status, media, hours, user_id, group_id):
        sql, p = " WHERE 1=1", []
        if status:
            sql += " AND status=?"; p.append(status)
        if media:
            sql += " AND media_type=?"; p.append(media)
        if hours:
            sql += " AND ts>=datetime('now', ?)"; p.append(f"-{int(hours)} hours")
        if user_id:
            sql += " AND user_id=?"; p.append(user_id)
        if group_id:
            sql += " AND group_id=?"; p.append(group_id)
        return sql, p

    async def downloads_count(self, *, media=None, status="done", hours=None, user_id=None, group_id=None) -> int:
        w, p = self._where(status, media, hours, user_id, group_id)
        return (await self._one("SELECT COUNT(*) c FROM downloads" + w, p))["c"]

    async def platform_usage(self, hours=None):
        w, p = self._where("done", "video", hours, None, None)
        return await self._all("SELECT platform, COUNT(*) c FROM downloads" + w + " GROUP BY platform ORDER BY c DESC", p)

    async def error_breakdown(self, hours=None):
        w, p = self._where("failed", None, hours, None, None)
        return await self._all("SELECT COALESCE(error_code,'failed') e, COUNT(*) c FROM downloads" + w + " GROUP BY e ORDER BY c DESC", p)

    # ---------- per-group values ----------
    @staticmethod
    def group_get(row, key: str, default=None):
        try:
            return json.loads(row["settings"] or "{}").get(key, default)
        except (TypeError, ValueError):
            return default

    # ---------- warns ----------
    async def add_warn(self, chat_id: int, user_id: int) -> int:
        await self._exec(
            "INSERT INTO warns(chat_id,user_id,n) VALUES(?,?,1) ON CONFLICT(chat_id,user_id) "
            "DO UPDATE SET n=n+1, updated=datetime('now')", (chat_id, user_id))
        return (await self._one("SELECT n FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id)))["n"]

    async def get_warns(self, chat_id: int, user_id: int) -> int:
        row = await self._one("SELECT n FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        return row["n"] if row else 0

    async def reset_warns(self, chat_id: int, user_id: int) -> None:
        await self._exec("DELETE FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id))

    # ---------- file_id cache ----------
    async def cache_get(self, key: str, kind: str, quality: int):
        return await self._one("SELECT * FROM cache WHERE key=? AND kind=? AND quality=?", (key, kind, quality))

    async def cache_put(self, key, kind, quality, file_id, file_type, result) -> None:
        await self._exec(
            "INSERT INTO cache(key,kind,quality,file_id,file_type,title,duration,size,uploader,width,height) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(key,kind,quality) DO UPDATE SET "
            "file_id=excluded.file_id, file_type=excluded.file_type, title=excluded.title, "
            "duration=excluded.duration, size=excluded.size, uploader=excluded.uploader, "
            "width=excluded.width, height=excluded.height, ts=datetime('now')",
            (key, kind, quality, file_id, file_type, result.title, int(result.duration) if result.duration else None,
             result.size, result.uploader, result.width, result.height))

    async def cache_delete(self, key: str, kind: str, quality: int) -> None:
        await self._exec("DELETE FROM cache WHERE key=? AND kind=? AND quality=?", (key, kind, quality))

    async def cache_clear(self) -> int:
        n, _ = await self._exec("DELETE FROM cache")
        return n

    async def cache_count(self) -> int:
        return (await self._one("SELECT COUNT(*) c FROM cache"))["c"]

    # ---------- rankings ----------
    async def top_users(self, limit: int = 5):
        return await self._all(
            "SELECT user_id, display_name, download_count FROM users WHERE download_count>0 "
            "ORDER BY download_count DESC LIMIT ?", (limit,))

    async def top_groups(self, limit: int = 5):
        return await self._all(
            "SELECT d.group_id AS chat_id, COALESCE(g.title,'') AS title, COUNT(*) c FROM downloads d "
            "LEFT JOIN groups g ON g.chat_id=d.group_id WHERE d.status='done' AND d.media_type='video' "
            "GROUP BY d.group_id ORDER BY c DESC LIMIT ?", (limit,))

# ======================================================================
# downloader/base.py
# ======================================================================
class DownloadError(Exception):
    """code: private | unsupported | unavailable | restricted | too_large | timeout | upload | failed"""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(code)
        self.code = code
        self.detail = detail


@dataclass
class MediaResult:
    path: Path
    title: str
    duration: float | None
    size: int
    uploader: str | None = None
    width: int | None = None
    height: int | None = None
    thumb: Path | None = None


class Provider:
    """Interface every platform provider implements."""

    key: str = ""      # settings key suffix, e.g. "youtube"
    label: str = ""    # display name
    domains: tuple = ()

    def matches(self, url: str) -> bool:
        raise NotImplementedError

    async def download(self, url, workdir, *, max_bytes, timeout, kind, state, quality=720) -> MediaResult:
        raise NotImplementedError

    async def fetch_thumbnail(self, url, workdir):
        raise NotImplementedError

# ======================================================================
# downloader/ytdlp.py
# ======================================================================
log = logging.getLogger(__name__)
_SKIP = {".part", ".ytdl", ".json", ".webp", ".jpg", ".jpeg", ".png", ".temp"}
_IMG = {".jpg", ".jpeg", ".png", ".webp"}


async def make_thumb(src, dst, max_side: int = 320, max_bytes: int = 200_000):
    """Convert/resize an image to JPEG with ffmpeg (Telegram thumbnails: <=320px, <=200KB)."""
    vf = f"scale='if(gt(iw,ih),min({max_side},iw),-2)':'if(gt(iw,ih),-2,min({max_side},ih))'"
    for q in ("4", "8", "14"):
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", vf, "-frames:v", "1", "-q:v", q,
                str(dst), stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
            await asyncio.wait_for(proc.wait(), 30)
        except Exception:
            return None
        if dst.exists() and dst.stat().st_size <= max_bytes:
            return dst
    return None


async def _find_thumb(workdir):
    try:
        img = next((p for p in sorted(workdir.iterdir())
                    if p.suffix.lower() in _IMG and p.name not in ("cover.jpg", "thumb.jpg")), None)
        return await make_thumb(img, workdir / "cover.jpg") if img else None
    except Exception:
        log.debug("thumbnail conversion failed", exc_info=True)
        return None


class _Log:
    """Captures yt-dlp messages we care about; keeps the console quiet."""

    def __init__(self):
        self.too_large = False

    def _chk(self, msg):
        if "max-filesize" in str(msg):
            self.too_large = True

    def debug(self, msg):
        self._chk(msg)

    info = warning = error = debug


def classify(message: str) -> str:
    m = message.lower()
    if "unsupported url" in m:
        return "unsupported"
    if any(k in m for k in ("private", "login", "log in", "sign in", "cookies", "authentication",
                            "members-only", "members only", "confirm your age", "age-restricted")):
        return "private"
    if any(k in m for k in ("geo", "not available in your country", "blocked it")):
        return "restricted"
    if any(k in m for k in ("not available", "removed", "deleted", "unavailable", "does not exist",
                            "no video", "404", "not found")):
        return "unavailable"
    return "failed"


class YtDlpProvider(Provider):
    def matches(self, url: str) -> bool:
        host = (urlparse(url).hostname or "").lower()
        return any(host == d or host.endswith("." + d) for d in self.domains)

    def _opts(self, workdir: Path, max_bytes: int, kind: str, hook, logger, quality: int = 720) -> dict:
        opts = {
            "outtmpl": str(workdir / "%(id).60s.%(ext)s"),
            "quiet": True, "no_warnings": True, "noplaylist": True, "logger": logger,
            "max_filesize": max_bytes, "socket_timeout": 20, "retries": 3,
            "restrictfilenames": True, "progress_hooks": [hook], "concurrent_fragment_downloads": 4,
            "writethumbnail": True,
        }
        if COOKIES_FILE:
            opts["cookiefile"] = COOKIES_FILE
        if PROXY_URL:
            opts["proxy"] = PROXY_URL
        if kind == "audio":
            opts["format"] = "bestaudio/best"
            opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
        else:
            n, h = max_bytes, quality
            opts["format"] = (
                f"bv*[ext=mp4][height<=?{h}][filesize<?{n}]+ba[ext=m4a]/"
                f"b[ext=mp4][height<=?{h}][filesize<?{n}]/b[height<=?{h}][filesize<?{n}]/b"
            )
            opts["merge_output_format"] = "mp4"
        return opts

    @staticmethod
    def _extract(url, opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=True)

    async def download(self, url, workdir, *, max_bytes, timeout, kind, state, quality=720) -> MediaResult:
        workdir.mkdir(parents=True, exist_ok=True)
        cancel = threading.Event()
        logger = _Log()

        def hook(d):
            if cancel.is_set():
                raise yt_dlp.utils.DownloadCancelled("cancelled")
            if d.get("status") == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                if total:
                    state["pct"] = min(99, int(d.get("downloaded_bytes", 0) * 100 / total))

        opts = self._opts(workdir, max_bytes, kind, hook, logger, quality)
        loop = asyncio.get_running_loop()
        try:
            info = await asyncio.wait_for(loop.run_in_executor(None, self._extract, url, opts), timeout)
        except asyncio.TimeoutError:
            cancel.set()
            raise DownloadError("timeout")
        except yt_dlp.utils.YoutubeDLError as e:
            code = "too_large" if logger.too_large else classify(str(e))
            log.warning("yt-dlp failed (%s): %s", code, str(e)[:300])
            raise DownloadError(code, str(e)[:300]) from e
        except Exception as e:
            log.exception("unexpected downloader error")
            raise DownloadError("failed") from e

        files = [p for p in workdir.iterdir() if p.is_file() and p.suffix.lower() not in _SKIP]
        if kind == "audio":
            files = [p for p in files if p.suffix.lower() == ".mp3"] or files
        if not files:
            raise DownloadError("too_large" if logger.too_large else "failed")
        path = max(files, key=lambda p: p.stat().st_size)
        size = path.stat().st_size
        if size > max_bytes:
            raise DownloadError("too_large")
        info = info or {}
        thumb = await _find_thumb(workdir)
        return MediaResult(
            path=path, title=info.get("title") or path.stem, duration=info.get("duration"), size=size,
            uploader=info.get("uploader") or info.get("channel"), width=info.get("width"), height=info.get("height"), thumb=thumb,
        )

    async def fetch_thumbnail(self, url, workdir, timeout: int = 60):
        """Download only the thumbnail image and return it as a JPEG path (or None)."""
        workdir.mkdir(parents=True, exist_ok=True)
        opts = {"outtmpl": str(workdir / "%(id).60s.%(ext)s"), "quiet": True, "no_warnings": True,
                "noplaylist": True, "skip_download": True, "writethumbnail": True,
                "socket_timeout": 20, "retries": 2, "logger": _Log()}
        if COOKIES_FILE:
            opts["cookiefile"] = COOKIES_FILE
        if PROXY_URL:
            opts["proxy"] = PROXY_URL
        loop = asyncio.get_running_loop()
        try:
            await asyncio.wait_for(loop.run_in_executor(None, self._extract, url, opts), timeout)
        except Exception as e:
            log.warning("thumbnail fetch failed: %s", str(e)[:200])
            return None
        img = next((p for p in sorted(workdir.iterdir()) if p.suffix.lower() in _IMG), None)
        return await make_thumb(img, workdir / "thumb.jpg", 1280, 9_000_000) if img else None

# ======================================================================
# downloader/youtube.py
# ======================================================================
class YouTubeProvider(YtDlpProvider):
    key = "youtube"
    label = "YouTube"
    domains = ("youtube.com", "youtu.be",)

# ======================================================================
# downloader/instagram.py
# ======================================================================
class InstagramProvider(YtDlpProvider):
    key = "instagram"
    label = "Instagram"
    domains = ("instagram.com", "instagr.am",)

# ======================================================================
# downloader/facebook.py
# ======================================================================
class FacebookProvider(YtDlpProvider):
    key = "facebook"
    label = "Facebook"
    domains = ("facebook.com", "fb.watch", "fb.com",)

# ======================================================================
# downloader/twitter.py
# ======================================================================
class TwitterProvider(YtDlpProvider):
    key = "twitter"
    label = "X / Twitter"
    domains = ("twitter.com", "x.com",)

# ======================================================================
# downloader/snapchat.py
# ======================================================================
class SnapchatProvider(YtDlpProvider):
    key = "snapchat"
    label = "Snapchat"
    domains = ("snapchat.com",)

# ======================================================================
# downloader/manager.py
# ======================================================================
# To add a platform: create a provider module and append it here.
PROVIDERS = [YouTubeProvider, InstagramProvider, FacebookProvider, TwitterProvider, SnapchatProvider]


class DownloadManager:
    def __init__(self, concurrency: int):
        self.providers = [p() for p in PROVIDERS]
        self._limit = concurrency
        self._sem = asyncio.Semaphore(concurrency)
        self._users: set[int] = set()
        self.active = 0
        self.waiting = 0

    def detect(self, url: str):
        for p in self.providers:
            if p.matches(url):
                return p
        return None

    def provider(self, key: str):
        return next((p for p in self.providers if p.key == key), None)

    def set_concurrency(self, n: int) -> None:
        if n != self._limit:
            self._limit, self._sem = n, asyncio.Semaphore(n)

    def reserve(self, user_id: int) -> bool:
        """One active request per user."""
        if user_id in self._users:
            return False
        self._users.add(user_id)
        return True

    def release(self, user_id: int) -> None:
        self._users.discard(user_id)

    @asynccontextmanager
    async def slot(self):
        sem = self._sem
        self.waiting += 1
        try:
            await sem.acquire()
        finally:
            self.waiting -= 1
        self.active += 1
        try:
            yield
        finally:
            self.active -= 1
            sem.release()

# ======================================================================
# bot/filters.py
# ======================================================================
class IsOwnerPrivate(Filter):
    """Owner panel access: numeric user id AND private chat. Usernames are never trusted."""

    async def __call__(self, event) -> bool:
        user = event.from_user
        msg = event if isinstance(event, Message) else event.message
        return bool(user and msg and msg.chat.type == "private" and user.id == OWNER_ID)

# ======================================================================
# bot/states.py
# ======================================================================
class Edit(StatesGroup):
    value = State()


class Find(StatesGroup):
    query = State()


class Cast(StatesGroup):
    content = State()
    confirm = State()

# ======================================================================
# bot/services/permissions.py
# ======================================================================
log = logging.getLogger(__name__)
_cache: dict[tuple, tuple] = {}
_notified: dict[str, float] = {}


async def is_group_admin(bot: Bot, chat_id: int, user_id: int, ttl: int = 30) -> bool:
    key, now = (chat_id, user_id), time.monotonic()
    hit = _cache.get(key)
    if hit and now - hit[0] < ttl:
        return hit[1]
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        ok = member.status in ("creator", "administrator")
    except TelegramAPIError:
        ok = False
    if len(_cache) > 5000:
        _cache.clear()
    _cache[key] = (now, ok)
    return ok


async def is_admin_message(bot: Bot, message: Message) -> bool:
    if message.sender_chat and message.sender_chat.id == message.chat.id:
        return True  # anonymous admin
    user = message.from_user
    if not user or user.is_bot:
        return False
    return user.id == OWNER_ID or await is_group_admin(bot, message.chat.id, user.id)


async def diagnose(bot: Bot, chat_id: int) -> dict:
    try:
        me = await bot.get_chat_member(chat_id, bot.id)
    except TelegramAPIError:
        return {"admin": False, "delete": False}
    return {
        "admin": me.status == "administrator",
        "delete": bool(getattr(me, "can_delete_messages", False)),
    }


async def notify_owner_once(bot: Bot, key: str, text: str, every: int = 3600) -> None:
    now = time.monotonic()
    if now - _notified.get(key, -every) < every:
        return
    _notified[key] = now
    try:
        await bot.send_message(OWNER_ID, text)
    except TelegramAPIError:
        log.warning("could not notify owner: %s", text)


def missing_rights_text(title: str, rights: dict) -> str:
    return (
        f"{em('warning')} {sc('permission problem in')} {title or ''}\n"
        f"{sc('bot is admin')}: {'✅' if rights['admin'] else '❌'}\n"
        f"{sc('can delete messages')}: {'✅' if rights['delete'] else '❌'}"
    )


async def restrict_user(bot: Bot, chat_id: int, user_id: int, action: str, minutes: int) -> bool:
    """Mute (temporary) or ban a member. Needs the bot to be admin with restrict rights."""
    try:
        if action == "ban":
            await bot.ban_chat_member(chat_id, user_id)
        else:
            until = datetime.now(timezone.utc) + timedelta(minutes=max(1, minutes))
            await bot.restrict_chat_member(chat_id, user_id, permissions=ChatPermissions(can_send_messages=False),
                                           until_date=until)
        return True
    except TelegramAPIError as e:
        log.warning("restrict failed (%s): %s", action, e)
        return False

# ======================================================================
# bot/services/forcejoin.py
# ======================================================================
log = logging.getLogger(__name__)
_USERNAME = re.compile(r"@[A-Za-z][A-Za-z0-9_]{3,31}")
_CHAT_ID = re.compile(r"-100\d{5,}")


def parse_channels(raw: str) -> list[tuple]:
    out = []
    for item in (raw or "").split(","):
        item = item.strip()
        if not item:
            continue
        ref, _, link = item.partition("|")
        ref, link = ref.strip(), link.strip()
        if _USERNAME.fullmatch(ref):
            out.append((ref, link or f"https://t.me/{ref[1:]}"))
        elif _CHAT_ID.fullmatch(ref) and link.startswith("https://"):
            out.append((int(ref), link))
    return out


def count_entries(raw: str) -> int:
    return len([i for i in (raw or "").split(",") if i.strip()])


async def missing_channels(bot: Bot, user_id: int, channels: list[tuple]) -> list[tuple]:
    missing = []
    for ref, link in channels:
        try:
            m = await bot.get_chat_member(ref, user_id)
            joined = m.status in ("creator", "administrator", "member") or (
                m.status == "restricted" and getattr(m, "is_member", False))
            if not joined:
                missing.append((ref, link))
        except TelegramAPIError as e:
            log.warning("force-join check failed for %s: %s", ref, e)
            await notify_owner_once(bot, f"fj:{ref}", f"Force join cannot verify {ref}. Make the bot an admin there.")
    return missing


async def send_prompt(bot: Bot, db, message: Message, missing: list[tuple]):
    user = message.from_user
    rows = [[btn("join channel", "lock", url=link)] for _, link in missing]
    rows.append([btn("i joined", "success", callback_data="fjc")])
    text = f"{em('lock')} {mention(user.id, user.full_name)}\n{render_template(db.get('force_join_text'), {})}"
    return await bot.send_message(
        message.chat.id, text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        message_thread_id=message.message_thread_id if message.is_topic_message else None,
        reply_parameters=ReplyParameters(message_id=message.message_id, allow_sending_without_reply=True),
        disable_notification=True,
    )

# ======================================================================
# bot/services/welcome.py
# ======================================================================
log = logging.getLogger(__name__)


def build_welcome(db, user_id: int, name: str, text: str | None = None):
    values = {"display_name": mention(user_id, name)}
    lines = [
        f"{em('welcome')} {render_template('Welcome, {display_name}', values)}",
        "",
        render_template(text or db.get("welcome_text"), values),
        "",
        f"{em('admin')} {sc('owner')}: {sc(db.get('owner_name'))}",
    ]
    username = db.get("owner_username").lstrip("@")
    if username:
        lines.append(f"{em('admin')} {sc('help')}: @{esc(username)}")
    lines += ["", f"{sc('if you have any problem, you can dm')} {sc(db.get('owner_name'))}."]
    kb = None
    link = db.get("channel_link")
    if link:
        kb = InlineKeyboardMarkup(inline_keyboard=[[btn("join channel", "welcome", url=link)]])
    return "\n".join(lines), kb


async def send_welcome(bot: Bot, db, user_id: int, name: str, welcome_text: str | None = None) -> bool:
    body, kb = build_welcome(db, user_id, name, welcome_text)
    try:
        await bot.send_message(user_id, body, reply_markup=kb)
        return True
    except TelegramForbiddenError:
        await db.set_dm(user_id, False)  # user never started the bot: stay silent
    except TelegramAPIError as e:
        log.info("welcome not delivered: %s", e)
    return False

# ======================================================================
# bot/services/broadcast.py
# ======================================================================
log = logging.getLogger(__name__)
broadcast_running = False


async def broadcast_recipients(db, target: str) -> list[tuple]:
    out = []
    if target in ("u", "b"):
        out += [("u", r["user_id"]) for r in await db.broadcast_users()]
    if target in ("g", "b"):
        out += [("g", r["chat_id"]) for r in await db.broadcast_groups()]
    return out


async def broadcast_run(bot: Bot, db, owner_chat: int, src_id: int, target: str, progress):
    global broadcast_running
    broadcast_running = True
    ok = fail = 0
    try:
        targets = await broadcast_recipients(db, target)
        for i, (kind, cid) in enumerate(targets, 1):
            for attempt in (1, 2):
                try:
                    await bot.copy_message(cid, owner_chat, src_id)
                    ok += 1
                except TelegramRetryAfter as e:
                    await asyncio.sleep(e.retry_after + 1)
                    if attempt == 1:
                        continue
                    fail += 1
                except TelegramForbiddenError:
                    fail += 1
                    if kind == "u":
                        await db.set_dm(cid, False)
                    else:
                        await db.set_group_active(cid, False)
                except TelegramAPIError:
                    fail += 1
                break
            if i % 20 == 0:
                await progress(i, len(targets), ok, fail)
            await asyncio.sleep(0.05)
        return len(targets), ok, fail
    finally:
        broadcast_running = False

# ======================================================================
# bot/services/stats.py
# ======================================================================
PERIODS = (("daily", 24), ("weekly", 168), ("monthly", 720))


async def dashboard_text(db, manager, started_at: float) -> str:
    users, groups = await db.count_users(), await db.count_groups()
    active = await db.count_groups(active_only=True)
    video = await db.downloads_count(media="video")
    audio = await db.downloads_count(media="audio")
    errors = await db.downloads_count(status="failed")
    usage = await db.platform_usage()
    free = shutil.disk_usage(BASE_DIR).free
    lines = [
        f"{em('admin')} {sc('dashboard')}", "",
        f"{em('user')} {sc('total users')}: {users}",
        f"{em('platform')} {sc('total groups')}: {groups}",
        f"{em('platform')} {sc('active groups')}: {active}",
        f"{em('download')} {sc('downloads')}: {video}",
        f"{em('audio')} {sc('audio downloads')}: {audio}",
        f"{em('error')} {sc('errors')}: {errors}",
        "",
        f"{em('platform')} {sc('platform statistics')}:",
    ]
    lines += [f"  {sc(r['platform'])}: {r['c']}" for r in usage] or [f"  {sc('no data yet')}"]
    lines += [
        "",
        f"{em('gear')} {sc('uptime')}: {sc(fmt_uptime(time.time() - started_at))}",
        f"{em('gear')} {sc('active / queued')}: {manager.active} / {manager.waiting}",
        f"{em('gear')} {sc('disk free')}: {sc(fmt_size(free))}",
        f"{em('gear')} {sc('maintenance')}: {sc('on' if db.get_bool('maintenance_enabled') else 'off')}",
        f"{em('gear')} {sc('system')}: python {sys.version_info.major}.{sys.version_info.minor}",
    ]
    return "\n".join(lines)


async def stats_text(db) -> str:
    lines = [f"{em('admin')} {sc('statistics')}", ""]
    for name, hours in PERIODS:
        v = await db.downloads_count(media="video", hours=hours)
        a = await db.downloads_count(media="audio", hours=hours)
        lines.append(f"{em('download')} {sc(name + ' downloads')}: {v}  ·  {sc('audio')}: {a}")
    lines += ["", f"{em('platform')} {sc('platform usage (30d)')}:"]
    lines += [f"  {sc(r['platform'])}: {r['c']}" for r in await db.platform_usage(720)] or [f"  {sc('no data yet')}"]
    video, audio = await db.downloads_count(media="video"), await db.downloads_count(media="audio")
    lines += ["", f"{em('audio')} {sc('video / audio usage')}: {video} / {audio}", "",
              f"{em('error')} {sc('error statistics (30d)')}:"]
    lines += [f"  {sc(r['e'])}: {r['c']}" for r in await db.error_breakdown(720)] or [f"  {sc('no errors')}"]
    lines += ["", f"{em('user')} {sc('top users')}:"]
    lines += [f"  {i}. {esc(trim(r['display_name'], 22) or r['user_id'])} - {r['download_count']}"
              for i, r in enumerate(await db.top_users(5), 1)] or [f"  {sc('no data yet')}"]
    lines += ["", f"{em('platform')} {sc('top groups')}:"]
    lines += [f"  {i}. {esc(trim(r['title'], 24) or r['chat_id'])} - {r['c']}"
              for i, r in enumerate(await db.top_groups(5), 1)] or [f"  {sc('no data yet')}"]
    return "\n".join(lines)

# ======================================================================
# bot/services/maintenance.py
# ======================================================================
log = logging.getLogger(__name__)
_restarting = False


def ytdlp_version() -> str:
    try:
        return importlib.metadata.version("yt-dlp")
    except Exception:
        return "unknown"


async def _restart_when_idle(manager) -> None:
    global _restarting
    if _restarting:
        return
    _restarting = True
    for _ in range(60):  # wait up to 5 minutes for running downloads
        if manager.active == 0 and manager.waiting == 0:
            break
        await asyncio.sleep(5)
    log.info("restarting to load updated yt-dlp")
    os.execv(sys.executable, [sys.executable] + sys.argv)


async def update_ytdlp(manager) -> str:
    """pip-upgrade yt-dlp. If the version changed, restart the bot once it is idle."""
    before = ytdlp_version()
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pip", "install", "-U", "--quiet", "yt-dlp",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        out, _ = await asyncio.wait_for(proc.communicate(), 300)
    except Exception as e:
        return f"{em('error')} {sc('update failed')}: {esc(str(e)[:200])}"
    if proc.returncode != 0:
        return f"{em('error')} {sc('update failed')}\n<code>{esc(out.decode(errors='replace')[-300:])}</code>"
    after = ytdlp_version()
    if after == before:
        return f"{em('success')} {sc('yt-dlp is up to date')}: <code>{esc(after)}</code>"
    asyncio.create_task(_restart_when_idle(manager))
    return (f"{em('success')} {sc('yt-dlp updated')}: <code>{esc(before)}</code> → <code>{esc(after)}</code>\n"
            f"{sc('the bot restarts when idle to load it')}")


async def auto_updater(bot: Bot, db, manager) -> None:
    await asyncio.sleep(120)
    while True:
        if db.get_bool("auto_update"):
            try:
                msg = await update_ytdlp(manager)
                log.info("auto update: %s", re.sub(r"<[^>]+>", "", msg)[:200])
                if "up to date" not in msg:
                    await notify_owner_once(bot, "autoupd", msg, every=6 * 3600)
            except Exception:
                log.exception("auto update crashed")
        await asyncio.sleep(max(1, db.get_int("auto_update_hours")) * 3600)


def _backup_sync(dst: Path) -> None:
    src, out = sqlite3.connect(DB_PATH), sqlite3.connect(dst)
    try:
        src.backup(out)
    finally:
        out.close()
        src.close()


async def backup_database() -> Path:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    dst = TEMP_DIR / f"bot-backup-{datetime.now():%Y%m%d-%H%M}.db"
    await asyncio.to_thread(_backup_sync, dst)
    return dst


def read_errors(limit: int = 15) -> str:
    path = LOG_DIR / "bot.log"
    if not path.exists():
        return f"{em('success')} {sc('no log yet')}"
    with open(path, "rb") as f:
        f.seek(0, 2)
        f.seek(max(0, f.tell() - 300_000))
        data = f.read().decode("utf-8", "replace")
    lines = [l for l in data.splitlines() if " ERROR " in l or " WARNING " in l or " CRITICAL " in l][-limit:]
    if not lines:
        return f"{em('success')} {sc('no recent errors')}"
    return f"{em('error')} {sc('last errors')}\n<pre>{esc(chr(10).join(trim(l, 230) for l in lines))}</pre>"

# ======================================================================
# bot/services/pipeline.py
# ======================================================================
log = logging.getLogger(__name__)

QUALITIES = (360, 720, 1080)
DEFAULT_QUALITY = 720

ERRORS = {
    "private": "private or login-required content",
    "unsupported": "unsupported link",
    "unavailable": "content unavailable or deleted",
    "restricted": "content is restricted in this region",
    "too_large": "file too large (max {mb} mb)",
    "timeout": "download timed out",
    "upload": "upload failed",
    "failed": "download failed",
}


def stage(db, key: str, emoji: str, **values) -> str:
    return f"{em(emoji)} {render_template(db.get(key), values)}"


def error_text(db, code: str, max_mb=None) -> str:
    msg = ERRORS.get(code, ERRORS["failed"]).format(mb=max_mb or db.get_int("max_file_mb"))
    return f"{em('error')} {sc(msg)}"


def group_max_mb(db, group) -> int:
    v = Database.group_get(group, "max_file_mb", None) if group else None
    return int(v) if v else db.get_int("max_file_mb")


def details(db, result: MediaResult, label: str, user, with_user: bool, quality: bool = False) -> str:
    lines = [
        f"{em('platform')} {sc('platform')}: {sc(label)}",
        f"{em('title')} {sc('title')}: {esc(trim(result.title, 90))}",
    ]
    if result.duration:
        lines.append(f"{em('duration')} {sc('duration')}: {sc(fmt_duration(result.duration))}")
    if quality and result.height:
        lines.append(f"{em('download')} {sc('quality')}: {result.height}p")
    lines.append(f"{em('size')} {sc('size')}: {sc(fmt_size(result.size))}")
    if with_user:
        lines.append(f"{em('user')} {sc('requested by')}: {mention(user.id, user.full_name)}")
    lines += ["", f"{sc('powered by')} {sc(db.get('owner_name'))}"]
    return "\n".join(lines)


def result_keyboard(db, dl_id: int, user_id: int, quality: int):
    sig = sign(dl_id, user_id)
    rows = []
    if db.get_bool("quality_buttons"):
        rows.append([btn(("✅ " if q == quality else "") + f"{q}p", callback_data=f"q:{dl_id}:{q}:{sig}")
                     for q in QUALITIES])
    extra = []
    if db.get_bool("audio_enabled"):
        extra.append(btn("download audio", "audio", callback_data=f"a:{dl_id}:{sig}"))
    if db.get_bool("thumbnail_enabled"):
        extra.append(btn("thumbnail", "thumb", callback_data=f"t:{dl_id}:{sig}"))
    if extra:
        rows.append(extra)
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None


def _result_from_cache(c) -> MediaResult:
    return MediaResult(path=None, title=c["title"] or "", duration=c["duration"], size=c["size"] or 0,
                       uploader=c["uploader"], width=c["width"], height=c["height"])


def _file_ref(msg, kind: str):
    if kind == "audio":
        return (msg.audio.file_id, "audio") if msg.audio else None
    if msg.video:
        return msg.video.file_id, "video"
    if msg.document:
        return msg.document.file_id, "document"
    return None


async def _watch(db, status: Status, state: dict, key: str) -> None:
    last = -1
    while True:
        await asyncio.sleep(3)
        pct = state.get("pct")
        if pct is None or pct == last:
            continue
        last = pct
        await status.show(stage(db, key, "download") + f"\n{bar(pct)} {pct}%")


@asynccontextmanager
async def fetched(db, manager, status: Status, provider, url: str, kind: str, stage_key: str,
                  max_bytes: int, quality: int = DEFAULT_QUALITY):
    """Download inside a queue slot; the temp dir lives until the caller finished uploading."""
    workdir = new_workdir()
    try:
        async with manager.slot():
            await status.show(stage(db, stage_key, "download"))
            state: dict = {}
            watcher = asyncio.create_task(_watch(db, status, state, stage_key))
            try:
                result = await provider.download(
                    url, workdir, max_bytes=max_bytes, timeout=db.get_int("download_timeout"),
                    kind=kind, state=state, quality=quality,
                )
            finally:
                watcher.cancel()
            await status.show(stage(db, "msg_processing", "download"))
            yield result
    finally:
        remove_dir(workdir)


async def _fail(db, ctx: dict, code: str, max_mb) -> None:
    log.warning("download failed code=%s", code)
    if ctx["dl_id"]:
        await db.finish_download(ctx["dl_id"], "failed", error=code)
    st = ctx["status"]
    if st:
        await st.show(error_text(db, code, max_mb))
        st.delete_later(6)


async def _run(db, manager, user_id: int, max_mb, body) -> bool:
    """One active request per user + unified error handling."""
    if not manager.reserve(user_id):
        return False
    ctx = {"status": None, "dl_id": None}
    try:
        await body(ctx)
        return True
    except DownloadError as e:
        await _fail(db, ctx, e.code, max_mb)
    except TelegramAPIError as e:
        log.warning("upload failed: %s", e)
        await _fail(db, ctx, "upload", max_mb)
    except Exception:
        log.exception("unexpected pipeline error")
        await _fail(db, ctx, "failed", max_mb)
    finally:
        manager.release(user_id)
    return False


async def _send_video(bot: Bot, chat_id, result: MediaResult, caption, kb, thread, reply):
    def thumb():
        return FSInputFile(result.thumb) if result.thumb else None
    try:
        return await bot.send_video(
            chat_id, FSInputFile(result.path), caption=caption, reply_markup=kb,
            duration=int(result.duration) if result.duration else None,
            width=result.width, height=result.height, thumbnail=thumb(), supports_streaming=True,
            message_thread_id=thread, reply_parameters=reply,
        )
    except TelegramBadRequest as e:
        if "too large" in str(e).lower():
            raise DownloadError("too_large")
        log.warning("send_video rejected (%s); retrying as document", e)
        return await bot.send_document(
            chat_id, FSInputFile(result.path), caption=caption, reply_markup=kb, thumbnail=thumb(),
            message_thread_id=thread, reply_parameters=reply)


async def _send_cached(bot: Bot, chat_id, c, caption, kb, thread, reply):
    if c["file_type"] == "document":
        return await bot.send_document(chat_id, c["file_id"], caption=caption, reply_markup=kb,
                                       message_thread_id=thread, reply_parameters=reply)
    return await bot.send_video(chat_id, c["file_id"], caption=caption, reply_markup=kb, supports_streaming=True,
                                message_thread_id=thread, reply_parameters=reply)


async def _deliver_video(bot, db, manager, status, chat_id, thread, reply, user, provider, url,
                         quality, dl_id, max_mb) -> None:
    max_bytes = max_mb * 1024 * 1024
    key = canon_url(url)
    use_cache = db.get_bool("cache_enabled")
    if use_cache:
        c = await db.cache_get(key, "video", quality)
        if c:
            if (c["size"] or 0) > max_bytes:
                raise DownloadError("too_large")
            result = _result_from_cache(c)
            try:
                await _send_cached(bot, chat_id, c, details(db, result, provider.label, user, True, True),
                                   result_keyboard(db, dl_id, user.id, quality), thread, reply)
                await db.finish_download(dl_id, "done", title=result.title, size=result.size, duration=result.duration)
                await db.bump_downloads(user.id)
                log.info("cache hit platform=%s quality=%s", provider.key, quality)
                return
            except TelegramAPIError as e:
                log.warning("cached file rejected (%s); downloading again", e)
                await db.cache_delete(key, "video", quality)
    async with fetched(db, manager, status, provider, url, "video", "msg_downloading", max_bytes, quality) as result:
        sent = await _send_video(bot, chat_id, result, details(db, result, provider.label, user, True, True),
                                 result_keyboard(db, dl_id, user.id, quality), thread, reply)
    ref = _file_ref(sent, "video")
    if use_cache and ref:
        await db.cache_put(key, "video", quality, ref[0], ref[1], result)
    await db.finish_download(dl_id, "done", title=result.title, size=result.size, duration=result.duration)
    await db.bump_downloads(user.id)
    log.info("download ok platform=%s size=%s quality=%s", provider.key, result.size, quality)


async def run_video(bot: Bot, db, manager, message: Message, provider, url: str, *, first=True, index=None) -> bool:
    chat, user = message.chat, message.from_user
    thread = message.message_thread_id if message.is_topic_message else None
    max_mb = group_max_mb(db, await db.get_group(chat.id))

    async def body(ctx):
        log.info("download request user=%s chat=%s platform=%s", user.id, chat.id, provider.key)
        reply = None
        if first:  # only the first link of a message deletes the original
            deleted = await try_delete(message)
            reply = None if deleted else ReplyParameters(message_id=message.message_id, allow_sending_without_reply=True)
        status = ctx["status"] = Status(bot, chat.id, thread, reply)
        if index and index[1] > 1:
            status.prefix = f"[{index[0]}/{index[1]}] "
        await status.show(stage(db, "msg_detecting", "search"))
        await asyncio.sleep(0.8)
        await status.show(stage(db, "msg_detected", "download", platform=sc(provider.label)))
        await asyncio.sleep(0.8)
        await status.show(stage(db, "msg_preparing", "download"))
        dl_id = ctx["dl_id"] = await db.add_download(user.id, chat.id, provider.key, "video", url)
        await _deliver_video(bot, db, manager, status, chat.id, thread, reply, user, provider, url,
                             DEFAULT_QUALITY, dl_id, max_mb)
        await status.show(stage(db, "msg_completed", "success"))
        status.delete_later(db.get_int("status_cleanup_seconds"))

    return await _run(db, manager, user.id, max_mb, body)


async def run_quality(bot: Bot, db, manager, cb, row, provider, quality: int) -> bool:
    """Re-deliver the same link in another quality (instant when cached)."""
    msg, user = cb.message, cb.from_user
    thread = msg.message_thread_id if msg.is_topic_message else None
    max_mb = group_max_mb(db, await db.get_group(row["group_id"]))

    async def body(ctx):
        reply = ReplyParameters(message_id=msg.message_id, allow_sending_without_reply=True)
        status = ctx["status"] = Status(bot, msg.chat.id, thread, reply)
        await status.show(stage(db, "msg_preparing", "download"))
        dl_id = ctx["dl_id"] = await db.add_download(user.id, row["group_id"], row["platform"], "video", row["url"])
        await _deliver_video(bot, db, manager, status, msg.chat.id, thread, reply, user, provider, row["url"],
                             quality, dl_id, max_mb)
        await status.show(stage(db, "msg_completed", "success"))
        status.delete_later(db.get_int("status_cleanup_seconds"))

    return await _run(db, manager, user.id, max_mb, body)


async def run_audio(bot: Bot, db, manager, cb, row, provider) -> bool:
    """Returns True on success. The caller already claimed audio_state=1."""
    msg, user = cb.message, cb.from_user
    thread = msg.message_thread_id if msg.is_topic_message else None
    max_mb = group_max_mb(db, await db.get_group(row["group_id"]))
    max_bytes = max_mb * 1024 * 1024

    async def body(ctx):
        reply = ReplyParameters(message_id=msg.message_id, allow_sending_without_reply=True)
        status = ctx["status"] = Status(bot, msg.chat.id, thread, reply)
        await status.show(stage(db, "msg_preparing", "audio"))
        dl_id = ctx["dl_id"] = await db.add_download(user.id, row["group_id"], row["platform"], "audio", row["url"])
        key, use_cache = canon_url(row["url"]), db.get_bool("cache_enabled")
        c = await db.cache_get(key, "audio", 0) if use_cache else None
        if c and (c["size"] or 0) > max_bytes:
            raise DownloadError("too_large")
        result = _result_from_cache(c) if c else None
        sent_ok = False
        if c:
            try:
                await bot.send_audio(msg.chat.id, c["file_id"], caption=details(db, result, provider.label, user, False),
                                     title=trim(result.title, 64), performer=result.uploader,
                                     duration=int(result.duration) if result.duration else None,
                                     reply_parameters=reply, message_thread_id=thread)
                sent_ok = True
            except TelegramAPIError as e:
                log.warning("cached audio rejected (%s)", e)
                await db.cache_delete(key, "audio", 0)
        if not sent_ok:
            async with fetched(db, manager, status, provider, row["url"], "audio", "msg_audio", max_bytes, 0) as result:
                try:
                    sent = await bot.send_audio(
                        msg.chat.id, FSInputFile(result.path), caption=details(db, result, provider.label, user, False),
                        title=trim(result.title, 64), performer=result.uploader,
                        thumbnail=FSInputFile(result.thumb) if result.thumb else None,
                        duration=int(result.duration) if result.duration else None,
                        reply_parameters=reply, message_thread_id=thread)
                except TelegramBadRequest as e:
                    if "too large" in str(e).lower():
                        raise DownloadError("too_large")
                    raise
            ref = _file_ref(sent, "audio")
            if use_cache and ref:
                await db.cache_put(key, "audio", 0, ref[0], ref[1], result)
        await db.finish_download(dl_id, "done", title=result.title, size=result.size, duration=result.duration)
        await status.show(stage(db, "msg_completed", "success"))
        status.delete_later(db.get_int("status_cleanup_seconds"))

    return await _run(db, manager, user.id, max_mb, body)


async def run_thumb(bot: Bot, db, manager, cb, row, provider) -> bool:
    """Send the video's thumbnail as a separate photo."""
    msg, user = cb.message, cb.from_user
    thread = msg.message_thread_id if msg.is_topic_message else None

    async def body(ctx):
        reply = ReplyParameters(message_id=msg.message_id, allow_sending_without_reply=True)
        status = ctx["status"] = Status(bot, msg.chat.id, thread, reply)
        await status.show(stage(db, "msg_preparing", "download"))
        workdir = new_workdir()
        try:
            async with manager.slot():
                path = await provider.fetch_thumbnail(row["url"], workdir)
            if not path:
                raise DownloadError("failed")
            caption = f"{esc(trim(row['title'], 90))}\n\n{sc('powered by')} {sc(db.get('owner_name'))}"
            await bot.send_photo(msg.chat.id, FSInputFile(path), caption=caption,
                                 reply_parameters=reply, message_thread_id=thread)
        finally:
            remove_dir(workdir)
        status.delete_later(0)

    return await _run(db, manager, user.id, None, body)

# ======================================================================
# owner_panel/views.py
# ======================================================================
TITLES = {
    "dash": "dashboard", "users": "users", "groups": "groups", "force": "force join",
    "welcome": "welcome", "dl": "downloads", "filters": "filters", "cast": "broadcast",
    "spam": "warn and flood", "stats": "statistics", "maint": "maintenance", "system": "system",
    "bot": "bot settings",
}


def _vb(text, data):
    return B(text=text, callback_data=data)


def back(to="menu"):
    return [_vb("‹ " + sc("back"), f"op:{to}")]


def _kb(rows):
    return KB(inline_keyboard=rows)


def menu(db):
    items = [_vb(sc(t), f"op:{k}") for k, t in TITLES.items()]
    rows = [items[i:i + 2] for i in range(0, len(items), 2)]
    return f"{em('admin')} {sc(db.get('bot_name'))} - {sc('owner panel')}\n\n{sc('select a section')}", _kb(rows)


def settings_view(db, section):
    lines = [f"{em('admin')} {sc(TITLES[section])}", ""]
    if section == "bot":
        lines.append(f"▫️ {sc('owner id')}: <code>{OWNER_ID}</code>")
    rows, pair = [], []
    for key, m in META.items():
        if section not in m["sections"]:
            continue
        val = db.get(key)
        if m["type"] == "bool":
            pair.append(_vb(f"{'✅' if val == '1' else '❌'} {sc(m['label'])}", f"tg:{section}:{key}"))
        else:
            lines.append(f"▫️ {sc(m['label'])}: <code>{esc(trim(val, 60) or '-')}</code>")
            pair.append(_vb(f"✏️ {sc(m['label'])}", f"ed:{section}:{key}"))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    if section == "welcome":
        rows.append([_vb("👁 " + sc("preview welcome"), "wp")])
    if section == "force":
        rows.append([_vb("🔍 " + sc("verify configuration"), "fjv")])
    rows.append(back())
    return "\n".join(lines), _kb(rows)


async def users_home(db):
    total, blocked = await db.count_users(), await db.count_users(blocked=True)
    text = (f"{em('admin')} {sc('user management')}\n\n{sc('total users')}: {total}\n"
            f"{sc('blocked')}: {blocked}")
    return text, _kb([[_vb("🔎 " + sc("search user"), "us:find"), _vb("🕘 " + sc("recent"), "us:recent")], back()])


def user_list(rows, title):
    buttons = [[_vb(f"{trim(r['display_name'], 22) or '-'} · {r['user_id']}", f"ui:{r['user_id']}")] for r in rows]
    text = f"{em('admin')} {sc(title)}" + ("" if rows else f"\n\n{sc('no users found')}")
    return text, _kb(buttons + [back("users")])


async def user_info(db, uid: int):
    u = await db.get_user(uid)
    if not u:
        return f"{em('error')} {sc('user not found')}", _kb([back("users")])
    audio = await db.downloads_count(media="audio", user_id=uid)
    errors = await db.downloads_count(status="failed", user_id=uid)
    text = "\n".join([
        f"{em('user')} {sc('user information')}", "",
        f"{sc('id')}: <code>{uid}</code>",
        f"{sc('name')}: {esc(u['display_name'])}",
        f"{sc('first seen')}: {esc(u['first_seen'])}",
        f"{sc('last seen')}: {esc(u['last_seen'])}",
        f"{sc('downloads')}: {u['download_count']}",
        f"{sc('audio downloads')}: {audio}",
        f"{sc('failed requests')}: {errors}",
        f"{sc('blocked')}: {'✅' if u['blocked'] else '❌'}",
    ])
    flag = 0 if u["blocked"] else 1
    label = "unblock user" if u["blocked"] else "block user"
    return text, _kb([[_vb(sc(label), f"ub:{uid}:{flag}")], back("users")])


async def groups_home(db):
    groups = await db.list_groups(20)
    buttons = [[_vb(f"{'🟢' if g['enabled'] and g['active'] else '🔴'} {trim(g['title'], 28) or g['chat_id']}",
                   f"gi:{g['chat_id']}")] for g in groups]
    text = (f"{em('admin')} {sc('group management')}\n\n{sc('total groups')}: {await db.count_groups()}\n"
            f"{sc('active groups')}: {await db.count_groups(active_only=True)}")
    return text, _kb(buttons + [back()])


PLAT_LABELS = (("youtube", "youtube"), ("instagram", "instagram"), ("facebook", "facebook"),
               ("twitter", "x / twitter"), ("snapchat", "snapchat"))


async def group_info(db, chat_id: int):
    g = await db.get_group(chat_id)
    if not g:
        return f"{em('error')} {sc('group not found')}", _kb([back("groups")])
    gf = Database.group_flag
    flt, wel = gf(g, "filter", True), gf(g, "welcome", True)
    mx = Database.group_get(g, "max_file_mb", None) or db.get_int("max_file_mb")
    wt = Database.group_get(g, "welcome_text", None)
    text = "\n".join([
        f"{em('platform')} {sc('group information')}", "",
        f"{sc('title')}: {esc(g['title'])}",
        f"{sc('id')}: <code>{chat_id}</code>",
        f"{sc('added')}: {esc(g['added_at'])}",
        f"{sc('bot in group')}: {'✅' if g['active'] else '❌'}",
        f"{sc('downloads')}: {await db.downloads_count(group_id=chat_id)}",
        f"{sc('max file size')}: {mx} {sc('mb')}",
        f"{sc('welcome text')}: <code>{esc(trim(wt, 50)) if wt else '-'}</code>",
    ])
    plats = [_vb(f"{'✅' if gf(g, 'plat_' + k, True) else '❌'} {sc(label)}", f"gp:{chat_id}:{k}")
             for k, label in PLAT_LABELS]
    return text, _kb([
        [_vb(f"{'✅' if g['enabled'] else '❌'} {sc('bot enabled')}", f"gt:{chat_id}"),
         _vb(f"{'✅' if flt else '❌'} {sc('link filter')}", f"gf:{chat_id}")],
        [_vb(f"{'✅' if wel else '❌'} {sc('welcome')}", f"gw:{chat_id}")],
        plats[:2], plats[2:4], plats[4:],
        [_vb("✏️ " + sc("max size"), f"ge:{chat_id}:max_file_mb"),
         _vb("✏️ " + sc("welcome text"), f"ge:{chat_id}:welcome_text")],
        back("groups"),
    ])


def cast_home():
    text = f"{em('admin')} {sc('broadcast')}\n\n{sc('choose who receives the message')}"
    return text, _kb([[_vb(sc("users"), "cs:u"), _vb(sc("groups"), "cs:g"), _vb(sc("both"), "cs:b")], back()])


async def render(section, db, manager, started_at):
    if section == "dash":
        text = await dashboard_text(db, manager, started_at)
        return text, _kb([[_vb("🔄 " + sc("refresh"), "op:dash")], back()])
    if section == "stats":
        return await stats_text(db), _kb([[_vb("🔄 " + sc("refresh"), "op:stats")], back()])
    if section == "users":
        return await users_home(db)
    if section == "groups":
        return await groups_home(db)
    if section == "cast":
        return cast_home()
    if section == "system":
        text, kb = settings_view(db, section)
        size = DB_PATH.stat().st_size if DB_PATH.exists() else 0
        text += (f"\n\n▫️ {sc('yt-dlp version')}: <code>{esc(ytdlp_version())}</code>"
                 f"\n▫️ {sc('cached files')}: {await db.cache_count()}"
                 f"\n▫️ {sc('database size')}: {sc(fmt_size(size))}")
        extra = [
            [_vb("💾 " + sc("backup db"), "sys:backup"), _vb("📜 " + sc("view errors"), "sys:errors")],
            [_vb("📄 " + sc("send log file"), "sys:logfile"), _vb("⬆️ " + sc("update yt-dlp"), "sys:update")],
            [_vb("🗑 " + sc("clear cache"), "sys:cache")],
        ]
        return text, _kb(kb.inline_keyboard[:-1] + extra + [back()])
    if section in TITLES:
        return settings_view(db, section)
    return menu(db)

# ======================================================================
# owner_panel/router.py
# ======================================================================
log = logging.getLogger(__name__)
owner_router = Router(name="owner_panel")
owner_router.message.filter(IsOwnerPrivate())
owner_router.callback_query.filter(IsOwnerPrivate())

_UNAME = re.compile(r"[A-Za-z][A-Za-z0-9_]{3,31}")


async def _panel(cb: CallbackQuery, bot: Bot, text, kb):
    await safe_edit(bot, cb.message.chat.id, cb.message.message_id, text, kb)


def validate(key: str, meta: dict, raw: str):
    """Returns (value, error)."""
    if meta["type"] == "int":
        try:
            n = int(raw)
        except ValueError:
            return None, "enter a whole number"
        if not meta["min"] <= n <= meta["max"]:
            return None, f"allowed range {meta['min']} to {meta['max']}"
        return str(n), None
    if len(raw) > 700:
        return None, "too long"
    if raw == "-":
        return "", None
    if key == "warn_action":
        return (raw.lower(), None) if raw.lower() in ("mute", "ban") else (None, "send mute or ban")
    if key == "owner_username":
        raw = raw.lstrip("@")
        return (raw, None) if _UNAME.fullmatch(raw) else (None, "invalid username")
    if key == "channel_link":
        if raw.startswith("@"):
            raw = "https://t.me/" + raw[1:]
        elif raw.startswith("t.me/"):
            raw = "https://" + raw
        return (raw, None) if raw.startswith(("https://", "http://")) else (None, "send a full https link")
    if key == "force_channels":
        if len(parse_channels(raw)) != count_entries(raw):
            return None, "invalid format, see the hint"
    return raw, None


@owner_router.message(CommandStart())
async def start(message: Message, state: FSMContext, db, manager, started_at):
    await state.clear()
    text, kb = menu(db)
    await message.answer(text, reply_markup=kb)


@owner_router.callback_query(F.data.startswith("op:"))
async def open_section(cb: CallbackQuery, state: FSMContext, bot: Bot, db, manager, started_at):
    await state.clear()
    text, kb = await render(cb.data[3:], db, manager, started_at)
    await _panel(cb, bot, text, kb)
    await cb.answer()


@owner_router.callback_query(F.data.startswith("tg:"))
async def toggle(cb: CallbackQuery, bot: Bot, db, manager, started_at):
    _, section, key = cb.data.split(":", 2)
    meta = META.get(key)
    if meta and meta["type"] == "bool":
        new = "0" if db.get_bool(key) else "1"
        await db.set(key, new)
        log.info("owner toggled %s=%s", key, new)
    text, kb = await render(section, db, manager, started_at)
    await _panel(cb, bot, text, kb)
    await cb.answer()


@owner_router.callback_query(F.data.startswith("ed:"))
async def edit_start(cb: CallbackQuery, state: FSMContext, bot: Bot, db):
    _, section, key = cb.data.split(":", 2)
    meta = META.get(key)
    if not meta or meta["type"] == "bool":
        return await cb.answer()
    await state.set_state(Edit.value)
    await state.update_data(key=key, section=section, panel=cb.message.message_id)
    hint = meta.get("hint") or (f"{meta['min']} - {meta['max']}" if meta["type"] == "int" else "")
    text = (f"{em('admin')} {sc('send the new value for')} <b>{sc(meta['label'])}</b>\n"
            f"{sc('current')}: <code>{esc(db.get(key) or '-')}</code>\n"
            + (f"{sc('hint')}: {esc(hint)}\n" if hint else "")
            + f"\n{sc('send - to clear')}")
    await _panel(cb, bot, text, _kb([back(section)]))
    await cb.answer()


@owner_router.message(Edit.value, F.text)
async def edit_value(message: Message, state: FSMContext, bot: Bot, db, manager, started_at):
    data = await state.get_data()
    key, section, panel = data["key"], data["section"], data["panel"]
    value, err = validate(key, META[key], message.text.strip())
    if err:
        note = await message.answer(f"{em('error')} {sc(err)}")
        schedule_delete(bot, message.chat.id, note.message_id, 4)
        return
    if data.get("group_id"):
        cid = data["group_id"]
        await db.set_group_flag(cid, key, int(value) if key == "max_file_mb" and value else value)
        log.info("owner changed group %s setting %s", cid, key)
        await state.clear()
        await try_delete(message)
        text, kb = await group_info(db, cid)
        await safe_edit(bot, message.chat.id, panel, text, kb)
        return
    await db.set(key, value)
    if key == "concurrent_downloads":
        manager.set_concurrency(int(value))
    log.info("owner changed setting %s", key)
    await state.clear()
    await try_delete(message)
    text, kb = await render(section, db, manager, started_at)
    await safe_edit(bot, message.chat.id, panel, text, kb)


@owner_router.callback_query(F.data == "wp")
async def welcome_preview(cb: CallbackQuery, bot: Bot, db):
    await send_welcome(bot, db, cb.from_user.id, cb.from_user.full_name)
    await cb.answer(sc("preview sent"))


@owner_router.callback_query(F.data == "fjv")
async def force_verify(cb: CallbackQuery, bot: Bot, db):
    channels = parse_channels(db.get("force_channels"))
    if not channels:
        return await cb.answer(sc("no channels configured"), show_alert=True)
    lines = []
    for ref, _ in channels:
        try:
            me = await bot.get_chat_member(ref, bot.id)
            lines.append(f"{'✅' if me.status == 'administrator' else '⚠️'} {esc(ref)}")
        except TelegramAPIError:
            lines.append(f"❌ {esc(ref)}")
    await cb.message.answer(f"{em('admin')} {sc('bot must be admin in each channel')}\n\n" + "\n".join(lines))
    await cb.answer()


# ---------------- users ----------------
@owner_router.callback_query(F.data == "us:find")
async def user_find(cb: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(Find.query)
    await state.update_data(panel=cb.message.message_id)
    await _panel(cb, bot, f"{em('admin')} {sc('send a user id or part of a name')}", _kb([back("users")]))
    await cb.answer()


@owner_router.message(Find.query, F.text)
async def user_find_result(message: Message, state: FSMContext, bot: Bot, db):
    panel = (await state.get_data())["panel"]
    await state.clear()
    await try_delete(message)
    text, kb = user_list(await db.search_users(message.text), "search results")
    await safe_edit(bot, message.chat.id, panel, text, kb)


@owner_router.callback_query(F.data == "us:recent")
async def user_recent(cb: CallbackQuery, bot: Bot, db):
    text, kb = user_list(await db.recent_users(10), "recent users")
    await _panel(cb, bot, text, kb)
    await cb.answer()


@owner_router.callback_query(F.data.startswith("ui:"))
async def user_show(cb: CallbackQuery, bot: Bot, db):
    text, kb = await user_info(db, int(cb.data[3:]))
    await _panel(cb, bot, text, kb)
    await cb.answer()


@owner_router.callback_query(F.data.startswith("ub:"))
async def user_block(cb: CallbackQuery, bot: Bot, db):
    _, uid, flag = cb.data.split(":")
    await db.set_blocked(int(uid), flag == "1")
    log.info("owner set blocked=%s for user %s", flag, uid)
    text, kb = await user_info(db, int(uid))
    await _panel(cb, bot, text, kb)
    await cb.answer()


# ---------------- groups ----------------
@owner_router.callback_query(F.data.startswith("gi:"))
async def group_show(cb: CallbackQuery, state: FSMContext, bot: Bot, db):
    await state.clear()
    text, kb = await group_info(db, int(cb.data[3:]))
    await _panel(cb, bot, text, kb)
    await cb.answer()


@owner_router.callback_query(F.data.startswith(("gt:", "gf:")))
async def group_toggle(cb: CallbackQuery, bot: Bot, db):
    kind, cid = cb.data[:2], int(cb.data[3:])
    g = await db.get_group(cid)
    if g:
        if kind == "gt":
            await db.set_group_enabled(cid, not g["enabled"])
        else:
            await db.set_group_flag(cid, "filter", not Database.group_flag(g, "filter", True))
        log.info("owner toggled %s for group %s", kind, cid)
    text, kb = await group_info(db, cid)
    await _panel(cb, bot, text, kb)
    await cb.answer()


# ---------------- broadcast ----------------
@owner_router.callback_query(F.data.startswith("cs:"))
async def cast_target(cb: CallbackQuery, state: FSMContext, bot: Bot):
    if broadcast_running:
        return await cb.answer(sc("a broadcast is already running"), show_alert=True)
    await state.set_state(Cast.content)
    await state.update_data(target=cb.data[3:], panel=cb.message.message_id)
    await _panel(cb, bot, f"{em('admin')} {sc('send the message to broadcast (any content)')}",
                 _kb([back("cast")]))
    await cb.answer()


@owner_router.message(Cast.content)
async def cast_content(message: Message, state: FSMContext, bot: Bot, db):
    data = await state.get_data()
    n = len(await broadcast_recipients(db, data["target"]))
    await state.update_data(src=message.message_id)
    await state.set_state(Cast.confirm)
    text = f"{em('admin')} {sc('ready to send to')} <b>{n}</b> {sc('recipients')}"
    await safe_edit(bot, message.chat.id, data["panel"], text, _kb([
        [_vb("✅ " + sc("send now"), "cg:go"), _vb("❌ " + sc("cancel"), "op:cast")]]))


@owner_router.callback_query(Cast.confirm, F.data == "cg:go")
async def cast_go(cb: CallbackQuery, state: FSMContext, bot: Bot, db):
    data = await state.get_data()
    await state.clear()
    chat_id, panel = cb.message.chat.id, cb.message.message_id

    async def progress(i, total, ok, fail):
        await safe_edit(bot, chat_id, panel, f"{em('admin')} {sc('broadcasting')} {i}/{total}  ✅ {ok}  ❌ {fail}")

    await cb.answer()
    log.info("owner started broadcast target=%s", data["target"])
    total, ok, fail = await broadcast_run(bot, db, chat_id, data["src"], data["target"], progress)
    await safe_edit(bot, chat_id, panel,
                    f"{em('success')} {sc('broadcast finished')}\n{sc('total')}: {total}  ✅ {ok}  ❌ {fail}",
                    _kb([back("cast")]))


# ---------------- per-group settings ----------------
async def _show_group(cb: CallbackQuery, bot: Bot, db, cid: int):
    text, kb = await group_info(db, cid)
    await _panel(cb, bot, text, kb)
    await cb.answer()


@owner_router.callback_query(F.data.startswith("gp:"))
async def group_platform(cb: CallbackQuery, bot: Bot, db):
    _, cid, plat = cb.data.split(":")
    g = await db.get_group(int(cid))
    if g and f"plat_{plat}" in META:
        await db.set_group_flag(int(cid), f"plat_{plat}", not Database.group_flag(g, f"plat_{plat}", True))
        log.info("owner toggled platform %s for group %s", plat, cid)
    await _show_group(cb, bot, db, int(cid))


@owner_router.callback_query(F.data.startswith("gw:"))
async def group_welcome(cb: CallbackQuery, bot: Bot, db):
    cid = int(cb.data[3:])
    g = await db.get_group(cid)
    if g:
        await db.set_group_flag(cid, "welcome", not Database.group_flag(g, "welcome", True))
    await _show_group(cb, bot, db, cid)


@owner_router.callback_query(F.data.startswith("ge:"))
async def group_edit_start(cb: CallbackQuery, state: FSMContext, bot: Bot, db):
    _, cid, key = cb.data.split(":", 2)
    if key not in ("max_file_mb", "welcome_text"):
        return await cb.answer()
    g = await db.get_group(int(cid))
    cur = Database.group_get(g, key, None) if g else None
    await state.set_state(Edit.value)
    await state.update_data(key=key, section="groups", panel=cb.message.message_id, group_id=int(cid))
    hint = "1 - 2000" if key == "max_file_mb" else "placeholders: {display_name}"
    text = (f"{em('admin')} {sc('send the new value for')} <b>{sc(META[key]['label'])}</b>\n"
            f"{sc('group value')}: <code>{esc(cur if cur not in (None, '') else '-')}</code>\n"
            f"{sc('hint')}: {esc(hint)}\n\n{sc('send - to use the global default')}")
    await _panel(cb, bot, text, _kb([[_vb("‹ " + sc("back"), f"gi:{cid}")]]))
    await cb.answer()


# ---------------- system tools ----------------
@owner_router.callback_query(F.data.startswith("sys:"))
async def system_action(cb: CallbackQuery, bot: Bot, db, manager):
    action, chat_id = cb.data[4:], cb.message.chat.id
    if action == "backup":
        await cb.answer(sc("preparing backup..."))
        path = await backup_database()
        try:
            await bot.send_document(chat_id, FSInputFile(path, filename=path.name),
                                    caption=f"{em('success')} {sc('database backup')}\n{sc('keep this file private')}")
        finally:
            path.unlink(missing_ok=True)
        log.info("owner downloaded a database backup")
    elif action == "errors":
        await cb.answer()
        await cb.message.answer(await asyncio.to_thread(read_errors, 15))
    elif action == "logfile":
        path = LOG_DIR / "bot.log"
        if path.exists():
            await bot.send_document(chat_id, FSInputFile(path, filename="bot.log"))
            await cb.answer()
        else:
            await cb.answer(sc("no log file yet"), show_alert=True)
    elif action == "update":
        await cb.answer(sc("checking for updates..."))
        await cb.message.answer(await update_ytdlp(manager))
    elif action == "cache":
        n = await db.cache_clear()
        log.info("owner cleared the file cache (%s)", n)
        await cb.answer(sc(f"{n} cached files cleared"), show_alert=True)
    else:
        await cb.answer()

# ======================================================================
# bot/handlers/members.py
# ======================================================================
members_router = Router(name="members")
GROUPS = F.chat.type.in_({"group", "supergroup"})


@members_router.my_chat_member(GROUPS)
async def bot_membership(event: ChatMemberUpdated, db):
    status = event.new_chat_member.status
    if status in ("member", "administrator"):
        await db.upsert_group(event.chat.id, event.chat.title or "")
        await db.set_group_active(event.chat.id, True)
    elif status in ("left", "kicked"):
        await db.set_group_active(event.chat.id, False)


@members_router.chat_member(GROUPS, ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def member_joined(event: ChatMemberUpdated, bot: Bot, db):
    user = event.new_chat_member.user
    if user.is_bot:
        return
    await db.upsert_group(event.chat.id, event.chat.title or "")
    group = await db.get_group(event.chat.id)
    if not group or not group["enabled"]:
        return
    await db.upsert_user(user.id, user.full_name)
    if db.get_bool("welcome_enabled") and Database.group_flag(group, "welcome", True):
        text = Database.group_get(group, "welcome_text", None) or None
        await send_welcome(bot, db, user.id, user.full_name, text)  # private only, never public

# ======================================================================
# bot/handlers/private.py
# ======================================================================
private_router = Router(name="private")


@private_router.message(F.chat.type == "private")
async def ignore_private(message: Message, db):
    user = message.from_user
    if user and not user.is_bot:
        await db.upsert_user(user.id, user.full_name)  # record only, never reply
        await db.set_dm(user.id, True)

# ======================================================================
# bot/handlers/group.py
# ======================================================================
log = logging.getLogger(__name__)
group_router = Router(name="group")
GROUP = F.chat.type.in_({"group", "supergroup"})
PLATFORMS = ("youtube", "instagram", "facebook", "twitter", "snapchat")

HELP = (
    f"{em('admin')} {sc('admin commands')}\n"
    f"/status - {sc('bot and permission status')}\n"
    f"/settings - {sc('group settings')}\n"
    f"/warns /unwarn - {sc('reply to a user')}\n"
    "/maintenance on|off"
)
SETTINGS_USAGE = (
    "/settings filter on|off\n"
    "/settings welcome on|off\n"
    "/settings welcometext &lt;text|-&gt;\n"
    "/settings maxsize &lt;mb&gt;\n"
    "/settings platform &lt;name&gt; on|off"
)


async def _note(bot: Bot, message: Message, text: str, delay: int = 8) -> None:
    try:
        sent = await bot.send_message(
            message.chat.id, text, disable_notification=True,
            message_thread_id=message.message_thread_id if message.is_topic_message else None)
        schedule_delete(bot, message.chat.id, sent.message_id, delay)
    except TelegramAPIError:
        pass


async def _rights_alert(bot: Bot, chat) -> None:
    await notify_owner_once(bot, f"rights:{chat.id}", missing_rights_text(chat.title, await diagnose(bot, chat.id)))


async def _violation(bot: Bot, db: Database, message: Message, user) -> None:
    """Telegram link/username was deleted: warn, and mute/ban at the limit."""
    chat = message.chat
    if not db.get_bool("warn_enabled"):
        if db.get_bool("filter_notice"):
            await _note(bot, message, f"{em('warning')} {mention(user.id, user.full_name)} "
                                      f"{sc('telegram links and usernames are not allowed')}", 5)
        return
    n, limit = await db.add_warn(chat.id, user.id), db.get_int("warn_limit")
    who = mention(user.id, user.full_name)
    if n < limit:
        await _note(bot, message, f"{em('warning')} {who} {sc('warning')} {n}/{limit}: "
                                  f"{sc('telegram links and usernames are not allowed')}")
        return
    await db.reset_warns(chat.id, user.id)
    action, minutes = db.get("warn_action"), db.get_int("warn_mute_minutes")
    ok = await restrict_user(bot, chat.id, user.id, action, minutes)
    log.info("warn limit reached user=%s chat=%s action=%s ok=%s", user.id, chat.id, action, ok)
    if ok:
        result = "banned" if action == "ban" else f"muted for {minutes} minutes"
        await _note(bot, message, f"{em('warning')} {who} {sc(f'reached {limit} warnings and was {result}')}", 10)
    else:
        await _rights_alert(bot, chat)


async def _group_settings(db: Database, chat_id: int, raw: str) -> str:
    parts = raw.split(None, 2)
    sub = parts[0].lower() if parts else ""
    arg = parts[1].lower() if len(parts) > 1 else ""
    note = ""
    if sub in ("filter", "welcome") and arg in ("on", "off"):
        await db.set_group_flag(chat_id, sub, arg == "on")
    elif sub == "welcometext" and len(parts) > 1:
        txt = raw.split(None, 1)[1].strip()
        await db.set_group_flag(chat_id, "welcome_text", "" if txt == "-" else txt[:500])
    elif sub == "maxsize" and arg.isdigit() and 1 <= int(arg) <= 2000:
        await db.set_group_flag(chat_id, "max_file_mb", int(arg))
    elif sub == "platform" and len(parts) > 2:
        name = "twitter" if arg == "x" else arg
        state = parts[2].strip().lower()
        if name in PLATFORMS and state in ("on", "off"):
            await db.set_group_flag(chat_id, f"plat_{name}", state == "on")
        else:
            note = sc("unknown platform or state")
    elif sub:
        note = sc("unknown option")
    g = await db.get_group(chat_id)
    on = lambda v: sc("on" if v else "off")  # noqa: E731
    gf = Database.group_flag
    mx = Database.group_get(g, "max_file_mb", None) or db.get_int("max_file_mb")
    lines = [
        f"{em('gear')} {sc('group settings')}",
        f"{sc('bot here')}: {on(g['enabled'])}",
        f"{sc('telegram link filter')}: {on(db.get_bool('filter_enabled') and gf(g, 'filter', True))}",
        f"{sc('welcome')}: {on(db.get_bool('welcome_enabled') and gf(g, 'welcome', True))}",
        f"{sc('max file size')}: {mx} {sc('mb')}",
    ] + [f"{sc(p)}: {on(db.get_bool('plat_' + p) and gf(g, 'plat_' + p, True))}" for p in PLATFORMS]
    if note:
        lines.append(f"\n{em('warning')} {note}")
    lines.append("\n" + SETTINGS_USAGE)
    return "\n".join(lines)


@group_router.message(GROUP, Command("start", "help", "settings", "status", "maintenance", "warns", "unwarn"))
async def admin_command(message: Message, command: CommandObject, bot: Bot, db: Database, manager: DownloadManager):
    if not await is_admin_message(bot, message):
        return  # unauthorized: no response at all
    chat, name = message.chat, command.command.lower()
    raw = (command.args or "").strip()
    await db.upsert_group(chat.id, chat.title or "")
    group = await db.get_group(chat.id)
    on = lambda v: sc("on" if v else "off")  # noqa: E731
    if name in ("start", "help"):
        text = HELP
    elif name == "status":
        r = await diagnose(bot, chat.id)
        text = (
            f"{em('gear')} {sc('status')}\n"
            f"{sc('bot is admin')}: {'✅' if r['admin'] else '❌'}\n"
            f"{sc('can delete messages')}: {'✅' if r['delete'] else '❌'}\n"
            f"{sc('bot here')}: {on(group['enabled'])}\n"
            f"{sc('active / queued')}: {manager.active} / {manager.waiting}"
        )
    elif name in ("warns", "unwarn"):
        target = message.reply_to_message.from_user if message.reply_to_message else None
        if not target:
            text = f"{em('warning')} {sc('reply to a user message')}"
        elif name == "warns":
            n = await db.get_warns(chat.id, target.id)
            text = f"{em('warning')} {mention(target.id, target.full_name)}: {n}/{db.get_int('warn_limit')}"
        else:
            await db.reset_warns(chat.id, target.id)
            text = f"{em('success')} {mention(target.id, target.full_name)} {sc('warnings cleared')}"
    elif name == "settings":
        text = await _group_settings(db, chat.id, raw)
        log.info("admin used /settings in %s", chat.id)
    else:  # maintenance: "on" pauses the bot in this group
        if raw.lower() in ("on", "off"):
            await db.set_group_enabled(chat.id, raw.lower() == "off")
            log.info("admin set group maintenance=%s in %s", raw.lower(), chat.id)
            group = await db.get_group(chat.id)
        text = f"{em('gear')} {sc('maintenance')}: {on(not group['enabled'])}"
    sent = await message.answer(text)
    schedule_delete(bot, chat.id, sent.message_id, 45 if name == "settings" else 30)


@group_router.message(GROUP, F.text | F.caption)
async def on_message(message: Message, bot: Bot, db: Database, manager: DownloadManager,
                     limiter: RateLimiter, flood: FloodGuard):
    user, chat = message.from_user, message.chat
    if message.sender_chat or not user or user.is_bot:
        return
    await db.upsert_group(chat.id, chat.title or "")
    group = await db.get_group(chat.id)
    if not group or not group["enabled"]:
        return
    await db.upsert_user(user.id, user.full_name)
    text = message.text or message.caption or ""
    if text.startswith("/"):
        return  # ordinary user commands are ignored silently
    entities = message.entities or message.caption_entities or []

    # ---- Telegram link / username filter (+ warn system) ----
    if db.get_bool("filter_enabled") and Database.group_flag(group, "filter", True):
        hit = (db.get_bool("filter_links") and has_telegram_link(text, entities)) or (
            db.get_bool("filter_usernames") and has_telegram_username(text, entities))
        if hit:
            exempt = db.get_bool("filter_exempt_admins") and (
                user.id == OWNER_ID or await is_group_admin(bot, chat.id, user.id))
            if not exempt:
                if await try_delete(message):
                    await _violation(bot, db, message, user)
                else:
                    await _rights_alert(bot, chat)
                return

    urls = extract_urls(text, entities)
    if not urls:
        return

    # ---- anti flood: too many link messages in a short window ----
    if db.get_bool("flood_enabled") and flood.hit(chat.id, user.id, db.get_int("flood_limit"),
                                                  db.get_int("flood_window")):
        if not (user.id == OWNER_ID or await is_group_admin(bot, chat.id, user.id)):
            flood.reset(chat.id, user.id)
            await try_delete(message)
            minutes = db.get_int("flood_mute_minutes")
            if await restrict_user(bot, chat.id, user.id, "mute", minutes):
                log.info("flood mute user=%s chat=%s", user.id, chat.id)
                await _note(bot, message, f"{em('warning')} {mention(user.id, user.full_name)} "
                                          f"{sc(f'muted for {minutes} minutes: too many links')}")
            else:
                await _rights_alert(bot, chat)
            return

    # ---- supported media links (several per message are queued in order) ----
    targets, seen = [], set()
    for u in urls:
        p = manager.detect(u)
        key = canon_url(u) if p else None
        if p and key not in seen:
            seen.add(key)
            if db.get_bool(f"plat_{p.key}") and Database.group_flag(group, f"plat_{p.key}", True):
                targets.append((p, u))
    targets = targets[: db.get_int("max_links")]
    if not targets or await db.is_blocked(user.id):
        return

    thread = message.message_thread_id if message.is_topic_message else None
    if db.get_bool("maintenance_enabled"):
        privileged = user.id == OWNER_ID or await is_group_admin(bot, chat.id, user.id)
        if not (db.get_bool("maintenance_bypass") and privileged):
            note = await bot.send_message(chat.id, f"{em('gear')} {sc(db.get('maintenance_text'))}",
                                          message_thread_id=thread, disable_notification=True)
            schedule_delete(bot, chat.id, note.message_id, 8)
            return

    if db.get_bool("force_join_enabled") and user.id != OWNER_ID:
        channels = parse_channels(db.get("force_channels"))
        if channels:
            missing = await missing_channels(bot, user.id, channels)
            if missing:
                note = await send_prompt(bot, db, message, missing)
                schedule_delete(bot, chat.id, note.message_id, 60)
                return

    if not limiter.allow(user.id, chat.id, db.get_int("user_cooldown"), db.get_int("group_per_minute")):
        return  # rate limited: silent, no spam
    for i, (provider, url) in enumerate(targets, 1):
        await run_video(bot, db, manager, message, provider, url, first=(i == 1), index=(i, len(targets)))

# ======================================================================
# bot/callbacks/forcejoin.py
# ======================================================================
forcejoin_router = Router(name="cb_forcejoin")


@forcejoin_router.callback_query(F.data == "fjc")
async def retry(cb: CallbackQuery, bot: Bot, db):
    channels = parse_channels(db.get("force_channels"))
    missing = await missing_channels(bot, cb.from_user.id, channels)
    if missing:
        await cb.answer(sc("you have not joined yet"), show_alert=True)
        return
    await cb.answer(sc("verified. send your link again."), show_alert=True)
    if isinstance(cb.message, Message):
        try:
            await cb.message.delete()
        except Exception:
            pass

# ======================================================================
# bot/callbacks/audio.py
# ======================================================================
log = logging.getLogger(__name__)
audio_router = Router(name="cb_audio")
MAX_AGE = 24 * 3600


async def _gate(cb: CallbackQuery, db, manager, limiter: RateLimiter, dl_id: int, sig: str, enabled_key: str):
    """Shared validation. Answers the callback itself on failure and returns None."""
    row = await db.get_download(dl_id)
    if (not row or row["status"] != "done" or row["media_type"] != "video"
            or not verify(dl_id, row["user_id"], sig) or row["group_id"] != cb.message.chat.id):
        await cb.answer(sc("this button is no longer valid"), show_alert=True)
        return None
    if cb.from_user.id != row["user_id"]:
        await cb.answer(sc("only the requester can use this button"), show_alert=True)
        return None
    if not db.get_bool(enabled_key):
        await cb.answer(sc("this option is disabled"), show_alert=True)
        return None
    age = (await db._one("SELECT strftime('%s','now') - strftime('%s', ?) a", (row["ts"],)))["a"]
    if age > MAX_AGE:
        await cb.answer(sc("this button has expired"), show_alert=True)
        return None
    provider = manager.provider(row["platform"])
    if not provider or not db.get_bool(f"plat_{row['platform']}"):
        await cb.answer(sc("platform unavailable"), show_alert=True)
        return None
    if not limiter.allow(cb.from_user.id, cb.message.chat.id, db.get_int("user_cooldown"), db.get_int("group_per_minute")):
        await cb.answer(sc("please wait a moment"))
        return None
    return row, provider


async def _strip(msg: Message, prefix: str) -> None:
    """Remove one button (by callback prefix) and keep the rest."""
    if not msg.reply_markup:
        return
    rows = [[b for b in row if not (b.callback_data or "").startswith(prefix)] for row in msg.reply_markup.inline_keyboard]
    rows = [r for r in rows if r]
    try:
        await msg.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=rows) if rows else None)
    except TelegramAPIError:
        pass


@audio_router.callback_query(F.data.startswith("a:"))
async def audio_button(cb: CallbackQuery, bot: Bot, db, manager, limiter: RateLimiter):
    if not isinstance(cb.message, Message):
        return await cb.answer()
    try:
        _, id_s, sig = cb.data.split(":")
        dl_id = int(id_s)
    except ValueError:
        return await cb.answer()
    gate = await _gate(cb, db, manager, limiter, dl_id, sig, "audio_enabled")
    if not gate:
        return
    row, provider = gate
    if not await db.claim_audio(dl_id):
        return await cb.answer(sc("audio already requested"))
    await cb.answer()
    ok = await run_audio(bot, db, manager, cb, row, provider)
    await db.set_audio_state(dl_id, 2 if ok else 0)
    if ok:
        await _strip(cb.message, "a:")


@audio_router.callback_query(F.data.startswith("q:"))
async def quality_button(cb: CallbackQuery, bot: Bot, db, manager, limiter: RateLimiter):
    if not isinstance(cb.message, Message):
        return await cb.answer()
    try:
        _, id_s, q_s, sig = cb.data.split(":")
        dl_id, quality = int(id_s), int(q_s)
    except ValueError:
        return await cb.answer()
    if quality not in QUALITIES:
        return await cb.answer()
    gate = await _gate(cb, db, manager, limiter, dl_id, sig, "quality_buttons")
    if not gate:
        return
    row, provider = gate
    await cb.answer()
    await run_quality(bot, db, manager, cb, row, provider, quality)


@audio_router.callback_query(F.data.startswith("t:"))
async def thumb_button(cb: CallbackQuery, bot: Bot, db, manager, limiter: RateLimiter):
    if not isinstance(cb.message, Message):
        return await cb.answer()
    try:
        _, id_s, sig = cb.data.split(":")
        dl_id = int(id_s)
    except ValueError:
        return await cb.answer()
    gate = await _gate(cb, db, manager, limiter, dl_id, sig, "thumbnail_enabled")
    if not gate:
        return
    row, provider = gate
    await cb.answer()
    if await run_thumb(bot, db, manager, cb, row, provider):
        await _strip(cb.message, "t:")

# ======================================================================
# main.py
# ======================================================================
log = logging.getLogger("main")


async def main() -> None:
    validate_config()
    setup_logging()
    wipe_all()
    db = Database(DB_PATH)
    await db.connect()
    manager = DownloadManager(db.get_int("concurrent_downloads"))

    bot = Bot(BOT_TOKEN, session=AiohttpSession(timeout=600),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage(), db=db, manager=manager,
                    limiter=RateLimiter(), flood=FloodGuard(), started_at=time.time())
    # order matters: owner panel first, then private catch-all, then group logic
    dp.include_routers(owner_router, private_router, members_router,
                       audio_router, forcejoin_router, group_router)

    sweep_task = asyncio.create_task(sweeper(db))
    update_task = asyncio.create_task(auto_updater(bot, db, manager))
    try:
        me = await bot.get_me()
        log.info("startup: @%s (id %s)", me.username, me.id)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        log.info("shutdown")
        sweep_task.cancel()
        update_task.cancel()
        await bot.session.close()
        await db.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
