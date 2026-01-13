import streamlit as st
import os
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

# Sidebar for displaying trip details if available
with st.sidebar:
    st.header("Trip Details")
    if st.session_state.trip_plan:
        plan = st.session_state.trip_plan
        st.subheader(f"Trip to {plan.destination}")
        st.write(f"**Budget:** {plan.budget}")
        if plan.interests:
            st.write(f"**Interests:** {', '.join(plan.interests)}")
        
        st.divider()
        st.subheader("Itinerary")
        for day in plan.itinerary:
            with st.expander(f"Day {day.day}: {day.summary}"):
                for node in day.nodes:
                    st.write(f"**{node.name}** ({node.type})")
                    st.write(node.description)
                    if node.cost:
                        st.write(f"*Cost: {node.cost}*")
                    if node.coordinates:
                        st.map([{"lat": node.coordinates.lat, "lon": node.coordinates.lng}])
    else:
        st.info("Plan your trip to see details here!")

# Chat interface
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# User input
if prompt := st.chat_input("Where do you want to go?"):
    # Add user message to state
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Invoke the graph
                # We pass the full history of messages
                # Note: In a real production app, you might want to manage state more carefully
                # to avoid context window limits.
                response = graph.invoke({"messages": st.session_state.messages})
                
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
