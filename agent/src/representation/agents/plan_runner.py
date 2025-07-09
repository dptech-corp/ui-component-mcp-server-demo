"""
loop plan items and process them one by one(calling step_runner)
until all plan items are completed
"""

import os
import sys
from google.adk.agents import LoopAgent
from representation.agents.step_runner import step_runner

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

plan_runner_desc = """
你是一个表征专家代理的任务执行者。你的目标是为用户执行任务。

你具备强大的执行能力：
- **任务执行**：通过调用 step_runner 来执行计划项的详细步骤
- **进度跟踪**：实时跟踪执行进度，确保任务按序完成后调用 toggle_plan 标记为完成
- **结果反馈**：向用户或上层代理系统展示执行结果和整体进度
"""

plan_runner = LoopAgent(
    name="plan_runner",
    description=plan_runner_desc,
    sub_agents=[step_runner],
    max_iterations=10,    
)
