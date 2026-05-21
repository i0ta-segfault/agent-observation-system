"""
Email Classification Agent
Classifies emails into categories.
"""

from typing import Any

from .runtime import AgentRuntime, OllamaClient
from .instrumentation import (
    instrument,
    ConsoleExporter,
)

# =========================================================
# GLOBAL INSTRUMENTATION INIT
# =========================================================

instrument(
    service_name="email-agent-system",
    exporter=ConsoleExporter(),
)


class EmailAgent:

    DEFAULT_CATEGORIES = [
        "invoice",
        "spam",
        "urgent",
        "general",
        "support",
        "marketing",
        "notification"
    ]

    def __init__(
        self,
        categories: list = None,
        model: str = "qwen2.5:3b",
        ollama_url: str = "http://localhost:11434",
    ):

        self.name = "EmailClassifier"

        self.model = model

        self.ollama_url = ollama_url

        self.categories = categories or self.DEFAULT_CATEGORIES

        self._ollama = OllamaClient(
            model=model,
            base_url=ollama_url,
        )

        self._runtime = AgentRuntime(
            name=self.name,
            model=self.model,

            prompt_builder=self.build_prompt,
            parser=self.parse_response,

            llm_call=self._ollama.generate,
        )

    # =====================================================
    # PROMPT BUILDER
    # =====================================================

    def build_prompt(self, input_data: Any) -> str:

        if isinstance(input_data, str):
            email_text = input_data

        elif isinstance(input_data, dict):

            subject = input_data.get("subject", "")
            body = input_data.get("body", "")

            email_text = f"""
Subject: {subject}

{body}
"""

        else:
            email_text = str(input_data)

        categories_str = ", ".join(self.categories)

        return f"""
You are an email classification assistant.

Classify the email into ONE category:

{categories_str}

Email:
{email_text}

Respond ONLY with category name.
"""

    # =====================================================
    # RESPONSE PARSER
    # =====================================================

    def parse_response(self, llm_response: str):

        category = llm_response.strip().lower()

        found_category = "general"

        for cat in self.categories:
            if cat.lower() in category:
                found_category = cat.lower()
                break

        confidence = (
            0.9
            if len(llm_response.strip()) < 20
            else 0.7
        )

        return {
            "category": found_category,
            "confidence": confidence,
            "raw_classification": llm_response.strip(),
        }

    # =====================================================
    # PUBLIC API
    # =====================================================

    def run(self, input_data: Any, **kwargs):
        return self._runtime.run(input_data, **kwargs)

    def classify_batch(self, emails: list):

        results = []

        for email in emails:
            results.append(self.run(email))

        return results