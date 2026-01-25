import os
import sys
# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from dotenv import load_dotenv
from travel_assistant.backend.agents.nodes import plan_itinerary
from travel_assistant.backend.state import TravelState

load_dotenv()

def test_weather_planner():
    # Test Case 1: Raining
    print("Testing Rainy Weather Scenario...")
    mock_state_rain: TravelState = {
        "messages": [],
        "destination": "London",
        "travel_dates": {"start": "2025-04-01", "end": "2025-04-01"},
        "preferences": {"interests": ["sightseeing"]},
        "weather_info": "Heavy rain expected all day. Temperature 10deg C.",
        "trip_plan": None
    }
    
    result_rain = plan_itinerary(mock_state_rain)
    plan_rain = result_rain.get("trip_plan")
    
    if plan_rain:
        print("Success! Plan generated.")
        for day in plan_rain.itinerary:
            print(f"  Day {day.day}: {day.summary}")
            for node in day.nodes:
                print(f"    - {node.name} ({node.type}) - {node.description}")
    else:
        print("Failed to generate plan.")

    # Test Case 2: Sunny
    print("\nTesting Sunny Weather Scenario...")
    mock_state_sun: TravelState = {
        "messages": [],
        "destination": "London",
        "travel_dates": {"start": "2025-04-01", "end": "2025-04-01"},
        "preferences": {"interests": ["sightseeing"]},
        "weather_info": "Sunny and clear. Temperature 25deg C.",
        "trip_plan": None
    }
    
    result_sun = plan_itinerary(mock_state_sun)
    plan_sun = result_sun.get("trip_plan")
    
    if plan_sun:
        print("Success! Plan generated.")
        for day in plan_sun.itinerary:
            print(f"  Day {day.day}: {day.summary}")
            for node in day.nodes:
                print(f"    - {node.name} ({node.type}) - {node.description}")
    else:
        print("Failed to generate plan.")

if __name__ == "__main__":
    test_weather_planner()
