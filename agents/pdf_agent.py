"""
PDF Text Extraction Agent
"""

from typing import Any, Dict

import os
import importlib

from pathlib import Path

from .runtime import AgentRuntime, OllamaClient


class PDFAgent:

    def __init__(
        self,
        use_ocr: bool = False,
        model: str = "phi3:mini",
        ollama_url: str = "http://localhost:11434",
    ):

        self.name = "PDFExtractor"

        self.model = model

        self.use_ocr = use_ocr

        self._last_extraction = {}

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
    # PDF EXTRACTION
    # =====================================================

    def extract_text_from_pdf(
        self,
        pdf_path: str,
    ) -> Dict[str, Any]:

        try:

            import pdfplumber

            if not os.path.exists(pdf_path):
                raise FileNotFoundError(
                    f"PDF not found: {pdf_path}"
                )

            all_text = []

            metadata = {
                "file_name": Path(pdf_path).name,
                "file_size": os.path.getsize(pdf_path),
                "total_pages": 0,
                "pages_with_text": 0,
            }

            with pdfplumber.open(pdf_path) as pdf:

                metadata["total_pages"] = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, 1):

                    text = page.extract_text()

                    if text and text.strip():

                        all_text.append(
                            f"--- Page {page_num} ---\n{text}"
                        )

                        metadata["pages_with_text"] += 1

                    elif self.use_ocr:

                        try:

                            image = page.to_image()

                            pytesseract = importlib.import_module(
                                "pytesseract"
                            )

                            ocr_text = pytesseract.image_to_string(
                                image.original
                            )

                            if ocr_text.strip():

                                all_text.append(
                                    f"--- Page {page_num} OCR ---\n{ocr_text}"
                                )

                                metadata["pages_with_text"] += 1

                        except ImportError:
                            pass

            combined_text = "\n\n".join(all_text)

            return {
                "success": True,
                "text": combined_text,

                "metadata": metadata,

                "char_count": len(combined_text),
                "word_count": len(combined_text.split()),
            }

        except Exception as exc:

            return {
                "success": False,
                "error": str(exc),
                "text": "",
                "metadata": {},
            }

    # =====================================================
    # PROMPT BUILDER
    # =====================================================

    def build_prompt(self, input_data: Any) -> str:

        if isinstance(input_data, str):

            pdf_path = input_data
            task = "summarize"

        else:

            pdf_path = input_data["pdf_path"]
            task = input_data.get("task", "summarize")

        extraction = self.extract_text_from_pdf(pdf_path)

        if not extraction["success"]:
            raise Exception(extraction["error"])

        self._last_extraction = extraction

        pdf_text = extraction["text"][:800]

        if task == "summarize":

            return f"""
Summarize this PDF.

PDF Content:
{pdf_text}
"""

        elif task == "classify":

            categories = input_data.get(
                "categories",
                ["business", "technical", "legal", "other"]
            )

            categories_str = ", ".join(categories)

            return f"""
Classify this document into ONE category:

{categories_str}

PDF Content:
{pdf_text}
"""

        elif task == "extract_info":

            fields = input_data.get(
                "fields",
                ["key information"]
            )

            fields_str = ", ".join(fields)

            return f"""
Extract these fields:

{fields_str}

PDF Content:
{pdf_text}
"""

        return f"""
Analyze this PDF.

PDF Content:
{pdf_text}
"""

    # =====================================================
    # RESPONSE PARSER
    # =====================================================

    def parse_response(self, llm_response: str):

        return {
            "processed_output": llm_response.strip(),

            "extraction_metadata":
                self._last_extraction.get("metadata", {}),

            "source_char_count":
                self._last_extraction.get("char_count", 0),

            "source_word_count":
                self._last_extraction.get("word_count", 0),
        }

    # =====================================================
    # PUBLIC API
    # =====================================================

    def run(self, input_data: Any, **kwargs):
        return self._runtime.run(input_data, **kwargs)

    def extract_only(self, pdf_path: str):
        return self.extract_text_from_pdf(pdf_path)

    def process_pdf(
        self,
        pdf_path: str,
        task: str = "summarize",
        **kwargs,
    ):

        return self.run({
            "pdf_path": pdf_path,
            "task": task,
            **kwargs,
        })