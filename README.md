# 🚀 Lokaler Observability Stack mit FastAPI, Alloy, Loki, Tempo, Prometheus & Grafana

Dieses Projekt demonstriert einen vollständigen, lokalen Observability-Stack. Es besteht aus:

- FastAPI App 🐍: Eine einfache Python-Anwendung, die Logs, Traces und Metriken erzeugt.

- Alloy: Ein Agent, der Logs und Traces sammelt und an Loki bzw. Tempo sendet. Hier kannst du den Status des Collectors überprüfen und die rohen Logs oder Traces einsehen.

- Loki: Ein System zum Speichern und Abfragen von Logs.

- Tempo: Ein System zum Speichern und Abfragen von Traces.

- Prometheus: Ein System zum Speichern und Abfragen von Metriken.

- Grafana 📊: Ein Dashboard-Tool zur Visualisierung der Logs und Traces.

Alle Dienste werden über Docker Compose verwaltet.

# 📋 Voraussetzungen

- Docker

- Docker Compose

- Python 3.9+ (nur für die lokale FastAPI-Entwicklung)

# 🌱 Entwicklung des Stacks

Das Repository ist schrittweise über drei Feature-Branches gewachsen, um die einzelnen Säulen der Observability
nacheinander einzuführen:

- Logs (`feat/api-loki-alloy-grafana`): Zuerst wurde eine FastAPI-App implementiert, die Logs erzeugt. Diese Logs werden
  vom Docker-Daemon an Alloy weitergeleitet, welches sie zur Speicherung an Loki sendet. In Grafana können die Logs
  visualisiert werden.

- Traces (`feat/api-loki-alloy-grafana-tempo-otel`): Im zweiten Schritt wurde die Anwendung mit OpenTelemetry
  instrumentiert. Alloy sammelt nun Logs und die neu hinzugekommenen Traces über das OTLP-Protokoll und leitet die
  Traces an Tempo weiter.

- Metriken (`feat/api-loki-alloy-grafana-tempo-otel-metrics`): Abschließend wurde der Stack um Metriken erweitert. Die
  Anwendung generiert nun auch Metriken, die von Alloy gesammelt und in Prometheus gespeichert werden. Damit ist der
  Stack mit allen drei Säulen der Observability komplett.

# 🐍 Lokale FastAPI

Die FastAPI (`app.py`) hat einen GET-Endpunkt (`/task`) und simuliert die Verarbeitung einer Aufgabe, die fehlschlagen
kann. Die
Funktion hat eine 20%ige Wahrscheinlichkeit, einen Fehler zu simulieren
und einen HTTP-Statuscode 500 auszulösen. Bei Erfolg wird eine
Erfolgsmeldung zurückgegeben. Die App generiert folglich zwei repräsentative Beispiele, für nützliche Logs.

Wenn du nur die FastAPI-Anwendung ohne den Rest des Stacks lokal testen möchtest:

1. Python-Abhängigkeiten installieren

```bash
make install
```

2. FastAPI-Server starten

```bash
make run
```

Die API ist nun unter http://localhost:5002 erreichbar.

# 🐳 Kompletter Stack mit Docker Compose

1. Alle Dienste starten

Führe im Hauptverzeichnis des Projekts (wo die docker-compose.yml liegt) folgenden Befehl aus:

```bash
docker-compose up -d
```

Dadurch werden alle Dienste (python-app, loki, tempo, alloy, grafana, prometheus) gestartet.

2. Zugriff auf die Dienste

- FastAPI App: http://localhost:5002
- Alloy UI: http://localhost:12345
- Loki, Tempo & Prometheus: Diese Dienste bieten keine eigene Benutzeroberfläche. Der Aufruf von http://localhost:3100 (
  Loki)
  oder http://localhost:3200 (Tempo) im Browser führt zu einem Fehler, was normales Verhalten ist. Sie dienen nur als
  Datenspeicher für Grafana. Prometheus bietet hingegen eine eigene Weboberfläche unter http://localhost:9090. Hier
  kannst du den Status deiner angebundenen Ziele (Targets) einsehen und Metriken direkt mit der Abfragesprache PromQL
  untersuchen.
