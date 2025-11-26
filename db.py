import sqlite3
from datetime import datetime
import pytz
from pathlib import Path

OMS_TZ = pytz.timezone("Asia/Omsk")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_NAME = DATA_DIR / "database.db"

DATA_DIR.mkdir(exist_ok=True)


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
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

def insert_record(user, uniform_type):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        now_omsk = datetime.now(OMS_TZ)
        ts = now_omsk.strftime("%H:%M %d-%m-%Y")

        cur.execute(
            "INSERT INTO laundry (user, uniform_type, timestamp) VALUES (?, ?, ?)",
            (user, uniform_type, ts)
        )
        conn.commit()

def get_last_records(limit=20):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT user, uniform_type, timestamp FROM laundry ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
    return rows

def get_current_holder_by_type(uniform_type):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT user, timestamp
            FROM laundry
            WHERE uniform_type = ?
            ORDER BY id DESC
            LIMIT 1
        """, (uniform_type,))
        row = cur.fetchone()
    return row

def get_all_records():
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, user, uniform_type, timestamp FROM laundry ORDER BY id DESC"
        )
        rows = cur.fetchall()
    return rows

def delete_record(rec_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM laundry WHERE id = ?", (rec_id,))
        conn.commit()
