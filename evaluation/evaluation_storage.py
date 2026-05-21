import sqlite3
import time


conn = sqlite3.connect(
    "evaluation_results.db",
    check_same_thread=False,
)

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS evaluations (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    trace_id TEXT,

    workflow_name TEXT,

    input_text TEXT,

    expected_output TEXT,

    actual_output TEXT,

    correct INTEGER,

    latency REAL,

    tokens INTEGER,

    evaluated_at REAL
)
""")

conn.commit()


def store_evaluation(result):

    cursor.execute("""
    INSERT INTO evaluations (

        trace_id,

        workflow_name,

        input_text,

        expected_output,

        actual_output,

        correct,

        latency,

        tokens,

        evaluated_at

    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        result["trace_id"],

        result["workflow_name"],

        result["input_text"],

        result["expected_output"],

        result["actual_output"],

        int(result["correct"]),

        result["latency"],

        result["tokens"],

        time.time(),
    ))

    conn.commit()