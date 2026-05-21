# =========================================================
# runtime.py
# =========================================================

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
        model: str = "qwen2.5:3b",
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

        print("\n[DEBUG] Starting Ollama generation")

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

        print("[DEBUG] Ollama response received")

        response.raise_for_status()

        data = response.json()

        print("[DEBUG] Ollama JSON parsed")

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

            print(
                f"\n[DEBUG] STARTING WORKFLOW: "
                f"{self.name}"
            )

            with self.tracer.span(
                event_type="workflow",
                name=self.name,
                input_payload=input_data,
            ) as root_span:

                print(
                    f"[DEBUG] WORKFLOW SPAN CREATED: "
                    f"{root_span}"
                )

                trace_id = root_span["trace_id"]

                print(
                    f"[DEBUG] TRACE ID: {trace_id}"
                )

                # ============================================
                # PROMPT BUILDER
                # ============================================

                with self.tracer.span(
                    event_type="prompt_builder",

                    name=f"{self.name}.prompt_builder",

                    trace_id=trace_id,

                    parent_span_id=root_span["span_id"],

                ) as prompt_span:

                    print(
                        f"[DEBUG] ENTERING PROMPT BUILDER"
                    )

                    prompt = self.prompt_builder(
                        input_data
                    )

                    prompt_span["metadata"] = {
                        "prompt_length": len(prompt),
                    }

                    prompt_span["output_payload"] = {
                        "prompt_preview": prompt[:300]
                    }

                    print(
                        f"[DEBUG] PROMPT BUILT: "
                        f"{len(prompt)} chars"
                    )

                # ============================================
                # LLM CALL
                # ============================================

                with self.tracer.span(

                    event_type="llm_call",

                    name=f"{self.name}:{self.model}",

                    trace_id=trace_id,

                    parent_span_id=root_span["span_id"],

                    input_payload={
                        "prompt_length": len(prompt)
                    },

                ) as llm_span:

                    print(
                        f"[DEBUG] STARTING LLM CALL"
                    )

                    response_text = self.llm_call(
                        prompt,
                        **kwargs,
                    )

                    print(
                        f"[DEBUG] LLM CALL COMPLETE"
                    )

                    tokens = estimate_tokens(
                        prompt,
                        response_text,
                    )

                    llm_span["tokens"] = tokens

                    llm_span["metadata"] = {
                        "model": self.model,
                        "prompt_length": len(prompt),
                        "response_length": len(
                            response_text
                        ),
                    }

                    llm_span["output_payload"] = {
                        "response_preview":
                            response_text[:500]
                    }

                    root_span["tokens"] = (
                        root_span.get("tokens", 0)
                        + tokens
                    )

                print(
                    f"[DEBUG] LLM SPAN EXITED"
                )

                # ============================================
                # PARSER
                # ============================================

                with self.tracer.span(

                    event_type="parser",

                    name=f"{self.name}.parser",

                    trace_id=trace_id,

                    parent_span_id=root_span["span_id"],

                ) as parser_span:

                    print(
                        f"[DEBUG] STARTING PARSER"
                    )

                    output = self.parser(
                        response_text
                    )

                    parser_span["output_payload"] = {
                        "parsed_output_preview":
                            str(output)[:500]
                    }

                    print(
                        f"[DEBUG] PARSER COMPLETE"
                    )

                print(
                    f"[DEBUG] PARSER SPAN EXITED"
                )

                root_span["metadata"] = {

                    "workflow_name": self.name,

                    "model": self.model,

                    "input_type":
                        str(type(input_data)),

                    "success": True,
                }

                root_span["output_payload"] = {
                    "workflow_output_preview":
                        str(output)[:500]
                }

                print(
                    f"[DEBUG] ABOUT TO EXIT "
                    f"WORKFLOW CONTEXT"
                )

            print(
                f"[DEBUG] WORKFLOW CONTEXT EXITED"
            )

            latency = time.time() - start

            print(
                f"[DEBUG] TOTAL LATENCY: "
                f"{latency:.2f}s"
            )

            tokens = root_span.get("tokens", 0)

            print(
                f"[DEBUG] TOKENS ESTIMATED: "
                f"{tokens}"
            )

            print(
                f"[DEBUG] RETURNING SUCCESS RESPONSE"
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

            print(
                f"\n[DEBUG] EXCEPTION OCCURRED "
                f"IN WORKFLOW: {self.name}"
            )

            print(
                f"[DEBUG] EXCEPTION TYPE: "
                f"{type(exc).__name__}"
            )

            print(
                f"[DEBUG] EXCEPTION: {exc}"
            )

            logger.exception(
                "%s runtime failed",
                self.name,
            )

            return {

                "success": False,

                "trace_id": trace_id,

                "error": str(exc),
            }