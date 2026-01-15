import re
from typing import Optional
from travel_assistant.backend.schemas import TripSchema, TripNodeSchema

def parse_cost(cost_str: Optional[str]) -> float:
    """Parses a cost string into a float.
    
    Handles formats like "$100", "500 CNY", "approx 50 EUR".
    Returns 0.0 if parsing fails or input is None.
    """
    if not cost_str:
        return 0.0
    
    # Remove currency symbols and non-numeric chars except dot
    # This is a basic implementation; robust parsing might need a library
    cleaned = re.sub(r'[^\d.]', '', cost_str)
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def calculate_itinerary_cost(trip_plan: TripSchema) -> float:
    """Calculates the total estimated cost of the trip itinerary.
    
    Sums up costs from all nodes in the itinerary.
    """
    total_cost = 0.0
    
    for day in trip_plan.itinerary:
        for node in day.nodes:
            total_cost += parse_cost(node.cost)
            
    return total_cost
