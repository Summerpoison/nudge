# Step 6: E-Mail-Versand und Mailpit-Anbindung

**Status:** Abgeschlossen
**Bezug:** REVIEW-FUNC-003. Setzt Mailpit voraus (siehe `00-tooling-and-process-independence.md`, Abschnitt 2 — in dieser Session lokal installiert, siehe unten).

---

## Mailpit-Installation

Lokal per `winget install axllent.mailpit` installiert (offizielles Paket des Mailpit-Maintainers, MIT-lizenziert, Quelle `github.com/axllent/mailpit`). Startet zwei Dienste:
- SMTP-Fänger auf Port `1025` (kein Auth, keine Verschlüsselung — reines lokales Test-Setup)
- Web-UI/API auf Port `8025` (`http://localhost:8025`)

Start: `mailpit` (nach Neustart der Shell, damit die PATH-Änderung greift) oder direkt über den vollen Pfad unter `%LOCALAPPDATA%\Microsoft\WinGet\Packages\axllent.mailpit_...\mailpit.exe`.

## Was gebaut wurde

`notification-worker/worker.py` erweitert um:

```python
SMTP_HOST = "localhost"
SMTP_PORT = 1025
FROM_ADDRESS = "nudge@localhost"
TO_ADDRESS = "user@localhost"
REVIEW_EMAIL_INTERVAL_SECONDS = 60  # steht für "wöchentlich" im lokalen Testbetrieb


def build_review_email(tasks: list[dict]) -> MIMEText:
    task_ids = ",".join(str(task["id"]) for task in tasks)
    subject = f"Nudge Weekly Review [ids: {task_ids}]"
    ...
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
```

### Eindeutige Referenz (REVIEW-FUNC-003)

Die Anforderung erlaubt explizit zwei Varianten ("Message-ID **oder** Task-IDs im Betreff") — beide wurden umgesetzt:
- **Task-IDs im Betreff** (`Nudge Weekly Review [ids: 2,1]`) ist die Variante, auf der die spätere Antwort-Zuordnung in Schritt 7 aufbauen wird — ein einfacher String-Match auf den Betreff ist robuster gegenüber Mailpits API (die eher auf Volltext-/Metadatensuche ausgelegt ist als auf klassisches IMAP-Header-Threading) und einfacher in der Prüfung zu erklären als E-Mail-Threading-Header.
- **`Message-ID`-Header** wird zusätzlich korrekt über `email.utils.make_msgid()` gesetzt (Python fügt diesen Header sonst nicht automatisch hinzu) — technisch korrekter E-Mail-Aufbau, auch wenn die eigentliche Zuordnung über die Betreffzeile läuft.

### "Alle offenen Tasks" und Checkpoint-Datum

Wiederverwendung derselben Filterlogik wie in Schritt 5 (`status == "active"`, siehe dortige Dokumentation zur "Fokus-Tasks kommen erst in Schritt 8"-Entscheidung). Für "Checkpoint-Datum" wird der jeweils **nächste noch nicht erreichte** Termin gezeigt (`next_checkpoint()`: Checkpoint 1, sonst Checkpoint 2, sonst die Buffer-Deadline) — bewusst dupliziert statt aus `core-app` importiert, weil der Worker als komplett eigenständiger Prozess ausschließlich über HTTP mit der Kern-App spricht (kein gemeinsames Python-Modul zwischen den Prozessen — unterstreicht die Prozess-Unabhängigkeit auch auf Code-Ebene, siehe `00-tooling-and-process-independence.md`).

### Sende-Rhythmus getrennt vom Polling

Der Worker pollt weiterhin alle 30s (Schritt 5), verschickt die Review-Mail aber nur, wenn seit dem letzten Versand mindestens `REVIEW_EMAIL_INTERVAL_SECONDS` vergangen sind (in-memory-Zeitstempel `last_review_sent`, verglichen über `time.monotonic()`). Der Wert steht für die im Original-Spec beschriebene "wöchentliche" Kadenz — für den lokalen Testbetrieb auf 60s statt einer Woche gesetzt, damit sich das Verhalten in angemessener Zeit beobachten lässt. Kein Missbrauch von `time.sleep()`-Wartezeiten für eine "echte" Woche in Tests.

### Fehlerbehandlung

Ein nicht erreichbares Mailpit (z. B. SMTP-Server nicht gestartet) wird als `OSError` abgefangen und geloggt, ohne den Worker-Prozess zum Absturz zu bringen — dieselbe Resilienz-Idee wie bei der Kern-App-Erreichbarkeit in Schritt 5, hier auf eine dritte, externe Abhängigkeit (den Mail-Server) angewendet.

### Gefundener und behobener Encoding-Bug

Beim Testen fiel auf, dass Log-Zeilen mit Sonderzeichen (Halbgeviertstrich `—`) in der umgeleiteten Log-Datei als `�` erschienen. Ursache: Python nutzt für `stdout` unter Windows standardmäßig die System-Codepage (hier `cp1252`) statt UTF-8, sobald die Ausgabe nicht an ein Terminal, sondern in eine Datei umgeleitet wird — der `—`-Charakter landete dadurch als Einzelbyte `0x97` (cp1252) statt als korrekte 3-Byte-UTF-8-Sequenz (`E2 80 94`) in der Datei. Behoben mit `sys.stdout.reconfigure(encoding="utf-8")` direkt nach den Imports. **Wichtig:** Betraf ausschließlich die lokalen Konsolen-Logs des Workers, nicht die tatsächlich versendeten E-Mails — Pythons `email`-Modul kodiert den Nachrichtentext unabhängig von der Konsolen-Codepage korrekt (im Mailpit-Test vor der Korrektur bereits als korrektes UTF-8 verifiziert).

