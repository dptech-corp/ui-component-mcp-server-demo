import asyncio
import time
import random

import httpx
from pocketflow import Node, AsyncNode
from pocketflow import Flow, AsyncFlow
from fastmcp import Client
import os
import json

mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse")

async def ask_for_approval(description: str):
    client = Client(mcp_server_url)
    async with client as session:
        res = await session.call_tool_mcp(name="ask_for_approval", arguments={"description": description})
        return res
async def get_approval_state_by_id_async(ticket_id: str):
    """
    后端获取审批结果。
    参数：
    - ticket_id (str): 要查询的审批请求的唯一标识符。
    返回：
    - dict: 包含审批数据的字典。
        """
    url = f"http://localhost:8000/api/approvals/{ticket_id}"
    async with httpx.AsyncClient() as client:  
        for i in range(5):
            await asyncio.sleep(2)
            response = await client.get(url)
            response.raise_for_status()  # 检查请求是否成功
            ticket_status = response.json()["status"]
            if ticket_status == "approved":
                return "approved"
            elif ticket_status == "rejected":
                return "rejected"
            else:
                print("waiting for human input")
                continue
        return "None"


class ProcessNode(Node):
    def prep(self, shared):
        task_input = input("请输入当前处理的待人机交互的任务：")
        shared["task_input"] = task_input
        print("处理节点：", task_input)
        return task_input

    def exec(self, prep_res):
        return "default"    


class ReviewNode(AsyncNode):
    async def prep_async(self, shared):
        task_name = shared.get("task_input", "No input")
        res = await ask_for_approval('人工检测：' + task_name)      
        ticket_id = json.loads(res.content[0].text)["ticketId"]
        return ticket_id
        
    async def exec_async(self, prep_res):
        if prep_res == "None":
            return "None"
        else:
            ticket_id = prep_res
            print("ticket_id: ", ticket_id)
            return await get_approval_state_by_id_async(ticket_id)
            
    async def post_async(self, shared, prep_res, exec_res):
        print("人机交互完成，人类交互的结果是：", exec_res)
        return exec_res

class NextNode(Node):
    def exec(self, prep_res):
        print("处理人机交互的下一个节点中。。。 ")

    def post(self, shared, prep_res, exec_res):
        print("NextNode Post: Flow finished.")
        return None  # End flow

def create_feedback_flow():
    """Creates the minimal feedback workflow."""
    process_node = ProcessNode()
    review_node = ReviewNode()
    next_node = NextNode()

    # Define transitions
    process_node >> review_node
    review_node - "approved" >> next_node
    review_node - "None" >> review_node
    review_node - "rejected" >> process_node # Loop back

    # Create the AsyncFlow
    flow = AsyncFlow(start=process_node)
    print("Minimal feedback flow created.")
    return flow
async def main():
    shared = {
        "task_input": "Example task input"
    }
    flow = create_feedback_flow()
    await flow.run_async(shared)
    print("Flow completed. Final result:", shared.get("final_result"))

if __name__ == "__main__":
    asyncio.run(main())
    # result = asyncio.run(get_approval_state_by_id_async("approval-0b8a86e9"))
    # print(result)