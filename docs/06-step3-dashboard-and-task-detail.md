# Step 3: Dashboard, All-Tasks, Add-Task und Task-Detail

**Status:** Abgeschlossen
**Bezug:** CHKP-FUNC-011, CHKP-FUNC-012. Screen-Grundlage und Entscheidungen siehe `02c-screen-audit-and-design-decisions.md`.

---

## Was gebaut wurde

```
core-app/
├── templates/
│   ├── base.html          Sidebar-Layout, Farbschema, Fonts
│   ├── dashboard.html      CHKP-FUNC-011 (Kernansicht)
│   ├── all_tasks.html      CHKP-FUNC-011 (Vollständige Liste) + Task anlegen
│   └── task_detail.html    CHKP-FUNC-012
├── uploads.py              Dateisystem-Helper für Artefakt-Uploads
├── app.py                  erweitert um HTML-Routen + Jinja-Filter
├── models.py                erweitert um Events/Status/Buffer-Fortschritt
└── db.py                    erweitert um task_events-Tabelle
```

### Routen-Umbau: `/api/tasks` vs. HTML-Seiten

Die JSON-API aus Schritt 2 (`POST/GET /tasks`, `GET /tasks/<id>`) wurde nach `/api/tasks` bzw. `/api/tasks/<id>` verschoben. Grund: `/tasks` und `/tasks/<id>` werden jetzt von echten HTML-Seiten belegt (All-Tasks-Liste, Task-Detail). Ohne den Umzug hätten sich JSON- und HTML-Antwort denselben Pfad teilen müssen, was weder sauber trennbar noch für den späteren Notification-Worker (Teil C, pollt die API) eindeutig gewesen wäre. Die API-Funktionalität selbst ist unverändert, nur die Pfade und Funktionsnamen (`api_create_task`, `api_list_tasks`, `api_get_task`) haben sich geändert.

Neue HTML-Routen:
- `GET /` — Dashboard
- `GET /tasks`, `POST /tasks` — All-Tasks-Liste bzw. Task-Anlage über das einfache Formular
- `GET /tasks/<id>` — Task-Detail
- `POST /tasks/<id>/upload` — Artefakt-Upload
- `POST /tasks/<id>/status` — Statuswechsel (aktuell genutzt für "Resume Task" und "Mark Complete")

### `base.html` — Farbschema und Fonts

Eigene, schlanke Tailwind-Konfiguration statt der von Stitch automatisch generierten ~40-Token-Paletten (siehe `02c-screen-audit-and-design-decisions.md`, Abschnitt 1):

```js
colors: {
    background: '#EEEEEE',
    surface: '#FFFFFF',
    primary: '#6FCF97',
    accent: '#2FA084',
    text: '#1F6F5F',
},
fontFamily: {
    display: ['Lexend', 'sans-serif'],
    body: ['Inter', 'sans-serif'],
},
```

Fünf Farben, zwei Fonts — bewusst minimal, um in der mündlichen Prüfung erklärbar zu bleiben. Tailwind wird weiterhin per CDN eingebunden (wie in den Stitch-Referenzscreens), da die Stitch-Vorlagen so am direktesten in Jinja2-Templates überführt werden können, ohne einen Build-Schritt (PostCSS/Tailwind-CLI) einzuführen — für den Scope dieser App reicht das aus. Die aktive Nav-Markierung erfolgt über einen Vergleich von `request.path` mit `url_for(...)` direkt im Template (Flask stellt `request` automatisch im Jinja-Kontext bereit).

### Dashboard (`CHKP-FUNC-011`, Kernansicht)

Zeigt genau einen hervorgehobenen "Next up"-Task (der aktive Task mit der nächsten Buffer-Deadline, da `get_all_tasks()` bereits danach sortiert) plus eine kompakte Liste der übrigen offenen Tasks. Bewusst *kein* Buffer-Fortschrittsbalken hier (siehe Entscheidung in `02c-...md`, Abschnitt 4: Buffer-Sichtbarkeit wandert in die Task-Detail-Ansicht, um das Dashboard minimalistisch zu halten).

### All-Tasks (`CHKP-FUNC-011`, Vollständige Übersicht + Task anlegen)

