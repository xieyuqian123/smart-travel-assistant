import asyncio
import os
import uuid
from langchain_core.messages import HumanMessage
from travel_assistant.backend.graph import builder
from travel_assistant.backend.memory.checkpointer import get_async_checkpointer

async def test_memory_flow():
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"Starting test with Thread ID: {thread_id}")
    
    # We must use the context manager
    async with get_async_checkpointer() as checkpointer:
        graph = builder.compile(checkpointer=checkpointer)
        
        # 1. First Turn: Create Plan
        print("\n--- Turn 1: Create Plan ---")
        msg1 = HumanMessage(content="Plan a 3-day trip to Tokyo with a budget of 1000 USD.")
        inputs1 = {"messages": [msg1]}
        
        response1 = await graph.ainvoke(inputs1, config=config)
        
        plan1 = response1.get("trip_plan")
        if plan1:
            print(f"Plan Created. Destination: {plan1.destination}, Budget: {plan1.budget}")
            print(f"Itinerary Length: {len(plan1.itinerary)} days")
        else:
            print("ERROR: No plan created.")
            return

        # 2. Second Turn: Modification
        print("\n--- Turn 2: Modify Plan (Memory Check) ---")
        msg2 = HumanMessage(content="Actually, I want to visit Kyoto instead.")
        inputs2 = {"messages": [msg2]}
        
        response2 = await graph.ainvoke(inputs2, config=config)
        
        plan2 = response2.get("trip_plan")
        if plan2:
            print(f"Plan Updated. Destination: {plan2.destination}")
            if "Kyoto" in plan2.destination:
                print("SUCCESS: Destination updated to Kyoto based on context.")
            else:
                print(f"FAILURE: Destination is {plan2.destination}, expected Kyoto.")
        else:
            print("ERROR: No updated plan returned.")

        # 3. Third Turn: Modification (Detail)
        print("\n--- Turn 3: Modify Detail ---")
        msg3 = HumanMessage(content="Add a visit to Kinkaku-ji temple on Day 1.")
        inputs3 = {"messages": [msg3]}
        
        response3 = await graph.ainvoke(inputs3, config=config)
        plan3 = response3.get("trip_plan")
        
        if plan3:
            day1 = plan3.itinerary[0]
            found = any("Kinkaku-ji" in node.name for node in day1.nodes)
            if found:
                 print("SUCCESS: Kinkaku-ji added to Day 1.")
            else:
                 print("FAILURE: Kinkaku-ji not found in Day 1 nodes.")

if __name__ == "__main__":
    asyncio.run(test_memory_flow())
