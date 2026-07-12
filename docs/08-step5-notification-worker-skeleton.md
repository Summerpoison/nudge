# Step 5: Notification-Worker-Grundgerüst (Teil C, Start)

**Status:** Abgeschlossen
**Bezug:** REVIEW-FUNC-001, REVIEW-FUNC-002. Ab hier beginnt Teil C (verteiltes System, siehe `00-tooling-and-process-independence.md`).

---

## Was gebaut wurde

```
notification-worker/
├── worker.py           eigenständiger Prozess, pollt die Kern-App-API periodisch
├── requirements.txt    aktuell leer (keine externen Abhängigkeiten nötig)
└── .venv/                eigene virtuelle Umgebung, getrennt von core-app/.venv
```

### `worker.py`

```python
CORE_APP_URL = "http://127.0.0.1:3000"
POLL_INTERVAL_SECONDS = 30


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
            log(f"{len(tasks)} open task(s): {[t['name'] for t in tasks]}")
        time.sleep(POLL_INTERVAL_SECONDS)
```

- **HTTP-Client:** `urllib.request` aus der Standardbibliothek statt `requests`. REVIEW-NFR-001 verlangt Stdlib-only explizit nur für SMTP/IMAP (kommt in Schritt 6), aber da für eine einzelne periodische GET-Anfrage kein externes Paket nötig ist, bleibt `requirements.txt` komplett leer — keine einzige Abhängigkeit im gesamten Worker-Prozess bislang. Passt zur "Minimal-Toollandschaft"-Leitlinie aus `00-tooling-and-process-independence.md`.
- **Cron-Ersatz:** Einfache `while True` / `time.sleep(30)`-Schleife statt einer zusätzlichen `schedule`-Bibliothek — laut Kickoff-Briefing explizit als gleichwertige Option vorgesehen ("Cron-artiger Trigger, z. B. schedule-Library oder einfache Loop mit time.sleep"). Eine Zeile Standardbibliothek ist einfacher zu erklären als eine zusätzliche Abhängigkeit.
- **Fehlerbehandlung:** Ein nicht erreichbarer core-app-Prozess führt zu einer geloggten `URLError`, nicht zu einem Absturz — direkte Umsetzung von REVIEW-NFR-002 ("Ausfall eines Prozesses darf den anderen nicht zum Absturz bringen"), hier aus Sicht des Workers.
- **`flush=True` beim Logging:** Python puffert `stdout` blockweise, sobald es nicht an ein Terminal, sondern (wie hier beim Testen) in eine Datei umgeleitet wird. Ohne `flush=True` wären Log-Zeilen erst beim Prozessende sichtbar geworden — beim ersten Testlauf tatsächlich aufgefallen (leere Logdatei trotz laufendem Prozess) und sofort behoben.

### Eigener Scope-Hinweis: "offene Tasks" statt "Fokus-Tasks"

REVIEW-FUNC-002 spricht von "offenen **Fokus**-Tasks" — der Fokus-Tasks-Begriff (die drei wöchentlich committeten Tasks) entsteht aber erst durch REVIEW-FUNC-006 (Rückspielen der Priorisierung), das laut Bau-Reihenfolge erst in Schritt 8 kommt. Für diesen Schritt pollt der Worker deshalb **alle aktiven Tasks** (`status == "active"`) — die Filterung auf tatsächliche Fokus-Tasks kommt automatisch dazu, sobald das Feld dafür existiert (Schritt 8). Kein Nacharbeiten nötig, nur eine Erweiterung der Filterbedingung in `fetch_open_tasks()`.

### Bewusst nicht gebaut

Kein eigener `/health`-Endpunkt für den Worker (der zweite Ausbau-Schritt aus `00-tooling-and-process-independence.md`, Abschnitt 3) — dafür müsste der Worker selbst einen HTTP-Server starten, was ihn von einem reinen Polling-Skript zu einem zweiten Webservice machen würde. Laut Doku reicht für die Abgabe "Stufe 1" (manueller Beweis per Log-Beobachtung), was in diesem Schritt bereits erbracht wurde (siehe Verifikation).

## Verifikation: Nachweis der Prozess-Unabhängigkeit (REVIEW-NFR-002, vorgezogen)

Obwohl der formale Nachweis erst Schritt 9 ist, wurde die Kernaussage schon hier direkt getestet, weil sie sich unmittelbar aus dem gebauten Code ergibt:

1. core-app gestartet, ein Test-Task angelegt.
2. Worker gestartet → pollt sofort, loggt `1 open task(s): ['Worker Poll Test']`. Zweiter Poll-Zyklus nach 30s bestätigt dasselbe Ergebnis.
3. core-app-Prozess hart beendet (`Stop-Process`).
4. Nächster Poll-Zyklus des Workers: `Could not reach core-app at http://127.0.0.1:3000: <urlopen error [WinError 10061] ...>` — **kein Absturz**, die Schleife läuft unverändert weiter (im nächsten Zyklus derselbe Fehler, sauber wiederholt).
5. core-app neu gestartet, ohne den Worker anzufassen.
6. Nächster Poll-Zyklus des Workers verbindet sich automatisch wieder erfolgreich, ohne Neustart des Worker-Prozesses nötig.

Damit ist die für Teil C zentrale Anforderung — zwei unabhängige Prozesse, Ausfall des einen bringt den anderen nicht zum Absturz — bereits im Kern demonstriert. Schritt 9 liefert dafür noch den formalen Screenshot-/GIF-Nachweis für die Abgabe.

Beide Prozesse danach gestoppt, Testdatenbank gelöscht.

## Nächster Schritt

Schritt 6: E-Mail-Versand + Mailpit-Anbindung (REVIEW-FUNC-003) — der Worker verschickt eine Mail mit allen offenen Fokus-Tasks über `smtplib`, lokal gegen Mailpit getestet.
