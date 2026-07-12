import json
import smtplib
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import make_msgid

sys.stdout.reconfigure(encoding="utf-8")

CORE_APP_URL = "http://127.0.0.1:3000"
POLL_INTERVAL_SECONDS = 30

SMTP_HOST = "localhost"
SMTP_PORT = 1025
FROM_ADDRESS = "nudge@localhost"
TO_ADDRESS = "user@localhost"
REVIEW_EMAIL_INTERVAL_SECONDS = 60  # stands in for "weekly" during local testing


def log(message: str) -> None:
    print(f"[{datetime.now().isoformat(timespec='seconds')}] {message}", flush=True)


def fetch_open_tasks() -> list[dict] | None:
    url = f"{CORE_APP_URL}/api/tasks"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            tasks = json.loads(response.read())
    except urllib.error.URLError as error:
        log(f"Could not reach core-app at {CORE_APP_URL}: {error}")
        return None

    return [task for task in tasks if task["status"] == "active"]


def format_date(value: str) -> str:
    return datetime.fromisoformat(value).strftime("%b %d, %Y %I:%M %p")


def next_checkpoint(task: dict) -> str:
    now = datetime.now()
    checkpoint_1 = datetime.fromisoformat(task["checkpoint_1"])
    checkpoint_2 = datetime.fromisoformat(task["checkpoint_2"])
    if now < checkpoint_1:
        return task["checkpoint_1"]
    if now < checkpoint_2:
        return task["checkpoint_2"]
    return task["buffer_deadline"]


def build_review_email(tasks: list[dict]) -> MIMEText:
    task_ids = ",".join(str(task["id"]) for task in tasks)
    subject = f"Nudge Weekly Review [ids: {task_ids}]"

    lines = ["Here are your currently open tasks:", ""]
    for task in tasks:
        lines.append(f"#{task['id']} — {task['name']}")
        lines.append(f"    Status: {task['status']}")
        lines.append(f"    Next checkpoint: {format_date(next_checkpoint(task))}")
        lines.append("")
    lines.append("Reply with the IDs of your top 3 priorities for this week.")

    message = MIMEText("\n".join(lines))
    message["Subject"] = subject
    message["From"] = FROM_ADDRESS
    message["To"] = TO_ADDRESS
    message["Message-ID"] = make_msgid()
    return message


def send_review_email(tasks: list[dict]) -> None:
    if not tasks:
        log("No open tasks — skipping weekly review email.")
        return

    message = build_review_email(tasks)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=5) as server:
            server.send_message(message)
    except OSError as error:
        log(f"Could not send weekly review email via {SMTP_HOST}:{SMTP_PORT}: {error}")
        return

    log(f"Sent weekly review email ({len(tasks)} task(s)), subject: {message['Subject']}")


def run() -> None:
    log(f"notification-worker started, polling {CORE_APP_URL} every {POLL_INTERVAL_SECONDS}s")
    last_review_sent = None

    while True:
        tasks = fetch_open_tasks()
        if tasks is not None:
            names = [task["name"] for task in tasks]
            log(f"{len(tasks)} open task(s): {names}")

            now = time.monotonic()
            if last_review_sent is None or now - last_review_sent >= REVIEW_EMAIL_INTERVAL_SECONDS:
                send_review_email(tasks)
                last_review_sent = now

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
