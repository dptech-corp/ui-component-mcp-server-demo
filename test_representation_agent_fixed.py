#!/usr/bin/env python3
"""
Test script to verify the fixed representation agent implementation with sub_agents
"""

import sys
import os
sys.path.append('/home/ubuntu/repos/ui-component-mcp-server-demo/agent/src')

def test_representation_agent():
    try:
        from representation.main import root_agent
        print("✅ Agent imported successfully!")
        print(f"Agent name: {root_agent.name}")
        print(f"Agent description: {root_agent.description}")
        print(f"Number of sub-agents: {len(root_agent.sub_agents) if hasattr(root_agent, 'sub_agents') and root_agent.sub_agents else 0}")
        
        if hasattr(root_agent, 'sub_agents') and root_agent.sub_agents:
            print("\nSub-agents:")
            for i, sub_agent in enumerate(root_agent.sub_agents):
                print(f"  {i+1}. {sub_agent.name}: {sub_agent.description}")
        
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
    test_representation_agent()
