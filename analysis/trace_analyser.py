# analysis/trace_analyzer.py

import sqlite3
import requests
import json
import time
from pathlib import Path


# =========================================================
# CONFIG
# =========================================================

SOURCE_DB = "../observability.db"

REPORT_DB = "analysis_reports.db"

OLLAMA_URL = "http://localhost:11434/api/chat"

MODEL = "qwen2.5:3b"


# =========================================================
# REPORT DATABASE
# =========================================================

report_conn = sqlite3.connect(REPORT_DB)

report_cursor = report_conn.cursor()

report_cursor.execute("""
CREATE TABLE IF NOT EXISTS analysis_reports (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    trace_id TEXT,

    generated_at REAL,

    model TEXT,

    workflow_name TEXT,

    total_latency REAL,

    total_spans INTEGER,

    llm_calls INTEGER,

    failures INTEGER,

    bottleneck_operation TEXT,

    bottleneck_latency REAL,

    summary TEXT,

    recommendations TEXT
)
""")

report_conn.commit()


# =========================================================
# LOAD TRACE DATA
# =========================================================

source_conn = sqlite3.connect(SOURCE_DB)

source_conn.row_factory = sqlite3.Row

source_cursor = source_conn.cursor()


def get_all_trace_ids():

    rows = source_cursor.execute("""
    SELECT DISTINCT trace_id
    FROM traces
    WHERE trace_id IS NOT NULL
    """).fetchall()

    return [row["trace_id"] for row in rows]


def load_trace(trace_id):

    rows = source_cursor.execute("""
    SELECT *
    FROM traces
    WHERE trace_id = ?
    ORDER BY start_ts
    """, (trace_id,)).fetchall()

    return [dict(row) for row in rows]


# =========================================================
# TRACE SUMMARY
# =========================================================

def build_trace_summary(spans):

    workflow_name = "unknown"

    total_latency = 0

    llm_calls = 0

    failures = 0

    bottleneck = None

    bottleneck_latency = -1

    summary_lines = []

    for span in spans:

        if span["event_type"] == "workflow":
            workflow_name = span["name"]
            total_latency = span["latency_seconds"]

        if span["event_type"] == "llm_call":
            llm_calls += 1

        if span["success"] == 0:
            failures += 1

        latency = span["latency_seconds"]

        if latency > bottleneck_latency:
            bottleneck_latency = latency
            bottleneck = span["name"]

        summary_lines.append(
            f"""
Event Type: {span['event_type']}
Name: {span['name']}
Latency: {span['latency_seconds']}s
Success: {span['success']}
"""
        )

    trace_text = "\n".join(summary_lines)

    return {
        "workflow_name": workflow_name,
        "total_latency": total_latency,
        "llm_calls": llm_calls,
        "failures": failures,
        "bottleneck": bottleneck,
        "bottleneck_latency": bottleneck_latency,
        "trace_text": trace_text,
        "total_spans": len(spans),
    }


# =========================================================
# PROMPT
# =========================================================

