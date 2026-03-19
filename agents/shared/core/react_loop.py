import json
from shared.core.groq_client import call_groq

async def run_react_loop(system_prompt: str, user_message: str, mcp_client, max_steps: int = 1) -> str:
    tools = mcp_client.get_tools_for_groq()

    print(f"  📨 user_message reçu : '{user_message[:100]}'")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_message}
    ]

    for step in range(max_steps):
        print(f"  🔄 ReAct step {step + 1}")
        response = await call_groq(messages, tools=tools)

        # Pas de tool call → retourne le texte directement
        if not response.get("tool_calls"):
            return response.get("content") or "⚠️ Aucune action effectuée"

        # Un seul tool call
        tool_call = response["tool_calls"][0]

        tool_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        print(f"  🔧 Tool : {tool_name}({arguments})")

        result = await mcp_client.call_tool(tool_name, arguments)
        print(f"  📤 Résultat : {result[:150]}...")

        return result

    return "⚠️ Max steps atteint"