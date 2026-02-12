from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="PitCrew Policy Engine")


class PolicyRequest(BaseModel):
    container: str
    action: str
    severity: str



@app.post("/evaluate")
def evaluate_policy(request: PolicyRequest):

    action = request.action.lower()
    severity = request.severity.lower()

    # Hardcoded governance rules
    if action == "fix":

        if severity == "high":
            return {
                "approved": False,
                "reason": "High severity action requires manual approval."
            }

        return {
            "approved": True,
            "reason": "Action permitted under current policy."
        }

    return {
        "approved": False,
        "reason": "Action not recognized by policy engine."
    }
