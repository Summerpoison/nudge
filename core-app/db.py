import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "nudge.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            external_deadline TEXT NOT NULL,
            buffer_deadline TEXT NOT NULL,
            checkpoint_1 TEXT NOT NULL,
            checkpoint_2 TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS task_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL REFERENCES tasks(id),
            event_type TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