def build_prompt(summary):

    return f"""
    You are an expert AI observability engineer and distributed systems analyst.

    You are analyzing the execution trace of an AI agent workflow instrumented using a custom tracing system.

    The trace contains spans representing:
    - workflow execution
    - prompt construction
    - LLM inference
    - parsing stages
    - internal runtime operations

    Your task is to deeply analyze this specific workflow execution and produce a professional observability report.

    =========================================================
    WORKFLOW INFORMATION
    =========================================================

    Agent / Workflow Name:
    {summary['workflow_name']}

    Total Workflow Latency:
    {summary['total_latency']} seconds

    Total Number of Spans:
    {summary['total_spans']}

    Total LLM Calls:
    {summary['llm_calls']}

    Failure Count:
    {summary['failures']}

    Most Expensive Operation:
    {summary['bottleneck']}

    Bottleneck Latency:
    {summary['bottleneck_latency']} seconds

    =========================================================
    TRACE EXECUTION DATA
    =========================================================

    {summary['trace_text']}

    =========================================================
    ANALYSIS OBJECTIVES
    =========================================================

    Analyze this trace as if you are debugging and optimizing a production AI agent system.

    Focus specifically on:

    1. Workflow Behavior
    - What type of workflow is this?
    - What sequence of operations occurred?
    - How did the workflow progress?

    2. Latency Analysis
    - Which spans dominate execution time?
    - Is latency concentrated in:
    - LLM inference?
    - prompt building?
    - parsing?
    - external calls?
    - Are there suspicious latency spikes?

    3. Failure Analysis
    - Did any spans fail?
    - What likely caused the failures?
    - Were failures propagated through child spans?

    4. Bottleneck Detection
    - Identify the primary bottleneck.
    - Explain WHY it became the bottleneck.
    - Estimate how much impact it had on total workflow latency.

    5. Efficiency Analysis
    - Was the workflow efficient?
    - Were there redundant operations?
    - Was the prompt likely too large?
    - Was the model potentially overloaded?
    - Were there too many sequential steps?

    6. Optimization Recommendations
    Provide concrete engineering recommendations such as:
    - caching
    - batching
    - prompt compression
    - model switching
    - chunking
    - parallelization
    - timeout tuning
    - retry policies
    - reducing context size

    7. Overall Assessment
    Give an overall assessment of:
    - system health
    - workflow quality
    - observability quality
    - runtime efficiency

    =========================================================
    IMPORTANT RULES
    =========================================================

    - Be highly technical and specific.
    - Infer likely workflow behavior from the traces.
    - Reference actual span names and operations.
    - Explain reasoning clearly.
    - Avoid generic statements.
    - Treat this as a real production observability analysis.
    - Mention the specific agent/workflow name repeatedly in the analysis.
    - If this appears to be an EmailClassifier workflow, discuss classification inference patterns.
    - If this appears to be a PDFExtractor workflow, discuss document extraction and summarization bottlenecks.
    - Use the trace structure and span hierarchy to infer execution flow.

    =========================================================
    OUTPUT FORMAT
    =========================================================

    SUMMARY:
    (technical workflow summary)

    BOTTLENECK ANALYSIS:
    (primary bottlenecks and latency breakdown)

    FAILURE ANALYSIS:
    (errors and propagation analysis)

    OPTIMIZATION RECOMMENDATIONS:
    (concrete improvements)

    OVERALL ASSESSMENT:
    (final evaluation of workflow health and efficiency)
"""

# =========================================================
# OLLAMA CALL
# =========================================================

def query_ollama(prompt):

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=300,
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]


# =========================================================
# PARSE RESPONSE
# =========================================================

def parse_analysis(text):

    summary = text

    recommendations = ""

    if "RECOMMENDATIONS:" in text:

        parts = text.split("RECOMMENDATIONS:")

        summary = parts[0].replace(
            "SUMMARY:",
            ""
        ).strip()

        recommendations = parts[1].strip()

    return summary, recommendations


# =========================================================
# STORE REPORT
# =========================================================

def store_report(
    trace_id,
    summary_data,
    summary,
    recommendations,
):

    report_cursor.execute("""
    INSERT INTO analysis_reports (

        trace_id,

        generated_at,

        model,

        workflow_name,

        total_latency,

        total_spans,

        llm_calls,

        failures,

        bottleneck_operation,

        bottleneck_latency,

        summary,

        recommendations

    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        trace_id,

        time.time(),

        MODEL,

        summary_data["workflow_name"],

        summary_data["total_latency"],

        summary_data["total_spans"],

        summary_data["llm_calls"],

        summary_data["failures"],

        summary_data["bottleneck"],

        summary_data["bottleneck_latency"],

        summary,

        recommendations
    ))

    report_conn.commit()


# =========================================================
# MAIN ANALYSIS
# =========================================================

def analyze_trace(trace_id):

    print(f"\nAnalyzing Trace: {trace_id}")

    spans = load_trace(trace_id)

    if not spans:
        print("No spans found")
        return

    summary_data = build_trace_summary(spans)

    prompt = build_prompt(summary_data)

    response = query_ollama(prompt)

    summary, recommendations = parse_analysis(response)

    store_report(
        trace_id,
        summary_data,
        summary,
        recommendations,
    )

    print("\nAnalysis Complete")

    print("\nSUMMARY:\n")

    print(summary)

    print("\nRECOMMENDATIONS:\n")

    print(recommendations)


# =========================================================
# RUN ALL
# =========================================================

def main():

    trace_ids = get_all_trace_ids()

    print(f"\nFound {len(trace_ids)} traces")

    for trace_id in trace_ids:

        try:
            analyze_trace(trace_id)

        except Exception as exc:

            print(
                f"\nFailed analyzing "
                f"{trace_id}: {exc}"
            )


if __name__ == "__main__":

    main()