- Grafana: http://localhost:3000

# Der Lebenszyklus der Telemetriedaten

Die `config.alloy`-Datei ist die zentrale Konfigurationsdatei für Grafana Alloy. Sie fungiert als Bauplan, der den
gesamten Lebenszyklus der Telemetriedaten definiert – von der Erfassung bis zur Weiterleitung.

In dieser Datei legen Sie eine Daten-Pipeline fest, die aus drei Hauptteilen besteht:

- Inputs und Receiver: Hier wird definiert, woher die Daten kommen. Das können zum Beispiel Logs von Docker-Containern,
  Metrik-Endpunkte von Prometheus oder Traces von Anwendungen sein.

- Verarbeitung (Processing): In diesem Schritt wird festgelegt, wie die gesammelten Daten transformiert werden sollen.
  Typische Aktionen sind das Filtern von unwichtigen Informationen oder das Hinzufügen und Umbenennen von Labels, um die
  Daten für Analysen besser nutzbar zu machen.

- Outputs und Exporter: Schließlich wird hier konfiguriert, wohin die aufbereiteten Daten gesendet werden sollen, zum
  Beispiel Logs an Loki, Metriken an Prometheus oder Traces an Tempo.

# Log Discovery ohne OpenTelemetry

Im Branch `feat/api-loki-alloy-grafana` startest du mit dem Erfassen von Logs.
Die discovery.docker-Komponente überwacht kontinuierlich den Docker-Daemon, um eine stets aktuelle Liste aller laufenden
Container zu erhalten. Jeder dieser Container wird zu einem "Ziel" für die Log-Sammlung.

Sobald ein Container als Ziel identifiziert ist, greift die loki.source.docker-Komponente auf dessen Log-Stream zu.
Während die Logs eingelesen werden, kommt der entscheidende Schritt des Relabelings: Aus den Metadaten des Containers,
wie zum Beispiel seinem Namen, wird automatisch ein sauberes service_name-Label generiert. Dieser Mechanismus sorgt
dafür, dass Logs nicht nur gesammelt, sondern auch intelligent mit Kontext angereichert werden, bevor sie zur
Speicherung an Loki weitergeleitet werden.

## 🛠️ Live Debugging mit Alloy

Alloy bietet eine nützliche Weboberfläche, um den Fluss deiner Telemetriedaten in Echtzeit zu überprüfen. Das ist
besonders praktisch, um zu sehen, ob deine Anwendung korrekt Daten sendet und ob Alloy diese wie erwartet empfängt.

Du kannst dieses feature in der `config.alloy` aktivieren per

```river
livedebugging {
  enabled = true
}
```

1. Alloy UI öffnen: Gehe zu http://localhost:12345.
2. Komponente auswählen: Klicke im linken Menü auf Component Explorer.
3. Receiver debuggen: Wähle die Komponente `discovery.docker.linux` aus. Hier kommen alle Daten von deiner FastAPI-App
   an.
