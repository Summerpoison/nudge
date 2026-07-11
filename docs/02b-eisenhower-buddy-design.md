# Design Decision: Eisenhower-Filter, Reminder-Bündelung & Accountability Buddy

**Status:** Design entschieden, Teile davon MVP-relevant
**Kontext:** Weiterentwicklung von Modul 1 (Checkpoint & Escalation) und Modul 4 (Weekly Review) aus dem ursprünglichen Spec. Beantwortet u.a. die im Spec offen gelassene Frage: *"Should the Wednesday check-in have a social/relational component?"*

---

## 1. Wednesday Check-in: von Kalendertag zu Bedingung

**Problem:** Ein fixer Wochentag ("Wednesday check-in") ignoriert, dass Checkpoints individuell unterschiedlich liegen können.

**Entscheidung:** Der Check-in ist kein Kalendertag mehr, sondern ein **aggregierter Trigger** — er feuert, wenn mindestens einer der drei aktuellen Fokus-Tasks einen Checkpoint erreicht oder eine definierte Zeit ohne Interaktion vergangen ist. Aus "Wednesday Check-in" wird konzeptionell ein "Fokus-Zwischenstand", ausgelöst durch Bedingung statt durch Datum.

## 2. Reminder-Bündelung

**Problem:** Zwei Tasks mit unterschiedlichen 50%-Checkpoints (z.B. Dienstag 16 Uhr, Donnerstag 12 Uhr) würden zwei separate Unterbrechungsmomente erzeugen.

**Entscheidung:** Reminder werden gebündelt statt pro Task einzeln verschickt. Ein täglicher Digest-Zeitpunkt (z.B. morgens) sammelt alle an diesem Tag fälligen Checkpoints in eine Nachricht ("2 Checkpoints heute fällig: Task 1, Task 2").

**Begründung:** Direkt gedeckt durch Spec-Prinzip *"Reduce decision latency"* — jede zusätzliche Unterbrechung hat Exekutivfunktions-Kosten. Technisch zudem einfacher: ein täglicher Cron-Lauf statt N Einzeltimer pro Task.

## 3. Overhead-Begrenzung: nur Fokus-Tasks

**Entscheidung:** Das gesamte Reminder-/Buddy-System bezieht sich ausschließlich auf die drei aktuell committeten Fokus-Tasks aus dem Weekly Review — nicht auf jeden Task im System. Alle anderen Tasks bleiben passiv im Dashboard sichtbar (mit Checkpoint-Datum), ohne aktive Benachrichtigung. Sie werden erst relevant, wenn sie zu einem Fokus-Task befördert werden.

**Begründung:** Hält die Kognitionslast konstant unabhängig von der Gesamtzahl der Tasks im System (5 oder 50 macht keinen Unterschied).

## 4. Kein Zwang bei freien Slots

**Szenario:** Nutzer erledigt alle drei Fokus-Tasks vorzeitig (z.B. Dienstag).

**Entscheidung:** Kein erzwungenes Nachfüllen. Das System bietet an ("Alle drei erledigt. Früher neu priorisieren oder bis zum nächsten regulären Zyklus warten?"), beide Antworten sind gleichwertig valide.

**Begründung:** Konsistent mit *"Respect the ADHD energy inversion"* — ein guter Tag soll nicht durch sofortiges Nachfüllen bestraft werden. Auch konsistent mit dem Grundprinzip "kein erzwungenes Verhalten, keine künstliche Verpflichtung".

## 5. Eisenhower-Matrix als Filterbedingung für Eskalation

**Ursprünglich:** Eisenhower-Klassifizierung war als reines Anzeige-/Sortierfeature gedacht (MoSCoW: Could).

**Jetzt:** Durch die Verknüpfung mit dem Buddy-System ist sie zur **strukturellen Filterbedingung** geworden, die entscheidet, ob die volle Eskalationskette überhaupt aktiv wird.

**Funktionsweise:**
- **Important + Urgent** → volle Eskalationskette inkl. Buddy-Benachrichtigung bei Stufe 3
- **Important + Not Urgent** → wird getrackt, im Dashboard sichtbar, löst aber **keine** aktiven Reminder oder Buddy-Alerts aus
- **Automatischer Quadranten-Wechsel:** Rückt die Buffer-Deadline eines "Important + Not Urgent"-Tasks unter einen Schwellenwert (Default-Vorschlag: < 3 Tage), wechselt der Task automatisch zu "Important + Urgent" und aktiviert die volle Logik

**Wichtig:** "Urgent" ist ein **berechneter Zustand** (aus Restzeit bis Deadline abgeleitet), kein manuelles Nutzerfeld — konsistent mit dem Spec-Prinzip *"Infer metadata, don't ask for it."*

## 6. Accountability Buddy

**Entscheidung:** Ein hinterlegter Buddy-Kontakt wird bei Eskalationsstufe 3 (75%-Checkpoint verpasst / Buffer-Deadline überschritten) automatisch benachrichtigt — analog zum Alarmy-Prinzip (Snooze/Ignorieren wird technisch unmöglich statt nur unbequem).

**Scope-Regeln:**
- Gilt nur für Tasks im Quadranten "Important + Urgent" (siehe Punkt 5)
- Buddy sieht nur "Task X braucht Aufmerksamkeit", keine vollen Task-Details (konsistent mit "No company data in the AI layer" / Datensparsamkeit gegenüber Dritten)
- Wo/wie der Buddy hinterlegt wird: Settings, analog zum E-Mail-Konto

**Offene Frage für spätere Iteration:** Automatisch ohne Rückfrage (Alarmy-Prinzip) oder mit kurzem Zwischenschritt, in dem der Nutzer selbst reagieren kann, bevor der Buddy involviert wird?

---

## MoSCoW-Einordnung für den MVP

| Feature | Einstufung | Begründung |
|---|---|---|
| Eisenhower-Klassifizierung (Important/Urgent als berechneter Zustand) | **Must** | Ohne Filterbedingung würde der Buddy-Alert bei jedem Task feuern |
| Fester Default-Schwellenwert für "urgent" (z.B. Buffer-Deadline < 3 Tage) | **Must** | Muss existieren, damit das System korrekt funktioniert |
| Schwellenwert in Settings konfigurierbar | **Should** | Wichtig fürs Produkt, aber Default reicht für funktionierenden MVP |
| Reminder-Bündelung (täglicher Digest) | **Must** | Kern des Overhead-Prinzips, sonst Spam bei mehreren Tasks |
| Accountability Buddy (Grundfunktion, Stufe-3-Trigger) | **Should** | Zentrale Design-Idee, aber MVP funktioniert auch ohne — kann als klar dokumentierte Erweiterung nachgezogen werden, falls Zeit fehlt |
| Pro-Task individualisierbare Schwellenwerte | **Could** | Feinschliff, kein struktureller Bestandteil |
| Live-Neuberechnung des Quadranten bei jedem App-Öffnen (statt nur im täglichen Cron) | **Could** | Optimierung, nicht funktionsrelevant |

**Leitprinzip für den Cut:** Der Unterschied zwischen Must und Should ist hier "funktioniert korrekt" vs. "ist vom Nutzer konfigurierbar". Ein sinnvoll gewählter, hartkodierter Default erfüllt die Architektur-Anforderung vollständig; die Konfigurierbarkeit ist UX-Politur, kein struktureller Bestandteil.
