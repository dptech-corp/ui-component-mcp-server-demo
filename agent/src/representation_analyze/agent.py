from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from utils.config import llm, mcp_server_url

representation_analyze_expert_desc = """representation_analyze_expert (表征分析专家子代理 uni-aims)
功能用途：
1. 执行各种材料表征数据的深度分析和解释
2. 提供XRD、XPS、FTIR、拉曼等谱学数据的专业解读
3. 进行电镜图像的定量分析和结构表征
4. 协助制定综合表征方案和实验设计
示例查询：
1. "请分析这组XRD数据并确定晶体结构和相组成"
2. "根据TEM图像计算纳米颗粒的尺寸分布"
3. "解释XPS谱图中的化学态信息和元素组成"
委托方式：调用 representation_analyze_expert 工具"""

representation_analyze_expert_instruction = """你是表征分析专家子代理 uni-aims。你的专业领域包括：
1. 执行各种材料表征数据的深度分析和解释
2. 提供XRD、XPS、FTIR、拉曼等谱学数据的专业解读
3. 进行电镜图像的定量分析和结构表征
4. 协助制定综合表征方案和实验设计

请根据用户提供的表征数据或分析需求，提供专业、详细的分析结果和解释。"""

representation_analyze_expert_mcp_toolset = MCPToolset(
    connection_params=SseServerParams(
        url=f"{mcp_server_url}/sse",
        headers={}
    ),
    tool_filter=["ls", "cat_run_sh", "bash_run_sh", 
                "create_python_notebook", "get_notebook_state",
                "create_file_tool", "list_files_tool"]
)

representation_analyze_expert = LlmAgent(
    model=llm,
    name="representation_analyze_expert",
    description=representation_analyze_expert_desc,
    instruction=representation_analyze_expert_instruction,
    tools=[representation_analyze_expert_mcp_toolset]
)

root_agent = representation_analyze_expert    
