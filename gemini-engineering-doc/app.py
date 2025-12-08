import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from agents import create_pid_agent,setup_artifact_service
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="Gemini P&ID Orchestrator", layout="wide")

# Title
st.title("Gemini P&ID Orchestrator Agent")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    project_id = st.text_input("Project ID", value=os.getenv("GOOGLE_CLOUD_PROJECT", ""), disabled=True)
    location = st.text_input("Location", value=os.getenv("GOOGLE_CLOUD_LOCATION", ""), disabled=True)

    if project_id:
        os.environ["PROJECT_ID"] = project_id
    if location:
        os.environ["LOCATION"] = location

st.header("Root Cause Analysis Scenario")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("P&ID Document Q&A")
    with st.expander("Context", expanded=False):
        try:
            with open("assets/pid_sample_1.pdf", "rb") as file:
                st.pdf(file.read(), height=400)
        except FileNotFoundError:
            st.error("Please ensure 'pid_sample_1.pdf' is in the app's asset directory.")

with col2:
    st.subheader("P&ID Instructor")
    with st.expander("Context", expanded=False):
        try:
            with open("assets/learning_course.pdf", "rb") as file:
                st.pdf(file.read(), height=400)
        except FileNotFoundError:
            st.error("Please ensure 'learning_course.pdf' is in the app's asset directory.")

with col3:
    st.subheader("P&ID Drawer (Experimental)")
    with st.expander("Context", expanded=False):
        try:
            with open("assets/reference_guide.pdf", "rb") as file:
                st.pdf(file.read(), height=400)
        except FileNotFoundError:
            st.error("Please ensure 'reference_guide.pdf' is in the app's asset directory.")      
        

if st.button("Ask Question"):
    if not project_id or not location:
        st.error("Please provide a Project ID and Location.")
    else:
        try:
            import asyncio

            # Create the RCA pipeline
            overseer_agent = create_pid_agent(project_id=project_id, location=location)
            
            # Set up ADK session and runner
            session_service = InMemorySessionService()
            
            async def create_session_async():
                return await session_service.create_session(
                    app_name="agents", 
                    user_id="user1"
                )
            
            # artifact_service = asyncio.run(setup_artifact_service())
            # if not artifact_service:
            #     print("CRITICAL: Failed to load artifacts!")

            session = asyncio.run(create_session_async())

            runner = Runner(
                agent=overseer_agent,
                app_name="agents",
                # artifact_service=artifact_service,
                session_service=session_service
            )
            
            # The initial prompt for the researcher agent
            user_content = types.Content(
                role='user', 
                parts=[types.Part(text="Describe what the P&ID document sample1.pdf is about.")]
            )

            events = runner.run(
                user_id="user1", 
                session_id=session.id, 
                new_message=user_content
            )

            # # Run the sequential pipeline and collect outputs
            # analyst_output = ""
            # instructor_text = ""
            # drafter_alert_text = ""

            for event in events:
                st.write(event)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.exception(e)