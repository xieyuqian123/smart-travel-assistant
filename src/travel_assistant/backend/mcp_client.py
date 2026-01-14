import asyncio
import os
from typing import Any, Dict, List, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClientManager:
    """Generic Manager for connecting to MCP servers."""

    def __init__(
        self,
        command: str,
        args: List[str],
        env: Optional[Dict[str, str]] = None,
        server_name: str = "mcp_server",
    ):
        """Initialize the MCP client manager.

        Args:
            command: The executable command to run the server (e.g., "python3").
            args: List of arguments for the command (e.g., ["-m", "amap_mcp_server"]).
            env: Environment variables to pass to the server process.
            server_name: A human-readable name for logging/debugging.
        """
        self.command = command
        self.args = args
        self.env = env or os.environ.copy()
        self.server_name = server_name

    async def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Connect to the MCP server and execute a tool.

        Args:
            tool_name: The name of the tool to execute.
            tool_args: Dictionary of arguments for the tool.

        Returns:
            The text output from the tool execution.
        """
        try:
            server_params = StdioServerParameters(
                command=self.command, args=self.args, env=self.env
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    result = await session.call_tool(tool_name, tool_args)

                    if result.isError:
                        return f"Error executing {tool_name} on {self.server_name}: {result.content}"

                    text_output = "\n".join(
                        [c.text for c in result.content if c.type == "text"]
                    )
                    return text_output

        except Exception as e:
            return f"Error calling {self.server_name} tool {tool_name}: {str(e)}"

    async def list_tools(self) -> Any:
        """List available tools on the MCP server.

        Returns:
            The list of tools returned by the server.
        """
        try:
            server_params = StdioServerParameters(
                command=self.command, args=self.args, env=self.env
            )

            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return await session.list_tools()

        except Exception as e:
            return f"Error listing tools on {self.server_name}: {str(e)}"
