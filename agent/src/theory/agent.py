
import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

# Add the parent directory to sys.path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.config import llm, mcp_server_url

theory_expert_desc = """theory_expert (领域理论专家子代理)
功能用途：
1. 处理显微学理论相关问题和概念解释
2. 解答衍射与成像技术的基础原理和应用
3. 提供波谱学与能谱学的理论知识和解释
4. 解答材料表征领域的前沿理论问题
示例查询：
1. "电子显微镜的分辨率极限是由什么因素决定的？"
2. "X射线衍射的布拉格定律如何应用于晶体结构测定？"
3. "拉曼光谱中的峰位移与分子振动模式有什么关系？"
委托方式：调用 theory_expert 工具"""

theory_expert_instruction = """你是领域理论专家子代理。你的专业领域包括：
1. 处理显微学理论相关问题和概念解释
2. 解答衍射与成像技术的基础原理和应用
3. 提供波谱学与能谱学的理论知识和解释
4. 解答材料表征领域的前沿理论问题

请根据用户的理论问题，提供严谨、准确的科学解释和理论知识。"""

theory_expert = LlmAgent(
    model=llm,
    name="theory_expert",
    description=theory_expert_desc,
    instruction=theory_expert_instruction,
)

root_agent = theory_expert
