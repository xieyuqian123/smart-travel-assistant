import os
from dotenv import load_dotenv
from travel_assistant.backend.agents.nodes import plan_itinerary
from travel_assistant.backend.state import TravelState

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY not found in environment. Please set it in .env")
    # For the agent run, I might need to ask the user, but let's try assuming it might work or fail gracefully.

def test_planner():
    mock_state: TravelState = {
        "messages": [],
        "destination": "Kyoto",
        "travel_dates": {"start": "2025-04-01", "end": "2025-04-03"},
        "preferences": {"interests": ["temples", "food", "anime"]},
        "trip_plan": None
    }
    
    print("Invoking plan_itinerary...")
    result_state = plan_itinerary(mock_state)
    
    trip_plan = result_state.get("trip_plan")
    if trip_plan:
        print("\nSuccessfully generated TripPlan!")
        print(f"Destination: {trip_plan.destination}")
        print(f"Budget: {trip_plan.budget}")
        print(f"Itinerary Days: {len(trip_plan.itinerary)}")
        for day in trip_plan.itinerary:
            print(f"  Day {day.day}: {day.summary}")
            for node in day.nodes:
                print(f"    - {node.name} ({node.type})")
    else:
        print("Failed to generate trip plan.")

if __name__ == "__main__":
    test_planner()
