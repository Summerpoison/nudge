# How To: Run and Test Nudge Locally

Reference guide for manually exercising everything built so far (Schritte 1–6). Update this as new features land — it's meant to stay current, not a one-time step record like the numbered docs.

---

## 1. Start all three processes

Three separate terminals, since Teil B (`core-app`) and Teil C (`notification-worker`) are independent processes by design, plus Mailpit as the local SMTP catcher.

**Terminal 1 — core-app:**
```powershell
cd D:\xampp\htdocs\nudge\core-app
.venv\Scripts\python.exe app.py
```
→ `http://127.0.0.1:3000`

**Terminal 2 — notification-worker:**
```powershell
cd D:\xampp\htdocs\nudge\notification-worker
.venv\Scripts\python.exe worker.py
```
→ polls core-app every 30s, sends the review email every 60s (test-only interval — see note below)

**Terminal 3 — Mailpit:**
POP3 must be explicitly enabled (off by default) for Step 7's reply-checking to work — it needs a plain `username:password` auth file matching `worker.py`'s `POP3_USERNAME`/`POP3_PASSWORD` constants:
```powershell
"nudge:nudge-local-test" | Out-File -Encoding ascii C:\path\to\pop3-auth.txt
mailpit --pop3-auth-file C:\path\to\pop3-auth.txt
```
(if the `mailpit` command isn't found, your shell hasn't picked up the PATH change yet — use the full path: `C:\Users\Summer\AppData\Local\Microsoft\WinGet\Packages\axllent.mailpit_Microsoft.Winget.Source_8wekyb3d8bbwe\mailpit.exe`)
→ SMTP catcher on port `1025`, POP3 on port `1110`, web UI at `http://localhost:8025`. Without `--pop3-auth-file`, Mailpit only starts SMTP + the web UI — the worker's reply-checking will log a connection-refused error every cycle.

You don't strictly need all three running to test core-app's UI — only the worker and Mailpit steps below need them.

**Want a ready-made test dataset instead of creating tasks by hand every time?**
```powershell
cd D:\xampp\htdocs\nudge\core-app
.venv\Scripts\python.exe seed_data.py
```
Wipes `nudge.db` and `uploads\` and repopulates 5 tasks covering every state the UI shows: plain active, checkpoint-reached, on-hold, done (with a sample attachment), and a focus task. Safe to re-run any time — both are gitignored throwaway artifacts, never real data.

---

## 2. Core-app walkthrough (Teil B — Checkpoint system)

- **Dashboard** — `http://127.0.0.1:3000/`
  Shows the one active task with the nearest checkpoint, plus a short list of the rest. Empty state if you have no active tasks yet.

- **All Tasks + Add Task** — `http://127.0.0.1:3000/tasks`
  Create a task here (name + deadline). Check it appears in the list with a status badge and buffer deadline.

- **Task Detail** — click any task
  - Verify the four computed dates make sense: external deadline, buffer deadline (70% of the way there), checkpoint 1 (50%) and checkpoint 2 (75%) — both between creation and the buffer deadline, not the external deadline.
  - Buffer progress bar should be near 0% for a freshly created task.
  - "Check In" button: outline style normally, switches to filled "Checkpoint reached — Check In" once `now` passes checkpoint 1 or 2.

- **Check-in screen** — click "Check In"
  - **Submit Proof**: choose a file, submit. Confirm it shows up under Attachments on the task detail page and gets a line in the Activity log. Click the filename to confirm it opens/downloads. Try the delete (trash) icon too.
  - **I'm Blocked** → goes to the Triage screen.

- **Triage screen**
  - **Start 10-Minute Timer**: redirects to a countdown page, ticks down live. Status should stay `active`, Activity log gets a "Started a 10-minute focus timer" entry.
  - **Stuck / Waiting / Scope-deadline**: clicking one reveals a prefilled draft (recipient blank, subject/body templated from the task name). Fill in any recipient email, click "Send & Pause Task".
    **Important:** this opens your **real default mail client** via a `mailto:` link — not Mailpit. That's intentional (`CHKP-FUNC-008`): blocker drafts are a person-to-person email Nudge never touches, completely separate from the worker's weekly review email in section 3 below. Don't be surprised if Outlook/Mail/etc. pops up.
  - Confirm the task's status flips to `On Hold` and a "Resume Task" button appears on its detail page.

- **Status actions** on the task detail page: "Mark Complete" → "Reopen Task", "Resume Task" for on-hold tasks. Each should log an Activity entry and update the status badge.

---

## 3. Notification-worker + Mailpit walkthrough (Teil C — Weekly review)

1. With all three processes running and at least one active task, watch **Terminal 2** — you should see log lines like:
   ```
   [...] N open task(s): [...]
   [...] Sent weekly review email (N task(s)), subject: Nudge Weekly Review [ids: ...]
   ```
2. Open `http://localhost:8025` (Mailpit's web UI) in a browser and open that email.
   - Subject contains the task IDs (the "unique reference" for later reply-matching).
   - Body lists every open task, sorted soonest-checkpoint-first, in blocks of 5 separated by a divider line if you have more than 5.
3. **Process-independence check:** stop core-app (Ctrl+C in Terminal 1). Watch Terminal 2 — the worker should log a connection error on its next poll but keep running, not crash. Restart core-app; the worker reconnects on its own next cycle, no restart needed.
4. Similarly, you can stop Mailpit and confirm the worker logs an SMTP error instead of crashing when it tries to send.
5. **Reply-parsing (Step 7):** since there's no real inbox to reply from, simulate one — send an email via Python matching the pattern below (adjust the IDs to whatever your last review email actually referenced, visible in its subject in Mailpit's UI):
   ```powershell
   python -c "
   import smtplib
   from email.mime.text import MIMEText
   msg = MIMEText('I think #2 and #1 are the priorities this week.')
   msg['Subject'] = 'Re: Nudge Weekly Review [ids: 2,1,3]'
   msg['From'] = 'user@localhost'
   msg['To'] = 'nudge@localhost'
   with smtplib.SMTP('localhost', 1025) as s:
       s.send_message(msg)
   "
   ```
   Watch Terminal 2 for `Reply to '...' parsed top priorities: [2, 1]` on the next poll cycle. Try an unrelated subject too (no `Re:` prefix, or a totally different subject) and confirm it's silently ignored — no log line at all, since the worker never acts on anything outside its own referenced thread (`REVIEW-FUNC-004`).

---

## 4. Shutting down

`Ctrl+C` in each terminal. One quirk worth knowing: core-app runs with `debug=True`, and Flask's auto-reloader spawns a child process — `Ctrl+C` in the terminal should take both down together, but if you ever kill it via Task Manager instead, look for **two** `python.exe` entries under `core-app` (and, separately, the worker sometimes shows as two processes too — a Git-Bash/Windows quirk, harmless).

---

## Useful resets

- **Fresh database:** delete `core-app\nudge.db` (recreated automatically on next `app.py` start).
- **Fresh uploads:** delete the `core-app\uploads\` folder.
- **Faster/slower worker cadence:** `POLL_INTERVAL_SECONDS` and `REVIEW_EMAIL_INTERVAL_SECONDS` at the top of `notification-worker\worker.py`. The 60s review-email interval is a stand-in for "weekly" — fine for local testing, would need to become a real weekly duration for actual use.
