import os
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel

from travel_assistant.nodes import generate_response
from travel_assistant.state import TravelState
from travel_assistant.schemas import TripSchema, DailyItinerarySchema, TripNodeSchema, CoordinateSchema, NoteSchema

load_dotenv()

def test_generate_response():
    # Mock data directly to avoid needing LLM for planning phase
    mock_itinerary = [
        DailyItinerarySchema(
            day=1,
            summary="Arrival in Kyoto",
            nodes=[
                TripNodeSchema(
                    name="Kyoto Station",
                    description="Arrive at Kyoto Station",
                    type="transport"
                )
            ]
        )
    ]
    
    mock_plan = TripSchema(
        destination="Kyoto",
        itinerary=mock_itinerary,
        notes=[NoteSchema(category="General", content="Have fun!")]
    )

    mock_state: TravelState = {
        "messages": [],
        "destination": "Kyoto",
        "travel_dates": {"start": "2025-04-01", "end": "2025-04-03"},
        "preferences": {},
        "trip_plan": mock_plan
    }
    
    print("Invoking generate_response...")
    result = generate_response(mock_state)
    
    messages = result.get("messages", [])
    if messages:
        print("\nGenerated Response:")
        print(messages[-1].content)
    else:
        print("No response generated.")

if __name__ == "__main__":
    test_generate_response()
