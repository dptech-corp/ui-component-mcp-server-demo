import httpx
import asyncio

async def get_approval_state_by_id_async(ticket_id: str):
    """
    后端获取审批数据。
    参数：
    - ticket_id (str): 要查询的审批请求的唯一标识符。
    返回：
    - dict: 包含审批数据的字典。
        """
    url = f"http://localhost:8000/api/approvals/{ticket_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()["status"]

# 使用 asyncio 运行异步函数
# approval_id = "approval-6314bd20"       
# approval_data = asyncio.run(fetch_approval(approval_id))
# print(approval_data)

import requests

def get_approval_state_by_id(ticket_id: str):
    """
    根据审批ID从后端获取审批状态。
    参数：
    - ticket_id (str): 要查询的审批请求的唯一标识符。
    返回：
    - str: 包含审批状态的字符串。
    """
    url = f"http://localhost:8000/api/approvals/{ticket_id}"
    response = requests.get(url)
    response.raise_for_status()  # 检查请求是否成功
    return response.json()["status"]

# approval_id = "approval-6314bd20"
# approval_data = get_approval_by_id(approval_id)
# print(approval_data)