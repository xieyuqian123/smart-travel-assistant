
import streamlit as st
import os
import streamlit.components.v1 as components
from travel_assistant.frontend.amap_component import render_amap_html

st.set_page_config(page_title="Amap Debugger")

st.title("🗺️ Amap Integration Debugger")

st.info("This tool verifies if your API Key and Security Code are correctly loaded.")

# 1. Check Variables
js_api_key = os.getenv("AMAP_MAPS_JS_API_KEY", "")
server_api_key = os.getenv("AMAP_MAPS_API_KEY", "")
security_code = os.getenv("AMAP_SECURITY_CODE", "")

st.subheader("Environment Variables Status")
col1, col2, col3 = st.columns(3)

with col1:
    if js_api_key:
        st.success(f"✅ JS API Key Found\n`{js_api_key[:6]}...`")
    else:
        st.error("❌ JS API Key Missing\n(AMAP_MAPS_JS_API_KEY)")

with col2:
    if security_code:
        st.success(f"✅ Security Code Found\n`{security_code[:3]}...`")
    else:
        st.error("❌ Security Code Missing\n(AMAP_SECURITY_CODE)")
        
with col3:
    if server_api_key:
        st.markdown(f"**Server Key:** `{server_api_key[:6]}...`")

# 2. Render Map
st.subheader("Map Test")

active_key = js_api_key or server_api_key

if active_key:
    if not security_code:
        st.warning("⚠️ **Security Code is missing.** Map will likely be white or fail to load.")
    
    # Mock Data
    markers = [{"position": [116.397428, 39.90923], "title": "Tian'anmen", "content": "Center of Beijing"}]
    path = [[116.397428, 39.90923], [116.407428, 39.90923]]
    
    html = render_amap_html(
        api_key=active_key, 
        markers=markers, 
        path_coordinates=path,
        height=400,
        security_code=security_code
    )
    
    components.html(html, height=400)
    
else:
    st.error("Cannot render map: No API Key available.")

st.markdown("---")
st.markdown("If the map above is blank, please check your `.env` file and Ensure `AMAP_SECURITY_CODE` is set.")
