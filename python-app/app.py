import logging
import random

from fastapi import FastAPI, HTTPException
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider, get_logger
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

SERVICE_NAME = "python-app"


def setup_telemetry(app_to_instrument: FastAPI):
    """Konfiguriert und initialisiert OpenTelemetry für Tracing und Logging."""

    # 1. Ressource definieren: Beschreibt unsere Anwendung.
    resource = Resource(attributes={"service.name": SERVICE_NAME})

    # 2. Tracer Provider einrichten: Verwaltet die Erstellung von Traces.
    tracer_provider = TracerProvider(resource=resource)

    # 3. Exporter konfigurieren: Sendet die Traces via OTLP gRPC an den Collector (Alloy).
    # Die Adresse wird über die Umgebungsvariable OTEL_EXPORTER_OTLP_ENDPOINT gesteuert.
    otlp_exporter = OTLPSpanExporter()
    # otlp_exporter = ConsoleSpanExporter() # wenn ich lokal die traces sehen will

    processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(processor)

    trace.set_tracer_provider(tracer_provider)


    # # 4. Logging Provider einrichten: Verwaltet die Erstellung von Traces.
    # provider = LoggerProvider()
    # processor = BatchLogRecordProcessor(
    #     OTLPLogExporter()
    # )  # console wenn ich in std out sehen will
    #
    # provider.add_log_record_processor(processor)
    # # Sets the global default logger provider
    # set_logger_provider(provider)
    #
    # handler = LoggingHandler(level=logging.INFO, logger_provider=provider)
    # logging.basicConfig(handlers=[handler], level=logging.INFO)
    #
    # # 5. Logging-Instrumentierung: Verknüpft Logs automatisch mit Traces.
    # # Fügt jedem Log-Eintrag, der während eines aktiven Traces erstellt wird,
    # # automatisch trace_id und span_id hinzu.
    # LoggingInstrumentor().instrument(
    #     set_logging_format=True, tracer_provider=tracer_provider
    # )

    # 6. FastAPI-Instrumentierung: Hakt sich in FastAPI ein.
    # Erstellt automatisch Spans für jeden eingehenden Request.
    FastAPIInstrumentor.instrument_app(app_to_instrument)


app = FastAPI()

setup_telemetry(app)


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
