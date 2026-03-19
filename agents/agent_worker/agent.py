from shared.state import State
from shared.core.react_loop import run_react_loop
SYSTEM_PROMPT = """You are a strict tool executor.

AVAILABLE TOOLS AND THEIR LIMITS:
- scaffold_project : creates project structure. ONLY supports types: 'fastapi', 'react', 'fullstack'
- write_file_safe  : writes a single file to /workspace
- validate_code_syntax : validates Python or JS syntax
- generate_dockerfile : generates Dockerfile for a project
- run_tests_in_sandbox : runs pytest tests
- extract_api_contract : extracts API routes from FastAPI file
- dependency_resolver : scans project and generates requirements.txt

RULES:
- Call ONLY ONE tool per response
- If the request cannot be fulfilled by any available tool, say exactly why
- Do NOT invent capabilities that don't exist
- Do NOT use 'fastapi' type when user asks for something else (kafka, django, flask...)
- If unsure which tool to use, explain the limitation instead of guessing"""

async def run(state: State, mcp_client) -> State:
    print(f"\n🔧 Agent Worker — itération {state.get('iterations', 0) + 1}")

    request = state["user_request"]
    if state.get("feedback"):
        request += f"\n\nFeedback: {state['feedback']}\nPlease fix and complete the task."

    output = await run_react_loop(
        system_prompt=SYSTEM_PROMPT,
        user_message=request,
        mcp_client=mcp_client
    )

    print(f"✅ Output : {output[:200]}...")
    return {
        **state,
        "worker_output": output,
        "iterations": state.get("iterations", 0) + 1
    }