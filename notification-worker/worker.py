import json
import time
import urllib.error
import urllib.request
from datetime import datetime

CORE_APP_URL = "http://127.0.0.1:3000"
POLL_INTERVAL_SECONDS = 30


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


def run() -> None:
    log(f"notification-worker started, polling {CORE_APP_URL} every {POLL_INTERVAL_SECONDS}s")
    while True:
        tasks = fetch_open_tasks()
        if tasks is not None:
            names = [task["name"] for task in tasks]
            log(f"{len(tasks)} open task(s): {names}")
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
