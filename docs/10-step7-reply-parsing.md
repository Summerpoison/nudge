# Step 7: Regelbasiertes Reply-Parsing

**Status:** Abgeschlossen
**Bezug:** REVIEW-FUNC-004, REVIEW-FUNC-005.

---

## Vorab geklärt: IMAP vs. POP3

`REVIEW-FUNC-004` und `REVIEW-NFR-001` nennen explizit IMAP/`imaplib`. Mailpit betreibt aber **keinen IMAP-Server** — bestätigt über `mailpit --help`: nur SMTP, POP3 (muss per `--pop3-auth-file` explizit aktiviert werden, standardmäßig aus) und die eigene REST-API. `00-tooling-and-process-independence.md` hatte diese Lücke mit der Formulierung "simulierter IMAP-Antwortzyklus" bereits vage angedeutet.

**Entscheidung (mit Nutzerin abgestimmt):** `poplib` (Python-Standardbibliothek, gleiche Kategorie wie `imaplib`) gegen Mailpits echten POP3-Server, statt gegen ein reales E-Mail-Konto oder gegen Mailpits REST-API. Begründung:
- Ein echtes Mail-Abruf-Protokoll gegen einen echten Server — kein HTTP-Mock, der die eigentliche Mechanik verschleiern würde.
- Stdlib-only bleibt erfüllt (nur der konkrete Modulname weicht vom Anforderungstext ab).
- Der spätere Umstieg auf `imaplib` gegen ein echtes Konto (Gmail o. ä.) wäre eine kleine, gut verstandene Änderung (gleiches Muster: verbinden → filtern → abrufen → parsen), ohne dass Zugangsdaten schon jetzt fest verdrahtet werden müssen.

Mailpit-Start für diesen Schritt: `mailpit --pop3-auth-file <pfad-zu-einer-datei-mit "nudge:nudge-local-test">` (siehe `how-to-run-and-test-locally.md`).

## Was gebaut wurde

`notification-worker/worker.py` erweitert um:

```python
POP3_HOST = "localhost"
POP3_PORT = 1110
POP3_USERNAME = "nudge"
POP3_PASSWORD = "nudge-local-test"

REVIEW_SUBJECT_PATTERN = re.compile(r"Nudge Weekly Review \[ids: ([\d,]+)\]")
TOP_PRIORITY_COUNT = 3
processed_reply_uids: set[str] = set()


def parse_top_priorities(body: str, valid_ids: set[int]) -> list[int]:
    priorities = []
    for match in re.finditer(r"#?\b(\d+)\b", body):
        candidate = int(match.group(1))
        if candidate in valid_ids and candidate not in priorities:
            priorities.append(candidate)
        if len(priorities) == TOP_PRIORITY_COUNT:
            break
    return priorities


def check_for_replies() -> None:
    try:
        conn = poplib.POP3(POP3_HOST, POP3_PORT, timeout=5)
        conn.user(POP3_USERNAME)
        conn.pass_(POP3_PASSWORD)
    except (OSError, poplib.error_proto) as error:
        log(f"Could not check for replies via POP3 at {POP3_HOST}:{POP3_PORT}: {error}")
        return

    try:
        _, uidl_lines, _ = conn.uidl()
        for line in uidl_lines:
            msg_num_str, uid = line.decode().split(" ", 1)
            if uid in processed_reply_uids:
                continue
            msg_num = int(msg_num_str)

            _, header_lines, _ = conn.top(msg_num, 0)
            headers = email.message_from_bytes(b"\r\n".join(header_lines), policy=email.policy.default)
            subject = headers.get("Subject", "")

            is_reply = subject.strip().lower().startswith("re:")
            match = REVIEW_SUBJECT_PATTERN.search(subject)
            if not is_reply or not match:
                processed_reply_uids.add(uid)
                continue

            valid_ids = {int(x) for x in match.group(1).split(",")}
            _, full_lines, _ = conn.retr(msg_num)
            full_message = email.message_from_bytes(b"\r\n".join(full_lines), policy=email.policy.default)
            body_part = full_message.get_body(preferencelist=("plain",))
            body_text = body_part.get_content() if body_part else ""

            priorities = parse_top_priorities(body_text, valid_ids)
            processed_reply_uids.add(uid)
            log(f"Reply to '{subject}' parsed top priorities: {priorities}" if priorities
                else f"Reply to '{subject}' matched but no valid task IDs found in the body")
    finally:
        conn.quit()
```

### "Nur den referenzierten Thread" (REVIEW-FUNC-004)

POP3 kennt kein serverseitiges Suchen/Filtern (kein `SEARCH`-Befehl wie bei IMAP) — jede Nachricht im Postfach muss einzeln über `UIDL`/`TOP` angeschaut werden, um zu entscheiden, ob sie relevant ist. Die "kein genereller Inbox-Zugriff"-Anforderung wird deshalb nicht auf Protokoll-, sondern auf Anwendungsebene umgesetzt:
- `TOP <msg> 0` holt **nur die Header**, keinen Body — die Betreffzeile wird geprüft, bevor überhaupt der volle Inhalt einer Nachricht abgerufen wird.
- Nachrichten, deren Betreff nicht zu unserem Referenzmuster passt, werden ignoriert (nur die UID landet im "gesehen"-Set, damit sie nicht bei jedem Zyklus erneut geprüft wird) — ihr Inhalt wird nirgends geloggt oder weiterverarbeitet.
- Es gibt keine UI und keine Funktion, die das Postfach durchsucht oder anzeigt — das Verhalten ist ausschließlich "prüfen, ob DAS die erwartete Antwort ist", nichts Generischeres.

