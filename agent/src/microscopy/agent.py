import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.adk.tools import agent_tool
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

from utils.prompts import return_descriptions_root,return_instructions_root
from utils.lightrag_tool import lightrag_tools
load_dotenv()

mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8001")

# TODO add pocketflow tools
microscopy_expert_mcp_toolset = MCPToolset(
    connection_params=SseServerParams(
        url=f"{mcp_server_url}/sse",
        headers={}
    ),
    tool_filter=[
        "create_python_notebook", "get_notebook_state",
        "create_file_tool", "list_files_tool"]
)
microscopy_expert_desc = return_descriptions_root(target="microscopy_expert")
tools = lightrag_tools
microscopy_tools = [tools[0], tools[1],microscopy_expert_mcp_toolset]  # TESCAN、国仪工具
microscopy_expert = LlmAgent(
    model=LiteLlm(
        model=os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash"),
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_API_BASE_URL")),
    tools=microscopy_tools,
    name="microscopy_expert",
    description=return_descriptions_root(target="microscopy_expert"),
    instruction=return_instructions_root(target="microscopy_expert")
)
root_agent = microscopy_expert
    
