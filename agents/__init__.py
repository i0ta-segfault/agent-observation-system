"""
LLM Agent Framework
Agent implementations + observability runtime.
"""

from .email_agent import EmailAgent
from .pdf_agent import PDFAgent

from .runtime import (
    AgentRuntime,
    OllamaClient,
)

from .instrumentation import (
    instrument,
    get_tracer,
    ConsoleExporter,
    HTTPExporter,
)

__all__ = [
    "EmailAgent",
    "PDFAgent",

    "AgentRuntime",
    "OllamaClient",

    "instrument",
    "get_tracer",

    "ConsoleExporter",
    "HTTPExporter",
]