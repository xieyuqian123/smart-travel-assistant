"""Tool definitions for the travel assistant using MCP."""

import os
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call_mcp_tool(
    command: str,
    args: List[str],
    tool_name: str,
    tool_args: Dict[str, Any],
    env: Optional[Dict[str, str]] = None,
) -> str:
    """Connect to an MCP server and call a tool."""
    try:
        if not command:
            return f"Error: No command configured for {tool_name}"

        server_params = StdioServerParameters(command=command, args=args, env=env)

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(tool_name, tool_args)

                if result.isError:
                    return f"Tool execution failed: {result.content}"

                text_output = "\n".join(
                    [c.text for c in result.content if c.type == "text"]
                )
                return text_output

    except Exception as e:
        return f"Error calling MCP tool {tool_name}: {str(e)}"


# Default configurations (can be overridden by env vars or config)
# Using placeholder "python3" and "-m mcp_server_..." for now.
ATTRACTION_CMD = os.environ.get("ATTRACTION_MCP_CMD", "python3")
ATTRACTION_ARGS = os.environ.get(
    "ATTRACTION_MCP_ARGS", "-m mcp_server_attraction"
).split()

WEATHER_CMD = os.environ.get("WEATHER_MCP_CMD", "python3")
WEATHER_ARGS = os.environ.get("WEATHER_MCP_ARGS", "-m mcp_server_weather").split()

HOTEL_CMD = os.environ.get("HOTEL_MCP_CMD", "python3")
HOTEL_ARGS = os.environ.get("HOTEL_MCP_ARGS", "-m mcp_server_hotel").split()


@tool
async def search_destinations(query: str) -> str:
    """Search for travel destinations based on a query.

    Args:
        query: The search query for destinations.
    """
    return await call_mcp_tool(
        ATTRACTION_CMD, ATTRACTION_ARGS, "search_destinations", {"query": query}
    )


@tool
async def get_weather(location: str, date: str) -> str:
    """Get weather information.

    Args:
        location: City/Place name
        date: Date in YYYY-MM-DD
    """
    return await call_mcp_tool(
        WEATHER_CMD, WEATHER_ARGS, "get_weather", {"location": location, "date": date}
    )


@tool
async def search_hotels(location: str, check_in: str, check_out: str) -> str:
    """Search for hotels.

    Args:
        location: City/Place name
        check_in: YYYY-MM-DD
        check_out: YYYY-MM-DD
    """
    return await call_mcp_tool(
        HOTEL_CMD,
        HOTEL_ARGS,
        "search_hotels",
        {"location": location, "check_in": check_in, "check_out": check_out},
    )


@tool
async def search_restaurants(location: str, cuisine: Optional[str] = None) -> str:
    """Search for restaurants in a location.

    Args:
        location: The location to search restaurants in.
        cuisine: Optional cuisine type filter.

    Returns:
        List of recommended restaurants.
    """
    # Placeholder for non-MCP tool or future implementation
    cuisine_str = f" ({cuisine} cuisine)" if cuisine else ""
    return f"Restaurants in {location}{cuisine_str} (Mock Data)"


tools = [search_destinations, get_weather, search_hotels, search_restaurants]
