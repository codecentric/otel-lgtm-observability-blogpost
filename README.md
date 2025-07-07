🚀 Lokaler Observability Stack mit FastAPI, Loki, Tempo & Grafana

Dieses Projekt demonstriert einen vollständigen, lokalen Observability-Stack. Es besteht aus:

    FastAPI App 🐍: Eine einfache Python-Anwendung, die Logs und Traces erzeugt.

    Loki: Ein System zum Speichern und Indizieren von Logs.

    Tempo: Ein System zum Speichern und Abfragen von Traces.

    Alloy: Ein Agent, der Logs und Traces sammelt und an Loki bzw. Tempo sendet.

    Grafana 📊: Ein Dashboard-Tool zur Visualisierung der Logs und Traces.

Alle Dienste werden über Docker Compose verwaltet.

📋 Voraussetzungen

    Docker

    Docker Compose

    Python 3.9+ (nur für die lokale FastAPI-Entwicklung)

# 🐍 Lokale Entwicklung (nur FastAPI)

Wenn du nur die FastAPI-Anwendung ohne den Rest des Stacks lokal testen möchtest:

1. Python-Abhängigkeiten installieren

Navigiere in den python-app-Ordner und installiere die benötigten Pakete in einer virtuellen Umgebung:
Bash

cd python-app
pip install -r requirements.txt

2. FastAPI-Server starten

Führe im python-app-Ordner folgenden Befehl aus:
Bash

uvicorn app:app --reload --port 5002

Die API ist nun unter http://localhost:5002 erreichbar.

# 🐳 Kompletter Stack mit Docker Compose

1. Alle Dienste starten

Führe im Hauptverzeichnis des Projekts (wo die docker-compose.yml liegt) folgenden Befehl aus:
Bash

docker-compose up -d

Dadurch werden alle Dienste (python-app, loki, tempo, alloy, grafana) im Hintergrund gestartet.

2. Zugriff auf die Dienste

   FastAPI App: http://localhost:5002

   Alloy UI: http://localhost:12345

        Hier kannst du den Status des Collectors überprüfen und die rohen Logs oder Traces einsehen.

   Loki & Tempo: Diese Dienste bieten keine eigene Benutzeroberfläche. Der Aufruf von http://localhost:3100 (Loki)
   oder http://localhost:3200 (Tempo) im Browser führt zu einem Fehler, was normales Verhalten ist. Sie dienen nur als
   Datenspeicher für Grafana.
   Grafana: http://localhost:3000

# Zero-Code Log Instrumentation

Die Umgebungsvariable OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED aktiviert die automatische Instrumentierung für
das Logging in Python-Anwendungen, die OpenTelemetry verwenden.

Wenn diese Variable auf true gesetzt ist, fängt das OpenTelemetry-Python-Agentenmodul automatisch Log-Einträge ab, die
von der Standard-logging-Bibliothek in Python erzeugt werden.

Was bewirkt die Aktivierung?

    Keine Code-Änderungen erforderlich: Du musst deinen Anwendungscode nicht manuell anpassen.

    Automatische Korrelation: Die Logs werden automatisch mit Traces und Metriken korreliert, was die Fehlersuche erheblich vereinfacht.

    Einfache Konfiguration: Die Aktivierung erfolgt unkompliziert durch das Setzen dieser einen Umgebungsvariable.

Wichtig: Die alloy config ändert sich!
Die folgenden Blöcke aus dem master branch sind für die instrumentierte Anwendung überflüssig, da die Logs nicht mehr
von Docker, sondern durch otel gescraped werden:

    discovery.docker "linux"

    discovery.relabel "logs_integrations_docker"

    loki.source.docker "default

Außerdem, da Alloy die Logs nicht mehr direkt von Docker abgreift (loki.source.docker), benötigt der Container keinen
Zugriff mehr auf den Docker-Socket. Wir können dieses Volume in der docker-compose,yml entfernen, um die Sicherheit zu
erhöhen, da der
Alloy-Container nun weniger Rechte auf dem Host-System hat.

# 🛠️ Live Debugging mit Alloy

Alloy bietet eine nützliche Weboberfläche, um den Fluss deiner Telemetriedaten in Echtzeit zu überprüfen. Das ist
besonders praktisch, um zu sehen, ob deine Anwendung korrekt Daten sendet und ob Alloy diese wie erwartet empfängt.

    Alloy UI öffnen: Gehe zu http://localhost:12345.

    Komponente auswählen: Klicke im linken Menü auf Component Explorer.

    Receiver debuggen: Wähle die Komponente otelcol.receiver.otlp.default aus. Hier kommen alle Daten von deiner FastAPI-App an.

    Live-Daten ansehen: Klicke auf den Debug Tab. Du siehst nun die rohen Logs und Traces, die durch den Receiver fließen.

Was sehe ich beim Debuggen?

Wenn du den Receiver debuggst, siehst du die rohen Datenstrukturen, bevor sie weiterverarbeitet und an Loki oder Tempo
gesendet werden.

Beispiel eines rohen Traces (als Log)

Durch die Auto-Instrumentierung werden Logs automatisch mit Trace-Informationen angereichert. Ein einzelner Log-Eintrag
im Debugger sieht dann so aus:

```
Trace ID: f935b2cd27ca22c89a60ccee282aaceb
Span ID: 26ea5b2e990e1895
Flags: 1
LogRecord #1
ObservedTimestamp: 2025-07-02 12:41:35.756210641 +0000 UTC
Timestamp: 2025-07-02 12:41:35.7560576 +0000 UTC
SeverityText: INFO
SeverityNumber: Info(9)
Body: Str(Task #7743 erfolgreich abgeschlossen.)
Attributes:
     -> otelSpanID: Str(26ea5b2e990e1895)
     -> otelTraceID: Str(f935b2cd27ca22c89a60ccee282aaceb)
     -> otelTraceSampled: Bool(true)
     -> otelServiceName: Str(python-app)
     -> code.file.path: Str(/app/app.py)
     -> code.function.name: Str(process_task)
     -> code.line.number: Int(81)
```

