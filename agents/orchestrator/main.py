import asyncio
import sys
import time
import os
sys.path.insert(0, "/app")

from shared.config import MCP_URL
from shared.core.mcp_client import MCPClient
from orchestrator.graph import build_graph


async def main():
    print("⏳ Connexion au serveur MCP...")
    time.sleep(3)

    mcp_client = MCPClient(MCP_URL)
    await mcp_client.initialize()

    app = build_graph(mcp_client)

    # Lit depuis variable d'environnement
    user_input = os.getenv("USER_REQUEST", "").strip()

    if not user_input:
        print("❌ Variable USER_REQUEST manquante !")
        print("   Lance avec : docker-compose run -e USER_REQUEST='ta demande' --rm agents")
        return

    print(f"\n✅ Demande : '{user_input}'")

    result = await app.ainvoke({
        "user_request": user_input,
        "worker_output": "",
        "feedback": "",
        "iterations": 0,
        "final_output": ""
    })

    print("\n" + "="*50)
    print("🎯 RÉSULTAT FINAL :")
    print("="*50)
    print(result.get("final_output") or result.get("worker_output"))

if __name__ == "__main__":
    asyncio.run(main())