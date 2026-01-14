"""Node definitions for the travel assistant graph."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from travel_assistant.backend.config import get_llm
from travel_assistant.backend.prompts import INPUT_EXTRACTION_SYSTEM_PROMPT, PLANNER_SYSTEM_PROMPT, RESPONSE_SYSTEM_PROMPT, get_planner_user_prompt
from travel_assistant.backend.schemas import InputSchema, TripSchema
from travel_assistant.backend.state import TravelState
from travel_assistant.backend.tools import search_destinations, get_weather, search_hotels


def process_input(state: TravelState) -> TravelState:
    """Process user input and extract travel information.

    This node analyzes user messages to extract:
    - Destination
    - Travel dates
    - Preferences

    Args:
        state: The current graph state.

    Returns:
        Updated state with extracted information.
    """
    llm = get_llm(structured_output=InputSchema)
    
    # Format conversation history
    history = "\n".join([f"{msg.type}: {msg.content}" for msg in state["messages"]])
    
    try:
        extraction = llm.invoke([
            SystemMessage(content=INPUT_EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(content=f"Conversation History:\n{history}")
        ])
        
        updates = {}
        if extraction.destination:
            updates["destination"] = extraction.destination
        if extraction.start_date and extraction.end_date:
            updates["travel_dates"] = {"start": extraction.start_date, "end": extraction.end_date}
        if extraction.interests:
            updates["preferences"] = {"interests": extraction.interests}
            
        return updates
        
    except Exception as e:
        print(f"Error extracting input: {e}")
        return state


def plan_itinerary(state: TravelState) -> TravelState:
    """Plan the travel itinerary based on user preferences.

    This node creates a personalized travel plan including:
    - Daily activities
    - Recommended accommodations
    - Restaurant suggestions

    Args:
        state: The current graph state.

    Returns:
        Updated state with itinerary information.
    """
    structured_llm = get_llm(structured_output=TripSchema)

    destination = state.get("destination", "determined by the AI")
    dates = state.get("travel_dates", {})
    preferences = state.get("preferences", {})
    
    system_prompt = PLANNER_SYSTEM_PROMPT
    user_prompt = get_planner_user_prompt(destination, dates, preferences)

    try:
        trip_plan = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        return {"trip_plan": trip_plan}
    except Exception as e:
        # In a real app, handle error gracefully
        print(f"Error generating itinerary: {e}")
        return state


def generate_response(state: TravelState) -> TravelState:
    """Generate a response to the user.

    This node creates a user-friendly response based on
    the current state and any planned itinerary.

    Args:
        state: The current graph state.

    Returns:
        Updated state with response message.
    """
    trip_plan = state.get("trip_plan")
    
    if not trip_plan:
        return {"messages": [AIMessage(content="I'm sorry, I couldn't generate a travel plan for you at this time.")]}
    
    llm = get_llm()
    system_prompt = RESPONSE_SYSTEM_PROMPT
    user_prompt = f"Here is the trip plan:\n{trip_plan.model_dump_json()}"
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    return {"messages": [response]}


from langgraph.prebuilt import create_react_agent

# Initialize Sub-Agents
# We use a smaller/faster model for these agents if configured (model_key="TOOL")
tool_llm = get_llm(model_key="TOOL")

attraction_agent_executor = create_react_agent(tool_llm, [search_destinations])
weather_agent_executor = create_react_agent(tool_llm, [get_weather])
hotel_agent_executor = create_react_agent(tool_llm, [search_hotels])


async def attraction_search_agent(state: TravelState) -> TravelState:
    """Agent that searches for attractions using MCP."""
    destination = state.get("destination")
    if not destination:
        return {"attractions_info": "No destination specified for attraction search."}

    prompt = f"Find top attractions and sights in {destination}. Provide a concise summary."
    
    try:
        # Invoke the sub-agent
        result = await attraction_agent_executor.ainvoke({"messages": [HumanMessage(content=prompt)]})
        # Extract the final response from the agent
        last_message = result["messages"][-1]
        return {"attractions_info": last_message.content}
    except Exception as e:
        return {"attractions_info": f"Failed to fetch attractions: {str(e)}"}


async def weather_query_agent(state: TravelState) -> TravelState:
    """Agent that queries weather using MCP."""
    destination = state.get("destination")
    if not destination:
        return {"weather_info": "No destination specified for weather query."}

    dates = state.get("travel_dates", {}) or {}
    start_date = dates.get("start", "today")
    
    prompt = f"Check the weather in {destination} for {start_date}. Provide a concise summary."

    try:
        result = await weather_agent_executor.ainvoke({"messages": [HumanMessage(content=prompt)]})
        last_message = result["messages"][-1]
        return {"weather_info": last_message.content}
    except Exception as e:
        return {"weather_info": f"Failed to fetch weather: {str(e)}"}


async def hotel_info_agent(state: TravelState) -> TravelState:
    """Agent that searches for hotels using MCP."""
    destination = state.get("destination")
    if not destination:
        return {"hotel_info": "No destination specified for hotel search."}

    dates = state.get("travel_dates", {}) or {}
    start_date = dates.get("start", "today")
    end_date = dates.get("end", "tomorrow")
    
    prompt = f"Find available hotels in {destination} from {start_date} to {end_date}. Provide a concise summary."

    try:
        result = await hotel_agent_executor.ainvoke({"messages": [HumanMessage(content=prompt)]})
        last_message = result["messages"][-1]
        return {"hotel_info": last_message.content}
    except Exception as e:
        return {"hotel_info": f"Failed to fetch hotels: {str(e)}"}

