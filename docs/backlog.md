# Backlog: Bewusst zurückgestellte Ideen

Sammelstelle für Punkte, die während des Baus aufkamen, aber bewusst nicht in den MVP-Scope gezogen wurden — kein Vollständigkeits-Versäumnis, sondern dokumentierte Entscheidung (siehe `03-mvp-requirements-checklist.md`, Abschnitt "Bewusst nicht atomarisiert" für dasselbe Prinzip). Jeder Eintrag verlinkt zurück zu der Stelle, an der er aufkam, für den vollen Kontext. Lebendes Dokument — bei Bedarf ergänzen, bei Umsetzung hierher als "erledigt" markieren oder entfernen.

---

- [ ] **HTML-formatierte Review-Mail** statt reinem Plaintext (`notification-worker/worker.py`, `build_review_email`). Aufgeworfen nach Schritt 6. Würde z. B. echte visuelle Blöcke statt Trennlinien-Zeichen, anklickbare Task-Links zurück in die Kern-App etc. ermöglichen. Reiner Plaintext war für den MVP bewusst einfacher (kein HTML-Templating im Worker nötig, in jedem Mail-Client lesbar, leicht in der Prüfung zu erklären).

- [ ] **14-Tage-Fenster + Cap bei 10 dringendsten Tasks** für die Review-Mail, falls sich in der Praxis zeigt, dass die reine Block-Formatierung (Schritt 6) bei sehr vielen offenen Tasks nicht ausreicht. Siehe `09-step6-email-and-mailpit.md`, Abschnitt "Nachtrag aus der Nutzerinnen-Review" für die volle Abwägung gegen REVIEW-FUNC-003.

- [ ] **Deadline-lose Tasks** (Backlog-/Ideen-Objekttyp, nimmt nicht am Checkpoint-/Buffer-/Eisenhower-Mechanismus teil). Erste Designidee: automatischer Wiedervorlage-Reminder ca. einen Monat nach Anlage. Siehe `05-step2-task-model.md`, Abschnitt "Scope-Frage während Review".

- [ ] **KI-gestütztes Reply-Parsing** (lokales Modell via Ollama) als dritter, unabhängiger Prozess, ergänzend zum regelbasierten Parsing aus Schritt 7 — nicht als Ersatz. Siehe `00-kickoff-briefing.md`, Abschnitt 7.

- [ ] **Settings-Screen** (SMTP-Konfiguration fürs UI statt hartkodierter Konstanten in `worker.py`, Checkpoint-Intervall-Overrides, Urgent-Schwellenwert, Accountability-Buddy-Kontakt). Aktuell kein eigener Bau-Schritt dafür vorgesehen; SMTP-Zugangsdaten und Review-Intervall stehen bislang als Konstanten direkt im Worker-Code. Bezug: `02c-screen-audit-and-design-decisions.md` (welche Teile von `nudge_settings` grundsätzlich übernehmbar wären), ESC-FUNC-003/004 in `03-mvp-requirements-checklist.md`.

- [ ] **Eigener `/health`-Endpunkt für den Worker** (Ausbaustufe 2 des Unabhängigkeits-Nachweises). Aktuell reicht die manuelle Log-Beobachtung (Stufe 1) für die Abgabe. Siehe `00-tooling-and-process-independence.md`, Abschnitt 3, und `08-step5-notification-worker-skeleton.md`.

- [ ] **Umbenennen von Attachments** im Task-Detail. View + Delete decken das ursprüngliche Problem (unbrauchbare Originaldateinamen) ausreichend ab; Rename wäre zusätzlicher Komfort, kein Blocker.

- [ ] **Docker** als spätere Portfolio-Politur (nicht Voraussetzung für den Distributed-Nachweis). Siehe `00-tooling-and-process-independence.md`, Abschnitt 1.

- [ ] **ESC-FUNC-006** (Could) — Pro-Task individualisierbare Urgent-Schwellenwerte, statt nur eines globalen Default-Werts.

- [ ] **ESC-FUNC-007** (Could) — Live-Neuberechnung des Eisenhower-Quadranten bei jedem App-Öffnen statt nur im täglichen Cron-Durchlauf.

- [ ] **Dashboard-Sortierung nach Fokus-Tasks** statt nur nach frühester Buffer-Deadline. Aufgeworfen nach Schritt 8 (`is_focus_task` existiert jetzt) — aktuell nur als Badge sichtbar, beeinflusst die Reihenfolge auf Dashboard/All-Tasks nicht. Siehe `11-step8-focus-task-writeback.md`.
