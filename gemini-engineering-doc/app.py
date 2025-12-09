import streamlit as st
import os
from dotenv import load_dotenv
from agents import create_pid_agent, setup_artifact_service
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="Gemini P&ID Multi-Agent", layout="wide")

# Title
st.title("Gemini P&ID Multi-Agent")

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

# --- Agent Profiles & Context ---
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

# --- Query Section ---
st.divider()

with st.form(key='question_form'):
    selected_question = st.selectbox("Choose a question:", questions)
    submit_button = st.form_submit_button(label='Ask a Question')

if submit_button:
    if not project_id or not location:
        st.error("Please provide a Project ID and Location.")
    else:
        # 1. Setup UI Layout: Log Expander on top, Final Response below
        thoughts_expander = st.expander("Agent Reasoning & Logs", expanded=True)
        
        st.subheader("Final Response")
        final_response_placeholder = st.empty() # Single placeholder for the final answer
        final_response_placeholder.info("Agents are working...")

        try:
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
                thoughts_expander.error("CRITICAL: Failed to load artifacts!")

            runner = Runner(
                agent=overseer_agent,
                app_name="agents",
                artifact_service=artifact_service,
                session_service=session_service
            )
            
            user_message_parts = [types.Part(text=selected_question)]
            user_content = types.Content(role='user', parts=user_message_parts)

            # --- Event Loop ---
            # We open the expander context to stream logs into it
            with thoughts_expander:
                st.caption("Stream initiated...")
                
                events = runner.run(
                    user_id="user1", 
                    session_id=session.id, 
                    new_message=user_content
                )
                
                for event in events:
                    if hasattr(event, 'content') and event.content and event.content.parts:
                        for part in event.content.parts:
                            
                            # -- CAPTURE THOUGHTS (Inside Expander) --
                            if hasattr(part, 'thought') and part.thought:
                                st.markdown(f"**🧠 {event.author} Thought:**")
                                st.info(part.text) 

                            # -- CAPTURE FUNCTION CALLS (Inside Expander) --
                            elif hasattr(part, 'function_call') and part.function_call:
                                st.markdown(f"**⚡ {event.author} Action:**")
                                st.code(f"Calling Tool: {part.function_call.name}\nArgs: {part.function_call.args}", language="json")

                            # -- CAPTURE FINAL TEXT (Outside Expander) --
                            elif hasattr(part, 'text') and part.text:
                                # We update the main placeholder outside this 'with' block
                                # But since Streamlit allows updating placeholders from anywhere, we call it here.
                                
                                # Optional: You can prepend the author name if you want to see who said it
                                final_response_placeholder.markdown(f"**{event.author}:**\n\n{part.text}")
                                
                                # Or just raw text as per your request:
                                # final_response_placeholder.markdown(part.text)

                    # -- CAPTURE SYSTEM ACTIONS (Inside Expander) --
                    if hasattr(event, 'actions') and event.actions:
                        if event.actions.transfer_to_agent:
                            st.write(f"🔄 **System:** Transferring execution to `{event.actions.transfer_to_agent}`")

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.exception(e)