import sqlite3
import json


conn = sqlite3.connect(
    "observability.db",
    check_same_thread=False,
)

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS traces (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    trace_id TEXT,
    span_id TEXT,
    parent_span_id TEXT,

    event_type TEXT,
    name TEXT,

    start_ts REAL,
    end_ts REAL,

    latency_seconds REAL,

    success INTEGER,

    input_payload TEXT,
    output_payload TEXT,

    error TEXT,

    tokens INTEGER,

    metadata TEXT
)
""")

conn.commit()


def store_event(event):

    cursor.execute("""
    INSERT INTO traces (

        trace_id,
        span_id,
        parent_span_id,

        event_type,
        name,

        start_ts,
        end_ts,

        latency_seconds,

        success,

        input_payload,
        output_payload,

        error,

        tokens,

        metadata

    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        event["trace_id"],
        event["span_id"],
        event["parent_span_id"],

        event["event_type"],
        event["name"],

        event["start_ts"],
        event["end_ts"],

        event["latency_seconds"],

        int(event["success"]),

        json.dumps(event.get("input")),
        json.dumps(event.get("output")),

        event.get("error"),

        event.get("tokens", 0),

        json.dumps(event.get("metadata", {}))
    ))

    conn.commit()