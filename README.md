🚀 Lokaler Observability Stack mit FastAPI, Alloy, Loki, Tempo, Prometheus & Grafana

Dieses Projekt demonstriert einen vollständigen, lokalen Observability-Stack. Es besteht aus:

    FastAPI App 🐍: Eine einfache Python-Anwendung, die Logs, Traces und Metriken erzeugt.

    Alloy: Ein Agent, der Logs und Traces sammelt und an Loki bzw. Tempo sendet. Hier kannst du den Status des Collectors überprüfen und die rohen Logs oder Traces einsehen.

    Loki: Ein System zum Speichern und Abfragen von Logs.

    Tempo: Ein System zum Speichern und Abfragen von Traces.

    Prometheus: Ein System zum Speichern und Abfragen von Metriken.

    Grafana 📊: Ein Dashboard-Tool zur Visualisierung der Logs und Traces.

Alle Dienste werden über Docker Compose verwaltet.

📋 Voraussetzungen

    Docker

    Docker Compose

    Python 3.9+ (nur für die lokale FastAPI-Entwicklung)

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
