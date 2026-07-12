# Step 4: Blocker-Triage und Mail-Draft

**Status:** Abgeschlossen
**Bezug:** CHKP-FUNC-004 bis 009, CHKP-FUNC-010 (Wiedereröffnung war bereits in Schritt 3 vorhanden). Screen-Grundlage und Vier-Optionen-Entscheidung siehe `02c-screen-audit-and-design-decisions.md`.

---

## Was gebaut wurde

```
core-app/
├── templates/
│   ├── checkin.html    Checkpoint-Interaktion: Submit Proof / I'm Blocked
│   ├── triage.html      Vier Optionen (Timer, Stuck, Waiting, Scope)
│   └── timer.html       10-Minuten-Fokus-Timer (Option A)
├── models.py            + is_checkpoint_due()
└── app.py               + /checkin, /triage, /triage/timer, /timer Routen
```

### Flow

```
Task-Detail --(Check In)--> Check-in --(Submit Proof)--> Upload (Schritt 3, wiederverwendet)
                               |
                          (I'm Blocked)
                               v
                            Triage --(Start 10-Min-Timer)--> Timer-Seite
                               |
                    (Stuck / Waiting / Scope)
                               v
                        Mail-Entwurf (bearbeitbar)
                               |
                      (Send & Pause Task)
                               v
                  mailto:-Link öffnet + Status -> On Hold
```

### Check-in-Screen (`checkpoint_q4_report`-Basis)

Zwei gleichwertige Karten: "Submit Proof" (Inline-Upload-Formular, postet an dieselbe Route wie in Schritt 3 — kein neuer Code nötig, nur eine zweite Stelle, von der aus dasselbe Formular erreichbar ist) und "I'm Blocked" (Link zur Triage). Direkt erreichbar über einen "Check In"-Button auf der Task-Detail-Seite, der hervorgehoben wird, sobald ein Checkpoint erreicht ist (`is_checkpoint_due()` in `models.py`: `now >= checkpoint_1 or now >= checkpoint_2`).

**Entscheidung zu CHKP-FUNC-004/005:** Der "Check In"-Button ist *immer* erreichbar, nicht nur bei fälligem Checkpoint — er wird nur visuell hervorgehoben (gefüllter statt outline-Button, Text "Checkpoint reached"), wenn ein Checkpoint erreicht ist. Kein Blocking-Zustand, kein erzwungenes Modal — konsistent mit CHKP-FUNC-005 ("kein Blocking-Zustand im UI") und mit dem Fehlen einer automatisierten Checkpoint-Überwachung (die kommt erst mit dem Notification-Worker in Teil C). Die Nutzerin sieht die Aufforderung, wird aber nicht daran gehindert, weiterzuarbeiten, ohne sie anzuklicken.

### Triage-Screen (`triage_what_s_blocking_you`-Basis, um Option A erweitert)

Vier Optionen exakt nach CHKP-FUNC-006:
- **A — Sprint starten:** "Start 10-Minute Timer to get started now", eigener Button oberhalb der drei Nachrichten-Optionen (Nutzerinnen-Entscheidung aus `02c-...md`). Löst **keinen** Mail-Entwurf aus (nur B/C/D tun das, siehe CHKP-FUNC-007: "Bei Triage-Option B, C oder D"). Postet an `/triage/timer`, protokolliert ein Activity-Log-Ereignis und leitet zur Timer-Seite weiter.
- **B/C/D** ("Stuck / need help", "Waiting on someone", "Scope or deadline problem"): Klick auf eine der drei Karten blendet per JavaScript ein vorausgefülltes Entwurfsformular ein (Empfänger/Betreff/Text), analog zum JS-Muster der Stitch-Vorlage — die drei Textbausteine liegen als kleines JS-Objekt im Template, referenzieren den echten Task-Namen (`{{ task.name|tojson }}`, sicher für die Einbettung in JavaScript).

**Kein gespeichertes Kontaktbuch:** Das Empfänger-Feld ist immer leer und muss von Hand ausgefüllt werden — konsistent mit CHKP-NFR-002 (keine Kontakt-/Mitbearbeiterverwaltung). Die generierten Texte sind reine Vorschläge, vollständig editierbar vor dem Versand (CHKP-FUNC-007).

### Versand (CHKP-FUNC-008/009)

