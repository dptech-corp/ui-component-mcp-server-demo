from google.adk.agents.callback_context import CallbackContext
from google.genai import types

def before_step_callback(callback_context: CallbackContext):
    print("before step_runner callback")
    if not callback_context.state.get("plan_mode"):
        return
    from representation.types import Plan

    agent_name = callback_context.agent_name
    if not callback_context.state.get("plan"):
        print("1111111111111111111111111111111111111111111111111111111")
        print("skip step_runner due to no plan found in state!!!!")
        return types.Content(
            parts=[types.Part(text=f"Agent {agent_name} skipped by before_agent_callback due to no plan.")],
            role="model" # Assign model role to the overriding response
        )
    plan_dict = callback_context.state.get("plan")
    plan = Plan(**plan_dict)

    if not callback_context.state.get("step_index"):
        print("2222222222222222222222222222222222222222222222222222222")
        callback_context.state["step_index"] = 0
        callback_context.state["step"] = plan.steps[0].model_dump()


def after_step_callback(callback_context: CallbackContext):
    if not callback_context.state.get("plan_mode"):
        return
    from representation.types import Plan
    if not callback_context.state.get("plan"):
        print("3333333333333333333333333333333333333333333333333333333")
        print("skip step_runner due to no plan found in state!!!!")
        return
    plan_dict = callback_context.state.get("plan")
    plan = Plan(**plan_dict)
    
    if callback_context.state.get("step_index") + 1< len(plan.steps):
        callback_context.state["step_index"] += 1
        callback_context.state["step"] = plan.steps[callback_context.state["step_index"]].model_dump()
    