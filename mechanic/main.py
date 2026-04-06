import subprocess
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="PitCrew Mechanic API")

def run_docker(cmd_list):
    """Executes a Docker command and returns the raw output or exact error."""
    try:
        # capture_output=True grabs both the success text and the error text
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        
        # If the command failed, return the exact reason (e.g., "Permission Denied")
        if result.returncode != 0:
            return f"Docker Command Failed: {result.stderr.strip()}"
        
        return result.stdout.strip()
    except Exception as e:
        return f"System Error: {str(e)}"

# 🔌 API Endpoints
@app.get("/containers")
def list_containers():
    return run_docker(["docker", "ps"])

@app.get("/containers/{container_name}/logs")
def get_logs(container_name: str):
    return run_docker(["docker", "logs", "--tail", "50", container_name])

@app.post("/containers/{container_name}/fix")
def fix_container(container_name: str):
    return run_docker(["docker", "exec", container_name, "rm", "-f", "broken.flag"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)