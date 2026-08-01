"""
backend/api/routes/sensors.py

API endpoints for the predictive maintenance sensor pipeline.
Receives sensor data, runs all 4 models, creates TriageFlow tickets
automatically when anomalies are detected.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models import Ticket

router = APIRouter(prefix="/sensors", tags=["sensors"])

# Pipeline loaded once at module level — expensive, don't reload per request
_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        try:
            from predictive.pipeline import TriageFlowPipeline
            _pipeline = TriageFlowPipeline(verbose=False)
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Predictive pipeline not available: {str(e)}"
            )
    return _pipeline


# ── Request / Response schemas ────────────────────────────────

class SensorReadingRequest(BaseModel):
    equipment_id: str
    signal: List[float]          # raw vibration samples
    sampling_rate: int = 20480   # Hz


class SensorPredictionResponse(BaseModel):
    equipment_id: str
    is_anomaly: bool
    anomaly_probability: float
    fault_type: str
    fault_confidence: float
    severity: str
    rms: float
    kurtosis: float
    peak_to_peak: float
    ticket_id: Optional[str] = None
    ticket_created: bool = False
    timestamp: str


class BulkSensorRequest(BaseModel):
    readings: List[SensorReadingRequest]


# ── Endpoints ─────────────────────────────────────────────────

@router.post("/analyze", response_model=SensorPredictionResponse)
def analyze_sensor_reading(
    request: SensorReadingRequest,
    db: Session = Depends(get_db),
):
    """
    Analyze a single sensor reading through all 4 ML models.
    If an anomaly is detected, automatically create a TriageFlow ticket.
    """
    import numpy as np
    from backend.graphs.triage_graph import get_triage_graph
    from backend.graphs.state import create_initial_state

    pipeline = get_pipeline()
    signal   = np.array(request.signal, dtype=np.float32)

    result = pipeline.predict(
        signal=signal,
        equipment_id=request.equipment_id,
        sampling_rate=request.sampling_rate,
    )

    ticket_id      = None
    ticket_created = False

    # Auto-create ticket only if anomaly detected
    if result.is_anomaly:
        ticket_text = pipeline.generate_ticket_text(result)

        try:
            graph        = get_triage_graph()
            state        = create_initial_state(ticket_text)
            ticket_id    = state["ticket_id"]
            thread_id    = f"ticket-{ticket_id}"
            config       = {"configurable": {"thread_id": thread_id}}

            graph.invoke(state, config=config)

            # Save to database
            db_ticket = Ticket(
                ticket_id=ticket_id,
                raw_text=ticket_text,
                status="awaiting_review",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(db_ticket)
            db.commit()
            ticket_created = True

        except Exception as e:
            # Don't fail the sensor analysis if ticket creation fails
            print(f"Ticket creation failed: {e}")

    return SensorPredictionResponse(
        equipment_id=result.equipment_id,
        is_anomaly=result.is_anomaly,
        anomaly_probability=result.anomaly_probability,
        fault_type=result.fault_type,
        fault_confidence=result.fault_confidence,
        severity=result.severity,
        rms=result.rms,
        kurtosis=result.kurtosis,
        peak_to_peak=result.peak_to_peak,
        ticket_id=ticket_id,
        ticket_created=ticket_created,
        timestamp=result.timestamp,
    )


@router.get("/status")
def sensor_pipeline_status():
    """Check whether the predictive pipeline models are loaded."""
    try:
        pipeline = get_pipeline()
        return {
            "status": "ready",
            "device": str(pipeline.device),
            "anomaly_threshold": pipeline.anomaly_threshold,
            "models_dir": str(pipeline.models_dir),
        }
    except Exception as e:
        return {
            "status": "unavailable",
            "error": str(e),
        }


@router.post("/simulate")
def simulate_sensor_stream(
    equipment_id: str = "P-204",
    n_samples: int = 10,
    include_faults: bool = True,
    db: Session = Depends(get_db),
):
    """
    Simulate a stream of sensor readings for testing.
    Generates synthetic healthy + faulty signals and runs them
    through the full pipeline.

    Use this to test the integration without real sensor hardware.
    """
    import numpy as np

    results   = []
    pipeline  = get_pipeline()

    for i in range(n_samples):
        # Alternate between healthy and faulty if include_faults=True
        if include_faults and i % 3 == 2:
            # Faulty: impulsive signal
            t      = np.linspace(0, 1, 20480)
            signal = (
                np.random.randn(20480) * 0.05 +
                0.4 * np.sin(2 * np.pi * 120 * t) +
                np.array([
                    1.5 if j % 170 == 0 else 0
                    for j in range(20480)
                ], dtype=np.float32)
            ).astype(np.float32)
        else:
            # Healthy: low-amplitude noise
            signal = np.random.randn(20480).astype(np.float32) * 0.05

        result = pipeline.predict(
            signal=signal,
            equipment_id=equipment_id,
        )

        ticket_id = None
        if result.is_anomaly:
            ticket_text = pipeline.generate_ticket_text(result)
            try:
                from backend.graphs.triage_graph import get_triage_graph
                from backend.graphs.state import create_initial_state

                graph     = get_triage_graph()
                state     = create_initial_state(ticket_text)
                ticket_id = state["ticket_id"]
                config    = {"configurable": {"thread_id": f"ticket-{ticket_id}"}}
                graph.invoke(state, config=config)

                db.add(Ticket(
                    ticket_id=ticket_id,
                    raw_text=ticket_text,
                    status="awaiting_review",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                ))
                db.commit()
            except Exception as e:
                print(f"Ticket creation error: {e}")

        results.append({
            "sample_index":       i,
            "is_anomaly":         result.is_anomaly,
            "anomaly_probability": result.anomaly_probability,
            "fault_type":         result.fault_type,
            "severity":           result.severity,
            "rms":                result.rms,
            "ticket_id":          ticket_id,
        })

    return {
        "equipment_id":   equipment_id,
        "samples_run":    n_samples,
        "anomalies_found": sum(1 for r in results if r["is_anomaly"]),
        "tickets_created": sum(1 for r in results if r["ticket_id"]),
        "results":         results,
    }