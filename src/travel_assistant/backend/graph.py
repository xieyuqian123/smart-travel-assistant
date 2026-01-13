"""Main graph definition for the travel assistant."""

from langgraph.graph import END, StateGraph

from travel_assistant.backend.agents.nodes import (
    attraction_search_agent,
    generate_response,
    hotel_info_agent,
    plan_itinerary,
    process_input,
    weather_query_agent,
)
from travel_assistant.backend.state import TravelState

# Create the graph
builder = StateGraph(TravelState)

# Add nodes
builder.add_node("process_input", process_input)
builder.add_node("attraction_search_agent", attraction_search_agent)
builder.add_node("weather_query_agent", weather_query_agent)
builder.add_node("hotel_info_agent", hotel_info_agent)
builder.add_node("plan_itinerary", plan_itinerary)
builder.add_node("generate_response", generate_response)

# Define the graph flow
builder.set_entry_point("process_input")
builder.add_edge("process_input", "attraction_search_agent")
builder.add_edge("attraction_search_agent", "weather_query_agent")
builder.add_edge("weather_query_agent", "hotel_info_agent")
builder.add_edge("hotel_info_agent", "plan_itinerary")
builder.add_edge("plan_itinerary", "generate_response")
builder.add_edge("generate_response", END)

# Compile the graph
graph = builder.compile()
