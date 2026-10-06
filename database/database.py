import sqlite3
from pathlib import Path
from config import DATABASE_PATH

def get_connection():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        active INTEGER NOT NULL DEFAULT 1
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS providers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        active INTEGER NOT NULL DEFAULT 1
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_date TEXT NOT NULL,
        location_id INTEGER NOT NULL,
        provider_id INTEGER NOT NULL,
        working_hours REAL NOT NULL DEFAULT 8,
        UNIQUE(schedule_date, location_id, provider_id),
        FOREIGN KEY(location_id) REFERENCES locations(id),
        FOREIGN KEY(provider_id) REFERENCES providers(id)
    )''')
    conn.commit()
    conn.close()
