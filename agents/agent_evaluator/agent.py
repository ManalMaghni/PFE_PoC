import asyncio
from shared.state import State
from shared.core.groq_client import call_groq

SYSTEM_PROMPT = """You are a strict task evaluator.
Given the user request and the worker output, decide if the task is fully complete.

Reply in this exact format:
STATUS: complete
or
STATUS: incomplete
FEEDBACK: what is missing or wrong"""

async def run_async(state: State) -> State:
    print(f"\n⚖️  Agent Evaluator — évalue...")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""User request: {state['user_request']}

Worker output: {state['worker_output']}

Is the task complete?"""}
    ]

    response = await call_groq(messages)
    evaluation = response.get("content", "").strip()
    print(f"⚖️  Evaluation : {evaluation[:200]}")

    if "STATUS: complete" in evaluation:
        return {**state, "feedback": "", "final_output": state["worker_output"]}

    feedback = evaluation.split("FEEDBACK:")[1].strip() if "FEEDBACK:" in evaluation else ""
    return {**state, "feedback": feedback, "final_output": ""}

def run(state: State) -> State:
    return asyncio.run(run_async(state))