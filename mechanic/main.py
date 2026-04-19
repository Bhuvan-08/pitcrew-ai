import docker
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="PitCrew Mechanic API (God Mode)")

# Initialize the official Docker SDK Client
try:
    client = docker.from_env()
except Exception as e:
    print(f"Failed to connect to Docker daemon: {e}")

@app.get("/containers")
def list_containers():
    """Dynamically lists all containers on the host machine."""
    try:
        containers = client.containers.list(all=True)
        return "\n".join([f"{c.short_id} - {c.name} - {c.status}" for c in containers])
    except Exception as e:
        return f"System Error: {str(e)}"

@app.get("/containers/{container_name}/logs")
def get_logs(container_name: str):
    try:
        container = client.containers.get(container_name)
        return container.logs(tail=50).decode('utf-8')
    except docker.errors.NotFound:
        return f"Error: Container '{container_name}' not found."
    except Exception as e:
        return f"System Error: {str(e)}"

@app.get("/containers/{container_name}/stats")
def get_stats(container_name: str):
    try:
        container = client.containers.get(container_name)
        stats = container.stats(stream=False)
        
        # Calculate raw CPU percentage from Docker SDK stats dictionary
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
        cpu_percent = 0.0
        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage'].get('percpu_usage', [1])) * 100.0
            
        mem_usage = stats['memory_stats'].get('usage', 0) / (1024 * 1024)
        mem_limit = stats['memory_stats'].get('limit', 1) / (1024 * 1024)
        
        return f"CPU: {cpu_percent:.2f}% | MEM: {mem_usage:.2f}MB / {mem_limit:.2f}MB"
    except Exception as e:
        return f"System Error getting stats: {str(e)}"

@app.post("/containers/{container_name}/restart")
def restart_container(container_name: str):
    try:
        container = client.containers.get(container_name)
        container.restart()
        return f"SUCCESS: {container_name} has been gracefully restarted."
    except Exception as e:
        return f"System Error restarting container: {str(e)}"

@app.post("/containers/{container_name}/fix")
def fix_container(container_name: str):
    """Executes the specific bash fix for the chaos flag."""
    try:
        container = client.containers.get(container_name)
        # 🚨 THE FIX: Removed '-f'. Now it will actually fail and return an error if the file is missing!
        exit_code, output = container.exec_run("rm broken.flag")
        if exit_code != 0:
            return f"Failed to fix: {output.decode('utf-8')}"
        return f"SUCCESS: Removed broken.flag from {container_name}."
    except Exception as e:
        return f"System Error: {str(e)}"

@app.get("/containers/{container_name}/disk")
def check_disk_space(container_name: str):
    """Executes 'df -h' to check for ephemeral storage exhaustion."""
    try:
        container = client.containers.get(container_name)
        exit_code, output = container.exec_run("df -h")
        if exit_code != 0:
            return f"Failed to check disk: {output.decode('utf-8')}"
        return output.decode('utf-8')
    except Exception as e:
        return f"System Error: {str(e)}"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)