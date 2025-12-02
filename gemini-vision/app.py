import streamlit as st
import os
import json
from dotenv import load_dotenv
from agents import run_scout_agent, get_infrastructure_monitoring_pipeline
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="SkyGuard ROW Monitor", layout="wide")

# Title
st.title("SkyGuard ROW Monitor")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    st.write(f"**Project ID:** {os.environ.get('GOOGLE_CLOUD_PROJECT')}")
    st.write(f"**Location:** {os.environ.get('GOOGLE_CLOUD_LOCATION')}")
    
    st.header("Scenario Selector")
    scenario = st.radio("Choose a Scenario:", ["Clear", "Farm", "Excavator"])
    
    st.header("Custom Upload")
    uploaded_file = st.file_uploader("Upload an aerial image", type=["png", "jpg", "jpeg"])

# Main Layout
col1, col2, col3 = st.columns(3)

# Helper to load assets
def load_asset(name):
    base_path = f"assets/{name.lower()}"
    if os.path.exists(f"{base_path}.png"):
        return f"{base_path}.png"
    elif os.path.exists(f"{base_path}.jpg"):
        return f"{base_path}.jpg"
    elif os.path.exists(f"{base_path}.jpeg"):
        return f"{base_path}.jpeg"
    return None

# Determine Image Source
image_path = None
temp_image_path = None

if uploaded_file:
    # Save uploaded file to temp path for reading
    temp_image_path = f"temp_{uploaded_file.name}"
    with open(temp_image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    image_path = temp_image_path
    st.toast("Using uploaded image")
else:
    image_path = load_asset(scenario)

# Column 1: The View
with col1:
    st.header("The View")
    if image_path and os.path.exists(image_path):
        st.image(image_path, caption="Aerial Feed", width="stretch")
    else:
        st.warning(f"Image not found: {image_path}")
        st.info("Please ensure assets/clear.png, assets/farm.png, and assets/excavator.png exist.")

# Execution Button
if st.button("Analyze Sector"):
    if not image_path or not os.path.exists(image_path):
        st.error("Please select or upload a valid image.")
    else:
        try:
            import asyncio
            
            # Create the sequential agent pipeline
            pipeline = get_infrastructure_monitoring_pipeline()
            
            # Set up ADK session and runner using async
            session_service = InMemorySessionService()
            
            # Use asyncio to create session properly
            async def create_session_async():
                return await session_service.create_session(
                    app_name="infrastructure_monitoring_pipeline", 
                    user_id="user1"
                )
            
            session = asyncio.run(create_session_async())
            
            runner = Runner(
                agent=pipeline, 
                app_name="infrastructure_monitoring_pipeline", 
                session_service=session_service
            )
            
            # Create user message with the image path
            user_content = types.Content(
                role='user', 
                parts=[types.Part(text=f"Please analyze this aerial image: {image_path}")]
            )
            
            # Run the sequential pipeline and collect outputs
            scout_output = ""
            risk_assessment_text = ""
            final_alert_text = ""
            
            with st.status("Running Infrastructure Monitoring Pipeline...", expanded=True) as main_status:
                events = runner.run(
                    user_id="user1", 
                    session_id=session.id, 
                    new_message=user_content
                )
                
                for event in events:
                    # Track which agent is currently active
                    if event.author == "scout_agent":
                        if event.is_final_response() and event.content:
                            scout_output = event.content.parts[0].text
                    elif event.author == "risk_agent":
                        if event.is_final_response() and event.content:
                            risk_assessment_text = event.content.parts[0].text
                    elif event.author == "dispatcher_agent":
                        if event.is_final_response() and event.content:
                            final_alert_text = event.content.parts[0].text
                
                main_status.update(label="Pipeline Complete", state="complete")
            
            # Display results in columns
            with col2:
                st.header("The Brain")
                
                # Scout Results
                with st.expander("Scout Analysis", expanded=True):
                    st.write("**Scout Output:**")
                    if scout_output:
                        try:
                            # Try to parse as JSON if it looks like JSON
                            if scout_output.strip().startswith('{'):
                                scout_json = json.loads(scout_output)
                                st.json(scout_json)
                            else:
                                st.write(scout_output)
                        except:
                            st.write(scout_output)
                    else:
                        st.info("Scout analysis in progress...")
                
                # Risk Assessment Results
                with st.expander("Risk Assessment", expanded=True):
                    st.write("**Risk Officer Output:**")
                    if risk_assessment_text:
                        st.write(risk_assessment_text)
                    else:
                        st.info("Risk assessment in progress...")
            
            with col3:
                st.header("The Action")
                with st.expander("Dispatcher Alert", expanded=True):
                    if final_alert_text:
                        # Determine style based on content (simple heuristic)
                        if "STOP WORK" in final_alert_text.upper() or "HIGH" in final_alert_text.upper():
                            st.error(final_alert_text)
                        else:
                            st.success(final_alert_text)
                    else:
                        st.info("Generating alert...")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.exception(e)

# Cleanup temp file
if temp_image_path and os.path.exists(temp_image_path):
    os.remove(temp_image_path)
