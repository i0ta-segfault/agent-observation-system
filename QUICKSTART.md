# Quick Start Guide - Phase 1

## 🚀 Get Started in 5 Minutes

### Step 1: Install Ollama

**Windows:**
```powershell
# Download from: https://ollama.ai/download
# After installation, open terminal and run:
ollama pull llama3
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3
```

### Step 2: Verify Ollama is Running

```bash
# Check if Ollama is running
curl http://localhost:11434

# You should see: "Ollama is running"
```

### Step 3: Setup Python Environment

```bash
# Navigate to project directory
cd agent-observation-system

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Create Test Data (Optional for PDF testing)

```bash
# Create test directory
mkdir test_data

# Add a sample PDF file to test_data/sample.pdf
# (any PDF document will work)
```

### Step 5: Run the Tests

```bash
python test_agents.py
```

## 📝 What You'll See

The test script will:

1. **Test Email Agent** (5 sample emails)
   - Invoice classification
   - Spam detection
   - Urgent message identification
   - General emails
   - Marketing content

2. **Test PDF Agent** (if PDF is provided)
   - Text extraction
   - Document summarization
   - Document classification

3. **Show Metrics**
   - Request counts
   - Success rates
   - Average latency
   - Token usage

## 🎯 Expected Output

```
╔════════════════════════════════════════════════════════════╗
║         LLM AGENT OBSERVATION SYSTEM - PHASE 1             ║
║              Agent Framework Testing                       ║
╚════════════════════════════════════════════════════════════╝

============================================================
TESTING EMAIL CLASSIFICATION AGENT
============================================================

--- Email 1 ---
Subject: Invoice #12345 - Payment Due
Body: Please find attached invoice for services...
✓ Category: invoice
  Confidence: 0.90
  Latency: 2.34s
  Tokens: ~245

[... more test results ...]

--- Agent Performance Metrics ---
agent_name: EmailClassifier
total_requests: 5
successful_requests: 5
average_latency: 2.15
success_rate: 1.0
```

## 🔧 Troubleshooting

### "Connection refused" error
- Make sure Ollama is running: `ollama serve`
- Check if port 11434 is accessible

### "Model not found" error
- Pull the model: `ollama pull llama3`
- Try a different model: `ollama pull mistral`

### Import errors
- Make sure virtual environment is activated
- Reinstall: `pip install -r requirements.txt`

### PDF extraction fails
- Install pdfplumber: `pip install pdfplumber`
- For OCR: `pip install pytesseract pillow`

## 🎉 Next Steps

Once Phase 1 tests pass:

1. ✅ Experiment with different prompts
2. ✅ Add custom email categories
3. ✅ Test with your own PDFs
4. ✅ Review agent metrics
5. ➡️ Ready for Phase 2: FastAPI Gateway

## LangGraph Compatibility Quick Note

- LangGraph is not yet the active workflow engine in the project.
- You can already instrument LangGraph nodes using provided wrappers.

```python
from agents import MetricsCollector, instrument_langgraph_node

collector = MetricsCollector("graph_demo")

def node(state):
   return {"ok": True, **state}

wrapped_node = instrument_langgraph_node(node, collector, "node")
state_out = wrapped_node({"step": 1})
print(collector.get_summary())
```

## 💡 Tips

- **Start with Email Agent**: Easier to test, no file dependencies
- **Use smaller models**: If slow, try `ollama pull phi3`
- **Check logs**: Detailed logging helps debug issues
- **Monitor metrics**: Watch latency and token usage

## 📚 Learn More

- [agents/runtime.py](agents/runtime.py) - Composable runtime
- [agents/instrumentation.py](agents/instrumentation.py) - Wrappers and tracing
- [agents/email_agent.py](agents/email_agent.py) - Email classification logic
- [agents/pdf_agent.py](agents/pdf_agent.py) - PDF extraction pipeline

---

**Need Help?** Check the main [README.md](README.md) for detailed documentation.
