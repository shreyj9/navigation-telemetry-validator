from statistics import quantiles
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import TelemetryEvent
from .schemas import TelemetryIn

VALID_TYPES = {"route_start", "route_update", "reroute", "route_complete"}

def validate_event(event: TelemetryIn) -> bool:
    if event.event_type not in VALID_TYPES:
        return False
    if event.predicted_eta_sec <= 0 or event.actual_eta_sec <= 0:
        return False
    if event.latency_ms < 0:
        return False
    return True

def persist_batch(db: Session, events: list[TelemetryIn]) -> tuple[int, int]:
    accepted = 0
    rejected = 0

    for event in events:
        valid = validate_event(event)
        db.add(TelemetryEvent(
            vehicle_id=event.vehicle_id,
            route_id=event.route_id,
            event_type=event.event_type,
            predicted_eta_sec=event.predicted_eta_sec,
            actual_eta_sec=event.actual_eta_sec,
            latency_ms=event.latency_ms,
            rerouted=event.rerouted,
            completed=event.completed,
            malformed=not valid,
        ))
        accepted += int(valid)
        rejected += int(not valid)

    db.commit()
    return accepted, rejected

def summary_metrics(db: Session) -> dict:
    rows = db.scalars(select(TelemetryEvent)).all()
    total = len(rows)

    if total == 0:
        return {
            "total_events": 0,
            "route_completion_rate": 0.0,
            "reroute_rate": 0.0,
            "malformed_rate": 0.0,
            "average_eta_error_sec": 0.0,
            "p95_ingestion_latency_ms": 0.0,
        }

    completion = sum(r.completed for r in rows) / total
    reroute = sum(r.rerouted for r in rows) / total
    malformed = sum(r.malformed for r in rows) / total
    eta_error = sum(abs(r.actual_eta_sec - r.predicted_eta_sec) for r in rows) / total
    latencies = sorted(r.latency_ms for r in rows if r.latency_ms >= 0)

    if len(latencies) >= 20:
        p95 = quantiles(latencies, n=100, method="inclusive")[94]
    elif latencies:
        p95 = latencies[-1]
    else:
        p95 = 0.0

    return {
        "total_events": total,
        "route_completion_rate": round(completion, 4),
        "reroute_rate": round(reroute, 4),
        "malformed_rate": round(malformed, 4),
        "average_eta_error_sec": round(eta_error, 2),
        "p95_ingestion_latency_ms": round(p95, 2),
    }
