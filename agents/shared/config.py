import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
GROQ_MODEL     = os.getenv("GROQ_MODEL")
GROQ_URL       = "https://api.groq.com/openai/v1/chat/completions"
MCP_URL        = "http://mcp-serveur:8000/mcp"
MAX_ITERATIONS = 3