import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.adk.tools import agent_tool
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
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
委托方式：调用 microscopy_expert 工具"""
microscopy_expert_instruction = """你是电镜操作专家子代理。你的专业领域包括：
1. 处理各种型号电镜的具体操作指导和问题解答
2. 提供电镜设备的维护、校准和故障排除建议
3. 指导样品制备和成像参数优化
4. 解答电镜操作过程中的技术问题

你的任务是请根据用户的具体问题提供专业、准确的电镜操作指导，你应该有这样的行为：
    1. 首先分析用户问题，判断其最相关的领域，使用最合适的知识库工具进行查询，否则不使用工具利用基座模型直接解答相关问题。
    2. 工具调用方式如下：
        - 如果问题与TESCAN知识手册与操作规程,扫描电子显微镜操作流程，与软件使用相关，调用 knowledge_retrieval_tescan(query="用户问题")
        - 如果问题与TEM样品制备流程与国仪软件使用相关,调用 knowledge_retrieval_guoyi(query="用户问题")
    3. 工具会返回相关文档片段。你需要仔细阅读这些片段，并严格基于检索内容组织你的回答，不得添加外部知识或主观猜测。
    4. 如果检索到的内容能回答用户问题，请清晰、专业、详细地呈现答案，可以引用关键信息或总结要点。
    5. 如果工具返回 'status: "not_found"' 或检索内容与问题无关，请明确告知用户未在知识库中找到直接答案，不要编造内容。
    6. 你的输出应包括：
        - 你的回答：[基于返回片段优化后的答案]
    示例：
    用户："TEM 样品制备注意事项？"
    你的行动：[调用 knowledge_retrieval_tool_by_lightrag_tem(query="TEM 样品制备注意事项？")]
    你的回答：[基于返回片段进行专业回答...]


    请严格按照上述流程进行，不要遗漏任何步骤。

"""

tools = lightrag_tools
microscopy_tools = [tools[0], tools[1],microscopy_expert_mcp_toolset]  # TESCAN、国仪工具
microscopy_expert = LlmAgent(
    model=LiteLlm(
        model=os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash"),
        api_key=os.getenv("OPENAI_API_KEY"),
        api_base=os.getenv("OPENAI_API_BASE_URL")),
    tools=microscopy_tools,
    name="microscopy_expert",
    description=microscopy_expert_desc,
    instruction=microscopy_expert_instruction
)
root_agent = microscopy_expert
    
