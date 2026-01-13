import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from travel_assistant.backend.graph import graph

load_dotenv()

def test_full_graph():
    print("Initializing full graph test...")
    
    # simulate a user starting a conversation
    initial_input = {
        "messages": [
            HumanMessage(content="I want to plan a 3-day trip to Kyoto starting April 1st, 2025. I have a budget of $3000 and love history and food.")
        ]
    }
    
    print("\nInvoking graph with input:")
    print(f"User: {initial_input['messages'][1-1].content}")  # 1-1 just to be safe with indexing if logic changes, simplified here
    
    # Stream the graph to see updates
    # Using .invoke() for simple end-to-end
    try:
        final_state = graph.invoke(initial_input)
        
        print("\n--- Execution Complete ---")
        
        # Check extracted state
        print(f"\nExtracted Destination: {final_state.get('destination')}")
        print(f"Extracted Dates: {final_state.get('travel_dates')}")
        
        # Check Trip Plan presence
        trip_plan = final_state.get('trip_plan')
        if trip_plan:
            print(f"\nTrip Plan Generated for: {trip_plan.destination}")
        else:
            print("\nWARNING: No trip plan generated.")
            
        # Check Final Response
        messages = final_state.get('messages', [])
        if messages and len(messages) > 1: # expecting user msg + ai response
            last_msg = messages[-1]
            print(f"\nFinal AI Response:\n{last_msg.content}")
        else:
            print("\nWARNING: No final response found.")
            
    except Exception as e:
        print(f"\nERROR running graph: {e}")

if __name__ == "__main__":
    test_full_graph()
