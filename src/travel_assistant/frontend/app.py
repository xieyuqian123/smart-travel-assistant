import streamlit as st
import os
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
        
        # 2. Map Data Preparation
        all_nodes = []
        path_data = []
        
        for day in plan.itinerary:
            day_path = []
            for node in day.nodes:
                if node.coordinates:
                    # Add to scatterplot data
                    all_nodes.append({
                        "name": node.name,
                        "type": node.type,
                        "coordinates": [node.coordinates.lng, node.coordinates.lat], # PyDeck uses [lng, lat]
                        "day": day.day,
                        "description": node.description
                    })
                    # Add to path data
                    day_path.append([node.coordinates.lng, node.coordinates.lat])
            
            if len(day_path) > 1:
                path_data.append({
                    "path": day_path,
                    "day": day.day,
                    "color": [255, 75, 75] # Red color
                })

        # 3. Render Map
        if all_nodes:
            # Calculate initial view state
            if all_nodes:
                initial_lat = all_nodes[0]["coordinates"][1]
                initial_lng = all_nodes[0]["coordinates"][0]
            else:
                initial_lat = 0
                initial_lng = 0
                
            view_state = pdk.ViewState(
                latitude=initial_lat,
                longitude=initial_lng,
                zoom=11,
                pitch=45,
            )
            
            # Layers
            scatter_layer = pdk.Layer(
                "ScatterplotLayer",
                data=all_nodes,
                get_position="coordinates",
                get_color=[255, 75, 75, 200],
                get_radius=200,
                pickable=True,
                auto_highlight=True,
            )
            
            path_layer = pdk.Layer(
                "PathLayer",
                data=path_data,
                get_path="path",
                get_color="color",
                width_scale=20,
                width_min_pixels=2,
                pickable=True,
            )
            
            text_layer = pdk.Layer(
                "TextLayer",
                data=all_nodes,
                get_position="coordinates",
                get_text="name",
                get_color=[0, 0, 0, 200],
                get_size=15,
                get_angle=0,
                get_text_anchor="middle",
                get_alignment_baseline="center",
                pixel_offset=[0, -20] # Offset text above point
            )

            r = pdk.Deck(
                layers=[path_layer, scatter_layer, text_layer],
                initial_view_state=view_state,
                tooltip={"text": "{name}\nType: {type}\nDay: {day}"},
                map_style="mapbox://styles/mapbox/light-v9"
            )
            
            st.pydeck_chart(r)
        else:
            st.info("No location data available for map visualization.")

        st.divider()

        # 4. Itinerary Cards
        st.subheader("Daily Itinerary")
        
        for day in plan.itinerary:
            st.markdown(f"### Day {day.day}: {day.summary}")
            
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
                    <div style="margin-top: 10px;">{node.description}</div>
                </div>
                """, unsafe_allow_html=True)

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
                # We pass the full history of messages
                # Note: In a real production app, you might want to manage state more carefully
                # to avoid context window limits.
                import asyncio
                response = asyncio.run(graph.ainvoke({"messages": st.session_state.messages}))
                
                # Get the returned messages
                final_messages = response["messages"]
                
                # Find new messages by comparing length
                # This assumes LangGraph appends messages to the input list
                # However, since we passed st.session_state.messages (which we just appended to),
                # the result should contain those plus new ones.
                
                new_msg_count = len(final_messages) - len(st.session_state.messages)
                
                if new_msg_count > 0:
                    new_messages = final_messages[-new_msg_count:]
                    for msg in new_messages:
                        if isinstance(msg, AIMessage):
                            st.markdown(msg.content)
                            st.session_state.messages.append(msg)
                
                # Update trip plan if available
                # The graph returns the state, so we check if 'trip_plan' is in it
                if response.get("trip_plan"):
                    # Only update if it's different or new
                    if st.session_state.trip_plan != response["trip_plan"]:
                        st.session_state.trip_plan = response["trip_plan"]
                        st.rerun() # Rerun to update sidebar
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
                import traceback
                st.error(traceback.format_exc())
