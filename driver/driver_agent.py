import requests
import ollama

MECHANIC_URL = "http://localhost:8001"
CONTAINER_NAME = "prod-api"
HEALTH_URL = "http://localhost:5000/health"


def get_logs(container_name):
    return requests.get(
        f"{MECHANIC_URL}/containers/{container_name}/logs",
        timeout=5
    ).json()["output"]


def restart_container(container_name):
    return requests.post(
        f"{MECHANIC_URL}/containers/{container_name}/restart",
        timeout=5
    ).json()


def fix_container(container_name):
    return requests.post(
        f"{MECHANIC_URL}/containers/{container_name}/fix",
        timeout=5
    ).json()


def check_health():
    try:
        res = requests.get(HEALTH_URL, timeout=5)
        return res.json()
    except:
        return {"status": "UNREACHABLE"}



def extract_critical_logs(log_text):
    lines = log_text.split("\n")

    critical = [l for l in lines if "CRITICAL" in l]

    # send ONLY last few signals to LLM
    if critical:
        return "\n".join(critical[-3:])

    return log_text[-400:]


def diagnose_system():

    raw_logs = get_logs(CONTAINER_NAME)
    logs = extract_critical_logs(raw_logs)

    prompt = f"""
You are a production Site Reliability Engineer.

Analyze the logs below.

LOGS:
{logs}

Respond EXACTLY in this format:

SEVERITY: LOW / MEDIUM / HIGH
STATUS: HEALTHY or FAILING
CAUSE: one short sentence
ACTION: FIX or NO_ACTION

Choose ONLY one action.
Do not explain.
"""

    response = ollama.chat(
        model="phi3:mini",
        messages=[{"role": "user", "content": prompt}]
    )

    result = response['message']['content']

    print("\n🧠 Diagnosis:\n")
    print(result)

    return result

def determine_action(result_text):
    text = result_text.lower()

    if any(word in text for word in ["restart", "fix", "recover"]):
        return "FIX"

    return "NO_ACTION"


def autonomous_recovery():

    print("\n" + "="*60)
    print("🚨 INCIDENT DETECTED — PitCrew Autonomous Response")
    print("="*60)

    result = diagnose_system()

    action = determine_action(result)

    if action == "FIX":

        print("\n⚡ Agent executing recovery sequence...\n")

        print("🔧 Removing failure trigger...")
        fix_container(CONTAINER_NAME)

        print("🔄 Restarting container...")
        restart_container(CONTAINER_NAME)

        print("\n⏳ Waiting for service stabilization...\n")

        import time
        time.sleep(4)

        health = check_health()

        print("📊 Post-Recovery Health:\n")
        print(health)

        if health.get("status") == "OK":
            print("\n✅ SERVICE SUCCESSFULLY HEALED.")
        else:
            print("\n⚠️ Service still unhealthy — manual investigation recommended.")

    else:
        print("\n✅ Agent determined no action is required.")


if __name__ == "__main__":
    print("\n🔎 PitCrew Driver Agent Starting...\n")
    autonomous_recovery()