Der "Send & Pause Task"-Button ist ein normaler Formular-Submit-Button. Ein `submit`-Event-Listener baut zusätzlich einen `mailto:`-Link aus den *aktuellen* (ggf. bearbeiteten) Feldwerten und öffnet ihn per `window.open(...)` — der eigentliche Versand läuft komplett im Mailprogramm der Nutzerin, Nudge selbst verschickt nichts (kein SMTP, kein Konto-Login für diesen Pfad, siehe `01-communication-architecture.md`). Parallel dazu läuft die normale Formular-Übermittlung an den Server weiter, die serverseitig **unabhängig davon**, ob die Mail tatsächlich verschickt wurde, den Status optimistisch auf `on_hold` setzt und ein Activity-Log-Ereignis schreibt. Das entspricht exakt CHKP-FUNC-009: "unabhängig vom tatsächlichen Mail-Versand".

### Timer-Seite (Option A)

Reiner Client-seitiger Countdown (`setInterval`, keine Server-Beteiligung nach dem initialen Ereignis-Log) — zeigt 10:00 herunterzählend, endet mit einer Abschlussmeldung. Keine erzwungene Dauer, keine serverseitige Durchsetzung — passend zum Grundprinzip "kein erzwungenes Verhalten" aus dem Original-Spec.

## Verifikation

Lokal im Browser durchgespielt (Testtask mit absichtlich nahem Deadline angelegt, damit beide Checkpoints sofort in der Vergangenheit liegen):

1. Task-Detail zeigt "Checkpoint reached — Check In" (hervorgehoben), sobald `now` einen Checkpoint überschreitet — vorher nur "Check In" (outline).
2. Check-in-Screen → "I'm Blocked" → Triage-Screen.
3. "Start 10-Minute Timer" → Weiterleitung zur Timer-Seite, Countdown läuft sichtbar herunter (9:58 nach dem ersten Tick), Status bleibt `active`, Activity-Log verzeichnet "Started a 10-minute focus timer".
4. "Waiting on someone" angeklickt → Entwurfsformular erscheint mit korrekt vorbefülltem Betreff ("Following up: Urgent Test Task"). Empfänger eingetragen, "Send & Pause Task" geklickt → Status wechselt zu `on_hold`, Activity-Log verzeichnet "Blocker triage (Waiting on someone): draft sent to marcus@example.com", "Resume Task"-Button erscheint danach auf der Task-Detail-Seite (Wiederverwendung der Schritt-3-Logik). Keine Konsolenfehler.
5. `GET /tasks/999/checkin`, `/triage`, `/timer` → jeweils `404`.

Server danach gestoppt, Testdatenbank gelöscht (nicht versioniert).

## Nachträge aus der Nutzerinnen-Review

Beim Durchklicken der Task-Detail-Seite wurden drei Layout-/Hierarchie-Probleme gefunden und behoben:

- **"Check In"-Button war nicht durchgängig breit:** `inline-flex` (passt sich am Inhalt an) durch `w-full flex items-center justify-center` ersetzt — betrifft beide Zustände (hervorgehoben bei fälligem Checkpoint, outline sonst).
- **Zu viele optisch gleiche gefüllte Accent-Buttons auf einer Seite:** "Mark Complete" von `bg-accent text-white` auf denselben Outline-Stil wie "Reopen Task" umgestellt (`border border-accent text-accent`). Damit bleiben auf der Task-Detail-Seite nur noch die tatsächlich primären Handlungen (Check-In bei fälligem Checkpoint, Submit Proof) visuell hervorgehoben; abschließende/verwaltende Aktionen (Mark Complete, Reopen Task) treten zurück. Bewusst nicht auf andere Seiten übertragen (Add Task, View Task, Resume Task, Send & Pause Task bleiben gefüllt) — nur dort geändert, wo es als Problem auffiel, keine ungefragte Ausweitung.
- **"Status"-Box enthielt keine Information, nur eine Aktion:** Die separate Status-Karte zeigte zusätzlich redundanten Text ("This task is on hold." / "Marked complete."), obwohl derselbe Zustand bereits im Status-Badge oben auf der Seite sichtbar ist. Status-Karte und Attachments-Karte zu einer gemeinsamen Sidebar-Karte zusammengelegt (Aktion oben, Trennlinie, Attachments darunter), redundante Textzeilen entfernt.

Verifiziert per JavaScript-Auswertung der berechneten Styles (nicht per Screenshot, da das Screenshot-Tool in dieser Session wiederholt Timeouts warf) — Breite, Hintergrundfarbe und Rahmenfarbe der Buttons direkt im DOM geprüft, sowie der komplette Mark-Complete-zu-Reopen-Task-Zyklus erneut durchgeklickt.

## Nächster Schritt

Schritt 5: Notification-Worker-Grundgerüst als separater Prozess (REVIEW-FUNC-001, 002) — eigenständiger Python-Prozess, der periodisch die Kern-App-API (`/api/tasks`) abfragt.
