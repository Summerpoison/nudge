# Step 10b: Settings-Screen

**Status:** Abgeschlossen
**Bezug:** ESC-FUNC-003 (Urgent-Schwellenwert konfigurierbar), Vorarbeit für ESC-FUNC-004/005 (Buddy-Kontakt-Eingabe, Logik folgt in Schritt 10c). Aus dem Backlog: Settings-Screen, konfigurierbares Datum-/Zeitformat.

---

## Architekturentscheidung: Settings leben in core-app, der Worker pollt sie

`notification-worker` hat keine eigene Datenbank und keine UI — beides existiert ausschließlich in `core-app`. Ein Settings-*Screen* kann also nur dort entstehen. Für die Werte, die eigentlich das Verhalten des Workers steuern (SMTP-Host/Port, Absender-/Empfängeradresse), gilt deshalb dasselbe Muster wie schon für Tasks: `core-app` ist die alleinige Quelle der Wahrheit, der Worker fragt sie per REST ab (`GET /api/settings`, neu, analog zu `GET /api/tasks`). Kein neues Architekturmuster — nur eine Erweiterung des bereits bestehenden Polling-Ansatzes auf eine zweite Ressource.

## Was gebaut wurde

### `settings`-Tabelle (Singleton-Row)

```sql
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    smtp_host TEXT NOT NULL DEFAULT 'localhost',
    smtp_port INTEGER NOT NULL DEFAULT 1025,
    from_address TEXT NOT NULL DEFAULT 'nudge@localhost',
    to_address TEXT NOT NULL DEFAULT 'user@localhost',
    checkpoint_1_ratio REAL NOT NULL DEFAULT 0.5,
    checkpoint_2_ratio REAL NOT NULL DEFAULT 0.75,
    urgent_threshold_days REAL NOT NULL DEFAULT 3,
    buddy_name TEXT NOT NULL DEFAULT '',
    buddy_email TEXT NOT NULL DEFAULT '',
    date_format TEXT NOT NULL DEFAULT '%b %d, %Y %I:%M %p'
)
```

`CHECK (id = 1)` erzwingt auf Schemaebene, dass es exakt eine Zeile geben kann — kein generischer Key-Value-Store (wäre für eine feste, bekannte Anzahl an Einstellungen unnötig generisch und in der Prüfung schwerer zu erklären als benannte Spalten). `INSERT OR IGNORE INTO settings (id) VALUES (1)` bei jedem `init_db()`-Aufruf legt die Default-Zeile beim ersten Start an und ist bei jedem weiteren Start ein No-op.

### Berechnungsfunktionen nehmen jetzt Parameter statt globaler Konstanten

`calculate_buffer_deadline`, `calculate_checkpoints` und `is_urgent` hatten die Verhältnis-/Schwellenwerte bisher als Modul-Konstanten fest verdrahtet. Jetzt akzeptieren sie optionale Parameter (Default = bisherige Konstante, für Abwärtskompatibilität und Tests ohne Settings-Kontext):

```python
def calculate_checkpoints(created_at, buffer_deadline,
                           checkpoint_1_ratio=CHECKPOINT_1_RATIO,
                           checkpoint_2_ratio=CHECKPOINT_2_RATIO):
    ...

def is_urgent(task, threshold_days=URGENT_THRESHOLD_DAYS):
    ...
```

`create_task()` liest die aktuellen Settings einmal selbst (`get_settings()`) und reicht die Checkpoint-Verhältnisse durch — Task-Anlage ist ein seltener, nicht performance-kritischer Vorgang, ein zusätzlicher DB-Read fällt nicht ins Gewicht. **Wichtig:** Bereits angelegte Tasks behalten ihre zum Anlagezeitpunkt berechneten Checkpoint-Daten — eine spätere Settings-Änderung wirkt sich nur auf künftige Tasks aus, nicht rückwirkend. `BUFFER_RATIO` (0,7) bleibt bewusst **kein** Setting — weder im Backlog-Eintrag noch in der Anforderungsliste war das gefordert, nur die Checkpoint-Intervalle.

### `friendly_date` und `g.settings`: einmal pro Request, nicht einmal pro Datum

Eine Seite wie All-Tasks rendert leicht ein Dutzend Datumsangaben. Statt bei jedem `|friendly_date`-Filteraufruf erneut die Datenbank zu lesen, lädt ein `@app.before_request`-Hook die Settings einmal pro Anfrage in Flasks anfrage-gebundenes `g`-Objekt:

```python
@app.before_request
def load_settings():
    g.settings = get_settings()

def friendly_date(value):
    if not value:
        return ""
    date_format = g.settings["date_format"] if "settings" in g else "%b %d, %Y %I:%M %p"
    return datetime.fromisoformat(value).strftime(date_format)
```

`is_urgent()`-Aufrufe in der All-Tasks-Route bekommen den aktuellen Schwellenwert ebenfalls aus `g.settings` übergeben, statt ihn selbst nachzuschlagen — dieselbe Überlegung (die Route ruft `is_urgent()` einmal pro Task auf, der Schwellenwert soll nur einmal gelesen werden).

