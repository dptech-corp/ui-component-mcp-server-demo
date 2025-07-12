from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from utils.config import llm, mcp_server_url
from utils.callbacks import before_step_callback, after_step_callback
from utils.LongRunningMCPToolset import LongRunningMCPToolset
from utils.LongRunningLlmAgent import LongRunningLlmAgent

software_expert_desc = """
software_expert (软件工程专家子代理)
功能用途：
1. 开发和优化表征数据处理的自动化工具
2. 构建数据分析流水线和可视化界面
3. 使用 Python Notebook 开发脚本
4. 操作文件系统
5. 在终端执行系统命令
示例查询：
1. "开发一个自动化的XRD峰位拟合和相分析程序"
2. "设计一个电镜图像批量处理和统计分析工具"
3. "构建多模态表征数据的集成分析平台"
委托方式：调用 software_expert 工具
"""

software_expert_instruction = """你是软件工程专家子代理。你的专业领域包括：
1. 开发和优化表征数据处理的自动化工具
2. 构建数据分析流水线和可视化界面
3. 使用 Python Notebook 开发脚本
4. 操作文件系统
5. 在终端执行系统命令

你可以使用以下工具：
- create_file_tool: 创建新文件，指定文件名、路径和内容
- list_files_tool: 列出系统中的所有文件
- ls, cat_run_sh, bash_run_sh: 执行系统命令和文件操作
- create_python_notebook, get_notebook_state: 管理Python笔记本

请根据用户的软件开发需求，提供专业的代码实现、架构设计或优化建议。"""

# Software expert MCP toolset for file system and notebook tools
software_expert_mcp_toolset = LongRunningMCPToolset(
    connection_params=SseServerParams(
        url=mcp_server_url,
        headers={}
    ),
    tool_filter=["ls", "cat_run_sh", "bash_run_sh", 
                "create_python_notebook", "get_notebook_state",
                "create_file_tool", "list_files_tool"],
    tools_set_long_running=["create_python_notebook"]
)


software_expert = LongRunningLlmAgent(
    model=llm,
    name="software_expert",
    description="软件工程专家子代理，专门开发和优化表征数据处理的自动化工具、构建数据分析流水线和集成系统。",
    instruction=software_expert_instruction,
    tools=[software_expert_mcp_toolset],
    before_agent_callback=before_step_callback,
    after_agent_callback=after_step_callback
)

root_agent = software_expert