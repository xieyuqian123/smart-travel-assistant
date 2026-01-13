"""Tests for the travel assistant graph."""

import pytest

from travel_assistant.backend.graph import graph
from travel_assistant.backend.state import TravelState


class TestTravelAssistantGraph:
    """Test suite for the travel assistant graph."""

    def test_graph_exists(self):
        """Test that the graph is properly compiled."""
        assert graph is not None

    def test_graph_has_nodes(self):
        """Test that the graph has the expected nodes."""
        # Get node names from the graph
        node_names = list(graph.nodes.keys())
        
        expected_nodes = ["process_input", "plan_itinerary", "generate_response"]
        for node in expected_nodes:
            assert node in node_names, f"Expected node '{node}' not found in graph"

    def test_state_structure(self):
        """Test that the state has the expected structure."""
        # Verify TravelState has required keys
        state_keys = TravelState.__annotations__.keys()
        
        assert "messages" in state_keys
        assert "destination" in state_keys
        assert "travel_dates" in state_keys
        assert "preferences" in state_keys


class TestTravelState:
    """Test suite for the travel state."""

    def test_state_initialization(self):
        """Test that state can be initialized with required fields."""
        state: TravelState = {
            "messages": [],
            "destination": None,
            "travel_dates": None,
            "preferences": None,
        }
        
        assert state["messages"] == []
        assert state["destination"] is None
