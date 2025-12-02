import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from agents.agent import create_rca_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="Gemini RCA Agent", layout="wide")

# Title
st.title("Gemini Advanced Root Cause Analysis Agent")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    project_id = st.text_input("Project ID", value=os.getenv("GOOGLE_CLOUD_PROJECT", ""), disabled=True)
    location = st.text_input("Location", value=os.getenv("GOOGLE_CLOUD_LOCATION", ""), disabled=True)
    model_name = st.selectbox("Model", ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-2.5-pro"])

    if project_id:
        os.environ["PROJECT_ID"] = project_id
    if location:
        os.environ["LOCATION"] = location

st.header("Root Cause Analysis Scenario")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Data Sources")
    with st.expander("ServiceNow Incidents", expanded=False):
        try:
            servicenow_df = pd.read_csv("data/servicenow_incidents.csv")
            st.dataframe(servicenow_df)
        except FileNotFoundError:
            st.error("data/servicenow_incidents.csv not found.")

    with st.expander("Versa SD-WAN Logs", expanded=False):
        try:
            versa_df = pd.read_csv("data/versa_sdwan_logs.csv")
            st.dataframe(versa_df)
        except FileNotFoundError:
            st.error("data/versa_sdwan_logs.csv not found.")

    with st.expander("Weather API", expanded=False):
        try:
            weather_df = pd.read_csv("data/weather.csv")
            st.dataframe(weather_df)
        except FileNotFoundError:
            st.error("data/weather.csv not found.")

if st.button("Run Root Cause Analysis"):
    if not project_id or not location:
        st.error("Please provide a Project ID and Location.")
    else:
        try:
            import asyncio

            # Create the RCA pipeline
            pipeline = create_rca_agent(project_id, location, model_name)
            
            # Set up ADK session and runner
            session_service = InMemorySessionService()
            
            async def create_session_async():
                return await session_service.create_session(
                    app_name="rca_agent", 
                    user_id="user1"
                )
            
            session = asyncio.run(create_session_async())
            
            runner = Runner(
                agent=pipeline, 
                app_name="rca_agent", 
                session_service=session_service
            )
            
            # The initial prompt for the researcher agent
            user_content = types.Content(
                role='user', 
                parts=[types.Part(text="Analyze the logs from ['data/servicenow_incidents.csv', 'data/versa_sdwan_logs.csv']")]
            )
            
            researcher_output = ""
            hypothesis_output = ""
            dispatcher_output = ""
            
            with st.status("Running Root Cause Analysis Pipeline...", expanded=True) as main_status:
                events = runner.run(
                    user_id="user1", 
                    session_id=session.id, 
                    new_message=user_content
                )
                
                for event in events:
                    if event.author == "NetworkLogResearcher":
                        if event.is_final_response() and event.content:
                            researcher_output = event.content.parts[0].text
                    elif event.author == "NetworkAnalyst":
                        if event.is_final_response() and event.content:
                            hypothesis_output = event.content.parts[0].text
                    elif event.author == "DispatchCoordinator":
                        if event.is_final_response() and event.content:
                            dispatcher_output = event.content.parts[0].text
                
                main_status.update(label="Pipeline Complete", state="complete")

            with col2:
                st.subheader("Agent Analysis")
                with st.expander("Researcher's Findings", expanded=True):
                    st.write(researcher_output)
                
                with st.expander("Hypothesis", expanded=True):
                    st.write(hypothesis_output)
                
                st.subheader("Final Recommendation")
                st.success(dispatcher_output)

                st.write("Would you like to submit this recommendation?")
                if st.button("Submit Recommendation"):
                    st.write("Submitted")

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.exception(e)