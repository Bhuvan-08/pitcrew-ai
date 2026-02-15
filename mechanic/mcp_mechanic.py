import os
import subprocess
import uvicorn
from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP

# 1. Initialize FastMCP with all your tools
mcp = FastMCP("pitcrew-mechanic")

@mcp.tool()
def list_containers() -> str:
    return subprocess.check_output(["docker", "ps"], text=True)

@mcp.tool()
def container_logs(container_name: str) -> str:
    return subprocess.check_output(["docker", "logs", "--tail", "50", container_name], text=True)

@mcp.tool()
def fix_container(container_name: str) -> str:
    return subprocess.check_output(["docker", "exec", container_name, "rm", "-f", "broken.flag"], text=True)

# 2. Create the FastAPI Bridge
app = FastAPI(title="PitCrew-Bridge")

@app.api_route("/sse", methods=["GET", "POST"])
async def handle_sse(request: Request):
    print(f"🔌 SSE Connection: {request.method}")
    # In 1.26.0, the actual server instance is stored in mcp._server
    # This server object contains the handle_sse method we need.
    return await mcp._server.handle_sse(request)

@app.post("/messages")
async def handle_messages(request: Request):
    # This handles the tool calls sent by Archestra after connection
    return await mcp._server.handle_messages(request)

# --- 🚀 LAUNCH ---
if __name__ == "__main__":
    print("🚀 Starting PitCrew 1.26.0 Bridge on 0.0.0.0:8000")
    
    # We must trigger the internal server setup before we can use _server
    # This prepares the tool definitions inside the server object.
    mcp.get_fastapi_app() 
    
    uvicorn.run(app, host="0.0.0.0", port=8000)