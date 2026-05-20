from __future__ import annotations

from typing import Any, Callable, Dict

import logging
import time
import requests

from .instrumentation import (
    get_tracer,
    estimate_tokens,
)

logger = logging.getLogger(__name__)


# =========================================================
# OLLAMA CLIENT
# =========================================================

class OllamaClient:
    def __init__(
        self,
        model: str = "phi3:mini",
        base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(
    self,
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 500,
) -> str:

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"]


# =========================================================
# AGENT RUNTIME
# =========================================================

class AgentRuntime:

    def __init__(
        self,
        name: str,
        model: str,

        prompt_builder: Callable[[Any], str],
        parser: Callable[[str], Any],

        llm_call: Callable[..., str],
    ):

        self.name = name
        self.model = model

        self.prompt_builder = prompt_builder
        self.parser = parser

        self.llm_call = llm_call

        self.tracer = get_tracer()

    def run(
        self,
        input_data: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:

        start = time.time()

        trace_id = None

        try:

            with self.tracer.span(
                event_type="workflow",
                name=self.name,
                input_payload=input_data,
            ) as root_span:

                trace_id = root_span["trace_id"]

                with self.tracer.span(
                    event_type="prompt_builder",
                    name=f"{self.name}.prompt_builder",
                    trace_id=trace_id,
                    parent_span_id=root_span["span_id"],
                ):

                    prompt = self.prompt_builder(input_data)

                with self.tracer.span(
                    event_type="llm_call",
                    name=f"{self.name}:{self.model}",
                    trace_id=trace_id,
                    parent_span_id=root_span["span_id"],
                    input_payload={
                        "prompt_length": len(prompt)
                    },
                ):

                    response_text = self.llm_call(
                        prompt,
                        **kwargs,
                    )

                with self.tracer.span(
                    event_type="parser",
                    name=f"{self.name}.parser",
                    trace_id=trace_id,
                    parent_span_id=root_span["span_id"],
                ):

                    output = self.parser(response_text)

            latency = time.time() - start

            tokens = estimate_tokens(
                prompt,
                response_text,
            )

            return {
                "success": True,
                "trace_id": trace_id,

                "output": output,
                "raw_response": response_text,

                "metrics": {
                    "latency": latency,
                    "tokens": tokens,
                },
            }

        except Exception as exc:

            logger.exception(
                "%s runtime failed",
                self.name,
            )

            return {
                "success": False,
                "trace_id": trace_id,
                "error": str(exc),
            }