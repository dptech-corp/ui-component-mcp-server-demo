"""
Google ADK Agent for UI Component Demo

This agent connects to the existing MCP server and provides AI-powered
control of the todo list component.
"""

import os
import sys
from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

# Add the parent directory to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from representation.agents.planner import planner
from representation.agents.plan_runner import plan_runner

load_dotenv()

representation_agent_instruction = f"""
你是一个表征专家代理。你的目标是与人类用户协作解决复杂的表征问题。
因为在处理科学问题，所以你需要严格、准确。

你具备强大的计划制定和执行能力：
- **计划创建**：通过 planner 子代理创建计划
- **执行跟踪**：对于拆接出的任务，调用 plan_runner 循环完成所有计划项（其内部会调用 step_runner 来执行每个计划项的详细步骤）
- **计划更新**：通过 planner 子代理更新计划, 当计划更新后，重新调用 plan_runner 循环完成所有计划项
- **进度管理**：实时跟踪整体进度，确保所有步骤按序完成(这个会由 plan_runner 完成)


你是一个严谨的面相科研的专家代理，你必须:
- 清晰与透明：用户必须始终知道你在做什么，结果是什么，以及你计划下一步做什么。
- 承认局限性：如果代理失败，报告失败，并建议不同的步骤或询问用户的指导。

"""


def create_agent():
    """Create and configure the ADK agent with MCP tools."""
    
    agent = LlmAgent(
        model=LiteLlm(
            model=os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash"),
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_API_BASE_URL")),
        name="representation_expert_agent",
        description="表征专家代理，协调和管理表征相关任务，可以委托给专业的子代理处理具体问题。",
        instruction=representation_agent_instruction,
        sub_agents=[planner, plan_runner],
    )
    
    return agent

root_agent = create_agent()