from app.schemas import TelemetryIn
from app.service import validate_event

def make_event(**overrides):
    data = dict(
        vehicle_id="vehicle-1",
        route_id="route-1",
        event_type="route_update",
        predicted_eta_sec=1200,
        actual_eta_sec=1250,
        latency_ms=20,
        rerouted=False,
        completed=True,
    )
    data.update(overrides)
    return TelemetryIn(**data)

def test_valid_event():
    assert validate_event(make_event()) is True

def test_rejects_unknown_event_type():
    assert validate_event(make_event(event_type="bad_type")) is False

def test_rejects_negative_eta():
    assert validate_event(make_event(predicted_eta_sec=-1)) is False

def test_rejects_negative_latency():
    assert validate_event(make_event(latency_ms=-1)) is False
