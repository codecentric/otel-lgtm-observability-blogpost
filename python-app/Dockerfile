FROM python:3.9-slim

# Setzt das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiert zuerst nur die requirements, um den Docker-Build-Cache zu nutzen
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Kopiert den gesamten Inhalt des python-app Ordners in das /app Verzeichnis im Container
COPY . .

# Startet den Server und macht ihn nach außen verfügbar
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5002"]
