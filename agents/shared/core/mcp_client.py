import httpx
import json

class MCPClient:
    def __init__(self, url: str):
        self.url = url
        self.tools = []
        self._session_id = None

    def _base_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        return headers

    def _parse_response(self, response: httpx.Response) -> dict:
        """Parse JSON ou SSE selon le content-type."""
        content_type = response.headers.get("content-type", "")

        if "text/event-stream" in content_type:
            # Parse SSE : cherche la ligne "data: {...}"
            for line in response.text.splitlines():
                if line.startswith("data:"):
                    payload = line[5:].strip()
                    if payload and payload != "[DONE]":
                        return json.loads(payload)
            return {}
        else:
            if response.text.strip():
                return response.json()
            return {}

    async def initialize(self):
        async with httpx.AsyncClient(timeout=30) as client:

            # 1. Initialize
            init_resp = await client.post(self.url, json={
                "jsonrpc": "2.0", "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "agents", "version": "1.0"}
                }
            }, headers=self._base_headers())

            self._session_id = init_resp.headers.get("mcp-session-id")
            print(f"🔌 Session ID: {self._session_id}")

            # 2. Notification initialized
            await client.post(self.url, json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }, headers=self._base_headers())

            # 3. Liste des tools
            tools_resp = await client.post(self.url, json={
                "jsonrpc": "2.0", "id": 2,
                "method": "tools/list",
                "params": {}
            }, headers=self._base_headers())

            print(f"📋 Content-Type: {tools_resp.headers.get('content-type')}")
            print(f"📋 Body raw: {tools_resp.text[:300]}")

            data = self._parse_response(tools_resp)

            if "result" in data:
                self.tools = data["result"]["tools"]
            elif "tools" in data:
                self.tools = data["tools"]
            else:
                raise ValueError(f"Format inattendu: {data}")

            print(f"✅ {len(self.tools)} tools disponibles")
            return self.tools

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(self.url, json={
                "jsonrpc": "2.0", "id": 3,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments}
            }, headers=self._base_headers())

            data = self._parse_response(response)

            if "error" in data:
                return f"❌ Erreur tool {tool_name}: {data['error']['message']}"

            content = data["result"]["content"]
            if isinstance(content, list):
                return "\n".join(c.get("text", "") for c in content)
            return str(content)

    def get_tools_for_groq(self) -> list:
        return [{
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("inputSchema", {"type": "object", "properties": {}})
            }
        } for t in self.tools]