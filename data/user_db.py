import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            preferences TEXT,
            history TEXT
        )
    ''')
    conn.commit()
    conn.close()

from functools import lru_cache

@lru_cache(maxsize=128)
def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT preferences, history FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"preferences": row[0], "history": row[1]}
    return None

def update_user_preferences(user_id, preferences, latest_chat_turn=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    user_data = get_user(user_id)
    # Check if user exists
    if user_data:
        history = user_data['history'] or ""
        if latest_chat_turn:
            history += latest_chat_turn + "\n"
            # Keep history short (last ~1000 chars)
            if len(history) > 1000:
                history = history[-1000:]
                
        cursor.execute('''
            UPDATE users SET preferences = ?, history = ? WHERE user_id = ?
        ''', (preferences, history, user_id))
    else:
        history = latest_chat_turn + "\n" if latest_chat_turn else ""
        cursor.execute('''
            INSERT INTO users (user_id, preferences, history)
            VALUES (?, ?, ?)
        ''', (user_id, preferences, history))
    conn.commit()
    conn.close()
    
    # Invalidate the cache for this user since their preferences changed
    get_user.cache_clear()

init_db()
