
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
from travel_assistant.backend.schemas import InputSchema, TripSchema, DailyItinerarySchema, TripNodeSchema

class TestRePlanning(unittest.TestCase):
    @patch("travel_assistant.backend.agents.nodes.attraction_agent_executor.ainvoke")
    @patch("travel_assistant.backend.agents.nodes.weather_agent_executor.ainvoke")
    @patch("travel_assistant.backend.agents.nodes.hotel_agent_executor.ainvoke")
    def test_re_planning_flow(self, mock_hotel, mock_weather, mock_attraction):
        # Mocks for sub-agents
        mock_attraction.return_value = {"messages": [AIMessage(content="Attractions")]}
        mock_weather.return_value = {"messages": [AIMessage(content="Weather")]}
        mock_hotel.return_value = {"messages": [AIMessage(content="Hotels")]}

        # Initial state with a budget
        initial_state = {
            "messages": [],
            "destination": "Paris",
            "travel_dates": {"start": "2024-06-01", "end": "2024-06-05"},
            "preferences": {"interests": ["art"]},
        }

        # Mock LLM to simulate over-budget then within-budget plans
        with patch("travel_assistant.backend.agents.nodes.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            
            # We need to track how many times the planner has been called to switch responses
            planner_call_count = 0
            
            def mock_invoke_side_effect(input_msgs, *args, **kwargs):
                nonlocal planner_call_count
                
                if not input_msgs:
                    return AIMessage(content="Fallback")
                
                system_prompt = input_msgs[0].content
                
                if system_prompt == INPUT_EXTRACTION_SYSTEM_PROMPT:
                    return InputSchema(
                        destination="Paris", 
                        start_date="2024-06-01", 
                        end_date="2024-06-05", 
                        interests=["art"],
                        budget="500" # User sets $500 budget
                    )
                elif system_prompt == PLANNER_SYSTEM_PROMPT:
                    planner_call_count += 1
                    user_prompt = input_msgs[1].content
                    
                    if planner_call_count == 1:
                        # First attempt: Over budget ($600)
                        return TripSchema(
                            destination="Paris", 
                            budget="500",
                            itinerary=[
                                DailyItinerarySchema(
                                    day=1, summary="Expensive Day",
                                    nodes=[TripNodeSchema(name="Luxury Hotel", description="Stay", cost="$600")]
                                )
                            ]
                        )
                    else:
                        # Second attempt: Within budget ($400)
                        # Check if feedback was in the prompt
                        if "IMPORTANT FEEDBACK FROM PREVIOUS ATTEMPT" not in user_prompt:
                            raise ValueError("Feedback not found in prompt during retry!")
                            
                        return TripSchema(
                            destination="Paris", 
                            budget="500",
                            itinerary=[
                                DailyItinerarySchema(
                                    day=1, summary="Cheap Day",
                                    nodes=[TripNodeSchema(name="Budget Hostel", description="Stay", cost="$400")]
                                )
                            ]
                        )
                        
                elif system_prompt == RESPONSE_SYSTEM_PROMPT:
                    return AIMessage(content="Here is your trip within budget!")
                else:
                    return AIMessage(content="Unknown prompt")

            mock_llm.invoke.side_effect = mock_invoke_side_effect
            mock_get_llm.return_value = mock_llm
            
            # Run graph
            result = asyncio.run(graph.ainvoke(initial_state))
            
            # Verifications
            self.assertEqual(result["budget_status"], "OK")
            self.assertEqual(planner_call_count, 2) # Should have replanned once
            self.assertIn("planner_feedback", result)

if __name__ == "__main__":
    unittest.main()
