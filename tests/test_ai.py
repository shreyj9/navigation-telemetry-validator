import pytest
from fastapi import HTTPException

from app import main
from app.schemas import IncidentAnalysisRequest


def test_ai_incident_analysis_success(monkeypatch):
    expected = (
        "Severity: High. Likely database connectivity degradation "
        "causing ingestion latency and malformed telemetry."
    )

    def fake_analyze_incident(log_text: str) -> str:
        assert "latency" in log_text.lower()
        return expected

    monkeypatch.setattr(main, "analyze_incident", fake_analyze_incident)

    request = IncidentAnalysisRequest(
        log_text="Navigation ingestion latency increased and database timeouts appeared."
    )

    response = main.ai_analyze_incident(request)

    assert response.analysis == expected


def test_ai_incident_analysis_failure_returns_503(monkeypatch):
    def fake_analyze_incident(log_text: str) -> str:
        raise RuntimeError("simulated provider failure")

    monkeypatch.setattr(main, "analyze_incident", fake_analyze_incident)

    request = IncidentAnalysisRequest(
        log_text="Navigation telemetry incident."
    )

    with pytest.raises(HTTPException) as exc_info:
        main.ai_analyze_incident(request)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == (
        "AI incident analysis is temporarily unavailable"
    )