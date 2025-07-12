import httpx
import asyncio
async def get_approval_state_by_id_async(ticket_id: str,repeat_times: int = 1):
    """
    从approval表中获取人工审批状态。
    参数：
    - ticket_id (str): 要查询的审批请求的唯一标识符。
    - repeat_times (int): 重复次数默认1次。
    返回：
    - str: 审批状态。
        """
    url = f"http://ui-mcp-backend:8000/api/approvals/{ticket_id}"
    async with httpx.AsyncClient() as client:
        status = 'pending'
        if repeat_times < 1:
            repeat_times = 1
        elif repeat_times > 15:
            repeat_times = 15
        for i in range(repeat_times):
            try:
                response = await client.get(url)
                response.raise_for_status()
                status = response.json()["status"]
                if status in ['approved', 'rejected']:
                    print("approval is completed: ", status)
                    return status
            except (httpx.ReadTimeout, httpx.WriteTimeout) as e:
                print(f"Request timeout, retrying... (attempt {i+1}/{repeat_times})")
                continue
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            if i < repeat_times - 1:
                await asyncio.sleep(2)      
        return status
async def get_code_interpreter_state_by_id_async(state_id: str,repeat_times: int = 1):
    """
    获取代码解释器执行状态。
    参数：
    - state_id (str): 要查询的代码解释器执行状态的唯一标识符。
    - repeat_times (int): 重复次数默认1次。
    返回：
    - str: 代码解释器执行状态。
    """
    url = f"http://ui-mcp-backend:8000/api/code-interpreter/states/{state_id}"
    timeout = httpx.Timeout(connect=10, read=30, write=10, pool=10)
    async with httpx.AsyncClient(timeout=timeout) as client:
        status = 'pending'
        if repeat_times < 1:
            repeat_times = 1
        elif repeat_times > 15:
            repeat_times = 15
        for i in range(repeat_times):
            try:
                response = await client.get(url)
                response.raise_for_status()
                status = response.json()["status"]
                if status in ['approved', 'rejected']:
                    print("code-interpreter is completed: ", status)
                    return status
                print("waiting for code-interpreter...", state_id)
            except (httpx.ReadTimeout, httpx.WriteTimeout) as e:
                print(f"Request timeout, retrying... (attempt {i+1}/15)")
                continue
            except Exception as e:
                print(f"Error occurred: {e}")
                continue
            if i < repeat_times - 1:
                await asyncio.sleep(2)

        return status

# 使用 asyncio 运行异步函数
# approval_id = "approval-6314bd20"     
# approval_data = asyncio.run(fetch_approval(approval_id))
# print(approval_data)
# state_id = "03164f7e-bc4a-4f82-b313-866ff741f877"
# code_interpreter_data = asyncio.run(get_code_interpreter_state_by_id_async(state_id))
# print(code_interpreter_data)

import requests

def get_approval_state_by_id(ticket_id: str):
    """
    根据审批ID从后端获取审批状态。
    参数：
    - ticket_id (str): 要查询的审批请求的唯一标识符。
    返回：
    - str: 包含审批状态的字符串。
    """
    url = f"http://ui-mcp-backend:8000/api/approvals/{ticket_id}"
    with requests.Session() as session:
        response = session.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()["status"]

def get_code_interpreter_state_by_id(state_id: str):
    """
    根据审批ID从后端获取审批状态。
    参数：
    - ticket_id (str): 要查询的审批请求的唯一标识符。
    返回：
    - str: 包含审批状态的字符串。
    """
    url = f"http://ui-mcp-backend:8000/api/code-interpreter/states/{state_id}"
    with requests.Session() as session:
        response = session.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()["status"]

# approval_id = "approval-6314bd20"
# approval_data = get_approval_by_id(approval_id)
# print(approval_data)