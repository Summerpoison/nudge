# Step 10a: Dashboard-Umbau und Eisenhower-Gruppierung

**Status:** Abgeschlossen
**Bezug:** ESC-FUNC-001 (berechneter Urgent-Zustand), ESC-FUNC-002 (Grundlage für die Eskalations-Filterbedingung — die eigentliche Eskalationskette selbst ist nicht Teil dieses Schritts). Erster von zwei Teilen aus Schritt 10 (zweiter Teil: Buddy-System, separat).

---

## Vorab geklärt: kein echtes 4-Quadranten-Raster

`nudge_task_overview_matrix` (Design-Referenz) zeigt vier Quadranten (Do First / Schedule / Delegate / Don't Do). `02b-eisenhower-buddy-design.md` beschreibt aber durchgängig nur **zwei**: "Important + Urgent" und "Important + Not Urgent" — kein einziges Mal "Not Important". Passt zum Datenmodell: Nudge trackt keine generische To-do-Liste, jeder existierende Task ist per Definition bereits committet (das wäre sonst der Anwendungsfall für die zurückgestellten "deadline-losen Tasks", siehe `backlog.md`). **Entscheidung (mit Nutzerin abgestimmt):** Gruppierung nach **Urgent / Not Urgent** statt eines vollen Eisenhower-Rasters — kein erfundenes "Important"-Feld, das nirgends spezifiziert ist.

## Was gebaut wurde

### `is_urgent()` (ESC-FUNC-001)

```python
URGENT_THRESHOLD_DAYS = 3

def is_urgent(task: dict) -> bool:
    if task["status"] != "active":
        return False
    buffer_deadline = datetime.fromisoformat(task["buffer_deadline"])
    return buffer_deadline - datetime.now() < timedelta(days=URGENT_THRESHOLD_DAYS)
```

Reine Funktion, kein gespeichertes Feld — exakt die Vorgabe aus ESC-FUNC-001 ("berechneter, nicht manuell gesetzter Zustand"), gleiches Muster wie `is_checkpoint_due()` aus Schritt 3. Schwellenwert (3 Tage) als Konstante hartkodiert, wie schon bei anderen Settings-artigen Werten (SMTP-Konfiguration im Worker) — ein echtes Settings-UI zum Anpassen ist in `backlog.md` vermerkt (ESC-FUNC-003, Should). `on_hold`/`done`-Tasks sind nie "urgent" — ergibt inhaltlich keinen Sinn für pausierte oder abgeschlossene Arbeit.

### All-Tasks wird zum Backlog

`app.py` — die `/tasks`-Route berechnet jetzt drei Gruppen serverseitig (`urgent_tasks`, `not_urgent_tasks`, `other_tasks` für `on_hold`/`done`) und übergibt sie zusätzlich zur unveränderten Flat-Liste an das Template.

`all_tasks.html` — Grouped/List-Umschalter (reines JavaScript, kein Page-Reload, gleiches Zwei-Zustands-Muster wie schon beim Datei-Auswahl-Button in Schritt 3): **Grouped ist Default** (Nutzerinnen-Entscheidung), zeigt drei Abschnitte (Urgent, Not Urgent, On Hold & Done — letzterer sichtbar, aber optisch zurückgenommen mit `opacity-70`, damit erledigte/pausierte Arbeit nicht verschwindet, aber auch nicht die Aufmerksamkeit dominiert). List bleibt als zweite Ansicht erhalten (Nutzerinnen-Entscheidung: nicht vollständig ersetzen) für den Fall, dass die flache, nach Dringlichkeit sortierte Übersicht nützlicher ist als die Gruppierung.

Ein Jinja-`{% macro task_row(task) %}` vermeidet, die Task-Card-Markup viermal zu duplizieren (drei Gruppen + Listenansicht).

### "Add a task" wandert zum Dashboard

`dashboard.html` bekommt das Formular aus `all_tasks.html` (identischer Code, nur der Ort hat sich geändert). Route bleibt unverändert (`POST /tasks`, semantisch weiterhin korrekt — ein Task wird an die Tasks-Ressource angehängt, unabhängig davon, von welcher Seite aus das Formular abgeschickt wird) — nur das Redirect-Ziel nach dem Anlegen wechselt von `all_tasks` zu `dashboard`. All-Tasks bekommt stattdessen einen kurzen Hinweistext mit Link zurück zum Dashboard, damit das Formular nicht ersatzlos "verschwindet", falls jemand es an der alten Stelle sucht.

## Verifikation

Mit dem Testdatensatz aus `seed_data.py` (bewusst gewählt, weil er bereits alle relevanten Zustände abdeckt):

1. `/tasks` (Grouped, Default) → korrekt in drei Gruppen sortiert: **Urgent** ("Fix login bug", "Prepare oral exam slides" — beide mit Buffer-Deadline < 3 Tage entfernt), **Not Urgent** ("Write research proposal" — Buffer-Deadline Wochen entfernt), **On Hold & Done** ("Review PR feedback", "Draft Q4 report").
2. List-Umschalter geklickt → flache, nach Dringlichkeit sortierte Liste mit allen 5 Tasks, keine Konsolenfehler.
3. Kein Add-Task-Formular mehr auf `/tasks` — stattdessen Hinweis mit Link zum Dashboard.
4. `/` (Dashboard) → Add-Task-Formular vorhanden, Task angelegt ("Dashboard add-task test") → Weiterleitung landet zurück auf dem Dashboard (nicht mehr auf All-Tasks), neuer Task erscheint sofort in "Other open tasks".

Testdatensatz danach neu geseedet (`seed_data.py`), damit ein sauberer Zustand für die nächste Session bereitsteht.

## Nächster Schritt

Schritt 10b: Buddy-System (ESC-FUNC-004, 005) — separat, wie mit der Nutzerin abgestimmt.
