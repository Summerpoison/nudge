# RE-Audit: adhd-proof-workflow-spec_v2.md

**Erstellt:** 2026-06-17  
**Methode:** Requirements Engineering — Qualitätsbewertung nach IEEE 830 / IREB-Kriterien  
**Ziel:** Vorbereitung für Abbildung in Notion / Airtable / Jira  

---

## 1. Gesamtübersicht (Scorecard)

| Kriterium | Bewertung | Kommentar (kurz) |
|---|---|---|
| Korrekt | ⚠️ Teilweise | Inhalte stimmen, aber mehrere Aussagen unpräzise |
| Vollständig | ❌ Unvollständig | Nicht-funktionale Anforderungen fehlen komplett |
| Eindeutig definiert / abgegrenzt | ❌ Mangelhaft | Viele Anforderungen nicht abgegrenzt vom Design-Rationale |
| Verständlich beschrieben | ✅ Gut | Sprache klar, ADHD-Kontext nachvollziehbar |
| Atomar | ❌ Mangelhaft | Anforderungen bündeln häufig 3–5 Einzelverhalten |
| Identifizierbar | ❌ Fehlt | Keine IDs, keine Nummerierung |
| Einheitlich dokumentiert | ⚠️ Teilweise | Inkonsistente Struktur je Modul |
| Notwendig | ✅ Gut | Kaum Goldplating, Parked-Ideas klar getrennt |
| Nachprüfbar / Testbar | ❌ Mangelhaft | Akzeptanzkriterien fehlen durchgehend |
| Rück- und vorwärts verfolgbar | ❌ Fehlt | Keine Verlinkung Problem → Anforderung → Implementierung |
| Konsistent | ⚠️ Teilweise | 1 potenzieller Widerspruch identifiziert |
| Klassifizierbar (jur.) | ❌ Fehlt | Kein Typ, keine Kategorie, keine Rechtsbindung |
| Gültigkeit / Aktualität | ⚠️ Teilweise | Status "Design concept" vorhanden, kein Review-Datum |
| Realisierbar | ✅ Gut | Implementierungsreihenfolge plausibel |
| Bewertbar / Priorisierbar | ⚠️ Teilweise | Reihenfolge in Impl. Notes, aber kein Prioritätsfeld |
| Widerspruchsfrei | ⚠️ Teilweise | Siehe Abschnitt 3.1 |
| Prüfbar | ❌ Mangelhaft | Testkriterien und -szenarien fehlen |
| Kundenorientiert | ✅ Gut | Starker ADHD-Kontext, Nutzerperspektive durchgehend |

**Gesamtbewertung: 4 ✅ / 6 ⚠️ / 8 ❌**  
Das Dokument ist ein exzellentes Konzept-/Designdokument, aber noch kein RE-konformes Anforderungsdokument.

---

## 2. Detailbewertung je Kriterium

### 2.1 Korrekt
**Definition:** Die Anforderung beschreibt korrekt, was das System leisten soll — keine sachlichen Fehler.

**Befund:** Die inhaltlichen Aussagen sind fachlich korrekt und ADHD-spezifisch gut begründet. Jedoch gibt es mehrere unpräzise Formulierungen:

| Problem | Textstelle | Konkret |
|---|---|---|
| Schwellenwert unscharf | "suspiciously long (e.g., 3+ hours)" | Was löst den Prompt aus — genau 3h, mehr als 3h, konfigurierbar? |
| Schwellenwert unscharf | "Progress significantly below expected threshold" (Panic Mode Trigger) | Kein quantitativer Wert definiert |
| Schwellenwert unscharf | "Estimate exceeded by a large margin" (Panic Mode Trigger) | Kein quantitativer Wert definiert |
| Implizite Annahme | "Buffer deadline = 70% of available time" | Bezugsgröße unklar: 70% der Zeit zwischen heute und externem Deadline? Zwischen Projektstart und Deadline? |
| Fehlende Randbedingung | "Lunch break auto-detected or defaulted if no activity for 45+ minutes" | Was ist "no activity"? Keine Timer-Interaktion? Keine Systemeingabe? |

**Empfehlung:** Alle Schwellenwerte als konfigurierbare Parameter mit Default-Wert und Einheit dokumentieren.

---

