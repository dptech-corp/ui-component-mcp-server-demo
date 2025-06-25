"""
Google ADK Agent for UI Component Demo

This agent connects to the existing MCP server and provides AI-powered
control of the todo list component.
"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from dotenv import load_dotenv
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

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
                    "ls", "cat_run_sh", "bash_run_sh", "wait_for_approval", "get_approval_status"]
    )
    print(f"model: {os.getenv('LLM_MODEL')}")
    # print(f"api_key: {os.getenv('OPENAI_API_KEY')}")
    # print(f"api_base: {os.getenv('OPENAI_API_BASE_URL')}")
    
    agent = LlmAgent(
        model=LiteLlm(
            model=os.getenv("LLM_MODEL", "gemini/gemini-1.5-flash"),
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_API_BASE_URL")),
        name="todo_assistant_agent",
        instruction="""You are a helpful assistant that can manage todo items and request human approval when needed.
        
        You can add, update, delete, and toggle todo items using the available MCP tools.
        
        For human-in-the-loop approval workflow:
        1. When you need human approval, call wait_for_approval with a clear description
        2. This will return a response with status="pending" and a ticketId
        3. You should then wait and periodically check the approval status using get_approval_status
        4. Once the human approves or rejects, you can proceed accordingly
        
        Always be helpful and provide clear feedback about the actions you take.
        When requesting approval, explain clearly what action you want to take and why.""",
        tools=[mcp_toolset]
    )
    
    return agent

root_agent = create_agent()
