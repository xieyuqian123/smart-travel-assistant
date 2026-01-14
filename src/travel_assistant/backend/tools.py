from typing import Any, Dict, List, Optional
import os
import sys

from langchain_core.tools import tool
from travel_assistant.backend.mcp_client import MCPClientManager

# AMap Configuration
AMAP_API_KEY = os.environ.get("AMAP_MAPS_API_KEY")

# Initialize AMap MCP Manager
# We assume the amap-mcp-server is installed and runnable via "python3 -m amap_mcp_server"
# or similar. Adjust command/args as per actual package structure.
AMAP_CMD = os.environ.get("AMAP_MCP_CMD", sys.executable)
AMAP_ARGS = os.environ.get("AMAP_MCP_ARGS", "-m amap_mcp_server").split()

amap_env = os.environ.copy()
if AMAP_API_KEY:
    amap_env["AMAP_MAPS_API_KEY"] = AMAP_API_KEY

amap_manager = MCPClientManager(
    command=AMAP_CMD,
    args=AMAP_ARGS,
    env=amap_env,
    server_name="amap_mcp_server"
)


@tool
async def search_destinations(query: str) -> str:
    """Search for travel destinations based on a query.

    Args:
        query: The search query for destinations.
    """
    # Mapping to AMap tool: maps_text_search
    return await amap_manager.execute_tool(
        "maps_text_search", {"keywords": query, "citylimit": "false"}
    )


@tool
async def get_weather(location: str, city_adcode: str = "") -> str:
    """Get weather information.

    Args:
        location: City/Place name (for display/context).
        city_adcode: The adcode of the city (required by AMap weather, or city name).
    """
    # Mapping to AMap tool: maps_weather
    # AMap 'maps_weather' takes 'city' arg (adcode or name)
    return await amap_manager.execute_tool(
        "maps_weather", {"city": city_adcode if city_adcode else location}
    )


@tool
async def search_hotels(location: str, keyword: str = "hotel") -> str:
    """Search for hotels.

    Args:
        location: City/Place name or adcode.
        keyword: Keyword to search (default: "hotel").
    """
    return await amap_manager.execute_tool(
        "maps_text_search", {"keywords": keyword, "city": location}
    )


@tool
async def search_restaurants(location: str, cuisine: Optional[str] = None) -> str:
    """Search for restaurants in a location.

    Args:
        location: The location/city to search restaurants in.
        cuisine: Optional cuisine type filter.

    Returns:
        List of recommended restaurants.
    """
    query = f"{cuisine} restaurant" if cuisine else "restaurant"
    return await amap_manager.execute_tool(
        "maps_text_search", {"keywords": query, "city": location}
    )


tools = [search_destinations, get_weather, search_hotels, search_restaurants]
