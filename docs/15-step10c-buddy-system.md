# Step 10c: Accountability Buddy System

**Status:** Abgeschlossen
**Bezug:** ESC-FUNC-002 (Eskalations-Filterbedingung), ESC-FUNC-004 (Buddy-Benachrichtigung bei Stufe 3), ESC-FUNC-005 (minimaler Nachrichteninhalt). Zweiter von zwei Teilen aus Schritt 10 (erster Teil: Dashboard/Eisenhower, `13-step10a-dashboard-and-eisenhower.md`; Buddy-Kontaktfeld selbst kam bereits in `14-step10b-settings.md`).

---

## Offene Frage aus `02b-eisenhower-buddy-design.md` geklärt

Der Design-Entscheid hatte bewusst offengelassen: *"Automatisch ohne Rückfrage (Alarmy-Prinzip) oder mit kurzem Zwischenschritt?"* Mit der Nutzerin abgestimmt: **automatisch, kein Zwischenschritt** (kein zusätzlicher UI-Zustand nötig) — aber mit einer wichtigen Präzisierung, die über den ursprünglichen Text hinausgeht.

**Nutzerinnen-Einwand beim Review:** Ein Alert direkt beim 75%-Checkpoint wäre zu aggressiv. Beispiel aus den Seed-Daten ("Write research proposal", externes Deadline 02.08., Buffer-Deadline 27.07., Checkpoint 1 = 19.07., Checkpoint 2 = 23.07.): Checkpoint 1 gemacht, Checkpoint 2 verpasst — heißt nicht automatisch, dass die Buffer-Deadline in Gefahr ist. Wörtlich: *"if I do 50% but miss 75% chances are good that I can still make the buffer deadline. but I'd say buffer deadline miss is a definite alert."*

**Resultierende Regel (`needs_buddy_alert()` in `models.py`):**
1. Buffer-Deadline bereits überschritten → **immer** ein Alert, unabhängig vom Checkpoint-Verlauf.
2. Sonst: Alert nur, wenn **beide** Checkpoints ohne Interaktion (Artefakt-Einreichung oder Triage-Entwurf, siehe CHKP-FUNC-004) verstrichen sind. Ein einzelner verpasster Checkpoint reicht nicht.

Das ist strenger als der ursprüngliche Design-Text ("bei Stufe 3 / 75%-Checkpoint verpasst"), aber inhaltlich näher an der eigentlichen Absicht: der Buddy soll erst einspringen, wenn die Selbstregulierung über einen längeren Zeitraum ausgeblieben ist — nicht bei einer einzelnen verpassten Gelegenheit.

### Nachtrag: Zeitfenster nachträglich verschärft

Erste Version dieser Regel hatte ein Problem, das die Nutzerin beim Review fand: das Zeitfenster für "Checkpoint 1 erfüllt" reichte von der Task-Anlage bis Checkpoint 2 — jede Interaktion in diesem gesamten Zeitraum zählte, egal wie früh. Ein Upload bei z. B. 30% hätte damit automatisch auch den 50%-Checkpoint "erfüllt", ohne dass tatsächlich zum fälligen Zeitpunkt reagiert wurde. Zusätzlich reichte das Fenster für "Checkpoint 2 erfüllt" bis zur Buffer-Deadline, was das System begrifflich mit "Buffer-Deadline verpasst" vermischte, obwohl beides technisch unabhängig geprüft wird.

**Fix:** Jeder Checkpoint bekommt ein eigenes, festes Gnadenfenster von **`CHECKPOINT_GRACE_HOURS = 24` Stunden** ab seiner eigenen Fälligkeit — unabhängig vom nächsten Checkpoint oder der Buffer-Deadline. "Verpasst" heißt jetzt konkret: keine Interaktion innerhalb `[checkpoint_zeit, checkpoint_zeit + 24h]`, und dieses Fenster ist bereits abgelaufen. Ein Upload bei 30% deckt damit nur noch sich selbst ab, nicht mehr automatisch spätere Checkpoints.

```python
CHECKPOINT_GRACE_HOURS = 24

def _checkpoint_status_from_events(checkpoint_time, events):
    now = datetime.now()
    if now < checkpoint_time:
        return "pending"
    grace_end = checkpoint_time + timedelta(hours=CHECKPOINT_GRACE_HOURS)
    if _has_check_in(events, checkpoint_time, grace_end):
        return "checked_in"
    if now < grace_end:
        return "grace"
    return "missed"

def needs_buddy_alert(task, threshold_days=URGENT_THRESHOLD_DAYS):
    if task["status"] != "active" or task["buddy_alerted"]:
        return False
    if not is_urgent(task, threshold_days):
        return False

    now = datetime.now()
    buffer_deadline = datetime.fromisoformat(task["buffer_deadline"])
    if now >= buffer_deadline:
        return True

    checkpoint_1 = datetime.fromisoformat(task["checkpoint_1"])
    checkpoint_2 = datetime.fromisoformat(task["checkpoint_2"])
    if now < checkpoint_2 + timedelta(hours=CHECKPOINT_GRACE_HOURS):
        return False  # checkpoint 2's own grace window hasn't closed yet

    events = get_task_events(task["id"])
    checkpoint_1_missed = _checkpoint_status_from_events(checkpoint_1, events) == "missed"
    checkpoint_2_missed = _checkpoint_status_from_events(checkpoint_2, events) == "missed"
    return checkpoint_1_missed and checkpoint_2_missed
```

