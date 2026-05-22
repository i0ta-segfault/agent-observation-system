# LLM Agent Observation System

An end-to-end observability, analysis, and evaluation system for LLM-powered agents using local models, tracing instrumentation, SQLite persistence, FastAPI, and Grafana dashboards.

---

# 📋 Project Overview

This project implements a lightweight observability stack inspired by OpenTelemetry concepts for agentic AI systems.

The system provides:

- Modular AI agents
- Runtime instrumentation
- Workflow tracing
- Nested spans
- Latency monitoring
- Token estimation
- Error tracking
- Persistent telemetry storage
- Grafana dashboard visualization
- AI-powered workflow analysis
- Offline evaluation pipelines
- LangGraph-compatible instrumentation wrappers

The goal is to monitor, analyze, and evaluate the internal execution flow of AI agents similarly to how observability platforms monitor distributed backend systems.

---

# 🏗️ Updated System Architecture

```text
                         ┌──────────────────────┐
                         │  User / Test Script  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                     ┌──────────────────────────┐
                     │ Instrumented Agent Layer │
                     └──────────┬───────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
   EmailAgent             PDFExtractor        LangGraph Nodes
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                │
                                ▼
                     ┌──────────────────────────┐
                     │   Ollama Local Models    │
                     │ (Qwen / Phi3 / Llama3)   │
                     └──────────┬───────────────┘
                                │
                                ▼
                     ┌──────────────────────────┐
                     │ Runtime Instrumentation  │
                     │   + Span Generation      │
                     └──────────┬───────────────┘
                                │
                                ▼
                     ┌──────────────────────────┐
                     │ FastAPI Telemetry Gateway│
                     └──────────┬───────────────┘
                                │
                                ▼
                     ┌──────────────────────────┐
                     │     observability.db     │
                     │  traces + spans storage  │
                     └──────────┬───────────────┘
                                │
               ┌────────────────┴────────────────┐
               │                                 │
               ▼                                 ▼
    analysis/trace_analyzer.py         evaluation/evaluate.py
               │                                 │
               ▼                                 ▼
      analysis_reports.db             evaluation_results.db
               │                                 │
               └────────────────┬────────────────┘
                                ▼
                     ┌──────────────────────────┐
                     │    Grafana Dashboards    │
                     └──────────────────────────┘
```

---

# 🔭 Observability Features

The system includes a lightweight observability stack inspired by OpenTelemetry.

## Features

- Workflow-level tracing
- Nested spans
- Span hierarchy
- Runtime latency tracking
- Token estimation
- Error monitoring
- Persistent telemetry storage
- Workflow DAG reconstruction
- AI-powered trace analysis
- Offline workflow evaluation
- Multi-model benchmarking

---

# 📡 Instrumented Span Types

The runtime automatically instruments:

- `workflow`
- `prompt_builder`
- `llm_call`
- `parser`

Each execution generates:

- `trace_id`
- `span_id`
- `parent_span_id`

allowing complete workflow reconstruction.

---

# 🧠 Implemented Agents

---

# 1. Email Classification Agent

Features:

- Email categorization
- Configurable categories
- Batch processing
- Runtime tracing
- Latency monitoring
- Token monitoring

Supported categories:

- invoice
- spam
- urgent
- general
- support
- marketing
- notification

---

# 2. PDF Extraction Agent

Features:

- PDF text extraction
- OCR support
- Multi-stage summarization
- Information extraction
- Chunk-based processing
- Runtime tracing
- Latency analysis

Processing modes:

- summarize
- extract_info
- classify
- custom analysis

---

# ⚙️ Runtime Architecture

The project uses composition and wrappers instead of inheritance-heavy design.

## Runtime Flow

```text
prompt_builder
      ↓
llm_call
      ↓
parser
```

with automatic tracing and instrumentation around every stage.

---

# 📦 Core Components

---

## `agents/runtime.py`

Generic runtime responsible for:

- workflow orchestration
- tracing spans
- handling errors
- latency tracking
- token estimation
- exporter integration

---

## `agents/instrumentation.py`

Provides:

- tracing
- spans
- exporters
- runtime wrappers
- token estimation
- telemetry exporting
- LangGraph-compatible instrumentation

---

## `gateway/main.py`

FastAPI telemetry ingestion gateway.

Receives:

```http
POST /events
```

and stores telemetry into SQLite.

---

## `gateway/storage.py`

SQLite persistence layer for traces and spans.

Stores:

- traces
- spans
- tokens
- latency
- metadata
- errors
- timestamps

---

## `analysis/trace_analyzer.py`

Offline AI-powered workflow analysis system.