### 2.2 Vollständig
**Definition:** Alle relevanten Anforderungen sind erfasst, inklusive Randfälle, nicht-funktionale Anforderungen, Schnittstellen.

**Befund:** Das Dokument ist auf funktionale Anforderungen fokussiert. Folgende Kategorien fehlen vollständig:

**Nicht-funktionale Anforderungen (NFR) — komplett fehlend:**
- Verfügbarkeit: Muss das System offline funktionieren?
- Performance: Wie schnell soll die Zeiterfassung reagieren?
- Datenschutz / DSGVO: Wo werden Daten gespeichert? Welche Daten verlassen das Gerät?
- Backup / Datenverlust: Was passiert bei Datenverlust?
- Plattform: Web, Desktop, Mobile — oder alle?
- Barrierefreiheit: Spezifische ADHD-UI-Anforderungen (z. B. kein Blink, kein überladenes Interface)?
- Internationalisierung: Nur Deutsch/Englisch? Zeitzonenverwaltung?

**Fehlende funktionale Bereiche:**
- Authentifizierung / Nutzerverwaltung (Einzelnutzer vs. Mehrnutzer?)
- Datenlöschung / Archivierung abgeschlossener Projekte
- Onboarding neuer Projekte (nur Kickoff-Formular? Wizard?)
- Fehlerbehandlung: Was passiert, wenn die Claude-API nicht verfügbar ist?
- Notifications: Welche Kanäle außer E-Mail? Push? In-App?
- Kalender-Integration: Schreibend oder nur lesend? Welche Anbieter (Google, Outlook, iCal)?
- Export-Formate: Exakt welche Formate für den Timesheet-Export?

**Empfehlung:** Systematische Erfassung mit Kategorie-Tags: `func`, `nfr-perf`, `nfr-sec`, `nfr-ux`, `interface`.

---

### 2.3 Eindeutig definiert / abgegrenzt
**Definition:** Jede Anforderung hat genau eine Interpretation. Kein Spielraum für unterschiedliche Lesarten.

**Befund:** Das Dokument vermischt systematisch:
- Anforderung (Was das System tun MUSS)
- Design-Rationale (Warum so)
- Implementierungshinweis (Wie es gebaut werden könnte)
- Designprinzip (übergeordnete Leitlinie)

**Beispiel — nicht abgegrenzt:**
> *"The system should prefer stronger artifacts but never block on them. The worst outcome is the user spending 20 minutes wondering 'does this count?' and avoiding the checkpoint entirely. Anything beats nothing."*

Das enthält: 1 Anforderung (prefer stronger), 1 Constraint (never block), 1 Rationale (20-Minuten-Problem), 1 Designprinzip (anything beats nothing).

**Weitere Mehrdeutigkeiten:**
- "System drafts a message" — bedeutet das: automatisch ohne Aktion? Nach Klick? Mit oder ohne Vorschau?
- "Tasks never hide" (bei Status C/Warten) — bedeutet das: immer in der Hauptansicht? In separatem Filter? Nie archivierbar?
- "The human only has to hit send" — ist das eine UI-Anforderung (Button sichtbar), eine Workflow-Anforderung (kein extra Schritt), oder beides?

**Empfehlung:** Template mit Pflichtfeldern "Shall-Formulierung", "Rationale" (getrennt), "Abgrenzung" (was explizit NICHT dazugehört).

---

### 2.4 Verständlich beschrieben
**Definition:** Die Anforderungen sind für alle Stakeholder (Entwickler, Nutzer, Tester) verständlich.

**Befund:** ✅ Stärke des Dokuments. Sprache ist klar, Kontext wird erklärt, Beispiele sind konkret. Die Tabellen und die Blocker-Triage-Menüstruktur sind besonders gelungen.

**Kleinere Verbesserungen:**
- Begriff "Context artifact" vs. "Proof artifact" sollte im Glossar definiert werden
- "Activation cost" ist ADHD-Fachjargon — für Entwickler-Stakeholder ggf. unbekannt
- "docassemble pattern" (Modul 1) ist ohne Vorwissen nicht verständlich — erklärt aber direkt danach

---

### 2.5 Atomar
**Definition:** Jede Anforderung beschreibt genau einen testbaren Sachverhalt.

