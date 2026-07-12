# 5.6 Terra Audit — Future Implementation Plan

**Status:** Post-MVP audit  
**Purpose:** Records the improvements deliberately left outside the university MVP. These are not defects that prevent the local demonstration; they are the next implementation steps required before Nudge could be used as a persistent, multi-user, or internet-facing product.

---

## Audit result at a glance

Nudge meets its MVP goal: a solo, ADHD-friendly task/checkpoint manager with a separate notification worker that communicates with the core app over REST. The audit found no blocker for a local university demonstration.

The main future work falls into four areas:

1. **Submission evidence and documentation consistency** — make the delivered GitHub repository self-contained and accurate.
2. **Reliability of background notifications** — avoid duplicated emails or reprocessed replies after restarts.
3. **Security and input validation** — required before exposing Nudge beyond a trusted local machine.
4. **Automated tests and product polish** — make future changes safe and improve the user experience.

---

## Priority 1 — Complete before submission / final repository hand-in

| Item | Finding | Future implementation | Why it matters |
|---|---|---|---|
| Commit evidence files | `google_stitch_prompts.txt` and `docs/how-to-run-and-test-locally.md` were untracked during the audit. | Add and commit them so they appear in GitHub. | The Stitch prompts are direct evidence for Part A; the local test guide documents reproducibility. |
| Clarify task-date overrides | The data/API layer accepts custom buffer/checkpoint values, but the visible Add Task form currently only asks for name and external deadline. | Either add an “Advanced dates” section to the GUI or state clearly in the report that overrides are API-supported in the MVP. | Keeps the requirements checklist aligned with the actual user interface. |
| Correct stale terminology | Some step documentation still names previous JSON routes and calls the timed loop a “Cron trigger.” The mail receiver is POP3 for Mailpit testing, not IMAP. | Update the affected Markdown files to match `/api/...`, “polling loop,” and the documented POP3 substitution. | Clear technical language is part of proving that the implementation is understood. |
| Capture visual process proof | The repository contains a detailed text transcript of process independence, but no screenshot/GIF. | Record a 2–3 minute screen capture: core app works alone; worker survives core-app shutdown; worker reconnects after restart. | Provides especially strong evidence for Part C. |

---

## Priority 2 — Reliability improvements

| Item | Current limitation | Future implementation |
|---|---|---|
| Persistent worker state | Processed POP3 message IDs and the time of the last weekly review are only held in memory. Restarting the worker can resend a review or process an old reply again. | Store processed message IDs and the last successful review timestamp in SQLite (or a small worker-owned state file). |
| Idempotent buddy alerts | The worker sends an alert first and then marks it sent through the API. If the write-back fails after SMTP succeeds, the next poll can send a duplicate. | Create an idempotency key / “alert pending” state in the core app and make the send-and-record sequence recoverable. |
| Configurable runtime settings | Worker URL, polling interval, POP3 settings, and test credentials are constants in source code. | Read non-secret values from environment variables or a configuration file; keep secrets out of source control. |
| Worker health check | Only the core app has `/health`; the worker is verified through logs. | Add a lightweight worker status endpoint or heartbeat file/record if operational monitoring becomes necessary. |
| Time-zone-aware dates | Timestamps use naive local `datetime` values. | Store timezone-aware UTC timestamps and convert only for display. |

---

## Priority 3 — Security and data protection (required before real deployment)

| Item | Current limitation | Future implementation |
|---|---|---|
| Authentication and authorization | Any local caller can use the API and change focus tasks or mark buddy alerts. | Add a single-user login/session for a hosted version and require a service token for worker API calls. |
| CSRF protection | HTML forms do not include CSRF tokens. | Use Flask-WTF or equivalent token validation for every state-changing browser form. |
| Server-side validation | Several routes trust form/JSON values; invalid dates, unknown statuses, or malformed payloads can cause errors or inconsistent data. | Validate schemas, enforce an allowed status set, check checkpoint ordering, and return helpful 400 responses. |
| Upload controls | Attachments have no allow-list, size limit, malware scan, or storage quota. | Add file-size/type limits, safe download headers, a quota, and malware scanning if files are stored outside a trusted local machine. |
| Email credentials and transport | Local Mailpit uses development credentials and plain local SMTP/POP3. | Use environment-managed credentials, TLS, and a real authenticated mail provider for deployment. |
| Privacy lifecycle | There is no retention, export, or deletion workflow for tasks, event history, settings, and attachments. | Add data export, task/archive deletion, attachment cleanup, and a privacy policy before collecting real personal data. |

---

## Priority 4 — Testing and maintainability

| Item | Future implementation |
|---|---|
| Automated tests | Add unit tests for buffer/checkpoint calculations, checkpoint grace windows, escalation rules, reply parsing, and attachment handling. |
| API integration tests | Test valid and invalid JSON payloads, unknown task IDs, status transitions, focus-task write-back, and worker/core-app outage recovery. |
| Dependency reproducibility | Pin Flask to a tested version and add a short `requirements`/environment setup verification step. |
| Structured logging | Replace print-only logs with structured levels and include task/message IDs in worker operations. |
| Database migrations | Introduce a migration mechanism before changing the SQLite schema after users have real task data. |

---

## Priority 5 — Product enhancements (post-MVP)

| Item | Value for Nudge |
|---|---|
| Daily focus-task digest | Implements the planned reminder loop only for committed focus tasks, preventing notification overload. |
| Early re-prioritisation | Offers a new weekly selection when all focus tasks are completed early. |
| Per-task urgency settings | Lets users treat genuinely high-stakes tasks differently without globally increasing stress. |
| Editable task dates | Lets a user revise an external deadline or checkpoint plan after circumstances change. |
| Accessible UI review | Add keyboard navigation, explicit labels, contrast checks, and screen-reader testing. |
| Backup/export | Provide an exportable JSON/CSV backup and straightforward restore workflow. |

---

## Suggested report wording

> The Terra Audit confirms that the MVP is fit for a local demonstration and fulfills the intended separation between the core application and notification worker. The remaining work was deliberately prioritised rather than hidden: repository evidence and documentation should be finalised before submission; persistent worker state, idempotent notifications, authentication, validation, and upload controls are required before a real deployment; and automated tests plus additional ADHD-friendly reminders form the planned post-MVP roadmap. This separation demonstrates conscious scope management rather than an unfinished core feature set.

