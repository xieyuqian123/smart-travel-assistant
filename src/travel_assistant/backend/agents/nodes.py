"""Node definitions for the travel assistant graph."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import datetime

from travel_assistant.backend.config import get_llm
from travel_assistant.backend.prompts import (
    INPUT_EXTRACTION_SYSTEM_PROMPT, 
    PLANNER_SYSTEM_PROMPT, 
    RESPONSE_SYSTEM_PROMPT, 
    PLANNER_MODIFICATION_SYSTEM_PROMPT,
    get_planner_user_prompt
)
from travel_assistant.backend.schemas import InputSchema, TripSchema
from travel_assistant.backend.state import TravelState
from travel_assistant.backend.tools import search_destinations, get_weather, search_hotels
from travel_assistant.backend.tools.calculator import calculate_itinerary_cost, parse_cost


def process_input(state: TravelState) -> TravelState:
    """Process user input and extract travel information.

    This node analyzes user messages to extract:
    - Destination
    - Travel dates
    - Preferences
    - User modification requests (if plan exists)

    Args:
        state: The current graph state.

    Returns:
        Updated state with extracted information.
    """
    llm = get_llm(structured_output=InputSchema, model_name="Pro/zai-org/GLM-4.7")
    
    # Format conversation history
    history = "\n".join([f"{msg.type}: {msg.content}" for msg in state["messages"]])
    
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    try:
        extraction = llm.invoke([
            SystemMessage(content=INPUT_EXTRACTION_SYSTEM_PROMPT),
            HumanMessage(content=f"Current Date: {current_date}\n\nConversation History:\n{history}")
        ])
        
        updates = {}
        if extraction.destination:
            updates["destination"] = extraction.destination
        if extraction.start_date and extraction.end_date:
            updates["travel_dates"] = {"start": extraction.start_date, "end": extraction.end_date}
        if extraction.budget:
            updates["budget"] = extraction.budget
        if extraction.interests:
            updates["preferences"] = {"interests": extraction.interests}
            
        # Check if this is a modification request
        # If we already have a plan, and the user input is treated as "interests" or just general conversational, 
        # it might be feedback.
        # But for robustness, let's assume if there's a plan, the latest message is potential feedback.
        if state.get("trip_plan"):
             # Get the latest human message content
             last_msg = state["messages"][-1]
             if isinstance(last_msg, HumanMessage):
                 updates["user_feedback"] = last_msg.content
            
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
    
    It supports creating NEW plans and MODIFYING existing plans.

    Args:
        state: The current graph state.

    Returns:
        Updated state with itinerary information.
    """
    structured_llm = get_llm(structured_output=TripSchema, model_name="Pro/zai-org/GLM-4.7")

    destination = state.get("destination", "determined by the AI")
    dates = state.get("travel_dates", {})
    budget = state.get("budget")
    preferences = state.get("preferences", {})
    feedback = state.get("planner_feedback")
    
    # Modification Logic
    trip_plan_obj = state.get("trip_plan")
    user_feedback = state.get("user_feedback")
    
    if trip_plan_obj and user_feedback:
        # Modification Flow
        system_prompt = PLANNER_MODIFICATION_SYSTEM_PROMPT
        user_prompt = get_planner_user_prompt(
            destination, 
            dates, 
            budget, 
            preferences, 
            feedback,
            existing_plan=trip_plan_obj.model_dump_json(),
            user_feedback=user_feedback
        )
    else:
        # Creation Flow
        system_prompt = PLANNER_SYSTEM_PROMPT
        user_prompt = get_planner_user_prompt(destination, dates, budget, preferences, feedback)

    try:
        trip_plan = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        return {"trip_plan": trip_plan, "user_feedback": None} # Clear feedback after processing
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


def validate_budget(state: TravelState) -> TravelState:
    """Validate if the trip plan is within budget.
    
    NOTE: As per user request, strict budget validation is disabled to focus on planning.
    This node now just passes through.

    Args:
        state: The current graph state.

    Returns:
        Updated state with budget status OK.
    """
    return {"budget_status": "OK"}


