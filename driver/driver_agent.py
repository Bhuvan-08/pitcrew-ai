import requests
import ollama
import time
import uuid

MECHANIC_URL = "http://localhost:8001"
OFFICIAL_URL = "http://localhost:8002"

CONTAINER_NAME = "prod-api"
HEALTH_URL = "http://localhost:5000/health"


def safe_request(method, url, **kwargs):
    try:
        return method(url, timeout=5, **kwargs)
    except Exception as e:
        print(f"\n⚠️ Service unreachable: {url}")
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

        if field == "ACTION" and line.startswith("ACTION"):
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

    prompt = f"""
You are a production Site Reliability Engineer.

Analyze the logs below.

LOGS:
{logs}

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

    # truncate anything after ACTION
    if "ACTION:" in result:
        result = result.split("ACTION:")[0] + "ACTION:" + result.split("ACTION:")[1].split("\n")[0]

    print("\n🧠 Diagnosis:\n")
    print(result)

    return result


def execute_recovery():

    print("\n⚙️ Initiating governed remediation...\n")

    fix_container(CONTAINER_NAME)
    restart_container(CONTAINER_NAME)

    print("⏳ Waiting for stabilization...\n")
    time.sleep(4)

    health = check_health()

    print("📊 Post-Recovery Health:\n", health)

    if health.get("status") == "OK":
        print("\n✅ SERVICE SUCCESSFULLY HEALED.")
    else:
        print("\n⚠️ Service still unhealthy.")


def autonomous_recovery():

    print("\n" + "="*70)
    print("🚨 PRODUCTION INCIDENT DETECTED — PitCrew Response Engine")
    print("="*70)

    incident_id = str(uuid.uuid4())[:8]
    print(f"\n🧾 Incident ID: {incident_id}")

    health = check_health()

    if health.get("status") == "OK":
        print("\n✅ System healthy — no incident detected.")
        return

    print("\n⚠️ Service health degraded — initiating diagnosis...\n")

    result = diagnose_system()


    action = extract_field(result, "ACTION") or "NO_ACTION"
    raw_severity = extract_field(result, "SEVERITY") or "LOW"
    severity = normalize_severity(raw_severity)

    print(f"\n📊 Severity Level: {severity}")
    print(f"⚙️ Proposed Action: {action}")

    if action == "NO_ACTION":
        print("\n✅ No action required.")
        return

    print("\n🛡️ Escalating to Policy Engine...")

    policy = check_policy(CONTAINER_NAME, action, severity)

    print(f"""
    🛡️ Governance Decision

    Risk Score : {policy.get("risk_score")}
    Rule       : {policy.get("rule_id")}
    Reason     : {policy.get("reason")}
    Approved   : {policy.get("approved")}
    """)


    if policy.get("approved"):
        execute_recovery()
        return

    print("\n🚫 Action blocked by policy.")

    if severity == "HIGH":

        time.sleep(1)

        user_input = input(
            "\n🔥 HIGH severity incident. Approve manual override? (y/n): "
        )

        if user_input.lower() == "y":
            execute_recovery()
        else:
            print("\n🛑 Operator denied action.")


if __name__ == "__main__":
    print("\n🔎 PitCrew Driver Agent Starting...\n")
    autonomous_recovery()
