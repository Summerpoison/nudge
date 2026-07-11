# Setup-Entscheidung: Tooling & Nachweis der Prozess-Unabhängigkeit

**Status:** Entschieden, MVP-relevant
**Kontext:** Klärung, wie die getrennten Prozesse (Kern-App / Notification-Worker) lokal entwickelt, getestet und die geforderte "Distributed"-Eigenschaft (getrennte, unabhängig lauffähige Prozesse) glaubwürdig nachgewiesen wird.

---

## 1. Docker: bewusst vorerst nicht genutzt

**Ausgangslage:** Docker Desktop lässt sich lokal nicht nutzen (Virtualisierungs-Voraussetzung unter Win10 nicht erfüllbar, vermutlich BIOS-seitige Virtualisierungseinstellung).

**Entscheidung:** Kein Blocker für das Kernziel. "Distributed" bedeutet **getrennte Prozesse**, nicht zwingend **getrennte Container**. Kern-App und Notification-Worker werden stattdessen als zwei separate, unabhängig gestartete lokale Programme betrieben (zwei Terminals, zwei OS-Prozesse mit eigener PID), die ausschließlich über HTTP miteinander kommunizieren (REST-Polling, siehe separate Architekturentscheidung zur Kommunikationsform).

```
Terminal 1: core-app       → läuft z. B. auf Port 3000
Terminal 2: notification-worker → läuft z. B. auf Port 3001, pollt Port 3000
```

**Einordnung:** Erfüllt die Distributed-Definition ("etwas erledigt eine Aufgabe und sendet an einen zweiten Teil, der die Daten verarbeitet") vollständig, ohne Container-Infrastruktur. Docker bleibt als möglicher späterer Ausbauschritt (Portfolio-Politur) im Hinterkopf, ist aber kein Muss für den Nachweis.

## 2. Mailpit statt echtem E-Mail-Server

**Problem:** Für den Weekly-Review-Loop (Modul 4) muss E-Mail-Versand und -Empfang getestet werden, ohne bei jedem Testlauf echte Mails zu verschicken.

**Entscheidung:** Mailpit (Docker-frei als Windows-Binary installierbar, falls Docker weiterhin nicht verfügbar ist) fängt SMTP-Versand lokal ab und macht ihn über eine Web-UI sowie eine API einsehbar — inklusive Abruf für den simulierten IMAP-Antwortzyklus. Damit lässt sich der komplette Zyklus (Mail raus → Antwort rein → Verarbeitung) ohne echtes Postfach durchspielen.

**Für die Abgabe/Demo optional:** Einmaliger Testlauf mit echtem Test-Postfach (z.B. separates Gmail-Konto) als zusätzlicher Beleg, dass es auch "in echt" funktioniert — nicht als Dauerlösung fürs Entwickeln.

## 3. Nachweis der Prozess-Unabhängigkeit

Drei Ebenen, gestaffelt nach Aufwand:

1. **Manueller Beweis (Minimalanforderung für die Doku):** Kern-App starten, Notification-Worker *nicht* starten → zeigen, dass die Kern-App normal nutzbar bleibt. Danach umgekehrt: Kern-App stoppen, Notification-Worker läuft weiter (loggt ggf. Fehler beim Pollen, stürzt aber nicht ab). Screenshot oder kurzes GIF von beiden Zuständen ist der zentrale Beleg für die Abgabe.
2. **Health-Check-Endpunkte:** Jeder Service bekommt eine eigene `/health`-Route, die unabhängig antwortet — zeigt sauber die eigenständige Lebensfähigkeit beider Prozesse.
3. **Log-getrennte Beobachtung:** Laufendes Beobachten der Worker-Logs während die Kern-App neu gestartet wird, um zu zeigen, dass der Worker unbeeinflusst weiterläuft.

**Für die Abgabe ausreichend:** Stufe 1 (manueller Beweis mit Screenshots/GIF). Stufen 2–3 sind Ausbaustufen, falls Zeit bleibt.

## 4. Minimal-Toollandschaft

Bewusst schlank gehalten, keine Tools "weil sie in der Präsentation vorkamen", sondern nur was tatsächlich gebraucht wird:

- **Claude Code (CLI)** — Hauptwerkzeug für die Kern-App-Entwicklung, Schritt-für-Schritt mit MD-Dokumentation
- **Kilo Code (VSCode-Plugin)** — Nachweis der zweiten geforderten Werkzeugkategorie, punktuell für Teile des Notification-Workers genutzt
- **Postman/Insomnia** — manuelles Testen der REST-Schnittstelle zwischen den beiden Prozessen, unabhängig von der UI
- **Mailpit** — SMTP/IMAP-Fake, siehe oben
- **Ollama** (später, nur falls die KI-Variante der Prio-Verarbeitung umgesetzt wird) — lokal bereits vorhanden aus früheren Experimenten, GTX 1070 ausreichend für Qwen 2.5 7B

**Bewusst nicht genutzt:** Message-Queues (Kafka/RabbitMQ), Kubernetes, Docker (siehe Punkt 1) — für die Größenordnung von Nudge nicht notwendig; REST-Polling deckt den Bedarf vollständig ab. Wird im Bericht als bewusste Abgrenzung dokumentiert, nicht als Lücke.
