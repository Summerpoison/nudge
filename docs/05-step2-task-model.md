# Step 2: Task-Datenmodell — Anlegen, Buffer-Deadline, Checkpoints

**Status:** Abgeschlossen
**Bezug:** CHKP-FUNC-001, CHKP-FUNC-002, CHKP-FUNC-003

---

## Was gebaut wurde

```
core-app/
├── db.py       SQLite-Verbindung + Schema (init_db)
├── models.py   Berechnungslogik + CRUD-Funktionen für Tasks
└── app.py      erweitert um /tasks-Routen (JSON-API)
```

### `db.py`

Nutzt `sqlite3` aus der Standardbibliothek — keine zusätzliche Abhängigkeit (ORM wie SQLAlchemy wäre für eine Einzelnutzer-App mit einer Handvoll Tabellen Overkill). `conn.row_factory = sqlite3.Row` sorgt dafür, dass Zeilen wie Dictionaries per Spaltenname ansprechbar sind (`row["name"]`), statt nur per Index.

Schema `tasks`:

| Spalte | Typ | Bedeutung |
|---|---|---|
| `id` | INTEGER PK | Autoincrement |
| `name` | TEXT | Task-Name (CHKP-FUNC-001) |
| `created_at` | TEXT (ISO 8601) | Erstellungsdatum, Bezugsgröße für alle Berechnungen |
| `external_deadline` | TEXT (ISO 8601) | vom Nutzer angegeben (CHKP-FUNC-001) |
| `buffer_deadline` | TEXT (ISO 8601) | berechnet, überschreibbar (CHKP-FUNC-002) |
| `checkpoint_1` / `checkpoint_2` | TEXT (ISO 8601) | berechnet, überschreibbar (CHKP-FUNC-003) |
| `status` | TEXT | Default `'active'`, wird ab Schritt 4 (Blocker-Triage) auf `'on_hold'` gesetzt |

Daten werden als ISO-8601-Strings gespeichert, nicht als SQLite-eigener Datumstyp (den gibt es nicht — SQLite kennt nur TEXT/INTEGER/REAL/BLOB). Vorteil von ISO 8601: alphabetische Sortierung entspricht chronologischer Sortierung, daher funktioniert `ORDER BY buffer_deadline` direkt.

### `models.py` — Berechnungslogik

```python
BUFFER_RATIO = 0.7
CHECKPOINT_1_RATIO = 0.5
CHECKPOINT_2_RATIO = 0.75


def calculate_buffer_deadline(created_at, external_deadline):
    available_time = external_deadline - created_at
    return created_at + BUFFER_RATIO * available_time


def calculate_checkpoints(created_at, buffer_deadline):
    buffer_window = buffer_deadline - created_at
    checkpoint_1 = created_at + CHECKPOINT_1_RATIO * buffer_window
    checkpoint_2 = created_at + CHECKPOINT_2_RATIO * buffer_window
    return checkpoint_1, checkpoint_2
```

- `calculate_buffer_deadline` setzt exakt CHKP-FUNC-002 um: `buffer_deadline = created_at + 0.7 × (external_deadline − created_at)`. Python erlaubt Subtraktion zweier `datetime`-Objekte (ergibt ein `timedelta`) und Multiplikation eines `timedelta` mit einem `float`.
- `calculate_checkpoints` **klärt eine im Original-Spec offene Frage**: CHKP-FUNC-003 sagt "50%/75% der verfügbaren Zeit", aber "verfügbare Zeit" war im RE-Audit (Abschnitt 3.2) nur für die Buffer-Berechnung präzise definiert (`external_deadline − created_at`), nicht explizit für die Checkpoints. Zwei Lesarten wären möglich gewesen:
  1. Checkpoints relativ zum **externen** Deadline-Fenster (creation → external_deadline) — hätte zur Folge, dass Checkpoint 2 (75%) **nach** der Buffer-Deadline (70%) läge, was keinen Sinn ergibt (ein Checkpoint nach dem eigenen internen Zieltermin).
  2. Checkpoints relativ zum **Buffer**-Fenster (creation → buffer_deadline) — beide Checkpoints liegen dann sauber innerhalb des Arbeitsfensters vor der Buffer-Deadline.
  **Entscheidung (mit Nutzerin abgestimmt):** Variante 2 (Buffer-Fenster). Diese Lesart ist im Code fest verankert (`calculate_checkpoints` nimmt `buffer_deadline`, nicht `external_deadline`, als zweites Argument) und hier dokumentiert, weil sie im ursprünglichen Anforderungstext nicht eindeutig war.
- **Override-Mechanismus:** `create_task()` akzeptiert `buffer_deadline`, `checkpoint_1`, `checkpoint_2` optional. Wird kein Wert übergeben (`None`), greift die Berechnung; wird ein Wert übergeben, wird er unverändert übernommen. Das setzt "automatisch berechnet, aber überschreibbar" aus CHKP-FUNC-001/003 um, ohne zwei getrennte Code-Pfade zu brauchen.

