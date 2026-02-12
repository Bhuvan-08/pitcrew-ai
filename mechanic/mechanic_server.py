from fastapi import FastAPI
import subprocess
import requests

OFFICIAL_URL = "http://localhost:8002"

app = FastAPI(title="PitCrew Mechanic MCP")


def run_docker_command(command: list[str]) -> str:
    """
    Runs a docker CLI command and returns output as text.
    """
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )
    return result.stdout.strip() or result.stderr.strip()

def check_policy(container, action, severity):
    return requests.post(
        f"{OFFICIAL_URL}/evaluate",
        json={
            "container": container,
            "action": action,
            "severity": severity
        },
        timeout=5
    ).json()

@app.get("/containers")
def list_containers():
    """
    Lists all running containers.
    """
    output = run_docker_command(["docker", "ps"])
    return {
        "tool": "list_containers",
        "output": output
    }


@app.get("/containers/{container_name}/status")
def container_status(container_name: str):
    """
    Gets detailed status of a specific container.
    """
    output = run_docker_command([
        "docker", "inspect", container_name
    ])
    return {
        "tool": "get_container_status",
        "container": container_name,
        "output": output
    }


@app.get("/containers/{container_name}/logs")
def container_logs(container_name: str):
    """
    Fetches recent logs from a container.
    """
    output = run_docker_command([
        "docker", "logs", "--tail", "50", container_name
    ])
    return {
        "tool": "get_container_logs",
        "container": container_name,
        "output": output
    }

@app.post("/containers/{container_name}/restart")
def restart_container(container_name: str):
    """
    Restarts a container safely.
    """
    output = run_docker_command([
        "docker", "restart", container_name
    ])

    return {
        "tool": "restart_container",
        "container": container_name,
        "result": output
    }

@app.post("/containers/{container_name}/fix")
def fix_container(container_name: str):
    """
    Removes the chaos flag to restore service.
    """
    output = run_docker_command([
        "docker", "exec", container_name,
        "rm", "-f", "broken.flag"
    ])

    return {
        "tool": "fix_container",
        "container": container_name,
        "result": output
    }
