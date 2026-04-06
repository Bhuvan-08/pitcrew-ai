import json
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv

from strategist.knowledge_base import query_runbooks

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(os.path.dirname(current_dir), '.env')
load_dotenv(dotenv_path=env_path, override=True) 

MECHANIC_URL = "http://localhost:8000"

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY") 
)

# ==========================================
# 1. TOOL SCHEMA DEFINITIONS (The VIP List)
# ==========================================
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_containers",
            "description": "Lists all running Docker containers and their status."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_container_logs",
            "description": "Fetches recent logs for a specific container to diagnose errors.",
            "parameters": {
                "type": "object",
                "properties": {"container_name": {"type": "string"}},
                "required": ["container_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_runbooks",
            "description": "Searches the internal SRE knowledge base for approved fixes.",
            "parameters": {
                "type": "object",
                "properties": {"search_query": {"type": "string"}},
                "required": ["search_query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fix_container",
            "description": "Removes the chaos flag from a container to restore service.",
            "parameters": {
                "type": "object",
                "properties": {"container_name": {"type": "string"}},
                "required": ["container_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_container_stats",
            "description": "Fetches live CPU and Memory telemetry for a container. Use this if logs do not show obvious errors.",
            "parameters": {
                "type": "object",
                "properties": {"container_name": {"type": "string"}},
                "required": ["container_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restart_container",
            "description": "Restarts a container to mitigate 100% CPU exhaustion or memory leaks.",
            "parameters": {
                "type": "object",
                "properties": {"container_name": {"type": "string"}},
                "required": ["container_name"]
            }
        }
    }
]

# ==========================================
# 2. TOOL IMPLEMENTATIONS (Business Logic)
# ==========================================
def tool_list_containers(kwargs):
    return requests.get(f"{MECHANIC_URL}/containers").text

def tool_get_container_logs(kwargs):
    param = list(kwargs.values())[0] if kwargs else ""
    return requests.get(f"{MECHANIC_URL}/containers/{param}/logs").text

def tool_search_runbooks(kwargs):
    param = list(kwargs.values())[0] if kwargs else ""
    return query_runbooks(param)

def tool_fix_container(kwargs):
    param = list(kwargs.values())[0] if kwargs else ""
    return requests.post(f"{MECHANIC_URL}/containers/{param}/fix").text

def tool_get_container_stats(kwargs):
    param = list(kwargs.values())[0] if kwargs else ""
    return requests.get(f"{MECHANIC_URL}/containers/{param}/stats").text

def tool_restart_container(kwargs):
    param = list(kwargs.values())[0] if kwargs else ""
    return requests.post(f"{MECHANIC_URL}/containers/{param}/restart").text

# ==========================================
# 3. DYNAMIC REGISTRY (The Routing Matrix)
# ==========================================
TOOL_REGISTRY = {
    "list_containers": tool_list_containers,
    "get_container_logs": tool_get_container_logs,
    "describe_container": tool_get_container_logs, # Alias safeguard
    "check_logs": tool_get_container_logs,         # Alias safeguard
    "search_runbooks": tool_search_runbooks,
    "fix_container": tool_fix_container,
    "get_container_stats": tool_get_container_stats,
    "restart_container": tool_restart_container
}

# ==========================================
# 4. THE ROUTER
# ==========================================
def execute_tool(func_name, kwargs):
    """Dynamically routes the LLM's tool request using OCP principles."""
    try:
        if func_name in TOOL_REGISTRY:
            return TOOL_REGISTRY[func_name](kwargs)
        else:
            return f"System Error: Tool '{func_name}' is not registered in the system."
    except Exception as e:
        return f"System Error executing '{func_name}': {str(e)}"

# ==========================================
# 5. PARSERS & AGENT LOOP
# ==========================================
def extract_first_json(text):
    """A foolproof stack-based parser to extract perfectly nested JSON."""
    depth = 0
    start = -1
    for i, char in enumerate(text):
        if char == '{':
            if depth == 0:
                start = i
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0 and start != -1:
                return text[start:i+1]
    return None

def run_agent(user_message, message_history):
    """The Ultimate Autonomous ReAct loop with System Rejections & Chain-of-Thought."""
    
    messages = [
        {
            "role": "system", 
            "content": (
                "You are the PitCrew Chief, an autonomous SRE agent. "
                "Your mission is to diagnose infrastructure alerts and execute mitigations to restore service.\n\n"
                
                "YOUR TOOLKIT:\n"
                "- 'list_containers': Audit the fleet if a service is missing or down.\n"
                "- 'get_container_logs': Investigate application crashes or text errors.\n"
                "- 'get_container_stats': Investigate performance issues (High CPU/Memory).\n"
                "- 'search_runbooks': Query the SRE knowledge base for mitigation policies.\n"
                "- 'fix_container' / 'restart_container': Execute mitigations.\n\n"
                
                "CRITICAL CHAIN-OF-THOUGHT RULE: You must NEVER guess the state of the infrastructure. "
                "You must explicitly reason about your next step based on the facts provided by your tools.\n"
                "Unless the incident is 100% resolved via a successful tool execution, your output MUST be formatted EXACTLY like this:\n"
                "THOUGHT: [Write 1 sentence explaining what you are checking and why]\n"
                '{"function": "tool_name", "parameters": {"param_name": "value"}}\n\n'
                
                "Only output normal conversational text WITHOUT JSON when you have definitively solved the problem."
            )
        }
    ]
    messages.extend(message_history)
    messages.append({"role": "user", "content": user_message})

    print(f"\n🚀 --- NEW AGENT MISSION TRIGGERED ---")

    for step in range(8):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        response_msg = response.choices[0].message

        # 🟢 PATH 1: NATIVE TOOL CALLING
        if response_msg.tool_calls:
            messages.append(response_msg)
            for tool_call in response_msg.tool_calls:
                func_name = tool_call.function.name
                
                print(f"🧠 [STEP {step + 1}] NATIVE TOOL INITIATED -> {func_name}")
                
                kwargs = json.loads(tool_call.function.arguments)
                tool_result = execute_tool(func_name, kwargs)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": str(tool_result)
                })
            continue 

        # 🪂 PATH 2: THE BULLETPROOF STACK PARSER & HALLUCINATION CHECK
        elif response_msg.content:
            text_content = response_msg.content.strip()
            
            print(f"🗣️ [STEP {step + 1}] LLM SPOKE: {text_content[:150]}...")
            
            tool_executed = False
            
            try:
                first_json_string = extract_first_json(text_content)
                
                if first_json_string:
                    parsed = json.loads(first_json_string)

                    if isinstance(parsed, dict):
                        func_name = parsed.get("name") or parsed.get("function") or parsed.get("tool")
                        
                        if func_name:
                            print(f"🧠 [STEP {step + 1}] JSON TOOL EXTRACTED -> {func_name}")
                            
                            kwargs = parsed.get("parameters", {})
                            if not kwargs:
                                kwargs = {k: v for k, v in parsed.items() if k not in ["name", "function", "tool", "type"]}

                            tool_result = execute_tool(func_name, kwargs)
                            
                            messages.append({"role": "assistant", "content": text_content})
                            messages.append({
                                "role": "user", 
                                "content": f"SYSTEM LOG: Tool '{func_name}' executed. Result: {tool_result}. Now evaluate the result and take your next step."
                            })
                            tool_executed = True
                            
            except Exception:
                pass

            if tool_executed:
                continue

            # 🛑 THE SLAP ON THE WRIST
            if step == 0:
                print(f"⚠️ [SYSTEM INTERCEPT]: AI tried to skip work. Forcing tool usage.")
                messages.append({"role": "assistant", "content": text_content})
                messages.append({
                    "role": "user", 
                    "content": "SYSTEM REJECTION: You just hallucinated. You did not use any tools to verify the system state. You MUST use a tool (like list_containers, get_container_stats, or get_container_logs) before you reply to the user!"
                })
                continue 

            return text_content

    return "Error: Agent reached maximum autonomous steps without finishing."