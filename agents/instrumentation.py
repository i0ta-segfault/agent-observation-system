# =========================================================
# instrumentation.py
# =========================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from queue import Queue, Empty
from threading import Thread, Event
from contextlib import contextmanager

import uuid
import time
import requests


# =========================================================
# TRACE EVENT
# =========================================================

@dataclass
class TraceEvent:

    trace_id: str
    span_id: str
    parent_span_id: Optional[str]

    event_type: str
    name: str

    start_ts: float
    end_ts: float

    latency_seconds: float

    success: bool

    input_payload: Any = None
    output_payload: Any = None

    error: Optional[str] = None

    tokens: int = 0

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):

        return {

            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,

            "event_type": self.event_type,
            "name": self.name,

            "start_ts": self.start_ts,
            "end_ts": self.end_ts,

            "start_iso": datetime.fromtimestamp(
                self.start_ts,
                tz=timezone.utc
            ).isoformat(),

            "end_iso": datetime.fromtimestamp(
                self.end_ts,
                tz=timezone.utc
            ).isoformat(),

            "latency_seconds": self.latency_seconds,

            "success": self.success,

            "input": self.input_payload,
            "output": self.output_payload,

            "error": self.error,

            "tokens": self.tokens,

            "metadata": self.metadata,
        }


# =========================================================
# EXPORTERS
# =========================================================

class BaseExporter:

    def export(self, events: List[TraceEvent]):
        raise NotImplementedError


class ConsoleExporter(BaseExporter):

    def export(self, events: List[TraceEvent]):

        for event in events:

            print(
                f"[TRACE] "
                f"{event.event_type} | "
                f"{event.name} | "
                f"{event.latency_seconds:.2f}s | "
                f"tokens={event.tokens} | "
                f"success={event.success}"
            )


class HTTPExporter(BaseExporter):

    def __init__(self, endpoint: str):

        self.endpoint = endpoint

    def export(self, events: List[TraceEvent]):

        payload = [
            event.to_dict()
            for event in events
        ]

        requests.post(
            self.endpoint,
            json=payload,
            timeout=5,
        )


# =========================================================
# BACKGROUND WORKER
# =========================================================

class ExportWorker:

    def __init__(
        self,
        queue: Queue,
        exporter: BaseExporter,
        batch_size: int = 10,
        flush_interval: int = 5,
    ):

        self.queue = queue

        self.exporter = exporter

        self.batch_size = batch_size
        self.flush_interval = flush_interval

        self.stop_event = Event()

        self.thread = Thread(
            target=self.run,
            daemon=True,
        )

    def start(self):

        self.thread.start()

    def stop(self):

        self.stop_event.set()

    def run(self):

        batch = []

        last_flush = time.time()

        while (
            not self.stop_event.is_set()
            or not self.queue.empty()
        ):

            try:

                event = self.queue.get(timeout=1)

                batch.append(event)

            except Empty:
                pass

            now = time.time()

            should_flush = (

                len(batch) >= self.batch_size

                or (

                    batch
                    and now - last_flush >= self.flush_interval
                )
            )

            if should_flush:

                try:

                    print(
                        f"[EXPORT DEBUG] "
                        f"FLUSHING {len(batch)} EVENTS"
                    )

                    self.exporter.export(batch)

                    print(
                        f"[EXPORT DEBUG] "
                        f"EXPORT SUCCESS"
                    )

                except Exception as exc:

                    print(
                        f"[EXPORT ERROR] {exc}"
                    )

                batch.clear()

                last_flush = now

        # =====================================================
        # FINAL FLUSH
        # =====================================================

        if batch:

            try:

                print(
                    f"[EXPORT DEBUG] "
                    f"FINAL FLUSH OF "
                    f"{len(batch)} EVENTS"
                )

                self.exporter.export(batch)

                print(
                    f"[EXPORT DEBUG] "
                    f"FINAL EXPORT SUCCESS"
                )

            except Exception as exc:

                print(
                    f"[FINAL EXPORT ERROR] {exc}"
                )


# =========================================================
# TOKEN ESTIMATION
# =========================================================

def estimate_tokens(*parts: Any) -> int:

    combined = "".join(
        str(p)
        for p in parts
        if p is not None
    )

    return (
        max(1, len(combined) // 4)
        if combined else 0
    )


# =========================================================
# SAFE SERIALIZATION
# =========================================================

def safe_json(data: Any):

    try:

        if data is None:
            return None

        if isinstance(
            data,
            (str, int, float, bool, list, dict)
        ):
            return data

        return str(data)

    except Exception:

        return str(type(data))


# =========================================================
# TRACER
# =========================================================

class Tracer:

    def __init__(
        self,
        service_name: str,
        exporter: BaseExporter,
    ):

        self.service_name = service_name

        self.queue = Queue()

        self.worker = ExportWorker(
            queue=self.queue,
            exporter=exporter,
        )

        self.worker.start()

    @contextmanager
    def span(
        self,
        event_type: str,
        name: str,

        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,

        input_payload: Any = None,
        output_payload: Any = None,

        metadata: Optional[Dict[str, Any]] = None,
    ):

        trace_id = trace_id or str(uuid.uuid4())

        span_id = str(uuid.uuid4())

        start = time.time()

        span_data = {

            "trace_id": trace_id,
            "span_id": span_id,

            "tokens": 0,

            "metadata": metadata or {},

            "output_payload": output_payload,
        }

        try:

            yield span_data

            end = time.time()

            event = TraceEvent(

                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,

                event_type=event_type,
                name=name,

                start_ts=start,
                end_ts=end,

                latency_seconds=end - start,

                success=True,

                input_payload=safe_json(input_payload),

                output_payload=safe_json(
                    span_data.get("output_payload")
                ),

                tokens=span_data.get("tokens", 0),

                metadata=safe_json(
                    span_data.get("metadata", {})
                ),
            )

            self.queue.put(event)

        except Exception as exc:

            end = time.time()

            event = TraceEvent(

                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,

                event_type=event_type,
                name=name,

                start_ts=start,
                end_ts=end,

                latency_seconds=end - start,

                success=False,

                input_payload=safe_json(input_payload),

                output_payload=safe_json(
                    span_data.get("output_payload")
                ),

                error=str(exc),

                tokens=span_data.get("tokens", 0),

                metadata=safe_json(
                    span_data.get("metadata", {})
                ),
            )

            self.queue.put(event)

            raise

    def shutdown(self):

        self.worker.stop()

        self.worker.thread.join(timeout=5)


# =========================================================
# GLOBAL INSTRUMENTATION
# =========================================================

_GLOBAL_TRACER: Optional[Tracer] = None


def instrument(
    service_name: str,
    exporter: BaseExporter,
):

    global _GLOBAL_TRACER

    _GLOBAL_TRACER = Tracer(
        service_name=service_name,
        exporter=exporter,
    )


def get_tracer() -> Tracer:

    if _GLOBAL_TRACER is None:

        raise RuntimeError(
            "Tracer not initialized. "
            "Call instrument() first."
        )

    return _GLOBAL_TRACER


def shutdown_tracer():

    global _GLOBAL_TRACER

    if _GLOBAL_TRACER is not None:

        _GLOBAL_TRACER.shutdown()