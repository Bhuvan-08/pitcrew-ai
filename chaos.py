import subprocess
import time

CONTAINER_NAME = "prod-api"

def break_service():
    print("Waiting 2 seconds before failure...")
    time.sleep(2)

    print("🔥 Simulating production failure...")
    
    subprocess.run([
        "docker",
        "exec",
        CONTAINER_NAME,
        "touch",
        "broken.flag"
    ])

    print("✅ Service is now unhealthy.")

def fix_service():
    print("🛠️ Restoring service...")
    
    subprocess.run([
        "docker",
        "exec",
        CONTAINER_NAME,
        "rm",
        "-f",
        "broken.flag"
    ])

    print("✅ Service restored.")

if __name__ == "__main__":
    choice = input("Type 'break' or 'fix': ").strip()

    if choice == "break":
        break_service()
    elif choice == "fix":
        fix_service()
    else:
        print("Invalid option.")
