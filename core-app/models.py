from datetime import datetime

from db import get_connection

BUFFER_RATIO = 0.7
CHECKPOINT_1_RATIO = 0.5
CHECKPOINT_2_RATIO = 0.75


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
