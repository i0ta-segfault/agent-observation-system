"""
PDF Text Extraction Agent
"""

from typing import Any, Dict

import os
import importlib

from pathlib import Path

from .runtime import AgentRuntime, OllamaClient
from .instrumentation import get_tracer


class PDFAgent:

    def __init__(
        self,
        use_ocr: bool = False,
        model: str = "qwen2.5:3b",
        ollama_url: str = "http://localhost:11434",
    ):

        self.name = "PDFExtractor"

        self.model = model

        self.use_ocr = use_ocr

        self._last_extraction = {}

        self.tracer = get_tracer()

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

                print(
                    f"\n[PDF DEBUG] "
                    f"TOTAL PAGES: {metadata['total_pages']}"
                )

                for page_num, page in enumerate(pdf.pages, 1):

                    print(
                        f"\n[PDF DEBUG] "
                        f"PROCESSING PAGE {page_num}"
                    )

                    page_start = page_num

                    with self.tracer.span(
                        event_type="pdf_page_extract",
                        name=f"PDFExtractor.page_{page_num}",
                    ):

                        text = page.extract_text()

                        if text and text.strip():

                            print(
                                f"[PDF DEBUG] "
                                f"TEXT FOUND ON PAGE {page_num}"
                            )

                            all_text.append(
                                f"--- Page {page_num} ---\n{text}"
                            )

                            metadata["pages_with_text"] += 1

                        elif self.use_ocr:

                            print(
                                f"[PDF DEBUG] "
                                f"RUNNING OCR ON PAGE {page_num}"
                            )

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

                    print(
                        f"[PDF DEBUG] "
                        f"PAGE {page_num} COMPLETE"
                    )

            combined_text = "\n\n".join(all_text)

            print(
                f"\n[PDF DEBUG] "
                f"TOTAL TEXT SIZE: {len(combined_text)} chars"
            )

            return {
                "success": True,
                "text": combined_text,

                "metadata": metadata,

                "char_count": len(combined_text),
                "word_count": len(combined_text.split()),
            }

        except Exception as exc:

            print(
                f"\n[PDF ERROR] {exc}"
            )

            return {
                "success": False,
                "error": str(exc),
                "text": "",
                "metadata": {},
            }

    # =====================================================
    # CHUNKING
    # =====================================================

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1200,
    ):

        chunks = []

        current = ""

        paragraphs = text.split("\n")

        for para in paragraphs:

            if len(current) + len(para) < chunk_size:

                current += "\n" + para

            else:

                chunks.append(current)

                current = para

        if current.strip():
            chunks.append(current)

        return chunks

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

        pdf_text = extraction["text"]

        chunks = self.chunk_text(pdf_text)

        print(
            f"\n[PDF DEBUG] "
            f"TOTAL CHUNKS: {len(chunks)}"
        )

        summarized_chunks = []

        for idx, chunk in enumerate(chunks, 1):

            print(
                f"\n[PDF DEBUG] "
                f"SUMMARIZING CHUNK {idx}"
            )

            with self.tracer.span(
                event_type="pdf_chunk_summary",
                name=f"PDFExtractor.chunk_{idx}",
            ):

                chunk_prompt = f"""
Summarize this PDF chunk briefly.

PDF Chunk:
{chunk[:1200]}
"""

                chunk_summary = self._ollama.generate(
                    chunk_prompt,
                    temperature=0.2,
                    max_tokens=200,
                )

                summarized_chunks.append(
                    f"Chunk {idx} Summary:\n{chunk_summary}"
                )

            print(
                f"[PDF DEBUG] "
                f"CHUNK {idx} SUMMARY COMPLETE"
            )

        combined_summary = "\n\n".join(
            summarized_chunks
        )

        print(
            f"\n[PDF DEBUG] "
            f"BUILDING FINAL PROMPT"
        )

        if task == "summarize":

            return f"""
Generate a final concise summary
from these chunk summaries.

Chunk Summaries:
{combined_summary}
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

Chunk Summaries:
{combined_summary}
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

Chunk Summaries:
{combined_summary}
"""

        return f"""
Analyze this PDF.

Chunk Summaries:
{combined_summary}
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