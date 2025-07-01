Lokaler Observability Stack mit FastAPI, Loki und Grafana

Dieses Projekt demonstriert einen vollständigen, lokalen Observability-Stack. Es besteht aus:

    FastAPI App: Eine einfache Python-Anwendung, die Logs erzeugt.

    Loki: Ein System zum Speichern und Indizieren dieser Logs.

    Alloy: Ein Agent, der die Logs von der App sammelt und an Loki sendet.

    Grafana: Ein Dashboard-Tool zur Visualisierung der in Loki gespeicherten Logs.

Alle Dienste werden über Docker Compose verwaltet.
Voraussetzungen

    Docker

    Docker Compose

    Python 3.9+ (nur für die lokale FastAPI-Entwicklung)

Lokale Entwicklung (nur FastAPI)

Wenn du nur die FastAPI-Anwendung ohne den Rest des Stacks lokal testen möchtest:

1. Python-Abhängigkeiten installieren

Navigiere in den python-app-Ordner und installiere die benötigten Pakete in einer virtuellen Umgebung:

cd python-app
pip install -r requirements.txt

2. FastAPI-Server starten

Führe im python-app-Ordner folgenden Befehl aus:

uvicorn app:app --reload --port 5002

Die API ist nun unter http://localhost:5002 erreichbar.
Kompletter Stack mit Docker Compose

1. Alle Dienste starten

Führe im Hauptverzeichnis des Projekts (wo die docker-compose.yml liegt) folgenden Befehl aus:

docker-compose up -d

Dadurch werden alle Dienste (python-app, loki, alloy, grafana) im Hintergrund gestartet.

2. Zugriff auf die Dienste

   FastAPI App: Die Anwendung ist über deinen Browser erreichbar unter:

        http://localhost:5002

   Alloy UI: Die Debugging-Oberfläche von Alloy ist erreichbar unter:

        http://localhost:12345
        Hier kannst du den Status des Log-Collectors überprüfen, aber nicht die Logs selbst einsehen.

   Loki: Loki bietet keine Benutzeroberfläche für den direkten Zugriff. Der Aufruf von http://localhost:3100 im Browser
   führt zu einem 404 Fehler, was normales Verhalten ist. Loki dient nur als Datenspeicher für Grafana.

3. Logs in Grafana ansehen

Grafana ist das zentrale Werkzeug, um deine Logs zu visualisieren.

    Grafana öffnen: Gehe im Browser zu http://localhost:3000.

    Einloggen: Die Standard-Anmeldedaten sind:

        Benutzername: admin

        Passwort: admin

    Datenquelle finden: Die Loki-Datenquelle wurde durch das Setup bereits automatisch konfiguriert. Du musst hier nichts weiter tun.

    Logs erkunden:

        Klicke im linken Menü auf das Kompass-Symbol (Explore).

        Klicke auf den Button "Log browser".

        Ein neues Label namens service_name sollte verfügbar sein (dank unserer Alloy-Konfiguration). Wähle dieses Label aus.

        Wähle aus der Liste der Werte den Dienst python-app aus.

        Klicke auf den blauen Button "Show logs".

Du siehst nun alle Logs, die von deiner FastAPI-Anwendung erzeugt wurden. Passe bei Bedarf den Zeitbereich oben rechts
an (z.B. auf "Last 5 minutes").

# Todo
- zero code implementation
- send info via grpc
- connect traces and logs
- muss in der tempo yaml noch http rein?
