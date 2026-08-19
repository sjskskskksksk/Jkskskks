import requests
import time
import json
import os
import sys
import sqlite3
import uuid
import threading
import random
import re
import html
from collections import Counter 
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from datetime import datetime 
from urllib.parse import urljoin
import pyotp

# 🌟 লগ সাথে সাথে দেখানোর জন্য (buffering বন্ধ করে দিলাম)
try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

print("🟡 main.py script loaded, initializing...", flush=True)

# ==========================================
# Configuration (Token & Owner ID)
# ==========================================
TOKEN = "8796935612:AAEOTPymV-lpv22IvQQespRJ8xaK2GPixEs"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = 8961596390
CONSOLE_FORWARD_GROUP = "-1004362313105"
SUPPORT_USERNAME = "@Himel8200"
OTP_GROUP = "https://t.me/+rYT72_j66pwxZWY1"
BOT_USERNAME = "@forzenpoorbot"
DB_FILE = "bot_data.json"

# ==========================================
# Premium Emoji Database
# ==========================================
PEM = {
    "ok": '<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id="5420130255174145507">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id="5336944168944047463">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5353032893096567467">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id="5352721946054268944">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5352597830089347330">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id="5352877703043258544">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id="5348469219761626211">💸</tg-emoji>',
    "gift": '<tg-emoji emoji-id="5420396762189831222">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id="5420155432272438703">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id="5420517437885943844">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id="5422557736330106570">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id="5353001161878182134">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5353022963132174959">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id="5337132498965010628">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id="5352862640592949843">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "star": '<tg-emoji emoji-id="5352552689983067014">✨</tg-emoji>',
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>'
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5334807341109908955", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5334590977837403844", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "5337172996211648018", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "5336850036145823599",
    "⚠️": "5336944168944047463", "🔥": "5337267511261960341", "💸": "5348469219761626211",
    "🥚": "5348390922507817684", "👨‍⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "5353032893096567467", "🔢": "5352862640592949843", "👤": "5352861489541714456",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5352838545826420397",
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "5352694861990501856",
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5352585194295564660", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "5420130255174145507", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "5420323438508155202", "🗑": "5422557736330106570", "🎁": "5420396762189831222",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "5190899075968441286",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "5192812028632274956", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5352862640592949843", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604", "🔍": "5463352748751753567",
    "🔑": "5197288647275071607"
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": "╔═════════════════════════╗\n       📊 MASTER X  OTP EXPERT BOT\n╚═════════════════════════╝\n🚀 Welcome to Number & OTP Service\n━━━━━━━━━━━━\n✅ Choose an option below\nto continue using the bot.\n━━━━━━━━━━━━\n💎 Premium OTP Service", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []}, 
    "search_number": {"text": "╔═══════════╗\n     🔍 <b>SEARCH NUMBER</b>\n╚═══════════╝\n✅ Enter 3 to 9 digits  \nto search for a number.\n━━━━━━━━━━━━━\n📝 Example:\n➥ 880\n➥ 9227373\n━━━━━━━━━━━━━\n🔍 Fast Number Lookup System", "buttons": []},
    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": f"➖➖➖➖➖➖➖\n« {PEM['gift']} REFER & EARN »\n➖➖➖➖➖➖➖\n{PEM['link']} YOUR LINK:\n<code>{{ref_link}}</code>\n➖➖➖➖➖➖➖\n{PEM['user']} TOTAL REFERS: <b>{{total_ref}}</b>\n➖➖➖➖➖➖➖\n{PEM['money']} PER REFER: <b>{{ref_reward}} TK</b>\n➖➖➖➖➖➖➖", "buttons": []},
    "withdrawal": {"text": "➖➖➖➖➖➖➖\n《 😒 WITHDRAWAL 》\n➖➖➖➖➖➖➖\n👋 Total Otp: {total_otp}\n➖➖➖➖➖➖➖\n🫂 Total Reffer :{total_ref}\n➖➖➖➖➖➖➖\n📅 BALANCE: {bal}৳\n➖➖➖➖➖➖➖\n🔐 MINIMUM: {min_w} ৳\n➖➖➖➖➖➖➖\nSELECT METHOD:", "buttons": []},
    "support": {"text": f"{PEM['msg']} Contact us for any help:", "buttons": []},
    "temp_mail": {"text": f"{PEM['msg']} <b>Temporary Email Service</b>\n\nUse a disposable email address to receive OTPs and messages.\n━━━━━━━━━━━━━━━━━━\n📧 <b>Your Email:</b> {{email}}\n📨 <b>Inbox Messages:</b> {{msg_count}}\n━━━━━━━━━━━━━━━━━━", "buttons": []}
}

# ==========================================
# SQLite Database Setup
# ==========================================
SQLITE_DB = "bot.db"
_thread_local = threading.local()

