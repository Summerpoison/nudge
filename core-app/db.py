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
            checkpoint_1_ratio REAL NOT NULL DEFAULT 0.5,
            checkpoint_2_ratio REAL NOT NULL DEFAULT 0.75,
            status TEXT NOT NULL DEFAULT 'active',
            is_focus_task INTEGER NOT NULL DEFAULT 0
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            smtp_host TEXT NOT NULL DEFAULT 'localhost',
            smtp_port INTEGER NOT NULL DEFAULT 1025,
            from_address TEXT NOT NULL DEFAULT 'nudge@localhost',
            to_address TEXT NOT NULL DEFAULT 'user@localhost',
            checkpoint_1_ratio REAL NOT NULL DEFAULT 0.5,
            checkpoint_2_ratio REAL NOT NULL DEFAULT 0.75,
            urgent_threshold_days REAL NOT NULL DEFAULT 3,
            buddy_name TEXT NOT NULL DEFAULT '',
            buddy_email TEXT NOT NULL DEFAULT '',
            date_format TEXT NOT NULL DEFAULT '%b %d, %Y %I:%M %p'
        )
        """
    )
    # Singleton row (CHECK id = 1 enforces this at the schema level) --
    # INSERT OR IGNORE means this is a no-op on every init after the first.
    conn.execute("INSERT OR IGNORE INTO settings (id) VALUES (1)")
    conn.commit()
    conn.close()
