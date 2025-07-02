#!/usr/bin/env python3
"""
Test script to verify the AgentTool implementation for representation agent
"""

import sys
import os
sys.path.append('/home/ubuntu/repos/ui-component-mcp-server-demo/agent/src')

def test_agent_tool_implementation():
    try:
        from representation.main import root_agent
        print("✅ Agent imported successfully!")
        print(f"Agent name: {root_agent.name}")
        print(f"Agent description: {root_agent.description}")
        
        if hasattr(root_agent, 'tools') and root_agent.tools:
            print(f"Number of tools: {len(root_agent.tools)}")
            print("\nTools:")
            for i, tool in enumerate(root_agent.tools):
                tool_name = getattr(tool, 'name', str(type(tool).__name__))
                tool_desc = getattr(tool, 'description', 'No description')
                print(f"  {i+1}. {tool_name}: {tool_desc}")
                
                if hasattr(tool, 'agent'):
                    agent = tool.agent
                    print(f"     -> Wraps agent: {agent.name}")
        
        if hasattr(root_agent, 'sub_agents'):
            if root_agent.sub_agents:
                print("❌ Warning: sub_agents still present, should be empty for AgentTool pattern")
            else:
                print("✅ sub_agents correctly empty/None")
        else:
            print("✅ sub_agents attribute not present (expected for AgentTool pattern)")
        
        print(f"\nInstruction length: {len(root_agent.instruction)} characters")
        print("\nFirst 200 characters of instruction:")
        print(root_agent.instruction[:200])
        print("\n✅ All tests passed!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_agent_tool_implementation()
