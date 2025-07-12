import asyncio
import json
from google.adk.agents import LlmAgent
from typing import Any, AsyncGenerator
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types
from typing_extensions import override
from utils.func_tool.database import *


class LongRunningLlmAgent(LlmAgent):
    """
    LongRunningLlmAgent 是一个自定义的 LlmAgent 类，
    其特点是可以支持设置 long-running 功能。
    """
    long_running_function_call: types.FunctionCall | None = None
    long_running_function_response: types.FunctionResponse | None = None
    ticket_id: str | None = None
    long_res: dict | None = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

    def get_long_running_function_call(self,event: Event) -> types.FunctionCall:
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
    def extract_task_name(self,input_string):
        """
        提取字符串中最后一个破折号之前的名称部分。
        """
        last_dash_index = input_string.rfind('-')
        if last_dash_index != -1:
            return input_string[:last_dash_index]
        else:
            return input_string


    def get_function_response(self,event: Event, function_call_id: str) -> types.FunctionResponse:
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
    
    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        async for event in super()._run_async_impl(ctx):
            # print("event: ", event)
            
            if not self.long_running_function_call:
                self.long_running_function_call = self.get_long_running_function_call(event)
            else:
                self.long_running_function_response = self.get_function_response(event, self.long_running_function_call.id)
                if self.long_running_function_response:
                    # self.ticket_id = self.long_running_function_response.response['ticketId']
                    # print("ticket_id: ", self.ticket_id)
                    # todo: 这里需要适配原始长函数，因为result是FunctionResponse，不是dict
                    result_str = self.long_running_function_response.response.get('result').content[0].text
                    self.long_res = json.loads(result_str)
                    self.ticket_id = self.long_res['ticket_id']
                    print("ticket_id: ", self.ticket_id)
                    
            yield event
            # 检测到了初始审批状态，等待数据库查询状态
            if self.ticket_id:
                # f"approval-{uuid.uuid4().hex[:8]}"
                # f"code-interpreter-{uuid.uuid4().hex[:8]}"
                task_name = self.extract_task_name(self.ticket_id)
                task_status = 'pending'
                if task_name == 'approval':
                    task_status = await get_approval_state_by_id_async(self.long_res['ticketId'],repeat_times=15)
                elif task_name == 'code-interpreter':
                    task_status = await get_code_interpreter_state_by_id_async(self.long_res['state_id'],repeat_times=15)
                # 'pending' | 'running' | 'completed' | 'error' | 'approved' | 'rejected'
                print("task_status: ", task_status)
                          
                updated_response = self.long_running_function_response.model_copy(deep=True)
                updated_response.response['status'] = task_status
                self.ticket_id = None
                self.long_res = None
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
