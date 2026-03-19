from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
import uvicorn

# Import de tous les outils (chaque fichier enregistre ses outils sur mcp)
from tools import register_all_tools

mcp = FastMCP(
    "PFE-MCP-Server",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False
    ),
)

# On passe l'instance mcp aux tools pour qu'ils s'enregistrent dessus
register_all_tools(mcp)

if __name__ == "__main__":
    uvicorn.run(
        mcp.streamable_http_app(),
        host="0.0.0.0",
        port=8000,
    )