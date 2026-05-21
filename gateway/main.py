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

    start_iso: Optional[str] = None
    end_iso: Optional[str] = None


# =========================================================
# INGESTION ENDPOINT
# =========================================================

@app.post("/events")
async def ingest_events(
    events: List[TraceEventModel]
):

    stored = 0

    for event in events:

        try:

            store_event(event.dict())

            stored += 1

        except Exception as exc:

            print(
                f"[GATEWAY ERROR] "
                f"Failed storing event: {exc}"
            )

    return {
        "status": "ok",
        "received": len(events),
        "stored": stored,
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }