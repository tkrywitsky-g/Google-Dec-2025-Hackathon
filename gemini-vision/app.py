import streamlit as st
import os
import json
from dotenv import load_dotenv
from agents import run_scout_agent, get_risk_agent, get_dispatcher_agent
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
    api_key = st.text_input("Google API Key", type="password", value=os.getenv("GOOGLE_API_KEY", ""))
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    
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
        st.image(image_path, caption="Aerial Feed", use_container_width=True)
    else:
        st.warning(f"Image not found: {image_path}")
        st.info("Please ensure assets/clear.png, assets/farm.png, and assets/excavator.png exist.")

# Execution Button
if st.button("Analyze Sector"):
    if not api_key and not os.getenv("GOOGLE_API_KEY"):
        st.error("Please provide a Google API Key.")
    elif not image_path or not os.path.exists(image_path):
        st.error("Please select or upload a valid image.")
    else:
        try:
            # Step 1: Scout
            with col2:
                st.header("The Brain")
                
                with st.status("Scout Agent Analyzing...", expanded=True) as status:
                    scout_output = run_scout_agent(image_path)
                    st.write("**Scout Output:**")
                    try:
                        scout_json = json.loads(scout_output)
                        st.json(scout_json)
                    except:
                        st.write(scout_output)
                    status.update(label="Scout Agent Complete", state="complete")
                
                # Step 2: Risk Officer
                with st.status("Risk Officer Assessing...", expanded=True) as status:
                    risk_agent = get_risk_agent()
                    
                    # Set up ADK session and runner
                    session_service = InMemorySessionService()
                    session = session_service.create_session(
                        app_name="skyguard", 
                        user_id="user1", 
                        session_id="risk_session"
                    )
                    runner = Runner(
                        agent=risk_agent, 
                        app_name="skyguard", 
                        session_service=session_service
                    )
                    
                    # Create user message
                    user_content = types.Content(
                        role='user', 
                        parts=[types.Part(text=f"Here is the scout report: {scout_output}")]
                    )
                    
                    # Run agent and extract response
                    risk_assessment_text = ""
                    events = runner.run(
                        user_id="user1", 
                        session_id="risk_session", 
                        new_message=user_content
                    )
                    
                    for event in events:
                        if event.is_final_response() and event.content:
                            risk_assessment_text = event.content.parts[0].text
                    
                    st.write("**Risk Assessment:**")
                    st.write(risk_assessment_text)
                    status.update(label="Risk Officer Complete", state="complete")

            # Step 3: Dispatcher
            with col3:
                st.header("The Action")
                with st.status("Dispatcher Generating Alert...", expanded=True) as status:
                    dispatcher_agent = get_dispatcher_agent()
                    
                    # Set up ADK session and runner
                    session_service_dispatcher = InMemorySessionService()
                    session_dispatcher = session_service_dispatcher.create_session(
                        app_name="skyguard", 
                        user_id="user1", 
                        session_id="dispatcher_session"
                    )
                    runner_dispatcher = Runner(
                        agent=dispatcher_agent, 
                        app_name="skyguard", 
                        session_service=session_service_dispatcher
                    )
                    
                    # Create user message
                    user_content_dispatcher = types.Content(
                        role='user', 
                        parts=[types.Part(text=f"Here is the risk assessment: {risk_assessment_text}")]
                    )
                    
                    # Run agent and extract response
                    final_alert_text = ""
                    events_dispatcher = runner_dispatcher.run(
                        user_id="user1", 
                        session_id="dispatcher_session", 
                        new_message=user_content_dispatcher
                    )
                    
                    for event in events_dispatcher:
                        if event.is_final_response() and event.content:
                            final_alert_text = event.content.parts[0].text
                    
                    # Determine style based on content (simple heuristic)
                    if "STOP WORK" in final_alert_text.upper() or "HIGH" in final_alert_text.upper():
                        st.error(final_alert_text)
                    else:
                        st.success(final_alert_text)
                    
                    status.update(label="Dispatcher Complete", state="complete")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.exception(e)

# Cleanup temp file
if temp_image_path and os.path.exists(temp_image_path):
    os.remove(temp_image_path)
