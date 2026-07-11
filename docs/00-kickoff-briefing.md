# Nudge — Kickoff-Briefing für Claude Code

**Lies dieses Dokument vollständig, bevor du mit dem Coden beginnst.** Es fasst alle Design-Entscheidungen zusammen, die vor dieser Session getroffen wurden. Frag nach, statt eigene Annahmen zu treffen, wenn etwas unklar ist — insbesondere zum Scope (Abschnitt 2).

---

## 1. Projektüberblick

**Nudge** ist ein persönliches ADHD-freundliches Task-/Checkpoint-Tool für eine Einzelnutzerin (keine Mehrbenutzer-/Collaboration-Funktionalität geplant oder gewünscht). Es entsteht im Rahmen einer Hochschul-Abgabe mit zwei Anforderungen:

1. **Teil B:** Ein mittelgroßes, funktionierendes Pet-Project (die Kern-App).
2. **Teil C:** Ein **distributed** System — mindestens zwei unabhängige, separat lauffähige Prozesse, die über eine definierte Schnittstelle kommunizieren (nicht nur Frontend/Backend-Layering im selben Prozess).

Die Nutzerin muss am Ende **jede Zeile Code selbst erklären können** (mündliche Prüfung, 15 Minuten, kurz nach Abgabe). Baue deshalb in kleinen, nachvollziehbaren Schritten und dokumentiere jeden Schritt in einer eigenen MD-Datei (siehe Abschnitt 5).

## 2. Scope — was gebaut wird und was explizit nicht

### Teil B: Kern-App
- Checkpoint-/Task-Verwaltung nach dem Modell aus `03-mvp-requirements-checklist.md`, Abschnitt CHKP
- Screens: Dashboard, Check-in, Triage + Mail-Draft, All-Tasks-Übersicht, einzelne Task-Ansicht, Settings, Add-Task (Rohfassung, darf im MVP simpel bleiben)
- GUI-Basis liegt bereits vor als generierte HTML/Tailwind-Screens im Ordner `design-reference/` — diese sind Rohmaterial (Google Stitch), NICHT 1:1 zu übernehmen, sondern gezielt zu kombinieren (siehe Abschnitt 4)

### Teil C: Notification-Worker
- Eigenständiger Prozess nach dem Modell aus `03-mvp-requirements-checklist.md`, Abschnitt REVIEW
- Regelbasierte Prioritäts-Erkennung aus E-Mail-Antworten (KEINE KI-Verarbeitung in dieser Version — das ist eine bewusst spätere, optionale Erweiterung, siehe Abschnitt 7)
- Eisenhower-Filter + Eskalations-/Buddy-Logik nach `03-mvp-requirements-checklist.md`, Abschnitt ESC (teilweise Should, nicht alles Must — Prioritäten dort beachten)

### Explizit NICHT bauen (auch wenn es sich beim GUI-Referenzmaterial anbietet)
- Kein Inbox-/Drafts-Feature mit eigenem Datenmodell im Tool
- Keine Kontakt-/Mitbearbeiter-/Zuständigkeits-Verwaltung
- Keine Mehrbenutzer-Funktionalität
- Keine KI-Integration in der Erstversion
- **Wichtig:** Die generierten GUI-Referenzscreens enthalten teils Elemente wie "Inbox" oder "Drafts" in der Navigation — das ist ein bekanntes Artefakt des Generierungstools (siehe `01-communication-architecture.md`, Abschnitt 4) und soll NICHT übernommen werden, auch wenn es im Referenzmaterial auftaucht.

Begründung für diesen Scope-Cut, falls relevant: `02b-eisenhower-buddy-design.md`, letzter Abschnitt ("Leitprinzip für den Cut").

## 3. Architektur

**Zwei unabhängige Prozesse, kein Docker** (Begründung: `00-tooling-and-process-independence.md`):

```
nudge/
├── core-app/              ← Teil B
│   ├── app.py              (Flask)
│   ├── templates/          (aus design-reference/ abgeleitete Jinja2-Templates)
│   └── static/
├── notification-worker/   ← Teil C
│   └── worker.py           (Python, stdlib smtplib/imaplib)
├── design-reference/       ← unveränderte Stitch-Exporte, nur zum Nachschlagen
├── docs/                   ← Schritt-für-Schritt-Dokumentation (siehe Abschnitt 5)
└── README.md
```

- **Kommunikation:** REST-Polling. Der Worker fragt die Kern-App-API periodisch ab (kein Message-Queue-System, das wäre für diesen Scope überdimensioniert — siehe `00-tooling-and-process-independence.md`, Punkt 4).
- **Start:** Beide Prozesse werden separat gestartet (zwei Terminals), nicht über Docker Compose. Docker ist bewusst kein Bestandteil dieser Version.
- **E-Mail-Testing:** Mailpit als lokaler SMTP/IMAP-Fake (siehe `00-tooling-and-process-independence.md`, Punkt 2) — kein Versand an echte Adressen während der Entwicklung.