Liste aller Tasks (unabhängig vom Status) mit Status-Badge und Buffer-Deadline, sortiert nach Dringlichkeit. Darunter ein einfaches Formular (Name + `datetime-local`-Feld) zum Anlegen — entspricht der in `02c-...md` getroffenen Entscheidung "einfaches Formular statt Freitext-Parser" für den MVP. Die separate `nudge_add_task`-Vorlage wurde dadurch nicht als eigene Seite übernommen, sondern als eingebettetes Formular auf dieser Seite umgesetzt (weniger Redundanz, ein einziger Task-Anlage-Weg statt zwei).

Eisenhower-Gruppierung (aus `nudge_task_overview_matrix`) ist hier bewusst noch nicht eingebaut — siehe `02c-...md`, Abschnitt 5 (verschoben auf den optionalen Eisenhower-Schritt, um Schritt 3 nicht zu verwässern).

### Task-Detail (`CHKP-FUNC-012`)

Zeigt für einen einzelnen Task:
- Kopfbereich mit Status-Badge, externem Deadline, Buffer-Deadline, beiden Checkpoints
- Buffer-Fortschrittsbalken (`buffer_progress_percent()` in `models.py`: verstrichene Zeit seit Anlage geteilt durch die Breite des Buffer-Fensters, auf 0–100 % begrenzt)
- Activity-Log: synthetisiertes "Task created"-Ereignis aus `created_at` plus alle gespeicherten `task_events`-Zeilen (aktuell: Artefakt-Einreichungen, Statuswechsel)
- Attachments: Liste der hochgeladenen Dateien (aus dem Dateisystem gelesen, siehe unten) plus Upload-Formular — deckt den in CHKP-FUNC-012 geforderten "Ort für Artefakt-Einreichung" ab
- Status-Aktion: "Resume Task" für `on_hold`-Tasks (CHKP-FUNC-010) bzw. "Mark Complete" für aktive Tasks

**"Mark Complete" ist keiner Anforderungs-ID zugeordnet** — die MVP-Checkliste spezifiziert nirgends, wie ein Task abgeschlossen wird, obwohl das für eine nutzbare Task-Verwaltung unverzichtbar ist (ähnlich wie "Löschen" nirgends spezifiziert ist). Pragmatisch ergänzt, im Dashboard/All-Tasks berücksichtigt (`status == 'done'` taucht nicht mehr unter "aktiv" auf).

### Neu: `task_events`-Tabelle und Datei-Uploads

`db.py` bekam eine zweite Tabelle `task_events` (id, task_id, event_type, description, created_at) für die Activity-Log-Historie — vorher wurde nur der aktuelle Task-Zustand gespeichert, keine Ereignis-Historie (siehe `02c-...md`, Abschnitt 6).

`uploads.py` ist ein eigenständiges, kleines Modul (kein DB-Zugriff) für Datei-Uploads: Dateien landen unter `core-app/uploads/<task_id>/<dateiname>`, das Dateisystem selbst ist die Quelle der Wahrheit (kein separates `attachments`-Tabellen-Tracking nötig — `list_attachments()` liest einfach das Verzeichnis). `secure_filename()` aus Werkzeug (Flask-Abhängigkeit, keine zusätzliche Library) verhindert Pfad-Traversal-Angriffe über den Dateinamen. `core-app/uploads/` ist in `.gitignore` (Nutzerinhalte, keine Quellcode-Datei).

## Verifikation

Lokal im Browser getestet (Server gestartet, `.venv`-Python, Port 3000):

1. `/` (Dashboard) im leeren Zustand → korrekter Empty-State-Text.
2. `/tasks` → Formular ausgefüllt ("Finish RE report", externes Deadline), Task angelegt, Weiterleitung zurück zu `/tasks`, neuer Task erscheint in der Liste mit Status `active`.
3. `/tasks/1` → alle vier Datumsfelder korrekt berechnet und angezeigt, Buffer-Fortschritt 0 % direkt nach Anlage.
4. "Mark Complete" geklickt → Status wechselt zu `done`, Activity-Log bekommt einen neuen Eintrag, Dashboard zeigt den Task danach nicht mehr als aktiv.
5. Datei-Upload und Statuswechsel auf `on_hold` per `curl -F`/`curl -d` gegen die laufende Instanz getestet → Datei landet unter `core-app/uploads/1/`, Activity-Log verzeichnet beides, "Resume Task"-Button erscheint für `on_hold`-Tasks.
6. `GET /tasks/999` → `404`.
7. `GET /api/tasks` weiterhin funktionsfähig nach dem Routen-Umbau, spiegelt den aktuellen Status (`on_hold`) korrekt wider.

Server danach gestoppt, Testdatenbank und Test-Uploads gelöscht (nicht versioniert).

