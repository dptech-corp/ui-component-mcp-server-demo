import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.adk.tools import agent_tool
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

# Add the parent directory to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from software import software_expert_desc, software_expert
from microscopy import microscopy_expert_desc, microscopy_expert
from representation_analyze import representation_analyze_expert, representation_analyze_expert_desc
from utils.prompts import return_descriptions_root,return_instructions_root
from utils.lightrag_tool import lightrag_tools
load_dotenv()

mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8001")
theory_expert_desc = return_descriptions_root(target="theory_expert")
tools = lightrag_tools
# theory_tools = [tools[2], tools[3], tools[4]]  # 显微学、波谱学、衍射学工具
theory_tools = []
theory_expert = LlmAgent(
    model=LiteLlm(
        model=os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash"),
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_API_BASE_URL")),
    name="theory_expert",
    tools=theory_tools,
    description=return_descriptions_root(target="theory_expert"),
    instruction=return_instructions_root(target="theory_expert"),
)



root_agent = theory_expert
