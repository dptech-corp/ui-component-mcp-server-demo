# call mcp api to get/list/create/update/delete plan and step

from fastmcp import Client
from utils.config import mcp_server_url



async def clear_plan():
    client = Client(mcp_server_url)
    async with client as session:
        print("22222222222222222222222222222222222222222")
        tools = await session.list_tools()
        print(tools)
        res = await session.call_tool_mcp(name="clear_plan", arguments={})
        return res

async def add_plan(title: str, sub_agent: str, description: str):
    client = Client(mcp_server_url)
    async with client as session:
        print("33333333333333333333333333333333333333333")
        tools = await session.list_tools()
        print(tools)
        description = f"agent: {sub_agent}\n\ndescription: {description}"
        res = await session.call_tool_mcp(name="add_plan", arguments={"title": title, "description": description})
        return res
