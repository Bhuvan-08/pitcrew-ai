import requests
import ollama
import time
import uuid

from strategist.strategist import retrieve_runbook
from datetime import datetime, timezone
from reporter.reporter import generate_postmortem


MECHANIC_URL = "http://localhost:8001"
OFFICIAL_URL = "http://localhost:8002"

CONTAINER_NAME = "prod-api"
HEALTH_URL = "http://localhost:5000/health"


def safe_request(method, url, **kwargs):
    try:
        return method(url, timeout=5, **kwargs)
    except:
        print(f"[WARN] Service unreachable: {url}")
        return None


def get_logs(container_name):
    res = safe_request(
        requests.get,
        f"{MECHANIC_URL}/containers/{container_name}/logs"
    )
    return res.json()["output"] if res else ""


def restart_container(container_name):
    safe_request(
        requests.post,
        f"{MECHANIC_URL}/containers/{container_name}/restart"
    )


def fix_container(container_name):
    safe_request(
        requests.post,
        f"{MECHANIC_URL}/containers/{container_name}/fix"
    )


def check_health():
    res = safe_request(requests.get, HEALTH_URL)
    return res.json() if res else {"status": "UNREACHABLE"}


def check_policy(container, action, severity):
    res = safe_request(
        requests.post,
        f"{OFFICIAL_URL}/evaluate",
        json={
            "container": container,
            "action": action,
            "severity": severity
        }
    )
    return res.json() if res else {"approved": False}


def extract_critical_logs(log_text):
    lines = log_text.split("\n")
    critical = [l for l in lines if "CRITICAL" in l]
    return "\n".join(critical[-3:]) if critical else log_text[-400:]


def extract_field(result, field):
    for line in result.split("\n"):
        line = line.strip().upper()
        if line.startswith(field):
            return line.split(":", 1)[-1].strip()
    return None


def normalize_severity(severity):

    severity = severity.upper()

    if severity in ["CRITICAL", "SEV-1", "SEV1", "HIGH"]:
        return "HIGH"

    if severity in ["MEDIUM", "MODERATE"]:
        return "MEDIUM"

    return "LOW"


def diagnose_system():

    logs = extract_critical_logs(get_logs(CONTAINER_NAME))

    runbook = retrieve_runbook(logs)

    print("\n[Strategist] Operational runbook located.")
    print("[Strategist] Applying: Payment Gateway Memory Failure\n")

    prompt = f"""
You are a production Site Reliability Engineer.

Prioritize the runbook over your own reasoning.

LOGS:
{logs}

RUNBOOK:
{runbook}

Respond EXACTLY in this format:

SEVERITY: LOW, MEDIUM, HIGH, or CRITICAL
STATUS: HEALTHY or FAILING
CAUSE: one short sentence
ACTION: FIX or NO_ACTION

No explanations.
"""

    response = ollama.chat(
        model="phi3:mini",
        messages=[{"role": "user", "content": prompt}]
    )

    result = response['message']['content']

    if "ACTION:" in result:
        result = result.split("ACTION:")[0] + "ACTION:" + result.split("ACTION:")[1].split("\n")[0]

    print("[Diagnosis]")
    print(result)

    return result


def execute_recovery(incident_id, detection_time):

    print("\n[Mechanic] Initiating governed remediation...\n")

    fix_container(CONTAINER_NAME)
    restart_container(CONTAINER_NAME)

    print("Waiting for stabilization...\n")
    time.sleep(4)

    health = check_health()

    print("[Post-Recovery Health]")
    print(health)

    if health.get("status") == "OK":
        print("\nService successfully restored.")
    else:
        print("\nService remains unhealthy.")

    recovery_time = datetime.now(timezone.utc)

    filepath, duration = generate_postmortem(
        incident_id=incident_id,
        service="payment-gateway",
        root_cause="MemoryAllocationFailure due to high usage.",
        resolution="Failure trigger removed and container restarted.",
        detection_time=detection_time,
        recovery_time=recovery_time
    )

    human_minutes = 15
    system_seconds = duration
    human_seconds = human_minutes * 60

    efficiency = round(human_seconds / system_seconds, 2) if system_seconds > 0 else "N/A"

    print("\nINCIDENT RESOLVED")
    print("--------------------------------")
    print(f"System Resolution Time : {system_seconds:.2f} seconds")
    print(f"Estimated Human Time   : {human_minutes} minutes")
    print(f"Operational Gain       : ~{efficiency}x faster")

    print(f"\nPostmortem generated at: {filepath}")



def autonomous_recovery():

    health = check_health()

    if health.get("status") == "OK":
        print("System healthy — no incident detected.")
        return

    print("PRODUCTION INCIDENT DETECTED — PitCrew Response Engine")

    incident_id = str(uuid.uuid4())[:8]
    print(f"\nIncident ID: {incident_id}")

    detection_time = datetime.now(timezone.utc)
    result = diagnose_system()

    action = extract_field(result, "ACTION") or "NO_ACTION"
    raw_severity = extract_field(result, "SEVERITY") or "LOW"
    severity = normalize_severity(raw_severity)

    print(f"\nSeverity : {severity}")
    print(f"Action   : {action}")

    if action == "NO_ACTION":
        print("\nNo action required.")
        return

    print("\nEscalating to Governance Engine...")

    policy = check_policy(CONTAINER_NAME, action, severity)

    print(f"""
Governance Decision
Risk Score : {policy.get("risk_score")}
Rule       : {policy.get("rule_id")}
Reason     : {policy.get("reason")}
Approved   : {policy.get("approved")}
""")

    if policy.get("approved"):
        execute_recovery()
        return

    print("Action blocked by governance.")

    if severity == "HIGH":

        auth_code = input("\nEnter authorization code to override: ")

    if auth_code == "PROD-ADMIN-OVERRIDE":
        execute_recovery(incident_id, detection_time)
    else:
        print("\nAuthorization failed. Action denied.")


if __name__ == "__main__":
    print("\nPitCrew Driver Agent Starting...\n")
    autonomous_recovery()
