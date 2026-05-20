from fastapi import FastAPI
from pydantic import BaseModel

from typing import Optional, Dict, Any, List

from .storage import store_event


app = FastAPI()


# =========================================================
# EVENT MODEL
# =========================================================

class TraceEventModel(BaseModel):

    trace_id: str
    span_id: str

    parent_span_id: Optional[str]

    event_type: str
    name: str

    start_ts: float
    end_ts: float

    latency_seconds: float

    success: bool

    input: Optional[Any] = None
    output: Optional[Any] = None

    error: Optional[str] = None

    tokens: int = 0

    metadata: Dict[str, Any] = {}


# =========================================================
# INGESTION ENDPOINT
# =========================================================

@app.post("/events")

async def ingest_events(
    events: List[TraceEventModel]
):

    for event in events:
        store_event(event.dict())

    return {
        "status": "ok",
        "received": len(events),
    }


@app.get("/health")

async def health():
    return {"status": "healthy"}