"""
process a given plan step and update plan item status
"""

import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.genai import types

# Add the parent directory to sys.path to allow absolute imports
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from representation.types import Plan, Step
from utils.config import llm, mcp_server_url
from software import software_expert_desc, software_expert
from microscopy import microscopy_expert_desc, microscopy_expert
from representation_analyze import representation_analyze_expert, representation_analyze_expert_desc
from theory import theory_expert_desc, theory_expert
from utils.LongRunningLlmAgent import LongRunningLlmAgent
from utils.LongRunningMCPToolset import LongRunningMCPToolset
from utils.func_tool.database import get_approval_state_by_id_async

step_runner_instruction = f"""
## 概述
你是一个表征专家代理的任务执行者。你的目标是为用户执行任务。
**你必须确保调用 planner 生成 plan 后才能调我**

你具备强大的执行能力：
- **任务执行**：执行计划项的详细步骤
- **结果反馈**：向用户展示执行结果和整体进度
- **step by step**：每完成一步后，必须等待用户确认后，再开始执行下一步
- **进度跟踪**：实时跟踪执行进度，任务完成后调用 toggle_plan 工具标记为完成


--


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

"""
func_tools = [get_approval_state_by_id_async]
mcp_toolset = LongRunningMCPToolset(
    connection_params=SseServerParams(
        url=mcp_server_url,
        headers={}
    ),
    # tool_filter=["add_plan", "delete_plan", "update_plan", "toggle_plan", "list_plan", "ask_for_approval"],
    tool_filter=["toggle_plan", "list_plan", "ask_for_approval"],
    tools_set_long_running=["ask_for_approval"]
)

theory_expert_tool = AgentTool(agent=theory_expert)
microscopy_expert_tool = AgentTool(agent=microscopy_expert)
representation_analyze_expert_tool = AgentTool(agent=representation_analyze_expert)
software_expert_tool = AgentTool(agent=software_expert)

agent_tools = [theory_expert_tool, microscopy_expert_tool, representation_analyze_expert_tool, software_expert_tool]
cu_tools = func_tools+[mcp_toolset]+agent_tools

def before_agent_callback(callback_context: CallbackContext):
    agent_name = callback_context.agent_name
    print("before step_runner callback")
    if not callback_context.state.get("plan"):
        print("1111111111111111111111111111111111111111111111111111111")
        print("skip step_runner due to no plan found in state!!!!")
        return types.Content(
            parts=[types.Part(text=f"Agent {agent_name} skipped by before_agent_callback due to no plan.")],
            role="model" # Assign model role to the overriding response
        )
    plan_dict = callback_context.state.get("plan")
    plan = Plan(**plan_dict)

    if not callback_context.state.get("step_index"):
        print("2222222222222222222222222222222222222222222222222222222")
        callback_context.state["step_index"] = 0
        callback_context.state["step"] = plan.steps[0].model_dump()
        # return types.Content(
        #     parts=[types.Part(text=f"Agent {agent_name} skipped by before_agent_callback due to init plan.")],
        #     role="model" # Assign model role to the overriding response
        # )
    # elif callback_context.state.get("step_index") + 1< len(plan.steps):
    #     callback_context.state["step_index"] += 1
    #     callback_context.state["step"] = plan.steps[callback_context.state["step_index"]].model_dump()

def after_agent_callback(callback_context: CallbackContext):
    if not callback_context.state.get("plan"):
        print("3333333333333333333333333333333333333333333333333333333")
        print("skip step_runner due to no plan found in state!!!!")
        return
    plan_dict = callback_context.state.get("plan")
    plan = Plan(**plan_dict)
    
    if callback_context.state.get("step_index") + 1< len(plan.steps):
        callback_context.state["step_index"] += 1
        callback_context.state["step"] = plan.steps[callback_context.state["step_index"]].model_dump()
    
    
step_runner = LlmAgent(
    name="step_runner",
    model=llm,
    instruction=step_runner_instruction,
    tools=agent_tools,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    )