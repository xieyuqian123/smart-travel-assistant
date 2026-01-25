import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()
import pydeck as pdk
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from travel_assistant.backend.graph import graph
from travel_assistant.backend.schemas import TripSchema

st.set_page_config(page_title="Smart Travel Assistant", layout="wide")

st.title("✈️ Smart Travel Assistant")
st.markdown("Describe your dream trip, and I'll plan it for you!")

# Check for API Key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    with st.sidebar:
        st.warning("⚠️ OpenAI API Key not found in environment variables.")
        api_key_input = st.text_input("Enter OpenAI API Key", type="password")
        if api_key_input:
            os.environ["OPENAI_API_KEY"] = api_key_input
            st.success("API Key set for this session!")
            st.rerun()
        else:
            st.stop()

# Initialize session state
import uuid
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "trip_plan" not in st.session_state:
    st.session_state.trip_plan = None

# Tabs for Chat and Itinerary
tab1, tab2 = st.tabs(["💬 Chat", "🗺️ Itinerary & Map"])

with tab1:
    # Chat interface
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(msg.content)

with tab2:
    if st.session_state.trip_plan:
        plan = st.session_state.trip_plan
        st.subheader(f"Trip to {plan.destination}")
        st.markdown(f"**Budget:** {plan.budget} | **Travelers:** {plan.travelers}")
        
        # --- MAP & CARDS UI ---
        
        # 1. Custom CSS
        st.markdown("""
        <style>
        .itinerary-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box_shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 5px solid #FF4B4B;
        }
        .itinerary-time {
            font-weight: bold;
            color: #FF4B4B;
        }
        .itinerary-title {
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .itinerary-type {
            font-size: 0.8em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .itinerary-cost {
            float: right;
            font-weight: bold;
            color: #28a745;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 2. Daily Itinerary & Map Loop
        amap_api_key = os.getenv("AMAP_MAPS_JS_API_KEY") or os.getenv("AMAP_MAPS_API_KEY")
        security_code = os.getenv("AMAP_SECURITY_CODE", "")
        
        if not amap_api_key:
            st.error("AMAP API Key not found. Maps cannot be rendered.")
        
        from travel_assistant.frontend.amap_component import render_amap_html
        import streamlit.components.v1 as components

        for day in plan.itinerary:
            st.markdown(f"### Day {day.day}: {day.summary}")
            
            col_map, col_cards = st.columns([1.2, 1]) # Map gets slightly more width
            
            with col_map:
                # Prepare data for this day
                day_markers = []
                day_path = []
                
                for node in day.nodes:
                    if node.coordinates:
                        # Amap expects [lng, lat]
                        pos = [node.coordinates.lng, node.coordinates.lat]
                        day_markers.append({
                            "position": pos,
                            "title": node.name,
                            "content": f"{node.type}: {node.name}"
                        })
                        day_path.append(pos)
                
                if day_markers and amap_api_key:
                    day_html = render_amap_html(
                        api_key=amap_api_key,
                        markers=day_markers,
                        path_coordinates=day_path,
                        height=400, # Per-day map height
                        security_code=security_code
                    )
                    components.html(day_html, height=400)
                elif not day_markers:
                    st.info("No location data for this day.")
                else:
                     st.warning("Map unavailable")

            with col_cards:
                 for node in day.nodes:
                    cost_html = f'<span class="itinerary-cost">{node.cost}</span>' if node.cost else ""
                    start_time = node.start_time if node.start_time else ""
                    end_time = f"- {node.end_time}" if node.end_time else ""
                    time_str = f"{start_time} {end_time}"
                    
                    st.markdown(f"""
                    <div class="itinerary-card">
                        {cost_html}
                        <div class="itinerary-type">{node.type or 'Activity'}</div>
                        <div class="itinerary-title">{node.name}</div>
                        <div class="itinerary-time">{time_str}</div>
                        <div style="margin-top: 10px; font-size: 0.9em;">{node.description}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.divider()

# User input
if prompt := st.chat_input("Where do you want to go?"):
    # Add user message to state
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Invoke the graph using asyncio for async node support
                import asyncio
                from travel_assistant.backend.memory.checkpointer import get_async_checkpointer
                from travel_assistant.backend.graph import builder
                
                async def run_chat():
                    async with get_async_checkpointer() as checkpointer:
                         # Compile graph with checkpointer at runtime
                         graph_run = builder.compile(checkpointer=checkpointer)
                         
                         # Use persistent config
                         config = {"configurable": {"thread_id": st.session_state.thread_id}}
                         
                         # Only pass the NEW message, let checkpointer handle history
                         inputs = {"messages": [HumanMessage(content=prompt)]}
                         
                         return await graph_run.ainvoke(inputs, config=config)

                response = asyncio.run(run_chat())
                
                # Get the returned messages
                final_messages = response["messages"]
                
                if final_messages:
                    last_msg = final_messages[-1]
                    if isinstance(last_msg, AIMessage):
                        st.session_state.messages.append(last_msg)
                        st.markdown(last_msg.content)
                
                # Update Trip Plan
                if response.get("trip_plan"):
                    st.session_state.trip_plan = response["trip_plan"]
                    st.rerun()
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
                import traceback
                st.error(traceback.format_exc())