Wichtige Felder:

    Trace ID: Die eindeutige ID für die gesamte Anfrage (den Trace). Alle Spans und Logs, die zu dieser Anfrage gehören, teilen sich diese ID.

    Span ID: Die eindeutige ID für eine spezifische Operation (den Span) innerhalb des Traces.

    Body: Der eigentliche Inhalt der Log-Nachricht.

    Attributes: Metadaten zum Log. Hier siehst du die automatische Korrelation in Aktion:

        otelTraceID und otelSpanID verknüpfen den Log-Eintrag direkt mit dem Trace.

        code.function.name und code.line.number zeigen dir genau, wo im Code der Log ausgelöst wurde.

Beispiel eines rohen Logs

Logs werden in Batches gesendet, die zusätzliche Metadaten über die Quelle enthalten.

```
ResourceLog #0
Resource SchemaURL:
Resource attributes:
     -> telemetry.sdk.language: Str(python)
     -> telemetry.sdk.name: Str(opentelemetry)
     -> telemetry.sdk.version: Str(1.34.1)
     -> service.name: Str(python-app)
     -> telemetry.auto.version: Str(0.55b1)
ScopeLogs #0
ScopeLogs SchemaURL:
InstrumentationScope app
LogRecord #0
ObservedTimestamp: 2025-07-02 12:42:13.830676697 +0000 UTC
Timestamp: 2025-07-02 12:42:13.83037568 +0000 UTC
SeverityText: INFO
SeverityNumber: Info(9)
Body: Str(Starte Verarbeitung von Task #9841...)
Attributes:
     -> otelSpanID: Str(452e51fa9e9f937d)
     -> otelTraceID: Str(7c732c512779dd2f06ced7488c5621b4)
     -> otelTraceSampled: Bool(true)
     -> otelServiceName: Str(python-app)
     -> code.file.path: Str(/app/app.py)
     -> code.function.name: Str(process_task)
     -> code.line.number: Int(73)
```

Wichtige Bereiche:

    Resource attributes: Beschreiben die Anwendung, die die Daten sendet. service.name ist hier das wichtigste Attribut, da es in Grafana zur Filterung verwendet wird.

    ScopeLogs: Gruppiert Logs, die von derselben Instrumentierungsbibliothek stammen.

    LogRecord: Enthält die eigentliche Log-Information, wie bereits oben beschrieben.

Die Debug-Ansicht in Alloy ist ein mächtiges Werkzeug, um Konfigurationsprobleme schnell zu finden und zu verstehen,
welche Daten deine Anwendung tatsächlich sendet.

# 📈 Logs und Traces in Grafana ansehen

Grafana ist das zentrale Werkzeug, um deine Telemetriedaten zu visualisieren.

    Grafana öffnen: Gehe im Browser zu http://localhost:3000.

    Einloggen: Die Standard-Anmeldedaten sind:

        Benutzername: admin

        Passwort: admin

    Datenquellen finden: Die Datenquellen für Loki und Tempo wurden bereits automatisch konfiguriert.

## Logs erkunden

    Klicke im linken Menü auf das Kompass-Symbol (Explore).

    Stelle sicher, dass oben als Datenquelle Loki ausgewählt ist.

    Klicke auf den Button Log browser.

    Wähle das Label service_name und den Wert python-app aus.

    Klicke auf Show logs.

Du siehst nun alle Logs, die von deiner FastAPI-Anwendung erzeugt wurden.

## Traces erkunden

    Klicke im linken Menü auf das Kompass-Symbol (Explore).

    Wähle oben als Datenquelle Tempo aus.

    Klicke auf den Tab Search.

    Im Dropdown "Service Name" sollte python-app erscheinen. Wähle es aus.

    Klicke auf Run query.

Es wird eine Liste der letzten Traces angezeigt. Klicke auf eine Trace-ID, um eine detaillierte Ansicht (Flame Graph) zu
erhalten.

## Logs und Traces verbinden

Dafür müssen wir eine Correlation zwischen Traces und Logs einrichten. Das machen wir
per Administration > Correlation und folgen dabei dieser
Anleitung https://grafana.com/docs/grafana/latest/datasources/tempo/traces-in-grafana/trace-correlations/.
Die query für Loki sieht dabei so aus:

```
{service_name="$serviceName"} | json | traceid=`$traceID`
```
Wir können die Correlation aber auch über die datasources.yaml konfigurieren. Dabei können wir uns an dieser
Doku orientieren: https://grafana.com/docs/grafana/latest/administration/correlations/create-a-new-correlation/#create-a-correlation-with-provisioning

Dieses Setup ist so konfiguriert, dass du direkt von einem Trace zu den zugehörigen Logs springen kannst.

    Wenn du dir einen einzelnen Trace in der Tempo-Ansicht ansiehst, siehst du bei jedem "Span" (jeder einzelnen Operation) ein kleines Ketten-Symbol.

    Ein Klick auf dieses Symbol öffnet ein neues Fenster mit genau den Logs aus Loki, die während dieser spezifischen Operation geschrieben wurden.

# ✅ TODO

    [ ] Metriken hinzufügen, wie in der OpenTelemetry-Dokumentation beschrieben.

    [x] Traces und Logs verknüpfen.