4. Live-Daten ansehen: Klicke auf den Debug Tab. Du siehst nun die rohen Logs, die Alloy vom Docker-Daemon mitbekommt.
5. Daten generieren: Greife auf den `task` Endpunkt der FastAPI zu (http://localhost:5002/task). Rohe Logs erscheinen
   nun
   in den Live-Daten.

Die wichtigsten Felder hier sind:

- `__meta_docker_container_name`: Der Name des laufenden Containers (/alloy). Dies ist die häufigste Quelle, um daraus
  ein service_name-Label für Logs oder Metriken zu erstellen.

- `__meta_docker_container_label_com_docker_compose_service`: Der Service-Name aus der docker-compose.yml-Datei (alloy).
  Dieses Feld ist extrem nützlich, um zuverlässig zu identifizieren, zu welchem Dienst der Container gehört.

- `__meta_docker_network_ip`: Die interne IP-Adresse, die der Container innerhalb des Docker-Netzwerks hat.

# 📈 Visualisierung per Grafana - Logs

Grafana ist das zentrale Werkzeug, um deine Telemetriedaten zu visualisieren.

1. Grafana öffnen: Gehe im Browser zu http://localhost:3000.

2. Einloggen: Die Standard-Anmeldedaten sind:

        Benutzername: admin

        Passwort: admin

3. Datenquellen finden: Die Datenquellen für Loki wurden bereits automatisch konfiguriert in der .

4. Logs erkunden

    - Klicke im linken Menü auf das Kompass-Symbol (Explore).

    - Stelle sicher, dass oben als Datenquelle Loki ausgewählt ist.

    - Klicke auf den Button Log browser.

    - Wähle das Label service_name und den Wert python-app aus.

    - Klicke auf "Run query".

Du siehst nun alle Logs, die von deiner FastAPI-Anwendung erzeugt wurden.

# App Instrumentation mit OpenTelemetry

Im nächsten Schritt instrumentierst du die App per OpenTelemetry und sammelst nun auch Trace Daten ein. Dies geschieht
im Branch `feat/api-loki-alloy-grafana-tempo-otel`. In diesem Branch kommen OpenTelemetry SDKs und APIs als Dependencies
dazu. Vergewissere dich, dass deine python Umgebung diese enthält. Führe dazu ggf. nochmal

```bash
make install
```

aus.

Um zu überprüfen, ob das Sammeln von Traces und Logs per OpenTelemetry funktioniert, kannst du dir lokal an Standardout
ausgeben lassen.
Starte die API und OpenTelemetry dafür folgendermaßen:

```bash
opentelemetry-instrument \
    --traces_exporter console \
    --logs_exporter console \
    --service_name python-app \
    uvicorn app:app --host 0.0.0.0 --port 5001
```

`opentelemetry-instrument` ist das Werkzeug zur automatischen Instrumentierung. Es startet die Python-Anwendung und
"injiziert" dabei Code, um Traces und Logs zu erfassen, ohne dass du den Quellcode deiner Anwendung manuell
ändern musst.

Um OpenTelemetry mit Alloy, den Exportern und Grafana zu verknüpfen sind wenige Code Änderungen
nötig:

1. Eine `tempo-config.yaml` kommt dazu.
2. Die `docker-compose.yaml` wird um den Service Tempo erweitert. Außerdem aktiviert die Umgebungsvariable
   `OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED` die
   automatische Instrumentierung für das Logging in Python-Anwendung.
3. Das Dockerfile ändert sich. Die App wird im Container nun per

```Docker
CMD ["opentelemetry-instrument", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5002"]
```

gestartet.

4. Die `config.alloy` ändert sich entscheidend. Die Logs werden nicht mehr von Docker, sondern durch OpenTelemetry
   gescraped. Außerdem kommt Tempo nun als Exporter dazu.

5. Vorab-Definition von Datenquellen: In einer `datasources.yaml` konfigurierst du nun auch automatisch zwei
   Datenquellen für Grafana: eine für Loki zur
   Log-Analyse und eine für Tempo zur Trace-Analyse.

Außerdem, da Alloy die Logs nicht mehr direkt von Docker abgreift (`loki.source.docker`), benötigt der Container keinen
Zugriff mehr auf den Docker-Socket. Wir können dieses Volume in der `docker-compose.yaml` entfernen, um die Sicherheit
zu erhöhen, da der Alloy-Container nun weniger Rechte auf dem Host-System hat.

## Logs und Traces verbinden

Logs können Details zu einem Fehler liefern, ihnen fehlt es aber häufig an
Kontext-Informationen zur gesamten Anfrage, die diesen Fehler provoziert hat. Traces hingegen zeigen diesen Kontext aber
gehen oft nicht genug ins Detail, um den Fehler zu debuggen. Um ein möglichst vollständiges Bild über das Verhalten der
App
zu bekommen, kannst du die Signale mehrerer Observability
Säulen miteinander korrelieren. Dank OpenTelemetry kannst du nun u.a. Logs und Traces
miteinander verbinden. Denn OpenTelemetry gibt Logs und Traces korrelierbare Metainformationen (u.a. die TraceID) mit.

In Grafana musst du dafür eine Correlation zwischen Traces und Logs einrichten. Das machst du
per Administration > Correlation und folgst dabei dieser
Anleitung https://grafana.com/docs/grafana/latest/datasources/tempo/traces-in-grafana/trace-correlations/.
Die query für Loki sieht dabei so aus:

```
{service_name="$serviceName"} | json | traceid=`$traceID`
```

Du kannst die Correlation aber auch vorab über die `datasources.yaml` konfigurieren. Dabei kannst du dich an dieser
Doku
orientieren: https://grafana.com/docs/grafana/latest/administration/correlations/create-a-new-correlation/#create-a-correlation-with-provisioning

Grafana ermöglicht es dir nun direkt aus einer Trace-Ansicht in
Tempo zu den zugehörigen Logs in Loki zu springen. Dies geschieht durch die vordefinierte Abfrage, die automatisch die
Trace-ID des aktuell angezeigten Traces verwendet, um die exakt passenden Log-Einträge zu finden und anzuzeigen. Wenn du
dir einen einzelnen Trace in der Tempo-Ansicht ansiehst, siehst du bei jedem "Span" (jeder einzelnen Operation) ein
kleines Ketten-Symbol. Ein Klick auf dieses Symbol öffnet ein neues Fenster mit genau den Logs aus Loki, die während
dieser spezifischen Operation geschrieben wurden.

# 🛠️ Live Debugging mit Alloy - otel, loki & tempo

Da sich die `config.alloy` geändert hat sieht nun der Zugriff auf die Live-Debugging Informationen anders aus.
In der Komponente `otelcol.receiver.otlp.default` kommen nun alle Logging und Tracing Daten von deiner FastAPI-App an.

Durch die Auto-Instrumentierung werden Traces automatisch mit Log-Informationen angereichert. Ein einzelner
Trace-Eintrag
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

Wichtige Felder sind hierbei:

- Trace ID: Die eindeutige ID für die gesamte Anfrage (den Trace). Alle Spans und Logs, die zu dieser Anfrage gehören,
  teilen sich diese ID.

- Span ID: Die eindeutige ID für eine spezifische Operation (den Span) innerhalb des Traces.

- Body: Der eigentliche Inhalt der Log-Nachricht.

- Attributes: Metadaten zum Log. Hier siehst du die automatische Korrelation in Aktion:
    - `otelTraceID` und `otelSpanID` verknüpfen den Log-Eintrag direkt mit dem Trace.
    - `code.function.name` und `code.line.number` zeigen dir genau, wo im Code der Log ausgelöst wurde.

Ein einzelner Log-Eintrag im Debugger sieht so aus:

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
ObservedTimestamp: 2025-07-02 12:41:35.756210641 +0000 UTC
Timestamp: 2025-07-02 12:41:35.7560576 +0000 UTC
SeverityText: INFO
SeverityNumber: Info(9)
Body: Str(Starte Verarbeitung von Task #9841...)
Attributes:
     -> otelSpanID: Str(26ea5b2e990e1895)
     -> otelTraceID: Str(f935b2cd27ca22c89a60ccee282aaceb)
     -> otelTraceSampled: Bool(true)
     -> otelServiceName: Str(python-app)
     -> code.file.path: Str(/app/app.py)
     -> code.function.name: Str(process_task)
     -> code.line.number: Int(73)
```

Wichtige Felder sind hierbei:

- Resource attributes: Beschreiben die Anwendung, die die Daten sendet. `service.name` ist hier das wichtigste Attribut,
  da es in Grafana zur Filterung verwendet wird.

- ScopeLogs: Gruppiert Logs, die von derselben Instrumentierungsbibliothek stammen.

- LogRecord: Enthält die eigentliche Log-Information, wie bereits oben beschrieben.