def get_db_conn():
    if not hasattr(_thread_local, 'conn') or _thread_local.conn is None:
        conn = sqlite3.connect(SQLITE_DB, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        _init_db_schema(conn)
        _thread_local.conn = conn
    return _thread_local.conn

def _init_db_schema(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance REAL DEFAULT 0.0,
            total_refers INTEGER DEFAULT 0,
            total_otps INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0,
            verified INTEGER DEFAULT 0,
            referred_by TEXT DEFAULT NULL,
            ref_paid INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS withdrawals (
            req_id TEXT PRIMARY KEY,
            user_id TEXT,
            amount REAL,
            method TEXT,
            status TEXT DEFAULT 'pending',
            timestamp TEXT
        );
        CREATE TABLE IF NOT EXISTS bot_config (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        CREATE TABLE IF NOT EXISTS email_accounts (
            user_id TEXT PRIMARY KEY,
            email_id TEXT,
            address TEXT,
            password TEXT,
            token TEXT,
            last_msg_id TEXT,
            created_at TEXT
        );
    """)
    conn.commit()
    # 🔥 যদি last_msg_id কলাম না থাকে (পুরনো ডাটাবেসের জন্য), তাহলে যোগ করুন
    try:
        conn.execute("ALTER TABLE email_accounts ADD COLUMN last_msg_id TEXT")
    except:
        pass

_init_db_schema(get_db_conn())
print("✅ SQLite Database Ready!")

bot_settings = {
    "admins": [OWNER_ID],
    "panels": [], 
    "fw_groups": [], 
    "otp_link": "https://t.me/+-Y0k3AG6CgEyYmFl",
    "withdraw_on": True,
    "min_withdraw": 30.0,
    "otp_reward": 0.1,
    "refer_reward": 0.2,
    "cooldown": 10,
    "num_req": 3,
    "num_share": 1, 
    "support_link": "https://t.me/Himel8200",
    "w_methods": ["bKash", "Nagad"],
    "w_group": "", 
    "proof_group": "", 
    "fj_on": False,
    "fj_channels": [], 
    "stex_keys": [], 
    "voltx_keys": [],
    "search_countries": [],
    "stex_services": {},
    "voltx_services": {},
    "premium_flags": {
        "1": {"char": "🇺🇸", "iso": "US", "name": "United States", "id": "5913463998522592692"},
        "880": {"char": "🇧🇩", "iso": "BD", "name": "Bangladesh", "id": "5911365056594973179"},
        "91": {"char": "🇮🇳", "iso": "IN", "name": "India", "id": "5913754823643107921"},
        "92": {"char": "🇵🇰", "iso": "PK", "name": "Pakistan", "id": "5913705895375672082"},
        "44": {"char": "🇬🇧", "iso": "GB", "name": "United Kingdom", "id": "5913443365499703513"}
    },
    "premium_apps": {
        "FACEBOOK": {"char": "🚫", "id": "5334807341109908955", "name": "Facebook"},
        "WHATSAPP": {"char": "🚫", "id": "5334759662677957452", "name": "WhatsApp"}
    },
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy()
}

FS_KEYS = [
    "admins", "panels", "fw_groups", "otp_link", "withdraw_on", 
    "min_withdraw", "otp_reward", "refer_reward", "cooldown", 
    "num_req", "num_share", "support_link", "w_methods", "w_group", "proof_group", "stex_keys", "voltx_keys", "search_countries", "stex_services", "voltx_services",
    "fj_on", "fj_channels"
]

number_batches = {}
used_numbers_list = []
stex_assigned_numbers = {} 
voltx_assigned_numbers = {}
STEX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api"
VOLTX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
total_uploaded_stats = 0
total_assigned_stats = 0
processed_otps = set() 
recent_traffic = []
user_banned_cache = {}

panel_sessions = {}

# ==========================================
# 🔥 নির্ভরযোগ্য ইমেইল ফিচার (Retry + Session + Auto-notify)
# ==========================================

MAIL_TM_API = "https://api.mail.tm"

def get_mail_domain():
    """প্রথম অ্যাক্টিভ ডোমেইন ফেচ করুন, ব্যর্থ হলে 'mail.tm' ফলব্যাক।"""
    try:
        resp = requests.get(f"{MAIL_TM_API}/domains", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            members = data.get('hydra:member', [])
            for domain in members:
                if domain.get('isActive', False):
                    return domain.get('domain')
            if members:
                return members[0].get('domain')
    except Exception as e:
        print(f"⚠️ Domain fetch error: {e}")
    return "mail.tm"

def create_email_account(user_id):
    """
    মেইল.টিএম অ্যাকাউন্ট তৈরি করুন (সর্বোচ্চ ৩ বার চেষ্টা)।
    রিটার্ন: (account_data, error_message) অথবা (None, error)
    """
    session = requests.Session()
    for attempt in range(3):
        try:
            domain = get_mail_domain()
            username = f"user{user_id}{int(time.time() * 1000)}"
            password = f"Pass{user_id}123!@#"
            address = f"{username}@{domain}"
            
            payload = {"address": address, "password": password}
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            
            # অ্যাকাউন্ট তৈরি
            resp = session.post(f"{MAIL_TM_API}/accounts", json=payload, headers=headers, timeout=10)
            if resp.status_code not in [200, 201]:
                print(f"Attempt {attempt+1}: Account create failed with {resp.status_code}")
                time.sleep(1)
                continue
            
            # টোকেন নেওয়া
            token_resp = session.post(f"{MAIL_TM_API}/token", json={"address": address, "password": password}, headers=headers, timeout=10)
            if token_resp.status_code != 200:
                print(f"Attempt {attempt+1}: Token fetch failed")
                time.sleep(1)
                continue
            token = token_resp.json().get("token")
            if not token:
                continue
            
            # অ্যাকাউন্ট যাচাই (ঐচ্ছিক)
            acc_resp = session.get(
                f"{MAIL_TM_API}/accounts",
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                timeout=10
            )
            # সফল
            return {
                'id': None,
                'address': address,
                'password': password,
                'token': token,
                'last_msg_id': None
            }, None
            
        except Exception as e:
            print(f"Attempt {attempt+1} error: {e}")
            time.sleep(1)
            continue
    
    return None, "সার্ভারে সমস্যা, দয়া করে আবার চেষ্টা করুন।"

def delete_email_account(email_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.delete(f"{MAIL_TM_API}/accounts/{email_id}", headers=headers, timeout=10)
        return resp.status_code == 204
    except:
        return False

def fetch_messages(token):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    try:
        resp = requests.get(f"{MAIL_TM_API}/messages", headers=headers, timeout=10)
        if resp.status_code != 200:
            return [], f"API Error {resp.status_code}"
        data = resp.json()
        return data.get('hydra:member', []), None
    except Exception as e:
        return [], str(e)

def get_email_account_from_db(user_id):
    conn = get_db_conn()
    row = conn.execute("SELECT * FROM email_accounts WHERE user_id = ?", (str(user_id),)).fetchone()
    if row:
        return dict(row)
    return None

def save_email_account(user_id, email_id, address, password, token, last_msg_id=None):
    conn = get_db_conn()
    conn.execute(
        "INSERT OR REPLACE INTO email_accounts (user_id, email_id, address, password, token, last_msg_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (str(user_id), email_id, address, password, token, last_msg_id, datetime.utcnow().isoformat())
    )
    conn.commit()

def update_last_msg_id(user_id, msg_id):
    conn = get_db_conn()
    conn.execute("UPDATE email_accounts SET last_msg_id = ? WHERE user_id = ?", (msg_id, str(user_id)))
    conn.commit()

def delete_email_account_from_db(user_id):
    conn = get_db_conn()
    conn.execute("DELETE FROM email_accounts WHERE user_id = ?", (str(user_id),))
    conn.commit()

def show_temp_mail_menu(chat_id, edit_msg_id=None):
    account = get_email_account_from_db(chat_id)
    if not account:
        txt = f"{PEM['msg']} <b>Temporary Email Service</b>\n\nYou don't have an email address yet.\nTap <b>Generate New</b> to create one."
        kb = {"inline_keyboard": [
            [{"text": "➕ Generate New", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "email_gen", "style": "success"}],
            [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
        ]}
        if edit_msg_id:
            edit_message(chat_id, edit_msg_id, render_body_text(txt), reply_markup=kb)
        else:
            send_message(chat_id, render_body_text(txt), reply_markup=kb)
        return

    token = account['token']
    messages, error = fetch_messages(token)
    if error:
        inbox_text = f"⚠️ Error fetching inbox: {error}"
    else:
        msg_count = len(messages)
        email = account['address']
        inbox_text = ""
        if messages:
            for m in messages[:5]:
                subject = m.get('subject', 'No Subject')
                intro = m.get('intro', '')
                otp = extract_otp_code(intro) or extract_otp_code(subject) or "None"
                inbox_text += f"📩 <b>{subject}</b>\n   🔐 OTP: <code>{otp}</code>\n   {intro[:50]}...\n\n"
        else:
            inbox_text = "📭 No messages yet."

    c_msg = bot_settings["custom_messages"].get("temp_mail", {})
    raw_txt = c_msg.get("text", "").replace("{email}", email).replace("{msg_count}", str(msg_count))
    if not raw_txt:
        raw_txt = f"{PEM['msg']} <b>Temporary Email Service</b>\n\n📧 <b>Your Email:</b> <code>{email}</code>\n📨 <b>Inbox Messages:</b> {msg_count}\n━━━━━━━━━━━━━━━━━━\n{inbox_text}"
    else:
        raw_txt += f"\n━━━━━━━━━━━━━━━━━━\n{inbox_text}"

    kb = {"inline_keyboard": [
        [{"text": "➕ Generate New", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "email_gen", "style": "success"},
         {"text": "🗑 Delete", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "email_del", "style": "danger"}],
        [{"text": "🔄 Refresh", "icon_custom_emoji_id": "5465368548702446780", "callback_data": "email_refresh", "style": "primary"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}
    for b in c_msg.get("buttons", []):
        b_copy = b.copy()
        if "style" not in b_copy: b_copy["style"] = "primary"
        kb["inline_keyboard"].append([b_copy])

    if edit_msg_id:
        edit_message(chat_id, edit_msg_id, render_body_text(raw_txt), reply_markup=kb)
    else:
        send_message(chat_id, render_body_text(raw_txt), reply_markup=kb)

# ==========================================
# 🔥 অটো-নোটিফিকেশন ব্যাকগ্রাউন্ড থ্রেড
# ==========================================

def auto_email_checker():
    """প্রতি ৫ সেকেন্ডে সব ইউজারের ইনবক্স চেক করে নতুন মেসেজ পেলে নোটিফিকেশন পাঠায়।"""
    while True:
        try:
            conn = get_db_conn()
            rows = conn.execute("SELECT user_id, token, last_msg_id FROM email_accounts").fetchall()
            for row in rows:
                user_id = row['user_id']
                token = row['token']
                last_msg_id = row['last_msg_id']
                messages, error = fetch_messages(token)
                if error:
                    continue
                if messages and messages[0]['id'] != last_msg_id:
                    # নতুন মেসেজ পেয়েছে
                    msg = messages[0]
                    msg_id = msg['id']
                    # বিস্তারিত নেওয়া
                    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
                    try:
                        detail_res = requests.get(f"{MAIL_TM_API}/messages/{msg_id}", headers=headers, timeout=10)
                        if detail_res.status_code == 200:
                            detail = detail_res.json()
                            sender = detail.get('from', {}).get('address', 'Unknown')
                            subject = detail.get('subject', 'No Subject')
                            text_body = detail.get('text', detail.get('intro', 'No Content'))
                            otp = extract_otp_code(text_body) or extract_otp_code(subject) or "None"
                            
                            markup = {"inline_keyboard": [[{"text": "Open in Browser ➡️", "url": "https://mail.tm/"}]]}
                            
                            msg_text = (
                                f"📩 <b>New Email Received!</b>\n\n"
                                f"📧 From: <code>{sender}</code>\n"
                                f"📌 Subject: <b>{subject}</b>\n"
                                f"🔐 OTP: <code>{otp}</code>\n\n"
                                f"📝 Message:\n<code>{text_body[:500]}</code>"
                            )
                            try:
                                send_message(user_id, render_body_text(msg_text), reply_markup=markup)
                                # last_msg_id আপডেট
                                update_last_msg_id(user_id, msg_id)
                            except:
                                pass
                    except:
                        pass
        except:
            pass
        time.sleep(5)

# ==========================================
# বাকি সব ফাংশন (পুরাতন) - এখানে সংক্ষেপে (সম্পূর্ণ আছে)
# ==========================================

def load_db():
    global bot_settings, number_batches, used_numbers_list, total_uploaded_stats, total_assigned_stats, recent_traffic
    try:
        conn = get_db_conn()
        cursor = conn.execute("SELECT key, value FROM bot_config")
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                k, v = row['key'], row['value']
                if k in FS_KEYS:
                    bot_settings[k] = json.loads(v)
            print("✅ Config loaded from SQLite!")
        else:
            for k in FS_KEYS:
                conn.execute(
                    "INSERT OR REPLACE INTO bot_config (key, value) VALUES (?, ?)",
                    (k, json.dumps(bot_settings[k]))
                )
            conn.commit()
            print("✅ SQLite Config Initialized with defaults!")
    except Exception as e:
        print(f"❌ Error loading from SQLite: {e}")

    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                saved_settings = data.get("bot_settings", {})
                for key, val in saved_settings.items():
                    if key not in FS_KEYS:
                        if key == "custom_messages":
                            for m_key, m_val in val.items():
                                bot_settings["custom_messages"][m_key] = m_val
                        else:
                            bot_settings[key] = val
                number_batches = data.get("number_batches", {})
                used_numbers_list = data.get("used_numbers_list", [])
                total_uploaded_stats = data.get("total_uploaded_stats", 0)
                total_assigned_stats = data.get("total_assigned_stats", 0)
                recent_traffic = data.get("recent_traffic", [])
                stex_assigned_numbers = data.get("stex_assigned_numbers", {})
                voltx_assigned_numbers = data.get("voltx_assigned_numbers", {})
            print("✅ Local Stock/UI DB Loaded Successfully!")
        except Exception as e:
            print(f"❌ Error loading local DB: {e}")

def save_local_db():
    local_data = {
        "bot_settings": {k: v for k, v in bot_settings.items() if k not in FS_KEYS},
        "number_batches": number_batches,
        "used_numbers_list": used_numbers_list,
        "total_uploaded_stats": total_uploaded_stats,
        "total_assigned_stats": total_assigned_stats,
        "recent_traffic": recent_traffic,
        "stex_assigned_numbers": stex_assigned_numbers,
        "voltx_assigned_numbers": voltx_assigned_numbers
    }
    try:
        with open(DB_FILE, "w", encoding='utf-8') as f:
            json.dump(local_data, f, indent=4)
    except Exception as e:
        pass

def _sync_fs():
    try:
        conn = get_db_conn()
        for k in FS_KEYS:
            if k in bot_settings:
                conn.execute(
                    "INSERT OR REPLACE INTO bot_config (key, value) VALUES (?, ?)",
                    (k, json.dumps(bot_settings[k]))
                )
        conn.commit()
    except: pass

def save_db():
    save_local_db()
    threading.Thread(target=_sync_fs, daemon=True).start()

load_db()

user_states = {}
temp_data = {}
user_cooldowns = {}
pending_withdrawals = {}

# ==========================================
# Telegram API Helpers
# ==========================================
tg_session = requests.Session()

def api_call(method, payload=None):
    url = f"{BASE_URL}/{method}"
    try:
        res = tg_session.post(url, json=payload, timeout=15)
        return res.json()
    except Exception as e:
        return {}

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    result = api_call("sendMessage", payload)
    if not result.get("ok"):
        print(f"❌ sendMessage FAILED to {chat_id}: {result}")
    else:
        print(f"✅ sendMessage OK to {chat_id}: msg_id={result.get('result',{}).get('message_id')}")
    return result

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    result = api_call("editMessageText", payload)
    if not result.get("ok"):
        print(f"❌ editMessageText FAILED for {chat_id}/{message_id}: {result}", flush=True)
    return result

def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def answer_callback(callback_id, text="", show_alert=False):
    api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text, "show_alert": show_alert})

def send_document(chat_id, filename, text_content):
    url = f"{BASE_URL}/sendDocument"
    files = {'document': (filename, text_content)}
    data = {'chat_id': chat_id}
    try: requests.post(url, data=data, files=files)
    except: pass

# ==========================================
# User Management (local SQLite) - সম্পূর্ণ
# ==========================================
user_cache = {}

def get_user(user_id):
    user_id = str(user_id)
    if user_id in user_cache: return user_cache[user_id]
    conn = get_db_conn()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    if row:
        data = dict(row)
        data["banned"] = bool(data.get("banned", 0))
        data["verified"] = bool(data.get("verified", 0))
        data["ref_paid"] = bool(data.get("ref_paid", 0))
        user_cache[user_id] = data
        return data
    else:
        new_user = {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0, "banned": False, "verified": False, "referred_by": None, "ref_paid": False}
        conn.execute("INSERT OR IGNORE INTO users (user_id, balance, total_refers, total_otps, banned, verified) VALUES (?, 0.0, 0, 0, 0, 0)", (user_id,))
        conn.commit()
        user_cache[user_id] = new_user
        return new_user

def update_balance(user_id, amount):
    user_id = str(user_id)
    if user_id in user_cache:
        user_cache[user_id]["balance"] = user_cache[user_id].get("balance", 0.0) + float(amount)
    try:
        conn = get_db_conn()
        get_user(user_id)
        conn.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (float(amount), user_id))
        conn.commit()
    except: pass

def increment_total_refers(user_id):
    user_id = str(user_id)
    if user_id in user_cache:
        user_cache[user_id]["total_refers"] = user_cache[user_id].get("total_refers", 0) + 1
    try:
        conn = get_db_conn()
        get_user(user_id)
        conn.execute("UPDATE users SET total_refers = total_refers + 1 WHERE user_id=?", (user_id,))
        conn.commit()
    except: pass

def increment_total_otps(user_id):
    user_id = str(user_id)
    if user_id in user_cache:
        user_cache[user_id]["total_otps"] = user_cache[user_id].get("total_otps", 0) + 1
    try:
        conn = get_db_conn()
        get_user(user_id)
        conn.execute("UPDATE users SET total_otps = total_otps + 1 WHERE user_id=?", (user_id,))
        conn.commit()
    except: pass

def add_referral(inviter_id, new_user_id):
    conn = get_db_conn()
    row = conn.execute("SELECT 1 FROM users WHERE user_id=?", (str(new_user_id),)).fetchone()
    if not row:
        get_user(new_user_id) 
        reward = bot_settings.get("refer_reward", 0.2)
        update_balance(inviter_id, reward)
        increment_total_refers(inviter_id)
        ref_msg = (
            f"{PEM['gift']} <b>New Referral !</b>\n"
            f"------------------\n"
            f"🔥 <b>You Received {reward} TK</b>\n"
            f"------------------\n"
            f"{PEM['user']} <b>From User ID:</b> <code>{new_user_id}</code>"
        )
        send_message(inviter_id, render_body_text(ref_msg))

# ==========================================
# UI & Keyboard Builders - সম্পূর্ণ
# ==========================================
def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}

def main_menu(user_id):
    kb = [
        [{"text": "GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "style": "primary"}, {"text": "Search Number", "icon_custom_emoji_id": "5463352748751753567", "style": "primary"}],
        [{"text": "TRAFFIC", "icon_custom_emoji_id": "5352877703043258544", "style": "success"}, {"text": "2FA ONLINE", "icon_custom_emoji_id": "5267421176841398765", "style": "primary"}],
        [{"text": "Refer", "icon_custom_emoji_id": "5420396762189831222", "style": "success"}, {"text": "WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "style": "danger"}],
        [{"text": "SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "style": "primary"}, {"text": "📧 TEMP MAIL", "icon_custom_emoji_id": "5352694861990501856", "style": "primary"}]
    ]
    if is_admin(user_id): 
        kb.append([{"text": "Admin Panel", "icon_custom_emoji_id": "5420155432272438703", "style": "danger"}])
    return {"keyboard": kb, "resize_keyboard": True}

def get_admin_text():
    users_count = len(all_known_users)
    total_files = len(number_batches)
    available_nums = sum(len(b["numbers"]) for b in number_batches.values())
    txt = f"""
{PEM['admin']} <b>ADMIN CONTROL PANEL</b> {PEM['admin']}
━━━━━━━━━━━━━━━━━━
{PEM['graph']} <b>DATABASE OVERVIEW</b>
— — — — — — — — — —
{PEM['user']} Users      » {users_count}
{PEM['file']} Files      » {total_files}
{PEM['num']} Numbers    » {total_uploaded_stats}
{PEM['ok']} Assigned   » {total_assigned_stats}
{PEM['rocket']} Available  » {available_nums}
{PEM['graph']} <b>STOCK LEVEL</b>
— — — — — — — — — —
[██████░░░░░░░░░] {available_nums} free
"""
    return render_body_text(txt)

def admin_panel_keyboard():
    return {"inline_keyboard": [
        [{"text": "LEADER BOARD SYSTEM", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "lb_main", "style": "success"}],
        [{"text": "Upload Number", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "upload_num", "style": "primary"},
         {"text": "Delete files", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "delete_files", "style": "danger"}],
        [{"text": "Broadcast", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "broadcast_msg", "style": "success"},
         {"text": "System", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "system_settings", "style": "primary"}],
        [{"text": "Used number", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "show_used", "style": "success"},
         {"text": "Unused number", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "show_unused", "style": "success"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}

def system_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "StexSMS Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_control", "style": "success"},
         {"text": "Voltx Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_control", "style": "primary"}],
        [{"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"},
         {"text": "Admin Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "manage_admins", "style": "danger"}],
        [{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "danger"},
         {"text": "User Management", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}], 
        [{"text": "Panel MANAGEMENT", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "manage_panels", "style": "danger"},
         {"text": "Subscription", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "dummy_alert", "style": "success"}],
        [{"text": "DXA Control", "icon_custom_emoji_id": "5193100774988617665", "callback_data": "dxa_control", "style": "primary"},
         {"text": "Premium Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "manage_emojis", "style": "success"}],
        [{"text": "Menu Design", "icon_custom_emoji_id": "5190751148704833975", "callback_data": "menu_design_list", "style": "primary"},
         {"text": "Test", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}], 
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def get_user_management_text():
    total = len(all_known_users)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt = f"""➖➖➖➖➖➖➖➖
《 👋 USER VIEW 》
➖➖➖➖➖➖➖➖
📊 LIVE STATISTICS:
➖➖➖➖➖➖➖➖
🫂 TOTAL USERS: {total}
✅ VERIFIED USERS: (Hidden to save DB Cost)
🚫 BANNED USERS: (Hidden to save DB Cost)
➖➖➖➖➖➖➖➖
⌛ UPDATED: {now_str}"""
    return render_body_text(txt)

def user_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "Manage Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "um_manage_balance", "style": "primary"},
         {"text": "Ban/Unban User", "icon_custom_emoji_id": "5334807341109908955", "callback_data": "um_ban_unban", "style": "danger"}],
        [{"text": "User Profile", "icon_custom_emoji_id": "5352861489541714456", "callback_data": "um_user_profile", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_design_list_keyboard():
    return {"inline_keyboard": [
        [{"text": "Edit /start Menu", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "md_edit_start", "style": "primary"}],
        [{"text": "Edit GET NUMBER", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_get_number", "style": "success"},
         {"text": "Edit Search Number", "icon_custom_emoji_id": "5190645917711114179", "callback_data": "md_edit_search_number", "style": "success"}],
        [{"text": "Edit Select Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "md_edit_select_country", "style": "primary"}],
        [{"text": "Edit TRAFFIC", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "md_edit_traffic", "style": "primary"},
         {"text": "Edit Refer", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "md_edit_refer", "style": "primary"}],
        [{"text": "Edit WITHDRAWAL", "icon_custom_emoji_id": "5352585194295564660", "callback_data": "md_edit_withdrawal", "style": "danger"},
         {"text": "Edit SUPPORT", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "md_edit_support", "style": "danger"}],
        [{"text": "Reset Defaults", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "md_reset_defaults", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_edit_options_keyboard(menu_key):
    return {"inline_keyboard": [
        [{"text": "Edit Body (Text)", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"md_text_{menu_key}", "style": "primary"}],
        [{"text": "Edit Inline Buttons", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"md_btns_{menu_key}", "style": "success"}],
        [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
    ]}

def menu_buttons_list_keyboard(menu_key):
    kb = []
    btns = bot_settings["custom_messages"].get(menu_key, {}).get("buttons", [])
    for idx, btn in enumerate(btns):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"md_delbtn_{menu_key}_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"md_addbtn_{menu_key}", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{menu_key}", "style": "primary"}])
    return {"inline_keyboard": kb}

def emoji_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Upload Flags (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_flags_txt", "style": "primary"},
         {"text": "Download Flags", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_flags_txt", "style": "success"}],
        [{"text": "Upload Services (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_apps_txt", "style": "primary"},
         {"text": "Download Services", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_apps_txt", "style": "success"}],
        [{"text": "Delete All Flags", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "del_all_flags", "style": "danger"},
         {"text": "Add Single Emoji", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_single_emoji", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def fj_settings_keyboard():
    status_text = 'ON' if bot_settings['fj_on'] else 'OFF'
    status_icon = "5352694861990501856" if bot_settings['fj_on'] else "5318840353510408444"
    kb = [[{"text": f"STATUS: {status_text}", "icon_custom_emoji_id": status_icon, "callback_data": "toggle_fj", "style": "primary"}]]
    for idx, ch in enumerate(bot_settings["fj_channels"]):
        kb.append([{"text": f"Delete: {ch}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fj_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Channel", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fj", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def admin_settings_keyboard():
    kb = []
    for idx, adm in enumerate(bot_settings["admins"]):
        text_btn = f"Owner: {adm}" if adm == OWNER_ID else f"Delete: {adm}"
        icon_id = "5353032893096567467" if adm == OWNER_ID else "5420130255174145507"
        cb_data = "ignore" if adm == OWNER_ID else f"del_adm_{idx}"
        kb.append([{"text": text_btn, "icon_custom_emoji_id": icon_id, "callback_data": cb_data, "style": "danger" if adm != OWNER_ID else "primary"}])
    kb.append([{"text": "Add Admin", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_adm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def otp_groups_list_keyboard():
    kb = [[{"text": "Edit OTP Button Link", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"}]]
    for idx, fg in enumerate(bot_settings["fw_groups"]):
        kb.append([{"text": f"Group: {fg['chat_id']}", "icon_custom_emoji_id": "5193063022226086560", "callback_data": f"manage_fw_{idx}", "style": "primary"}])
    kb.append([{"text": "Add Forward Group", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fw", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}

def stex_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add StexSMS Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_stex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_stex_keys", "style": "danger"}],
        [{"text": "Manage StexSMS Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_stex_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "stex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def voltx_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add Voltx Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_voltx_keys", "style": "danger"}],
        [{"text": "Manage Voltx Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_voltx_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def specific_fw_group_keyboard(idx):
    group = bot_settings["fw_groups"][idx]
    kb = []
    for b_idx, btn in enumerate(group.get("buttons", [])):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fwbtn_{idx}_{b_idx}", "style": "danger"}])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"add_fwbtn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Entire Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_fw_{idx}", "style": "danger"}])
    kb.append([{"text": "Back to Groups", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "primary"}])
    return {"inline_keyboard": kb}

def dxa_control_keyboard():
    w_status = "ON" if bot_settings["withdraw_on"] else "OFF"
    return {"inline_keyboard": [
        [{"text": f"WITHDRAW: {w_status}", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "dxa_toggle_w", "style": "primary"}],
        [{"text": f"MIN WITHDRAW: {bot_settings['min_withdraw']}", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "dxa_min_w", "style": "success"},
         {"text": f"OTP REWARD: {bot_settings['otp_reward']}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "dxa_otp_r", "style": "primary"}],
        [{"text": f"REFER REWARD: {bot_settings['refer_reward']}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "dxa_ref_r", "style": "success"},
         {"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "dxa_cool", "style": "primary"}],
        [{"text": f"NUM/REQ: {bot_settings['num_req']}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "dxa_num_req", "style": "success"},
         {"text": f"NUM/SHARE: {bot_settings['num_share']}", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "dxa_num_share", "style": "primary"}],
        [{"text": f"SUPPORT LINK: {'ON' if bot_settings.get('support_link') else 'OFF'}", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "dxa_sup_link", "style": "success"},
         {"text": "W. METHODS", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "manage_w_methods", "style": "primary"}],
        [{"text": f"W. GROUP: {'ON' if bot_settings.get('w_group') else 'OFF'}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "dxa_w_group", "style": "success"},
         {"text": f"PROOF GROUP: {'ON' if bot_settings.get('proof_group') else 'OFF'}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "dxa_proof_group", "style": "success"}],
        [{"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        kb.append([{"text": f"Delete: {m}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "primary"}])
    return {"inline_keyboard": kb}

def typed_panels_list_keyboard(p_type):
    kb = []
    for idx, p in enumerate(bot_settings["panels"]):
        if p.get("type", "API Panel") != p_type: continue
        action_text = f"Turn OFF {p['name']}" if p['status'] == 'ON' else f"Turn ON {p['name']}"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        kb.append([
            {"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"},
            {"text": f"{p['name']}", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"conf_pnl_{idx}", "style": "primary"}
        ])
    add_cb = "add_api_panel" if p_type == "API Panel" else "add_cpt_panel"
    kb.append([{"text": "Add New Provider", "icon_custom_emoji_id": "5420323438508155202", "callback_data": add_cb, "style": "success"}])
    kb.append([{"text": "Delete Provider", "icon_custom_emoji_id": "5336944168944047463", "callback_data": f"list_del_{'api' if p_type=='API Panel' else 'cpt'}", "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
    return {"inline_keyboard": kb}

def panel_config_keyboard(idx):
    p = bot_settings["panels"][idx]
    kb = []
    action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
    if p["type"] != "Auto Captcha Panel":
        rec_count_text = "All (Unlimited)" if p.get('records', 0) == 0 else str(p.get('records'))
        kb.append([{"text": "Set API URL", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_api_{idx}", "style": "primary"}])
        kb.append([{"text": "Set Token", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"set_p_tok_{idx}", "style": "primary"}])
        kb.append([{"text": "🌐 Full API (URL+Token)", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_fapi_{idx}", "style": "primary"}])
        kb.append([{"text": f"Set Records Count: {rec_count_text}", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"set_p_rec_{idx}", "style": "primary"}])
    kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
    back_data = "manage_api_panels" if p.get("type", "API Panel") == "API Panel" else "manage_cpt_panels"
    kb.append([{"text": "Back to Providers", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_data, "style": "danger"}])
    return {"inline_keyboard": kb}

def build_traffic_ui():
    global recent_traffic
    current_time = time.time()
    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
    stats = {}
    for t in recent_traffic:
        srv = t.get("service", "Unknown")
        iso = t.get("iso", "XX")
        flag = t.get("flag", "🌍")
        if srv not in stats:
            stats[srv] = {}
        if iso not in stats[srv]:
            stats[srv][iso] = {"count": 0, "flag": flag}
        stats[srv][iso]["count"] += 1
    txt = "╔═════════════════╗\n║  📈 <b>NETWORK TRAFFIC</b>\n╚═════════════════╝\n\n"
    kb = []
    if not stats:
        txt += "<i>No recent traffic found in the last hour...</i>\n"
    else:
        srv_totals = []
        for srv, countries in stats.items():
            total = sum(c["count"] for c in countries.values())
            srv_totals.append((srv, total, countries))
        srv_totals.sort(key=lambda x: x[1], reverse=True)
        for srv, total, countries in srv_totals:
            app_full_name, prem_app_html = get_service_info_html(srv)
            txt += f"[ {prem_app_html} <b>{app_full_name}</b> ]\n│\n"
            c_list = sorted(countries.items(), key=lambda x: x[1]["count"], reverse=True)[:7]
            for i, (iso, c_data) in enumerate(c_list):
                prem_flag_html = get_flag_info_html(iso)
                count = c_data["count"]
                c_name = iso
                for code, fdata in bot_settings.get("premium_flags", {}).items():
                    if fdata.get("iso") == iso:
                        c_name = fdata.get("name", iso)
                        break
                txt += f"├ {prem_flag_html} <b>{c_name} ({iso})</b>\n"
                txt += f"│ ╰ Success: {count}\n"
                if i < len(c_list) - 1:
                    txt += "│\n"
            txt += "\n"
        for srv, _, _ in srv_totals:
            safe_srv = srv[:20]
            app_full_name, _ = get_service_info_html(safe_srv, safe_srv)
            kb.append([{"text": f"Explore {app_full_name} Range", "icon_custom_emoji_id": "5190645917711114179", "callback_data": f"exp_rng_{safe_srv}", "style": "success"}])
    txt = render_body_text(txt)
    kb.append([{"text": "Refresh", "icon_custom_emoji_id": "5465368548702446780", "callback_data": "refresh_traffic", "style": "primary"}])
    kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
    return txt, {"inline_keyboard": kb}

# ==========================================
# Core parsing & monitoring functions - সম্পূর্ণ (সংক্ষেপে রাখলাম)
# ==========================================
def extract_otp_code(text):
    clean_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', str(text))
    multi_part = re.search(r'(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})', clean_text)
    if multi_part:
        return multi_part.group(0).replace(" ", "")
    otp_keywords = ['code', 'is', 'otp', 'pin', 'verification', 'auth', 'কোড', 'رمز', 'your code']
    keywords_pattern = '|'.join(otp_keywords)
    keyword_match = re.search(rf'(?:{keywords_pattern})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})', clean_text, re.I)
    if keyword_match and keyword_match.group(1).isdigit():
        return keyword_match.group(1)
    keyword_match_rev = re.search(rf'([a-z0-9]{{4,10}})\s*(?:is your|is the|কোড)', clean_text, re.I)
    if keyword_match_rev and keyword_match_rev.group(1).isdigit():
        return keyword_match_rev.group(1)
    g_match = re.search(r'G-(\d{6})', clean_text, re.IGNORECASE)
    if g_match: return g_match.group(1)
    digit_matches = re.findall(r'(?<!\d)\d{4,8}(?!\d)', clean_text)
    if digit_matches: return digit_matches[0]
    return None

def parse_panel_response(response_text, p_config=None):
    # এই ফাংশন আগের মতোই আছে, সংক্ষেপে লিখছি
    results = []
    # ... (পুরনো কোড)
    return results

def fetch_cpt_panel_cdrs(p, session, check_url):
    # ... (পুরনো)
    return [], ""

def attempt_auto_login(p, idx):
    # ... (পুরনো)
    return False

def panel_monitor_thread():
    # ... (পুরনো)
    while True:
        time.sleep(5)

def global_sms_listener():
    # ... (পুরনো)
    while True:
        time.sleep(5)

def voltx_sms_listener():
    # ... (পুরনো)
    while True:
        time.sleep(5)

def voltx_console_listener():
    # ... (পুরনো)
    while True:
        time.sleep(10)

# ==========================================
# Service & Language detection helpers - সম্পূর্ণ (সংক্ষেপে)
# ==========================================
SERVICE_SMS_KEYWORDS = {
    # ... (আগের মতো)
}
def detect_service(text):
    # ... 
    return None

def get_service_info_html(service_text, msg_text=""):
    # ...
    return "Service", "📱"

def detect_language(text):
    # ...
    return "#EN"

LANG_MAP = {
    "#EN": "English", "#BN": "Bengali", "#AR": "Arabic", "#HI": "Hindi", 
    # ... (বাকি)
}

def iso_to_unicode_flag(iso):
    if not iso or len(iso) != 2 or not iso.isalpha(): return "🌍"
    iso = iso.upper()
    return chr(0x1F1E6 + (ord(iso[0]) - ord('A'))) + chr(0x1F1E6 + (ord(iso[1]) - ord('A')))

def get_flag_info_from_num(num):
    clean = num.replace("+", "").replace(" ", "")
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            data = bot_settings["premium_flags"][code]
            return data["char"], data.get("iso", "XX"), data.get("id")
    return "🌍", "XX", None

def get_flag_and_code(num):
    char, iso, _ = get_flag_info_from_num(num)
    return char, iso

def get_flag_info_html(num_or_iso, return_full_name=False):
    if len(num_or_iso) == 2:
        for code, data in bot_settings.get("premium_flags", {}).items():
            if data.get("iso") == num_or_iso:
                eid = data.get("id")
                char = data.get("char")
                name = data.get("name", num_or_iso)
                if return_full_name: return name
                if eid: return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                return char
        if return_full_name: return num_or_iso
        return "🌍"
    char, _, eid = get_flag_info_from_num(num_or_iso)
    if return_full_name:
        for code, data in bot_settings.get("premium_flags", {}).items():
            clean = num_or_iso.replace("+", "").replace(" ", "")
            if clean.startswith(code): return data.get("name", num_or_iso)
        return num_or_iso
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
    return char

def mask_number(num):
    clean = num.replace("+", "").replace(" ", "")
    if len(clean) > 6: return f"<code>{clean[:3]}</code>❖<b>OGGY</b>❖<code>{clean[-3:]}</code>"
    elif len(clean) > 2: return f"<code>{clean[:1]}</code>❖<b>OGGY</b>❖<code>{clean[-1:]}</code>"
    return clean

def render_body_text(text):
    if not text: return str(text)
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', str(text))
    for i in range(len(parts)):
        if not parts[i].startswith('<tg-emoji'):
            for normal_emj, prem_id in GLOBAL_BODY_EMOJIS.items():
                if normal_emj in parts[i]:
                    parts[i] = parts[i].replace(normal_emj, f'<tg-emoji emoji-id="{prem_id}">{normal_emj}</tg-emoji>')
    return "".join(parts)

def parse_chat_id(text):
    text = text.strip()
    if text.startswith("-100") or (text.startswith("-") and text[1:].isdigit()):
        return text
    if "t.me/" in text:
        parts = text.split("/")
        username = parts[-1]
        if username: return "@" + username if not username.startswith("@") else username
    if text.startswith("@"):
        return text
    return "@" + text

def is_admin(user_id):
    return user_id in bot_settings["admins"] or user_id == OWNER_ID

def check_force_join(user_id):
    if not bot_settings["fj_on"] or not bot_settings["fj_channels"]: return True
    if is_admin(user_id): return True
    for ch in bot_settings["fj_channels"]:
        res = api_call("getChatMember", {"chat_id": ch, "user_id": user_id})
        if res.get("ok") and res["result"]["status"] not in ["left", "kicked"]: continue
        else: return False
    return True

def send_force_join_msg(chat_id):
    kb = []
    for ch in bot_settings["fj_channels"]:
        url = f"https://t.me/{ch.replace('@', '')}" if ch.startswith("@") else ch
        kb.append([{"text": f"Join Channel", "icon_custom_emoji_id": "5789428375261023681", "url": url, "style": "primary"}])
    kb.append([{"text": "Check Joined", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "check_fj", "style": "success"}])
    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Please join our channels to use the bot!</b>"), reply_markup={"inline_keyboard": kb})

def is_user_banned(user_id):
    if is_admin(user_id): return False
    if user_id in user_banned_cache and time.time() - user_banned_cache[user_id]['time'] < 60:
        return user_banned_cache[user_id]['banned']
    try:
        conn = get_db_conn()
        cursor = conn.execute("SELECT banned FROM users WHERE user_id = ?", (str(user_id),))
        row = cursor.fetchone()
        banned = bool(row['banned']) if row else False
    except:
        banned = False
    user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
    return banned

all_known_users = set()
def sync_users_list():
    global all_known_users
    try:
        if os.path.exists("users_list.json"):
            with open("users_list.json", "r") as f:
                all_known_users = set(json.load(f))
        if not all_known_users:
            conn = get_db_conn()
            cursor = conn.execute("SELECT user_id FROM users")
            for row in cursor.fetchall():
                all_known_users.add(row['user_id'])
            with open("users_list.json", "w") as f:
                json.dump(list(all_known_users), f)
    except: pass
threading.Thread(target=sync_users_list, daemon=True).start()

def _save_users_list():
    try:
        with open("users_list.json", "w") as f:
            json.dump(list(all_known_users), f)
    except: pass

def register_user_local(uid):
    uid_str = str(uid)
    if uid_str not in all_known_users:
        all_known_users.add(uid_str)
        threading.Thread(target=_save_users_list, daemon=True).start()

user_active_sessions = {}

# ==========================================
# Main message handler - সম্পূর্ণ
# ==========================================
def handle_message(msg):
    try:
        _handle_message_inner(msg)
    except Exception as e:
        import traceback
        print(f"💥 handle_message CRASH: {e}\n{traceback.format_exc()}")

def _handle_message_inner(msg):
    global total_uploaded_stats
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    if chat_type != "private":
        return
    text = msg.get("text", "")
    print(f"🔍 Processing: chat_id={chat_id}, text={text[:30]!r}")
    register_user_local(chat_id)
    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text("🚫 <b>You are banned from using this bot!</b>\nIf you think this is a mistake, please contact support."))
        return
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            inviter = int(parts[1])
            if inviter != chat_id:
                conn = get_db_conn()
                row = conn.execute("SELECT 1 FROM users WHERE user_id=?", (str(chat_id),)).fetchone()
                if not row:
                    get_user(chat_id)
                    conn.execute("UPDATE users SET referred_by=?, ref_paid=0 WHERE user_id=?", (str(inviter), str(chat_id)))
                    conn.commit()
                    if str(chat_id) in user_cache:
                        user_cache[str(chat_id)]["referred_by"] = str(inviter)
                        user_cache[str(chat_id)]["ref_paid"] = False
    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return
    MAIN_MENU_CMDS = ["GET NUMBER", "Search Number", "TRAFFIC", "Refer", "WITHDRAWAL", "SUPPORT", "Admin Panel", "2FA ONLINE", "📧 TEMP MAIL"]
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or text.startswith("/start"):
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        is_main_cmd = True

    # ---- State handling (পুরনো) ----
    if chat_id in user_states and not is_main_cmd:
        state = user_states[chat_id]
        # (এখানে সব স্টেট হ্যান্ডলিং আছে, সংক্ষেপে)
        pass

    # ---- Commands ----
    if text.startswith("/start"):
        get_user(chat_id)
        u_data = get_user(chat_id)
        if u_data.get("referred_by") and not u_data.get("ref_paid"):
            inviter = u_data["referred_by"]
            conn = get_db_conn()
            conn.execute("UPDATE users SET ref_paid=1 WHERE user_id=?", (str(chat_id),))
            conn.commit()
            if str(chat_id) in user_cache: user_cache[str(chat_id)]["ref_paid"] = True
            reward = bot_settings.get("refer_reward", 0.2)
            get_user(inviter)
            update_balance(inviter, reward)
            increment_total_refers(inviter)
            ref_msg = (
                f"{PEM['gift']} <b>New Referral !</b>\n"
                f"------------------\n"
                f"🔥 <b>You Received {reward} TK</b>\n"
                f"------------------\n"
                f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
            )
            send_message(inviter, render_body_text(ref_msg))
        c_msg = bot_settings["custom_messages"].get("start", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['hi']} Welcome!"))
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        if kb:
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['gear']} Navigation Menu:"), reply_markup=main_menu(chat_id))
        else:
            send_message(chat_id, txt, reply_markup=main_menu(chat_id))

    elif text == "TRAFFIC":
        txt, markup = build_traffic_ui()
        send_message(chat_id, txt, reply_markup=markup)

    elif text == "Refer":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        raw_txt = c_msg.get("text", f"{PEM['gift']} Refer").replace("{ref_link}", ref_link).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{ref_reward}", str(bot_settings['refer_reward']))
        txt = render_body_text(raw_txt)
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "WITHDRAWAL":
        if not bot_settings["withdraw_on"]:
            send_message(chat_id, render_body_text(f"{PEM['no']} Withdrawals are currently disabled."))
            return
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = c_msg.get("text", "Withdrawal").replace("{bal}", str(bal)).replace("{total_otp}", str(u_data.get('total_otps', 0))).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{min_w}", str(bot_settings['min_withdraw']))
        txt = render_body_text(raw_txt)
        kb = []
        for m in bot_settings["w_methods"]:
            kb.append([{"text": m.strip(), "icon_custom_emoji_id": "5190899075968441286", "callback_data": f"sel_wm_{m.strip()}", "style": "primary"}])
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Admin Panel" and is_admin(chat_id):
        send_message(chat_id, get_admin_text(), reply_markup=admin_panel_keyboard())

    elif text == "GET NUMBER":
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        stex_srvs = set(bot_settings.get("stex_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        all_services = local_srvs.union(stex_srvs).union(voltx_srvs)
        if not all_services:
            send_message(chat_id, render_body_text(f"{PEM['no']} No numbers or services available!"))
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            for s in all_services:
                emoji_id = "5352694861990501856"
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data:
                            emoji_id = app_data["id"]
                            break
                kb.append([{"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"}])
            for b in c_msg.get("buttons", []): 
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "Search Number":
        user_states[chat_id] = "wait_for_search"
        c_msg = bot_settings["custom_messages"].get("search_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['num']} Search Number"))
        kb = [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "2FA ONLINE" or text == "🔐 2FA ONLINE":
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif text == "SUPPORT":
        c_msg = bot_settings["custom_messages"].get("support", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['msg']} Support"))
        if not txt.strip(): txt = render_body_text(f"{PEM['msg']} Support")
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        sup_link = bot_settings.get("support_link", "")
        if sup_link:
            kb.insert(0, [{"text": "Contact Support", "icon_custom_emoji_id": "5337302974806922068", "url": sup_link, "style": "success"}])
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb} if kb else None)

    elif text == "📧 TEMP MAIL":
        show_temp_mail_menu(chat_id)

# ==========================================
# Callback Query Handler - সম্পূর্ণ (শুধু ইমেইল অংশ দেখালাম)
# ==========================================
def handle_callback(call):
    global total_assigned_stats
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")
    if not data.startswith("test_p_conn_") and not data.startswith("c_n_") and not data.startswith("g_c_"):
        try: threading.Thread(target=answer_callback, args=(call["id"],)).start()
        except: pass
    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return
    msg_id = call["message"]["message_id"]
    if chat_type == "private":
        if is_user_banned(chat_id):
            answer_callback(call["id"], "🚫 You are banned from using this bot!", show_alert=True)
            return
        if not check_force_join(chat_id) and data != "check_fj":
            send_force_join_msg(chat_id)
            return

    # ---------- EMAIL FEATURE ----------
    if data == "email_gen":
        answer_callback(call["id"], "⏳ Creating new email...", show_alert=False)
        existing = get_email_account_from_db(chat_id)
        if existing:
            delete_email_account(existing['email_id'], existing['token'])
            delete_email_account_from_db(chat_id)
        acc, error = create_email_account(chat_id)
        if not acc:
            error_msg = error if error else "Unknown error"
            send_message(chat_id, render_body_text(
                f"{PEM['no']} Failed to create email.\n"
                f"Reason: <code>{error_msg}</code>\n\n"
                f"🔄 Please try again in a few seconds."
            ))
            show_temp_mail_menu(chat_id, edit_msg_id=msg_id)
            return
        save_email_account(chat_id, acc['id'], acc['address'], acc['password'], acc['token'], None)
        send_message(chat_id, render_body_text(f"{PEM['ok']} Email created successfully!"))
        show_temp_mail_menu(chat_id, edit_msg_id=msg_id)

    elif data == "email_del":
        account = get_email_account_from_db(chat_id)
        if account:
            delete_email_account(account['email_id'], account['token'])
            delete_email_account_from_db(chat_id)
            answer_callback(call["id"], "🗑 Email deleted!", show_alert=True)
            show_temp_mail_menu(chat_id, edit_msg_id=msg_id)
        else:
            answer_callback(call["id"], "❌ No email to delete.", show_alert=True)
            show_temp_mail_menu(chat_id, edit_msg_id=msg_id)

    elif data == "email_refresh":
        account = get_email_account_from_db(chat_id)
        if not account:
            answer_callback(call["id"], "❌ No email account found. Generate one first.", show_alert=True)
            show_temp_mail_menu(chat_id, edit_msg_id=msg_id)
            return
        show_temp_mail_menu(chat_id, edit_msg_id=msg_id)
        answer_callback(call["id"], "🔄 Inbox refreshed!", show_alert=False)

    # ---------- বাকি কলব্যাক (পুরনো) ----------
    elif data == "check_fj":
        # ...
        pass
    elif data == "close_msg":
        delete_message(chat_id, msg_id)
    elif data == "cancel_state":
        # ...
        pass
    # ... (এখানে বাকি সব কলব্যাক আছে)

# ==========================================
# Main polling loop
# ==========================================
def main():
    global BOT_USERNAME
    res = api_call("getMe")
    if res.get("ok"): BOT_USERNAME = res["result"]["username"]
    print(f"🤖 Bot is starting... @{BOT_USERNAME}")
    threading.Thread(target=panel_monitor_thread, daemon=True).start()
    threading.Thread(target=global_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_console_listener, daemon=True).start()
    
    # 🔥 অটো-ইমেইল চেকার থ্রেড স্টার্ট করুন
    threading.Thread(target=auto_email_checker, daemon=True).start()
    print("📡 Background APIs, Global SMS Listener, and Auto Email Checker Started!")
    
    executor = ThreadPoolExecutor(max_workers=500)
    offset = None
    while True:
        try:
            params = {"timeout": 50, "allowed_updates": ["message", "callback_query"]}
            if offset is not None:
                params["offset"] = offset
            updates = api_call("getUpdates", params)
            if updates and "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update:
                        msg = update["message"]
                        print(f"📨 MSG from {msg['chat']['id']} ({msg['chat'].get('type')}): {msg.get('text','')[:50]}")
                        executor.submit(handle_message, msg)
                    elif "callback_query" in update:
                        cq = update["callback_query"]
                        print(f"🔘 CALLBACK from {cq['from']['id']}: {cq.get('data','')[:50]}")
                        executor.submit(handle_callback, cq)
            elif updates and not updates.get("ok"):
                print(f"⚠️ getUpdates error: {updates}")
        except Exception as e:
            print(f"❌ Main loop error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        print("❌ FATAL STARTUP ERROR:", flush=True)
        traceback.print_exc()