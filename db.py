import os
import sqlite3
from datetime import datetime

# Папка для базы внутри контейнера
DB_DIR = "/data"
DB_NAME = os.path.join(DB_DIR, "database.db")


def _ensure_db_dir():
    """Создаёт папку /data, если она отсутствует."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)


def _connect():
    """Гарантирует существование пути и открывает SQLite."""
    _ensure_db_dir()
    return sqlite3.connect(DB_NAME, timeout=10)


def init_db():
    """Создание таблицы + миграция структуры."""
    conn = _connect()
    cur = conn.cursor()

    # Создаем таблицу, если её нет
    cur.execute("""
        CREATE TABLE IF NOT EXISTS laundry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            uniform_type TEXT,
            timestamp TEXT,
            active INTEGER DEFAULT 1
        )
    """)
    conn.commit()

    # Проверяем наличие колонки active (для старых баз)
    cur.execute("PRAGMA table_info(laundry)")
    cols = [row[1] for row in cur.fetchall()]
    if "active" not in cols:
        cur.execute("ALTER TABLE laundry ADD COLUMN active INTEGER DEFAULT 1")
        conn.commit()

    conn.close()


def insert_record(user, uniform_type):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO laundry (user, uniform_type, timestamp, active) VALUES (?, ?, ?, 1)",
        (user, uniform_type, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def close_active_records(uniform_type):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "UPDATE laundry SET active = 0 WHERE uniform_type = ? AND active = 1",
        (uniform_type,)
    )
    conn.commit()
    conn.close()


def get_active_holder(uniform_type):
    conn = _connect()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, user, timestamp FROM laundry
            WHERE uniform_type = ? AND active = 1
            ORDER BY datetime(timestamp) DESC LIMIT 1
        """, (uniform_type,))
        row = cur.fetchone()
    except sqlite3.OperationalError:
        cur.execute("""
            SELECT id, user, timestamp FROM laundry
            WHERE uniform_type = ?
            ORDER BY id DESC LIMIT 1
        """, (uniform_type,))
        row = cur.fetchone()
    conn.close()
    return row


def get_last_records(limit=50):
    conn = _connect()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, user, uniform_type, timestamp, active FROM laundry
            ORDER BY datetime(timestamp) DESC LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
    except sqlite3.OperationalError:
        cur.execute("""
            SELECT id, user, uniform_type, timestamp, active FROM laundry
            ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
    conn.close()
    return rows

def activate_previous_record(uniform_type):
    """После удаления активируем предыдущую запись по этому комплекту."""
    conn = _connect()
    cur = conn.cursor()

    # найти последнюю запись для этого комплекта
    cur.execute("""
        SELECT id FROM laundry 
        WHERE uniform_type = ? 
        ORDER BY datetime(timestamp) DESC 
        LIMIT 1
    """, (uniform_type,))
    row = cur.fetchone()

    if row:
        prev_id = row[0]
        cur.execute("UPDATE laundry SET active = 1 WHERE id = ?", (prev_id,))
        conn.commit()

    conn.close()

def delete_record(record_id):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM laundry WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
