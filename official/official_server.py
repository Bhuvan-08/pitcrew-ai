from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import os

app = FastAPI(title="PitCrew Governance Engine")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIT_PATH = os.path.join(BASE_DIR, "audit.log")


class PolicyRequest(BaseModel):
    container: str
    action: str
    severity: str


def calculate_risk(action, severity, env="prod"):

    risk = 0

    if env == "prod":
        risk += 50

    if action.lower() == "fix":
        risk += 25

    if severity.upper() == "HIGH":
        risk += 20

    return min(risk, 100)


def get_rule(action, severity):

    if severity.upper() == "HIGH":
        return ("R-301", "High-risk production action requires approval.")

    if action.lower() == "delete":
        return ("S-201", "Destructive operations are prohibited.")

    return ("P-101", "Action permitted under governance policy.")


def write_audit_log(incident_id, risk, decision, rule_id):

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    log_line = (
        f"[{timestamp}] "
        f"[INC:{incident_id}] "
        f"[RISK:{risk}] "
        f"[RULE:{rule_id}] "
        f"{decision}"
    )

    with open(AUDIT_PATH, "a") as f:
        f.write(log_line + "\n")


@app.post("/evaluate")
def evaluate_policy(request: PolicyRequest):

    incident_id = datetime.utcnow().strftime("%H%M%S")

    severity = request.severity.upper()
    action = request.action.lower()

    risk = calculate_risk(action, severity)
    rule_id, reason = get_rule(action, severity)

    approved = risk < 70

    decision_text = "APPROVED" if approved else "BLOCKED"

    write_audit_log(
        incident_id=incident_id,
        risk=risk,
        decision=decision_text,
        rule_id=rule_id
    )

    return {
        "approved": approved,
        "risk_score": f"{risk}/100",
        "rule_id": rule_id,
        "reason": reason
    }
