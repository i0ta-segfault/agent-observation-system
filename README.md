# LLM Agent Observation System

An end-to-end system for monitoring, evaluating, and optimizing LLM agents with local models.

## 📋 Project Overview

This system implements a complete observability and optimization pipeline for LLM agents:

- **Agent Framework**: Modular agent system with Email Classification and PDF Extraction
- **Observability**: Prometheus metrics and Grafana dashboards
- **Evaluation**: Automated benchmarking and performance analysis
- **Optimization**: Behavior analysis and cost simulation

## 🏗️ Architecture

```
User/Test Script
      │
      ▼
FastAPI Gateway (Phase 2)
      │
      ▼
LLM Agents (Phase 1) ✅
      │
      ▼
Local LLM (Ollama)
      │
      ▼
Metrics + Evaluation
      │
      ├── Prometheus (Phase 4)
      └── Evaluation Engine (Phase 5)
              │
              ▼
           Grafana
```

## Phase 1: Agent Framework (Wrapper-Based) Completed

### Implemented Agents

1. **Email Classification Agent**
   - Classifies emails into categories (invoice, spam, urgent, etc.)
   - Configurable categories
   - Batch processing support

2. **PDF Extraction Agent**
   - Extracts text from PDFs using pdfplumber
   - Optional OCR support for image-based PDFs
   - Multiple processing modes: summarize, extract_info, classify

### Features

- Wrapper-first runtime (no hard inheritance requirement)
- Built-in trace and metrics collection (latency, tokens, success rate)
- ✅ Ollama integration for local LLM inference
- ✅ Comprehensive error handling and logging
- ✅ Test suite with sample data

## Current Architecture

The project uses composition and wrappers:

- `agents/runtime.py`: generic runtime for `prompt_builder -> llm_call -> parser`
- `agents/instrumentation.py`: reusable wrappers for LLM calls, tools, and nodes
- `agents/email_agent.py`: email classifier built on runtime + wrappers
- `agents/pdf_agent.py`: pdfplumber/OCR extractor built on runtime + wrappers

This keeps agents decoupled and easier to extend across frameworks.

## LangGraph Status

- Is LangGraph orchestrating workflows right now: **No**
- Are we compatible with LangGraph instrumentation: **Yes**

You can instrument LangGraph nodes using `instrument_langgraph_node(...)`.

Example:

```python
from agents import MetricsCollector, instrument_langgraph_node

collector = MetricsCollector("my_graph")

def planner_node(state):
      return {"next": "tool", **state}

wrapped_planner = instrument_langgraph_node(planner_node, collector, "planner")
```

## When LangGraph Workflow Will Be Added

LangGraph orchestration is best added as a separate phase after API wiring:

1. Phase 2: FastAPI gateway for unified run/evaluate endpoints
2. Phase 3: LangGraph workflow graph (planner/tool/reasoning loops)
3. Phase 4: Prometheus + Grafana for exported observability

## 📦 Installation

### Prerequisites

1. **Install Ollama** (for local LLM inference)
   ```bash
   # Visit: https://ollama.ai/download
   # After installation, pull a model:
   ollama pull llama3
   ```

2. **Python 3.9+** required

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd agent-observation-system

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🧪 Testing Phase 1

### Start Ollama
```bash
# Make sure Ollama is running
ollama serve
```

### Run Tests
```bash
python test_agents.py
```

This will test:
- Email classification with sample emails
- PDF text extraction (create `test_data/sample.pdf` first)
- Agent metrics tracking

## 📁 Project Structure

```
agent-observation-system/
│
├── agents/                 # Agent implementations
│   ├── __init__.py
│   ├── instrumentation.py # Wrappers and tracing utilities
│   ├── runtime.py         # Generic composable agent runtime
│   ├── email_agent.py     # Email classifier
│   └── pdf_agent.py       # PDF extractor
│
├── test_agents.py         # Test script
├── requirements.txt       # Python dependencies
├── QUICKSTART.md          # Quick start guide
└── README.md
```

## 🔧 Usage Examples

### Email Classification

```python
from agents import EmailAgent

# Initialize agent
email_agent = EmailAgent()

# Classify an email
result = email_agent.run({
    "subject": "Invoice #12345",
    "body": "Payment due in 30 days"
})

print(result["output"]["category"])  # "invoice"
print(result["metrics"]["latency"])  # Response time
```

### PDF Extraction

```python
from agents import PDFAgent

# Initialize agent
pdf_agent = PDFAgent(use_ocr=False)

# Extract text only
extraction = pdf_agent.extract_only("document.pdf")
print(extraction["text"])

# Summarize PDF
summary = pdf_agent.process_pdf("document.pdf", task="summarize")
print(summary["output"]["processed_output"])
```

## 📊 Agent Metrics

Each agent automatically tracks:
- **Total Requests**: Total number of requests processed
- **Success Rate**: Percentage of successful requests
- **Average Latency**: Mean response time in seconds
- **Total Tokens**: Estimated token usage (for cost simulation)

```python
# Get agent metrics
trace_id = result["trace_id"]
print(f"Success Rate: {metrics['success_rate']:.2%}")
print(f"Avg Latency: {metrics['average_latency']:.2f}s")

# Get recent traces
traces = email_agent.get_recent_traces(limit=5)
print(traces[-1]["event_type"])
```

## 🎯 Next Phases

### Phase 2: FastAPI Gateway
- API endpoints for agents
- Request routing and validation
- API documentation

### Phase 3: Ollama Integration Enhancement
- Model switching
- Parameter tuning
- Response caching

### Phase 4: Observability
- Prometheus metrics
- Grafana dashboards
- Real-time monitoring

### Phase 5: Evaluation System
- Automated benchmarks
- Performance comparison
- Test datasets

### Phase 6: Optimization
- Behavior analysis
- Cost simulation
- A/B testing

## 🛠️ Technology Stack

- **Language**: Python 3.9+
- **LLM Runtime**: Ollama (Llama3, Mistral, Phi-3)
- **PDF Processing**: pdfplumber
- **Future**: FastAPI, Prometheus, Grafana, Pandas, Scikit-learn

## 📝 Development Timeline

- [x] **Week 1-2**: Phase 1 - Agent Framework ✅
- [ ] **Week 3**: Phase 2 - API Gateway
- [ ] **Week 4**: Phase 3-4 - Observability
- [ ] **Week 5**: Phase 5 - Evaluation
- [ ] **Week 6**: Phase 6 - Optimization

## 🤝 Contributing

This is a learning project. Feel free to:
- Add new agents
- Improve existing agents
- Add test cases
- Optimize performance

## 📄 License

MIT License

## 🔗 Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

---

**Current Status**: Phase 1 Complete ✅ | Ready for Phase 2: FastAPI Gateway