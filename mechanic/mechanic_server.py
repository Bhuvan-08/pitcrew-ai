import os
import subprocess
import requests
import uvicorn
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP

# 1. Initialize FastMCP
mcp = FastMCP("pitcrew-mechanic")

# 2. Configuration
# Note: Since the mechanic is in a container, localhost refers to itself. 
# Use the Docker service name for the official policy evaluator.
OFFICIAL_URL = os.getenv("OFFICIAL_URL", "http://official-evaluator:8002")

# --- 🛠️ DOCKER HELPER ---
def run_docker_command(command: list[str]) -> str:
    """Runs a docker CLI command and returns output as text."""
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip() or result.stderr.strip()

# --- 🛠️ TOOLS (Merged from your code) ---

@mcp.tool()
def list_containers() -> str:
    """Lists all running containers."""
    return run_docker_command(["docker", "ps"])

@mcp.tool()
def container_status(container_name: str) -> str:
    """Gets detailed status of a specific container."""
    return run_docker_command(["docker", "inspect", container_name])

@mcp.tool()
def container_logs(container_name: str) -> str:
    """Fetches recent logs (last 50 lines) from a container."""
    return run_docker_command(["docker", "logs", "--tail", "50", container_name])

@mcp.tool()
def restart_container(container_name: str) -> str:
    """Restarts a container safely."""
    return f"Result: {run_docker_command(['docker', 'restart', container_name])}"

@mcp.tool()
def fix_container(container_name: str) -> str:
    """Removes the chaos flag (broken.flag) to restore service."""
    return f"Result: {run_docker_command(['docker', 'exec', container_name, 'rm', '-f', 'broken.flag'])}"

@mcp.tool()
def check_policy(container: str, action: str, severity: str) -> dict:
    """Evaluates an action against the official policy."""
    try:
        response = requests.post(
            f"{OFFICIAL_URL}/evaluate",
            json={"container": container, "action": action, "severity": severity},
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": f"Policy check failed: {str(e)}"}

# --- ☢️ DEEP NETWORK PATCH & MULTI-METHOD ROUTE ---

if __name__ == "__main__":
    print("🔓 PitCrew: Applying DEEP Uvicorn Config Patch...")

    # Force Uvicorn to use 0.0.0.0 regardless of library defaults
    original_config_init = uvicorn.Config.__init__
    def patched_config_init(self, *args, **kwargs):
        kwargs['host'] = "0.0.0.0"
        kwargs['port'] = 8000
        original_config_init(self, *args, **kwargs)
    uvicorn.Config.__init__ = patched_config_init

    # Access the internal FastAPI app to add custom route handling
    app = mcp._fastapi_app

    # FIX for the '405 Method Not Allowed'
    # This explicitly allows POST requests to the /sse endpoint
    @app.api_route("/sse", methods=["GET", "POST"])
    async def sse_handler(request: Request):
        print(f"🔌 Connection via {request.method} to /sse")
        from mcp.server.fastmcp import SSEHandler
        handler = SSEHandler(mcp)
        return await handler.handle(request)

    print("🚀 Starting Server with Dual-Method Support...")
    mcp.run(transport="sse")