import logging
import random

from fastapi import FastAPI, HTTPException

# Konfiguriert das grundlegende Logging-Format für die Anwendung.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()


@app.get("/")
async def home():
    """
    Stellt einen einfachen Willkommens-Endpunkt bereit.

    Loggt eine Informationsmeldung für jede eingehende Anfrage und gibt
    eine statische JSON-Antwort zurück.
    """
    user_ip = "127.0.0.1"
    logging.info(f"Anfrage auf der Homepage von IP: {user_ip}")
    return {"message": "Willkommen auf der Homepage!"}


@app.get("/task")
async def process_task():
    """
    Simuliert die Verarbeitung einer Aufgabe, die fehlschlagen kann.

    Die Funktion hat eine 20%ige Wahrscheinlichkeit, einen Fehler zu simulieren
    und einen HTTP-Statuscode 500 auszulösen. Bei Erfolg wird eine
    Erfolgsmeldung zurückgegeben.

    Raises:
        HTTPException: Wenn die Aufgabe mit einer 20%-Wahrscheinlichkeit fehlschlägt.
    """
    task_id = random.randint(1000, 9999)
    logging.info(f"Starte Verarbeitung von Task #{task_id}...")

    if random.random() < 0.2:
        logging.error(
            f"Fehler bei der Verarbeitung von Task #{task_id}! Daten konnten nicht gelesen werden."
        )
        raise HTTPException(status_code=500, detail=f"Fehler bei Task #{task_id}")

    logging.info(f"Task #{task_id} erfolgreich abgeschlossen.")
    return {"message": f"Task #{task_id} erledigt!"}