**Befund:** ❌ Kritischstes Problem für RE-Tool-Import. Nahezu alle Anforderungen sind compound requirements.

**Beispiel — Modul 3 Zeiterfassung:**
> *"If a timer has been running suspiciously long (e.g., 3+ hours), prompt on next interaction: 'Was that really 3.5 hours, or did you switch earlier?' Allow splitting the block retroactively"*

Das sind mindestens 3 atomare Anforderungen:
- `TT-01` Das System erkennt, wenn ein laufender Timer einen konfigurierbaren Schwellenwert überschreitet (Default: 3h)
- `TT-02` Das System zeigt beim nächsten Benutzerinterakt einen Bestätigungs-Dialog für den laufenden Timer
- `TT-03` Der Nutzer kann einen bestehenden Zeitblock rückwirkend aufteilen

**Beispiel — Modul 4 Weekly Review:**
> *"Those 3 get time-blocked in your calendar (manually or auto-scheduled if calendar integration is available). Each block includes the micro-instructions or current status so you don't have to reconstruct context when the block arrives."*

Mindestens 4 Anforderungen:
- Prioritäten werden kalendarisch blockiert (manuell)
- Prioritäten werden kalendarisch blockiert (auto, wenn Integration vorhanden)
- Jeder Kalenderblock enthält Mikro-Instruktionen oder aktuellen Status
- Die Darstellung verhindert Kontext-Rekonstruktion beim Erreichen des Blocks

**Empfehlung:** Jede Anforderung als eigenständiger Datensatz mit genau einem messbaren Verhalten.

---

### 2.6 Identifizierbar
**Definition:** Jede Anforderung hat eine eindeutige, stabile ID.

**Befund:** ❌ Keine IDs vorhanden. Das Dokument referenziert sich intern nur über Modulnamen und Prosa (z. B. "see Module 5"). Für ein RE-Tool ist das ein Blocker.

**Empfohlenes ID-Schema:**

```
[MODUL]-[TYP]-[NUMMER]

Beispiele:
CHKP-FUNC-001   Checkpoint-System, funktionale Anforderung 1
TIME-FUNC-003   Zeiterfassung, funktionale Anforderung 3
SYS-NFR-001     System-übergreifend, nicht-funktionale Anforderung 1
PANIC-FUNC-002  Panic Mode, funktionale Anforderung 2
```

Alternativ für flachere Struktur:
```
REQ-001 bis REQ-NNN (fortlaufend, mit Modul als Metadaten-Feld)
```

---

### 2.7 Einheitlich dokumentiert
**Definition:** Alle Anforderungen folgen demselben Dokumentationsschema.

**Befund:** ⚠️ Jedes Modul hat eine eigene Struktur:
- Modul 1: Tabellen + Fließtext + Blocker-Triage-Menü + Eskalationstabelle
- Modul 2: Code-Block für Capture-Format + Fließtext
- Modul 3: Aufzählung + Datentabelle
- Modul 4: Fließtext mit eingebetteten Prozessschritten
- Modul 5: Trigger-Liste + Fragen-Liste + Design Notes

Kein einheitliches Anforderungs-Template. Macht maschinellen Import und Tool-Abbildung schwierig.

**Empfohlenes Template (pro Anforderung):**

```
ID:              [z. B. CHKP-FUNC-001]
Titel:           [Kurztitel, ≤ 60 Zeichen]
Typ:             [Funktional | NFR-Performance | NFR-Security | NFR-UX | Interface]
Priorität:       [Must Have | Should Have | Nice to Have | Parked]
Modul:           [1 Checkpoint | 2 Task Prep | 3 Time Tracker | 4 Weekly Review | 5 Panic Mode | Cross-cutting]
Beschreibung:    [Shall-Formulierung: "Das System SOLL / MUSS ..."]
Rationale:       [Warum diese Anforderung — getrennt von der Beschreibung]
Akzeptanzkriterien: [Testbares Kriterium 1 / Kriterium 2 / ...]
Abgrenzung:      [Was NICHT dazugehört]
Abhängigkeiten:  [IDs anderer Anforderungen]
Status:          [Draft | Review | Approved | Implemented | Deprecated]
Quelle:          [adhd-proof-workflow-spec_v2.md, Modul X]
Erstellt:        [Datum]
Geändert:        [Datum]
```

