from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from utils.config import llm, mcp_server_url
from utils.callbacks import before_step_callback, after_step_callback

# TODO add pocketflow tools
microscopy_expert_mcp_toolset = MCPToolset(
    connection_params=SseServerParams(
        url=mcp_server_url,
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

def scan_sample():
    print("666666666666666666666666666 scan_sample")
    return "./scan_sample/scanned_image_001.png"


  # TESCAN、国仪工具
microscopy_expert = LlmAgent(
    model=llm,
    # tools=[microscopy_expert_mcp_toolset],
    name="microscopy_expert",
    tools=[scan_sample],
    description=microscopy_expert_desc,
    instruction=microscopy_expert_instruction,
    before_agent_callback=before_step_callback,
    after_agent_callback=after_step_callback
)

root_agent = microscopy_expert
