"""
Google ADK Agent for UI Component Demo

This agent connects to the existing MCP server and provides AI-powered
control of the todo list component.
"""
import asyncio
import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.adk.tools.tool_context import ToolContext
from typing import Any, AsyncGenerator, List, Optional
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.events import Event
from google.genai import types
from agent.database import database
from typing_extensions import override
from google.adk.tools.mcp_tool.mcp_tool import MCPTool
import json

load_dotenv()

def get_approval_status(ticket_id: str) -> dict:
    import redis
    import json
    r = redis.Redis(host='localhost', port=6379, db=0)
    key = f"approval:{ticket_id}"
    value = r.get(key)
    if value:
        return json.loads(value)
    else:
        return {"status": "pending"}
async def get_approval(approval_id: str) ->dict:

# (id, session_id, function_call_id, description, status, created_at, updated_at, result)
#                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",

    """Get an approval request by ID."""
    async with database.get_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id, session_id, function_call_id, description, status, created_at, updated_at, result FROM approvals WHERE id = %s",
                (approval_id,)
            )
            row = await cursor.fetchone()
            return {
                'status': row[4],
            }


def reimburse(purpose: str, amount: float) -> str:
  """Reimburse the amount of money to the employee."""
  print("reimburse")
  return {
      'status': 'ok',
  }
def ask_for_approval(
    purpose: str, amount: float, tool_context: ToolContext
) -> dict[str, Any]:
  """Ask for approval for the reimbursement."""
  print("ask_for_approval: ", purpose, amount, tool_context)
  return {
      'status': 'pending',
      'amount': amount,
      'ticketId': 'reimbursement-ticket-001',
  }

  

def get_long_running_function_call(event: Event) -> types.FunctionCall:
    # Get the long running function call from the event
    if not event.long_running_tool_ids or not event.content or not event.content.parts:
        return
    for part in event.content.parts:
        if (
            part
            and part.function_call
            and event.long_running_tool_ids
            and part.function_call.id in event.long_running_tool_ids
        ):
            return part.function_call

def get_function_response(event: Event, function_call_id: str) -> types.FunctionResponse:
    # Get the function response for the fuction call with specified id.
    if not event.content or not event.content.parts:
        return
    for part in event.content.parts:
        if (
            part
            and part.function_response
            and part.function_response.id == function_call_id
        ):
            return part.function_response

class ReimbursementAgent(LlmAgent):
    # Define fields that will be set after initialization
    long_running_function_call: types.FunctionCall | None = None
    long_running_function_response: types.FunctionResponse | None = None
    ticket_id: str | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        async for event in super()._run_async_impl(ctx):
            print("event: ", event)
            
            if not self.long_running_function_call:
                self.long_running_function_call = get_long_running_function_call(event)
            else:
                self.long_running_function_response = get_function_response(event, self.long_running_function_call.id)
                if self.long_running_function_response:

                    # self.ticket_id = self.long_running_function_response.response['ticketId']
                    result_str = self.long_running_function_response.response.get('result').content[0].text
                    self.ticket_id = json.loads(result_str)['ticketId']
                    print("ticket_id: ", self.ticket_id)
            
            yield event
            # 检测到了初始审批状态，等待
            if self.ticket_id:
                while True:
                    await asyncio.sleep(2)
                    print("waiting for approval...")
                    approval_status = await get_approval(self.ticket_id)
                    if approval_status['status'] == 'approved':
                        break
                    elif approval_status['status'] == 'rejected':
                        break
                    else:
                        print("approval_status: ", approval_status)
                    # approval_status = {'status': 'approved'}
                # TODO: 添加一个访问redis的 mcp 工具，用于获取审批状态
                    
                updated_response = self.long_running_function_response.model_copy(deep=True)
                updated_response.response['status'] = approval_status['status']
                self.ticket_id = None
                self.long_running_function_call = None
                self.long_running_function_response = None
                print("updated_response: ", updated_response)
                
                # Create Event with proper content and author fields
                yield Event(
                    author="assistant",
                    content=types.Content(
                        parts=[types.Part(function_response=updated_response)],
                        role='assistant'
                    )
                )
APP_NAME="reimbursement_agent"
USER_ID="user1234"
SESSION_ID="1234"
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
                    
def create_agent():
    """Create and configure the ADK agent with MCP tools."""
    
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
    # mcp_server_url = "http://localhost:8001"
    mcp_toolset = MyMCPToolset(
        connection_params=SseConnectionParams(
            url=f"{mcp_server_url}/sse",
            headers={}
        ),
        tool_filter=["ask_for_approval"],
        tools_set_long_running=["ask_for_approval"]
    )
    
    # TODO P0: 添加 mcp 中真实的 ask_for_approval 并设置 long running

    # tools = [reimburse, LongRunningFunctionTool(ask_for_approval)]
    tools = [reimburse, mcp_toolset]
    agent = ReimbursementAgent(
        model=LiteLlm(
            model=os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash"),
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_API_BASE_URL")),
        name="todo_assistant_agent",
        instruction="""You are an agent whose job is to handle the reimbursement process for
            the employees. If the amount is less than $100, you will automatically
            approve the reimbursement.

            If the amount is greater than $100, you will
            ask for approval from the manager. If the manager approves, you will
            call reimburse() to reimburse the amount to the employee. If the manager
            rejects, you will inform the employee of the rejection.""",
        tools=tools
    )
    
    return agent

root_agent = create_agent()
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner


# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)
    await asyncio.sleep(1000)

import asyncio

if __name__ == "__main__":
    asyncio.run(call_agent_async("帮我报销1000元买书的钱"))

        