---

### 2.8 Notwendig
**Definition:** Jede Anforderung ist tatsächlich erforderlich — kein Goldplating.

**Befund:** ✅ Das Dokument ist außergewöhnlich gut diszipliniert. Die "Parked Ideas"-Sektion mit expliziten Begründungen für das Zurückstellen ist RE-Best-Practice. Keine überschüssigen Anforderungen identifiziert.

**Kleiner Hinweis:** Die Auto-Rules für Kalender-Integration (Modul 3) sind als separate optionale Anforderungen zu markieren, da sie eine Kalender-Integration voraussetzen, die laut Spec optional ist.

---

### 2.9 Nachprüfbar / Testbar
**Definition:** Für jede Anforderung lässt sich ein konkreter Testfall formulieren.

**Befund:** ❌ Kein einziger Akzeptanzkriterium oder Testfall dokumentiert.

**Beispiele für fehlende Testbarkeit:**

| Anforderung (paraphrasiert) | Problem | Testbares Kriterium (Beispiel) |
|---|---|---|
| "Buffer deadline = 70% of available time" | Was ist Bezugsgröße? | "Bei externer Deadline 14 Tage ab heute → Buffer-Deadline = heute + 9,8 Tage (gerundet auf 10 Tage)" |
| "System drafts extension email" | Wann genau? Was enthält sie? | "Email-Draft enthält: erledigte Teile, vorgeschlagene neue Deadline (+7 Tage), Begründung. Wird innerhalb von 2s nach Auswahl von Option D generiert." |
| "Tasks never hide" | Welche Ansicht? | "In der Hauptaufgabenliste erscheint eine Aufgabe mit Status 'Waiting' immer in der Standardansicht, nicht nur in Filteransichten" |
| "Panic Mode auto-triggers" | Threshold 48h — ab wann genau? | "Wenn aktuelle Zeit < 48h vor externer Deadline UND kein Artefakt vorhanden → Panic Mode wird aktiviert. Gilt unabhängig von Tageszeit." |

**Empfehlung:** Jede Anforderung bekommt min. 1 Happy-Path-Akzeptanzkriterium + 1 Edge-Case-Kriterium.

---

### 2.10 Rück- und vorwärts verfolgbar
**Definition:** Jede Anforderung ist rückverfolgbar auf ein Nutzerbedürfnis/Problem und vorwärts verfolgbar auf eine Implementierung/Testfall.

**Befund:** ❌ Rückverfolgbarkeit: Jedes Modul hat eine "Problem it solves"-Sektion — das ist gut, aber nicht formalisiert. Keine explizite Verlinkung Anforderung ↔ Problem.

Vorwärts-Verfolgbarkeit: Fehlt komplett. Keine Verlinkung zu:
- User Stories
- Implementierungs-Tickets
- Testfällen

**Empfohlene Traceability-Matrix (für Notion/Airtable):**

```
Problem/User Need → Designprinzip → Anforderung → Implementierungs-Ticket → Testfall
```

Beispiel:
```
"Scope creep unsichtbar" → "Proof over self-report" → CHKP-FUNC-001 (Artifact required) 
  → GitHub Issue #12 → TEST-CHKP-001
```

---

### 2.11 Konsistent
**Definition:** Anforderungen widersprechen sich nicht innerhalb des Dokuments.

**Befund:** ⚠️ Ein potenzieller Widerspruch identifiziert (siehe auch 2.16).

**Widerspruch 1 — Artifact Level vs. Deadline-Logik:**
> *"The system should prefer stronger artifacts but never block on them."* (Modul 1)

Versus:

> *"At each checkpoint, the system requires an artifact. Not a checkbox."* (Modul 1)

Ist das "require" im zweiten Satz eine Blocking-Anforderung oder nicht? Die Eskalationstabelle (Level 1: "Checkpoint approaching, no activity → Blocker triage") legt nahe: kein hartes Blocking, aber die Formulierung "requires" ist mehrdeutig.

**Mögliche Inkonsistenz 2 — Datenschutz und Claude API:**
> *"No company data through third-party AI."* (Designprinzip + Tech Notes)

Versus:

> *"Claude API for the intelligence layer (blocker triage drafting, timesheet cleanup, weekly summary generation)"*

