from langgraph.graph import StateGraph, END
from shared.state import State
from shared.config import MAX_ITERATIONS
from agent_worker.agent import run as worker_run
from agent_evaluator.agent import run_async as evaluator_run

def should_continue(state: State) -> str:
    if state.get("final_output"):
        return "end"
    if state.get("iterations", 0) >= MAX_ITERATIONS:
        print("⚠️  Max itérations atteint")
        return "end"
    return "worker"

def build_graph(mcp_client):
    async def worker_node(state):
        return await worker_run(state, mcp_client)

    async def evaluator_node(state):
        return await evaluator_run(state)

    graph = StateGraph(State)
    graph.add_node("agent_worker", worker_node)
    graph.add_node("agent_evaluator", evaluator_node)

    graph.set_entry_point("agent_worker")
    graph.add_edge("agent_worker", "agent_evaluator")
    graph.add_conditional_edges(
        "agent_evaluator",
        should_continue,
        {"worker": "agent_worker", "end": END}
    )

    return graph.compile()