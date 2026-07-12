import email
import email.policy
import json
import poplib
import re
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

# Mailpit has no IMAP server (confirmed via `mailpit --help`) — only SMTP,
# POP3, and its own REST API. REVIEW-FUNC-004/REVIEW-NFR-001 name IMAP
# specifically, but poplib is the closest available stdlib equivalent that
# still talks a real mail-retrieval protocol to a real server rather than a
# REST mock. See docs/how-to-run-and-test-locally.md for how to enable
# Mailpit's POP3 server with matching credentials.
POP3_HOST = "localhost"
POP3_PORT = 1110
POP3_USERNAME = "nudge"
POP3_PASSWORD = "nudge-local-test"

REVIEW_SUBJECT_PATTERN = re.compile(r"Nudge Weekly Review \[ids: ([\d,]+)\]")
TOP_PRIORITY_COUNT = 3

processed_reply_uids: set[str] = set()


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


TASKS_PER_BLOCK = 5


def build_review_email(tasks: list[dict]) -> MIMEText:
    task_ids = ",".join(str(task["id"]) for task in tasks)
    subject = f"Nudge Weekly Review [ids: {task_ids}]"

    # tasks arrive sorted by urgency (core-app orders /api/tasks by buffer
    # deadline), so grouping them in fixed-size blocks as-is means each
    # block is also roughly a tier of urgency, not an arbitrary chunk.
    lines = ["Here are your currently open tasks:", ""]
    for index, task in enumerate(tasks):
        if index > 0 and index % TASKS_PER_BLOCK == 0:
            lines.append("-" * 30)
            lines.append("")
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


def parse_top_priorities(body: str, valid_ids: set[int]) -> list[int]:
    priorities: list[int] = []
    for match in re.finditer(r"#?\b(\d+)\b", body):
        candidate = int(match.group(1))
        if candidate in valid_ids and candidate not in priorities:
            priorities.append(candidate)
        if len(priorities) == TOP_PRIORITY_COUNT:
            break
    return priorities


def check_for_replies() -> None:
    try:
        conn = poplib.POP3(POP3_HOST, POP3_PORT, timeout=5)
        conn.user(POP3_USERNAME)
        conn.pass_(POP3_PASSWORD)
    except (OSError, poplib.error_proto) as error:
        log(f"Could not check for replies via POP3 at {POP3_HOST}:{POP3_PORT}: {error}")
        return

    try:
        _, uidl_lines, _ = conn.uidl()
        for line in uidl_lines:
            msg_num_str, uid = line.decode().split(" ", 1)
            if uid in processed_reply_uids:
                continue
            msg_num = int(msg_num_str)

            # REVIEW-FUNC-004: only ever act on replies to our own
            # referenced thread — TOP fetches headers only (0 body lines)
            # so we can check the subject before pulling the full message.
            _, header_lines, _ = conn.top(msg_num, 0)
            headers = email.message_from_bytes(
                b"\r\n".join(header_lines), policy=email.policy.default
            )
            subject = headers.get("Subject", "")

            # Mailpit catches everything the worker sends AND receives in
            # one shared mailbox (no separate "Sent" folder like a real
            # account), so the review email we just sent would otherwise
            # match its own reference pattern. Requiring "Re:" is what
            # actually distinguishes an incoming reply from our own
            # outgoing message in this local setup.
            is_reply = subject.strip().lower().startswith("re:")
            match = REVIEW_SUBJECT_PATTERN.search(subject)
            if not is_reply or not match:
                processed_reply_uids.add(uid)
                continue

            valid_ids = {int(x) for x in match.group(1).split(",")}

            _, full_lines, _ = conn.retr(msg_num)
            full_message = email.message_from_bytes(
                b"\r\n".join(full_lines), policy=email.policy.default
            )
            body_part = full_message.get_body(preferencelist=("plain",))
            body_text = body_part.get_content() if body_part else ""

            priorities = parse_top_priorities(body_text, valid_ids)
            processed_reply_uids.add(uid)

            if priorities:
                log(f"Reply to '{subject}' parsed top priorities: {priorities}")
            else:
                log(f"Reply to '{subject}' matched but no valid task IDs found in the body")
    finally:
        conn.quit()


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

        check_for_replies()
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