### `app.py` — JSON-API

Drei neue Routen:
- `POST /tasks` — Task anlegen. Erwartet JSON-Body mit `name`, `external_deadline` (ISO-8601-String), optional `buffer_deadline`/`checkpoint_1`/`checkpoint_2` für die Override-Fälle.
- `GET /tasks` — alle Tasks, sortiert nach Buffer-Deadline (dringendste zuerst).
- `GET /tasks/<id>` — einzelner Task, `404` falls nicht vorhanden.

`init_db()` wird beim Modulimport von `app.py` einmalig aufgerufen (legt die Tabelle an, falls sie noch nicht existiert — `CREATE TABLE IF NOT EXISTS` ist idempotent, kann also bei jedem Start gefahrlos erneut laufen).

**Bewusst noch keine HTML-Formulare/Views** — das ist Schritt 3 (Dashboard- und Task-Detail-Views). Dieser Schritt liefert nur die Datenschicht + eine testbare Schnittstelle.

## Verifikation

Server gestartet, dann manuell getestet:

```
POST /tasks {"name": "Write RE report", "external_deadline": "2026-07-26T18:00:00"}
→ 201, buffer_deadline ≈ creation + 10.3 Tage, checkpoint_1 ≈ +5.15 Tage, checkpoint_2 ≈ +7.73 Tage
GET /tasks           → Liste mit dem angelegten Task
GET /tasks/1         → derselbe Task einzeln
GET /tasks/999       → 404
```

Rechnerische Kontrolle: External Deadline lag ca. 14,73 Tage in der Zukunft. `0.7 × 14,73 ≈ 10,3 Tage` (Buffer-Fenster). `0.5 × 10,3 ≈ 5,15 Tage`, `0.75 × 10,3 ≈ 7,73 Tage` — stimmt mit der Serverantwort überein.

Testdatenbank (`nudge.db`) nach dem Test gelöscht (nicht versioniert, siehe `.gitignore`).

## Scope-Frage während Review: Tasks ohne Deadline

**Aufgeworfen während der lokalen Code-Review dieses Schritts:** `external_deadline` ist `TEXT NOT NULL` — sollte das Feld optional sein, damit Tasks auch ohne Deadline angelegt werden können (z. B. Ideen/Backlog-Einträge)?

**Analyse:**
- `CHKP-FUNC-001` definiert `external_deadline` bereits explizit als Pflichtfeld bei der Task-Erstellung (Must). `TEXT NOT NULL` setzt diese Anforderung korrekt um, keine Lücke.
- Kein Widerspruch zur Eisenhower-Logik (`02b-eisenhower-buddy-design.md`, Abschnitt 5): "Not Urgent" bedeutet nicht "keine Deadline", sondern "Buffer-Deadline noch weit genug entfernt" (Default-Schwelle: ≥ 3 Tage). Ein Task mit Deadline in drei Monaten ist heute "Important + Not Urgent" und wechselt automatisch zu "Urgent", sobald die Buffer-Deadline näher rückt (`ESC-FUNC-001`/`002`). Weit entfernte, aber reale Deadlines sind also bereits sauber abgedeckt.
- Ein Task **ganz ohne** Deadline ist etwas strukturell anderes: Ohne `external_deadline` gibt es keine Buffer-Deadline, keine Checkpoints, keine Eskalation — der komplette Kernmechanismus von Nudge (siehe Leitprinzip *"the system earns its value in the first 48 hours after a deadline slips"*) greift nicht. Das ist kein Nudge-"Task", sondern ein anderes Objekt (Backlog-/Ideen-Eintrag).

**Entscheidung:** `external_deadline` bleibt Pflichtfeld für Tasks im MVP-Scope, wie in `CHKP-FUNC-001` spezifiziert. Kein Schema-Change.

**Bewusst spätere Erweiterung (nicht Teil des MVP):** Ein separater Objekttyp für deadline-lose Einträge (Backlog/Ideen/Drafts), der explizit **nicht** am Checkpoint-/Buffer-/Eisenhower-Mechanismus teilnimmt. Erste Designidee dafür (festgehalten für später, nicht spezifiziert): automatischer Wiedervorlage-Reminder z. B. einen Monat nach Anlage ("Ist das mittlerweile konkreter geworden?"), um Backlog-Einträge nicht endlos liegen zu lassen, ohne die Nutzerin zu zwingen, sofort eine Deadline zu erfinden. Analog zur KI-Reply-Parsing-Erweiterung (`00-kickoff-briefing.md`, Abschnitt 7): dokumentiert, aber erst nach Abschluss des MVP relevant.

## Nächster Schritt

Schritt 3: Dashboard- und Task-Detail-Views (CHKP-FUNC-011, 012) — HTML/Jinja2-Templates auf Basis der Stitch-Referenzscreens, plus die "Rohfassung" Add-Task-Form.
