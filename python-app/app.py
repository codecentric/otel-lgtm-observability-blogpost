import logging
import random

from fastapi import FastAPI, HTTPException


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()


@app.get("/")
async def home():
    user_ip = "127.0.0.1"  # Simulierter Wert
    logging.info(f"Anfrage auf der Homepage von IP: {user_ip}")
    return {"message": "Willkommen auf der Homepage!"}


@app.get("/task")
async def process_task():
    task_id = random.randint(1000, 9999)
    logging.info(f"Starte Verarbeitung von Task #{task_id}...")

    if random.random() < 0.2:  # 20% Fehlerwahrscheinlichkeit
        logging.error(
            f"Fehler bei der Verarbeitung von Task #{task_id}! Daten konnten nicht gelesen werden."
        )
        # HTTPException ist der idiomatische Weg in FastAPI, um Fehler mit Statuscodes zu handhaben.
        raise HTTPException(status_code=500, detail=f"Fehler bei Task #{task_id}")

    logging.info(f"Task #{task_id} erfolgreich abgeschlossen.")
    return {"message": f"Task #{task_id} erledigt!"}