## Verifikation

Vollständiger lokaler Testlauf mit allen drei Prozessen (core-app, notification-worker, Mailpit):

1. Zwei Test-Tasks angelegt, Worker gestartet → erste Review-Mail sofort verschickt (`Nudge Weekly Review [ids: 2,1]`), in Mailpit per API abgerufen und inhaltlich geprüft: korrekte Task-Liste mit ID, Status, nächstem Checkpoint-Datum, korrekt gesetzter `Message-ID`-Header.
2. Zweiter Poll-Zyklus (30s später, insgesamt 30s seit letztem Versand) → **kein** erneuter Versand (Intervall-Sperre funktioniert, Mailpit-Nachrichtenzahl bleibt bei 1).
3. Dritter Poll-Zyklus (60s seit letztem Versand) → erneuter Versand, Mailpit-Nachrichtenzahl steigt auf 2.
4. Mailpit-Prozess beendet, während core-app und Worker weiterlaufen → nächster Versand-Versuch loggt sauber `Could not send weekly review email via localhost:1025: [WinError 10061] ...`, Worker-Prozess läuft unverändert weiter.
5. Beide Test-Tasks auf `done` gesetzt → nächster Zyklus loggt `0 open task(s)` und `No open tasks — skipping weekly review email.` statt eine leere Mail zu verschicken.
6. Encoding-Fix angewendet, Prozesse neu gestartet, derselbe Skip-Fall erneut ausgelöst → Log-Datei enthält jetzt die korrekten UTF-8-Bytes für den Halbgeviertstrich (per `od -c` gegen die Rohbytes verifiziert, nicht nur visuell).

Alle Prozesse (core-app, Worker, Mailpit) danach gestoppt, Testdatenbank gelöscht.

## Nachtrag aus der Nutzerinnen-Review: Skalierung bei vielen offenen Tasks

**Aufgeworfen:** `build_review_email()` hatte keine Obergrenze — bei 20+ offenen Tasks würde die Mail zu einer unübersichtlichen Textwand. Vorschlag der Nutzerin: nur Tasks mit Deadline in den nächsten 14 Tagen, bei mehr als 10 nur die 10 dringendsten, in Fünferblöcken.

**Analyse:** REVIEW-FUNC-003 verlangt wörtlich "eine E-Mail mit **allen** offenen Tasks" (Must). Das Original-Spec (`adhd-proof-workflow-spec_v2.md`, Modul 4) begründet das explizit: *"Lists all open tasks... makes the invisible visible... You reply with your top 3 priorities... The system doesn't let you say 'all of them.'"* Der Überlastungsschutz ist im Design bewusst auf die **Antwort** verlagert (Zwang zur Wahl von genau 3), nicht auf die Anzeige — vollständige Sichtbarkeit ist hier der Punkt, nicht ein Nebeneffekt. Ein stiller Cutoff bei 10 Tasks würde sowohl vom Anforderungstext als auch von dieser Design-Begründung abweichen.

**Entscheidung (mit Nutzerin abgestimmt):** Weiterhin **alle** offenen Tasks auflisten, aber lesbarer formatieren:
- Tasks erscheinen bereits nach Dringlichkeit sortiert (`/api/tasks` ordnet nach Buffer-Deadline, diese Reihenfolge bleibt durch den Listen-Filter in `fetch_open_tasks()` erhalten).
- Neue Konstante `TASKS_PER_BLOCK = 5`: nach jeweils 5 Tasks wird eine Trennlinie (`---...`) eingefügt — rein visuelle Gliederung, keine Task fällt weg. Getestet mit 12 Tasks: korrekte Blöcke 5/5/2, durchgehend nach Dringlichkeit sortiert.

**Zurückgestellter Alternativvorschlag (für später, falls sich in der Praxis ein echtes Bedürfnis zeigt):** 14-Tage-Fenster + Cap bei 10 dringendsten Tasks, wie ursprünglich vorgeschlagen. Nutzerin vermutet, dass sich dieses Muster im echten Gebrauch von selbst ergeben könnte (z. B. durch manuelles Filtern/Ignorieren weit entfernter Tasks) und dass die geplante "deadline-lose Tasks"-Erweiterung (siehe `05-step2-task-model.md`, Abschnitt "Scope-Frage während Review") die Größe der aktiven Task-Liste ohnehin reduzieren dürfte, sobald Backlog-Einträge nicht mehr als reguläre Tasks mitgezählt werden. Explizit als möglicher späterer Anforderungs-Change festgehalten, kein aktueller Widerspruch zu REVIEW-FUNC-003.

## Nächster Schritt

Schritt 7: Regelbasiertes Reply-Parsing (REVIEW-FUNC-004, 005) — der Worker fragt per IMAP/POP3 gezielt nach Antworten auf die referenzierte Mail und extrahiert die Top-3-Priorisierung aus der Antwort.