Die Blocker-Triage generiert Nachrichten auf Basis von Aufgaben-Kontext. Auch wenn Labels vage sind ("Client A deliverable"), könnte der strukturelle Kontext (Deadlines, Stakeholder-Namen, Eskalationslevel) als company-sensitiv gelten. Diese Spannung ist im Dokument erkannt aber nicht aufgelöst.

---

### 2.12 Klassifizierbar (jur.)
**Definition:** Anforderungen sind nach Typ, Verbindlichkeit und rechtlicher Relevanz klassifizierbar.

**Befund:** ❌ Keine Klassifizierung vorhanden. Empfohlene Klassifikationsfelder:

| Klassifikation | Mögliche Werte | Relevanz |
|---|---|---|
| **Anforderungstyp** | Funktional / NFR / Constraint / Interface | Standard-RE |
| **Verbindlichkeit** | MUSS / SOLL / KANN (nach RFC 2119 / MoSCoW) | Priorisierung |
| **Rechtsrelevanz** | DSGVO-relevant / Datenschutz / Keine | Bei Personendaten-Verarbeitung |
| **Datenklasse** | Personenbezogen / Arbeitgeber-sensitiv / Öffentlich | Datenschutz-Design |
| **Stakeholder** | Nutzer / System / Extern (Arbeitgeber) | Traceability |

**Besondere Hinweise (DSGVO-Relevanz):**
Das System verarbeitet potenziell:
- Arbeitszeitdaten (Module 3) → §26 BDSG relevant bei Arbeitsverhältnis
- Kommunikationsdaten (Stakeholder-Kontakte)
- Produktivitätsdaten / Verhaltensmuster

Diese müssen als DSGVO-relevante Anforderungen separat geführt werden, auch wenn aktuell nur Eigenbedarf.

---

### 2.13 Gültigkeit / Aktualität
**Definition:** Anforderungen sind aktuell und spiegeln den heutigen Stand wider.

**Befund:** ⚠️ Das Dokument hat einen Status ("Design concept — not yet implemented") und ein Datum (June 2026). Das ist gut.

**Fehlend:**
- Kein formales Review-Datum / nächster Review-Termin
- Keine Versionsnummer mit Changelog (v2 zu v1 — was änderte sich?)
- Keine Verfallsmarkierung für zeitlich bedingte Annahmen (z. B. "Google Apps Script — free" könnte sich ändern)
- "Parked Ideas" haben kein "Revisit-Datum" oder "Revisit-Bedingung" als formales Feld

**Empfehlung:** Jede Anforderung mit `valid_from` und `valid_until` (oder "until condition") versehen.

---

### 2.14 Realisierbar
**Definition:** Anforderungen sind technisch und ressourcenmäßig umsetzbar.

**Befund:** ✅ Das Dokument ist realistisch. Die "What to build first"-Reihenfolge ist sinnvoll. Die Safeguard-Sektion ("building is more fun than using") zeigt pragmatisches Scope-Management.

**Offene Realisierbarkeits-Risiken:**
- "Auto-detect lunch break" via "no activity" — welche Activity-Signale sind verfügbar? Ohne OS-Integration nicht lösbar.
- "Calendar integration" — bei Google Apps Script machbar; bei Outlook/Exchange aufwändiger
- "Claude API drafting" — API-Kosten und Latenz bei Offline-Nutzung nicht adressiert
- Estimate Calibration Ratio — braucht signifikante historische Datenmenge; erstes Jahr liefert wenig valide Daten

---

### 2.15 Bewertbar / Priorisierbar
**Definition:** Anforderungen können nach Wichtigkeit, Dringlichkeit und Aufwand bewertet werden.

**Befund:** ⚠️ Die "What to build first"-Reihenfolge (1-5) ist eine implizite Priorisierung nach Wert. Kein formales Prioritätsfeld pro Anforderung.

**Fehlend:**
- MoSCoW-Klassifikation oder Kano-Modell pro Anforderung
- Aufwandsschätzung (auch rough: S/M/L/XL)
- Business-Value-Score
- Abhängigkeits-Graph (was muss vor was gebaut werden?)

