import os
import sys
# import asyncio
from google.adk.agents import LlmAgent
from utils.config import llm, mcp_server_url
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from dotenv import load_dotenv

# Add the parent directory to sys.path to allow absolute imports
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from representation.agents.planner import planner
# from representation.agents.plan_runner import plan_runner
# from representation.agents.step_runner import step_runner

from utils.config import llm, mcp_server_url
from software import software_expert_desc, software_expert
from microscopy import microscopy_expert_desc, microscopy_expert
from representation_analyze import representation_analyze_expert, representation_analyze_expert_desc
from theory import theory_expert_desc, theory_expert
from report import report_expert_desc, report_expert


load_dotenv()

representation_agent_instruction = f"""
## 概述
你是一个表征专家代理。你的目标是与人类用户协作解决复杂的表征问题。
因为在处理科学问题，所以你需要严格、准确。
在调用子代理时，一次只能调用一个，等上一个子代理完成后再调用下一个子代理。

你具备强大的计划制定和执行能力：
- **计划创建**：通过 planner 子代理创建计划
- **执行跟踪**：对于拆接出的任务，调用对应的子代理来执行每个计划项的详细步骤
- **step by step**：每完成一步后，必须等待用户确认后，再开始执行下一步
- **计划更新**：通过 planner 子代理更新计划
- **进度管理**：实时跟踪整体进度，确保所有步骤按序完成


## 任务规约
你是一个严谨的面相科研的专家代理，你必须:
- **计划优先**：在没有明确计划的时候，你必须先创建计划(planner)，待用户确认后，再开始执行计划(对应的 expert)。
- **计划更新**：当计划更新后，重新调用 planner 循环完成所有计划项
- **计划执行**：使用对应的 expert 来执行每个计划项的详细步骤
- 清晰与透明：用户必须始终知道你在做什么，结果是什么，以及你计划下一步做什么。
- 承认局限性：如果代理失败，报告失败，并建议不同的步骤或询问用户的指导。

## IMPORTANT
**PLAN FIRST, THEN EXECUTE STEP BY STEP, ASK FOR HUMAN CONFIRMATION BEFORE EXECUTE NEXT STEP**


## 常见任务划分
对于不同问题你可以选用不同的工作流程，一般来讲，大体是下面几种：
- 对于表征相关领域的理论问题(显微学/衍射与成像技术/波谱学与能谱学)，调用 theory_expert 工具交由领域理论专家子代理处理
- 对于具体型号电镜相关操作问题，查询对应操作手册后给出回答
- 如果用户想让你帮忙执行电镜具体操作，调用 microscopy_expert 工具交由电镜操作专家子代理处理
- 对于表征分析问题，调用 representation_analyze_expert 工具交由表征分析专家子代理 uni-aims 处理
- 对于软件工程问题，调用 software_expert 工具交由软件工程专家子代理处理
- 如果需要人工确认，调用 ask_for_approval 工具交由人工确认

## 子系统能力介绍
你可以访问以下专业化的子代理。你必须将任务委托给合适的子代理来执行操作。

- {theory_expert_desc}

- {microscopy_expert_desc} 

- {representation_analyze_expert_desc}

- {software_expert_desc}

- {report_expert_desc}
"""

def before_agent_callback(callback_context: CallbackContext):
    if not callback_context.state.get("plan_mode"):
        callback_context.state["plan_mode"] = True
    


def create_agent():
    """Create and configure the ADK agent with MCP tools."""
    
    mcp_toolset = MCPToolset(
        connection_params=SseServerParams(
            url=mcp_server_url,
            headers={}
        ),
        # tool_filter=["add_plan", "delete_plan", "update_plan", "toggle_plan", "list_plan"]
    )

    # TODO 为什么工具返回的结果在上层没拿到
    theory_expert_tool = AgentTool(agent=theory_expert)
    microscopy_expert_tool = AgentTool(agent=microscopy_expert)
    representation_analyze_expert_tool = AgentTool(agent=representation_analyze_expert)
    software_expert_tool = AgentTool(agent=software_expert)
    report_expert_tool = AgentTool(agent=report_expert)

    agent_tools = [theory_expert_tool, microscopy_expert_tool, representation_analyze_expert_tool, software_expert_tool, report_expert_tool]
    
    agent = LlmAgent(
        model=llm,
        name="representation_expert_agent",
        description="表征专家代理，协调和管理表征相关任务，可以委托给专业的子代理处理具体问题。",
        instruction=representation_agent_instruction,
        tools=agent_tools,
        sub_agents=[planner],
        before_agent_callback=before_agent_callback
    )
    
    return agent

root_agent = create_agent()
