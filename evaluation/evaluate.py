import sqlite3
import json

from pathlib import Path

from ground_truth import (
    GROUND_TRUTH_EMAILS
)

from evaluation_storage import (
    store_evaluation
)


# =========================================================
# OBSERVABILITY DATABASE
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

OBS_DB = BASE_DIR / "observability.db"


conn = sqlite3.connect(OBS_DB)

conn.row_factory = sqlite3.Row

cursor = conn.cursor()


# =========================================================
# LOAD EMAIL WORKFLOW SPANS
# =========================================================

def load_email_workflows():

    rows = cursor.execute("""

    SELECT *

    FROM traces

    WHERE event_type = 'workflow'
    AND name = 'EmailClassifier'

    ORDER BY start_ts DESC

    LIMIT 4

    """).fetchall()

    rows = list(reversed(rows))

    return [dict(r) for r in rows]


# =========================================================
# EXTRACT PREDICTED CATEGORY
# =========================================================

def extract_prediction(output_payload):

    if not output_payload:
        return "unknown"

    try:

        payload = json.loads(output_payload)

        workflow_preview = payload.get(
            "workflow_output_preview",
            ""
        )

        workflow_preview = workflow_preview.lower()

        categories = [
            "invoice",
            "spam",
            "urgent",
            "general",
            "support",
            "marketing",
            "notification",
        ]

        for category in categories:

            if category in workflow_preview:
                return category

        return workflow_preview.strip()

    except Exception:

        return "unknown"


# =========================================================
# EVALUATION
# =========================================================

def evaluate():

    workflows = load_email_workflows()

    print(
        f"\nLoaded "
        f"{len(workflows)} workflows"
    )

    total = 0
    correct = 0

    for idx, (workflow, gt) in enumerate(

        zip(
            workflows,
            GROUND_TRUTH_EMAILS
        ),

        1
    ):

        print(f"\n--- Evaluation {idx} ---")

        predicted = extract_prediction(
            workflow.get("output_payload")
        )

        expected = gt["expected"]

        is_correct = (
            predicted == expected
        )

        if is_correct:
            correct += 1

        total += 1

        print(
            f"Expected : {expected}"
        )

        print(
            f"Predicted: {predicted}"
        )

        print(
            f"Correct  : {is_correct}"
        )

        store_evaluation({

            "trace_id":
                workflow["trace_id"],

            "workflow_name":
                workflow["name"],

            "input_text":
                str(gt["input"]),

            "expected_output":
                expected,

            "actual_output":
                predicted,

            "correct":
                is_correct,

            "latency":
                workflow["latency_seconds"],

            "tokens":
                workflow["tokens"],
        })

    accuracy = (

        (correct / total) * 100

        if total > 0 else 0
    )

    print("\n====================")

    print(
        f"Accuracy: "
        f"{accuracy:.2f}%"
    )

    print("====================")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    evaluate()