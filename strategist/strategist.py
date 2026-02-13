import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.dirname(BASE_DIR)

RUNBOOK_PATH = os.path.join(
    PROJECT_ROOT,
    "runbooks",
    "payment_gateway.md"
)


def retrieve_runbook(log_text):

    if "MemoryAllocationFailure" in log_text:

        if os.path.exists(RUNBOOK_PATH):
            with open(RUNBOOK_PATH, "r") as f:
                return f.read()

        return "Runbook file missing."

    return "No runbook found."
