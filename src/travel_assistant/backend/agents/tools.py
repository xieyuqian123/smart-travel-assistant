"""Tools execution helpers for agents."""

import json
from langchain_core.messages import HumanMessage, ToolMessage
from travel_assistant.backend.config import get_llm

# Initialize Sub-Agents
# We use a smaller/faster model for these agents if configured (model_key="TOOL")
tool_llm = get_llm(model_key="TOOL", model_name="Qwen/Qwen2.5-7B-Instruct")

async def run_simple_tool_agent(prompt: str, tools_list: list, llm) -> str:
    """Executes a simple ReAct-style loop: LLM -> Tool -> LLM Summary.
    
    Robustly handles stringified tool arguments which can occur with some models.
    """
    llm_with_tools = llm.bind_tools(tools_list)
    messages = [HumanMessage(content=prompt)]
    
    # 1. First LLM Call (Decide to call tool)
    response = await llm_with_tools.ainvoke(messages)
    messages.append(response)
    
    # 2. Execute Tools if any
    if response.tool_calls:
        for tc in response.tool_calls:
            # Robust parsing of args
            tool_args = tc["args"]
            if isinstance(tool_args, str):
                try:
                    tool_args = json.loads(tool_args)
                except json.JSONDecodeError:
                    pass # Keep as string if parsing fails, might be just a string arg
            
            # Find matching tool
            tool_name = tc["name"]
            selected_tool = next((t for t in tools_list if t.name == tool_name), None)
            
            tool_output = "Tool not found."
            if selected_tool:
                try:
                     # Await if async tool, else call
                     if hasattr(selected_tool, "ainvoke"):
                         tool_output = await selected_tool.ainvoke(tool_args)
                     else:
                         tool_output = selected_tool.invoke(tool_args)
                except Exception as e:
                    tool_output = f"Tool execution error: {e}"
            
            messages.append(ToolMessage(content=str(tool_output), tool_call_id=tc["id"]))
            
        # 3. Final Summary Call
        final_response = await llm_with_tools.ainvoke(messages)
        return final_response.content
    
    # If no tool called, return original content
    return response.content
