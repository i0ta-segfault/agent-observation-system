# LLM Agent Observation System

An end-to-end observability and evaluation system for LLM-powered agents using local models, tracing instrumentation, SQLite persistence, FastAPI, and Grafana dashboards.

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
- LangGraph-compatible instrumentation wrappers

The goal is to monitor and analyze the internal execution flow of AI agents similarly to how observability platforms monitor distributed backend systems.

---

# 🏗️ System Architecture

```text
User/Test Script
      │
      ▼
FastAPI Telemetry Gateway
      │
      ▼
Instrumented Agent Runtime
      │
      ├── EmailAgent
      ├── PDFAgent
      └── LangGraph-compatible nodes
      │
      ▼
Ollama Local LLM
      │
      ▼
Tracing + Span Generation
      │
      ▼
SQLite Observability Store
      │
      ▼
Grafana Dashboards
```

---

# 🔭 Observability Pipeline

The system includes a lightweight observability stack inspired by OpenTelemetry.

## Features

- Workflow-level tracing
- Nested spans
- Span hierarchy
- Latency tracking
- Token estimation
- Error monitoring
- Trace persistence
- Dashboard visualization
- Workflow DAG reconstruction

---

# 📡 Span Types

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

## 1. Email Classification Agent

Features:

- Email categorization
- Configurable categories
- Batch processing
- Runtime tracing
- Latency monitoring

Supported categories:

- invoice
- spam
- urgent
- general
- support
- marketing
- notification

---

## 2. PDF Extraction Agent

Features:

- PDF text extraction
- OCR support
- Summarization
- Classification
- Information extraction
- Runtime tracing

Processing modes:

- summarize
- extract_info
- classify
- custom analysis

---

# ⚙️ Runtime Architecture

The project uses composition and wrappers instead of inheritance-heavy design.

## Core Runtime Flow

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

## `agents/runtime.py`

Generic runtime responsible for:

- orchestrating execution
- tracing spans
- handling errors
- token estimation
- latency tracking

---

## `agents/instrumentation.py`

Provides:

- tracing
- spans
- exporters
- instrumentation wrappers
- token estimation
- event persistence
- LangGraph compatibility

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

---

# 📦 Installation

## Prerequisites

### 1. Install Ollama

Download:

https://ollama.ai/download

Pull a model:

```bash
ollama pull phi3:mini
```

or:

```bash
ollama pull llama3
```

---

### 2. Python 3.9+

Required.

---

# 🔧 Setup

## Clone Repository

```bash
git clone https://github.com/nandikabansal/agent-observation-system.git  # if PR not yet merged use this link https://github.com/i0ta-segfault/agent-observation-system.git
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

## 1. Start Ollama

```bash
ollama serve
```

---

## 2. Start FastAPI Gateway

From project root:

```bash
uvicorn gateway.main:app --reload
```

---

## 3. Run Agent Tests

```bash
python test_agents.py
```

This will:

- execute agents
- generate traces
- persist telemetry
- populate SQLite database
- feed Grafana dashboards

---

# 🗄️ Observability Storage

Telemetry is stored in:

```text
observability.db
```

and optionally:

```text
observability_llama3.db
```

These databases contain:

- traces
- spans
- latency data
- token estimates
- failures
- metadata

---

# 📈 Grafana Dashboard Setup

## Install Grafana OSS

Download:

https://grafana.com/grafana/download

---

## Install SQLite Plugin

Inside Grafana `bin/` directory:

```powershell
.\grafana.exe cli plugins install frser-sqlite-datasource
```

Restart Grafana afterward.

---

## Start Grafana

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

# 🔌 Add SQLite Datasource

Go to:

```text
Connections → Data Sources
```

Add:

```text
frser-sqlite-datasource
```

---

## Database Path Examples

### Windows

```text
D:\Programming\agent-observation-system\observability.db
```

### WSL

```text
/mnt/d/Programming/agent-observation-system/observability.db
```

---

# 📊 Example Grafana Queries

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

## Email Agent Latency

```sql
SELECT
  start_ts * 1000 AS time,
  latency_seconds
FROM traces
WHERE event_type = 'workflow'
AND name = 'EmailClassifier'
ORDER BY start_ts;
```

Visualization:

```text
Time Series
```

---

## PDF Agent Latency

```sql
SELECT
  start_ts * 1000 AS time,
  latency_seconds
FROM traces
WHERE event_type = 'workflow'
AND name = 'PDFExtractor'
ORDER BY start_ts;
```

Visualization:

```text
Time Series
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

Completed.

Implemented:

- Email Classification Agent
- PDF Extraction Agent
- Wrapper-based runtime architecture
- Ollama local inference integration
- Error handling
- Test suite

---

# ✅ Phase 2 — FastAPI Gateway

Completed.

Implemented:

- FastAPI telemetry ingestion server
- Unified event pipeline
- Request routing
- SQLite integration
- Telemetry persistence

---

# ✅ Phase 3 — Runtime Instrumentation

Completed.

Implemented:

- Span tracing
- Workflow tracing
- Nested instrumentation
- Trace IDs
- Parent-child span relationships
- Token estimation
- Runtime wrappers

---

# ✅ Phase 4 — Observability Dashboarding

Completed.

Implemented:

- SQLite persistence
- Grafana integration
- Dashboard panels
- Latency visualization
- Span distribution visualization
- Failure analysis
- Workflow DAG reconstruction

---

# 🚧 Phase 5 — Evaluation System

In Progress.

Planned Features:

- Automated benchmarking
- Test datasets
- Accuracy scoring
- Hallucination analysis
- Agent comparison
- Response quality evaluation
- Latency benchmarking across models
- Evaluation reports

Potential Stack:

- pandas
- scikit-learn
- matplotlib

---

# 🚧 Phase 6 — Optimization System

In Progress.

Planned Features:

- Cost simulation
- Token optimization
- Prompt optimization
- Behavior analysis
- Response caching
- A/B testing
- Adaptive routing
- Multi-model optimization

Potential Features:

- Dynamic model switching
- Prompt compression
- Smart retries
- Caching layers

---

# 📁 Project Structure

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
├── gateway/
│   ├── main.py
│   └── storage.py
│
├── observability.db
├── observability_llama3.db
├── test_agents.py
├── requirements.txt
├── QUICKSTART.md
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

- Llama3
- Phi3
- Mistral

---

## PDF Processing

- pdfplumber
- pytesseract (optional OCR)

---

# 📌 Notes

Included sample databases:

- `observability.db`
- `observability_llama3.db`

can be directly mounted into Grafana for instant dashboard visualization without rerunning agents.