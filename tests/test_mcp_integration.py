
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
    @patch("travel_assistant.backend.agents.nodes.attraction_agent_executor.ainvoke")
    @patch("travel_assistant.backend.agents.nodes.weather_agent_executor.ainvoke")
    @patch("travel_assistant.backend.agents.nodes.hotel_agent_executor.ainvoke")
    def test_graph_flow(self, mock_hotel, mock_weather, mock_attraction):
        # Setup mock returns for Sub-Agents
        mock_attraction.return_value = {"messages": [AIMessage(content="Eiffel Tower, Louvre")]}
        mock_weather.return_value = {"messages": [AIMessage(content="Sunny, 20C")]}
        mock_hotel.return_value = {"messages": [AIMessage(content="Hotel Ritz")]}

        # Initial state
        initial_state = {
            "messages": [],
            "destination": "Paris",
            "travel_dates": {"start": "2024-06-01", "end": "2024-06-05"},
            "preferences": {"interests": ["art"]},
        }

        with patch("travel_assistant.backend.agents.nodes.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            
            def mock_invoke_side_effect(input_msgs, *args, **kwargs):
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
            result = asyncio.run(graph.ainvoke(initial_state))
            
            # Verify flow and state updates
            self.assertIn("attractions_info", result)
            self.assertEqual(result["attractions_info"], "Eiffel Tower, Louvre")
            
            self.assertIn("weather_info", result)
            self.assertEqual(result["weather_info"], "Sunny, 20C")
            
            self.assertIn("hotel_info", result)
            self.assertEqual(result["hotel_info"], "Hotel Ritz")
            
            # Verify sub-agents were called
            mock_attraction.assert_called_once()
            mock_weather.assert_called_once()
            mock_hotel.assert_called_once()

if __name__ == "__main__":
    unittest.main()