### Settings-Formular (`/settings`)

Vier Abschnitte, angelehnt an die im Screen-Audit (`02c`) als grundsätzlich übernehmbar eingestuften Teile von `nudge_settings`, um zwei neue erweitert:
- **Email** — SMTP-Host/-Port, Absender-/Empfängeradresse (steuert den Worker).
- **Checkpoints** — Checkpoint-1/-2-Prozentsätze für neue Tasks (Formular zeigt Prozent, `update_settings()` rechnet in Verhältniswerte 0–1 um).
- **Escalation** — Urgent-Schwellenwert in Tagen (ESC-FUNC-003), Buddy-Name/-Email (Eingabefeld für Schritt 10c vorbereitet, noch ohne Eskalationslogik dahinter).
- **Display** — Datumsformat, fünf feste Presets (US mit Monatsname, EU mit Monatsname, US numerisch, EU numerisch, ISO) statt eines Freitext-`strftime`-Feldes — weniger fehleranfällig für eine UI-Auswahl, einfacher zu erklären als ein rohes Format-Pattern.

`POST /settings` übernimmt nur eine feste Menge benannter Felder aus `request.form` (kein `**request.form` direkt an `update_settings()` durchgereicht) — verhindert, dass ein manipulierter Formular-Feldname zu einer unbeabsichtigten Spalten-Injektion führen könnte, auch wenn das Risiko bei einer Solo-App mit einer einzigen Nutzerin gering ist.

### Worker: `fetch_settings()` mit Fallback

```python
DEFAULT_SETTINGS = {
    "smtp_host": "localhost", "smtp_port": 1025,
    "from_address": "nudge@localhost", "to_address": "user@localhost",
}

def fetch_settings() -> dict:
    url = f"{CORE_APP_URL}/api/settings"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return json.loads(response.read())
    except urllib.error.URLError as error:
        log(f"Could not fetch settings from core-app at {url}, using defaults: {error}")
        return DEFAULT_SETTINGS
```

Wird bei jedem Versand-Zyklus neu aufgerufen (nicht einmalig beim Start gecacht) — eine Settings-Änderung wirkt sich damit spätestens beim nächsten Versand aus, ohne den Worker neu starten zu müssen. Gleiches Resilienz-Muster wie `fetch_open_tasks()`: nicht erreichbares core-app führt zu geloggten Fallback-Defaults, nicht zum Absturz. POP3-Zugangsdaten (`POP3_USERNAME`/`PASSWORD`) bleiben bewusst weiterhin Code-Konstanten — nicht Teil des ursprünglichen Backlog-Eintrags ("SMTP-Konfiguration"), keine ungefragte Scope-Erweiterung.

## Verifikation

1. `/api/settings` direkt nach Erststart geprüft → korrekte Default-Werte, Singleton-Zeile existiert.
2. `/settings`-Formular geöffnet, alle vier Abschnitte korrekt vorbefüllt, keine Konsolenfehler.
3. Werte geändert (Datumsformat → ISO, Checkpoint 1 → 40 %, Urgent-Schwellenwert → 5 Tage, Buddy-Kontakt gesetzt) und gespeichert → `GET /api/settings` bestätigt alle neuen Werte, Formular zeigt nach Reload dieselben Werte (Redirect-Then-Reload-Zyklus funktioniert).
4. Datumsformat-Änderung wirkt sich sofort auf `/tasks` aus — alle angezeigten Daten wechseln von `Jul 12, 2026 11:08 AM` zu `2026-07-12 11:58`, ohne Serverneustart.
5. Neuer Task angelegt, Checkpoint-1-Verhältnis rechnerisch aus den gespeicherten Zeitstempeln zurückgerechnet → exakt 0,40, wie in Settings hinterlegt. Checkpoint 2 (unverändert 75 %) weiterhin korrekt.
6. Mailpit + Worker gestartet, Settings zuvor auf klar erkennbare Test-Adressen geändert (`settings-test@nudge.local` / `settings-recipient@nudge.local`) → verschickte Review-Mail in Mailpit trägt exakt diese Absender-/Empfängeradresse, nicht die alten Code-Konstanten.
7. core-app während laufendem Worker beendet → Worker überspringt den Versand korrekt (kein Task-Datensatz zum Versenden vorhanden, gleiches Verhalten wie in Schritt 6 etabliert), kein Absturz. core-app neu gestartet → Worker verbindet sich automatisch wieder und versendet beim nächsten fälligen Zyklus mit den weiterhin korrekten (Settings-gespeicherten) Adressen.

Testdatensatz danach neu geseedet (`seed_data.py`), Settings dadurch wieder auf Defaults zurückgesetzt.

## Nächster Schritt

Schritt 10c: Buddy-System (ESC-FUNC-004, 005) — Eskalationsstufe 3 nutzt den in diesem Schritt bereits eingerichteten Buddy-Kontakt aus den Settings.
