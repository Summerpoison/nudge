"""Wipe core-app's database and repopulate it with a small, realistic
test dataset covering the states the UI needs to show: a plain active
task, one past its first checkpoint, one on hold, one done, and one
marked as this week's focus task.

nudge.db and core-app/uploads/ are throwaway local artifacts (both
gitignored) -- safe to re-run any time you want a clean, predictable
state instead of manually recreating tasks by hand.

Usage:
    .venv\\Scripts\\python.exe seed_data.py
"""

import shutil
from datetime import datetime, timedelta

from db import DB_PATH, get_connection, init_db
from models import calculate_buffer_deadline, calculate_checkpoints
from uploads import UPLOAD_DIR, task_upload_dir


def seed_task(conn, name, created_at, external_deadline, status="active", is_focus_task=False):
    buffer_deadline = calculate_buffer_deadline(created_at, external_deadline)
    checkpoint_1, checkpoint_2 = calculate_checkpoints(created_at, buffer_deadline)
    cursor = conn.execute(
        """
        INSERT INTO tasks
            (name, created_at, external_deadline, buffer_deadline, checkpoint_1, checkpoint_2, status, is_focus_task)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            created_at.isoformat(),
            external_deadline.isoformat(),
            buffer_deadline.isoformat(),
            checkpoint_1.isoformat(),
            checkpoint_2.isoformat(),
            status,
            1 if is_focus_task else 0,
        ),
    )
    return cursor.lastrowid


def seed_event(conn, task_id, event_type, description, created_at):
    conn.execute(
        "INSERT INTO task_events (task_id, event_type, description, created_at) VALUES (?, ?, ?, ?)",
        (task_id, event_type, description, created_at.isoformat()),
    )


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    init_db()

    conn = get_connection()
    now = datetime.now()

    seed_task(
        conn,
        "Write research proposal",
        created_at=now - timedelta(days=1),
        external_deadline=now + timedelta(days=21),
    )

    seed_task(
        conn,
        "Fix login bug",
        created_at=now - timedelta(days=6),
        external_deadline=now + timedelta(days=2),
    )

    on_hold_id = seed_task(
        conn,
        "Review PR feedback",
        created_at=now - timedelta(days=3),
        external_deadline=now + timedelta(days=10),
        status="on_hold",
    )
    seed_event(
        conn,
        on_hold_id,
        "triage_draft_sent",
        "Blocker triage (Waiting on someone): draft sent to teamlead@example.com",
        now - timedelta(hours=6),
    )

    done_id = seed_task(
        conn,
        "Draft Q4 report",
        created_at=now - timedelta(days=10),
        external_deadline=now + timedelta(days=5),
        status="done",
    )
    seed_event(conn, done_id, "status_changed", "Status changed to Done", now - timedelta(days=1))
    upload_dir = task_upload_dir(done_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    (upload_dir / "q4_report_draft.txt").write_text(
        "Placeholder content for local testing.\n", encoding="utf-8"
    )
    seed_event(
        conn, done_id, "artifact_submitted", "Artifact submitted: q4_report_draft.txt", now - timedelta(days=2)
    )

    focus_id = seed_task(
        conn,
        "Prepare oral exam slides",
        created_at=now - timedelta(days=4),
        external_deadline=now + timedelta(days=3),
        is_focus_task=True,
    )
    seed_event(
        conn, focus_id, "marked_focus_task", "Marked as a focus task for this week", now - timedelta(hours=2)
    )

    conn.commit()
    conn.close()

    print("Seeded 5 test tasks:")
    print("  1. Write research proposal   -- active, no checkpoint due")
    print("  2. Fix login bug             -- active, checkpoint reached")
    print("  3. Review PR feedback        -- on hold")
    print("  4. Draft Q4 report           -- done, has an attachment")
    print("  5. Prepare oral exam slides  -- focus task, checkpoint reached")


if __name__ == "__main__":
    main()
