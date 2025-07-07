import logging
import random
import time

from fastapi import FastAPI, HTTPException
from fastapi import Request
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

# Konfiguriert das grundlegende Logging-Format für die Anwendung.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_NAME = "python-app"


def setup_instrumentation(app_to_instrument: FastAPI):
    """
    Konfiguriert und initialisiert OpenTelemetry für Tracing und Logging.
    Die automatische Instrumentierung erfasst Telemetriedaten an den
    Grenzen der Systeme aus, z. B. eingehende und ausgehende HTTP-Anfragen,
    aber sie erfasst nicht, was in der Anwendung vor sich geht.
    Hierfür müssen wir eine manuelle Instrumentierung schreiben.

    """

    # 1. Ressource definieren: Beschreibt unsere Anwendung.
    resource = Resource(attributes={"service.name": SERVICE_NAME})

    # 2. Tracer Provider einrichten: Verwaltet die Erstellung von Traces.
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # 3. Meter Provider für Metriken einrichten

    # Die Python-App exportiert die manuell erstellten Metriken nicht.
    # Die Umgebungsvariablen (OTEL_METRICS_EXPORTER=otlp) in der docker-compose.yaml
    # konfigurieren nur die Auto-Instrumentierung. Da wir einen eigenen MeterProvider
    # erstellsen, müssen wir ihm explizit einen Exporter zuweisen.

    # Prometheus ist nicht dafür konfiguriert, Daten per remote_write zu empfangen.
    # Alloy versucht, die Metriken an Prometheus zu pushen, aber Prometheus lauscht
    # standardmäßig nicht auf diesem Weg.

    # Erstellt einen Reader, der Metriken alle 15 Sekunden exportiert.
    # Der Exporter sendet die Daten an den OTLP-Endpunkt, der per Umgebungsvariable
    # (OTEL_EXPORTER_OTLP_ENDPOINT) konfiguriert ist.
    reader = PeriodicExportingMetricReader(OTLPMetricExporter())

    # Der MeterProvider wird mit dem konfigurierten Reader initialisiert.
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)

    # 4. FastAPI-Instrumentierung: Hakt sich in FastAPI ein.
    # Erstellt automatisch Spans für jeden eingehenden Request.
    FastAPIInstrumentor.instrument_app(app_to_instrument)


app = FastAPI()

setup_instrumentation(app)

# 5. Manuelle Metrik-Instrumente erstellen
meter = metrics.get_meter("fastapi.app.manual.meter")

tasks_processed_counter = meter.create_counter(
    name="tasks_processed_total",
    description="Zählt die Gesamtzahl der verarbeiteten Tasks",
    unit="1",
)

task_duration_histogram = meter.create_histogram(
    name="task_processing_duration_seconds",
    description="Dauer der Verarbeitung eines Tasks in Sekunden",
    unit="s",
)


@app.get("/")
async def home(request: Request):
    """
    Stellt einen einfachen Willkommens-Endpunkt bereit.

    Loggt eine Informationsmeldung für jede eingehende Anfrage und gibt
    eine statische JSON-Antwort zurück.
    """
    user_ip = request.client.host
    logger.info(f"Anfrage auf der Homepage von IP: {user_ip}")
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
    logger.info(f"Starte Verarbeitung von Task #{task_id}...")

    start_time = time.time()

    try:
        if random.random() < 0.2:
            raise ValueError("Daten konnten nicht gelesen werden.")

        # Erfolgreicher Fall
        logger.info(f"Task #{task_id} erfolgreich abgeschlossen.")
        tasks_processed_counter.add(1, {"success": "true"})
        return {"message": f"Task #{task_id} erledigt!"}

    except ValueError as e:
        # Fehlerfall
        logger.error(f"Fehler bei der Verarbeitung von Task #{task_id}! Grund: {e}")
        tasks_processed_counter.add(1, {"success": "false"})
        raise HTTPException(status_code=500, detail=f"Fehler bei Task #{task_id}")

    finally:
        # Dauer messen und aufzeichnen, egal ob Erfolg oder Fehler
        duration = time.time() - start_time
        task_duration_histogram.record(duration)