**Empfehlung für Jira/Notion:** Felder `Priority` (Must/Should/Could/Won't), `Effort` (Story Points oder T-Shirt), `Value` (1-5) + automatisch berechnetes `Value/Effort-Ratio`.

---

### 2.16 Widerspruchsfrei
**Definition:** Keine zwei Anforderungen widersprechen sich direkt oder indirekt.

**Befund:** ⚠️ Zusätzlich zu Abschnitt 2.11:

**Spannungsfeld — Automatik vs. Kontrolle:**
- "Infer metadata, don't ask for it" (Designprinzip) — Maximale Automatisierung
- "The human only has to hit send" — Kontrolle bleibt beim Menschen
- Aber: "Exiting panic mode requires either: the deadline passes, the task is completed, or the user explicitly deactivates it" — hier ist die Automatik recht aggressiv (kein automatischer Exit außer durch Zeitablauf)

Diese Spannung ist konzeptuell beabsichtigt, muss aber in konkreten Anforderungen explizit aufgelöst werden: "Was macht das System automatisch?" vs. "Was erfordert immer eine Nutzeraktion?"

**Empfehlung:** Für jede automatische Systemfunktion eine explizite Anforderung: "Das System führt X aus OHNE Nutzeraktion, außer wenn Y."

---

### 2.17 Prüfbar
**Definition:** Jede Anforderung kann durch Review, Inspektion oder Test formal verifiziert werden.

**Befund:** ❌ Synonym zu Testbar (2.9), mit zusätzlichem Fokus auf Reviews und Inspektionen.

**Spezifisch für RE-Tool-Kontext:**
- Keine "Definition of Done" pro Anforderung
- Keine Review-Checkliste
- Keine Abnahmekriterien auf Modul-Ebene

---

### 2.18 Kundenorientiert
**Definition:** Anforderungen spiegeln echte Nutzerbedürfnisse wider, nicht interne technische Präferenzen.

**Befund:** ✅ Stärke des Dokuments. Die ADHD-spezifische Perspektive ist konsistent durchgehalten:
- "Build for the spiral, not the good days" — antizipiert Versagensmodi
- Blocker-Triage als Menü statt offener Frage — reduziert exekutive Belastung
- "Anything beats nothing" bei Artefakten — verhindert Perfektionismus-Blocking
- "Context artifact" neben "Proof artifact" — anerkennt, dass Dokumentation auch Wert hat

**Kein Persona-Dokument nötig:** Die Zielgruppe ist implizit klar und wird es bleiben — Single-User-System, Nutzerin = Designerin = Entwicklerin. Persona-Dokumentation wird erst relevant, wenn jemand anderes das System anfasst. Das ist nicht geplant.

---

## 3. Spezifische Problempunkte

### 3.1 Widerspruch: Artifact Required vs. Never Block

**Ort:** Modul 1, Abschnitt "Acceptable artifacts"

**Problem:**
- Satz 1: `"At each checkpoint, the system requires an artifact. Not a checkbox."`
- Satz 2: `"The system should prefer stronger artifacts but never block on them."`
- Eskalationstabelle Level 1: `"No activity → Blocker triage"` (nicht: Blockieren)

**Auflösung (beschlossen):** Der Checkpoint erfordert eine *Interaktion* (Artefakt-Upload oder Triage-Auswahl), nicht spezifisch ein Artefakt. Das ist die saubere Trennung.

```
CHKP-FUNC-010: Das System MUSS bei Checkpoint-Fälligkeit eine Nutzerinteraktion erfordern:
               entweder Artefakt-Upload (beliebiges Level) ODER Triage-Auswahl (A/B/C/D).
               Ein reines Checkbox-Abhaken MUSS abgelehnt werden.
CHKP-FUNC-011: Das System DARF den Nutzer NICHT am Fortfahren hindern, sofern eine der 
               beiden Interaktionsformen (Artefakt oder Triage) abgeschlossen wurde.
```

### 3.2 Fehlende Definition: "Available Time" für Buffer-Berechnung

**Ort:** Modul 1, Kickoff-Tabelle

**Problem:** "Buffer deadline = 70% of available time" — Bezugsgröße nicht definiert.

**Klärungsfrage:** Ist "available time" = (external_deadline - project_kickoff) oder (external_deadline - today)?

**Auflösung (beschlossen):** `available_time = external_deadline - task_creation_date`

### 3.3 Fehlende Anforderung: Offline-Funktionalität

**Ort:** Tech Considerations

**Problem:** "Local-first where possible" als Prinzip, aber keine Anforderung: Welche Features MÜSSEN offline funktionieren? Zeiterfassung? Artefakt-Upload?

### 3.4 Fehlende Anforderung: Datenlöschung

**Ort:** Nicht vorhanden

**Problem:** Keine Anforderung zur Löschung, Archivierung oder Retention von Daten. DSGVO-relevant bei Arbeitszeitdaten.

---

## 4. Empfehlungen für Tool-Import (Notion / Airtable / Jira)

### 4.1 Minimales Datenbankschema

```
Tabelle: Requirements
├── ID              TEXT (Primary Key, z. B. CHKP-FUNC-001)
├── Titel           TEXT (≤ 60 Zeichen)
├── Beschreibung    TEXT (Shall-Formulierung)
├── Rationale       TEXT (Warum — getrennt)
├── Typ             SELECT [Funktional | NFR | Constraint | Interface]
├── Modul           SELECT [1-Checkpoint | 2-TaskPrep | 3-TimeTracker | 4-Review | 5-Panic | Cross]
├── Priorität       SELECT [Must | Should | Could | Parked]
├── Status          SELECT [Draft | Review | Approved | Implemented | Deprecated]
├── Akzeptanzkriterien  TEXT (min. 1 testbares Kriterium)
├── Abgrenzung      TEXT (was NICHT dazugehört)
├── Abhängigkeiten  RELATION → Requirements.ID (many-to-many)
├── Quelle          TEXT (Spec-Datei + Abschnitt)
├── DSGVO_relevant  BOOLEAN
├── Erstellt        DATE
├── Geändert        DATE
└── Gültig_bis      DATE (optional)
```

### 4.2 Migrations-Aufwand

Das aktuelle Dokument enthält schätzungsweise **60–80 atomare Anforderungen** nach Zerlegung. Empfohlener Workflow:

1. **Modul-weise vorgehen** (entsprechend Implementierungsreihenfolge)
2. **Pro Modul:** Fließtext in atomare Shall-Formulierungen zerlegen
3. **Parallel:** NFR-Anforderungen ergänzen (ca. 15–20 zusätzliche)
4. **Akzeptanzkriterien** in separater Session ergänzen (zeitaufwändigster Schritt)
5. **Review** auf Widerspruchsfreiheit nach vollständigem Import

### 4.3 Reihenfolge für Tool-Erfassung (nach Implementierungspriorität)

| Phase | Modul | Geschätzte Anforderungen |
|---|---|---|
| 1 | Modul 3 (Time Tracker) | ~15 |
| 2 | Modul 2 (Task Prep) | ~8 |
| 3 | Cross-cutting NFRs | ~15 |
| 4 | Modul 4 (Weekly Review) | ~12 |
| 5 | Modul 1 (Checkpoint) | ~20 |
| 6 | Modul 5 (Panic Mode) | ~10 |
| **Gesamt** | | **~80** |

---

## 5. Fazit

Das Dokument ist ein überdurchschnittlich gut durchdachtes Konzept-Dokument mit starkem Nutzer-Fokus und guter Begründungstiefe. Es ist jedoch **noch kein RE-konformes Anforderungsdokument**.

**Kritischste Lücken für den Tool-Import:**
1. Keine IDs → ohne IDs ist kein sinnvolles Tracking möglich
2. Keine Atomarität → Zerlegung nötig bevor Import
3. Keine Akzeptanzkriterien → Testbarkeit nicht gegeben
4. Keine NFRs → Systemverhalten außerhalb der Happy Paths nicht definiert
5. Kein Traceability-Schema → Anforderungen nicht mit Problemen verknüpft

**Was gut ist und beibehalten werden soll:**
- "Problem it solves" pro Modul → wird zur Rückverfolgbarkeits-Basis
- Parked Ideas mit Begründung → korrekte RE-Praxis
- Designprinzipien als übergeordnete Constraints → werden zu System-Level-Requirements
- Implementierungsreihenfolge → wird zur Prioritätsbasis

---

*Dieses Audit-Dokument ist selbst kein Requirements-Dokument — es ist eine Analyse-Grundlage für die RE-Erfassung.*