Reads traces from:

```text
observability.db
```

Generates optimization reports into:

```text
analysis_reports.db
```

Capabilities:

- bottleneck analysis
- latency analysis
- optimization recommendations
- workflow summaries
- failure analysis

---

## `evaluation/evaluate.py`

Offline evaluation pipeline for Email Classification workflows.

Reads workflow traces from:

```text
observability.db
```

Compares against manually defined ground-truth datasets and stores results in:

```text
evaluation_results.db
```

Current evaluation support:

- EmailClassifier only

Metrics:

- classification accuracy
- latency
- token usage
- prediction correctness

---

# 📦 Installation

## Prerequisites

---

## 1. Install Ollama

Download:

```text
https://ollama.ai/download
```

Pull a model:

```bash
ollama pull qwen2.5:3b
```

Optional models:

```bash
ollama pull phi3:mini
ollama pull llama3
ollama pull tinyllama
```

---

## 2. Python 3.9+

Required.

---

# 🔧 Setup

---

## Clone Repository

```bash
git clone https://github.com/i0ta-segfault/agent-observation-system.git

cd agent-observation-system
```

---

## Create Virtual Environment

### Windows

```powershell
python -m venv venv

.\venv\Scripts\activate
```

### Linux / WSL

```bash
python -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🚀 Running The System

---

# 1. Start Ollama

```bash
ollama serve
```

---

# 2. Start FastAPI Gateway

From project root:

```bash
uvicorn gateway.main:app --reload
```

---

# 3. Run Agent Tests

```bash
python test_agents.py
```

This will:

- execute workflows
- generate spans
- estimate tokens
- export telemetry
- populate observability database
- feed Grafana dashboards

---

# 4. Run Workflow Analysis

```bash
cd analysis

python trace_analyzer.py
```

This generates:

```text
analysis_reports.db
```

containing AI-generated workflow analysis reports.

---

# 5. Run Evaluation Pipeline

```bash
python evaluation/evaluate.py
```

This generates:

```text
evaluation_results.db
```

containing Email Classification evaluation metrics.

---

# 🗄️ Database Architecture

---

# 1. `observability.db`

Primary telemetry database.

Contains:

- traces
- spans
- latency
- tokens
- errors
- workflow metadata

Used for:

- observability dashboards
- tracing
- latency analysis
- runtime monitoring

---

# 2. `analysis_reports.db`

AI-generated workflow analysis reports.

Generated by:

```text
analysis/trace_analyzer.py
```

Contains:

- workflow summaries
- bottleneck analysis
- optimization recommendations
- latency insights

---

# 3. `evaluation_results.db`

Offline evaluation database.

Current support:

- EmailClassifier evaluation only

Contains:

- expected outputs
- predicted outputs
- correctness
- latency
- token usage
- accuracy metrics

---

# 📈 Grafana Setup

---

# Install Grafana OSS

Download:

```text
https://grafana.com/grafana/download
```

---

# Install SQLite Plugin

Inside Grafana `bin/` directory:

```powershell
.\grafana.exe cli plugins install frser-sqlite-datasource
```

Restart Grafana afterward.

---

# Start Grafana

```powershell
.\grafana.exe server
```

Open:

```text
http://localhost:3000
```

Default login:

```text
admin / admin
```

---

# 🔌 Add SQLite Datasources

Go to:

```text
Connections → Data Sources
```

Add:

```text
frser-sqlite-datasource
```

Create separate datasources for:

- observability.db
- analysis_reports.db
- evaluation_results.db

---

# 📊 Example Grafana Queries

---

# OBSERVABILITY DATABASE QUERIES

Datasource:

```text
observability.db
```

---

## Workflow Latency

```sql
SELECT
  start_ts * 1000 AS time,
  latency_seconds
FROM traces
WHERE event_type = 'workflow'
ORDER BY start_ts;
```

Visualization:

```text
Time Series
```

---

## Workflow Success Rate

```sql
SELECT
  name as workflow,

  ROUND(
    100.0 * SUM(success) / COUNT(*),
    2
  ) as success_rate

FROM traces

WHERE event_type = 'workflow'

GROUP BY name;
```

Visualization:

```text
Bar Chart
```

---

## Token Usage by Workflow

```sql
SELECT
  name,

  SUM(tokens) as total_tokens

FROM traces

WHERE event_type = 'workflow'

GROUP BY name

ORDER BY total_tokens DESC;
```

Visualization:

```text
Bar Chart
```

---

## Slowest Operations

```sql
SELECT
  name,
  AVG(latency_seconds) AS avg_latency
