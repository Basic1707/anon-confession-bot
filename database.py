import sqlite3
import time
import threading
import os

# Creates 'bot.db' file in the directory where the bot runs. 
# This way it works smoothly on both Windows and Linux.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bot.db")

# --- CONNECTION ---
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# --- CREATE TABLES ---
def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                chat_id TEXT PRIMARY KEY,
                lang TEXT DEFAULT 'tr',
                username TEXT DEFAULT NULL
            );
            CREATE TABLE IF NOT EXISTS stats (
                key TEXT PRIMARY KEY,
                value INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS user_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT,
                link_name TEXT,
                views INTEGER DEFAULT 0,
                msgs INTEGER DEFAULT 0,
                UNIQUE(chat_id, link_name)
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS waiting_list (
                chat_id TEXT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS banned_users (
                chat_id TEXT PRIMARY KEY,
                reason TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS link_senders (
                sender_id TEXT,
                target_id TEXT,
                link_name TEXT,
                PRIMARY KEY (sender_id, target_id, link_name)
            );
            CREATE TABLE IF NOT EXISTS used_reply_tokens (
                token TEXT PRIMARY KEY,
                created_at INTEGER DEFAULT (strftime('%s','now'))
            );
        """)
        conn.execute("INSERT OR IGNORE INTO stats (key, value) VALUES ('total_msgs', 0)")
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance', 'false')")
        # Migration: add username column to old DB
        try:
            conn.execute("ALTER TABLE users ADD COLUMN username TEXT")
        except sqlite3.OperationalError:
            pass
        conn.commit()

# --- USER ---
def get_lang_db(user, bot, admin_id):
    chat_id = str(user.id)
    username = user.username or None
    conn = get_conn()

    try:
        row = conn.execute("SELECT lang FROM users WHERE chat_id = ?", (chat_id,)).fetchone()
        if row:
            conn.execute("UPDATE users SET username = ? WHERE chat_id = ?", (username, chat_id))
            conn.commit()
            return row["lang"]
        
        lang_code = user.language_code or ""
        chosen = "ru" if lang_code.startswith("ru") else "en" if lang_code.startswith("en") else "tr"
        
        conn.execute("INSERT OR IGNORE INTO users (chat_id, lang, username) VALUES (?, ?, ?)", (chat_id, chosen, username))
        conn.commit()

        # Notification to admin (outside finally block or controlled so the connection closes even if an error occurs)
        try:
            full_name = user.first_name or ""
            if user.last_name:
                full_name += f" {user.last_name}"
            username_str = f" (@{user.username})" if user.username else ""
            notif_text = (
                f"👤 **YENİ KULLANICI KATILDI!**\n\n"
                f"🆔 **ID:** `{chat_id}`\n"
                f"👤 **İsim:** {full_name}{username_str}\n"
                f"🌍 **Dil:** {chosen.upper()}"
            )
            bot.send_message(admin_id, notif_text, parse_mode="Markdown")
        except sqlite3.OperationalError:
            pass

        return chosen
    finally:
        conn.close()

def set_lang_db(chat_id, lang):
    conn = get_conn()
    try:
        conn.execute("INSERT OR REPLACE INTO users (chat_id, lang) VALUES (?, ?)", (str(chat_id), lang))
        conn.commit()
    finally:
        conn.close()

def get_all_users():
    with get_conn() as conn:
        rows = conn.execute("SELECT chat_id, lang FROM users").fetchall()
        return {row["chat_id"]: row["lang"] for row in rows}

def get_user_count():
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]

def get_lang_counts():
    with get_conn() as conn:
        rows = conn.execute("SELECT lang, COUNT(*) as c FROM users GROUP BY lang").fetchall()
        counts = {"tr": 0, "en": 0, "ru": 0}
        for row in rows:
            counts[row["lang"]] = row["c"]
        return counts

def get_recent_users(limit=20):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT chat_id, lang, username FROM users ORDER BY rowid DESC LIMIT ?", (limit,)
        ).fetchall()
        return [(row["chat_id"], row["lang"], row["username"] if row["username"] else None) for row in rows]

# --- MAINTENANCE ---
def get_maintenance():
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = 'maintenance'").fetchone()
        return row["value"] == "true" if row else False

def set_maintenance(val: bool):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES ('maintenance', ?)",
            ("true" if val else "false",)
        )
        conn.commit()

# --- STATISTICS ---
def get_total_msgs():
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM stats WHERE key = 'total_msgs'").fetchone()
        return row["value"] if row else 0

def increment_total_msgs():
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO stats (key, value) VALUES ('total_msgs', 1) "
            "ON CONFLICT(key) DO UPDATE SET value = value + 1"
        )
        conn.commit()

# --- LINKS ---
def get_user_links(chat_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT link_name, views, msgs FROM user_links WHERE chat_id = ?", (str(chat_id),)
        ).fetchall()
        return {row["link_name"]: {"views": row["views"], "msgs": row["msgs"]} for row in rows}

def ensure_link(chat_id, link_name):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO user_links (chat_id, link_name, views, msgs) VALUES (?, ?, 0, 0)",
            (str(chat_id), link_name)
        )
        conn.commit()

def increment_link_views(chat_id, link_name):
    with get_conn() as conn:
        conn.execute(
            "UPDATE user_links SET views = views + 1 WHERE chat_id = ? AND link_name = ?",
            (str(chat_id), link_name)
        )
        conn.commit()

def increment_link_msgs(chat_id, link_name):
    with get_conn() as conn:
        conn.execute(
            "UPDATE user_links SET msgs = msgs + 1 WHERE chat_id = ? AND link_name = ?",
            (str(chat_id), link_name)
        )
        conn.commit()

def delete_link(chat_id, link_name):
    with get_conn() as conn:
        conn.execute(
            "DELETE FROM user_links WHERE chat_id = ? AND link_name = ?",
            (str(chat_id), link_name)
        )
        conn.commit()

def delete_all_links(chat_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM user_links WHERE chat_id = ?", (str(chat_id),))
        conn.commit()

# --- WAITING LIST ---
def get_waiting_list():
    with get_conn() as conn:
        rows = conn.execute("SELECT chat_id FROM waiting_list").fetchall()
        return [int(row["chat_id"]) for row in rows]

def add_to_waiting_list(chat_id):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO waiting_list (chat_id) VALUES (?)", (str(chat_id),))
        conn.commit()

def clear_waiting_list():
    with get_conn() as conn:
        conn.execute("DELETE FROM waiting_list")
        conn.commit()

# --- BAN ---
def ban_user(chat_id, reason=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO banned_users (chat_id, reason) VALUES (?, ?)",
            (str(chat_id), reason)
        )
        conn.commit()

def unban_user(chat_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM banned_users WHERE chat_id = ?", (str(chat_id),))
        conn.commit()

def is_banned(chat_id):
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM banned_users WHERE chat_id = ?", (str(chat_id),)).fetchone()
        return row is not None

def get_all_banned():
    with get_conn() as conn:
        rows = conn.execute("SELECT chat_id, reason FROM banned_users").fetchall()
        return [(row["chat_id"], row["reason"]) for row in rows]

# --- LINK SENDER (1 COMMENT LIMIT) ---
def has_sent_to_link(sender_id, target_id, link_name):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM link_senders WHERE sender_id = ? AND target_id = ? AND link_name = ?",
            (str(sender_id), str(target_id), link_name)
        ).fetchone()
        return row is not None

def mark_sent_to_link(sender_id, target_id, link_name):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO link_senders (sender_id, target_id, link_name) VALUES (?, ?, ?)",
            (str(sender_id), str(target_id), link_name)
        )
        conn.commit()

# --- REPLY TOKEN (ONE-TIME USE) ---
def is_reply_token_used(token):
    with get_conn() as conn:
        row = conn.execute("SELECT 1 FROM used_reply_tokens WHERE token = ?", (token,)).fetchone()
        return row is not None

def mark_reply_token_used(token):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO used_reply_tokens (token, created_at) VALUES (?, strftime('%s','now'))",
            (token,)
        )
        conn.commit()

def clean_old_tokens():
    """Clear reply tokens older than 7 days"""
    seven_days_ago = int(time.time()) - (7 * 24 * 60 * 60)
    with get_conn() as conn:
        deleted = conn.execute(
            "DELETE FROM used_reply_tokens WHERE created_at < ?", (seven_days_ago,)
        ).rowcount
        conn.commit()
    if deleted > 0:
        print(f"🧹 {deleted} eski reply token temizlendi.")

def start_token_cleaner():
    """Run the token cleaner every 24 hours"""
    def loop():
        while True:
            clean_old_tokens()
            time.sleep(24 * 60 * 60)
    t = threading.Thread(target=loop, daemon=True)
    t.start()
