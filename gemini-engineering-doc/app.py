import streamlit as st
import os
import json
from dotenv import load_dotenv
from agents import get_pandid_agent,setup_artifact_service
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="Flow Diagram Q&A", layout="wide")

# Title
st.title("P&ID Agent Demo")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    st.write(f"**Project ID:** {os.environ.get('GOOGLE_CLOUD_PROJECT')}")
    st.write(f"**Location:** {os.environ.get('GOOGLE_CLOUD_LOCATION')}")

    selected_model = st.selectbox(
        "Select Gemini Model:",
        ["gemini-3-pro-preview"]
    )

    user_question = st.text_input("Ask a question about the flow diagrams:")

# Main Layout
col1, col2, col3 = st.columns(3)

# Execution Button
if st.button("Ask Question"):
    if not user_question:
        st.error("Please enter a question.")
    else:
        try:
            import asyncio

            # Create the sequential agent pipeline
            pipeline = get_pandid_agent()

            # Set up ADK session and runner using async
            session_service = InMemorySessionService()

            async def create_session_async():
                return await session_service.create_session(
                    app_name="flow_diagram_pipeline",
                    user_id="user1",
                    # Pass user_question to the session
                    session_kwargs={"user_question": user_question}
                )
            
            artifact_service = asyncio.run(setup_artifact_service())
            if not artifact_service:
                print("CRITICAL: Failed to load artifacts!")


            session = asyncio.run(create_session_async())

            runner = Runner(
                agent=pipeline,
                app_name="flow_diagram_pipeline",
                artifact_service=artifact_service,
                session_service=session_service
            )

            # Create user message
            user_content = types.Content(
                role='user',
                parts=[types.Part(text=user_question)]
            )

            # Run the sequential pipeline and collect outputs
            reviewer_answer = ""
            refined_answer = ""
            public_info = ""

            with st.status("Running Flow Diagram Q&A Pipeline...", expanded=True) as main_status:
                events = runner.run(
                    user_id="user1",
                    session_id=session.id,
                    new_message=user_content
                )

                for event in events:
                    if event.author == "diagram_reviewer_agent":
                        if event.is_final_response() and event.content:
                            reviewer_answer = event.content.parts[0].text
                    elif event.author == "critique_agent":
                        if event.is_final_response() and event.content:
                            refined_answer = event.content.parts[0].text
                    elif event.author == "public_retrieval_agent":
                        if event.is_final_response() and event.content:
                            public_info = event.content.parts[0].text

                main_status.update(label="Pipeline Complete", state="complete")

            # Display results in columns
            with col1:
                st.header("Initial Answer")
                with st.expander("Diagram Reviewer Output", expanded=True):
                    if reviewer_answer:
                        st.write(reviewer_answer)
                    else:
                        st.info("Review in progress...")

            with col2:
                st.header("Refined Answer")
                with st.expander("Critique Output", expanded=True):
                    if refined_answer:
                        st.write(refined_answer)
                    else:
                        st.info("Critique in progress...")

            with col3:
                st.header("Public Information")
                with st.expander("Public Retrieval Output", expanded=True):
                    if public_info:
                        st.write(public_info)
                    else:
                        st.info("Public retrieval in progress...")

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.exception(e)