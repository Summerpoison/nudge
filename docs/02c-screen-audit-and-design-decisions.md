# Design Decision: Screen-Audit der Google-Stitch-Exports & Umsetzungsentscheidungen

**Status:** Entschieden, MVP-relevant
**Kontext:** Vor Schritt 3 (Dashboard- und Task-Detail-Views) wurden alle 15 Stitch-Exporte (`design-reference/google_stitch/`, zwei Generierungsdurchläufe: `stitch_nudge_smart_deadline_manager` und `stitch_nudge_stress_free_task_manager`) einzeln gesichtet. Grund: starke Inkonsistenz zwischen den Screens und wiederholt eingeschleuste Out-of-Scope-Features (Inbox/Drafts, Kontaktverwaltung, Multi-User-Signale). Dieses Dokument hält fest, welche Screens als Ausgangspunkt dienen, was verworfen wird und warum.

---

## 1. Warum die Exporte inkonsistent sind

Die beiden Ordner sind keine Variationen *eines* Designsystems, sondern zwei separate Stitch-Generierungen mit unterschiedlichem Prompt-Ziel (Nutzerin: zweiter Durchlauf sollte "weniger zen" werden, driftete aber erneut ab). Das zeigt sich auch in den beiden `DESIGN.md`-Briefs:

- `smart_deadline_manager` ("Serene Focus"): **Modern Utility** — kantigere Formsprache (0.25–0.75rem Radius), Hanken Grotesk für Headlines + Inter für Body, Unterstrich-Navigation.
- `stress_free_task_manager` ("Serene Productivity"): **Organic Tactility** — Pill-Formsprache (1–3rem Radius), nur Inter, "Blob"-Pill-Navigation.

Jede der 15 `code.html`-Dateien bringt zusätzlich ihre eigene, automatisch generierte Tailwind-Konfiguration mit (~40 Farb-Tokens), die trotz gleicher Token-Namen (`primary`, `surface-container-lowest`, …) unterschiedliche Hex-Werte je Datei enthält. Es gibt keine geteilte Komponentenbasis, auch nicht innerhalb eines Ordners.

**Entscheidung:** `smart_deadline_manager` (Modern Utility) ist die visuelle Basis für `base.html`. Statt der auto-generierten 40-Token-Paletten wird ein eigenes, kleines Farbschema aus vier von der Nutzerin vorgegebenen Werten gebaut:

| Rolle | Hex | Herkunft |
|---|---|---|
| Hintergrund / Level 0 | `#EEEEEE` | entspricht "Serene Focus"-Komponentenrichtlinie |
| Primäre Aktion (Buttons, aktive Zustände) | `#6FCF97` | Soft Green |
| Sekundär / Erfolg / Fortschritt | `#2FA084` | Seafoam Green |
| Text / Headlines | `#1F6F5F` | Deep Forest Green |

**Fonts:** Lexend (700/800) für Logo/Headlines, Inter für Fließtext (bereits durchgängig in den Exporten verwendet, gute Lesbarkeit in Kombination mit Lexend). Ein Logo/Vektorgrafik ist in Arbeit, noch nicht Teil dieses Schritts.

**Navigation:** Kein Export passt zu unserer tatsächlichen IA (alle enthalten Inbox/Drafts/Projects/Archive/Insights/History-Kombinationen, die nicht existieren). Eigene, schlanke Nav wird gebaut (Dashboard/All Tasks/Settings als Ausgangspunkt), erweiterbar für später geplante Features.

## 2. Bekanntes Artefakt: "Inbox"/"Drafts" (bereits in `01-communication-architecture.md` dokumentiert)

Bestätigt durch die Detailsichtung: `nudge_inbox` ist ein vollständiger GTD-Capture-Screen mit eigenem Datenmodell (rohe Strings, kein Deadline-/Checkpoint-Bezug), und der Nav-Eintrag "Drafts" taucht in 6 von 8 `stress_free_task_manager`-Screens als aktiver Sidebar-Punkt auf — fest im Chrome dieser Generierung verankert, kein Einzelfall. **Wird vollständig verworfen.**

