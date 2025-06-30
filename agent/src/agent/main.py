"""
Google ADK Agent for UI Component Demo

This agent connects to the existing MCP server and provides AI-powered
control of the todo list component.
"""
import asyncio
import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.adk.tools.tool_context import ToolContext
from typing import Any, AsyncGenerator
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.events import Event
from google.genai import types

# 条件导入 override 装饰器，兼容 Python 3.11
if sys.version_info >= (3, 12):
    from typing import override
else:
    # 在 Python 3.11 中创建一个空的装饰器
    def override(func):
        return func

load_dotenv()

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
                    self.ticket_id = self.long_running_function_response.response['ticketId']
                    print("ticket_id: ", self.ticket_id)
            
            yield event

            if self.ticket_id:
                for i in range(5):
                    await asyncio.sleep(2)
                    print("waiting for approval...")
                    
                updated_response = self.long_running_function_response.model_copy(deep=True)
                updated_response.response['status'] = 'approved'
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

                    
def create_agent():
    """Create and configure the ADK agent with MCP tools."""
    
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8001")
    
    mcp_toolset = MCPToolset(
        connection_params=SseServerParams(
            url=f"{mcp_server_url}/sse",
            headers={}
        ),
        tool_filter=["add_todo", "delete_todo", "update_todo", "toggle_todo", "list_todo", 
                    "add_backlog", "delete_backlog", "update_backlog", "send_backlog_to_todo", "list_backlog",
                    "ls", "cat_run_sh", "bash_run_sh"]
    )
    # TODO P0: 添加 mcp 中真实的 ask_for_approval 并设置 long running

    tools = [reimburse, LongRunningFunctionTool(ask_for_approval)]
    
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
