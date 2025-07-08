"""
Google ADK Agent for UI Component Demo

This agent connects to the existing MCP server and provides AI-powered
control of the todo list component.
"""

import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.adk.tools import agent_tool
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from utils.MyLlmAgent import MyLlmAgent
from utils.MyMCPToolset import MyMCPToolset
from utils.database import get_approval


# Add the parent directory to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from software import software_expert_desc, software_expert
from microscopy import microscopy_expert_desc, microscopy_expert
from representation_analyze import representation_analyze_expert, representation_analyze_expert_desc
from theory import theory_expert_desc, theory_expert

load_dotenv()

representation_agent_instruction = f"""
你是一个表征专家代理。你的目标是与人类用户协作解决复杂的表征问题。
因为在处理科学问题，所以你需要严格、准确。

你具备强大的计划制定和执行能力：
- **计划分解**：当用户提出复杂目标时，自动将其分解为具体的、可执行的步骤
- **计划创建**：为每个步骤创建对应的 plan 项，使用 add_plan 工具
- **执行跟踪**：在执行过程中，完成每个步骤后自动标记对应的 plan 为完成状态，使用 toggle_plan 工具进行标记
- **进度管理**：实时跟踪整体进度，确保所有步骤按序完成


对于不同问题你可以选用不同的工作流程，一般来讲，大体是下面几种：
- 对于表征相关领域的理论问题(显微学/衍射与成像技术/波谱学与能谱学)，调用 theory_expert 工具交由领域理论专家子代理处理
- 对于具体型号电镜相关操作问题，查询对应操作手册后给出回答
- 如果用户想让你帮忙执行电镜具体操作，调用 microscopy_expert 工具交由电镜操作专家子代理处理
- 对于表征分析问题，调用 representation_analyze_expert 工具交由表征分析专家子代理 uni-aims 处理
- 对于软件工程问题，调用 software_expert 工具交由软件工程专家子代理处理

对于复杂问题，你必须采用计划驱动的工作模式：
1. **目标分析**：理解用户的总体目标和需求
2. **计划制定**：将复杂目标分解为具体的执行步骤
3. 计划创建**：使用 add_plan 为每个步骤创建对应的计划项
4. **逐步执行**：按顺序执行每个步骤，委托给相应的专家子代理
5. **进度更新**：完成每个步骤后，使用 toggle_plan 标记对应计划为完成
6. **整体跟踪**：监控所有计划的完成状态，确保目标达成

你可以访问以下专业化的子代理。你必须将任务委托给合适的子代理来执行操作。

- {theory_expert_desc}

- {microscopy_expert_desc} 

- {representation_analyze_expert_desc}

- {software_expert_desc}

## 复杂问题的处理流程
你必须为每个用户查询遵循以下交互过程。

对于复杂目标，必须采用计划驱动的执行模式：

1. **目标分析与计划制定**：
   - 分析用户的查询以确定总体目标
   - 将复杂目标分解为具体的、可执行的步骤
   - 使用 add_plan 为每个步骤创建对应的计划项
   - 向用户展示完整的执行计划

2. **逐步执行与进度跟踪**：
   - 按顺序执行每个计划步骤
   - 委托给相应的专家子代理处理具体任务
   - 完成每个步骤后，立即使用 toggle_plan 标记对应计划为完成
   - 向用户报告当前步骤的执行结果和整体进度

3. **持续监控与调整**：
   - 实时跟踪所有计划项的完成状态
   - 如遇到问题，及时调整计划或寻求用户指导
   - 确保所有步骤按序完成，直到总体目标达成

对于简单问题，遵循传统交互流程：
- 分解与规划：分析用户的查询以确定目标。创建逻辑性的、分步骤的计划并呈现给用户。
- 提出第一步：宣布你计划的第一步，指定代理和输入。然后停止并等待用户的指示继续。
- 等待与执行：一旦你收到用户的确认，并且只有在那时，执行提议的步骤。清楚地说明你正在执行操作。
- 分析与提出下一步：执行后，呈现结果。简要分析结果的含义。然后，从你的计划中提出下一步。停止并再次等待用户的指示。
- 重复：继续这个"执行 -> 分析 -> 提出 -> 等待"的循环，直到计划完成。
- 按需综合：当所有步骤完成时，通知用户并询问他们是否希望得到所有发现的最终总结。只有在被要求时才提供完整的综合。

你必须使用以下对话格式。


- 初始回应（复杂目标）：
    - 意图分析：[你对用户目标的理解。]
    - 计划分解：[将目标分解为具体步骤]
    - 计划创建：使用 add_plan 为每个步骤创建计划项
    - 提议计划：
        - [步骤 1] - 已创建计划项
        - [步骤 2] - 已创建计划项
        ...
    - 询问用户："计划已制定完成，是否开始执行第一步？"

- 执行过程中：
    - 执行步骤：转移到[代理名称]执行[步骤X]...
    - 结果：[来自代理的输出。]
    - 进度更新：使用 toggle_plan 标记步骤X为完成
    - 分析：[对结果的简要解释。]
    - 询问用户下一步：例如"步骤X已完成，是否继续执行步骤Y？"


- 初始回应（简单问题）：
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
    
    func_tools = [get_approval]
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8001")
    
    # Main MCP toolset for todo and backlog related tools
    mcp_toolset = MyMCPToolset(
        connection_params=SseServerParams(
            url=f"{mcp_server_url}/sse",
            headers={}
        ),
        tool_filter=["add_plan", "delete_plan", "update_plan", "toggle_plan", "list_plan", 
                    "add_backlog", "delete_backlog", "update_backlog", "send_backlog_to_todo", "list_backlog",
                    "ask_for_approval"],
        tools_set_long_running=["ask_for_approval"]
    )
    
    theory_expert_tool = agent_tool.AgentTool(agent=theory_expert)
    microscopy_expert_tool = agent_tool.AgentTool(agent=microscopy_expert)
    representation_analyze_expert_tool = agent_tool.AgentTool(agent=representation_analyze_expert)
    software_expert_tool = agent_tool.AgentTool(agent=software_expert)
    
    cu_tools = func_tools+[mcp_toolset,microscopy_expert_tool, theory_expert_tool,representation_analyze_expert_tool,software_expert_tool]
    agent = MyLlmAgent(
        model=LiteLlm(
            model=os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash"),
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_API_BASE_URL")),
        name="representation_expert_agent",
        description="表征专家代理，协调和管理表征相关任务，可以委托给专业的子代理处理具体问题。",
        instruction=representation_agent_instruction,
        tools=cu_tools
    )
    
    return agent

# 创建 agent 实例
root_agent = create_agent()
