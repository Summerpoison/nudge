"""Wipe core-app's database and repopulate it with a small, realistic
test dataset covering the states the UI needs to show: plain active
tasks, one past its first checkpoint, one in the checkpoint grace
window, on-hold tasks (triaged and untriaged), a done task, focus
tasks, and overdue tasks at each stage of buddy escalation (pending
and already alerted).

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


def seed_task(
    conn, name, created_at, external_deadline, status="active", is_focus_task=False, buddy_alerted=False
):
    buffer_deadline = calculate_buffer_deadline(created_at, external_deadline)
    checkpoint_1, checkpoint_2 = calculate_checkpoints(created_at, buffer_deadline)
    cursor = conn.execute(
        """
        INSERT INTO tasks
            (name, created_at, external_deadline, buffer_deadline, checkpoint_1, checkpoint_2, status,
             is_focus_task, buddy_alerted)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            1 if buddy_alerted else 0,
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

    seed_task(
        conn,
        "Update onboarding docs",
        created_at=now - timedelta(days=8),
        external_deadline=now + timedelta(days=15),
        is_focus_task=True,
    )

    seed_task(
        conn,
        "Sort out laptop replacement",
        created_at=now - timedelta(days=2),
        external_deadline=now + timedelta(days=14),
        status="on_hold",
    )

    seed_task(
        conn,
        "Migrate reporting queries",
        created_at=now - timedelta(days=3),
        external_deadline=now + timedelta(days=5),
    )

    seed_task(
        conn,
        "Submit conference talk abstract",
        created_at=now - timedelta(days=20),
        external_deadline=now - timedelta(days=1),
    )

    escalated_id = seed_task(
        conn,
        "Refactor auth middleware",
        created_at=now - timedelta(days=15),
        external_deadline=now - timedelta(days=2),
        buddy_alerted=True,
    )
    seed_event(
        conn, escalated_id, "buddy_alert_sent", "Buddy notified: task needs attention", now - timedelta(days=1)
    )

    conn.commit()
    conn.close()

    print("Seeded 10 test tasks:")
    print("  1. Write research proposal        -- active, no checkpoint due")
    print("  2. Fix login bug                  -- active, checkpoint reached")
    print("  3. Review PR feedback             -- on hold, triage draft sent")
    print("  4. Draft Q4 report                -- done, has an attachment")
    print("  5. Prepare oral exam slides       -- focus task, checkpoint reached")
    print("  6. Update onboarding docs         -- second focus task, no checkpoint due")
    print("  7. Sort out laptop replacement    -- on hold, not yet triaged")
    print("  8. Migrate reporting queries      -- active, checkpoint 1 missed (in grace window)")
    print("  9. Submit conference talk abstract -- active, overdue, buddy alert pending")
    print(" 10. Refactor auth middleware       -- active, overdue, buddy already alerted")


if __name__ == "__main__":
    main()