### Gefundener Bug: eigene Mail als "Antwort auf sich selbst" erkannt

Beim ersten Testlauf wurde die soeben vom Worker selbst verschickte Review-Mail vom Reply-Parser fälschlich als Antwort erkannt (und ergab sogar plausible Top-3-Werte, weil die Task-IDs im Body der Review-Mail selbst als `#3`, `#2`, `#1` auftauchen). Ursache: Mailpit fängt gesendete und "empfangene" Mails im selben Postfach, ohne Trennung zwischen "Gesendet" und "Posteingang" wie bei einem echten Konto. **Behoben** durch eine zusätzliche Prüfung: Nur Nachrichten, deren Betreff mit `Re:` beginnt, werden als Antwort gewertet — die eigene ausgehende Mail hat diesen Präfix nie. Bei einem echten Konto würde dieses Problem strukturell gar nicht auftreten (die eigene gesendete Mail läge im "Gesendet"-Ordner, nicht im überwachten Posteingang), ist hier also ein reines Mailpit-Testartefakt, aber die `Re:`-Prüfung ist trotzdem eine sinnvolle, realistische Zusatzabsicherung.

### Regelbasiertes Parsing (REVIEW-FUNC-005)

`parse_top_priorities()`: durchsucht den Klartext-Body nach Zahlen (`#?\b(\d+)\b`, optionales `#`-Präfix), behält nur Zahlen, die tatsächlich in der Menge der im Betreff referenzierten Task-IDs vorkommen (schützt vor zufälligen Zahlen wie Uhrzeiten oder Mengenangaben in der Antwort), verwirft Duplikate und bricht nach den ersten drei Treffern ab — in der Reihenfolge, in der sie im Text auftauchen. Kein KI-Modell, rein Regex + Mengen-Abgleich, wie von REVIEW-FUNC-005 gefordert.

`full_message.get_body(preferencelist=("plain",))` (Python-`email`-Modul mit `policy=email.policy.default`) extrahiert zuverlässig den Text-Teil, auch falls ein echter Mail-Client eine `multipart/alternative`-Nachricht (Text + HTML) verschickt — unsere eigene ausgehende Mail ist zwar reines `MIMEText`, aber die Antwort einer Nutzerin über Gmail/Outlook wäre typischerweise multipart.

### Bewusst nicht gebaut

- **Kein Löschen verarbeiteter Nachrichten per `DELE`:** Wäre die "sauberere" POP3-Variante (kein In-Memory-Zustand nötig), hätte aber zur Folge, dass verarbeitete Antworten auch aus Mailpits Web-UI verschwinden — schlecht fürs Nachvollziehen beim Testen. Stattdessen ein In-Memory-Set bereits geprüfter UIDs (geht bei Worker-Neustart verloren, für den MVP akzeptabel, gleiches Muster wie `last_review_sent` aus Schritt 6).
- **Rückspielen der Priorisierung in die Kern-App:** Das ist explizit Schritt 8 (REVIEW-FUNC-006). Dieser Schritt endet mit dem geloggten Ergebnis der Top-3-Extraktion, noch ohne API-Call an core-app.

## Verifikation

Vollständiger lokaler Testlauf (core-app, Worker, Mailpit mit `--pop3-auth-file`):

1. Drei Test-Tasks angelegt, Worker gestartet → Review-Mail verschickt (`Nudge Weekly Review [ids: 3,2,1]`). **Vor** dem `Re:`-Fix: Worker erkannte seine eigene Mail fälschlich als Antwort. Nach dem Fix: kein Fehltreffer mehr.
2. Simulierte echte Antwort verschickt (`Re: Nudge Weekly Review [ids: 3,2,1]`, Body erwähnt "#3 and #1 ... plus 2") → nächster Poll-Zyklus loggt `Reply to '...' parsed top priorities: [3, 1, 2]` — korrekte Reihenfolge (Erscheinungsreihenfolge im Text), korrekt auf drei begrenzt.
3. Irrelevante Mail verschickt (Betreff "Buy now!!", keine Beziehung zum Referenzmuster) → nächster Zyklus zeigt **keinerlei** Log-Eintrag dazu — vollständig ignoriert, wie von REVIEW-FUNC-004 gefordert.
4. Zweiter Poll-Zyklus nach der geparsten Antwort → dieselbe Antwort wird **nicht** erneut verarbeitet (UID bereits im "gesehen"-Set).
5. Mailpit-Prozess beendet → sowohl der nächste Sendeversuch als auch der nächste Reply-Check loggen sauber `Could not ...`-Fehler, Worker-Prozess läuft unverändert weiter.
6. Mailpit neu gestartet, Antwort ohne erkennbare Task-IDs verschickt ("Sounds good... No specific top pick", keine Ziffern) → korrekt geloggt als "matched but no valid task IDs found in the body" statt eine leere/falsche Priorisierung anzunehmen.

Alle Prozesse danach gestoppt, Testdatenbank gelöscht.

## Nächster Schritt

Schritt 8: Rückspielen der Priorisierung in die Kern-App (REVIEW-FUNC-006) — die in Schritt 7 extrahierten Top-3-IDs werden per REST-Call an `core-app` übertragen und dort als "Fokus-Tasks der Woche" markiert (neues Feld im Task-Datenmodell).