def refine_itinerary(state: TravelState) -> TravelState:
    """Refine the itinerary with gathered information (costs, descriptions).
    
    This node runs after the search agents. It uses an LLM to update the 
    TripSchema with the specific details found by the agents.
    """
    trip_plan = state.get("trip_plan")
    if not trip_plan:
        return {} # No plan to refine
        
    attractions_info = state.get("attractions_info", "")
    weather_info = state.get("weather_info", "")
    hotel_info = state.get("hotel_info", "")
    
    # If no info gathered, skip
    if not (attractions_info or weather_info or hotel_info):
        return {}
        
    llm = get_llm(structured_output=TripSchema, model_name="Pro/zai-org/GLM-4.7")
    
    system_prompt = (
        "You are a travel assistant editor. Your goal is to UPDATE an existing travel itinerary "
        "with new information gathered from external tools. "
        "Focus on updating COSTS, TIMINGS, DESCRIPTIONS, and COORDINATES. "
        "If a specific cost was found (e.g. for a hotel or ticket), update the 'cost' field "
        "of the corresponding node. "
        "Crucially, if the tool output contains location details, you MUST populate the 'coordinates' "
        "field (lat, lng) for each node so they can be shown on a map. "
        "Do NOT change the structure of the trip or the destinations unless necessary. "
        "Maintain the original plan as much as possible, just enrich it."
    )
    
    user_prompt = (
        f"Original Plan: {trip_plan.model_dump_json()}\n\n"
        f"Gathered Information:\n"
        f"Attractions Info: {attractions_info}\n"
        f"Weather Info: {weather_info}\n"
        f"Hotel Info: {hotel_info}\n\n"
        "Please output the updated TripSchema."
    )
    
    try:
        updated_plan = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        return {"trip_plan": updated_plan}
    except Exception as e:
        print(f"Error refining itinerary: {e}")
        return {} # Keep original plan on error


from langgraph.prebuilt import create_react_agent
from travel_assistant.backend.agents.tools import run_simple_tool_agent, tool_llm


async def attraction_search_agent(state: TravelState) -> TravelState:
    """Agent that searches for attractions using MCP."""
    destination = state.get("destination")
    trip_plan = state.get("trip_plan")
    
    if not destination:
        return {"attractions_info": "No destination specified for attraction search."}

    # If we have a plan, search for the specific attractions in it
    targets = []
    if trip_plan and hasattr(trip_plan, "itinerary") and trip_plan.itinerary:
        for day in trip_plan.itinerary:
            for node in day.nodes:
                if node.type in ["attraction", "activity", "sight"]:
                    targets.append(node.name)
    
    if targets:
        items = ", ".join(targets[:5]) # Search for top 5 to avoid long queries
        prompt = f"Find details (ticket price, opening hours) for these attractions in {destination}: {items}. Provide a concise summary."
    else:
        prompt = f"Find top attractions and sights in {destination}. Provide a concise summary."
    
    print(f"DEBUG - Attraction Agent Prompt: {prompt}")

    try:
        # Invoke the sub-agent using robust helper
        content = await run_simple_tool_agent(prompt, [search_destinations], tool_llm)
        return {"attractions_info": content}
    except Exception as e:
        return {"attractions_info": f"Failed to fetch attractions: {str(e)}"}


async def weather_query_agent(state: TravelState) -> TravelState:
    """Agent that queries weather using MCP."""
    destination = state.get("destination")
    trip_plan = state.get("trip_plan")
    
    if not destination:
        return {"weather_info": "No destination specified for weather query."}

    dates = state.get("travel_dates", {}) or {}
    start_date = dates.get("start", "today")
    
    # Use plan dates if available
    if trip_plan and trip_plan.start_date:
        start_date = trip_plan.start_date
    
    prompt = f"Check the weather in {destination} for {start_date}. Provide a concise summary."

    print(f"DEBUG - Weather Agent Prompt: {prompt}")

    try:
        content = await run_simple_tool_agent(prompt, [get_weather], tool_llm)
        return {"weather_info": content}
    except Exception as e:
        return {"weather_info": f"Failed to fetch weather: {str(e)}"}


async def hotel_info_agent(state: TravelState) -> TravelState:
    """Agent that searches for hotels using MCP."""
    destination = state.get("destination")
    trip_plan = state.get("trip_plan")
    
    if not destination:
        return {"hotel_info": "No destination specified for hotel search."}

    dates = state.get("travel_dates", {}) or {}
    start_date = dates.get("start", "today")
    end_date = dates.get("end", "tomorrow")
    
    if trip_plan and trip_plan.start_date and trip_plan.end_date:
        start_date = trip_plan.start_date
        end_date = trip_plan.end_date

    # If we have a plan, check for specific hotels
    targets = []
    if trip_plan and hasattr(trip_plan, "itinerary") and trip_plan.itinerary:
        for day in trip_plan.itinerary:
            for node in day.nodes:
                if node.type in ["hotel", "accommodation", "lodging"]:
                    targets.append(node.name)
    
    if targets:
         items = ", ".join(targets[:3])
         prompt = f"Find prices and availability for these hotels in {destination} from {start_date} to {end_date}: {items}. Provide a concise summary."
    else:
        prompt = f"Find available hotels in {destination} from {start_date} to {end_date}. Provide a concise summary."

    print(f"DEBUG - Hotel Agent Prompt: {prompt}")

    try:
        content = await run_simple_tool_agent(prompt, [search_hotels], tool_llm)
        return {"hotel_info": content}
    except Exception as e:
        return {"hotel_info": f"Failed to fetch hotels: {str(e)}"}

