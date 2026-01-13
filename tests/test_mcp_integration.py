
import asyncio
import unittest
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage
from travel_assistant.backend.graph import graph
from travel_assistant.backend.prompts import (
    INPUT_EXTRACTION_SYSTEM_PROMPT,
    PLANNER_SYSTEM_PROMPT,
    RESPONSE_SYSTEM_PROMPT,
)
from travel_assistant.backend.schemas import InputSchema, TripSchema

class TestMCPIntegration(unittest.TestCase):
    @patch("travel_assistant.backend.tools.call_mcp_tool")
    def test_graph_flow(self, mock_call_mcp):
        # Setup mock returns for MCP tools
        mock_call_mcp.side_effect = [
            "Eiffel Tower, Louvre",  # Attraction
            "Sunny, 20C",            # Weather
            "Hotel Ritz",            # Hotel
        ]

        # Initial state
        # We provide enough info so extraction might be redundant but will run
        initial_state = {
            "messages": [],
            "destination": "Paris",
            "travel_dates": {"start": "2024-06-01", "end": "2024-06-05"},
            "preferences": {"interests": ["art"]},
        }

        with patch("travel_assistant.backend.agents.nodes.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            
            def mock_invoke_side_effect(input_msgs, *args, **kwargs):
                # input_msgs is usually a list of messages
                # Check first message for system prompt
                if not input_msgs or not hasattr(input_msgs[0], "content"):
                    return AIMessage(content="Fallback")
                
                system_prompt = input_msgs[0].content
                
                if system_prompt == INPUT_EXTRACTION_SYSTEM_PROMPT:
                    return InputSchema(
                        destination="Paris", 
                        start_date="2024-06-01", 
                        end_date="2024-06-05", 
                        interests=["art"]
                    )
                elif system_prompt == PLANNER_SYSTEM_PROMPT:
                    return TripSchema(
                        destination="Paris", 
                        itinerary=[], 
                        notes=[], 
                        budget="1000", 
                        travelers=1
                    )
                elif system_prompt == RESPONSE_SYSTEM_PROMPT:
                    return AIMessage(content="Enjoy your trip to Paris!")
                else:
                    return AIMessage(content="Unknown prompt")

            mock_llm.invoke.side_effect = mock_invoke_side_effect
            mock_get_llm.return_value = mock_llm
            
            # Using asyncio.run for async graph
            # This requires 'ainvoke'
            result = asyncio.run(graph.ainvoke(initial_state))
            
            # Verify flow and state updates
            self.assertIn("attractions_info", result)
            self.assertEqual(result["attractions_info"], "Eiffel Tower, Louvre")
            
            self.assertIn("weather_info", result)
            self.assertEqual(result["weather_info"], "Sunny, 20C")
            
            self.assertIn("hotel_info", result)
            self.assertEqual(result["hotel_info"], "Hotel Ritz")
            
            # Verify MCP calls count
            # Expect 3 calls: Attraction, Weather, Hotel
            self.assertEqual(mock_call_mcp.call_count, 3)
            
            # Verify specific call args
            # First call should be Attraction
            args0, _ = mock_call_mcp.call_args_list[0]
            self.assertEqual(args0[2], "search_destinations")  # tool_name
            self.assertEqual(args0[3], {"query": "Paris"})     # tool_args

if __name__ == "__main__":
    unittest.main()
