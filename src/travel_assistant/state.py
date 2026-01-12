"""State definitions for the travel assistant graph."""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class TravelState(TypedDict):
    """The state of the travel assistant graph.

    Attributes:
        messages: The conversation messages, using LangGraph's add_messages reducer.
        destination: The travel destination (if specified).
        travel_dates: The travel dates (if specified).
        preferences: User preferences for the trip.
    """

    messages: Annotated[list, add_messages]
    destination: str | None
    travel_dates: dict | None
    preferences: dict | None
