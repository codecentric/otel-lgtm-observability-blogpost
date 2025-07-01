# Makefile für den Observability Stack

# .PHONY deklariert "virtuelle" Ziele, die nicht von Dateien auf der Festplatte abhängen.
.PHONY: help install run up down logs clean ps

# Standardziel, das ausgeführt wird, wenn man nur "make" eingibt. Zeigt eine Hilfe an.
all: help

help:
	@echo "Verfügbare Befehle:"
	@echo "------------------"
	@echo "make install - Installiert die Python-Abhängigkeiten mit uv (lokal)"
	@echo "make run     - Startet die FastAPI-Anwendung lokal auf Port 5002"
	@echo "make up      - Startet alle Dienste mit docker-compose im Hintergrund"
	@echo "make down    - Stoppt alle Dienste"
	@echo "make logs    - Zeigt die Logs aller laufenden Dienste an"
	@echo "make ps      - Zeigt den Status der Docker-Container an"
	@echo "make clean   - Stoppt alle Dienste und löscht Volumes und Netzwerke"


# Installiert die Python-Pakete für die lokale Entwicklung.
install:
	@echo "--> Installiere Python-Abhängigkeiten mit uv..."
	(cd python-app && uv pip install -r requirements.txt)

# Startet die FastAPI-App lokal mit Hot-Reload.
run:
	@echo "--> Starte FastAPI-Anwendung lokal auf http://localhost:5002 ..."
	(cd python-app && uvicorn app:app --reload --port 5002)

# Startet die gesamte Docker-Compose-Umgebung im Hintergrund.
up:
	@echo "--> Starte Docker-Compose-Stack im Hintergrund..."
	docker-compose up -d

# Stoppt die Docker-Compose-Umgebung.
down:
	@echo "--> Stoppe Docker-Compose-Stack..."
	docker-compose down

# Zeigt die Live-Logs aller laufenden Container an.
logs:
	@echo "--> Zeige Logs an (mit Strg+C beenden)..."
	docker-compose logs -f

# Zeigt den Status der von docker-compose verwalteten Container an.
ps:
	@echo "--> Aktueller Status der Docker-Container:"
	docker-compose ps

# Fährt die Umgebung herunter und löscht alle zugehörigen Daten und Netzwerke.
clean:
	@echo "--> Stoppe und bereinige den Docker-Compose-Stack (inkl. Volumes)..."
	docker-compose down --volumes
	docker network prune -f

# Führt die Linter und Formatierer auf allen Dateien aus.
lint:
	@echo "--> Führe Linter (Ruff) auf allen Dateien aus..."
	pre-commit run --all-files
