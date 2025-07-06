import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.adk.tools import agent_tool
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8001")

microscopy_expert_desc = """microscopy_expert (电镜操作专家子代理)
功能用途：
1. 处理各种型号电镜的具体操作指导和问题解答
2. 提供电镜设备的维护、校准和故障排除建议
3. 指导样品制备和成像参数优化
4. 解答电镜操作过程中的技术问题
示例查询：
1. "如何调整透射电镜的聚焦条件以获得最佳分辨率？"
2. "扫描电镜样品制备时应该注意哪些关键步骤？"
3. "电镜成像过程中出现漂移现象应该如何处理？"
委托方式：调用 microscopy_expert 工具
"""

microscopy_expert_instruction = """电镜操作专家子代理，专门处理各种型号电镜的具体操作指导、设备维护、样品制备和成像参数优化等问题。",
你是电镜操作专家子代理。你的专业领域包括：
1. 处理各种型号电镜的具体操作指导和问题解答
2. 提供电镜设备的维护、校准和故障排除建议
3. 指导样品制备和成像参数优化
4. 解答电镜操作过程中的技术问题

请根据用户的具体问题提供专业、准确的电镜操作指导
"""

microscopy_expert_mcp_toolset = MCPToolset()
    
microscopy_expert = LlmAgent(
    model=LiteLlm(
        model=os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash"),
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_API_BASE_URL")),
    name="microscopy_expert",
    description="电镜操作专家子代理，专门处理各种型号电镜的具体操作指导、设备维护、样品制备和成像参数优化等问题。",
    instruction=microscopy_expert_instruction,
    tools=[microscopy_expert_mcp_toolset]
)