## 3. Neu identifiziert: durchgängige Fake-Persona/Multi-User-Signale

Jeder Screen erfindet eine eigene, inkonsistente Nutzer-Identität mit KI-generiertem, extern gehosteten Avatar (`lh3.googleusercontent.com/aida-public/...`, Stitch/AIDA-Wegwerf-URLs): "Alex Chen", "Julian", "Elena Vance" (mit Tag "Premium Zen"), "Alex Rivera". Ein Screen zeigt zusätzlich ein "Pro Plan"-Badge. Das impliziert ein Multi-Tier-SaaS-Produkt — Widerspruch zum Solo-Tool-Scope (siehe `00-kickoff-briefing.md`, Abschnitt 1). **Wird aus allen übernommenen Screens entfernt**, kein Nutzer-Avatar/-Name/-Badge in der Navigation.

## 4. Screen-Mapping: was wird wie übernommen

| Screen (Quelle) | Ziel | Entscheidung |
|---|---|---|
| `checkpoint_q4_report` | Check-in-Screen (CHKP-FUNC-004) | Basis. Übergang direkt in `triage_what_s_blocking_you` bei "I'm Blocked" statt eigenem Freitext-Feld. |
| `triage_what_s_blocking_you` | Triage-Screen (CHKP-FUNC-006/007) | Basis, aber Optionen müssen komplett neu: aktuell nur 3 (B/C/D-artig), keine der drei Export-Varianten hat Option A. **Neue vierte Option oberhalb der drei Nachrichten-Optionen: "Start 10-Minute Timer"** (Pomodoro, führt direkt zum Task-Start statt zu einem Mail-Entwurf — einziger Triage-Pfad ohne Draft, siehe CHKP-FUNC-007 "bei Option B, C oder D"). |
| `nudge_check_in` (Modal-Variante) | — | Verworfen. Redundant zu `checkpoint_q4_report`, "Dismiss for 15 minutes"-Snooze war ungewollter Feature-Creep. |
| `ready_to_send` | — | Verworfen. `triage_what_s_blocking_you` deckt den Mail-Entwurfs-/Versand-Schritt bereits ab, kein zweiter Confirm-Screen nötig. |
| `nudge_triage_action`, `nudge_minimal_triage` | — | Verworfen (Duplikate von `triage_what_s_blocking_you` mit anderem Wortlaut, keine der drei hat Option A). |
| `nudge_dashboard` (smart_deadline) | All-Tasks-Übersicht (CHKP-FUNC-011, Teil) | Nicht als Hauptdashboard nutzbar (generische Prio-Queue + Kalender, kein Buffer-/Checkpoint-Bezug — Einfluss der Trevor-AI-Inspiration, siehe `design-reference/inspiration/`). Wird zur All-Tasks-Ansicht umgewidmet. Das Quick-Add-Eingabefeld am unteren Rand ist der eigentlich interessante Teil. |
| `nudge_dashboard` / `nudge_zen_dashboard` (stress_free) | — | Verworfen (Bento-Board mit Zitat-Karte und Fake-Gamification-Stats — erneuter "zu zen"-Ausreißer). Die "Buffer Remaining"-Progress-Bar-Idee wandert stattdessen in die Task-Detail-Ansicht statt prominent im Dashboard zu stehen. |
| `nudge_my_focus` | Hauptdashboard (CHKP-FUNC-011) | Basis, muss aber deutlich minimalistischer werden als im Export (weniger dekorative Elemente). |
| `nudge_task_overview_matrix` | Eisenhower-Gruppierung in All-Tasks (ESC-Block) | Guter visueller Referenzpunkt für später. Gruppierte Ansicht soll später Default werden — siehe Abschnitt 5 zur zeitlichen Einordnung. |
| `redesigned_task_detail` | Task-Detail (CHKP-FUNC-012) | Basis. Activity-Log-Timeline entspricht direkt der geforderten Historie, Attachments-Sektion direkt der Artefakt-Einreichung. Verworfen: Notes/Strategy-Freitextblock, Assignees/Team-Verwaltung (Kontakt-Feature, CHKP-NFR-002), "Studio Context"-Dekobild, "Request Extension"-Button (nirgends spezifiziert), Log-Eintrag "Buffer added based on focus patterns" (impliziert adaptive KI-Logik, die es nicht gibt). |
| `nudge_add_task` | Add-Task-Rohfassung | Basis (sauberstes, einfachstes Formular unter allen Exporten). Nav und "Priority"-Pill werden entfernt/ersetzt, echtes Datum/Zeit-Feld statt vager "Select time"-Pille. |
| `nudge_settings` | Settings | Nur zwei Sektionen übernommen: E-Mail-/SMTP-Konfiguration (wird vom Notification-Worker gebraucht) und Checkpoint-Intervalle 50%/75% (CHKP-FUNC-003-Override). Verworfen: Stakeholder-Contacts-Tabelle, Theme-Switcher, Sound-Auswahl, Datenexport/"Clear all data". |
| `nudge_inbox` | — | Verworfen, siehe Abschnitt 2. |