## 4. Tech-Stack

- **Sprache:** Python durchgängig für beide Prozesse (Begründung: stdlib-Unterstützung für SMTP/IMAP im Worker, spätere Ollama-Anbindung, ein Sprachkontext statt zwei — Nutzerin muss beides in der Prüfung erklären können)
- **Kern-App-Backend:** Flask + Jinja2-Templates
- **Frontend:** Kein React/SPA-Framework. Die Stitch-Exporte (statisches HTML/Tailwind CDN/Vanilla JS) werden zu Jinja2-Templates umgebaut (hartkodierte Werte → `{{ variable }}`), keine vollständige Neuimplementierung
- **Worker:** Reines Python-Skript, `smtplib`/`imaplib` aus der Standardbibliothek, Cron-artiger Trigger (z. B. `schedule`-Library oder einfache Loop mit `time.sleep`)
- **API zwischen den Prozessen:** Einfache REST-Endpunkte in Flask (kein separates API-Framework nötig)

## 5. Arbeitsweise: kleine Schritte, MD-Doku pro Schritt

Die Nutzerin hat bereits ein Requirements-Engineering-Dokument (`re-audit_adhd-proof-workflow-spec_v2.md`) und eine gescopte Anforderungsliste (`03-mvp-requirements-checklist.md`). **Arbeite diese Checkliste ab, ein sinnvoller Block pro Schritt**, nicht alles auf einmal generieren.

Für jeden Schritt:
1. Kurz ankündigen, was gebaut wird und warum (Bezug auf die jeweilige Anforderungs-ID, z. B. CHKP-FUNC-001–003)
2. Code schreiben
3. Eine MD-Datei unter `docs/` anlegen, die den Schritt zusammenfasst: was wurde gebaut, welche Entscheidungen wurden getroffen, welche Anforderungs-IDs sind damit erfüllt

Vorschlag für die Reihenfolge (aus `03-mvp-requirements-checklist.md` abgeleitet):
1. Projekt-Setup (Ordnerstruktur, Flask-Grundgerüst, erste Route)
2. Task-Datenmodell + CHKP-FUNC-001 bis 003 (Task anlegen, Buffer/Checkpoint-Berechnung)
3. Dashboard- und Task-Detail-Views (CHKP-FUNC-011, 012)
4. Blocker-Triage + Mail-Draft (CHKP-FUNC-004 bis 009)
5. Notification-Worker-Grundgerüst als separater Prozess (REVIEW-FUNC-001, 002)
6. E-Mail-Versand + Mailpit-Anbindung (REVIEW-FUNC-003)
7. Reply-Parsing, regelbasiert (REVIEW-FUNC-004, 005)
8. Rückspielen der Priorisierung in die Kern-App (REVIEW-FUNC-006)
9. Nachweis der Prozess-Unabhängigkeit (REVIEW-NFR-002) — manueller Test + Screenshot/GIF
10. Optional, falls Zeit bleibt: Eisenhower-Filter + Buddy-Eskalation (ESC-Block)

**Jeder Schritt muss "in einer Session funktionsfähig" sein** (Design-Prinzip aus dem Original-Spec: "Each module must be usable within one build session"). Wenn ein Schritt zu groß wird, weiter unterteilen statt einen Zwischenzustand als "fertig" zu markieren.

## 6. Referenzdokumente (im Repo, bitte vor Bezugnahme lesen)

- `00-tooling-and-process-independence.md` — Docker-Verzicht, Mailpit, Unabhängigkeitsnachweis, Toolwahl
- `01-communication-architecture.md` — Warum es zwei getrennte Kommunikationskanäle gibt (Mensch↔Mensch vs. Mensch↔System), warum kein Inbox-Feature
- `02b-eisenhower-buddy-design.md` — Eisenhower-Filter, Reminder-Bündelung, Buddy-System, MoSCoW-Begründung
- `03-mvp-requirements-checklist.md` — die atomare Anforderungsliste, an der sich der Bau-Fortschritt orientiert
- `re-audit_adhd-proof-workflow-spec_v2.md` — vollständiges RE-Audit des Original-Spec (nur die MVP-relevanten Punkte daraus sind in Abschnitt 3.1/3.2 bereits in die Checkliste übernommen)

## 7. Bewusst spätere Erweiterung (nicht Teil dieses Kickoffs)

Falls nach Abschluss des MVP noch Zeit bleibt: KI-gestütztes Reply-Parsing als dritter, ebenfalls unabhängiger Prozess (lokales Modell via Ollama), das die regelbasierte Variante ergänzt, nicht ersetzt. Beide Varianten sollen dokumentiert und im Bericht als bewusster Trade-off (Zuverlässigkeit/Einfachheit vs. natürlichere Eingabe) gegenübergestellt werden. Bis dahin: **regelbasiert bauen, funktionsfähig bekommen, dokumentieren.**
