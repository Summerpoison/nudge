# Nudge MVP — Atomare Anforderungen (Scoped Checkliste)

**Zweck:** Konkrete, testbare Einzelanforderungen für den tatsächlich gebauten Scope (Teil B + Teil C). Kein vollständiges RE-Dokument nach IEEE-830-Standard — das wäre für diesen Projektumfang Overkill (siehe RE-Audit, Abschnitt 4.2: ~80 Anforderungen für das *gesamte* Original-Spec, hier nur der MVP-Ausschnitt). ID-Schema übernommen aus `re-audit_adhd-proof-workflow-spec_v2.md`.

**Format:** `[MODUL]-[TYP]-[NUMMER]` — TYP ist `FUNC` (funktional) oder `NFR` (nicht-funktional). Priorität nach MoSCoW.

---

## CHKP — Checkpoint & Task-System (Teil B, Kern-App)

- [x] **CHKP-FUNC-001** (Must) — Beim Anlegen eines Tasks MUSS der Nutzer folgende Felder angeben: Task-Name, externes Deadline. Buffer-Deadline und Checkpoints (50%/75%) werden automatisch berechnet, sind aber überschreibbar. *(Schritt 2)*
- [x] **CHKP-FUNC-002** (Must) — Die Buffer-Deadline wird berechnet als `task_creation_date + 0.7 × (external_deadline − task_creation_date)`. *(Aufgelöst in RE-Audit 3.2 — Bezugsgröße ist das Erstellungsdatum, nicht "heute". Schritt 2.)*
- [x] **CHKP-FUNC-003** (Must) — Checkpoint 1 liegt bei 50%, Checkpoint 2 bei 75% der verfügbaren Zeit (Default, überschreibbar). *(Schritt 2 — "verfügbare Zeit" als Buffer-Fenster ausgelegt, siehe `05-step2-task-model.md`.)*
- [x] **CHKP-FUNC-004** (Must) — Bei Checkpoint-Fälligkeit MUSS das System eine Nutzerinteraktion erfordern: entweder Artefakt-Einreichung (beliebiges Level: Strong/Medium/Minimal) ODER Triage-Auswahl (A/B/C/D). Ein reines Abhaken ohne eine der beiden Formen ist nicht zulässig. *(Aufgelöst in RE-Audit 3.1. Schritt 4.)*
- [x] **CHKP-FUNC-005** (Must) — Der Nutzer wird NICHT am Fortfahren gehindert, sobald eine der beiden Interaktionsformen aus CHKP-FUNC-004 abgeschlossen ist. Kein Blocking-Zustand im UI. *(Schritt 4 — Check-in-Button immer erreichbar, nur visuell hervorgehoben.)*
- [x] **CHKP-FUNC-006** (Must) — Blocker-Triage bietet exakt vier Optionen (A: Sprint starten, B: Stuck/Hilfe nötig, C: Warte auf jemanden, D: Scope/Deadline-Problem), kein Freitext als Ersatz. *(Schritt 4.)*
- [x] **CHKP-FUNC-007** (Must) — Bei Triage-Option B, C oder D generiert das System einen vorausgefüllten Nachrichtenentwurf (Empfänger, Betreff, Text), den der Nutzer vor dem Versand bearbeiten kann. *(Schritt 4.)*
- [x] **CHKP-FUNC-008** (Must) — Der Versand des Entwurfs erfolgt über einen `mailto:`-Link (Standard-Mailprogramm des Nutzers), NICHT über einen im Tool integrierten Versand. Kein E-Mail-Konto-Login erforderlich für diesen Pfad. *(Schritt 4.)*
- [x] **CHKP-FUNC-009** (Must) — Nach Klick auf "Send" wird der betroffene Task optimistisch auf Status "On Hold" gesetzt (lokale Zustandsänderung, unabhängig vom tatsächlichen Mail-Versand). *(Schritt 4.)*
- [x] **CHKP-FUNC-010** (Should) — Der Nutzer kann einen "On Hold"-Task manuell wieder auf "aktiv" setzen. Kein automatisches Reply-Tracking für diesen Pfad (siehe REVIEW-Modul für den einzigen Pfad mit automatischem Tracking). *(Schritt 3.)*
- [x] **CHKP-FUNC-011** (Must) — Dashboard zeigt alle offenen Tasks mit Checkpoint-Datum und Status in einer Übersicht. *(Schritt 3.)*
- [x] **CHKP-FUNC-012** (Must) — Task-Detail-Ansicht zeigt Historie, aktuellen Status und Ort für Artefakt-Einreichung für einen einzelnen Task. *(Schritt 3.)*
- [x] **CHKP-NFR-001** (Must) — Kein im System gespeichertes "Inbox"- oder "Drafts"-Objekt mit eigenem Lifecycle. Entwürfe sind Wegwerf-Artefakte (siehe `01-communication-architecture.md`).
- [ ] **CHKP-NFR-002** (Won't, MVP) — Keine Kontakt-/Mitbearbeiter-Verwaltung, keine Zuständigkeiten-Zuweisung im Tool.

## REVIEW — Weekly Review Loop (Teil C, Notification-Worker)

- [x] **REVIEW-FUNC-001** (Must) — Der Notification-Worker läuft als eigenständiger, unabhängig startbarer Prozess (separater OS-Prozess, kein Modul im Kern-App-Prozess). *(Schritt 5.)*
- [x] **REVIEW-FUNC-002** (Must) — Der Worker fragt periodisch (Cron-Trigger) per REST-Polling die Kern-App-API nach offenen Fokus-Tasks ab. *(Schritt 5 — pollt aktuell alle aktiven Tasks, da der Fokus-Task-Begriff erst mit REVIEW-FUNC-006 entsteht, siehe `08-step5-notification-worker-skeleton.md`.)*
- [x] **REVIEW-FUNC-003** (Must) — Der Worker verschickt eine E-Mail mit allen offenen Tasks (Checkpoint-Datum, Status), einer eindeutigen Referenz (Message-ID oder Task-IDs im Betreff) zur späteren Zuordnung der Antwort. *(Schritt 6.)*
- [x] **REVIEW-FUNC-004** (Must) — Der Worker fragt per IMAP NUR nach Antworten auf den referenzierten Thread ab (kein genereller Inbox-Zugriff/keine generische Inbox-UI). *(Schritt 7 — per `poplib` statt `imaplib`, da Mailpit keinen IMAP-Server anbietet; mit Nutzerin abgestimmt, siehe `10-step7-reply-parsing.md`.)*
- [x] **REVIEW-FUNC-005** (Must) — Die Antwort-Mail wird regelbasiert geparst (Task-IDs/Zeilen-Matching, kein KI-Modell in der MVP-Basisversion), um die Top-3-Priorität zu extrahieren. *(Schritt 7.)*
- [x] **REVIEW-FUNC-006** (Must) — Die extrahierte Priorisierung wird per REST-Call an die Kern-App zurückgespielt und dort als "Fokus-Tasks der Woche" markiert. *(Schritt 8.)*
- [ ] **REVIEW-FUNC-007** (Should) — Fällige Checkpoint-Reminder für Fokus-Tasks werden gebündelt (ein täglicher Digest statt Einzel-Reminder pro Task).
- [ ] **REVIEW-FUNC-008** (Must) — Reminder/aktive Benachrichtigungen beziehen sich AUSSCHLIESSLICH auf die aktuell committeten Fokus-Tasks, nicht auf alle Tasks im System.
- [ ] **REVIEW-FUNC-009** (Should) — Sind alle Fokus-Tasks vor Zyklusende erledigt, bietet das System eine vorzeitige Neu-Priorisierung an, erzwingt sie aber nicht.
- [x] **REVIEW-NFR-001** (Must) — Der Worker nutzt für SMTP/IMAP ausschließlich Python-Standardbibliothek (`smtplib`, `imaplib`) — keine externen E-Mail-Abhängigkeiten. *(`smtplib` wie spezifiziert; für den Empfang `poplib` statt `imaplib` — ebenfalls Standardbibliothek, siehe REVIEW-FUNC-004-Anmerkung. Keine externe Abhängigkeit in beiden Fällen.)*
- [ ] **REVIEW-NFR-002** (Must) — Kern-App und Worker sind unabhängig voneinander lauffähig: Ausfall eines Prozesses darf den anderen nicht zum Absturz bringen (nachgewiesen durch manuellen Test, siehe `00-tooling-and-process-independence.md`). *(Textueller Nachweis in Schritt 9 abgeschlossen, siehe `12-step9-process-independence-proof.md` — vollständiges Log-Transkript beider Ausfallrichtungen. Nur das für die Abgabe geforderte visuelle Material (Screenshot/GIF) steht noch aus, daher hier bewusst noch unchecked.)*

## ESC — Eisenhower-Filter & Eskalation (Teil C, Erweiterung)

- [x] **ESC-FUNC-001** (Must) — Jeder Task hat einen berechneten (nicht manuell gesetzten) Zustand "Urgent" ja/nein, basierend auf Restzeit bis Buffer-Deadline (Default-Schwellenwert: < 3 Tage). *(Schritt 10a — `is_urgent()`, reine Funktion, kein gespeichertes Feld. Kein "Important"-Feld eingeführt, siehe `13-step10a-dashboard-and-eisenhower.md`.)*
- [x] **ESC-FUNC-002** (Must) — Nur Tasks im Zustand "Important + Urgent" lösen die volle Eskalationskette (Reminder, ggf. Buddy-Alert) aus. "Important + Not Urgent"-Tasks werden getrackt, aber ohne aktive Benachrichtigung. *(Schritt 10c — kein separates "Important"-Feld, siehe 10a; Gate ist `is_urgent()` plus die Checkpoint-Miss-Regel aus `needs_buddy_alert()`.)*
- [x] **ESC-FUNC-003** (Should) — Der Urgent-Schwellenwert ist in den Settings konfigurierbar (Default-Wert reicht für MVP-Funktionalität). *(Schritt 10b.)*
- [x] **ESC-FUNC-004** (Should) — Ein hinterlegter Accountability-Buddy-Kontakt (Settings) wird bei Eskalationsstufe 3 (75%-Checkpoint verpasst / Buffer-Deadline überschritten) für "Important + Urgent"-Tasks automatisch benachrichtigt. *(Schritt 10c — verschärft gegenüber dem ursprünglichen Wortlaut: Alert erst wenn beide Checkpoints ohne Interaktion verstrichen sind, ODER die Buffer-Deadline selbst überschritten ist; mit Nutzerin abgestimmt, siehe `15-step10c-buddy-system.md`.)*
- [x] **ESC-FUNC-005** (Should) — Die Buddy-Benachrichtigung enthält nur "Task X braucht Aufmerksamkeit", keine vollen Task-Details. *(Schritt 10c.)*
- [ ] **ESC-FUNC-006** (Could) — Pro-Task individualisierbare Urgent-Schwellenwerte.
- [ ] **ESC-FUNC-007** (Could) — Live-Neuberechnung des Eisenhower-Quadranten bei jedem App-Öffnen statt nur im täglichen Cron-Durchlauf.

---

## Bewusst nicht atomarisiert (außerhalb MVP-Scope)

Diese Bereiche aus dem RE-Audit bleiben unangetastet, weil die zugehörigen Module nicht Teil von B/C sind:
- Modul 3 (Time Tracker) — Schwellenwerte für "suspiciously long" Timer etc.
- Modul 5 (Panic Mode) — Trigger-Schwellenwerte, vier Notfall-Fragen
- Vollständiger NFR-Katalog (Datenschutz/DSGVO, Internationalisierung, Barrierefreiheit, Backup)
- Datenlöschung/Archivierung

**Begründung für den Bericht:** Bewusste Scope-Entscheidung, kein Vollständigkeits-Versäumnis — konsistent mit der Design-Safeguard "Build one module at a time" aus dem Original-Spec.