`_checkpoint_status_from_events()` returns one of four states (`pending`, `checked_in`, `grace`, `missed`), reused both for the alert decision and for the single-task-view indicator below — one function, two consumers, no duplicated windowing logic. `CHECKPOINT_GRACE_HOURS` is a hardcoded constant for now (same pattern `URGENT_THRESHOLD_DAYS` started as before it got a Settings field in Schritt 10b) — not exposed in Settings yet, since the buddy system as a whole is still Should-priority.

## Warum "missed" aus `task_events` berechnet wird, nicht aus einem neuen Feld

Es gibt kein "Checkpoint 1 erledigt"-Flag im Datenmodell — nur die generischen `task_events` (`artifact_submitted`, `triage_draft_sent`, ...) mit Zeitstempel. Statt ein neues Schema-Feld pro Checkpoint einzuführen, wird "verpasst" als reine Funktion aus vorhandenen Daten berechnet — gleiches Prinzip wie `is_urgent()`/`is_checkpoint_due()` (ESC-FUNC-001: "berechneter, nicht manuell gesetzter Zustand"). Die teure `get_task_events()`-Abfrage in `needs_buddy_alert()` läuft erst, nachdem die billigen Vorprüfungen (Status, `buddy_alerted`, `is_urgent`, Buffer-Deadline, Checkpoint-2-Gnadenfenster) den Task bereits als echten Kandidaten bestätigt haben — kein unnötiger N+1-Overhead für die Mehrheit der Tasks, die gar nicht in der Nähe der Eskalation sind.

## Checkpoint-Status auf der Task-Detail-Seite

Zweiter Nachtrag aus dem Review: auf einen Blick sichtbar machen, ob ein Checkpoint erfüllt wurde. `checkpoint_check_in_status(task, checkpoint_number)` (dieselbe Zustandsmaschine wie oben) wird in der `task_detail`-Route berechnet und in `task_detail.html` als kleines Icon neben dem jeweiligen Checkpoint-Label gerendert: grüner Haken (`check_circle`, erfüllt), gelbe Uhr (`schedule`, noch im Gnadenfenster), rotes Kreuz (`cancel`, verpasst), kein Icon (noch nicht fällig).

## ESC-FUNC-002: kein "Important"-Feld, also reines Urgent-Gate

Wie in `13-step10a-dashboard-and-eisenhower.md` entschieden, gibt es kein separates "Important"-Feld — jeder existierende Task ist per Definition bereits committet. Die Eskalationskette wird also allein durch `is_urgent()` plus die Checkpoint-Miss-Regel oben gegatet, nicht durch ein "Important + Urgent"-Kreuzprodukt. Konsistente Fortsetzung der Schritt-10a-Entscheidung, kein neuer Bruch.

## Wo die Logik liegt: Kern-App entscheidet, Worker führt aus

`needs_buddy_alert()` lebt in `core-app/models.py`, nicht im Worker — der Worker hat keine eigene DB und sieht `task_events` nie direkt (REVIEW-FUNC-002: reines REST-Polling). `GET /api/tasks` reichert jeden Task serverseitig um das Flag `needs_buddy_alert` an (`app.py`, gleiches Muster wie die bereits bestehende `urgent_tasks`/`not_urgent_tasks`-Gruppierung in der `/tasks`-Route):

```python
@app.route("/api/tasks", methods=["GET"])
def api_list_tasks():
    threshold = g.settings["urgent_threshold_days"]
    tasks = get_all_tasks()
    for task in tasks:
        task["needs_buddy_alert"] = needs_buddy_alert(task, threshold)
    return jsonify(tasks)
```

Der Worker (`notification-worker/worker.py`) macht reines I/O: filtert auf `needs_buddy_alert=True`, verschickt die Mail per SMTP, meldet den Versand zurück. Keine Geschäftslogik-Duplikation zwischen den beiden Prozessen — Kern-App bleibt alleinige Quelle der Wahrheit für "ist dieser Task eskalationswürdig".

## Persistenz gegen doppelten Versand: `buddy_alerted`

Der Worker pollt alle 30s — ohne einen persistenten Zustand würde derselbe Task bei jedem Zyklus erneut alarmiert. Anders als `is_urgent()`/`needs_buddy_alert()` selbst ist "wurde bereits benachrichtigt" aber keine reine Funktion der aktuellen Zeit — es ist ein historisches Faktum, das gespeichert werden muss (gleiches Muster wie das bereits bestehende `is_focus_task`-Flag aus Schritt 8, kein Bruch mit der "berechnet, nicht gespeichert"-Regel, die nur für zeitabhängige Zustände gilt).

