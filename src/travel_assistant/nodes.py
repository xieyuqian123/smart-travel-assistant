"""Node definitions for the travel assistant graph."""

from langchain_core.messages import HumanMessage, SystemMessage

from travel_assistant.config import get_llm
from travel_assistant.prompts import PLANNER_SYSTEM_PROMPT, get_planner_user_prompt
from travel_assistant.schemas import TripSchema
from travel_assistant.state import TravelState


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
    # TODO: Implement input processing logic
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
    # TODO: Implement response generation logic
    return state
