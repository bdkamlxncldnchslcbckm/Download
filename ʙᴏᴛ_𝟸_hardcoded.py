#!/usr/bin/env python3
"""KD Messaging Studio — one-source-file application, Python 3.11+.

INSTALL / CONFIGURE (Linux, private host; no .env file required)
    python -m pip install aiogram==3.31.0 Telethon==1.45.0 cryptography==46.0.5
    python main.py --keygen
Copy the printed shell exports into a private operator environment. Preserve both
keys separately from database backups. Do not share the private RSA/Fernet keys.
Edit the four hardcoded values at the beginning of serve():
    token = 'PASTE_YOUR_BOT_TOKEN_HERE'  # Replace with your actual bot token.
    owners = {0}  # Replace 0 with your numeric Telegram user ID.
    owner_name = 'KD'
    developer_name = 'KD'
These four values are not read from environment variables. On each startup, the
hardcoded names replace the saved owner/developer display names. Session encryption
and provisioning keys still use the environment exports from --keygen.
    export KD_DB='./kd.sqlite3'
    python main.py --self-test
    python main.py
Only main.py is a source deliverable. SQLite, WAL, SHM, lock files and protected
backups are runtime data. Run ONE process per database. SQLite suits one small
installation, not a horizontally scaled service. Use a persistent private disk,
process supervision, a non-root OS user, and restrictive filesystem permissions.
No shell, eval, filesystem browser, or remotely supplied Python is exposed.

ACCOUNT CONNECTION (same Telegram identity as the control-bot customer)
Tap Connect Account, copy the public key and short-lived challenge. On a trusted
LOCAL terminal, with this same source and dependencies, run:
    python main.py --authorize
Paste the public key and challenge when asked. Enter API_ID, API_HASH, phone, OTP
and optional 2FA locally. Only the encrypted KD1 package is sent to the control
bot. The bot decrypts it, validates the challenge and get_me().id against the
customer, then encrypts the session at rest. The RSA public key must be obtained
from your authentic control bot. Session custody gives this server account access;
use only a server/operator you trust. No plaintext session import is accepted.
One active session per customer; no account rotation or third-party accounts.
Deleting stored credentials DOES NOT revoke Telegram authorization. Use Revoke
Session before deletion or Telegram Settings > Devices to terminate the session.

OPERATING GUIDE
/start shows the menu; names are clickable tg://user links, never public handles.
Owner Panel > Plans: edit each plan using the supplied JSON form before checkout.
Month labels default to fixed 30/60/90 days. XTR denotes Telegram Stars. No
recurring debit is created. Purchase and activation are separate transactions.
Paid orders enter owner review; approval asks the purchaser to confirm a user ID.
A different beneficiary must first /start; owner sees both IDs before activation.
Rejecting a paid order initiates a Stars refund, not an unannounced forfeiture.
/approve USER_ID DAYS grants an explicit manual exception; /revoke USER_ID,
/stats, /users, /paysupport, /massdm TEXT, /unsubscribe are supported.

Create an audience by connecting a channel/group: both the customer and this bot
must be administrators. Set its specific immutable purpose. Share the consent
link. Recipients first consent in the control bot, then send /kdconsent TOKEN to
the customer's account using the displayed profile link. This second step proves
reachability and gives the sender its own account-scoped access hash. No member
scraping, ID imports, or silent bot-sent campaign substitutions are implemented.
Recipients can /unsubscribe in the control bot or /stop in the sending-account
chat. /stop TOKEN withdraws one audience; /stop withdraws all from that sender.
Consent is rechecked for every send; a request already in flight cannot be recalled.
Before each send the account checks up to 101 messages after the consent proof
in that private conversation, catching /stop sent during downtime. If history
exceeds this bounded check, sending is skipped until consent is renewed. This
conservative safeguard avoids silently missing an offline withdrawal.

Campaign wizard: account > audience > original text > exact preview > confirm or
schedule. Schedule with UTC ISO-8601, e.g. 2026-12-01T12:00:00+00:00. Campaigns
send plain text via Telethon with parse_mode=None, no buttons and no link preview.
The branded UI does not alter customers' outgoing content. Pause/cancel stop the
next send, not an RPC already in flight. Counters mean API acceptance, not reads.
Network/timeout outcomes become UNCERTAIN and are never automatically replayed;
restart converts in-flight deliveries to uncertain. Exactly-once is not promised.
FloodWait persists an account-wide deadline. PeerFlood/auth failures block the
account and pause its campaigns; reconnect only after resolving restrictions.
Global emergency stop and expired/revoked access pause campaigns. Resume is manual.
Default one worker, 5-second account spacing; this is NOT ban prevention.

OWNER CONFIGURATION
All business settings are edited through validated JSON forms behind owner-only
buttons. Menu labels/styles use stable action keys; blank or duplicate labels are
rejected. Welcome text is literal text, not arbitrary HTML. English UI strings use
small caps; identifiers, URLs, API data and customer message bodies remain intact.
Owner name/developer name, support owner ID, custom emoji pool, verified flag map,
welcome/working media, membership gates, referral days, limits and retention are
editable. Owner recovery bypasses force-join/maintenance, but NOT recipient consent.
Media editors accept Telegram photo/animation messages or '-' to remove media.
Working animation is an optional uploaded animation; absent it, Telegram typing
and animated custom emoji (where available) are used. No artificial edit loops.

EMOJI / TELEGRAM LIMITATIONS (official docs checked during preparation)
https://core.telegram.org/bots/api#keyboardbutton
https://core.telegram.org/bots/api#inlinekeyboardbutton
https://core.telegram.org/bots/api#formatting-options
https://core.telegram.org/bots/payments-stars
https://docs.telethon.dev/en/stable/
Native styles: success/green, danger/red, primary/blue. Bot API 9.4+ fields are
supported by pinned aiogram. Custom emoji requires the documented Fragment/bot-owner
Premium eligibility. Toggle custom_emoji_enabled only when eligible. Diagnostics
checks sticker IDs against Telegram and flags mismatched country mappings; it
cannot prove account entitlement or identical client rendering. Telegram requires
an ordinary emoji INSIDE tg-emoji as fallback metadata; notifications/old clients
may display it. If IDs are unavailable, decoration is omitted, never replaced by
unrelated random emojis. The supplied flag mapping contains duplicate/conflicting
IDs: mismatched flags are disabled until corrected. No usernames are displayed;
Telegram deep-link URLs necessarily contain the bot's handle internally.

PAYMENTS / UPI
Digital services sold inside Telegram use Stars. UPI checkout is deliberately
DISABLED and cannot be toggled on in this digital-subscription deployment. The
requested alternative would be: immutable order > QR generated locally from UPI
ID and amount > screenshot/UTR > independent settlement check > payment review >
separate activation. QR/screenshot/UTR alone does not prove payment. No UPI QR or
payment-evidence collection is exposed in the live Stars flow; Stars charge IDs
are stored as evidence. No Stripe, PayPal or cryptocurrency integration.

SECURITY / RETENTION / BACKUP
The bot token is configured in serve(); encryption keys remain environment-only.
Logs contain event/error class, never exception
messages, input, tokens or session material. Runtime owner logs omit credentials.
Backup button saves an additional fully Fernet-encrypted consistent SQLite snapshot
under KD_BACKUP_DIR (default ./kd-backups), with 0600 permissions. It never sends
session backups through Telegram. Restore while the service is STOPPED:
    python main.py --restore /absolute/path/to/backup.kdbak
Restore validates decrypted SQLite and schema, then atomically replaces KD_DB;
existing data is preserved in a timestamped private pre-restore copy. Never rotate
SESSION_KEY without decrypt/re-encrypt migration. Keep RSA provisioning key stable.
/delete_data purges account credentials, workflows, consents and message bodies;
transactional payment/subscription/audit records are retained for reconciliation.
Owner retention_days (default 90) removes old terminal campaign bodies, results,
expired UI tokens and notification records. Audit and financial records remain;
choose legal retention requirements with your operator before a live deployment.

TESTING / DEPLOYMENT GATES
--self-test uses temporary SQLite only, no Telegram calls. It covers authorization,
row ownership, consent withdrawal, expiry/renewal, order stages, duplicate grants,
referrals, rendering, callback expiry/replay, campaign controls/recovery and waits.
Dependency import and self-tests were checked in the build environment; no real
bot token/account/payment was supplied, so LIVE TESTING HAS NOT BEEN PERFORMED.
The 15 included offline self-tests passed during preparation.
Before sale, test two different users; owner impersonation; invalid callbacks;
Stars success, duplicate update, refund and disputed/refunded service events;
manual activation and expiry; permissions lost mid-campaign; consent withdrawal;
FloodWait; crash while sending; backup/restore; custom emoji eligibility; media;
force-join outage; every UI form; and an encrypted session disconnect/revoke.
No claim of zero errors, guaranteed delivery or production certification is made.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import contextlib
import copy
import fcntl
import getpass
import hashlib
import html
import io
import json
import logging
import os
import re
import secrets
import shutil
import sqlite3
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

try:
    from aiogram import Bot, Dispatcher, F
    from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
    from aiogram.types import (Message, CallbackQuery, PreCheckoutQuery, InlineKeyboardMarkup,
                               InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice)
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from telethon import TelegramClient, events, errors
    from telethon.sessions import StringSession
    from telethon.tl.types import InputPeerUser
except ImportError as exc:
    raise SystemExit('Install dependencies listed in the opening main.py docstring. Missing: ' + exc.name)

DAY = 86400
EMOJI_MAPPING = {
    '✅': ['6246537187614005254', '6246782404476803545'], '✔️': ['6246871001062185760'],
    '☑️': ['6246537187614005254'], '👁️': ['6035338338406242050', '6035051267087143217'],
    '👁': ['6035338338406242050'], '👀': ['6035225389356290238', '6035081585261287115'],
    '🔥': ['4956222745814762495', '4956606007221421405'], '💥': ['6032673796530377389'],
    '⚡': ['5791970059597386804'], '❤️': ['5783157259152397008', '5801084710343938087'],
    '💙': ['5780496071645991525'], '💚': ['5888789252493283486'], '💛': ['5840261097719148872'],
    '🧡': ['5840263144212529797'], '💜': ['5840265018655703965'], '🖤': ['5840266939932994956'],
    '⭐': ['6244496562752331516', '5904618938578243567'], '🌟': ['6010156854955480259'],
    '✨': ['6010338729640596556', '6010086134023985536'], '🧛': ['6034871295072539452'],
    '🧛‍♂️': ['6034871295072539452'], '👹': ['6034962795055812935'], '👺': ['6034962795055812935'],
    '👻': ['6035070298087231243'], '👿': ['6035242444671421879'],
    '😈': ['6035136809950778133', '6032695825417638128'], '👑': ['5794422335599546668', '6089003761496232797'],
    '💰': ['6089104607328342288', '6086730718774300509'], '💵': ['6089140105233044310'],
    '💎': ['6086778246882399112', '5791697221799907788'], '👍': ['6089313931149448495', '4958626617535497157'],
    '👎': ['6088789257285988672'], '👏': ['6093744967304352336'], '😀': ['6093864814071780526'],
    '😁': ['6035060329468137931'], '😂': ['5782741660936966676', '5782746664573867142'],
    '😃': ['6035337951859184840'], '😄': ['5782942227319756256'], '😅': ['5782670102486848559'],
    '😆': ['5782670102486848559'], '😉': ['6089024570612781324'], '😊': ['5780690182692935276'],
    '😍': ['6010179687001625256'], '🥰': ['6044369013952222465', '6044359320211034681'],
    '😘': ['6044373012566774137'], '😎': ['6032853480782172520', '6044373012566774137'],
    '😢': ['5780793884678296697'], '😭': ['5783024321324651865'], '😤': ['6034865170449175739'],
    '😠': ['6035355642829475999'], '😡': ['6035355642829475999'],
    '🤔': ['5782756916660802905', '5783034045130610245'],
}
FLAG_MAPPING = dict(zip(
    '🇺🇸 🇬🇧 🇫🇷 🇩🇪 🇮🇳 🇯🇵 🇨🇳 🇷🇺 🇧🇷 🇮🇹 🇨🇦 🇦🇺 🇰🇷 🇪🇸 🇲🇽 🇮🇩 🇳🇱 🇹🇷 🇸🇦 🇦🇪 🇿🇦 🇵🇰 🇧🇩 🇱🇰 🇳🇵 🇲🇾 🇸🇬 🇵🇭 🇻🇳 🇹🇭 🇪🇬 🇳🇬 🇰🇪 🇦🇷 🇨🇱 🇵🇪 🇨🇴 🇻🇪 🇵🇹 🇸🇪 🇳🇴 🇩🇰 🇫🇮 🇮🇪 🇨🇭 🇦🇹 🇧🇪 🇬🇷 🇨🇿 🇭🇺 🇵🇱 🇷🇴 🇺🇦'.split(),
    '5433865586356531140 5433827537241258614 5433636707549331311 5433845881046578644 5433601609076586221 5434147542369579483 5435996255207567113 5433674924168328689 5433825269498525925 5433627189901801019 5433979415874779870 5434067655977874913 5434142701941437163 5434026158003862063 5434131139889478358 5431739800883312139 5431656358258685474 5433792911214917126 5433991338703991663 5434013938821902926 5431489619038320862 5434064563601421981 5433854239052935880 5433609855413794108 5433852744404317916 5431620340662940910 5433884376838454074 5434119663736862995 5431676201007592926 5433814347396692144 5433643519367461444 5433982207603520017 5433845881046578644 5433845881046578644 5433827537241258614 5433827537241258614 5433825269498525925 5433767976937585990 5433598722858562967 5433628435442316429 5434098446598419585 5434129692485498098 5434115081006756195 5434012796360604182 5433902785068283672 5434027579638035690 5431755073787016798 5433972762970437003 5434115081006756195 5434001565021123877 5433833485770964033 5434132406904830055 5434132406904830055'.split()))
PRIMARY_EMOJIS = '''6035051267087143217 6034945975963881533 6034845323405299835 6035169816774446606
6035085583875837709 6032965553658794901 6035158121578501544 6035208832257364215 6035067476293718178
6033130342964007608 6035179291472302298 6034986056598688136 6032765485492214347 6032660275973330342
6034916516783198293 6034904439335162652 6034928023000585140 6035372904303038740 6035137110598492010
6035338338406242050 6035225389356290238 6035081585261287115 6035243995154616907 6034865170449175739
6035173858338672933 6035210301136182368 6035265083444042235 6034871295072539452 6035251193519805118
6035136809950778133 6032695825417638128 6032739101508113500 6032985916098750553 6035374291577475270
6035355642829475999 6035337951859184840 6035072209347678547 6035060329468137931 6033077437556855182
6032823763903452409 6034853694296560978 6035015146412183834 6035372401791864953 6034955549445984368
6032673796530377389 6032916496542339992 6034855438053282213 6034962795055812935 6034832094906028632
6035087164423802534 6035343380697846690 6032737138708059114 6035194237958493530 6035317340311129897
6035070298087231243 6035242444671421879 6034957847253487695 6034925781027656042 6033067975743902590
6032975015471747801 6034926000070988470 6034843326245508065 6032853480782172520 6044373012566774137
6044369013952222465 6044359320211034681 6044290806892729376 6044238120528908813 5791970059597386804
5794422335599546668'''.split()
ALL_PREMIUM_EMOJIS = list(dict.fromkeys(PRIMARY_EMOJIS + '''6246537187614005254 6246610665914505571
6244496562752331516 6246782404476803545 6247039939305808563 6246774261218810895 6246871001062185760
5780840497958360623 5780413823022273797 5782940582347281850 5783091623462180025 5783151611270403662
5783124312458270318 5782741660936966676 5782753386197685582 5783029694328738752 5782671841948603573
5780425243340313827 5783170625090622777 5782858359493366808 5783016603268420398 5782914709464289647
5782897082918507949 5783023329187206172 5782731481864475831 5782734256413349701 5783133172975801184
5783157259152397008 5783175250770399822 5782876166427775766 5782804668107199927 5783176625159935132
5782829832320586664 5782670102486848559 5782901906166780625 6084695058894819673 6086730718774300509
6086664791026307819 6089003761496232797 6298332994260175589 6296140830067395531 6298821774423361023
6136464120779638846 4956222745814762495 4958617898751886363 4958479549265347295 4958624886663678191'''.split()))
SMALL_CAPS_MAP = str.maketrans(dict(zip('abcdefghijklmnopqrstuvwxyz', 'ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ')))
MENU = {'home':'Home','plans':'Buy Subscription','subscription':'My Subscription',
        'connect':'Connect Account','accounts':'Connected Accounts','audiences':'Connect Channel / Group',
        'create':'Create Message','campaigns':'Start Campaign','history':'My Campaigns',
        'referrals':'Referral Dashboard','profile':'My Profile / My ID','support':'Support',
        'help':'Help','payments':'Payment Status','unsubscribe':'Unsubscribe','owner':'Owner Panel'}
DEFAULTS = {
    'welcome':'Your private command centre is ready. Create with clarity. Deliver with consent.',
    'owner_name':'KD', 'developer_name':'KD',
    'support_id':0, 'help':'Connect your account securely, create an audience, invite opt-ins, preview and send.',
    'timezone':'Asia/Kolkata', 'maintenance':False, 'emergency_stop':False,
    'custom_emoji_enabled':False, 'referral_days':0, 'max_recipients':500,
    'daily_limit':1000, 'send_interval':5, 'max_accounts':50, 'retention_days':90,
    'welcome_media':None, 'working_media':None,
    'emoji':EMOJI_MAPPING, 'flags':FLAG_MAPPING, 'primary_emojis':PRIMARY_EMOJIS,
    'premium_pool':ALL_PREMIUM_EMOJIS, 'labels':MENU,
    'styles':{'positive':'success','destructive':'danger','navigation':'primary'},
}


def now() -> int:
    return int(time.time())


def sc(text: str) -> str:
    """ONLY trusted display labels; never apply this to assembled HTML or user data."""
    # Keep literal URLs, commands and handles in owner-editable display text intact.
    parts = re.split(r'((?:https?://|tg://)\S+|@[A-Za-z0-9_]+|/[A-Za-z0-9_]+)',text)
    return ''.join(p if i % 2 else p.lower().translate(SMALL_CAPS_MAP) for i,p in enumerate(parts))


def e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def mention(uid: int, name: str) -> str:
    return f'<a href="tg://user?id={int(uid)}">{e(name)}</a>'


def require(test: Any, message: str) -> None:
    if not test:
        raise ValueError(message)


def integer(value: Any, minimum: int = 1, maximum: int = 10**15) -> int:
    require(type(value) is int and minimum <= value <= maximum, 'Invalid integer or range.')
    return value


def log_event(event: str, error: Exception | None = None) -> None:
    print(json.dumps({'time':now(),'event':event,'error':type(error).__name__ if error else None}), flush=True)


def audit(c: sqlite3.Connection, actor: int, action: str, target: Any, detail: Any = None) -> None:
    c.execute('INSERT INTO audit(actor,action,target,detail,at) VALUES(?,?,?,?,?)',
              (actor,action,str(target),json.dumps(detail or {}),now()))


SCHEMA = '''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,expires INTEGER NOT NULL DEFAULT 0,
 banned INTEGER NOT NULL DEFAULT 0,limits TEXT NOT NULL DEFAULT '{}',referrer INTEGER REFERENCES users(id),created INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS plans(id INTEGER PRIMARY KEY,body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY,uid INTEGER NOT NULL REFERENCES users(id),snapshot TEXT NOT NULL,
 state TEXT NOT NULL,charge TEXT UNIQUE,beneficiary INTEGER REFERENCES users(id),created INTEGER NOT NULL,activated_days INTEGER);
CREATE TABLE IF NOT EXISTS grants(id TEXT PRIMARY KEY,uid INTEGER NOT NULL REFERENCES users(id),days INTEGER NOT NULL,
 source TEXT NOT NULL,at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS rewards(order_id TEXT PRIMARY KEY REFERENCES orders(id),referrer INTEGER NOT NULL REFERENCES users(id),
 days INTEGER NOT NULL,reversed INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS payment_events(charge TEXT PRIMARY KEY,order_id TEXT NOT NULL,uid INTEGER NOT NULL,
 currency TEXT NOT NULL,amount INTEGER NOT NULL,state TEXT NOT NULL,created INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS checkout_reservations(order_id TEXT PRIMARY KEY REFERENCES orders(id),
 query_id TEXT NOT NULL,expires INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS accounts(uid INTEGER PRIMARY KEY REFERENCES users(id),secret TEXT NOT NULL,revision TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'connected',next_at INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS audiences(id INTEGER PRIMARY KEY AUTOINCREMENT,uid INTEGER NOT NULL REFERENCES users(id),
 chat INTEGER NOT NULL,title TEXT NOT NULL,purpose TEXT NOT NULL,token TEXT UNIQUE NOT NULL,enabled INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS consent(audience INTEGER NOT NULL REFERENCES audiences(id),recipient INTEGER NOT NULL REFERENCES users(id),
 state TEXT NOT NULL,peer_hash TEXT,at INTEGER NOT NULL,PRIMARY KEY(audience,recipient));
CREATE TABLE IF NOT EXISTS consent_proofs(audience INTEGER NOT NULL REFERENCES audiences(id),recipient INTEGER NOT NULL REFERENCES users(id),
 message_id INTEGER NOT NULL,PRIMARY KEY(audience,recipient));
CREATE TABLE IF NOT EXISTS campaigns(id INTEGER PRIMARY KEY AUTOINCREMENT,uid INTEGER NOT NULL REFERENCES users(id),
 audience INTEGER NOT NULL REFERENCES audiences(id),body TEXT NOT NULL,state TEXT NOT NULL DEFAULT 'draft',
 next_at INTEGER NOT NULL DEFAULT 0,created INTEGER NOT NULL,reason TEXT NOT NULL DEFAULT '',report_at INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS deliveries(campaign INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
 recipient INTEGER NOT NULL REFERENCES users(id),state TEXT NOT NULL DEFAULT 'pending',tries INTEGER NOT NULL DEFAULT 0,
 next_at INTEGER NOT NULL DEFAULT 0,reason TEXT NOT NULL DEFAULT '',message_id INTEGER,at INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(campaign,recipient));
CREATE TABLE IF NOT EXISTS required_channels(id INTEGER PRIMARY KEY,link TEXT NOT NULL,enabled INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS workflows(uid INTEGER PRIMARY KEY REFERENCES users(id),body TEXT NOT NULL,expires INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS callbacks(token TEXT PRIMARY KEY,uid INTEGER NOT NULL REFERENCES users(id),body TEXT NOT NULL,
 expires INTEGER NOT NULL,used INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY AUTOINCREMENT,uid INTEGER NOT NULL,body TEXT NOT NULL,
 state TEXT NOT NULL DEFAULT 'pending',tries INTEGER NOT NULL DEFAULT 0,next_at INTEGER NOT NULL DEFAULT 0,created INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,actor INTEGER NOT NULL,action TEXT NOT NULL,
 target TEXT NOT NULL,detail TEXT NOT NULL,at INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS monitors(campaign INTEGER PRIMARY KEY REFERENCES campaigns(id),uid INTEGER NOT NULL,
 message_id INTEGER NOT NULL,updated INTEGER NOT NULL DEFAULT 0);
CREATE INDEX IF NOT EXISTS jobs_ready ON campaigns(state,next_at);
CREATE INDEX IF NOT EXISTS recipient_jobs ON deliveries(state,next_at);
CREATE INDEX IF NOT EXISTS audience_owner ON audiences(uid);
CREATE INDEX IF NOT EXISTS orders_owner ON orders(uid,created);
CREATE INDEX IF NOT EXISTS outbox_ready ON outbox(state,next_at);
CREATE INDEX IF NOT EXISTS accepted_today ON deliveries(at,state);
PRAGMA user_version=1;
'''


class DB:
    """Each callable is one serialized transaction, executed off the event loop."""
    def __init__(self, path: str):
        self.path = path
        self.lock = asyncio.Lock()

    async def run(self, fn: Callable) -> Any:
        async with self.lock:
            def execute():
                c = sqlite3.connect(self.path, timeout=15)
                c.row_factory = sqlite3.Row
                c.execute('PRAGMA foreign_keys=ON')
                c.execute('PRAGMA busy_timeout=15000')
                try:
                    c.execute('BEGIN IMMEDIATE')
                    result = fn(c)
                    c.commit()
                    return result
                except BaseException:
                    c.rollback()
                    raise
                finally:
                    c.close()
            return await asyncio.to_thread(execute)

    async def rows(self, sql: str, args: tuple = ()) -> list[dict]:
        return await self.run(lambda c:[dict(r) for r in c.execute(sql,args)])

    async def one(self, sql: str, args: tuple = ()) -> dict | None:
        rows = await self.rows(sql,args)
        return rows[0] if rows else None

    async def execute(self, sql: str, args: tuple = ()) -> None:
        await self.run(lambda c:c.execute(sql,args).rowcount)

    async def initialize(self):
        def init():
            c = sqlite3.connect(self.path)
            try:
                c.execute('PRAGMA journal_mode=WAL')
                require(c.execute('PRAGMA user_version').fetchone()[0] in (0,1), 'Unsupported database version.')
                c.executescript(SCHEMA)
                for k,v in DEFAULTS.items():
                    c.execute('INSERT OR IGNORE INTO settings VALUES(?,?)',(k,json.dumps(v)))
                for i,days in enumerate((30,60,90),1):
                    body = dict(name=f'{i} month',price=0,days=days,description='Configure price and features.',
                                enabled=False,max_recipients=500,daily_limit=1000)
                    c.execute('INSERT OR IGNORE INTO plans VALUES(?,?)',(i,json.dumps(body)))
                c.commit()
            finally:
                c.close()
        await asyncio.to_thread(init)
        os.chmod(self.path,0o600)

    async def settings(self) -> dict:
        return {r['key']:json.loads(r['value']) for r in await self.rows('SELECT * FROM settings')}

    async def register(self, uid: int, name: str, referrer: int | None = None):
        def job(c):
            ref = c.execute('SELECT id FROM users WHERE id=?',(referrer,)).fetchone()
            c.execute('INSERT INTO users(id,name,created,referrer) VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name',
                      (uid,name[:128],now(),referrer if ref and referrer != uid else None))
        await self.run(job)

    async def state(self, uid: int, data: dict | None = None):
        if data is not None:
            await self.execute('INSERT OR REPLACE INTO workflows VALUES(?,?,?)',(uid,json.dumps(data),now()+1800))
        else:
            row = await self.one('SELECT body FROM workflows WHERE uid=? AND expires>?',(uid,now()))
            return json.loads(row['body']) if row else {}

    async def token(self, uid: int, action: str, data: Any = None) -> str:
        token = secrets.token_urlsafe(12)
        await self.execute('INSERT INTO callbacks VALUES(?,?,?,?,0)',(token,uid,json.dumps([action,data]),now()+1800))
        return token

    async def consume(self, uid: int, token: str) -> tuple:
        def job(c):
            r = c.execute('SELECT * FROM callbacks WHERE token=?',(token,)).fetchone()
            require(r and r['uid']==uid and not r['used'] and r['expires']>now(), 'Button expired or already used. Reopen the menu.')
            c.execute('UPDATE callbacks SET used=1 WHERE token=?',(token,))
            return json.loads(r['body'])
        return await self.run(job)

    async def recover(self):
        await self.execute("UPDATE deliveries SET state='uncertain',reason='process_restart' WHERE state='sending'")
        await self.execute("UPDATE orders SET state='refund_retry' WHERE state='refunding'")


def enqueue(c, uid: int, body: str):
    c.execute('INSERT INTO outbox(uid,body,created) VALUES(?,?,?)',(uid,body,now()))


def grant(c, uid: int, days: int, key: str, source: str) -> bool:
    integer(days,1,3650)
    user = c.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
    require(user and not user['banned'], 'User must /start first and must not be banned.')
    if c.execute('SELECT 1 FROM grants WHERE id=?',(key,)).fetchone():
        return False
    c.execute('INSERT INTO grants VALUES(?,?,?,?,?)',(key,uid,days,source,now()))
    c.execute('UPDATE users SET expires=? WHERE id=?',(max(now(),user['expires'])+days*DAY,uid))
    return True


class Service:
    def __init__(self, db: DB, owners: set[int]):
        self.db, self.owners = db, owners

    def owner(self, uid: int):
        require(uid in self.owners, 'Owner access required.')

    async def paid(self, uid: int):
        r = await self.db.one('SELECT * FROM users WHERE id=?',(uid,))
        require(r and (uid in self.owners or (not r['banned'] and r['expires']>now())), 'An active subscription is required. Open Buy Subscription.')
        return r

    async def owned(self, table: str, key: int, uid: int):
        require(table in ('campaigns','audiences'), 'Unsupported resource.')
        r = await self.db.one(f'SELECT * FROM {table} WHERE id=? AND uid=?',(key,uid))
        require(r, 'This resource is unavailable for your account.')
        return r

    async def order(self, uid: int, plan_id: int) -> str:
        def job(c):
            row = c.execute('SELECT body FROM plans WHERE id=?',(plan_id,)).fetchone()
            require(row,'Plan missing.')
            p = json.loads(row['body'])
            require(p['enabled'] and p['price']>0,'Owner must configure this plan first.')
            oid = secrets.token_urlsafe(16)
            c.execute('INSERT INTO orders(id,uid,snapshot,state,created) VALUES(?,?,?,?,?)',
                      (oid,uid,json.dumps(p),'awaiting_payment',now()))
            return oid
        return await self.db.run(job)

    async def received(self, uid: int, oid: str, charge: str, currency: str, amount: int):
        def job(c):
            if c.execute('SELECT 1 FROM payment_events WHERE charge=?',(charge,)).fetchone():
                return
            r = c.execute('SELECT * FROM orders WHERE id=? AND uid=?',(oid,uid)).fetchone()
            valid = r and currency=='XTR' and json.loads(r['snapshot'])['price']==amount
            # A second real charge is financial evidence, never discarded as an
            # exception. Queue its own refund without altering the first grant.
            if not valid or (r['charge'] and r['charge']!=charge):
                c.execute('INSERT INTO payment_events VALUES(?,?,?,?,?,?,?)',
                          (charge,oid,uid,currency,amount,'refund_pending',now()))
                audit(c,uid,'unapplied_payment',oid)
                enqueue(c,uid,sc('A duplicate or unmatched payment was recorded for refund review. Contact /paysupport.'))
                for owner in self.owners:
                    enqueue(c,owner,sc('Unapplied payment recorded for refund:')+' '+e(oid))
                return
            c.execute('INSERT INTO payment_events VALUES(?,?,?,?,?,?,?)',
                      (charge,oid,uid,currency,amount,'applied',now()))
            if r['charge']==charge:
                return
            require(r['state']=='awaiting_payment' and not r['charge'], 'Order already paid; contact support.')
            c.execute("UPDATE orders SET state='pending_review',charge=? WHERE id=?",(charge,oid))
            audit(c,uid,'payment_received',oid)
            enqueue(c,uid,sc('Payment received. Owner review is pending. Access is not yet active.'))
            for owner in self.owners:
                enqueue(c,owner,sc('New Stars payment awaiting review.')+'\n'+e(oid))
        await self.db.run(job)

    async def review(self, actor: int, oid: str):
        self.owner(actor)
        def job(c):
            r = c.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone()
            require(r and r['state']=='pending_review','Order is not awaiting payment review.')
            c.execute("UPDATE orders SET state='awaiting_beneficiary' WHERE id=?",(oid,))
            audit(c,actor,'payment_approved',oid)
            enqueue(c,r['uid'],sc('Payment approved. Open Payment Status and confirm the beneficiary ID.'))
        await self.db.run(job)

    async def beneficiary(self, uid: int, oid: str, target: int):
        def job(c):
            r = c.execute('SELECT * FROM orders WHERE id=? AND uid=?',(oid,uid)).fetchone()
            require(r and r['state']=='awaiting_beneficiary','Order cannot accept a beneficiary now.')
            require(c.execute('SELECT 1 FROM users WHERE id=?',(target,)).fetchone(),'Beneficiary must /start this bot first.')
            c.execute("UPDATE orders SET state='awaiting_activation',beneficiary=? WHERE id=?",(target,oid))
            audit(c,uid,'beneficiary_confirmed',oid,{'beneficiary':target})
            for owner in self.owners:
                enqueue(c,owner,sc('An order is ready for separate access activation.')+'\n'+e(oid))
        await self.db.run(job)

    async def activate(self, actor: int, oid: str, days: int):
        self.owner(actor)
        def job(c):
            r = c.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone()
            require(r and r['state']=='awaiting_activation','Already activated or not ready.')
            grant(c,r['beneficiary'],days,'order:'+oid,'purchase')
            p = json.loads(r['snapshot'])
            c.execute('UPDATE users SET limits=? WHERE id=?',(json.dumps({k:p[k] for k in ('max_recipients','daily_limit')}),r['beneficiary']))
            c.execute("UPDATE orders SET state='active',activated_days=? WHERE id=?",(days,oid))
            purchaser = c.execute('SELECT referrer FROM users WHERE id=?',(r['uid'],)).fetchone()
            reward_days = json.loads(c.execute("SELECT value FROM settings WHERE key='referral_days'").fetchone()[0])
            # One qualifying reward per purchaser, even with multiple orders.
            prior = c.execute('SELECT 1 FROM rewards JOIN orders ON orders.id=rewards.order_id WHERE orders.uid=?',(r['uid'],)).fetchone()
            ref = purchaser['referrer']
            if ref and reward_days and not prior:
                refuser = c.execute('SELECT banned FROM users WHERE id=?',(ref,)).fetchone()
                if refuser and not refuser['banned']:
                    grant(c,ref,reward_days,'referral:'+str(r['uid']),'referral')
                    c.execute('INSERT INTO rewards(order_id,referrer,days) VALUES(?,?,?)',(oid,ref,reward_days))
                    enqueue(c,ref,sc('Referral reward applied.')+' '+str(reward_days)+' '+sc('days'))
            audit(c,actor,'access_activated',oid,{'beneficiary':r['beneficiary'],'days':days})
            enqueue(c,r['beneficiary'],sc('Subscription activated.')+' '+str(days)+' '+sc('days. Open My Subscription.'))
        await self.db.run(job)

    async def refund_record(self, oid: str):
        def job(c):
            r = c.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone()
            require(r,'Unknown order.')
            if r['state']=='refunded':
                return
            if r['activated_days'] and r['beneficiary']:
                c.execute('UPDATE users SET expires=MAX(?,expires-?) WHERE id=?',(now(),r['activated_days']*DAY,r['beneficiary']))
                c.execute("UPDATE campaigns SET state='paused',reason='order_refund' WHERE uid=? AND state IN ('running','scheduled')",(r['beneficiary'],))
            rw = c.execute('SELECT * FROM rewards WHERE order_id=? AND reversed=0',(oid,)).fetchone()
            if rw:
                c.execute('UPDATE users SET expires=MAX(?,expires-?) WHERE id=?',(now(),rw['days']*DAY,rw['referrer']))
                c.execute('UPDATE rewards SET reversed=1 WHERE order_id=?',(oid,))
            c.execute("UPDATE orders SET state='refunded' WHERE id=?",(oid,))
            c.execute("UPDATE payment_events SET state='refunded' WHERE charge=?",(r['charge'],))
            audit(c,0,'payment_refunded',oid)
            enqueue(c,r['uid'],sc('Payment refunded. Related access/rewards adjusted.'))
        await self.db.run(job)

    async def control(self, uid: int, cid: int, action: str, when: int = 0):
        def job(c):
            r = c.execute('SELECT * FROM campaigns WHERE id=? AND uid=?',(cid,uid)).fetchone()
            require(r,'Campaign unavailable.')
            if action=='start':
                require(r['state']=='draft','Campaign already confirmed.')
                count = c.execute("SELECT COUNT(*) FROM consent WHERE audience=? AND state='active'",(r['audience'],)).fetchone()[0]
                settings = {x['key']:json.loads(x['value']) for x in c.execute('SELECT * FROM settings')}
                user = c.execute('SELECT limits FROM users WHERE id=?',(uid,)).fetchone()
                limits = json.loads(user['limits'])
                require(0<count<=min(settings['max_recipients'],limits.get('max_recipients',settings['max_recipients'])), 'Audience empty or above campaign limit.')
                c.execute("INSERT INTO deliveries(campaign,recipient) SELECT ?,recipient FROM consent WHERE audience=? AND state='active'",(cid,r['audience']))
                c.execute("UPDATE campaigns SET state=?,next_at=? WHERE id=?",('scheduled' if when>now() else 'running',when,cid))
            elif action=='pause':
                require(r['state'] in ('running','scheduled'),'Campaign is not running.')
                c.execute("UPDATE campaigns SET state='paused',reason='user_pause' WHERE id=?",(cid,))
            elif action=='resume':
                require(r['state']=='paused','Campaign is not paused.')
                c.execute("UPDATE campaigns SET state='running',reason='' WHERE id=?",(cid,))
            elif action=='cancel':
                require(r['state'] not in ('done','cancelled'),'Campaign is already terminal.')
                c.execute("UPDATE campaigns SET state='cancelled',reason='user_cancel' WHERE id=?",(cid,))
                c.execute("UPDATE deliveries SET state='skipped',reason='cancelled' WHERE campaign=? AND state='pending'",(cid,))
            else:
                raise ValueError('Invalid campaign action.')
            audit(c,uid,'campaign_'+action,cid)
        await self.db.run(job)


class App:
    def __init__(self, db: DB, owners: set[int], bot: Bot, key: bytes, private_key):
        self.db, self.svc, self.bot = db, Service(db,owners), bot
        self.owners, self.crypt, self.private_key = owners, Fernet(key), private_key
        self.settings = copy.deepcopy(DEFAULTS)
        self.clients: dict[int,tuple[str,TelegramClient]] = {}
        self.emoji_valid: dict[str,str] = {}
        self.diagnostics: list[str] = []
        self.me = None
        self.stopping = asyncio.Event()
        self.locks: dict[int,asyncio.Lock] = {}

    def user_lock(self, uid):
        return self.locks.setdefault(uid,asyncio.Lock())

    def date(self, stamp: int):
        return datetime.fromtimestamp(stamp,ZoneInfo(self.settings['timezone'])).strftime('%d %b %Y %H:%M %Z') if stamp else '—'

    def icon(self, symbol='💎'):
        if not self.settings['custom_emoji_enabled']:
            return None
        return next((x for x in self.settings['emoji'].get(symbol,[]) if x in self.emoji_valid),None)

    def heading(self, text: str, symbol='💎'):
        eid = self.icon(symbol)
        prefix = f'<tg-emoji emoji-id="{eid}">{e(self.emoji_valid[eid])}</tg-emoji> ' if eid else ''
        return prefix+f'<b>{e(sc(text))}</b>'

    def frame(self, title: str, body: str):
        return self.heading(title)+'\n\n'+body+'\n\n'+e('powered by ᴋᴅ')

    async def send(self, uid: int, title: str, body: str = '', buttons=None, home=False):
        markup = await self.keyboard(uid) if home else buttons
        try:
            return await self.bot.send_message(uid,self.frame(title,body),parse_mode='HTML',reply_markup=markup,
                                               link_preview_options={'is_disabled':True})
        except TelegramBadRequest as ex:
            # Only decoration errors trigger a retry. Never retry an unknown send outcome.
            if 'emoji' not in str(ex).lower():
                raise
            self.settings['custom_emoji_enabled'] = False
            self.diagnostics.append('Custom emoji rejected by Telegram; decoration disabled for this process.')
            if markup:
                data = markup.model_dump(exclude_none=True)
                for rows in (data.get('inline_keyboard',[]),data.get('keyboard',[])):
                    for row in rows:
                        for btn in row:
                            if isinstance(btn,dict):
                                btn.pop('icon_custom_emoji_id',None)
                markup = type(markup).model_validate(data)
            return await self.bot.send_message(uid,self.frame(title,body),parse_mode='HTML',reply_markup=markup,
                                               link_preview_options={'is_disabled':True})

    async def buttons(self, uid: int, specs: list[tuple], nav=True):
        rows = []
        for label,action,data,*kind in specs:
            role = kind[0] if kind else 'navigation'
            args = dict(text=sc(str(label))[:64],style=self.settings['styles'][role],icon_custom_emoji_id=self.icon('✅' if role=='positive' else '💎'))
            if action=='url':
                args['url'] = data
            else:
                args['callback_data'] = await self.db.token(uid,action,data)
            rows.append([InlineKeyboardButton(**args)])
        if nav:
            rows.append([InlineKeyboardButton(text=sc(label),style='primary',callback_data=await self.db.token(uid,'nav',action))
                         for label,action in [('Back','home'),('Home','home'),('Cancel','cancel')]])
        return InlineKeyboardMarkup(inline_keyboard=rows)

    async def keyboard(self, uid):
        keys = [k for k in MENU if k!='owner' or uid in self.owners]
        values = [KeyboardButton(text=sc(self.settings['labels'][k]),style=self.settings['styles']['navigation'],
                                 icon_custom_emoji_id=self.icon()) for k in keys]
        return ReplyKeyboardMarkup(keyboard=[values[i:i+2] for i in range(0,len(values),2)],resize_keyboard=True,is_persistent=True)

    async def ask(self, uid, step, title, body, data=None):
        await self.db.state(uid,{'step':step,'data':data})
        await self.send(uid,title,body,await self.buttons(uid,[]))

    async def animate(self, uid):
        with contextlib.suppress(TelegramBadRequest,TelegramForbiddenError,TelegramRetryAfter):
            media = self.settings['working_media']
            if media:
                await self.bot.send_animation(uid,media['id'],caption='powered by ᴋᴅ')
            else:
                await self.bot.send_chat_action(uid,'typing')

    async def gate(self, uid):
        user = await self.svc.paid(uid)
        if uid in self.owners:
            return user
        require(not self.settings['maintenance'],'Maintenance is active. Support remains available.')
        require(not self.settings['emergency_stop'],'Campaign emergency stop is active.')
        missing = []
        for row in await self.db.rows('SELECT * FROM required_channels WHERE enabled=1'):
            try:
                member = await self.bot.get_chat_member(row['id'],uid)
            except (TelegramBadRequest,TelegramForbiddenError) as ex:
                raise ValueError('Membership configuration cannot be verified. Contact Support; owner must check bot permissions.') from ex
            if member.status in ('left','kicked') or (member.status=='restricted' and not member.is_member):
                missing.append(('Join required channel','url',row['link']))
        if missing:
            await self.send(uid,'Membership required',sc('Join these channels, then check again.'),
                            await self.buttons(uid,missing+[('Check Membership','check',None,'positive')]))
            raise ValueError('Membership check is incomplete.')
        return user

    async def verify_context(self, uid: int, chat_id: int):
        chat = await self.bot.get_chat(chat_id)
        require(chat.type in ('group','supergroup','channel'),'Choose a channel or group.')
        for who in (uid,self.me.id):
            member = await self.bot.get_chat_member(chat_id,who)
            require(member.status in ('administrator','creator'),'Customer and control bot must both be administrators.')
        return chat

    async def client(self, uid: int) -> TelegramClient:
        row = await self.db.one("SELECT * FROM accounts WHERE uid=? AND status='connected'",(uid,))
        require(row,'Connect your account first, or resolve the account restriction.')
        cached = self.clients.get(uid)
        if cached and cached[0]==row['revision']:
            if not cached[1].is_connected():
                await cached[1].connect()
            return cached[1]
        if cached:
            await cached[1].disconnect()
            del self.clients[uid]
        require(len(self.clients)<self.settings['max_accounts'],'Server account capacity reached; contact support.')
        data = json.loads(self.crypt.decrypt(row['secret'].encode()))
        cl = TelegramClient(StringSession(data['session']),data['api_id'],data['api_hash'],
                            flood_sleep_threshold=0,request_retries=0,connection_retries=2,
                            retry_delay=1,timeout=15,raise_last_call_error=True)
        await cl.connect()
        require(await cl.is_user_authorized(),'Authorization revoked. Reconnect.')
        require((await cl.get_me()).id==uid,'Account identity mismatch.')
        async def private_message(event):
            try:
                await self.on_private(uid,event)
            except Exception as ex:
                log_event('consent_listener_error',ex)
        cl.add_event_handler(private_message,events.NewMessage(incoming=True,func=lambda ev:ev.is_private))
        self.clients[uid] = (row['revision'],cl)
        return cl

    async def on_private(self, owner: int, event):
        text = (event.raw_text or '').strip()
        recipient = event.sender_id
        if not recipient or recipient==owner:
            return
        if text=='/stop' or text.startswith('/stop '):
            token = text.partition(' ')[2].strip()
            await self.db.execute("UPDATE consent SET state='withdrawn',peer_hash=NULL,at=? WHERE recipient=? AND audience IN (SELECT id FROM audiences WHERE uid=? AND (?='' OR token=?))",
                                  (now(),recipient,owner,token,token))
            await self.db.run(lambda c:audit(c,recipient,'consent_withdrawn',owner))
            return
        if not text.startswith('/kdconsent '):
            return
        token = text.split(maxsplit=1)[1].strip()
        audience = await self.db.one('SELECT * FROM audiences WHERE uid=? AND token=? AND enabled=1',(owner,token))
        if not audience:
            return
        peer = await event.get_input_sender()
        if not isinstance(peer,InputPeerUser):
            return
        def job(c):
            n = c.execute("UPDATE consent SET state='active',peer_hash=?,at=? WHERE audience=? AND recipient=? AND state='pending'",
                          (str(peer.access_hash),now(),audience['id'],recipient)).rowcount
            if n:
                c.execute('INSERT OR REPLACE INTO consent_proofs VALUES(?,?,?)',(audience['id'],recipient,event.id))
                audit(c,recipient,'consent_verified',audience['id'])
                enqueue(c,recipient,sc('Consent verified for:')+' '+e(audience['purpose'])+'\n'+sc('Use /unsubscribe here or /stop with the sender at any time.'))
        await self.db.run(job)

    async def import_account(self, uid, package):
        require(len(package)<12000 and package.startswith('KD1.'),'Paste only the encrypted KD1 package; never OTPs or passwords.')
        state = await self.db.state(uid)
        require(state.get('step')=='provision','Reopen Connect Account for a fresh challenge.')
        wrapped, encrypted = package[4:].split('.',1)
        key = self.private_key.decrypt(base64.urlsafe_b64decode(wrapped),padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
        data = json.loads(Fernet(key).decrypt(encrypted.encode(),ttl=1800))
        require(data['challenge']==state['data']['challenge'] and data['uid']==uid,'Wrong customer or expired challenge.')
        cl = TelegramClient(StringSession(data['session']),int(data['api_id']),data['api_hash'],flood_sleep_threshold=0,request_retries=0)
        try:
            await cl.connect()
            me = await cl.get_me()
            require(me and not me.bot and me.id==uid,'Only your control-bot identity can be connected.')
        finally:
            await cl.disconnect()
        async with self.user_lock(uid):
            old = self.clients.pop(uid,None)
            if old:
                await old[1].disconnect()
            secret = self.crypt.encrypt(json.dumps(data).encode()).decode()
            def job(c):
                count = c.execute('SELECT COUNT(*) FROM accounts WHERE uid<>?',(uid,)).fetchone()[0]
                require(count<self.settings['max_accounts'],'Account capacity reached.')
                c.execute('INSERT OR REPLACE INTO accounts VALUES(?,?,?,?,?)',(uid,secret,secrets.token_hex(8),'connected',0))
                c.execute('DELETE FROM workflows WHERE uid=?',(uid,))
                audit(c,uid,'account_connected',uid)
            await self.db.run(job)
        await self.client(uid)
        await self.send(uid,'Account connected',mention(uid,me.first_name or 'Profile')+'\n'+sc('Encrypted session stored.'))

    async def home(self, uid):
        user = await self.db.one('SELECT * FROM users WHERE id=?',(uid,))
        media = self.settings['welcome_media']
        if media:
            method = self.bot.send_photo if media['type']=='photo' else self.bot.send_animation
            with contextlib.suppress(TelegramBadRequest):
                await method(uid,media['id'],caption='powered by ᴋᴅ')
        body = (e(sc(self.settings['welcome']))+'\n\n'+mention(uid,user['name'])+'\n'+sc('Chat ID:')+f' <code>{uid}</code>\n'
                +sc('Access: ')+('OWNER' if uid in self.owners else self.date(user['expires']) if user['expires']>now() and not user['banned'] else sc('inactive'))+'\n\n'
                +sc('Owner:')+' '+mention(min(self.owners),self.settings['owner_name'])+'\n'
                +sc('Developer:')+' '+e(self.settings['developer_name'])+'\n'
                +sc('Private account messaging • explicit consent • campaign control'))
        await self.send(uid,'KD • Messaging Studio',body,home=True)

    async def nav(self, uid: int, action: str, page: int = 0):
        if action in ('home','cancel'):
            await self.db.state(uid,{})
            return await self.home(uid)
        if action in ('connect','accounts','audiences','create','campaigns','history'):
            await self.gate(uid)
        if action=='profile':
            u = await self.db.one('SELECT * FROM users WHERE id=?',(uid,))
            await self.send(uid,'Your profile',mention(uid,u['name'])+f'\n<code>{uid}</code>',
                            await self.buttons(uid,[('Delete my data','confirm',['delete_data',None],'destructive')]))
        elif action=='subscription':
            u = await self.db.one('SELECT * FROM users WHERE id=?',(uid,))
            await self.send(uid,'Subscription',sc('Expiry:')+' '+self.date(u['expires'])+'\n'+sc('Status:')+' '+sc('banned' if u['banned'] else 'active' if u['expires']>now() else 'inactive'))
        elif action in ('support','help'):
            sid = self.settings['support_id'] or min(self.owners)
            await self.send(uid,action,mention(sid,self.settings['owner_name'])+'\n'+e(sc(self.settings['help']))+'\n'+sc('For payment questions use /paysupport.'))
        elif action=='plans':
            specs=[]
            for row in await self.db.rows('SELECT * FROM plans ORDER BY id'):
                p=json.loads(row['body'])
                await self.send(uid,p['name'],e(sc(p['description']))+f"\n{p['days']} "+sc('days')+f" • {p['price']} XTR\n"+sc('Enabled:')+' '+str(p['enabled']),
                                await self.buttons(uid,[(f"Buy {p['name']}",'buy',row['id'],'positive')] if p['enabled'] and p['price']>0 else []))
        elif action=='payments':
            rows=await self.db.rows('SELECT * FROM orders WHERE uid=? ORDER BY created DESC LIMIT 10 OFFSET ?',(uid,page*10))
            for r in rows:
                specs=[('Confirm my ID','beneficiary',[r['id'],uid],'positive'),('Different beneficiary','beneficiary_other',r['id'])] if r['state']=='awaiting_beneficiary' else []
                await self.send(uid,'Order',e(r['id'])+'\n'+e(sc(r['state'])),await self.buttons(uid,specs))
            await self.pagination(uid,action,page,len(rows))
        elif action=='connect':
            public=base64.urlsafe_b64encode(self.private_key.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)).decode()
            challenge=secrets.token_urlsafe(24)
            await self.ask(uid,'provision','Secure account connection',sc('Run python main.py --authorize on your trusted local terminal. Public key:')+f'\n<code>{public}</code>\n'+sc('Challenge:')+f'\n<code>{challenge}</code>\n'+sc('Paste only the encrypted KD1 package here. Never send OTP or 2FA.'),{'challenge':challenge})
        elif action=='accounts':
            row=await self.db.one('SELECT status,next_at FROM accounts WHERE uid=?',(uid,))
            await self.send(uid,'Connected account',sc('One identity per customer.')+'\n'+(e(sc(row['status']))+'\n'+self.date(row['next_at']) if row else sc('No account connected.')),
                            await self.buttons(uid,[('Reconnect','nav','connect'),('Delete stored session','confirm',['disconnect',False],'destructive'),('Revoke Telegram session','confirm',['disconnect',True],'destructive')]))
        elif action=='audiences':
            rows=await self.db.rows('SELECT * FROM audiences WHERE uid=? ORDER BY id DESC LIMIT 10 OFFSET ?',(uid,page*10))
            for r in rows:
                link=f'https://t.me/{self.me.username}?start=c_{r["token"]}'
                await self.send(uid,r['title'],e(r['purpose'])+'\n'+sc('Consent link:')+f'\n<a href="{e(link)}">{e(sc("Join this audience"))}</a>',
                                await self.buttons(uid,[('Disable audience' if r['enabled'] else 'Enable audience','audience_toggle',r['id'])]))
            await self.send(uid,'Audience manager',sc('Create a separate audience for each specific purpose.'),await self.buttons(uid,[('Add channel / group','audience_add',None,'positive')]))
            await self.pagination(uid,action,page,len(rows))
        elif action=='create':
            await self.send(uid,'Select sending account',mention(uid,(await self.db.one('SELECT name FROM users WHERE id=?',(uid,)))['name']),
                            await self.buttons(uid,[('Use my connected account','choose_audience',None,'positive')]))
        elif action in ('campaigns','history'):
            rows=await self.db.rows('SELECT id FROM campaigns WHERE uid=? ORDER BY id DESC LIMIT 10 OFFSET ?',(uid,page*10))
            for r in rows:
                await self.campaign_card(uid,r['id'])
            await self.pagination(uid,action,page,len(rows))
        elif action=='unsubscribe':
            rows=await self.db.rows("SELECT a.* FROM consent c JOIN audiences a ON a.id=c.audience WHERE c.recipient=? AND c.state IN ('active','pending') ORDER BY a.id LIMIT 10 OFFSET ?",(uid,page*10))
            await self.send(uid,'Consent management',sc('Withdraw any audience; this does not affect payment access.'),
                            await self.buttons(uid,[(r['title']+' / '+r['purpose'][:25],'withdraw',r['id'],'destructive') for r in rows]))
            await self.pagination(uid,action,page,len(rows))
        elif action=='referrals':
            refs=await self.db.one('SELECT COUNT(*) n FROM users WHERE referrer=?',(uid,))
            rewards=await self.db.rows('SELECT days,reversed,order_id FROM rewards WHERE referrer=? ORDER BY rowid DESC LIMIT 10',(uid,))
            link=f'https://t.me/{self.me.username}?start=r_{uid}'
            await self.send(uid,'Referrals',f'<a href="{e(link)}">{sc("Your referral invitation")}</a>\n'+sc('Referrals:')+f' {refs["n"]}\n'+sc('Reward days:')+f' {self.settings["referral_days"]}\n'+e(json.dumps(rewards)))
        elif action=='owner':
            self.svc.owner(uid)
            specs=[('Dashboard','admin',['stats',0]),('Users','admin',['users',0]),('Find user','admin',['search',0]),
                   ('Payments and activations','admin',['orders',0]),('Plans','admin',['plans',0]),('Business settings','admin',['settings',0]),
                   ('Menu labels','edit_setting','labels'),('Button styles','edit_setting','styles'),('Custom emoji mapping','edit_setting','emoji'),
                   ('Flag mapping','edit_setting','flags'),('Emoji diagnostics / preview','diagnose',None),
                   ('Welcome media','media_edit','welcome_media'),('Working animation','media_edit','working_media'),
                   ('Force join','admin',['channels',0]),('Audit history','admin',['audit',0]),('Campaign operations','admin',['campaigns',0]),
                   ('Encrypted backup','backup',None),('Emergency stop','confirm',['emergency',None],'destructive')]
            await self.send(uid,'KD owner panel',sc('Every control is authorized by numeric owner ID.'),await self.buttons(uid,specs))
        else:
            raise ValueError('Unknown navigation action.')

    async def pagination(self, uid, action, page, count):
        specs=[]
        if page>0: specs.append(('Previous','page',[action,page-1]))
        if count==10: specs.append(('Next','page',[action,page+1]))
        await self.send(uid,'Navigation',sc('Page')+f' {page+1}',await self.buttons(uid,specs))

    async def campaign_card(self, uid, cid):
        r=await self.svc.owned('campaigns',cid,uid)
        counts=await self.db.rows('SELECT state,COUNT(*) n FROM deliveries WHERE campaign=? GROUP BY state',(cid,))
        specs=[('Refresh progress','campaign_card',cid)]
        if r['state']=='draft': specs += [('Preview','preview',cid),('Confirm and start','campaign_action',[cid,'start'],'positive'),('Schedule','schedule',cid)]
        if r['state'] in ('running','scheduled'): specs.append(('Pause','campaign_action',[cid,'pause']))
        if r['state']=='paused': specs.append(('Resume','campaign_action',[cid,'resume'],'positive'))
        if r['state'] not in ('done','cancelled'): specs.append(('Cancel campaign','confirm',['campaign_cancel',cid],'destructive'))
        text=sc('State:')+' '+e(sc(r['state']))+'\n'+e(sc(r['reason']))+'\n'+ '\n'.join(e(sc(x['state']))+f': {x["n"]}' for x in counts)
        message=await self.send(uid,f'Campaign {cid}',text,await self.buttons(uid,specs))
        if message and r['state'] in ('running','scheduled','paused'):
            await self.db.execute('INSERT OR REPLACE INTO monitors VALUES(?,?,?,?)',(cid,uid,message.message_id,now()))

    async def preview(self, uid, cid):
        r=await self.svc.owned('campaigns',cid,uid)
        counts=await self.db.rows('SELECT state,COUNT(*) n FROM consent WHERE audience=? GROUP BY state',(r['audience'],))
        # Exact plain-text body sent separately; no small caps, entities or branding added.
        await self.send(uid,'Exact outgoing text follows',sc('The next message is the unmodified campaign preview.'))
        await self.bot.send_message(uid,r['body'],parse_mode=None,link_preview_options={'is_disabled':True})
        await self.send(uid,'Audience review','\n'.join(e(sc(x['state']))+f': {x["n"]}' for x in counts)+'\n'+sc('Pending and withdrawn recipients are excluded.'),
                        await self.buttons(uid,[('Confirm and start','campaign_action',[cid,'start'],'positive'),('Schedule','schedule',cid)]))

    async def dispatch(self, uid, action, data):
        # All callbacks are single-use, customer-bound and short-lived in SQLite.
        if action=='nav': return await self.nav(uid,data)
        if action=='page': return await self.nav(uid,data[0],integer(data[1],0,100000))
        if action=='confirm':
            return await self.send(uid,'Confirm action',sc('This changes stored data or service state.'),
                                   await self.buttons(uid,[('Confirm','confirmed',data,'destructive')]))
        if action=='confirmed': return await self.destructive(uid,*data)
        if action=='check':
            await self.gate(uid)
            return await self.send(uid,'Membership verified',sc('You can continue.'))
        if action=='buy':
            u=await self.db.one('SELECT banned FROM users WHERE id=?',(uid,))
            require(not u['banned'] and not self.settings['maintenance'],'Checkout unavailable; contact support.')
            oid=await self.svc.order(uid,data)
            order=await self.db.one('SELECT * FROM orders WHERE id=?',(oid,))
            p=json.loads(order['snapshot'])
            await self.bot.send_invoice(uid,title=p['name'][:32],description=(p['description']+' • powered by KD')[:255],payload=oid,
                                        currency='XTR',prices=[LabeledPrice(label=p['name'],amount=p['price'])],provider_token='')
            return
        if action=='beneficiary':
            await self.svc.beneficiary(uid,data[0],data[1])
            return await self.send(uid,'Awaiting activation',sc('Owner will separately select access duration.'))
        if action=='beneficiary_other':
            return await self.ask(uid,'beneficiary','Beneficiary ID',sc('Enter the numeric ID. The owner will review this assignment.'),data)
        if action=='withdraw':
            await self.db.execute("UPDATE consent SET state='withdrawn',peer_hash=NULL,at=? WHERE audience=? AND recipient=?",(now(),data,uid))
            await self.db.run(lambda c:audit(c,uid,'consent_withdrawn',data))
            return await self.send(uid,'Unsubscribed',sc('Further queued sends will skip you.'))
        if action=='consent':
            a=await self.db.one('SELECT * FROM audiences WHERE id=? AND enabled=1',(data,))
            require(a,'Audience unavailable.')
            await self.db.execute("INSERT INTO consent(audience,recipient,state,at) VALUES(?,?,'pending',?) ON CONFLICT(audience,recipient) DO UPDATE SET state='pending',peer_hash=NULL,at=excluded.at",(data,uid,now()))
            await self.db.run(lambda c:audit(c,uid,'consent_requested',data,{'purpose':a['purpose']}))
            sender=await self.db.one('SELECT name FROM users WHERE id=?',(a['uid'],))
            return await self.send(uid,'Verify with sender',sc('Open this profile and send the command below:')+'\n'+mention(a['uid'],sender['name'])+f'\n<code>/kdconsent {a["token"]}</code>\n'+sc('You may withdraw with /unsubscribe or /stop.'))
        if action in ('audience_add','audience_toggle','choose_audience','audience_select','preview','campaign_action','campaign_card','schedule'):
            await self.gate(uid)
            if action=='audience_add':
                return await self.ask(uid,'audience_chat','Channel / group',sc('Enter the numeric chat ID. You and this bot must be admins.'))
            if action=='audience_toggle':
                a=await self.svc.owned('audiences',data,uid)
                await self.db.execute('UPDATE audiences SET enabled=? WHERE id=?',(1-a['enabled'],data))
                return await self.nav(uid,'audiences')
            if action=='choose_audience':
                await self.client(uid)
                rows=await self.db.rows('SELECT * FROM audiences WHERE uid=? AND enabled=1 ORDER BY id DESC LIMIT 50',(uid,))
                return await self.send(uid,'Select audience',sc('Each audience has a specific consent purpose.'),await self.buttons(uid,[(r['title']+' / '+r['purpose'][:25],'audience_select',r['id']) for r in rows]))
            if action=='audience_select':
                a=await self.svc.owned('audiences',data,uid)
                await self.verify_context(uid,a['chat'])
                state=await self.db.state(uid)
                prefill=state.get('prefill')
                if prefill: return await self.create_campaign(uid,data,prefill)
                return await self.ask(uid,'campaign_text','Normal text message',sc('Send the exact message, up to 3500 UTF-16 units. It will not be restyled.'),data)
            if action=='preview': return await self.preview(uid,data)
            if action=='campaign_card': return await self.campaign_card(uid,data)
            if action=='schedule':
                await self.svc.owned('campaigns',data,uid)
                return await self.ask(uid,'schedule','UTC schedule',sc('Enter ISO-8601 with timezone, e.g. 2026-12-01T12:00:00+00:00.'),data)
            if action=='campaign_action':
                await self.svc.control(uid,data[0],data[1])
                return await self.campaign_card(uid,data[0])
        if action in ('admin','edit_setting','edit_plan','media_edit','diagnose','backup','review','activate','user_view','user_op','required_toggle','required_add'):
            self.svc.owner(uid)
            return await self.admin_action(uid,action,data)
        raise ValueError('Action unavailable.')

    async def create_campaign(self, uid, audience, body):
        require(body and len(body.encode('utf-16-le'))//2<=3500,'Message must contain 1–3500 UTF-16 units.')
        await self.svc.owned('audiences',audience,uid)
        def job(c):
            active=c.execute("SELECT COUNT(*) FROM campaigns WHERE uid=? AND state NOT IN ('done','cancelled')",(uid,)).fetchone()[0]
            require(active<25,'Finish or cancel existing campaigns first (25 open maximum).')
            cid=c.execute('INSERT INTO campaigns(uid,audience,body,created) VALUES(?,?,?,?)',(uid,audience,body,now())).lastrowid
            audit(c,uid,'campaign_created',cid)
            return cid
        cid=await self.db.run(job)
        await self.db.state(uid,{})
        await self.preview(uid,cid)

    async def admin_action(self, uid, action, data):
        if action=='admin':
            section,page=data
            integer(page,0,100000)
            if section=='stats':
                totals=await self.db.one('SELECT COUNT(*) total,SUM(expires>? AND banned=0) active FROM users',(now(),))
                jobs=await self.db.rows('SELECT state,COUNT(*) n FROM campaigns GROUP BY state')
                await self.send(uid,'Dashboard',e(json.dumps(totals))+'\n'+e(json.dumps(jobs))+'\n'+sc('Connected clients:')+f' {len(self.clients)}')
            elif section=='users':
                rows=await self.db.rows('SELECT id,name FROM users ORDER BY id LIMIT 10 OFFSET ?',(page*10,))
                await self.send(uid,'Users',sc('Select a profile.'),await self.buttons(uid,[(r['name']+' • '+str(r['id']),'user_view',r['id']) for r in rows]))
                await self.admin_pagination(uid,section,page,len(rows))
            elif section=='search':
                await self.ask(uid,'user_search','Search users',sc('Enter numeric ID or profile-name text.'))
            elif section=='orders':
                rows=await self.db.rows("SELECT * FROM orders WHERE charge IS NOT NULL ORDER BY created DESC LIMIT 10 OFFSET ?",(page*10,))
                for r in rows:
                    p=json.loads(r['snapshot'])
                    text=(f'<code>{e(r["id"])}</code>\n'+sc('Purchaser:')+f' {r["uid"]}\n'+sc('Beneficiary:')+f' {r["beneficiary"]}\n'
                          +e(sc(r['state']))+f' • {p["price"]} XTR • {p["days"]} '+sc('days')+'\n'+sc('Verified charge:')+f' <code>{e(r["charge"])}</code>')
                    specs=[]
                    if r['state']=='pending_review': specs.append(('Approve payment only','review',r['id'],'positive'))
                    if r['state']=='awaiting_activation': specs.append(('Set days and activate','activate',r['id'],'positive'))
                    if r['state'] not in ('refunded','refunding','refund_retry'): specs.append(('Reject / refund','confirm',['refund',r['id']],'destructive'))
                    await self.send(uid,'Payment review',text,await self.buttons(uid,specs))
                await self.admin_pagination(uid,section,page,len(rows))
            elif section=='plans':
                rows=await self.db.rows('SELECT * FROM plans ORDER BY id')
                await self.send(uid,'Plan editor',sc('Prices are integer Stars. Zero-price plans cannot be purchased.'),await self.buttons(uid,[(json.loads(r['body'])['name'],'edit_plan',r['id']) for r in rows]))
            elif section=='settings':
                keys=[k for k in self.settings if k not in ('welcome_media','working_media','emoji','flags','labels','styles')]
                part=keys[page*10:page*10+10]
                await self.send(uid,'Business settings',sc('Select a field. Changes are validated and audited.'),await self.buttons(uid,[(k,'edit_setting',k) for k in part]))
                await self.admin_pagination(uid,section,page,len(part))
            elif section=='channels':
                rows=await self.db.rows('SELECT * FROM required_channels ORDER BY id LIMIT 10 OFFSET ?',(page*10,))
                specs=[(str(r['id'])+(' enabled' if r['enabled'] else ' disabled'),'required_toggle',r['id']) for r in rows]
                specs.append(('Add / edit channel','required_add',None,'positive'))
                await self.send(uid,'Force join',sc('Tap a channel to enable/disable. Editor also supports deletion.'),await self.buttons(uid,specs))
                await self.admin_pagination(uid,section,page,len(rows))
            elif section=='audit':
                rows=await self.db.rows('SELECT actor,action,target,at,detail FROM audit ORDER BY id DESC LIMIT 10 OFFSET ?',(page*10,))
                await self.send(uid,'Audit history',e('\n'.join(json.dumps(r) for r in rows)[:3200]))
                await self.admin_pagination(uid,section,page,len(rows))
            elif section=='campaigns':
                rows=await self.db.rows('SELECT id,uid,state,reason FROM campaigns ORDER BY id DESC LIMIT 10 OFFSET ?',(page*10,))
                await self.send(uid,'Campaign operations','\n'.join(e(json.dumps(r)) for r in rows),
                                await self.buttons(uid,[(f'Stop campaign {r["id"]}','confirm',['owner_campaign_stop',r['id']],'destructive') for r in rows if r['state'] not in ('done','cancelled')]))
                await self.admin_pagination(uid,section,page,len(rows))
            else: raise ValueError('Unknown owner section.')
        elif action=='edit_setting':
            require(data in DEFAULTS,'Unknown setting.')
            val=self.settings[data]
            sample=val
            if isinstance(val,dict) and data in ('emoji','flags'): sample=dict(list(val.items())[:2])
            if isinstance(val,list): sample=val[:3]
            await self.ask(uid,'setting','Edit '+data,sc('Send a JSON value. Mapping updates merge by key; arrays replace the pool. Current/sample:')+'\n<pre>'+e(json.dumps(sample,ensure_ascii=False))+'</pre>',data)
        elif action=='edit_plan':
            p=await self.db.one('SELECT body FROM plans WHERE id=?',(data,))
            require(p,'Plan not found.')
            await self.ask(uid,'plan','Edit plan',sc('Send the complete JSON object:')+'\n<pre>'+e(p['body'])+'</pre>',data)
        elif action=='media_edit':
            await self.ask(uid,'media','Upload media',sc('Send animation (or photo for welcome), maximum 10 MB, or - to remove.'),data)
        elif action=='diagnose':
            await self.validate_emojis()
            text='\n'.join(self.diagnostics[:15]) or 'No invalid mappings detected.'
            text+='\nValidated IDs: '+str(len(self.emoji_valid))+'\nEntitlement must be checked on your real bot.'
            await self.send(uid,'Emoji diagnostics',e(text))
            await self.send(uid,'Custom emoji preview',self.heading('Welcome • KD','👑')+'\n'+self.heading('Payments','💰')+'\n'+self.heading('Confirmed','✅'),await self.buttons(uid,[('Preview button','nav','home','positive')]))
        elif action=='backup':
            path=await self.backup()
            await self.db.run(lambda c:audit(c,uid,'backup_created',Path(path).name))
            await self.send(uid,'Encrypted backup',sc('Saved on the protected server disk:')+'\n<code>'+e(path)+'</code>\n'+sc('Restore instructions are in the main.py docstring.'))
        elif action=='review':
            await self.svc.review(uid,data)
            await self.send(uid,'Payment approved',sc('Access remains inactive until beneficiary confirmation and a separate grant.'))
        elif action=='activate':
            r=await self.db.one('SELECT * FROM orders WHERE id=?',(data,))
            require(r and r['state']=='awaiting_activation','Order not ready.')
            await self.ask(uid,'activate','Access duration',sc('Purchaser / beneficiary:')+f' {r["uid"]} / {r["beneficiary"]}\n'+sc('Enter exact days, 1–3650. This is separate from payment approval.'),data)
        elif action=='user_view':
            r=await self.db.one('SELECT * FROM users WHERE id=?',(data,))
            require(r,'User not found.')
            hist=await self.db.rows('SELECT days,source,at FROM grants WHERE uid=? ORDER BY at DESC LIMIT 10',(data,))
            await self.send(uid,'User details',mention(data,r['name'])+f'\n{data}\n'+sc('Expires:')+' '+self.date(r['expires'])+'\n'+sc('Banned:')+' '+str(r['banned'])+'\n'+e(json.dumps(hist)),
                            await self.buttons(uid,[('Grant / extend days','user_op',[data,'grant'],'positive'),('Revoke access','confirm',['revoke',data],'destructive'),
                                                   ('Ban' if not r['banned'] else 'Unban','confirm',['ban',[data,not r['banned']]],'destructive')]))
        elif action=='user_op':
            require(data[1]=='grant','Invalid user operation.')
            await self.ask(uid,'grant','Grant / extend subscription',sc('Enter days for user:')+f' {data[0]}',data[0])
        elif action=='required_toggle':
            await self.db.run(lambda c:(c.execute('UPDATE required_channels SET enabled=1-enabled WHERE id=?',(data,)),audit(c,uid,'required_channel_toggled',data)))
            await self.admin_action(uid,'admin',['channels',0])
        elif action=='required_add':
            await self.ask(uid,'required','Force-join channel',sc('Send JSON. Bot must be admin. Set delete:true to remove.')+'\n<pre>'+e(json.dumps({'id':-1001234567890,'link':'https://t.me/+REPLACE','enabled':True,'delete':False}))+'</pre>')

    async def admin_pagination(self, uid, section, page, count):
        specs=[]
        if page: specs.append(('Previous','admin',[section,page-1]))
        if count==10: specs.append(('Next','admin',[section,page+1]))
        specs.append(('Owner panel','nav','owner'))
        await self.send(uid,'Navigation',sc('Page')+f' {page+1}',await self.buttons(uid,specs))

    async def destructive(self, uid, action, data):
        if action in ('refund','revoke','ban','emergency','owner_campaign_stop'):
            self.svc.owner(uid)
        if action=='disconnect':
            async with self.user_lock(uid):
                if data:
                    cl=await self.client(uid)
                    require(await cl.log_out(),'Telegram session revocation failed.')
                old=self.clients.pop(uid,None)
                if old: await old[1].disconnect()
                def job(c):
                    c.execute('DELETE FROM accounts WHERE uid=?',(uid,))
                    c.execute("UPDATE campaigns SET state='paused',reason='account_disconnected' WHERE uid=? AND state IN ('running','scheduled')",(uid,))
                    audit(c,uid,'session_revoked' if data else 'stored_session_deleted',uid)
                await self.db.run(job)
        elif action=='campaign_cancel':
            await self.svc.control(uid,data,'cancel')
        elif action=='refund':
            def job(c):
                r=c.execute('SELECT * FROM orders WHERE id=?',(data,)).fetchone()
                require(r and r['charge'] and r['state'] not in ('refunded','refunding','refund_retry'),'Refund unavailable or already queued.')
                c.execute("UPDATE orders SET state='refund_retry' WHERE id=?",(data,))
                audit(c,uid,'refund_requested',data)
            await self.db.run(job)
        elif action in ('revoke','ban'):
            target=data if action=='revoke' else data[0]
            require(target not in self.owners,'Owner recovery access cannot be removed through this panel.')
            def job(c):
                if action=='revoke': c.execute('UPDATE users SET expires=0 WHERE id=?',(target,))
                else: c.execute('UPDATE users SET banned=? WHERE id=?',(int(data[1]),target))
                if action=='revoke' or data[1]:
                    c.execute("UPDATE campaigns SET state='paused',reason='access_revoked' WHERE uid=? AND state IN ('running','scheduled')",(target,))
                audit(c,uid,action,target)
            async with self.user_lock(target): await self.db.run(job)
        elif action=='emergency':
            def job(c):
                c.execute("UPDATE settings SET value='true' WHERE key='emergency_stop'")
                c.execute("UPDATE campaigns SET state='paused',reason='emergency_stop' WHERE state IN ('running','scheduled')")
                audit(c,uid,'emergency_stop','all')
            await self.db.run(job)
            self.settings=await self.db.settings()
        elif action=='owner_campaign_stop':
            r=await self.db.one('SELECT uid FROM campaigns WHERE id=?',(data,))
            require(r,'Campaign unavailable.')
            await self.svc.control(r['uid'],data,'cancel')
            await self.db.run(lambda c:audit(c,uid,'owner_campaign_cancelled',data))
        elif action=='delete_data':
            async with self.user_lock(uid):
                old=self.clients.pop(uid,None)
                if old: await old[1].disconnect()
                def job(c):
                    c.execute('DELETE FROM accounts WHERE uid=?',(uid,))
                    c.execute("UPDATE campaigns SET body='',state='cancelled',reason='data_deleted' WHERE uid=?",(uid,))
                    c.execute('DELETE FROM deliveries WHERE campaign IN (SELECT id FROM campaigns WHERE uid=?)',(uid,))
                    c.execute("UPDATE consent SET state='withdrawn',peer_hash=NULL WHERE recipient=? OR audience IN (SELECT id FROM audiences WHERE uid=?)",(uid,uid))
                    c.execute('UPDATE audiences SET enabled=0 WHERE uid=?',(uid,))
                    c.execute('DELETE FROM workflows WHERE uid=?',(uid,))
                    c.execute('DELETE FROM callbacks WHERE uid=?',(uid,))
                    c.execute('DELETE FROM outbox WHERE uid=?',(uid,))
                    c.execute("UPDATE users SET name='Deleted profile' WHERE id=?",(uid,))
                    audit(c,uid,'data_deleted',uid)
                await self.db.run(job)
            await self.send(uid,'Data deleted',sc('Financial/audit records retained. Terminate Telegram authorization in Settings > Devices.'))
            return
        else: raise ValueError('Unknown destructive action.')
        await self.send(uid,'Action recorded',sc('Changes have been saved.'))

    async def edit_setting(self, uid, key, value):
        self.svc.owner(uid)
        require(key in DEFAULTS and key not in ('welcome_media','working_media'),'Unknown editable setting.')
        previous=self.settings[key]
        if isinstance(previous,dict):
            require(isinstance(value,dict),'Expected JSON object.')
            value={**previous,**value}
        if key in ('maintenance','emergency_stop','custom_emoji_enabled'):
            require(type(value) is bool,'Expected true/false.')
        elif key in ('max_recipients','daily_limit'): integer(value,1,100000)
        elif key=='send_interval': integer(value,1,3600)
        elif key=='max_accounts': integer(value,1,500)
        elif key=='retention_days': integer(value,7,3650)
        elif key=='referral_days': integer(value,0,365)
        elif key=='support_id': integer(value,0)
        elif key=='timezone':
            require(isinstance(value,str),'Expected timezone string.')
            ZoneInfo(value)
        elif key in ('owner_name','developer_name','help','welcome'):
            require(isinstance(value,str) and 0<len(value)<=1000,'Expected 1–1000 characters.')
        elif key=='labels':
            require(set(value)==set(MENU),'Use the existing menu action keys.')
            require(all(isinstance(v,str) and 1<=len(v)<=40 for v in value.values()),'Labels must be 1–40 characters.')
            require(len(set(sc(v) for v in value.values()))==len(value),'Menu labels must be unique.')
        elif key=='styles':
            require(set(value)=={'positive','destructive','navigation'} and all(v in ('primary','success','danger') for v in value.values()),'Invalid style map.')
        elif key in ('emoji','flags'):
            require(len(value)<=200,'At most 200 mappings.')
            for symbol,ids in value.items():
                require(isinstance(symbol,str) and 1<=len(symbol)<=12,'Invalid emoji key.')
                ids=ids if key=='emoji' else [ids]
                require(isinstance(ids,list) and len(ids)<=10 and all(isinstance(x,str) and re.fullmatch(r'[0-9]{5,22}',x) for x in ids),'Invalid custom emoji ID list.')
        elif key in ('primary_emojis','premium_pool'):
            require(isinstance(value,list) and len(value)<=300 and all(isinstance(x,str) and re.fullmatch(r'[0-9]{5,22}',x) for x in value),'Invalid emoji pool.')
            value=list(dict.fromkeys(value))
        def job(c):
            c.execute('UPDATE settings SET value=? WHERE key=?',(json.dumps(value),key))
            audit(c,uid,'setting_updated',key,{'before_hash':hashlib.sha256(json.dumps(previous).encode()).hexdigest(),'after_hash':hashlib.sha256(json.dumps(value).encode()).hexdigest()})
            if key in ('maintenance','emergency_stop') and value:
                c.execute("UPDATE campaigns SET state='paused',reason=? WHERE state IN ('running','scheduled')",(key,))
        await self.db.run(job)
        self.settings=await self.db.settings()
        if key in ('emoji','flags','custom_emoji_enabled','primary_emojis','premium_pool'): await self.validate_emojis()

    async def input(self, msg: Message):
        uid=msg.from_user.id
        text=msg.text or ''
        state=await self.db.state(uid)
        step,data=state.get('step'),state.get('data')
        require(step,'Use a menu button or /start.')
        if step in ('provision','audience_chat','audience_purpose','campaign_text','schedule'):
            await self.gate(uid)
        if step in ('setting','plan','media','activate','grant','required','user_search'):
            self.svc.owner(uid)
        if step=='provision':
            await self.animate(uid)
            return await self.import_account(uid,text.strip())
        if step=='audience_chat':
            chat=await self.verify_context(uid,int(text))
            return await self.ask(uid,'audience_purpose','Audience purpose',sc('Describe precisely what recipients agree to receive (5–200 characters). Purpose cannot later be changed.'),{'chat':chat.id,'title':chat.title or 'Community'})
        if step=='audience_purpose':
            require(5<=len(text)<=200,'Purpose must be 5–200 characters.')
            count=await self.db.one('SELECT COUNT(*) n FROM audiences WHERE uid=?',(uid,))
            require(count['n']<50,'This installation supports up to 50 purpose-specific audiences per customer.')
            await self.db.execute('INSERT INTO audiences(uid,chat,title,purpose,token) VALUES(?,?,?,?,?)',(uid,data['chat'],data['title'],text,secrets.token_urlsafe(16)))
        elif step=='campaign_text':
            return await self.create_campaign(uid,data,text)
        elif step=='schedule':
            date=datetime.fromisoformat(text)
            require(date.tzinfo is not None,'Timezone offset is required.')
            when=int(date.timestamp())
            require(now()<when<=now()+365*DAY,'Schedule must be within the next 365 days.')
            await self.svc.control(uid,data,'start',when)
        elif step=='beneficiary':
            await self.svc.beneficiary(uid,data,integer(int(text)))
        elif step=='activate':
            await self.svc.activate(uid,data,integer(int(text),1,3650))
        elif step=='grant':
            days=integer(int(text),1,3650)
            # Workflow nonce makes repeated message processing unable to double-extend.
            key='manual:'+str(uid)+':'+str(msg.chat.id)+':'+str(msg.message_id)
            await self.db.run(lambda c:(grant(c,data,days,key,'owner'),audit(c,uid,'manual_grant',data,{'days':days}),enqueue(c,data,sc('Owner granted access days:')+f' {days}')))
        elif step=='user_search':
            rows=await self.db.rows('SELECT id,name FROM users WHERE id=? OR instr(lower(name),lower(?))>0 LIMIT 30',(int(text) if text.isdigit() else 0,text[:128]))
            await self.send(uid,'Search results',sc('Select a profile.'),await self.buttons(uid,[(r['name']+' • '+str(r['id']),'user_view',r['id']) for r in rows]))
        elif step=='setting':
            await self.edit_setting(uid,data,json.loads(text))
        elif step=='plan':
            p=json.loads(text)
            require(isinstance(p,dict) and set(p)=={'name','price','days','description','enabled','max_recipients','daily_limit'},'Use exactly the supplied plan fields.')
            for k,lo,hi in [('price',0,100000),('days',1,3650),('max_recipients',1,100000),('daily_limit',1,100000)]: integer(p[k],lo,hi)
            require(type(p['enabled']) is bool and isinstance(p['name'],str) and 1<=len(p['name'])<=32 and isinstance(p['description'],str) and 1<=len(p['description'])<=200,'Invalid plan fields.')
            require(not p['enabled'] or p['price']>0,'Set a positive Stars price before enabling checkout.')
            await self.db.run(lambda c:(c.execute('UPDATE plans SET body=? WHERE id=?',(json.dumps(p),data)),audit(c,uid,'plan_updated',data,p)))
        elif step=='media':
            media=None
            if text.strip()!='-':
                item=msg.animation or (msg.photo[-1] if msg.photo and data=='welcome_media' else None)
                require(item and (item.file_size or 0)<=10*1024*1024,'Send an animation or allowed welcome photo under 10 MB.')
                media={'type':'animation' if msg.animation else 'photo','id':item.file_id}
            await self.db.run(lambda c:(c.execute('UPDATE settings SET value=? WHERE key=?',(json.dumps(media),data)),audit(c,uid,'media_updated',data)))
            self.settings=await self.db.settings()
        elif step=='required':
            obj=json.loads(text)
            require(isinstance(obj,dict) and set(obj)=={'id','link','enabled','delete'},'Use exactly the supplied fields.')
            require(type(obj['id']) is int and obj['id']<0 and type(obj['enabled']) is bool and type(obj['delete']) is bool,'Invalid channel fields.')
            if obj['delete']:
                await self.db.run(lambda c:(c.execute('DELETE FROM required_channels WHERE id=?',(obj['id'],)),audit(c,uid,'required_channel_removed',obj['id'])))
            else:
                require(isinstance(obj['link'],str) and re.fullmatch(r'https://t\.me/[A-Za-z0-9_+/-]{3,200}',obj['link']),'Use a valid Telegram join link.')
                member=await self.bot.get_chat_member(obj['id'],self.me.id)
                require(member.status in ('administrator','creator'),'Bot must be a channel administrator.')
                await self.db.run(lambda c:(c.execute('INSERT OR REPLACE INTO required_channels VALUES(?,?,?)',(obj['id'],obj['link'],int(obj['enabled']))),audit(c,uid,'required_channel_updated',obj['id'])))
        else: raise ValueError('Workflow expired. Reopen its menu.')
        await self.db.state(uid,{})
        await self.send(uid,'Saved',sc('Your action was recorded.'),await self.buttons(uid,[]))

    async def validate_emojis(self):
        mapping=self.settings['emoji']
        ids=list(dict.fromkeys([x for xs in mapping.values() for x in xs]+list(self.settings['flags'].values())+self.settings['primary_emojis']+self.settings['premium_pool']))
        valid={}
        issues=[]
        for i in range(0,len(ids),200):
            try:
                stickers=await self.bot.get_custom_emoji_stickers(ids[i:i+200])
            except (TelegramBadRequest,TelegramRetryAfter) as ex:
                issues.append('Emoji validation unavailable: '+type(ex).__name__)
                continue
            for s in stickers:
                if s.custom_emoji_id and s.emoji:
                    valid[s.custom_emoji_id]=s.emoji
        for symbol,eid in self.settings['flags'].items():
            if valid.get(eid)!=symbol:
                issues.append('Disabled mismatched/unavailable flag: '+symbol+' / '+eid)
        for eid in ids:
            if eid not in valid: issues.append('Unavailable custom emoji ID: '+eid)
        self.emoji_valid=valid
        self.diagnostics=issues

    async def backup(self):
        directory=Path(os.getenv('KD_BACKUP_DIR','./kd-backups')).resolve()
        directory.mkdir(mode=0o700,parents=True,exist_ok=True)
        require(directory.is_dir(),'Backup directory unavailable.')
        os.chmod(directory,0o700)
        path=directory/(str(now())+'-'+secrets.token_hex(4)+'.kdbak')
        # sqlite backup API gives a transactionally consistent WAL-aware snapshot.
        async with self.db.lock:
            def work():
                source=sqlite3.connect(self.db.path)
                target=sqlite3.connect(':memory:')
                try:
                    source.backup(target)
                    payload=self.crypt.encrypt(target.serialize())
                    with open(path,'xb') as f:
                        os.chmod(path,0o600)
                        f.write(payload)
                        f.flush()
                        os.fsync(f.fileno())
                finally:
                    source.close(); target.close()
            await asyncio.to_thread(work)
        return str(path)

    async def pause_account(self, uid, reason):
        def job(c):
            c.execute("UPDATE accounts SET status='restricted' WHERE uid=?",(uid,))
            c.execute("UPDATE campaigns SET state='paused',reason=? WHERE uid=? AND state IN ('running','scheduled')",(reason,uid))
            audit(c,uid,'account_paused',uid,{'reason':reason})
            enqueue(c,uid,sc('Account paused:')+' '+e(reason)+'. '+sc('Resolve the restriction before reconnecting.'))
        await self.db.run(job)

    async def delivery_result(self, cid, recipient, state, reason='', mid=None, retry_at=0):
        await self.db.execute('UPDATE deliveries SET state=?,reason=?,message_id=?,next_at=?,at=? WHERE campaign=? AND recipient=?',
                              (state,reason,mid,retry_at,now(),cid,recipient))

    async def send_one(self, job: dict):
        uid,cid=job['uid'],job['id']
        async with self.user_lock(uid):
            try:
                await self.gate(uid)
                require(not self.settings['emergency_stop'],'Emergency stop active.')
                a=await self.svc.owned('audiences',job['audience'],uid)
                require(a['enabled'],'Audience is disabled.')
                await self.verify_context(uid,a['chat'])
                cl=await self.client(uid)
            except (ValueError,TelegramBadRequest,TelegramForbiddenError) as ex:
                await self.db.execute("UPDATE campaigns SET state='paused',reason=? WHERE id=? AND state IN ('running','scheduled')",(type(ex).__name__+'_eligibility',cid))
                return
            except errors.FloodWaitError as ex:
                await self.db.execute('UPDATE accounts SET next_at=? WHERE uid=?',(now()+ex.seconds+1,uid))
                return
            except errors.RPCError as ex:
                await self.pause_account(uid,type(ex).__name__)
                return
            # Transaction rechecks all mutable local eligibility immediately before claiming.
            def claim(c):
                camp=c.execute('SELECT * FROM campaigns WHERE id=?',(cid,)).fetchone()
                account=c.execute('SELECT * FROM accounts WHERE uid=?',(uid,)).fetchone()
                user=c.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
                settings={r['key']:json.loads(r['value']) for r in c.execute('SELECT * FROM settings')}
                if not camp or camp['state'] not in ('running','scheduled') or camp['next_at']>now(): return None
                if not account or account['status']!='connected' or account['next_at']>now(): return None
                if settings['emergency_stop'] or (uid not in self.owners and (settings['maintenance'] or user['banned'] or user['expires']<=now())):
                    c.execute("UPDATE campaigns SET state='paused',reason='access_check' WHERE id=?",(cid,))
                    return None
                eligible=c.execute('SELECT enabled FROM audiences WHERE id=?',(camp['audience'],)).fetchone()
                if not eligible or not eligible['enabled']: return None
                limit=min(settings['daily_limit'],json.loads(user['limits']).get('daily_limit',settings['daily_limit']))
                day=now()//DAY*DAY
                sent=c.execute("SELECT COUNT(*) FROM deliveries d JOIN campaigns j ON j.id=d.campaign WHERE j.uid=? AND d.state IN ('accepted','uncertain','sending') AND d.at>=?",(uid,day)).fetchone()[0]
                if sent>=limit:
                    c.execute('UPDATE campaigns SET next_at=? WHERE id=?',(day+DAY,cid))
                    return None
                r=c.execute("SELECT d.*,co.state consent_state,co.peer_hash FROM deliveries d LEFT JOIN consent co ON co.audience=? AND co.recipient=d.recipient WHERE d.campaign=? AND d.state='pending' AND d.next_at<=? ORDER BY d.recipient LIMIT 1",(camp['audience'],cid,now())).fetchone()
                if not r:
                    pending=c.execute("SELECT 1 FROM deliveries WHERE campaign=? AND state IN ('pending','sending') LIMIT 1",(cid,)).fetchone()
                    if not pending:
                        c.execute("UPDATE campaigns SET state='done' WHERE id=?",(cid,))
                        summary={x['state']:x['n'] for x in c.execute('SELECT state,COUNT(*) n FROM deliveries WHERE campaign=? GROUP BY state',(cid,))}
                        enqueue(c,uid,sc('Campaign completed:')+f' {cid}\n'+e(json.dumps(summary)))
                    return None
                if r['consent_state']!='active' or not r['peer_hash']:
                    c.execute("UPDATE deliveries SET state='skipped',reason='consent_withdrawn',at=? WHERE campaign=? AND recipient=?",(now(),cid,r['recipient']))
                    return None
                c.execute("UPDATE deliveries SET state='sending',tries=tries+1,at=? WHERE campaign=? AND recipient=?",(now(),cid,r['recipient']))
                c.execute("UPDATE campaigns SET state='running' WHERE id=?",(cid,))
                c.execute('UPDATE accounts SET next_at=? WHERE uid=?',(now()+settings['send_interval'],uid))
                return dict(r)
            recipient=await self.db.run(claim)
            if not recipient: return
            rid=recipient['recipient']
            try:
                proof=await self.db.one('SELECT message_id FROM consent_proofs WHERE audience=? AND recipient=?',(job['audience'],rid))
                # A /stop sent while the process was offline must still win. Query
                # only this consenting user's private conversation, never members.
                if not proof:
                    await self.delivery_result(cid,rid,'skipped','consent_reverification_required')
                    return
                history=await asyncio.wait_for(cl.get_messages(InputPeerUser(rid,int(recipient['peer_hash'])),limit=101,min_id=proof['message_id']),timeout=20)
                stopped=any(not m.out and (m.raw_text or '').strip() in ('/stop','/stop '+a['token']) for m in history)
                if stopped or len(history)>100:
                    await self.db.execute("UPDATE consent SET state=?,peer_hash=NULL,at=? WHERE audience=? AND recipient=?",('withdrawn' if stopped else 'pending',now(),job['audience'],rid))
                    await self.delivery_result(cid,rid,'skipped','unsubscribe' if stopped else 'consent_reverification_required')
                    return
                current=await self.db.one('SELECT co.state consent_state,j.state job_state,u.expires,u.banned FROM consent co JOIN campaigns j ON j.audience=co.audience JOIN users u ON u.id=j.uid WHERE j.id=? AND co.recipient=?',(cid,rid))
                no_access=current and uid not in self.owners and (current['expires']<=now() or current['banned'] or self.settings['maintenance'])
                if not current or current['consent_state']!='active' or current['job_state']!='running' or no_access or self.settings['emergency_stop']:
                    await self.delivery_result(cid,rid,'skipped','eligibility_changed')
                    return
                result=await asyncio.wait_for(cl.send_message(InputPeerUser(rid,int(recipient['peer_hash'])),job['body'],parse_mode=None,link_preview=False),timeout=45)
            except errors.FloodWaitError as ex:
                deadline=now()+ex.seconds+1
                # No send accepted by server; safe to retry after the explicit deadline.
                await self.delivery_result(cid,rid,'pending','FloodWait',retry_at=deadline)
                await self.db.execute('UPDATE accounts SET next_at=MAX(next_at,?) WHERE uid=?',(deadline,uid))
            except (errors.PeerFloodError,errors.AuthKeyUnregisteredError,errors.SessionRevokedError,errors.UserDeactivatedBanError) as ex:
                await self.delivery_result(cid,rid,'failed',type(ex).__name__)
                await self.pause_account(uid,type(ex).__name__)
            except (errors.UserPrivacyRestrictedError,errors.UserIsBlockedError,errors.InputUserDeactivatedError,
                    errors.ChatWriteForbiddenError,errors.PeerIdInvalidError) as ex:
                await self.delivery_result(cid,rid,'failed',type(ex).__name__)
            except (asyncio.TimeoutError,OSError,ConnectionError) as ex:
                await self.delivery_result(cid,rid,'uncertain',type(ex).__name__)
            except errors.RPCError as ex:
                # Only explicit server transient errors are bounded retries; other errors are terminal.
                if getattr(ex,'code',0)>=500 and recipient['tries']<2:
                    await self.delivery_result(cid,rid,'pending',type(ex).__name__,retry_at=now()+30*(recipient['tries']+1))
                else:
                    await self.delivery_result(cid,rid,'failed',type(ex).__name__)
            except asyncio.CancelledError:
                await asyncio.shield(self.delivery_result(cid,rid,'uncertain','shutdown'))
                raise
            except Exception as ex:
                await self.delivery_result(cid,rid,'uncertain',type(ex).__name__)
                log_event('unexpected_send_outcome',ex)
            else:
                await self.delivery_result(cid,rid,'accepted',mid=result.id)

    async def refund_tick(self):
        extra=await self.db.one("SELECT * FROM payment_events WHERE state='refund_pending' ORDER BY created LIMIT 1")
        if extra:
            try:
                require(extra['currency']=='XTR','Non-Stars charge requires manual review.')
                await self.bot.refund_star_payment(extra['uid'],extra['charge'])
            except TelegramBadRequest as ex:
                if 'CHARGE_ALREADY_REFUNDED' not in str(ex).upper():
                    await self.db.execute("UPDATE payment_events SET state='manual_review' WHERE charge=?",(extra['charge'],))
                    return
            except ValueError:
                await self.db.execute("UPDATE payment_events SET state='manual_review' WHERE charge=?",(extra['charge'],))
                return
            await self.db.execute("UPDATE payment_events SET state='refunded' WHERE charge=?",(extra['charge'],))
            await self.db.run(lambda c:enqueue(c,extra['uid'],sc('The additional/unmatched payment has been refunded.')))
            return
        r=await self.db.one("SELECT * FROM orders WHERE state='refund_retry' ORDER BY created LIMIT 1")
        if not r: return
        await self.db.execute("UPDATE orders SET state='refunding' WHERE id=?",(r['id'],))
        try:
            await self.bot.refund_star_payment(r['uid'],r['charge'])
        except TelegramBadRequest as ex:
            # Telegram may have completed the refund before our previous process died.
            if 'CHARGE_ALREADY_REFUNDED' not in str(ex).upper():
                await self.db.execute("UPDATE orders SET state='refund_failed' WHERE id=?",(r['id'],))
                for owner in self.owners:
                    await self.db.run(lambda c,o=owner:enqueue(c,o,sc('Refund requires manual review:')+' '+e(r['id'])))
                return
        except Exception:
            await self.db.execute("UPDATE orders SET state='refund_retry' WHERE id=?",(r['id'],))
            raise
        await self.svc.refund_record(r['id'])

    async def notification_tick(self):
        row=await self.db.one("SELECT * FROM outbox WHERE state='pending' AND next_at<=? ORDER BY id LIMIT 1",(now(),))
        if not row: return
        try:
            await self.send(row['uid'],'KD notification',row['body'])
        except TelegramRetryAfter as ex:
            await self.db.execute('UPDATE outbox SET next_at=? WHERE id=?',(now()+ex.retry_after+1,row['id']))
        except TelegramForbiddenError:
            await self.db.execute("UPDATE outbox SET state='failed' WHERE id=?",(row['id'],))
        except Exception:
            await self.db.execute("UPDATE outbox SET tries=tries+1,next_at=?,state=? WHERE id=?",(now()+60,'failed' if row['tries']>=2 else 'pending',row['id']))
        else:
            await self.db.execute("UPDATE outbox SET state='sent' WHERE id=?",(row['id'],))

    async def progress_tick(self):
        row=await self.db.one('SELECT m.*,j.state,j.reason FROM monitors m JOIN campaigns j ON j.id=m.campaign WHERE m.updated<? ORDER BY m.updated LIMIT 1',(now()-15,))
        if not row: return
        counts=await self.db.rows('SELECT state,COUNT(*) n FROM deliveries WHERE campaign=? GROUP BY state',(row['campaign'],))
        body=sc('State:')+' '+e(sc(row['state']))+'\n'+e(sc(row['reason']))+'\n'+'\n'.join(e(sc(x['state']))+f': {x["n"]}' for x in counts)
        try:
            # Omit reply_markup to preserve the current bound action buttons.
            await self.bot.edit_message_text(self.frame(f'Campaign {row["campaign"]}',body),chat_id=row['uid'],message_id=row['message_id'],parse_mode='HTML')
        except TelegramRetryAfter as ex:
            await self.db.execute('UPDATE monitors SET updated=? WHERE campaign=?',(now()+ex.retry_after,row['campaign']))
            return
        except TelegramBadRequest as ex:
            if 'message is not modified' not in str(ex).lower():
                await self.db.execute('DELETE FROM monitors WHERE campaign=?',(row['campaign'],))
                return
        except TelegramForbiddenError:
            await self.db.execute('DELETE FROM monitors WHERE campaign=?',(row['campaign'],))
            return
        await self.db.execute('UPDATE monitors SET updated=? WHERE campaign=?',(now(),row['campaign']))
        if row['state'] in ('done','cancelled'):
            await self.db.execute('DELETE FROM monitors WHERE campaign=?',(row['campaign'],))

    async def cleanup(self):
        cutoff=now()-self.settings['retention_days']*DAY
        def job(c):
            c.execute('DELETE FROM callbacks WHERE expires<?',(now(),))
            c.execute('DELETE FROM workflows WHERE expires<?',(now(),))
            c.execute("DELETE FROM outbox WHERE created<? AND state!='pending'",(cutoff,))
            c.execute("DELETE FROM deliveries WHERE campaign IN (SELECT id FROM campaigns WHERE state IN ('done','cancelled') AND created<?)",(cutoff,))
            c.execute("UPDATE campaigns SET body='' WHERE state IN ('done','cancelled') AND created<?",(cutoff,))
        await self.db.run(job)

    async def worker(self):
        tick=0
        while not self.stopping.is_set():
            try:
                self.settings=await self.db.settings()
                await self.notification_tick()
                await self.progress_tick()
                if tick%30==0:
                    await self.refund_tick()
                    # Keep authorized connections listening for opt-in and /stop events.
                    for row in await self.db.rows("SELECT a.uid FROM accounts a JOIN users u ON u.id=a.uid WHERE a.status='connected' AND u.banned=0 AND (u.expires>? OR u.id IN ("+','.join('?' for _ in self.owners)+'))',(now(),*sorted(self.owners))):
                        try:
                            async with self.user_lock(row['uid']):
                                await self.client(row['uid'])
                        except errors.FloodWaitError as ex:
                            await self.db.execute('UPDATE accounts SET next_at=? WHERE uid=?',(now()+ex.seconds+1,row['uid']))
                        except Exception as ex:
                            log_event('client_connect_failed',ex)
                if tick%600==0: await self.cleanup()
                jobs=await self.db.rows("SELECT j.* FROM campaigns j LEFT JOIN accounts a ON a.uid=j.uid WHERE j.state IN ('running','scheduled') AND j.next_at<=? AND (a.next_at IS NULL OR a.next_at<=?) ORDER BY j.report_at,j.id LIMIT 20",(now(),now()))
                for job in jobs:
                    if self.stopping.is_set(): break
                    await self.send_one(job)
                    await self.db.execute('UPDATE campaigns SET report_at=? WHERE id=?',(now(),job['id']))
            except asyncio.CancelledError:
                raise
            except Exception as ex:
                log_event('worker_cycle_error',ex)
            tick+=1
            try: await asyncio.wait_for(self.stopping.wait(),timeout=1)
            except asyncio.TimeoutError: pass

    async def message(self, msg: Message):
        if msg.chat.type!='private' or not msg.from_user or msg.from_user.is_bot: return
        uid=msg.from_user.id
        raw=msg.text or ''
        parts=raw.split(maxsplit=1)
        cmd=parts[0].split('@')[0].lower() if parts else ''
        arg=parts[1] if len(parts)>1 else ''
        ref=int(arg[2:]) if cmd=='/start' and re.fullmatch(r'r_[0-9]+',arg) else None
        await self.db.register(uid,msg.from_user.full_name,ref)
        try:
            if msg.successful_payment:
                p=msg.successful_payment
                await self.svc.received(uid,p.invoice_payload,p.telegram_payment_charge_id,p.currency,p.total_amount)
                return
            if msg.refunded_payment:
                p=msg.refunded_payment
                row=await self.db.one('SELECT id FROM orders WHERE charge=? AND uid=?',(p.telegram_payment_charge_id,uid))
                if row: await self.svc.refund_record(row['id'])
                await self.db.execute("UPDATE payment_events SET state='refunded' WHERE charge=?",(p.telegram_payment_charge_id,))
                return
            if cmd=='/start' and arg.startswith('c_'):
                a=await self.db.one('SELECT * FROM audiences WHERE token=? AND enabled=1',(arg[2:],))
                require(a,'Consent invitation is invalid or disabled.')
                sender=await self.db.one('SELECT name FROM users WHERE id=?',(a['uid'],))
                await self.send(uid,'Permission to message you',mention(a['uid'],sender['name'])+'\n'+e(a['title'])+'\n'+sc('Purpose:')+' '+e(a['purpose'])+'\n'+sc('You agree to receive direct messages from this account for this purpose. You can withdraw at any time.'),
                                await self.buttons(uid,[('I consent','consent',a['id'],'positive'),('Decline','nav','home','destructive')]))
                return
            if cmd in ('/start','/home','/cancel'): return await self.nav(uid,'home')
            if cmd in ('/help','/support','/paysupport','/unsubscribe','/profile'):
                return await self.nav(uid,{'/paysupport':'support'}.get(cmd,cmd[1:]))
            if cmd=='/delete_data': return await self.dispatch(uid,'confirm',['delete_data',None])
            if cmd=='/approve':
                self.svc.owner(uid)
                target,days=map(int,arg.split())
                integer(target); integer(days,1,3650)
                return await self.ask(uid,'grant','Confirm manual grant',sc('Reply with the number of days to grant:')+f' {days}\n'+sc('Target:')+f' {target}',target)
            if cmd=='/revoke':
                self.svc.owner(uid)
                return await self.dispatch(uid,'confirm',['revoke',integer(int(arg))])
            if cmd in ('/stats','/users','/owner'):
                self.svc.owner(uid)
                return await self.nav(uid,'owner') if cmd=='/owner' else await self.admin_action(uid,'admin',[cmd[1:],0])
            if cmd=='/massdm':
                await self.gate(uid)
                require(arg,'Usage: /massdm your normal text message')
                await self.db.state(uid,{'prefill':arg})
                return await self.nav(uid,'create')
            actions={sc(v):k for k,v in self.settings['labels'].items()}
            if raw in actions:
                await self.db.state(uid,{})
                return await self.nav(uid,actions[raw])
            await self.input(msg)
        except (ValueError,KeyError,TypeError,OverflowError) as ex:
            safe=str(ex) if isinstance(ex,ValueError) and not isinstance(ex,json.JSONDecodeError) else 'Invalid input. Follow the form example and retry.'
            # Never echo a decoding exception containing credential material.
            if (await self.db.state(uid)).get('step')=='provision': safe='Account import failed. Check identity, challenge, encrypted package and local authorization.'
            await self.send(uid,'Please check',e(safe[:600]),await self.buttons(uid,[]))
        except Exception as ex:
            log_event('handler_error',ex)
            with contextlib.suppress(Exception):
                await self.send(uid,'Action unavailable',sc('The request could not be completed. Contact Support; no sensitive error details are shown.'))

    async def callback(self, query: CallbackQuery):
        if not query.message or query.message.chat.type!='private': return
        uid=query.from_user.id
        with contextlib.suppress(TelegramBadRequest): await query.answer()
        try:
            action,data=await self.db.consume(uid,query.data or '')
            await self.dispatch(uid,action,data)
        except ValueError as ex:
            await self.send(uid,'Please check',e(str(ex)[:600]),await self.buttons(uid,[]))
        except Exception as ex:
            log_event('callback_error',ex)
            with contextlib.suppress(Exception): await self.send(uid,'Action unavailable',sc('Reopen the menu or contact support.'))

    async def precheckout(self, query: PreCheckoutQuery):
        try:
            def reserve(c):
                r=c.execute('SELECT o.*,u.banned FROM orders o JOIN users u ON u.id=o.uid WHERE o.id=? AND o.uid=?',(query.invoice_payload,query.from_user.id)).fetchone()
                require(r and r['state']=='awaiting_payment' and r['created']>now()-3600 and not r['banned'],'Order unavailable or expired.')
                require(query.currency=='XTR' and query.total_amount==json.loads(r['snapshot'])['price'],'Amount mismatch.')
                require(not json.loads(c.execute("SELECT value FROM settings WHERE key='maintenance'").fetchone()[0]),'Checkout is temporarily unavailable.')
                previous=c.execute('SELECT * FROM checkout_reservations WHERE order_id=?',(r['id'],)).fetchone()
                require(not previous or previous['query_id']==query.id or previous['expires']<=now(),'Checkout already in progress.')
                c.execute('INSERT OR REPLACE INTO checkout_reservations VALUES(?,?,?)',(r['id'],query.id,now()+600))
            await self.db.run(reserve)
            await query.answer(ok=True)
        except Exception:
            await query.answer(ok=False,error_message='Order expired or unavailable. Open Buy Subscription again or contact support.')


def private_material():
    key=os.environ.get('SESSION_KEY','').encode()
    require(key,'Set SESSION_KEY using python main.py --keygen.')
    Fernet(key)
    encoded=os.environ.get('PROVISION_PRIVATE_KEY','')
    require(encoded,'Set PROVISION_PRIVATE_KEY using python main.py --keygen.')
    private=serialization.load_der_private_key(base64.urlsafe_b64decode(encoded),password=None)
    require(isinstance(private,rsa.RSAPrivateKey) and private.key_size>=3072,'Use a 3072-bit or stronger RSA provisioning key.')
    return key,private


async def authorize_local():
    require(sys.stdin.isatty(),'Authorization requires an interactive trusted terminal.')
    public=serialization.load_der_public_key(base64.urlsafe_b64decode(input('Control-bot public key: ').strip()))
    require(isinstance(public,rsa.RSAPublicKey) and public.key_size>=3072,'Invalid public key.')
    challenge=input('Control-bot challenge: ').strip()
    require(re.fullmatch(r'[A-Za-z0-9_-]{20,64}',challenge),'Invalid challenge.')
    api_id=int(input('Your API_ID: ').strip())
    api_hash=getpass.getpass('Your API_HASH (hidden): ').strip()
    phone=getpass.getpass('Your phone number (hidden): ').strip()
    cl=TelegramClient(StringSession(),api_id,api_hash,flood_sleep_threshold=0,request_retries=0)
    try:
        await cl.connect()
        sent=await cl.send_code_request(phone)
        code=getpass.getpass('Telegram login code (local only): ').strip()
        try: await cl.sign_in(phone=phone,code=code,phone_code_hash=sent.phone_code_hash)
        except errors.SessionPasswordNeededError:
            await cl.sign_in(password=getpass.getpass('Two-factor password (local only): '))
        me=await cl.get_me()
        require(me and not me.bot,'A personal account is required.')
        data=dict(uid=me.id,api_id=api_id,api_hash=api_hash,session=cl.session.save(),challenge=challenge)
        key=Fernet.generate_key()
        encrypted=Fernet(key).encrypt(json.dumps(data).encode()).decode()
        wrapped=public.encrypt(key,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
        print('\nPaste this encrypted package into the authentic control bot within 30 minutes:\nKD1.'+base64.urlsafe_b64encode(wrapped).decode()+'.'+encrypted)
        print('If you do not import it, terminate this authorization in Telegram Settings > Devices.')
    finally:
        await cl.disconnect()


def keygen():
    private=rsa.generate_private_key(public_exponent=65537,key_size=3072)
    private_der=private.private_bytes(serialization.Encoding.DER,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
    print("export SESSION_KEY='"+Fernet.generate_key().decode()+"'")
    print("export PROVISION_PRIVATE_KEY='"+base64.urlsafe_b64encode(private_der).decode()+"'")
    print('# Keep these keys private; losing SESSION_KEY makes stored sessions/backups unrecoverable.')


def acquire_lock(path: str):
    p=Path(path).resolve()
    p.parent.mkdir(parents=True,mode=0o700,exist_ok=True)
    lock=open(str(p)+'.lock','a+b')
    os.chmod(str(p)+'.lock',0o600)
    try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        raise ValueError('Another bot/restore process is using this database. Stop it first.')
    return lock


def restore(path: str, backup: str):
    key,_=private_material()
    lock=acquire_lock(path)
    try:
        raw=Fernet(key).decrypt(Path(backup).read_bytes())
        require(raw.startswith(b'SQLite format 3\x00'),'Invalid backup.')
        memory=sqlite3.connect(':memory:')
        try:
            memory.deserialize(raw)
            require(memory.execute('PRAGMA integrity_check').fetchone()[0]=='ok','Backup integrity check failed.')
            require(memory.execute('PRAGMA user_version').fetchone()[0]==1,'Unsupported backup schema.')
            require(memory.execute("SELECT COUNT(*) FROM sqlite_master WHERE name IN ('users','accounts','orders')").fetchone()[0]==3,'Missing backup tables.')
        finally: memory.close()
        target=Path(path).resolve()
        if target.exists():
            existing=sqlite3.connect(target)
            try: existing.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            finally: existing.close()
            previous=target.with_name(target.name+'.pre-restore-'+str(now()))
            shutil.copyfile(target,previous)
            os.chmod(previous,0o600)
        for suffix in ('-wal','-shm'):
            with contextlib.suppress(FileNotFoundError): Path(str(target)+suffix).unlink()
        fd,tmp=tempfile.mkstemp(dir=target.parent,prefix='.kd-restore-')
        try:
            with os.fdopen(fd,'wb') as f:
                f.write(raw); f.flush(); os.fsync(f.fileno())
            os.replace(tmp,target)
            os.chmod(target,0o600)
        finally:
            with contextlib.suppress(FileNotFoundError): os.unlink(tmp)
        print('Backup restored. Keep the service stopped until configuration and key checks are complete.')
    finally: lock.close()


async def serve():
    # EDIT THESE FOUR VALUES DIRECTLY. No environment lookup is used for them.
    token = '8920648917:AAHTyWdxgvg3wkgjJ5RMcDJYGF0RT8rdoms'
    owners = {1630422629}
    owner_name = 'T10 メ KĐ~[𝖒𝖒]'
    developer_name = '@KD1948'
    require(token and token != 'PASTE_YOUR_BOT_TOKEN_HERE'
            and owners and all(type(x) is int and x > 0 for x in owners),
            'Edit token and owners at the beginning of serve() before starting the bot.')
    require(isinstance(owner_name, str) and owner_name.strip()
            and isinstance(developer_name, str) and developer_name.strip(),
            'Set non-empty owner_name and developer_name in serve().')
    key,private=private_material()
    path=os.getenv('KD_DB','./kd.sqlite3')
    lock=acquire_lock(path)
    db=DB(path)
    bot=Bot(token)
    app=App(db,owners,bot,key,private)
    task=None
    try:
        await db.initialize()
        # Apply source-configured names even when an existing database is reused.
        await db.run(lambda c: c.executemany(
            'INSERT INTO settings(key,value) VALUES(?,?) '
            'ON CONFLICT(key) DO UPDATE SET value=excluded.value',
            [('owner_name', json.dumps(owner_name)),
             ('developer_name', json.dumps(developer_name))],
        ).rowcount)
        await db.recover()
        app.settings=await db.settings()
        app.me=await bot.get_me()
        await app.validate_emojis()
        dp=Dispatcher()
        # Per-user serialization keeps workflows consistent while pre-checkout answers
        # remain independent of slower account connections and administrator tasks.
        ui_locks: dict[int,asyncio.Lock] = {}
        async def message_handler(message: Message):
            if message.from_user:
                async with ui_locks.setdefault(message.from_user.id,asyncio.Lock()):
                    await app.message(message)
        async def callback_handler(callback_query: CallbackQuery):
            async with ui_locks.setdefault(callback_query.from_user.id,asyncio.Lock()):
                await app.callback(callback_query)
        dp.message.register(message_handler)
        dp.callback_query.register(callback_handler)
        dp.pre_checkout_query.register(app.precheckout)
        task=asyncio.create_task(app.worker(),name='kd-persistent-worker')
        log_event('bot_started')
        await dp.start_polling(bot,allowed_updates=['message','callback_query','pre_checkout_query'],handle_as_tasks=True,
                               tasks_concurrency_limit=100,close_bot_session=False)
    finally:
        app.stopping.set()
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError): await task
        for _,cl in list(app.clients.values()):
            with contextlib.suppress(Exception): await cl.disconnect()
        await bot.session.close()
        lock.close()


async def self_test():
    """Integration checks of real persistence/services with fake Telegram boundaries."""
    import unittest

    class BaseSender:
        async def get_messages(self,*args,**kwargs): return []

    class FakeBot:
        def __init__(self): self.messages=[]
        async def get_chat(self, cid):
            from types import SimpleNamespace
            return SimpleNamespace(id=cid,type='supergroup',title='Test community')
        async def get_chat_member(self,cid,uid):
            from types import SimpleNamespace
            return SimpleNamespace(status='administrator')
        async def send_message(self,*args,**kwargs): self.messages.append((args,kwargs))

    class Checks(unittest.IsolatedAsyncioTestCase):
        async def asyncSetUp(self):
            from types import SimpleNamespace
            self.tmp=tempfile.TemporaryDirectory()
            self.db=DB(str(Path(self.tmp.name)/'test.sqlite3'))
            await self.db.initialize()
            for uid in (1,2,3,4): await self.db.register(uid,f'Person {uid}')
            self.s=Service(self.db,{1})
            self.bot=FakeBot()
            self.app=App(self.db,{1},self.bot,Fernet.generate_key(),None)
            self.app.me=SimpleNamespace(id=99,username='test_bot')
            self.app.settings=await self.db.settings()
            await self.db.run(lambda c:grant(c,2,30,'initial','owner'))
            await self.db.execute('INSERT INTO audiences(uid,chat,title,purpose,token) VALUES(?,?,?,?,?)',(2,-100,'Test','Product releases','audience-token'))
            await self.db.execute("INSERT INTO consent VALUES(1,3,'active','123',?)",(now(),))
            await self.db.execute('INSERT INTO consent_proofs VALUES(1,3,10)')
            await self.db.execute("INSERT INTO campaigns(uid,audience,body,created) VALUES(2,1,'Exact Text @Example https://example.com',?)",(now(),))
            await self.db.execute("INSERT INTO accounts VALUES(2,'unused','revision','connected',0)")
        async def asyncTearDown(self): self.tmp.cleanup()

        async def order_ready(self):
            p=json.loads((await self.db.one('SELECT body FROM plans WHERE id=1'))['body'])
            p.update(price=50,enabled=True)
            await self.db.execute('UPDATE plans SET body=? WHERE id=1',(json.dumps(p),))
            oid=await self.s.order(2,1)
            await self.s.received(2,oid,'charge-'+oid,'XTR',50)
            return oid

        async def test_owner_and_tenant_isolation(self):
            with self.assertRaises(ValueError): self.s.owner(2)
            with self.assertRaises(ValueError): await self.s.owned('campaigns',1,3)
            with self.assertRaises(ValueError): await self.s.control(3,1,'start')
            with self.assertRaises(ValueError): await self.s.paid(3)

        async def test_renewal_and_idempotent_grant(self):
            before=(await self.db.one('SELECT expires FROM users WHERE id=2'))['expires']
            first=await self.db.run(lambda c:grant(c,2,2,'unique','owner'))
            second=await self.db.run(lambda c:grant(c,2,2,'unique','owner'))
            self.assertTrue(first); self.assertFalse(second)
            self.assertEqual((await self.db.one('SELECT expires FROM users WHERE id=2'))['expires'],before+2*DAY)
            await self.db.execute('UPDATE users SET expires=? WHERE id=2',(now()-1,))
            with self.assertRaises(ValueError): await self.s.paid(2)
            await self.db.run(lambda c:grant(c,2,1,'expired-renewal','owner'))
            self.assertAlmostEqual((await self.db.one('SELECT expires FROM users WHERE id=2'))['expires'],now()+DAY,delta=2)

        async def test_payment_activation_separation_and_refund(self):
            before=(await self.db.one('SELECT expires FROM users WHERE id=2'))['expires']
            oid=await self.order_ready()
            self.assertEqual((await self.db.one('SELECT expires FROM users WHERE id=2'))['expires'],before)
            with self.assertRaises(ValueError): await self.s.activate(1,oid,30)
            await self.s.review(1,oid)
            self.assertEqual((await self.db.one('SELECT expires FROM users WHERE id=2'))['expires'],before)
            await self.s.beneficiary(2,oid,2)
            await self.s.activate(1,oid,30)
            with self.assertRaises(ValueError): await self.s.activate(1,oid,30)
            await self.s.received(2,oid,'charge-'+oid,'XTR',50)
            self.assertEqual((await self.db.one('SELECT expires FROM users WHERE id=2'))['expires'],before+30*DAY)
            await self.s.refund_record(oid); await self.s.refund_record(oid)
            self.assertEqual((await self.db.one('SELECT expires FROM users WHERE id=2'))['expires'],before)

        async def test_additional_charge_recorded_without_second_access(self):
            oid=await self.order_ready()
            await self.s.received(2,oid,'different-actual-charge','XTR',50)
            event=await self.db.one('SELECT state FROM payment_events WHERE charge=?',('different-actual-charge',))
            self.assertEqual(event['state'],'refund_pending')
            self.assertEqual((await self.db.one('SELECT charge FROM orders WHERE id=?',(oid,)))['charge'],'charge-'+oid)
            await self.s.received(2,oid,'different-actual-charge','XTR',50)
            self.assertEqual((await self.db.one('SELECT COUNT(*) n FROM payment_events'))['n'],2)

        async def test_checkout_reservation_blocks_parallel_charges(self):
            from types import SimpleNamespace
            oid=await self.order_ready()
            await self.db.execute("UPDATE orders SET state='awaiting_payment',charge=NULL WHERE id=?",(oid,))
            results=[]
            class Query:
                invoice_payload=oid
                from_user=SimpleNamespace(id=2)
                currency='XTR'
                total_amount=50
                def __init__(self,key): self.id=key
                async def answer(self,**kwargs): results.append(kwargs['ok'])
            await self.app.precheckout(Query('first'))
            await self.app.precheckout(Query('second'))
            self.assertEqual(results,[True,False])

        async def test_referral_once_and_reversal(self):
            await self.db.execute('UPDATE users SET referrer=4 WHERE id=2')
            await self.db.execute("UPDATE settings SET value='3' WHERE key='referral_days'")
            for _ in range(2):
                oid=await self.order_ready()
                await self.s.review(1,oid); await self.s.beneficiary(2,oid,2); await self.s.activate(1,oid,30)
            rewards=await self.db.rows('SELECT * FROM rewards')
            self.assertEqual(len(rewards),1)
            before=(await self.db.one('SELECT expires FROM users WHERE id=4'))['expires']
            await self.s.refund_record(rewards[0]['order_id'])
            self.assertLess((await self.db.one('SELECT expires FROM users WHERE id=4'))['expires'],before)
            self.assertEqual((await self.db.one('SELECT reversed FROM rewards'))['reversed'],1)

        async def test_callback_ownership_expiry_and_replay(self):
            token=await self.db.token(2,'nav','home')
            with self.assertRaises(ValueError): await self.db.consume(3,token)
            self.assertEqual(await self.db.consume(2,token),['nav','home'])
            with self.assertRaises(ValueError): await self.db.consume(2,token)
            token=await self.db.token(2,'nav','home')
            await self.db.execute('UPDATE callbacks SET expires=0 WHERE token=?',(token,))
            with self.assertRaises(ValueError): await self.db.consume(2,token)
            with self.assertRaises(ValueError): await self.db.consume(2,'malformed')

        async def test_campaign_controls_and_restart(self):
            await self.s.control(2,1,'start')
            with self.assertRaises(ValueError): await self.s.control(2,1,'start')
            await self.s.control(2,1,'pause'); await self.s.control(2,1,'resume')
            await self.db.execute("UPDATE deliveries SET state='sending' WHERE campaign=1")
            await self.db.recover()
            self.assertEqual((await self.db.one('SELECT state FROM deliveries'))['state'],'uncertain')
            await self.s.control(2,1,'cancel')
            with self.assertRaises(ValueError): await self.s.control(2,1,'resume')

        async def test_consent_withdrawal_prevents_send(self):
            await self.s.control(2,1,'start')
            await self.db.execute("UPDATE consent SET state='withdrawn' WHERE audience=1")
            class NeverSend(BaseSender):
                async def send_message(self,*a,**k): raise AssertionError('Consent withdrawn')
            async def client(uid): return NeverSend()
            self.app.client=client
            await self.app.send_one(await self.db.one('SELECT * FROM campaigns WHERE id=1'))
            self.assertEqual((await self.db.one('SELECT state FROM deliveries'))['state'],'skipped')

        async def test_floodwait_is_persistent_account_wide(self):
            await self.s.control(2,1,'start')
            class Limited(BaseSender):
                async def send_message(self,*a,**k): raise errors.FloodWaitError(request=None,capture=90)
            async def client(uid): return Limited()
            self.app.client=client
            await self.app.send_one(await self.db.one('SELECT * FROM campaigns WHERE id=1'))
            row=await self.db.one('SELECT * FROM deliveries')
            self.assertEqual(row['state'],'pending')
            self.assertGreaterEqual(row['next_at'],now()+89)
            self.assertEqual((await self.db.one('SELECT next_at FROM accounts'))['next_at'],row['next_at'])
            await self.db.recover()
            self.assertEqual((await self.db.one('SELECT next_at FROM deliveries'))['next_at'],row['next_at'])

        async def test_text_preserved_and_success(self):
            from types import SimpleNamespace
            captured=[]
            class Sender(BaseSender):
                async def send_message(self,*a,**kw):
                    captured.append((a,kw)); return SimpleNamespace(id=123)
            async def client(uid): return Sender()
            self.app.client=client
            await self.s.control(2,1,'start')
            await self.app.send_one(await self.db.one('SELECT * FROM campaigns WHERE id=1'))
            self.assertEqual(captured[0][0][1],'Exact Text @Example https://example.com')
            self.assertIsNone(captured[0][1]['parse_mode'])
            self.assertFalse(captured[0][1]['link_preview'])
            self.assertEqual((await self.db.one('SELECT state FROM deliveries'))['state'],'accepted')

        async def test_timeout_not_replayed(self):
            class Sender(BaseSender):
                async def send_message(self,*a,**kw): raise asyncio.TimeoutError()
            async def client(uid): return Sender()
            self.app.client=client
            await self.s.control(2,1,'start')
            await self.app.send_one(await self.db.one('SELECT * FROM campaigns WHERE id=1'))
            self.assertEqual((await self.db.one('SELECT state FROM deliveries'))['state'],'uncertain')
            await self.db.recover()
            self.assertEqual((await self.db.one('SELECT state FROM deliveries'))['state'],'uncertain')

        async def test_html_and_button_fields(self):
            self.assertEqual(sc('Welcome'),'ᴡᴇʟᴄᴏᴍᴇ')
            self.assertIn('https://Example.com/AbC',sc('Visit https://Example.com/AbC'))
            self.assertIn('/unsubscribe',sc('Use /unsubscribe'))
            self.assertEqual(mention(3,'<Bad & Name>'),'<a href="tg://user?id=3">&lt;Bad &amp; Name&gt;</a>')
            buttons=await self.app.buttons(2,[('Confirm','nav','home','positive')])
            self.assertEqual(buttons.inline_keyboard[0][0].style,'success')
            self.assertNotIn('tg-emoji',buttons.inline_keyboard[0][0].text)
            self.assertIn('powered by ᴋᴅ',self.app.frame('Title',e('<tg-emoji>')))

        async def test_offline_unsubscribe_prevents_send(self):
            from types import SimpleNamespace
            class Sender(BaseSender):
                async def get_messages(self,*args,**kwargs):
                    return [SimpleNamespace(out=False,raw_text='/stop')]
                async def send_message(self,*args,**kwargs):
                    raise AssertionError('Offline unsubscribe must prevent sending')
            async def client(uid): return Sender()
            self.app.client=client
            await self.s.control(2,1,'start')
            await self.app.send_one(await self.db.one('SELECT * FROM campaigns WHERE id=1'))
            self.assertEqual((await self.db.one('SELECT state FROM deliveries'))['state'],'skipped')
            self.assertEqual((await self.db.one('SELECT state FROM consent'))['state'],'withdrawn')

        async def test_encryption_and_settings_validation(self):
            token=self.app.crypt.encrypt(b'secret-session')
            self.assertNotIn(b'secret-session',token)
            self.assertEqual(self.app.crypt.decrypt(token),b'secret-session')
            with self.assertRaises(ValueError): await self.app.edit_setting(2,'send_interval',10)
            with self.assertRaises(ValueError): await self.app.edit_setting(1,'styles',{'navigation':'orange'})
            with self.assertRaises(ValueError): await self.app.edit_setting(1,'labels',{'home':'Support'})
            await self.app.edit_setting(1,'send_interval',10)
            self.assertEqual((await self.db.settings())['send_interval'],10)

    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    # unittest owns its event loops, so run the suite in a separate synchronous thread.
    result=await asyncio.to_thread(unittest.TextTestRunner(verbosity=2).run,suite)
    require(result.wasSuccessful(),'Self-tests failed.')


def main():
    os.umask(0o077)
    # Avoid dependency logs leaking requests, entity data or authentication material.
    logging.basicConfig(level=logging.CRITICAL)
    parser=argparse.ArgumentParser(description='KD single-file messaging studio')
    modes=parser.add_mutually_exclusive_group()
    modes.add_argument('--keygen',action='store_true')
    modes.add_argument('--authorize',action='store_true')
    modes.add_argument('--self-test',action='store_true')
    modes.add_argument('--restore',metavar='ENCRYPTED_BACKUP')
    args=parser.parse_args()
    try:
        if args.keygen: keygen()
        elif args.authorize: asyncio.run(authorize_local())
        elif args.self_test: asyncio.run(self_test())
        elif args.restore: restore(os.getenv('KD_DB','./kd.sqlite3'),args.restore)
        else: asyncio.run(serve())
    except KeyboardInterrupt: pass
    except Exception as ex:
        if isinstance(ex,ValueError) and not args.authorize:
            print('Configuration/action error: '+str(ex)[:400],file=sys.stderr)
        else:
            print('Operation failed: '+type(ex).__name__+'. Check configuration and Telegram authorization.',file=sys.stderr)
        raise SystemExit(1)


if __name__=='__main__':
    main()
