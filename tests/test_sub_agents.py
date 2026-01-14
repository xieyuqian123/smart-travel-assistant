
import asyncio
import unittest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage

from travel_assistant.backend.agents.nodes import (
    attraction_search_agent,
    weather_query_agent,
    hotel_info_agent
)

class TestSubAgents(unittest.TestCase):
    


    @patch("travel_assistant.backend.agents.nodes.attraction_agent_executor.ainvoke")
    def test_attraction_agent_execution(self, mock_ainvoke):
        # Setup mock return
        mock_ainvoke.return_value = {
            "messages": [AIMessage(content="Eiffel Tower is great.")]
        }
        
        state = {"destination": "Paris"}
        result = asyncio.run(attraction_search_agent(state))
        
        self.assertEqual(result["attractions_info"], "Eiffel Tower is great.")
        mock_ainvoke.assert_called_once()
        
    @patch("travel_assistant.backend.agents.nodes.weather_agent_executor.ainvoke")
    def test_weather_agent_execution(self, mock_ainvoke):
        mock_ainvoke.return_value = {
            "messages": [AIMessage(content="Sunny 25C.")]
        }
        
        state = {"destination": "Paris", "travel_dates": {"start": "2024-06-01"}}
        result = asyncio.run(weather_query_agent(state))
        
        self.assertEqual(result["weather_info"], "Sunny 25C.")

    @patch("travel_assistant.backend.agents.nodes.hotel_agent_executor.ainvoke")
    def test_hotel_agent_execution(self, mock_ainvoke):
        mock_ainvoke.return_value = {
            "messages": [AIMessage(content="Hotel Ritz is available.")]
        }
        
        state = {"destination": "Paris", "travel_dates": {"start": "2024-06-01", "end": "2024-06-02"}}
        result = asyncio.run(hotel_info_agent(state))
        
        self.assertEqual(result["hotel_info"], "Hotel Ritz is available.")

if __name__ == "__main__":
    unittest.main()
