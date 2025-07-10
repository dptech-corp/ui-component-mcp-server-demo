"""
Google ADK Agent for UI Component Demo

This agent connects to the existing MCP server and provides AI-powered
control of the todo list component.
"""

import os
import sys
# import asyncio
from google.adk.agents import LlmAgent
from utils.config import llm, mcp_server_url
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from dotenv import load_dotenv

# Add the parent directory to sys.path to allow absolute imports
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from representation.agents.planner import planner
from representation.agents.plan_runner import plan_runner
from representation.agents.step_runner import step_runner
from microscopy import microscopy_expert
from software import software_expert
from representation_analyze import representation_analyze_expert
from theory import theory_expert

load_dotenv()

representation_agent_instruction = f"""
## 概述
你是一个表征专家代理。你的目标是与人类用户协作解决复杂的表征问题。
因为在处理科学问题，所以你需要严格、准确。

你具备强大的计划制定和执行能力：
- **计划创建**：通过 planner 子代理创建计划
- **执行跟踪**：对于拆接出的任务，调用 step_runner 来执行每个计划项的详细步骤
- **step by step**：每完成一步后，必须等待用户确认后，再开始执行下一步
- **计划更新**：通过 planner 子代理更新计划, 当计划更新后，重新调用 plan_runner 循环完成所有计划项
- **进度管理**：实时跟踪整体进度，确保所有步骤按序完成(这个会由 plan_runner 完成)


## 任务规约
你是一个严谨的面相科研的专家代理，你必须:
- **计划优先**：在没有明确计划的时候，你必须先创建计划(planner)，待用户确认后，再开始执行计划(plan_runner)。
- **计划更新**：当计划更新后，重新调用 plan_runner 循环完成所有计划项
- **计划执行**：使用  step_runner 来执行每个计划项的详细步骤
- 清晰与透明：用户必须始终知道你在做什么，结果是什么，以及你计划下一步做什么。
- 承认局限性：如果代理失败，报告失败，并建议不同的步骤或询问用户的指导。

## IMPORTANT
**PLAN FIRST, THEN EXECUTE STEP BY STEP, ASK FOR HUMAN CONFIRMATION BEFORE EXECUTE NEXT STEP**

"""


def create_agent():
    """Create and configure the ADK agent with MCP tools."""
    
    mcp_toolset = MCPToolset(
        connection_params=SseServerParams(
            url=mcp_server_url,
            headers={}
        ),
        # tool_filter=["add_plan", "delete_plan", "update_plan", "toggle_plan", "list_plan"]
    )
    
    agent = LlmAgent(
        model=llm,
        name="representation_expert_agent",
        description="表征专家代理，协调和管理表征相关任务，可以委托给专业的子代理处理具体问题。",
        instruction=representation_agent_instruction,
        # sub_agents=[planner, plan_runner, step_runner],
        sub_agents=[planner, step_runner],
        # tools=[mcp_toolset]
    )
    
    return agent

root_agent = create_agent()
