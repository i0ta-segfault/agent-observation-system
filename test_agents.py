"""
Test Script for Agent Framework
"""

import sys
import os

from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents import EmailAgent, PDFAgent

from agents.instrumentation import (
    instrument,
    ConsoleExporter,
    HTTPExporter
)


# =========================================================
# EMAIL TEST
# =========================================================

def test_email_agent():

    print("\n" + "=" * 60)
    print("TESTING EMAIL CLASSIFICATION AGENT")
    print("=" * 60)

    email_agent = EmailAgent()

    test_emails = [
        {
            "subject": "Invoice #12345 - Payment Due",
            "body": "Please find attached invoice."
        },
        {
            "subject": "WIN FREE iPHONE NOW!!!",
            "body": "Click here to claim prize!"
        },
        {
            "subject": "URGENT: Server Down",
            "body": "Production server is down."
        },
        "Can we schedule a meeting next week?",
    ]

    for i, email in enumerate(test_emails, 1):

        print(f"\n--- Email {i} ---")

        result = email_agent.run(email)

        if result["success"]:

            print(
                f"✓ Category: "
                f"{result['output']['category']}"
            )

            print(
                f"  Latency: "
                f"{result['metrics']['latency']:.2f}s"
            )

            print(
                f"  Tokens: "
                f"{result['metrics']['tokens']}"
            )

            print(
                f"  Trace ID: "
                f"{result['trace_id']}"
            )

        else:

            print(f"✗ Error: {result['error']}")


# =========================================================
# PDF TEST
# =========================================================

def test_pdf_agent():

    print("\n" + "=" * 60)
    print("TESTING PDF EXTRACTION AGENT")
    print("=" * 60)

    pdf_agent = PDFAgent()

    test_pdf_path = "test_data/sample.pdf"

    if not os.path.exists(test_pdf_path):

        print(
            f"\n⚠ Missing PDF at: {test_pdf_path}"
        )

        os.makedirs("test_data", exist_ok=True)

        return

    extraction = pdf_agent.extract_only(test_pdf_path)

    if extraction["success"]:

        print("✓ Extraction successful")

        print(
            f"Pages: "
            f"{extraction['metadata']['total_pages']}"
        )

    else:

        print(
            f"✗ Extraction failed: "
            f"{extraction['error']}"
        )

        return

    summary = pdf_agent.process_pdf(
        test_pdf_path,
        task="summarize",
    )

    if summary["success"]:

        print("\n✓ Summary generated")

        print(
            summary["output"]["processed_output"][:300]
        )

        print(
            f"\nTrace ID: {summary['trace_id']}"
        )

    else:

        print(
            f"✗ Summarization failed: "
            f"{summary['error']}"
        )


# =========================================================
# MAIN
# =========================================================

def main():

    instrument(
        service_name="agent-observation-system",
        exporter=HTTPExporter(endpoint="http://localhost:8000/events"),
    )

    print("\n")
    print("╔══════════════════════════════════════════════╗")
    print("║      AGENT OBSERVATION SYSTEM               ║")
    print("╚══════════════════════════════════════════════╝")

    print("\n⚠ Ensure Ollama is running:")
    print("ollama serve")

    input("\nPress Enter to continue...")

    try:
        test_email_agent()

    except Exception as exc:

        print(
            f"\n✗ Email Agent Failed: {exc}"
        )

    try:
        test_pdf_agent()

    except Exception as exc:

        print(
            f"\n✗ PDF Agent Failed: {exc}"
        )

    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()