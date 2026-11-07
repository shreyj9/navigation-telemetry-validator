import json
import logging
import time
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from .db import Base, SessionLocal, engine
from .schemas import (
    IncidentAnalysisRequest,
    IncidentAnalysisResponse,
    IngestResult,
    TelemetryIn,
)
from .ai_service import analyze_incident
from .service import persist_batch, summary_metrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("navigation-validator")

app = FastAPI(title="Navigation Telemetry Validator", version="1.0.0")

@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("database_ready")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/events/batch", response_model=IngestResult)
def ingest_batch(events: list[TelemetryIn], db: Session = Depends(get_db)):
    started = time.perf_counter()
    accepted, rejected = persist_batch(db, events)
    elapsed_ms = (time.perf_counter() - started) * 1000

    logger.info(json.dumps({
        "event": "batch_ingested",
        "batch_size": len(events),
        "accepted": accepted,
        "rejected": rejected,
        "elapsed_ms": round(elapsed_ms, 2),
    }))
    return IngestResult(accepted=accepted, rejected=rejected)

@app.get("/metrics/summary")
def metrics_summary(db: Session = Depends(get_db)):
    return summary_metrics(db)


@app.post("/ai/analyze-incident", response_model=IncidentAnalysisResponse)
def ai_analyze_incident(request: IncidentAnalysisRequest):
    started = time.perf_counter()

    try:
        analysis = analyze_incident(request.log_text)
        elapsed_ms = (time.perf_counter() - started) * 1000

        logger.info(json.dumps({
            "event": "ai_incident_analysis",
            "success": True,
            "elapsed_ms": round(elapsed_ms, 2),
        }))

        return IncidentAnalysisResponse(analysis=analysis)

    except Exception:
        elapsed_ms = (time.perf_counter() - started) * 1000

        logger.exception(json.dumps({
            "event": "ai_incident_analysis",
            "success": False,
            "elapsed_ms": round(elapsed_ms, 2),
        }))

        raise HTTPException(
            status_code=503,
            detail="AI incident analysis is temporarily unavailable",
        )
