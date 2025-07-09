"""
create plan items for a given goal
"""

import os
import sys
# from typing import override
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator, Optional
from google.genai import types # For types.Content
from google.adk.events import Event
from google.adk.agents.callback_context import CallbackContext
from fastmcp import Client


# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from utils.config import llm, mcp_server_url
from representation.types import Plan, Step
from representation.agents.step_runner import step_runner_instruction
from representation.service.plan import add_plan, clear_plan

planner_instruction = f"""
## 概述
你是一个专家代理的任务规划者。你的目标是为用户创建任务计划。
因为在处理科学问题，所以你需要严格、准确。

你具备强大的计划制定和执行能力：
- **计划分解**：当用户提出复杂目标时，自动将其分解为具体的、可执行的步骤
- **计划创建**：为每个步骤创建对应的 plan 项
- **执行跟踪**：在执行过程中，完成每个步骤后自动标记对应的 plan 为完成状态
- **进度管理**：实时跟踪整体进度，确保所有步骤按序完成
- 人是系统中关键的一环， human 可以作为一个 sub_agent，因此你的计划中可以有需要人进行介入的步骤(如: 放入样品、取出样品、启动系统等)

--

## 复杂问题的处理流程
你必须为每个用户查询遵循以下交互过程。

对于复杂目标，必须采用计划驱动的执行模式：

1. **目标分析与计划制定**：
   - 分析用户的查询以确定总体目标
   - 将复杂目标分解为具体的、可执行的步骤
   - 向用户展示完整的执行计划

2. **逐步执行与进度跟踪**：
   - 按顺序执行每个计划步骤
   - 委托给相应的专家子代理处理具体任务
   - 向用户报告当前步骤的执行结果和整体进度

3. **持续监控与调整**：
   - 实时跟踪所有计划项的完成状态
   - 如遇到问题，及时调整计划或寻求用户指导
   - 确保所有步骤按序完成，直到总体目标达成

--
## **IMPORTANT HINT**
1. 你是一个 "Human-in-the-loop" 的系统，人是系统中关键的一环， human 可以作为一个 sub_agent，因此你的计划中可以有需要人进行介入的步骤(如: 放入样品、取出样品、启动系统等)
2. 在制定计划时，你要充分各个子系统的能力，子系统的能力如下面 (子系统能力介绍一小节)
在没有收集到足够的信息制定计划时，你必须停止并等待用户提供更多信息。

## 子系统能力介绍
{step_runner_instruction}
"""


plan_saver_instruction = f"""
save plan items to mcp tool and save to state.

按照下面的方式存储计划项：
1. 从 unstructured_plan 中提取计划项
2. 保存到 state
3. 在 callback 中使用 add_plan 工具添加计划项

--
Your job is to take the research plan from {{unstructured_plan}} and
format them according to this strict JSON schema:

{Plan.model_json_schema()}
"""

unstructured_planner = LlmAgent(
    name="unstructured_planner",
    model=llm,
    instruction=planner_instruction,
    description="unstructured_planner",
    output_key="unstructured_plan",
)


async def add_steps(plan: Plan):
    print("aaaaaaaaaaaaa add plan")
    print(plan)
    steps = plan.steps
    for i in range(len(steps)):
        step = steps[i]
        # TODO 更新计划 id 到 state 中
        await add_plan(f"{i+1}. {step.title}", step.sub_agent, step.description)
    return None

async def save_plan_after_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    print("0000000000000000000000000000000000000000000000")
    await clear_plan()
    plan_dict = callback_context.state["plan"]
    plan = Plan(**plan_dict)
    await add_steps(plan)
    return None

plan_saver = LlmAgent(
    name="plan_saver",
    model=llm,
    instruction=plan_saver_instruction,
    description="plan_saver",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=Plan,
    output_key="plan",
)

planner = SequentialAgent(
    name="planner",
    sub_agents=[unstructured_planner, plan_saver],
    description="planner",
    after_agent_callback=save_plan_after_agent,
)