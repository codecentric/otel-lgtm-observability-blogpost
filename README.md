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

Beispiel eines rohen Metrik Eintrages in alloy `prometheus.remote_write.to_prometheus`

```
http_server_name="localhost:5002", http_status_code="500", http_target="/task", job="python-app", le="+Inf", net_host_port="5002"}, value=5.000000
metadata: labels={__name__="tasks_processed_total"}, type="counter", unit="1", help="Zählt die Gesamtzahl der verarbeiteten Tasks"
sample: ts=1751879547153, labels={__name__="tasks_processed_total", job="python-app", success="true"}, value=8.000000
```

Wichtige Bereiche:

    __name__="tasks_processed_total": Dies ist der Name der Metrik. Er ist entscheidend, um die Daten in Prometheus oder Grafana abzufragen.

    value=8.000000: Dies ist der eigentliche Messwert. Da es sich um einen Zähler (counter) handelt, zeigt dieser Wert an, dass insgesamt 8 Tasks erfolgreich verarbeitet wurden.

    success="true": Dies ist ein Label (eine Dimension), das den Messwert genauer beschreibt. Es ermöglicht dir, zwischen erfolgreichen (true) und fehlgeschlagenen (false) Tasks zu filtern.

    type="counter": Dieser Metadateneintrag sagt aus, dass es sich um einen Zähler handelt. Das bedeutet, der Wert kann nur ansteigen oder gleich bleiben.

    ts=1751879547153: Dies ist der Zeitstempel (Timestamp) in Millisekunden, der angibt, wann der Messwert erfasst wurde.

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
Doku
orientieren: https://grafana.com/docs/grafana/latest/administration/correlations/create-a-new-correlation/#create-a-correlation-with-provisioning

Dieses Setup ist so konfiguriert, dass du direkt von einem Trace zu den zugehörigen Logs springen kannst.

    Wenn du dir einen einzelnen Trace in der Tempo-Ansicht ansiehst, siehst du bei jedem "Span" (jeder einzelnen Operation) ein kleines Ketten-Symbol.

    Ein Klick auf dieses Symbol öffnet ein neues Fenster mit genau den Logs aus Loki, die während dieser spezifischen Operation geschrieben wurden.

# 🪙 Metriken mit Prometheus und OpenTelemetry

Neben Logs und Traces sind Metriken die dritte Säule der Observability. Sie geben uns aggregierte, numerische Einblicke
in den Zustand unserer Anwendung über die Zeit.

## Was ist Prometheus?

Prometheus ist ein führendes Open-Source-System zur Überwachung und Alarmierung. Es sammelt und speichert Daten als
Zeitreihen (Time Series), d.h., Metrikwerte werden zusammen mit einem Zeitstempel erfasst. Dies ist ideal, um Graphen zu
erstellen und das Verhalten einer Anwendung zu analysieren (z.B. "Wie viele Anfragen pro Sekunde hat unser Service
letzte Woche verarbeitet?").

In unserem Stack ist Prometheus der Speicher für unsere Anwendungsmetriken. Der Datenfluss sieht so aus:

    Die FastAPI-App erzeugt Metriken (z.B. einen Zähler für verarbeitete Tasks) mit dem OpenTelemetry SDK.

    Alloy empfängt diese Metriken über das OTLP-Protokoll.

    Alloy leitet die Metriken per remote_write an Prometheus weiter.

    Grafana fragt Prometheus ab, um die Metriken zu visualisieren.

## Welche Code-Änderungen waren nötig?

Um die Metriken von der App zu Prometheus zu bekommen, waren zwei Änderungen entscheidend:

    In app.py (Python-Anwendung):

        Änderung: Wir haben dem manuell erstellten MeterProvider einen PeriodicExportingMetricReader mit einem OTLPMetricExporter hinzugefügt.

        Grund: Die OTEL_* Umgebungsvariablen konfigurieren nur die automatische Instrumentierung. Für manuell erstellte Metriken, wie unseren tasks_processed_counter, müssen wir dem Code explizit sagen, wie und wohin er die Metriken exportieren soll. Ohne diesen Codeblock erzeugt die Anwendung zwar Metriken, sendet sie aber nie ab.

    In docker-compose.yaml (Prometheus-Dienst):

        Änderung: Wir haben das Startkommando des Prometheus-Containers um das Flag --web.enable-remote-write-receiver erweitert.

        Grund: Standardmäßig ist Prometheus darauf ausgelegt, Metriken von Zielen aktiv abzufragen (Scraping). In unserem Aufbau sendet Alloy die Metriken jedoch aktiv an Prometheus (Pushing). Dieses Flag aktiviert den Endpunkt, an dem Prometheus diese gesendeten Daten empfangen kann. Ohne es würde Prometheus die Daten von Alloy einfach ablehnen.

## Metriken erkunden

So kannst du deine neuen Metriken in Grafana ansehen:

    Gehe wie gewohnt in den Explore-Bereich (Kompass-Symbol).

    Wähle oben als Datenquelle Prometheus aus.

    Klicke auf den Button Metric explorer oder gib direkt den Namen der Metrik tasks_processed_total in das Abfragefeld ein.

    Klicke auf Run query.

Du siehst nun den Graphen des Zählers. Du kannst die Abfrage weiter verfeinern, z.B. um nur erfolgreiche oder
fehlgeschlagene Tasks anzuzeigen:
tasks_processed_total{success="true"}

# ✅ TODO
