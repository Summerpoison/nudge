# Step 9: Formaler Nachweis der Prozess-Unabhängigkeit

**Status:** Textueller Nachweis abgeschlossen; visuelles Beweismaterial (Screenshot/GIF) für die Abgabe noch offen — siehe Abschnitt "Was für die Abgabe noch fehlt".
**Bezug:** REVIEW-NFR-002. Nachweis-Stufen wie in `00-tooling-and-process-independence.md`, Abschnitt 3 definiert.

---

## Was gezeigt werden musste (Stufe 1, "Minimalanforderung für die Doku")

1. **core-app allein starten** (Notification-Worker nie gestartet) → core-app bleibt vollständig normal nutzbar.
2. **Umgekehrt:** core-app stoppen, während der Worker läuft → Worker läuft unverändert weiter (loggt ggf. Fehler beim Pollen, stürzt aber nicht ab).

## Testaufbau

Alle Befehle einzeln nachvollziehbar, keine gemeinsame Konfiguration zwischen den Prozessen außer der HTTP-URL `http://127.0.0.1:3000`.

### Teil 1 — core-app ganz ohne Worker

```
cd core-app
.venv\Scripts\python.exe app.py
```

Bestätigt: kein `notification-worker`-Prozess läuft zu diesem Zeitpunkt (per Prozessliste geprüft). core-app im Browser aufgerufen:
- `/` (Dashboard) rendert korrekt, leerer Zustand.
- `/tasks` → Formular ausgefüllt ("Process independence proof task"), Task erfolgreich angelegt, erscheint sofort in der Liste mit Status `active`.

**Ergebnis:** core-app benötigt den Worker an keiner Stelle, um voll funktionsfähig zu sein — kein einziger Codepfad in `core-app` referenziert den Worker oder wartet auf ihn.

### Teil 2 — Worker gestartet, dann core-app beendet

```
cd notification-worker
.venv\Scripts\python.exe worker.py
```

Log-Transkript (Zeitstempel Original, Prozessliste jeweils parallel geprüft):

```
[2026-07-12T20:19:54] notification-worker started, polling http://127.0.0.1:3000 every 30s
[2026-07-12T20:19:54] 1 open task(s): ['Process independence proof task']
[2026-07-12T20:19:58] Could not send weekly review email via localhost:1025: [WinError 10061] ...
[2026-07-12T20:20:02] Could not check for replies via POP3 at localhost:1110: [WinError 10061] ...
```

(Mailpit war für diesen Test absichtlich nicht gestartet — zusätzlicher Beleg, dass der Worker auch den Ausfall einer *dritten* Abhängigkeit sauber übersteht, nicht nur core-app. Nicht der Kern dieses Nachweises, aber eine kostenlose Zusatzbeobachtung.)

**core-app beendet** (`Stop-Process`, hart, kein Shutdown-Signal an den Prozess):

```
[2026-07-12T20:20:34] Could not reach core-app at http://127.0.0.1:3000: <urlopen error [WinError 10061] ...>
[2026-07-12T20:20:38] Could not check for replies via POP3 at localhost:1110: [WinError 10061] ...
[2026-07-12T20:21:10] Could not reach core-app at http://127.0.0.1:3000: <urlopen error [WinError 10061] ...>
[2026-07-12T20:21:14] Could not check for replies via POP3 at localhost:1110: [WinError 10061] ...
```

Worker-Prozess zu diesem Zeitpunkt per Prozessliste bestätigt: weiterhin aktiv, kein Absturz, keine Exception, die den Prozess beendet — er loggt den Fehler und schläft bis zum nächsten Zyklus, exakt wie in `fetch_open_tasks()`/`check_for_replies()`/`send_review_email()` implementiert (`try`/`except URLError`/`OSError`, kein unbehandelter Fehler).

**core-app neu gestartet** (ohne den Worker anzufassen):

```
[2026-07-12T20:21:44] 1 open task(s): ['Process independence proof task']
[2026-07-12T20:21:48] Could not send weekly review email via localhost:1025: [WinError 10061] ...
```

**Ergebnis:** Der Worker verbindet sich beim nächsten regulären Poll-Zyklus automatisch wieder — keine manuelle Aktion am Worker-Prozess nötig. Zusätzlich bestätigt: der während des Ausfalls angelegte Task ("Process independence proof task") ist nach dem Neustart weiterhin vorhanden (`GET /api/tasks` geprüft) — SQLite-Datei überlebt den Prozess-Neustart unversehrt, keine Datenverluste durch den harten Kill.

## Warum das die Anforderung erfüllt

- **Getrennte OS-Prozesse:** eigene PID, eigenes `.venv`, eigenes `requirements.txt` je Prozess (seit Schritt 1/5).
- **Kein Shared-State außer HTTP:** kein gemeinsames Python-Modul, keine gemeinsame Datenbankverbindung — `notification-worker` kennt core-app ausschließlich über `CORE_APP_URL` und redet nur über REST/JSON mit ihm.
- **Kein Absturz bei Ausfall der Gegenseite:** beide Richtungen geprüft (core-app läuft ohne Worker; Worker läuft ohne core-app), jeweils mit sauberer Fehlerbehandlung statt unbehandelter Exception.
- **Automatische Wiederherstellung ohne manuellen Eingriff:** einmal gestartet, braucht der Worker nach einem Ausfall der Gegenseite keinen Neustart.

## Was für die Abgabe noch fehlt

`00-tooling-and-process-independence.md` verlangt für Stufe 1 explizit ein **Screenshot oder kurzes GIF** als zentralen Beleg — dieser Schritt liefert stattdessen einen vollständigen, reproduzierbaren **Text-Nachweis** (Log-Transkript + Prozesslisten-Prüfung). Screenshots des Browser-Fensters ließen sich in dieser Session technisch nicht zuverlässig aufnehmen (das Screenshot-Werkzeug lief während der gesamten Session wiederholt in Timeouts, unabhängig vom eigentlichen App-Zustand). Funktionale Prüfung (Seiteninhalt lesen, Formulare ausfüllen, Task tatsächlich anlegen) wurde stattdessen als Ersatz genutzt und ist inhaltlich mindestens gleichwertig, aber kein Bildmaterial für die Abgabe.

**Für die eigentliche Abgabe empfohlen:** Dieselbe Sequenz einmal selbst mit Bildschirmaufnahme (z. B. Windows' `Win+Alt+R` oder ShareX) wiederholen — der komplette Ablauf ist oben exakt dokumentiert und in dieser Session mehrfach reproduziert worden, dauert in der Praxis nur 2–3 Minuten:
1. core-app starten, im Browser einen Task anlegen (zeigt: core-app allein funktionsfähig).
2. Worker starten, kurz warten (zeigt: beide zusammen).
3. core-app-Terminal schließen/`Strg+C` (zeigt: Worker-Log läuft weiter, loggt Fehler statt abzustürzen).
4. core-app neu starten (zeigt: Worker verbindet sich von selbst wieder, kein Neustart nötig).

## Nächster Schritt

Alle in `03-mvp-requirements-checklist.md` als "Must" markierten Punkte aus CHKP und REVIEW sind jetzt entweder abgehakt oder (REVIEW-NFR-002) inhaltlich nachgewiesen, nur das visuelle Abgabe-Material steht noch aus. Optional laut Bau-Reihenfolge: Schritt 10, Eisenhower-Filter + Buddy-Eskalation (ESC-Block, mehrheitlich Should/Could) — oder Rückkehr zur Dashboard-Sortierung nach Fokus-Tasks (siehe `backlog.md`), je nach Priorität.
