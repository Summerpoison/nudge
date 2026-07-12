from datetime import datetime, timedelta

from db import get_connection

BUFFER_RATIO = 0.7
CHECKPOINT_1_RATIO = 0.5
CHECKPOINT_2_RATIO = 0.75
URGENT_THRESHOLD_DAYS = 3


def round_to_nearest_30_minutes(value: datetime) -> datetime:
    discard = timedelta(minutes=value.minute % 30, seconds=value.second, microseconds=value.microsecond)
    rounded = value - discard
    if discard >= timedelta(minutes=15):
        rounded += timedelta(minutes=30)
    return rounded


def calculate_buffer_deadline(
    created_at: datetime, external_deadline: datetime, buffer_ratio: float = BUFFER_RATIO
) -> datetime:
    available_time = external_deadline - created_at
    return round_to_nearest_30_minutes(created_at + buffer_ratio * available_time)


def calculate_checkpoints(
    created_at: datetime,
    buffer_deadline: datetime,
    checkpoint_1_ratio: float = CHECKPOINT_1_RATIO,
    checkpoint_2_ratio: float = CHECKPOINT_2_RATIO,
) -> tuple[datetime, datetime]:
    buffer_window = buffer_deadline - created_at
    checkpoint_1 = round_to_nearest_30_minutes(created_at + checkpoint_1_ratio * buffer_window)
    checkpoint_2 = round_to_nearest_30_minutes(created_at + checkpoint_2_ratio * buffer_window)
    return checkpoint_1, checkpoint_2


def create_task(
    name: str,
    external_deadline: datetime,
    buffer_deadline: datetime | None = None,
    checkpoint_1: datetime | None = None,
    checkpoint_2: datetime | None = None,
) -> dict:
    created_at = datetime.now()
    settings = get_settings()

    if buffer_deadline is None:
        buffer_deadline = calculate_buffer_deadline(created_at, external_deadline)

    calc_checkpoint_1, calc_checkpoint_2 = calculate_checkpoints(
        created_at, buffer_deadline, settings["checkpoint_1_ratio"], settings["checkpoint_2_ratio"]
    )
    if checkpoint_1 is None:
        checkpoint_1 = calc_checkpoint_1
    if checkpoint_2 is None:
        checkpoint_2 = calc_checkpoint_2

    # Back-calculated from the *actual* stored timestamps (not just copied
    # from settings) so the ratio always matches reality exactly, even
    # after 30-minute rounding or an explicit per-task override -- the
    # label on the task-detail page must never claim a percentage that
    # doesn't correspond to the real stored dates.
    buffer_window = (buffer_deadline - created_at).total_seconds()
    checkpoint_1_ratio = (checkpoint_1 - created_at).total_seconds() / buffer_window if buffer_window else 0
    checkpoint_2_ratio = (checkpoint_2 - created_at).total_seconds() / buffer_window if buffer_window else 0

    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO tasks (name, created_at, external_deadline, buffer_deadline, checkpoint_1, checkpoint_2,
                            checkpoint_1_ratio, checkpoint_2_ratio, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """,
        (
            name,
            created_at.isoformat(),
            external_deadline.isoformat(),
            buffer_deadline.isoformat(),
            checkpoint_1.isoformat(),
            checkpoint_2.isoformat(),
            checkpoint_1_ratio,
            checkpoint_2_ratio,
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
    # Resetting buddy_alerted here means a task that gets reopened after
    # being put on hold or marked done starts its escalation state fresh --
    # otherwise a task alerted once could never trigger a second, genuinely
    # new round of buddy attention after being resumed.
    conn.execute("UPDATE tasks SET status = ?, buddy_alerted = 0 WHERE id = ?", (status, task_id))
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


def is_urgent(task: dict, threshold_days: float = URGENT_THRESHOLD_DAYS) -> bool:
    if task["status"] != "active":
        return False
    buffer_deadline = datetime.fromisoformat(task["buffer_deadline"])
    return buffer_deadline - datetime.now() < timedelta(days=threshold_days)


# Only these event types count as the "did the required checkpoint
# interaction" per CHKP-FUNC-004 -- a status change or focus-task marking
# is not a check-in.
CHECK_IN_EVENT_TYPES = {"artifact_submitted", "triage_draft_sent"}


def _has_check_in(events: list[dict], window_start: datetime, window_end: datetime) -> bool:
    return any(
        event["event_type"] in CHECK_IN_EVENT_TYPES
        and window_start <= datetime.fromisoformat(event["created_at"]) <= window_end
        for event in events
    )


def needs_buddy_alert(task: dict, threshold_days: float = URGENT_THRESHOLD_DAYS) -> bool:
    """ESC-FUNC-004: escalation stage 3.

    Buffer deadline blown is always a definite alert. Short of that, a
    single missed checkpoint isn't enough on its own -- checking in at
    checkpoint 1 but skipping checkpoint 2 usually still leaves enough
    runway to hit the buffer deadline. Only *both* checkpoints going by
    without an interaction means the buddy gets pulled in.
    """
    if task["status"] != "active" or task["buddy_alerted"]:
        return False
    if not is_urgent(task, threshold_days):
        return False

    now = datetime.now()
    created_at = datetime.fromisoformat(task["created_at"])
    checkpoint_2 = datetime.fromisoformat(task["checkpoint_2"])
    buffer_deadline = datetime.fromisoformat(task["buffer_deadline"])

    if now >= buffer_deadline:
        return True
    if now < checkpoint_2:
        return False

    events = get_task_events(task["id"])
    checkpoint_1_missed = not _has_check_in(events, created_at, checkpoint_2)
    checkpoint_2_missed = not _has_check_in(events, checkpoint_2, now)
    return checkpoint_1_missed and checkpoint_2_missed


def mark_buddy_alerted(task_id: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE tasks SET buddy_alerted = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def get_settings() -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM settings WHERE id = 1").fetchone()
    conn.close()
    return dict(row)


def update_settings(**fields) -> dict:
    conn = get_connection()
    assignments = ", ".join(f"{key} = ?" for key in fields)
    conn.execute(f"UPDATE settings SET {assignments} WHERE id = 1", list(fields.values()))
    conn.commit()
    conn.close()
    return get_settings()


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
