from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
import os

load_dotenv()

mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8001")

llm = LiteLlm(
    model=os.getenv("LLM_MODEL", "gemini/gemini-2.0-flash"),
    api_key=os.getenv("OPENAI_API_KEY"),
    api_base=os.getenv("OPENAI_API_BASE_URL")
)
