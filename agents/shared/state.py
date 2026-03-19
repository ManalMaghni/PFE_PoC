from typing import TypedDict

class State(TypedDict):
    user_request: str
    worker_output: str
    feedback: str
    iterations: int
    final_output: str