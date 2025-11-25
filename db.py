import sqlite3
from datetime import datetime
import pytz
import os

OMS_TZ = pytz.timezone("Asia/Omsk")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_NAME = os.path.join(DATA_DIR, "database.db")

os.makedirs(DATA_DIR, exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS laundry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            uniform_type TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_record(user, uniform_type):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Текущее время Омска
    now_omsk = datetime.now(OMS_TZ)
    ts = now_omsk.strftime("%H:%M %d-%m-%Y")

    cur.execute(
        "INSERT INTO laundry (user, uniform_type, timestamp) VALUES (?, ?, ?)",
        (user, uniform_type, ts)
    )
    conn.commit()
    conn.close()


def get_last_records(limit=20):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT user, uniform_type, timestamp FROM laundry ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_current_holder_by_type(uniform_type):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT user, timestamp
        FROM laundry
        WHERE uniform_type = ?
        ORDER BY id DESC
        LIMIT 1
    """, (uniform_type,))
    row = cur.fetchone()
    conn.close()
    return row