## Nachträge aus der Nutzerinnen-Review

Beim manuellen Durchklicken durch die Nutzerin wurden vier Punkte gefunden und direkt behoben:

- **Status-Karte war für `done`-Tasks leer:** Die ursprüngliche Bedingung in `task_detail.html` deckte nur `on_hold` und `active` ab, kein `{% elif %}`-Zweig für `done`. Ergänzt: Anzeige "Marked complete." plus "Reopen Task"-Button (setzt zurück auf `active`, Outline-Stil statt Solid, da es sich um eine seltenere Korrekturaktion handelt, nicht die primäre Handlung auf der Seite).
- **Datei-Upload sah nach nicht gestyltem Standard-Input aus:** `<input type="file">` wird jetzt per CSS versteckt und durch ein als Button gestyltes `<label>` ersetzt (Material-Symbols-Icon `upload_file`, Outline-Stil als sekundäre Handlung gegenüber "Submit Proof"). Der ausgewählte Dateiname ersetzt per JavaScript den Label-Text direkt, statt in einer separaten Zeile zwischen den beiden Buttons zu erscheinen — vermeidet die von der Nutzerin bemängelte visuelle Lücke. Ein dauerhafter "No file selected"-Platzhaltertext wurde entfernt (der Browser feuert ohnehin kein Event, wenn der Dateidialog ohne Auswahl abgebrochen wird — ein zuverlässiger "abgebrochen"-Zustand ist so nicht sauber abbildbar, daher: kein Text, bis wirklich eine Datei gewählt wurde).
- **Angehängte Dateien waren weder einsehbar noch löschbar:** Neue Route `GET /tasks/<id>/uploads/<filename>` (Auslieferung über `send_from_directory`) macht jeden Dateinamen in der Liste zu einem anklickbaren Link — wichtig, weil Originaldateinamen (z. B. "unbenannt2.png") oft nichtssagend sind und man den Inhalt prüfen können muss. Neue Route `POST /tasks/<id>/uploads/<filename>/delete` entfernt eine Datei wieder (mit Eintrag im Activity-Log). Beide Routen wenden `secure_filename()` erneut auf den URL-Parameter an, bevor er mit dem Task-Upload-Verzeichnis kombiniert wird (Schutz vor Pfad-Traversal über einen manipulierten Dateinamen in der URL).
- **Zu wenig visuelle Hierarchie bei den Datumsfeldern:** `dt` (Label, z. B. "EXTERNAL DEADLINE") und `dd` (Wert) teilten sich vorher dieselbe Textfarbe/-transparenz vom übergeordneten `<dl>`. Jetzt getrennt gestylt: Label bleibt klein/uppercase, bekommt aber `font-semibold` für Lesbarkeit; Wert bekommt volle Textfarbe (kein Transparenz-Abzug) und `font-medium`, damit der eigentliche Inhalt stärker hervorsticht als die Kategorisierung darüber.

**Zusätzlich unaufgefordert korrigiert:** Der Kontrast von `bg-primary` (`#6FCF97`) mit `text-text` (`#1F6F5F`) liegt rechnerisch bei ca. 3.16:1, unterhalb des WCAG-AA-Werts von 4.5:1 für normalen Fließtext. Barrierefreiheit ist laut `03-mvp-requirements-checklist.md` ("Bewusst nicht atomarisiert") explizit außerhalb des MVP-NFR-Scopes — es wurde hier trotzdem kostenlos nachgebessert, weil es eine reine Klassenänderung ohne Abweichung von der vorgegebenen Farbpalette ist: alle primären Call-to-Action-Buttons (Add Task, View Task, Submit Proof, Resume/Reopen Task) nutzen jetzt `bg-accent` (`#2FA084`) mit weißem Text (ca. 3.24:1) statt der ursprünglichen Kombination. Echtes AA (4.5:1) ist mit der vorgegebenen Palette für Button-Text nicht erreichbar, ohne von den vier vorgegebenen Farbwerten abzuweichen — das wäre eine separate Entscheidung, keine stillschweigende Änderung.

## Nächster Schritt

Schritt 4: Blocker-Triage + Mail-Draft (CHKP-FUNC-004 bis 009) — Check-in-Screen (`checkpoint_q4_report`-Basis) mit Übergang zur Triage (`triage_what_s_blocking_you`-Basis, vier Optionen inkl. 10-Minuten-Timer), `mailto:`-Versand und optimistischer Status-Wechsel auf "On Hold".
