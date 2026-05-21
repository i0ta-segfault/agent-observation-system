import sqlite3
import json


# =========================================================
# SQLITE CONNECTION
# =========================================================

conn = sqlite3.connect(
    "observability.db",
    check_same_thread=False,
)

cursor = conn.cursor()


# =========================================================
# TRACE TABLE
# =========================================================

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

    metadata TEXT,

    start_iso TEXT,
    end_iso TEXT
)
""")

conn.commit()


# =========================================================
# SAFE JSON SERIALIZATION
# =========================================================

def safe_json(data):

    try:

        return json.dumps(
            data,
            default=str,
        )

    except Exception:

        return json.dumps(
            str(data)
        )


# =========================================================
# STORE EVENT
# =========================================================

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

        metadata,

        start_iso,
        end_iso

    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        event["trace_id"],

        event["span_id"],

        event.get("parent_span_id"),

        event["event_type"],

        event["name"],

        event["start_ts"],

        event["end_ts"],

        event["latency_seconds"],

        int(event["success"]),

        safe_json(event.get("input")),

        safe_json(event.get("output")),

        event.get("error"),

        event.get("tokens", 0),

        safe_json(
            event.get("metadata", {})
        ),

        event.get("start_iso"),

        event.get("end_iso"),
    ))

    conn.commit()

    print(
        f"[STORAGE] "
        f"{event['event_type']} | "
        f"{event['name']} | "
        f"tokens={event.get('tokens', 0)}"
    )