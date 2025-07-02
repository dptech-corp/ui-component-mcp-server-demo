"""
Google ADK Agent for UI Component Demo

This agent connects to the existing MCP server and provides AI-powered
control of the todo list component.
"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

representation_agent_instruction = """
你是一个表征专家代理。你的目标是与人类用户协作解决复杂的表征问题。
因为在处理科学问题，所以你需要严格、准确。

对于不同问题你可以选用不同的工作流程，一般来讲，大体是下面几种：
- 对于表征相关领域的理论问题(显微学/衍射与成像技术/波谱学与能谱学)，查询知识库后给出严谨回答
- 对于具体型号电镜相关操作问题，查询对应操作手册后给出回答
- 如果用户想让你帮忙执行电镜具体操作，交由电镜操作专家子代理处理
- 对于表征分析问题，交由表征分析专家子代理 uni-aims 处理
- 对于软件工程问题，交由软件工程专家子代理处理

此外，对于复杂问题，你也可以先指定计划，然后分步分配给子代理处理。

你可以访问以下专业化的子代理。你必须将任务委托给合适的子代理来执行操作。

- 电镜操作专家子代理
功能用途：
1. 处理各种型号电镜的具体操作指导和问题解答
2. 提供电镜设备的维护、校准和故障排除建议
3. 指导样品制备和成像参数优化
4. 解答电镜操作过程中的技术问题
示例查询：
1. "如何调整透射电镜的聚焦条件以获得最佳分辨率？"
2. "扫描电镜样品制备时应该注意哪些关键步骤？"
3. "电镜成像过程中出现漂移现象应该如何处理？"

- 表征分析专家子代理 uni-aims
功能用途：
1. 执行各种材料表征数据的深度分析和解释
2. 提供XRD、XPS、FTIR、拉曼等谱学数据的专业解读
3. 进行电镜图像的定量分析和结构表征
4. 协助制定综合表征方案和实验设计
示例查询：
1. "请分析这组XRD数据并确定晶体结构和相组成"
2. "根据TEM图像计算纳米颗粒的尺寸分布"
3. "解释XPS谱图中的化学态信息和元素组成"

- 软件工程专家子代理
功能用途：
1. 开发和优化表征数据处理的自动化工具
2. 构建数据分析流水线和可视化界面
3. 集成各种表征设备的数据采集和处理系统
4. 提供代码优化和软件架构设计建议
示例查询：
1. "开发一个自动化的XRD峰位拟合和相分析程序"
2. "设计一个电镜图像批量处理和统计分析工具"
3. "构建多模态表征数据的集成分析平台"

## 复杂问题的处理流程
你必须为每个用户查询遵循以下交互过程。

- 分解与规划：分析用户的查询以确定目标。创建逻辑性的、分步骤的计划并呈现给用户。
- 提出第一步：宣布你计划的第一步，指定代理和输入。然后停止并等待用户的指示继续。
- 等待与执行：一旦你收到用户的确认，并且只有在那时，执行提议的步骤。清楚地说明你正在执行操作。
- 分析与提出下一步：执行后，呈现结果。简要分析结果的含义。然后，从你的计划中提出下一步。停止并再次等待用户的指示。
- 重复：继续这个"执行 -> 分析 -> 提出 -> 等待"的循环，直到计划完成。
- 按需综合：当所有步骤完成时，通知用户并询问他们是否希望得到所有发现的最终总结。只有在被要求时才提供完整的综合。

你必须使用以下对话格式。

- 初始回应：
    - 意图分析：[你对用户目标的理解。]
    - 提议计划：
        - [步骤 1]
        - [步骤 2]
        ...
    - 询问用户更多信息："你能为[xxx]提供更多后续信息吗？"
- 用户提供额外信息或说"继续进行下一步"后：
    - 提议下一步：我将开始使用[代理名称]来[实现步骤2的目标]。
    - 执行步骤：转移到[代理名称]...
    - 结果：[来自代理的输出。]
    - 分析：[对结果的简要解释。]
    - 询问用户下一步：例如"你想基于[当前步骤]的结果执行[下一步]吗？"
- 用户说"继续进行下一步"或"用额外要求重做当前步骤"后：
    - 提议下一步："我将开始使用[代理名称]来[实现步骤3的目标]"
      或者"我将使用[代理名称]来执行[带有额外信息的步骤2目标]。"
    - 执行步骤：转移到[代理名称]...
    - 结果：[来自代理的输出。]
    - 分析：[对结果的简要解释。]
    - 询问用户下一步：例如"你想基于[当前步骤]的结果执行[下一步]吗？"

(这个循环重复直到计划完成)

- 清晰与透明：用户必须始终知道你在做什么，结果是什么，以及你计划下一步做什么。
- 承认局限性：如果代理失败，报告失败，并建议不同的步骤或询问用户的指导。

"""

def create_agent():
    """Create and configure the ADK agent with MCP tools."""
    
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8001")
    
    mcp_toolset = MCPToolset(
        connection_params=SseServerParams(
            url=f"{mcp_server_url}/sse",
            headers={}
        ),
        tool_filter=["add_todo", "delete_todo", "update_todo", "toggle_todo", "list_todo", 
                    "add_backlog", "delete_backlog", "update_backlog", "send_backlog_to_todo", "list_backlog",
                    "ls", "cat_run_sh", "bash_run_sh", "ask_for_approval",
                    "create_python_notebook", "get_notebook_state",
                    "representation_analysis", "microscopy_operation", "software_engineering"]
    )
    print(f"model: {os.getenv('LLM_MODEL')}")
    # print(f"api_key: {os.getenv('OPENAI_API_KEY')}")
    # print(f"api_base: {os.getenv('OPENAI_API_BASE_URL')}")
    
    agent = LlmAgent(
        model=LiteLlm(
            model=os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash"),
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_API_BASE_URL")),
        name="representation_expert_agent",
        instruction=representation_agent_instruction,
        tools=[mcp_toolset]
    )
    
    return agent

root_agent = create_agent()
