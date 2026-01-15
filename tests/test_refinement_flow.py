
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

class TestRefinementFlow(unittest.TestCase):
    @patch("travel_assistant.backend.agents.nodes.attraction_agent_executor.ainvoke")
    @patch("travel_assistant.backend.agents.nodes.weather_agent_executor.ainvoke")
    @patch("travel_assistant.backend.agents.nodes.hotel_agent_executor.ainvoke")
    def test_refinement_pipeline(self, mock_hotel, mock_weather, mock_attraction):
        # Mocks
        mock_attraction.return_value = {"messages": [AIMessage(content="Attraction info")]}
        mock_weather.return_value = {"messages": [AIMessage(content="Weather info")]}
        mock_hotel.return_value = {"messages": [AIMessage(content="Hotel info found: ExpensiveHotel is $600")]}

        # Initial state
        initial_state = {
            "messages": [],
            "destination": "TestCity",
        }

        with patch("travel_assistant.backend.agents.nodes.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            
            def mock_invoke_side_effect(input_msgs, *args, **kwargs):
                if not input_msgs: return AIMessage(content="Fallback")
                
                system_prompt = input_msgs[0].content
                
                # 1. Extraction
                if system_prompt == INPUT_EXTRACTION_SYSTEM_PROMPT:
                    return InputSchema(destination="TestCity", budget="500")
                
                # 2. Planner (Initial draft, low/no cost)
                elif system_prompt == PLANNER_SYSTEM_PROMPT:
                    # Note: In new flow, this runs BEFORE agents. It doesn't know costs yet
                    return TripSchema(
                        destination="TestCity", 
                        budget="500",
                        itinerary=[
                            DailyItinerarySchema(
                                day=1, summary="Day 1",
                                nodes=[TripNodeSchema(name="ExpensiveHotel", description="Stay", cost="?")]
                            )
                        ]
                    )
                
                # 3. Refinement Node
                elif "You are a travel assistant editor" in system_prompt:
                    # This node sees the agent info ($600) and updates the plan
                    user_prompt = input_msgs[1].content
                    
                    # Check if we are refining the cheap plan
                    if "CheapHotel" in user_prompt:
                         return TripSchema(
                            destination="TestCity", 
                            budget="500",
                            itinerary=[
                                DailyItinerarySchema(
                                    day=1, summary="Day 1",
                                    nodes=[TripNodeSchema(name="CheapHotel", description="Stay", cost="400")]
                                )
                            ]
                        )
                    
                    # Otherwise refining the expensive plan
                    if "Hotel info found: ExpensiveHotel is $600" not in user_prompt:
                         raise ValueError("Refinement node didn't receive hotel info!")
                         
                    return TripSchema(
                        destination="TestCity", 
                        budget="500",
                        itinerary=[
                            DailyItinerarySchema(
                                day=1, summary="Day 1",
                                nodes=[TripNodeSchema(name="ExpensiveHotel", description="Stay", cost="600")]
                            )
                        ]
                    )
                    
                # 4. Response (if budget OK or planner retries)
                elif system_prompt == RESPONSE_SYSTEM_PROMPT:
                    return AIMessage(content="Plan ready!")
                
                # 5. Planner Retry (if triggered by budget check)
                # Currently we loop back to plan_itinerary if over budget.
                # In this test, we expect OVER_BUDGET status after refinement updates cost to 600 vs budget 500
                
                else:
                    return AIMessage(content="Unknown prompt")

            mock_llm.invoke.side_effect = mock_invoke_side_effect
            mock_get_llm.return_value = mock_llm
            
            # Exec
            # We must use proper handling since it's a loop. But unittest limits loop runs usually.
            # We just want to check the state after one pass or ensure flow hits refinement.
            
            # Since graph loops on OVER_BUDGET, we might get stuck if we don't handle the retry in mock.
            # Let's adjust mock: if feedback is present (retry), return cheaper plan.
            
            original_invoke = mock_llm.invoke.side_effect
            def smart_invoke(input_msgs, *args, **kwargs):
                # Check for feedback in planner prompt
                if len(input_msgs) > 1 and "IMPORTANT FEEDBACK FROM PREVIOUS ATTEMPT" in input_msgs[1].content:
                     return TripSchema(
                        destination="TestCity", 
                        budget="500",
                        itinerary=[
                            DailyItinerarySchema(
                                day=1, summary="Day 1",
                                nodes=[TripNodeSchema(name="CheapHotel", description="Stay", cost="400")]
                            )
                        ]
                    )
                return original_invoke(input_msgs, *args, **kwargs)
            
            mock_llm.invoke.side_effect = smart_invoke

            result = asyncio.run(graph.ainvoke(initial_state))
            
            # Assertions
            self.assertIn("refine_itinerary", str(graph.nodes.keys())) # indirectly checking graph has node
            # Ideally check execution trace, but result state tells us:
            # 1. Did we get budget status?
            # 2. Did we get a final response?
            self.assertEqual(result["budget_status"], "OK")
            # If we succeeded, it means we likely replanned or the mock handled it.
            
            # To strictly prove "Refine" ran, we can check if Hotel Info was in the prompt of Refine.
            # (Validated by the raise ValueError in mock)

if __name__ == "__main__":
    unittest.main()
