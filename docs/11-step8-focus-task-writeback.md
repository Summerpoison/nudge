# Step 8: Rückspielen der Priorisierung in die Kern-App

**Status:** Abgeschlossen
**Bezug:** REVIEW-FUNC-006.

---

## Was gebaut wurde

### Neues Feld: `is_focus_task`

`core-app/db.py` — `tasks`-Tabelle um `is_focus_task INTEGER NOT NULL DEFAULT 0` erweitert. Kein separates "Fokus-Tasks"-Objekt/-Tabelle — ein einzelnes Flag auf dem Task selbst reicht, da laut `02b-eisenhower-buddy-design.md` zu jedem Zeitpunkt nur ein Satz "aktuell committeter" Fokus-Tasks existiert (kein Verlauf über mehrere Wochen nötig für den MVP).

### `set_focus_tasks()` — Ersetzen statt Hinzufügen

```python
def set_focus_tasks(task_ids: list[int]) -> list[int]:
    conn = get_connection()
    conn.execute("UPDATE tasks SET is_focus_task = 0")

    applied: list[int] = []
    if task_ids:
        placeholders = ",".join("?" * len(task_ids))
        rows = conn.execute(f"SELECT id FROM tasks WHERE id IN ({placeholders})", task_ids).fetchall()
        applied = [row["id"] for row in rows]
        conn.execute(f"UPDATE tasks SET is_focus_task = 1 WHERE id IN ({placeholders})", task_ids)

    conn.commit()
    conn.close()
    return applied
```

Jeder Aufruf setzt zuerst **alle** Tasks auf `is_focus_task = 0` zurück, bevor die neu übergebenen IDs gesetzt werden — passend zu "Fokus-Tasks **der Woche**": eine neue Priorisierung ersetzt die alte vollständig, statt sich zu addieren. Der Rückgabewert (`applied`) enthält nur IDs, die tatsächlich existieren — falls der Worker eine ungültige ID schicken würde, würde sie still ignoriert statt einen Fehler zu werfen (kann in der Praxis kaum passieren, da die IDs direkt aus der zuvor verschickten Review-Mail stammen, aber schadet nicht als Absicherung).

### Neue Route: `POST /api/tasks/focus`

```python
@app.route("/api/tasks/focus", methods=["POST"])
def api_set_focus_tasks():
    data = request.get_json()
    task_ids = data["task_ids"]
    applied = set_focus_tasks(task_ids)
    for task_id in applied:
        add_task_event(task_id, "marked_focus_task", "Marked as a focus task for this week")
    return jsonify(focus_task_ids=applied)
```

Jeder neu markierte Task bekommt einen Activity-Log-Eintrag ("Marked as a focus task for this week") — gleiches Muster wie Statuswechsel und Datei-Uploads aus früheren Schritten, macht die Markierung in der Task-Historie nachvollziehbar.

### Worker: `post_focus_tasks()`

`notification-worker/worker.py` — nach erfolgreichem Parsing einer Antwort (Schritt 7) wird das Ergebnis nicht mehr nur geloggt, sondern per `urllib.request` (POST, JSON-Body) an die neue Route geschickt:

```python
def post_focus_tasks(task_ids: list[int]) -> None:
    url = f"{CORE_APP_URL}/api/tasks/focus"
    payload = json.dumps({"task_ids": task_ids}).encode("utf-8")
    request_obj = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request_obj, timeout=5) as response:
            result = json.loads(response.read())
    except urllib.error.URLError as error:
        log(f"Could not post focus tasks to core-app at {url}: {error}")
        return
    log(f"Marked focus tasks for this week: {result['focus_task_ids']}")
```

Wird nur aufgerufen, wenn `parse_top_priorities()` tatsächlich mindestens eine gültige ID gefunden hat (siehe Schritt 7) — eine Antwort ohne erkennbare Priorisierung ("Sounds good, no specific pick") löscht die bisherigen Fokus-Tasks nicht versehentlich, sondern lässt den bestehenden Stand unangetastet. Scheitert der REST-Call (core-app nicht erreichbar), wird das geloggt, ohne den Worker abstürzen zu lassen — gleiches Resilienz-Muster wie in den Schritten 5–7.

### Sichtbarkeit: "Focus"-Badge im UI

Reine Anzeige-Ergänzung, keine Änderung an Sortierlogik: Ein kleines "Focus"-Label (Flag-Icon, `bg-accent`) erscheint überall, wo Tasks bereits dargestellt werden — Dashboard (Hero-Karte und Liste), All-Tasks, Task-Detail-Kopfbereich. Ohne diese Markierung wäre `is_focus_task` ein unsichtbares Datenbank-Flag ohne erkennbaren Effekt in der Demo. Dashboard-Sortierung (aktuell: früheste Buffer-Deadline zuerst) bleibt unverändert — eine Fokus-basierte Priorisierung der Dashboard-Reihenfolge wäre ein größerer, hier nicht angefragter Eingriff und ist in `backlog.md` vermerkt, falls später gewünscht.

## Verifikation

Vollständiger Testlauf (core-app, Worker, Mailpit mit `--pop3-auth-file`):

1. Vier Test-Tasks angelegt, alle mit `is_focus_task: 0` (Schema-Default korrekt, keine Migration-Probleme bei frischer Test-Datenbank).
2. Review-Mail abgewartet, Antwort simuliert ("Lets focus on #3, #4 and #2") → Worker parst `[3, 4, 2]`, postet an `/api/tasks/focus`, loggt `Marked focus tasks for this week: [2, 3, 4]`.
3. `GET /api/tasks` bestätigt: Tasks 2, 3, 4 haben `is_focus_task: 1`, Task 1 weiterhin `0`.
4. UI geprüft: "Focus"-Badge korrekt auf All-Tasks, Dashboard (Hero-Karte + Liste) und Task-Detail-Kopfbereich sichtbar für alle drei markierten Tasks, korrekt abwesend beim vierten. Activity-Log von Task 2 zeigt den neuen Eintrag "Marked as a focus task for this week".
5. **Ersetzen-Semantik geprüft:** zweite simulierte Antwort auf eine neue Review-Mail ("This week I only want to focus on #1") → Worker postet `[1]` → `GET /api/tasks` zeigt danach nur noch Task 1 mit `is_focus_task: 1`, Tasks 2/3/4 korrekt auf `0` zurückgesetzt.

Alle Prozesse danach gestoppt, Testdatenbank gelöscht.

## Nebenbei erledigt: Anforderungs-Checkliste aktualisiert

`03-mvp-requirements-checklist.md` war seit Beginn des Baus nie mit dem tatsächlichen Fortschritt synchronisiert (alle Boxen standen auf `[ ]`, obwohl längst mehrere Module fertig waren). Alle bisher tatsächlich umgesetzten CHKP- und REVIEW-FUNC-Anforderungen wurden abgehakt, mit Verweis auf den jeweiligen Bau-Schritt. Zwei Anforderungen bewusst **nicht** abgehakt, obwohl der zugrundeliegende Mechanismus schon funktioniert:
- **REVIEW-NFR-002** (Prozess-Unabhängigkeit) — Mechanismus in Schritt 5 verifiziert, aber der formale Nachweis (Screenshot/GIF für die Abgabe) ist explizit erst Schritt 9.
- **CHKP-NFR-002** und alle Should/Could-Punkte, die noch nicht gebaut sind, bleiben korrekt unangetastet.

## Nächster Schritt

Schritt 9: Formaler Nachweis der Prozess-Unabhängigkeit (REVIEW-NFR-002) — Screenshot/GIF von core-app und Worker, die unabhängig voneinander starten/stoppen, für die Abgabe.
