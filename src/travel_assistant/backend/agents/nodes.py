"""Node definitions for the travel assistant graph."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from travel_assistant.backend.config import get_llm
from travel_assistant.backend.prompts import INPUT_EXTRACTION_SYSTEM_PROMPT, PLANNER_SYSTEM_PROMPT, RESPONSE_SYSTEM_PROMPT, get_planner_user_prompt
from travel_assistant.backend.schemas import InputSchema, TripSchema
from travel_assistant.backend.state import TravelState


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

