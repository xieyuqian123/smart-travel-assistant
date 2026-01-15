
import unittest
from travel_assistant.backend.schemas import TripSchema, DailyItinerarySchema, TripNodeSchema
from travel_assistant.backend.tools.calculator import calculate_itinerary_cost, parse_cost

class TestCalculator(unittest.TestCase):
    def test_parse_cost(self):
        self.assertEqual(parse_cost("$100"), 100.0)
        self.assertEqual(parse_cost("500.50"), 500.50)
        self.assertEqual(parse_cost("approx 200 EUR"), 200.0)
        self.assertEqual(parse_cost("Free"), 0.0)
        self.assertEqual(parse_cost(None), 0.0)
        self.assertEqual(parse_cost(""), 0.0)

    def test_calculate_itinerary_cost(self):
        trip_plan = TripSchema(
            destination="Test City",
            itinerary=[
                DailyItinerarySchema(
                    day=1,
                    summary="Day 1",
                    nodes=[
                        TripNodeSchema(name="Hotel", description="Stay", cost="$200"),
                        TripNodeSchema(name="Lunch", description="Food", cost="50")
                    ]
                ),
                DailyItinerarySchema(
                    day=2,
                    summary="Day 2",
                    nodes=[
                        TripNodeSchema(name="Museum", description="Art", cost="20 EUR"),
                    ]
                )
            ]
        )
        total = calculate_itinerary_cost(trip_plan)
        self.assertEqual(total, 270.0)

if __name__ == "__main__":
    unittest.main()