## 5. Zwei Scope-Fragen, mit Nutzerin geklärt

**Quick-Add-Syntax-Parser (All-Tasks-Screen):** Freitext-Eingabe mit automatischem Parsing von Deadline/Projekt (z. B. "Draft report by Friday 5pm #Work") wäre möglich, aber zusätzlicher Aufwand (Datums-Parsing-Ansatz, definierte Syntax). **Entscheidung:** Für den MVP ein einfaches Formular (Name + Datumsfeld), passend zur bestehenden Einstufung "Add-Task (Rohfassung, darf im MVP simpel bleiben)" aus `00-kickoff-briefing.md`. Der Parser wird als spätere Erweiterung dokumentiert, analog zur KI-Reply-Parsing-Erweiterung (`00-kickoff-briefing.md`, Abschnitt 7).

**Eisenhower-Gruppierung als Default in All-Tasks:** Die gruppierte gewünschte Standardansicht setzt die berechnete "Urgent"-Klassifizierung (ESC-FUNC-001) voraus — die Eisenhower-Logik ist im Bau-Reihenfolge-Vorschlag aber erst optionaler Schritt 10. **Entscheidung:** All-Tasks startet vorerst mit der einfachen Listenansicht als Default. Die gruppierte Ansicht bleibt UI-seitig vorbereitet (siehe `nudge_task_overview_matrix`-Referenz), wird aber erst funktional und zum Default, wenn Schritt 10 (Eisenhower-Filter) gebaut wird. Kein Vorziehen von ESC-FUNC-001 in Schritt 3, um den Build-Plan nicht zu verwässern.

## 6. Neue, bisher nicht dokumentierte Datenmodell-Bedarfe

Durch die Task-Detail-Sichtung (`redesigned_task_detail`) werden zwei Dinge sichtbar, die noch nicht im Datenmodell (Schritt 2) existieren:

- **`task_events`-Tabelle:** Für die Activity-Log-Historie aus CHKP-FUNC-012 ("zeigt Historie"). Bisher wird nur der aktuelle Task-Zustand gespeichert, keine Ereignis-Historie. Wird in Schritt 3 ergänzt (task erstellt, Checkpoint erreicht + Interaktionsart, Statuswechsel).
- **Artefakt-Speicherort:** Für CHKP-FUNC-004/012 (Artefakt-Einreichung) werden hochgeladene Dateien lokal unter `core-app/uploads/<task_id>/` abgelegt, nur Dateiname/-pfad in der DB referenziert (kein Blob-Storage-Overkill für eine Solo-App).

## 7. Nächster Schritt

Schritt 3: Dashboard (`nudge_my_focus`-Basis), Task-Detail (`redesigned_task_detail`-Basis), All-Tasks (`nudge_dashboard`/smart_deadline-Basis, einfaches Formular statt Parser), Add-Task-Rohfassung (`nudge_add_task`-Basis) — als Jinja2-Templates mit dem in Abschnitt 1 festgelegten Farbschema/Font-Pairing.
