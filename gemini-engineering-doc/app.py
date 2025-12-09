import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from agents import create_pid_agent,setup_artifact_service
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio
import json

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

st.header("P&ID Document Insights")
hcol1, hcol2, hcol3 = st.columns([1, 2, 1])
with hcol2: 
    st.image("assets/architecture.png", width='stretch')



col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Overseer")
    st.image("assets/overseer.png", width='stretch')

with col2:
    st.subheader("Analyst")
    st.image("assets/analyst.png", width='stretch')
    with st.expander("Context", expanded=False):
        try:
            with open("assets/pid_sample_1.pdf", "rb") as file:
                st.pdf(file.read(), height=400)
        except FileNotFoundError:
            st.error("Please ensure 'pid_sample_1.pdf' is in the app's asset directory.")

with col3:
    st.subheader("Instructor")
    st.image("assets/instructor.png", width='stretch')
    with st.expander("Context", expanded=False):
        try:
            with open("assets/learning_course.pdf", "rb") as file:
                st.pdf(file.read(), height=400)
        except FileNotFoundError:
            st.error("Please ensure 'learning_course.pdf' is in the app's asset directory.")      

questions = [
    "What does the P&ID document pid_sample_1.pdf depict?",
    "What are the key components when drafting a P&ID document?",
    "What are the key components of our pid_sample_1.pdf P&ID document?",
    "Who would need to sign off on a P&ID Document?"
]
with st.form(key='question_form'):
    # The user selects a question
    selected_question = st.selectbox("Choose a question:", questions)
    
    # The submit button
    submit_button = st.form_submit_button(label='Ask a Question')


if submit_button:
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
            
            session = asyncio.run(create_session_async())

            artifact_service = asyncio.run(setup_artifact_service(
                app_name="agents", 
                user_id="user1", 
                session_id=session.id
            ))
            if not artifact_service:
                print("CRITICAL: Failed to load artifacts!")

            runner = Runner(
                agent=overseer_agent,
                app_name="agents",
                artifact_service=artifact_service,
                session_service=session_service
            )
            
            # The initial prompt for the researcher agent
            user_message_parts = [types.Part(text=selected_question)]
            user_content = types.Content(
                role='user', 
                parts=user_message_parts
            )

            # Run the sequential pipeline and collect outputs
            overseer_output = ""
            instructor_output = ""
            analyst_output = ""

            with st.status("Running P&ID Agents...", expanded=True) as main_status:
                events = runner.run(
                    user_id="user1", 
                    session_id=session.id, 
                    new_message=user_content
                )
                for event in events:
                    st.write(event)
                    # Track which agent is currently active
                    if event.author == "overseer_agent":
                        if event.is_final_response() and event.content:
                            overseer_output = event.content.parts[0].text
                    elif event.author == "analyst_agent":
                        if event.is_final_response() and event.content:
                            analyst_output = event.content.parts[0].text
                    elif event.author == "instructor_agent":
                        if event.is_final_response() and event.content:
                            instructor_output = event.content.parts[0].text
                
                main_status.update(label="Answer Complete", state="complete")
        
            # Display results in columns
            rcol1, rcol2, rcol3 = st.columns(3)
            with col1:
               
                # Overseer Results
                st.write("**Overseer Output:**")
                if overseer_output:
                    try:
                        # Try to parse as JSON if it looks like JSON
                        if overseer_output.strip().startswith('{'):
                            overseer_json = json.loads(overseer_output)
                            st.json(overseer_json)
                        else:
                            st.write(overseer_output)
                    except:
                        st.write(overseer_output)
                else:
                    st.info("Overseer currently overseeing :) ...")
            
            with col2:
                # Analyst Results
                with st.expander("Response", expanded=True):
                    st.write("**Analyst Output:**")
                    if analyst_output:
                        try:
                            # Try to parse as JSON if it looks like JSON
                            if analyst_output.strip().startswith('{'):
                                analyst_json = json.loads(analyst_output)
                                st.json(analyst_json)
                            else:
                                st.write(analyst_output)
                        except:
                            st.write(analyst_output)
                    else:
                        st.info("Currently Analyzing ...")
            with col3:
                # Instructor Results
                with st.expander("Response", expanded=True):
                    st.write("**Instructor Output:**")
                    if instructor_output:
                        try:
                            # Try to parse as JSON if it looks like JSON
                            if instructor_output.strip().startswith('{'):
                                instructor_json = json.loads(instructor_output)
                                st.json(instructor_json)
                            else:
                                st.write(instructor_output)
                        except:
                            st.write(instructor_output)
                    else:
                        st.info("Currently Instructing :) ...")

            for event in events:
                st.write(event)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.exception(e)