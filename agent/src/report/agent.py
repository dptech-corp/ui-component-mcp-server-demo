from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from utils.config import llm, mcp_server_url
from utils.callbacks import before_step_callback, after_step_callback

report_expert_desc = """
report_expert (报告专家子代理)
功能用途：
1. 生成报告
示例查询：
1. "生成一个关于镍铬合金的报告"
委托方式：调用 report_expert 工具
"""

report_expert_instruction = """你是报告专家子代理。你的专业领域包括：
1. 生成报告
"""

# Software expert MCP toolset for file system and notebook tools
report_expert_mcp_toolset = MCPToolset(
    connection_params=SseServerParams(
        url=mcp_server_url,
        headers={}
    ),
    tool_filter=["ls", "cat_run_sh", "bash_run_sh"]
)


report_expert = LlmAgent(
    model=llm,
    name="report_expert",
    description="报告专家子代理，专门开发和优化表征数据处理的自动化工具、构建数据分析流水线和集成系统。",
    instruction=report_expert_instruction,
    tools=[report_expert_mcp_toolset],
    before_agent_callback=before_step_callback,
    after_agent_callback=after_step_callback
)

root_agent = report_expert