import os
import json
from dotenv import load_dotenv
from travel_assistant.nodes import plan_itinerary
from travel_assistant.state import TravelState

load_dotenv()

def generate_json_output():
    mock_state: TravelState = {
        "messages": [],
        "destination": "Kyoto",
        "travel_dates": {"start": "2025-04-01", "end": "2025-04-03"},
        "preferences": {"interests": ["temples", "food", "anime"]},
        "trip_plan": None
    }
    
    result_state = plan_itinerary(mock_state)
    trip_plan = result_state.get("trip_plan")
    
    if trip_plan:
        print(trip_plan.model_dump_json(indent=2))
    else:
        print("Error: Could not generate trip plan")

if __name__ == "__main__":
    generate_json_output()