FROM traces
GROUP BY name
ORDER BY avg_latency DESC;
```

Visualization:

```text
Bar Chart
```

---

## Failure Analysis

```sql
SELECT
  name,
  COUNT(*) AS failures
FROM traces
WHERE success = 0
GROUP BY name;
```

Visualization:

```text
Bar Chart
```

---

## Span Distribution

```sql
SELECT
  event_type,
  COUNT(*) AS total
FROM traces
GROUP BY event_type;
```

Visualization:

```text
Pie Chart
```

---

## Workflow DAG / Span Relationships

```sql
SELECT
  trace_id,
  span_id,
  parent_span_id,
  event_type,
  name
FROM traces
ORDER BY start_ts;
```

Visualization:

```text
Table
```

---

# ANALYSIS DATABASE QUERIES

Datasource:

```text
analysis_reports.db
```

---

## Workflow Bottlenecks

```sql
SELECT
  workflow_name,
  bottleneck_operation,
  bottleneck_latency
FROM analysis_reports
ORDER BY bottleneck_latency DESC;
```

Visualization:

```text
Table
```

---

## Workflow Analysis Summaries

```sql
SELECT
  workflow_name,
  summary,
  recommendations
FROM analysis_reports;
```

Visualization:

```text
Table
```

---

# EVALUATION DATABASE QUERIES

Datasource:

```text
evaluation_results.db
```

⚠ Current evaluation support is implemented only for the Email Classification workflow.

---

## Email Classifier Accuracy

```sql
SELECT
  ROUND(
    AVG(correct) * 100,
    2
  ) as accuracy_percent
FROM evaluations;
```

Visualization:

```text
Gauge
```

---

# 🧪 LangGraph Compatibility

Current status:

- LangGraph orchestration: ❌ Not yet implemented
- LangGraph instrumentation compatibility: ✅ Supported

Example:

```python
from agents import instrument_langgraph_node

wrapped_node = instrument_langgraph_node(
    node_fn,
    collector,
    "planner",
)
```

---

# 🎯 Development Phases

---

# ✅ Phase 1 — Agent Framework

Implemented:

- Email Classification Agent
- PDF Extraction Agent
- Ollama integration
- Runtime orchestration
- Error handling

---

# ✅ Phase 2 — FastAPI Gateway

Implemented:

- Telemetry ingestion server
- Unified event pipeline
- SQLite persistence
- Export pipeline

---

# ✅ Phase 3 — Runtime Instrumentation

Implemented:

- Span tracing
- Workflow tracing
- Nested instrumentation
- Parent-child span relationships
- Token estimation
- Exporters

---

# ✅ Phase 4 — Observability Dashboarding

Implemented:

- SQLite persistence
- Grafana integration
- Dashboard panels
- DAG reconstruction
- Failure analysis
- Token visualization

---

# ✅ Phase 5 — Workflow Analysis System

Implemented:

- AI-powered trace analysis
- Bottleneck detection
- Workflow summarization
- Optimization recommendations
- Offline report generation

---

# 🚧 Phase 6 — Evaluation & Optimization

In Progress.

Current Features:

- Email classification evaluation
- Ground-truth comparisons
- Accuracy measurement
- Offline evaluation pipeline

Planned Features:

- hallucination analysis
- model benchmarking
- adaptive routing
- prompt optimization
- caching
- multi-model orchestration

---

# 📁 Updated Project Structure

```text
agent-observation-system/
│
├── agents/
│   ├── __init__.py
│   ├── instrumentation.py
│   ├── runtime.py
│   ├── email_agent.py
│   └── pdf_agent.py
│
├── analysis/
│   ├── trace_analyzer.py
│   └── analysis_reports.db
│
├── evaluation/
│   ├── evaluate.py
│   ├── evaluation_storage.py
│   └── ground_truth.py
│
├── gateway/
│   ├── main.py
│   ├── storage.py
│   └── models.py
│
├── test_data/
│
├── observability.db
├── observability_llama3.db
├── evaluation_results.db
├── test_agents.py
├── QUICKSTART.md
├── requirements.txt
└── README.md
```

---

# 🛠️ Technology Stack

## Core

- Python 3.9+
- Ollama
- SQLite
- FastAPI
- Grafana OSS

---

## AI Runtime

- Qwen2.5
- Phi3
- Llama3
- TinyLlama

---

## PDF Processing

- pdfplumber
- pytesseract (optional OCR)

---

# 📌 Notes

Included sample databases:

- observability.db
- observability_llama3.db

can be directly mounted into Grafana for instant visualization without rerunning workflows.

The evaluation system currently supports only Email Classification workflows.