"""Tool definitions for the travel assistant."""

from langchain_core.tools import tool


@tool
def search_destinations(query: str) -> str:
    """Search for travel destinations based on a query.

    Args:
        query: The search query for destinations.

    Returns:
        Information about matching destinations.
    """
    # TODO: Implement destination search logic
    return f"Searching for destinations matching: {query}"


@tool
def get_weather(location: str, date: str) -> str:
    """Get weather information for a location and date.

    Args:
        location: The location to get weather for.
        date: The date to get weather for (YYYY-MM-DD format).

    Returns:
        Weather information for the specified location and date.
    """
    # TODO: Implement weather lookup logic
    return f"Weather for {location} on {date}: Sunny, 25°C"


@tool
def search_hotels(location: str, check_in: str, check_out: str) -> str:
    """Search for hotels in a location.

    Args:
        location: The location to search hotels in.
        check_in: Check-in date (YYYY-MM-DD format).
        check_out: Check-out date (YYYY-MM-DD format).

    Returns:
        List of available hotels.
    """
    # TODO: Implement hotel search logic
    return f"Hotels in {location} from {check_in} to {check_out}"


@tool
def search_restaurants(location: str, cuisine: str | None = None) -> str:
    """Search for restaurants in a location.

    Args:
        location: The location to search restaurants in.
        cuisine: Optional cuisine type filter.

    Returns:
        List of recommended restaurants.
    """
    # TODO: Implement restaurant search logic
    cuisine_str = f" ({cuisine} cuisine)" if cuisine else ""
    return f"Restaurants in {location}{cuisine_str}"


# List of all available tools
tools = [
    search_destinations,
    get_weather,
    search_hotels,
    search_restaurants,
]
