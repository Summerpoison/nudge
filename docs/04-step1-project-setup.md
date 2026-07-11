# Step 1: Projekt-Setup — Flask-Grundgerüst

**Status:** Abgeschlossen
**Bezug:** Keine CHKP-/REVIEW-ID direkt (Scaffolding-Schritt), legt aber die Grundlage für alle folgenden Schritte.

---

## Was gebaut wurde

```
core-app/
├── app.py            Flask-Anwendung, ein Health-Check-Endpunkt
├── requirements.txt  Abhängigkeiten (bisher nur Flask)
├── templates/         (leer, für Jinja2-Templates ab Schritt 3)
├── static/
│   ├── css/
│   └── js/
└── .venv/             lokale virtuelle Umgebung (nicht versioniert, siehe .gitignore)
```

`app.py`:

```python
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify(status="ok", service="core-app")


if __name__ == "__main__":
    app.run(port=3000, debug=True)
```

- `Flask(__name__)` erzeugt die Anwendungsinstanz; `__name__` sagt Flask, wo es liegt (für spätere Template-/Static-Pfad-Auflösung relevant, auch wenn hier noch nicht genutzt).
- `@app.route("/health")` registriert eine URL-Regel; die Funktion darunter wird bei jedem `GET /health` aufgerufen.
- `jsonify(...)` baut aus den Keyword-Argumenten eine JSON-Response mit korrektem `Content-Type`.
- `app.run(port=3000, debug=True)` startet den eingebauten Entwicklungsserver. `debug=True` aktiviert Auto-Reload bei Codeänderungen und den interaktiven Debugger — nur für lokale Entwicklung, nicht für den späteren Abgabe-/Demo-Betrieb relevant, aber unschädlich.

## Entscheidungen

- **Port 3000 fest im Code** (nicht per Umgebungsvariable), wie in `00-tooling-and-process-independence.md` vorgesehen (`core-app` auf 3000, `notification-worker` pollt später 3000 und läuft selbst auf 3001). Für den MVP-Scope reicht das; keine Konfigurationsebene nötig, die niemand außer der Entwicklerin selbst je ändert.
- **`/health` als erste Route statt einer "richtigen" Seite:** Direkter Bezug zu Abschnitt 3 in `00-tooling-and-process-independence.md` ("Health-Check-Endpunkte ... zeigen sauber die eigenständige Lebensfähigkeit beider Prozesse"). Sinnvoller erster Nachweis, dass der Prozess läuft, bevor irgendein Datenmodell existiert.
- **Eigene virtuelle Umgebung pro Prozess** (`core-app/.venv`, später `notification-worker/.venv`): Unterstreicht die Prozess-Unabhängigkeit auch auf Abhängigkeits-Ebene — beide Prozesse haben getrennte `requirements.txt`, keine gemeinsame Umgebung.

## Verifikation

```
cd core-app
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python app.py
```

Aufruf von `http://127.0.0.1:3000/health` liefert:

```json
{"service": "core-app", "status": "ok"}
```

Lokal getestet (venv angelegt, Flask installiert, Server gestartet, `curl` gegen `/health` ausgeführt, Antwort verifiziert, Server wieder gestoppt).

## Nächster Schritt

Schritt 2: Task-Datenmodell + CHKP-FUNC-001 bis 003 (Task anlegen, Buffer-Deadline- und Checkpoint-Berechnung).
