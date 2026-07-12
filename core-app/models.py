from datetime import datetime, timedelta

from db import get_connection

BUFFER_RATIO = 0.7
CHECKPOINT_1_RATIO = 0.5
CHECKPOINT_2_RATIO = 0.75
URGENT_THRESHOLD_DAYS = 3


def calculate_buffer_deadline(created_at: datetime, external_deadline: datetime) -> datetime:
    available_time = external_deadline - created_at
    return created_at + BUFFER_RATIO * available_time


def calculate_checkpoints(created_at: datetime, buffer_deadline: datetime) -> tuple[datetime, datetime]:
    buffer_window = buffer_deadline - created_at
    checkpoint_1 = created_at + CHECKPOINT_1_RATIO * buffer_window
    checkpoint_2 = created_at + CHECKPOINT_2_RATIO * buffer_window
    return checkpoint_1, checkpoint_2


def create_task(
    name: str,
    external_deadline: datetime,
    buffer_deadline: datetime | None = None,
    checkpoint_1: datetime | None = None,
    checkpoint_2: datetime | None = None,
) -> dict:
    created_at = datetime.now()

    if buffer_deadline is None:
        buffer_deadline = calculate_buffer_deadline(created_at, external_deadline)

    calc_checkpoint_1, calc_checkpoint_2 = calculate_checkpoints(created_at, buffer_deadline)
    if checkpoint_1 is None:
        checkpoint_1 = calc_checkpoint_1
    if checkpoint_2 is None:
        checkpoint_2 = calc_checkpoint_2

    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO tasks (name, created_at, external_deadline, buffer_deadline, checkpoint_1, checkpoint_2, status)
        VALUES (?, ?, ?, ?, ?, ?, 'active')
        """,
        (
            name,
            created_at.isoformat(),
            external_deadline.isoformat(),
            buffer_deadline.isoformat(),
            checkpoint_1.isoformat(),
            checkpoint_2.isoformat(),
        ),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return get_task(task_id)


def get_task(task_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_tasks() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY buffer_deadline ASC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_task_status(task_id: int, status: str) -> None:
    conn = get_connection()
    conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()


def add_task_event(task_id: int, event_type: str, description: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO task_events (task_id, event_type, description, created_at) VALUES (?, ?, ?, ?)",
        (task_id, event_type, description, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_task_events(task_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM task_events WHERE task_id = ? ORDER BY created_at ASC", (task_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def buffer_progress_percent(task: dict) -> int:
    created_at = datetime.fromisoformat(task["created_at"])
    buffer_deadline = datetime.fromisoformat(task["buffer_deadline"])
    window = (buffer_deadline - created_at).total_seconds()
    if window <= 0:
        return 100
    elapsed = (datetime.now() - created_at).total_seconds()
    return max(0, min(100, int(elapsed / window * 100)))


def is_checkpoint_due(task: dict) -> bool:
    now = datetime.now()
    checkpoint_1 = datetime.fromisoformat(task["checkpoint_1"])
    checkpoint_2 = datetime.fromisoformat(task["checkpoint_2"])
    return now >= checkpoint_1 or now >= checkpoint_2


def is_urgent(task: dict) -> bool:
    if task["status"] != "active":
        return False
    buffer_deadline = datetime.fromisoformat(task["buffer_deadline"])
    return buffer_deadline - datetime.now() < timedelta(days=URGENT_THRESHOLD_DAYS)


def set_focus_tasks(task_ids: list[int]) -> list[int]:
    conn = get_connection()
    conn.execute("UPDATE tasks SET is_focus_task = 0")

    applied: list[int] = []
    if task_ids:
        placeholders = ",".join("?" * len(task_ids))
        rows = conn.execute(f"SELECT id FROM tasks WHERE id IN ({placeholders})", task_ids).fetchall()
        applied = [row["id"] for row in rows]
        conn.execute(f"UPDATE tasks SET is_focus_task = 1 WHERE id IN ({placeholders})", task_ids)

    conn.commit()
    conn.close()
    return applied
