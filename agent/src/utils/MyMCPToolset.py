from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from typing import List
from google.adk.tools.mcp_tool.mcp_tool import MCPTool

class MyMCPToolset(MCPToolset):
    def __init__(
        self,
        tools_set_long_running: List[str] = [],
        **kwargs,
    ):
        """
        支持设置long running的mcp toolset

        Args:
            tools_set_long_running: List[str] = [],
        """
        super().__init__(**kwargs)
        self.tools_set_long_running = tools_set_long_running
    async def get_tools(self, *args, **kwargs) -> List[MCPTool]:
        tools = await super().get_tools(*args, **kwargs)
        tools_dict = {tool.name: tool for tool in tools}
        
        for tool in tools_dict.values():
            if tool.name in self.tools_set_long_running:
                tool.is_long_running = True
            else:
                tool.is_long_running = False

        return tools
