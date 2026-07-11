# Design Decision: Kommunikationsarchitektur (Mensch↔Mensch vs. Mensch↔System)

**Status:** Design entschieden, MVP-relevant
**Kontext:** Ausgelöst durch die Frage, wie der "I'm Blocked"-Screen (Blocker-Triage, Modul 1) und der Weekly-Review-Loop (Modul 4) mit E-Mail umgehen sollen, ohne dass Nudge zu einem generischen Collaboration-/Inbox-Tool wird.

---

## 1. Der Kernunterschied: zwei verschiedene E-Mail-Situationen

Nudge hat zwei strukturell unterschiedliche Kommunikationsmuster, die denselben UI-Baustein ("E-Mail draften") teilen und dadurch leicht vermischt werden:

| | Fall 1: Blocker-Draft | Fall 2: Weekly-Review-Loop |
|---|---|---|
| **Art** | Mensch-zu-Mensch | Mensch-zu-System |
| **Beispiel** | "I'm Blocked" → Draft an Teamlead | Montags-Mail mit Prio-Abfrage |
| **Wer liest die Antwort?** | Der Empfänger (Teamlead), nicht Nudge | Nudge selbst (muss geparst werden) |
| **Braucht verbundenes E-Mail-Konto?** | Nein | Ja (SMTP zum Senden, IMAP zum Empfangen) |
| **Nudge nach dem Senden noch beteiligt?** | Nein, Konversation läuft extern weiter | Ja, aktiv Teil des Rückkanals |

**Konsequenz:** Diese beiden Fälle müssen architektonisch getrennt behandelt werden, nicht über einen gemeinsamen "E-Mail-Feature"-Layer.

## 2. Lösung für Fall 1 (Blocker-Draft)

- **Kein Account-Login/Konto-Verbindung erforderlich.**
- "Send & Pause Task" öffnet einen `mailto:`-Link mit vorausgefülltem To/Subject/Body im Standard-Mailprogramm des Nutzers. Der tatsächliche Versand passiert außerhalb von Nudge (Outlook, Gmail, etc.).
- Der Task wird beim Klick optimistisch auf "On Hold" gesetzt — das Draften + Klicken ist der Commitment-Moment, nicht der tatsächliche SMTP-Versand.
- **Kein automatisches Reply-Tracking für diesen Fall.** Der Nutzer setzt den Task manuell wieder auf "aktiv", wenn die Antwort kam. (Reply-Monitoring bleibt exklusiv Modul 4 vorbehalten, siehe unten.)

**Löst:** Das ursprüngliche Problem "was, wenn jemand kein E-Mail-Konto verbinden will/kann/darf" — für diesen Use Case muss niemand ein Konto verbinden, weil Nudge hier gar nicht selbst sendet.

## 3. Lösung für Fall 2 (Weekly-Review-Loop)

- Braucht zwingend ein verbundenes Konto (SMTP + IMAP), weil Nudge die Antwort aktiv lesen und verarbeiten muss.
- **Kein generisches Inbox-Feature.** Stattdessen ein schmaler, zweckgebundener "Reply-Catcher": Der Notification-Worker verschickt die Montags-Mail mit eindeutiger Referenz (Message-ID oder Task-IDs im Betreff), fragt periodisch per IMAP *nur* nach Antworten auf genau diesen Thread ab, ignoriert alles andere im Postfach.
- Ursprüngliche Design-Intention bleibt erhalten: den Nutzer dort abholen, wo er ohnehin arbeitet (E-Mail-Programm), statt ihn zu zwingen, ständig die App zu öffnen.

## 4. Bewusst NICHT gebaut: generische Inbox/Collaboration-Features

**Beobachtung während der GUI-Entwicklung mit Google Stitch:** Stitch schlug in mehreren Screen-Varianten von sich aus Features vor, die dem eigentlichen Tool-Charakter widersprechen — u.a. eine "Inbox"/"Drafts"-Ansicht, Kontaktverwaltung, Zuständigkeiten und Mitbearbeiter-Zuweisung. Diese Vorschläge implizieren eine Verschiebung der Kommunikation ins Tool selbst und damit einen Collaboration-/Project-Management-Charakter (Kanban-artig), der explizit nicht das Ziel von Nudge ist — Nudge ist ein Solo-Tool.

**Einordnung für den Bericht:** Das ist ein legitimer, dokumentationswürdiger Kritikpunkt an KI-generierten GUIs — das Tool schlägt nicht "was inhaltlich passt", sondern "was in den Trainingsdaten am häufigsten als Task-Tool-UI vorkommt" (generische SaaS-Pattern). Das aktive Dagegenhalten (Features bewusst nicht übernehmen) ist Teil des "jeden Code verstehen"-Nachweises — es zeigt, dass das Tool geführt wird, nicht umgekehrt.

**Konkrete Abgrenzung:**
- Kein Inbox-Screen
- Keine im System gespeicherten Drafts mit eigenem Lifecycle — Drafts sind Wegwerf-Artefakte, die per `mailto:` an den Nutzer übergeben werden
- Keine Kontakt-/Mitbearbeiter-Verwaltung
- Jedes dieser Features hätte den Scope Richtung "eigentlich baue ich jetzt doch ein kleines Asana" verschoben — außerhalb des Aufgaben- und Projektrahmens

---

## Zusammenfassung für die Architektur-Legende

Zwei separate, unabhängig voneinander funktionierende Kommunikationskanäle:
1. **Blocker-Draft** — rein clientseitig (`mailto:`), kein Backend-Bezug zum E-Mail-Versand
2. **Weekly-Review-Loop** — serverseitig über den Notification-Worker, mit gezieltem (nicht generischem) IMAP-Polling auf einen einzelnen erwarteten Antwort-Thread

Diese Trennung ist zugleich ein Beispiel für bewusste Scope-Kontrolle gegenüber einem KI-Codegenerierungstool, das ungefragt Zusatzfunktionalität vorschlägt.
