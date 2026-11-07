from pydantic import BaseModel, Field

class TelemetryIn(BaseModel):
    vehicle_id: str = Field(min_length=1, max_length=64)
    route_id: str = Field(min_length=1, max_length=64)
    event_type: str
    predicted_eta_sec: float
    actual_eta_sec: float
    latency_ms: float
    rerouted: bool = False
    completed: bool = True

class IngestResult(BaseModel):
    accepted: int
    rejected: int

class IncidentAnalysisRequest(BaseModel):
    log_text: str = Field(min_length=1, max_length=5000)


class IncidentAnalysisResponse(BaseModel):
    analysis: str