- Neue Spalte `tasks.buddy_alerted` (Default 0).
- Neuer Endpoint `POST /api/tasks/<id>/buddy-alert`: setzt `buddy_alerted = 1` und schreibt einen `task_events`-Eintrag ("Buddy notified: task needs attention") — erscheint automatisch in der bestehenden Activity-Timeline auf der Task-Detail-Seite, ohne Template-Änderung.
- `update_task_status()` setzt `buddy_alerted` bei jedem Statuswechsel zurück auf 0 — ein wiedereröffneter oder fortgesetzter Task startet mit frischem Eskalationszustand. Sonst könnte ein einmal alarmierter Task nach "Resume" nie wieder alarmiert werden, selbst wenn er erneut in Verzug gerät.

## ESC-FUNC-005: minimaler Inhalt

```python
def build_buddy_alert_email(task, settings):
    subject = f"Nudge Buddy Alert: {task['name']}"
    greeting = f"Hi {settings['buddy_name']},\n\n" if settings.get("buddy_name") else ""
    message = MIMEText(f"{greeting}{task['name']} needs attention.\n")
    ...
```

Betreff und Text enthalten nur den Task-Namen — kein Deadline, kein Status, keine Historie. Deckt sich mit der Datensparsamkeits-Vorgabe aus `02b-eisenhower-buddy-design.md`.

## Verifikation

Manuell gegen Mailpit getestet (Kern-App, Worker und Mailpit lokal gestartet, Buddy-E-Mail über `/settings` gesetzt), zwei Runden — erste Runde mit der ursprünglichen breiten Fensterlogik, zweite Runde nach der Verschärfung:

**Erste Runde (breite Fenster, vor dem Nachtrag):**
1. "Fix login bug" (Buffer-Deadline bereits überschritten) und "Prepare oral exam slides" (beide Checkpoints ohne Interaktion verstrichen) lösten beim ersten Poll-Zyklus je einen Alert aus, sichtbar in Mailpit (`Nudge Buddy Alert: Fix login bug` / `... Prepare oral exam slides`, Empfänger = Buddy-Adresse, Inhalt exakt wie oben).
2. Kein Doppelversand im zweiten Poll-Zyklus (30s später) — `buddy_alerted` korrekt auf 1, Activity-Timeline zeigt den Eintrag.
3. Ad-hoc-Testtask mit Checkpoint 1 erfüllt / Checkpoint 2 verpasst / Buffer-Deadline noch offen: `needs_buddy_alert` korrekt `False` — bestätigt die Grundregel, dass ein einzelner verpasster Checkpoint keinen Alert auslöst.
4. Gleicher Testtask, Buffer-Deadline künstlich in die Vergangenheit verschoben: `needs_buddy_alert` sofort `True` — bestätigt den bedingungslosen Override.

**Zweite Runde (nach der 24h-Gnadenfenster-Verschärfung, gegen frisch geseedete Daten):**
5. "Fix login bug" (Buffer-Deadline längst überschritten) weiterhin `needs_buddy_alert = True` — Override funktioniert unverändert unabhängig vom Gnadenfenster.
6. "Prepare oral exam slides" (Checkpoint 2 erst vor ca. 8h fällig geworden) jetzt korrekt `needs_buddy_alert = False`, weil das 24h-Gnadenfenster für Checkpoint 2 noch nicht abgelaufen ist — genau der Unterschied, den die Verschärfung bewirken sollte (vorher hätte dieselbe Konstellation sofort gefeuert).
7. Task-Detail-Ansicht für alle vier Zustände geprüft: `pending` (kein Icon, "Write research proposal", Checkpoints noch nicht fällig), `missed` (rotes Kreuz, "Fix login bug", beide Checkpoints), `grace` (gelbe Uhr, "Prepare oral exam slides" Checkpoint 2), `checked_in` (grüner Haken, Ad-hoc-Event innerhalb des Checkpoint-1-Gnadenfensters von "Fix login bug" eingefügt) — alle vier rendern das erwartete Icon.
8. Mit demselben Ad-hoc-Check-in-Event (Checkpoint 1 jetzt "checked_in") blieb `needs_buddy_alert` für "Fix login bug" weiterhin `True`, weil die Buffer-Deadline bereits überschritten ist — bestätigt, dass der Override Vorrang vor dem Checkpoint-Status hat.
9. Alle Testtasks/-events wieder entfernt, Datenbank mit `seed_data.py` neu geseedet für einen sauberen Zustand.

## Nächster Schritt

Kein weiterer Schritt in der ursprünglichen Schritt-10-Aufteilung offen (10a Dashboard/Eisenhower, 10b Settings, 10c Buddy-System — alle drei abgeschlossen). Verbleibende, bewusst zurückgestellte Punkte stehen in `backlog.md` (u. a. Sortier-/Gruppier-Toolbar für All-Tasks, jetzt freigegeben, da 10c abgeschlossen ist).
