import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from travel_assistant.backend.agents.nodes import process_input
from travel_assistant.backend.state import TravelState

load_dotenv()

def test_process_input():
    # Mock a conversation history
    mock_messages = [
        HumanMessage(content="Hi! I want to plan a trip to Tokyo."),
        HumanMessage(content="I'm thinking of going from April 1st to April 5th, 2025."),
        HumanMessage(content="My budget is around $2000 and I love anime and food.")
    ]
    
    mock_state: TravelState = {
        "messages": mock_messages,
        "destination": None,
        "travel_dates": None,
        "preferences": None,
        "trip_plan": None
    }
    
    print("Invoking process_input...")
    result_state = process_input(mock_state)
    
    print("\nResult State Updates:")
    print(f"Destination: {result_state.get('destination')}")
    print(f"Dates: {result_state.get('travel_dates')}")
    print(f"Preferences: {result_state.get('preferences')}")

if __name__ == "__main__":
    test_process_input()
