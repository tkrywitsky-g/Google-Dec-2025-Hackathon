from google.adk.agents import Agent
from google.genai import types
from google.adk.planners import BuiltInPlanner
from google.adk.artifacts import InMemoryArtifactService
from pathlib import Path
import vertexai
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional

from google.adk import Agent

ASSETS_DIR = Path("./assets")

async def inject_pid_context(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    print("⚡ [Callback] Injecting P&ID into context...")
    
    # 1. Load the file (Pass-by-Value, but it's okay because it's User Role)
    # Note: In a real app, you might check context.state to see if it's already loaded
    filename = "pid_sample_1.pdf"
    try:
        # Load the latest version
        report_artifact = await callback_context.load_artifact(filename=filename)

        if report_artifact and report_artifact.inline_data:
            print(f"Successfully loaded latest Python artifact '{filename}'.")
            print(f"MIME Type: {report_artifact.inline_data.mime_type}")
            pdf_bytes = report_artifact.inline_data.data
            print(f"Report size: {len(pdf_bytes)} bytes.")
        else:
            print(f"Python artifact '{filename}' not found.")

    except ValueError as e:
        print(f"Error loading Python artifact: {e}. Is ArtifactService configured?")
    except Exception as e:
        # Handle potential storage errors
        print(f"An unexpected error occurred during Python artifact load: {e}")

def create_analyst_agent(model):

    return Agent(
        name="analyst_agent",
        model=model,
        before_model_callback=inject_pid_context,        
        instruction="""
        You are a Senior Process Engineer acting as a P&ID Analyst.
        
        **Context:** A P&ID diagram (PDF) has been attached to the user's message in your context. 
        You have immediate visual access to this document.
        
        **Your Goal:** Answer technical questions based *strictly* on the visual information in that attached diagram.
        
        **Analysis Guidelines:**
        - **Visual Tracing:** Trace process lines carefully from source to destination to confirm flow direction.
        - **Tag Identification:** Identify components explicitly by their tag numbers (e.g., V-101, P-20A) whenever possible.
        - **Ambiguity:** If a symbol is distinct but you cannot read the tag (e.g., due to resolution), describe the component's visual appearance and location (e.g., "The pump in the bottom left") rather than guessing.
        - **Standards:** Do not rely on general industry standards if they conflict with what is drawn; the specific diagram takes precedence.
        
        **Output Format:**
        - **Strictly use Markdown** for all responses.
        - Use **Bold** for specific tag numbers (e.g., **V-101**) and component names.
        - Use `Headed Sections` (###) to separate different parts of your analysis.
        - Use bullet points for lists of components or process steps.
        """,
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=16000,
            )
        )
    )

async def inject_instructor_context(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    print("⚡ [Callback] Injecting Learnign Course into context...")
    
    # 1. Load the file (Pass-by-Value, but it's okay because it's User Role)
    # Note: In a real app, you might check context.state to see if it's already loaded
    filename = "learning_course.pdf"
    try:
        # Load the latest version
        report_artifact = await callback_context.load_artifact(filename=filename)

        if report_artifact and report_artifact.inline_data:
            print(f"Successfully loaded latest Python artifact '{filename}'.")
            print(f"MIME Type: {report_artifact.inline_data.mime_type}")
            pdf_bytes = report_artifact.inline_data.data
            print(f"Report size: {len(pdf_bytes)} bytes.")
        else:
            print(f"Python artifact '{filename}' not found.")

    except ValueError as e:
        print(f"Error loading Python artifact: {e}. Is ArtifactService configured?")
    except Exception as e:
        # Handle potential storage errors
        print(f"An unexpected error occurred during Python artifact load: {e}")

def create_instructor_agent(model):
    """
    Call this agent when the user wants to learn concepts, 
    understands symbols, or needs a tutorial on P&ID standards.
    """
    
    # Placeholder: Logic to invoke the Instructor Agent
    return Agent(
        name="instructor_agent",
        model=model,
        before_model_callback=inject_instructor_context,
        instruction="""
        You are a friendly and knowledgeable P&ID Instructor.
        
        **Context:** A Course Guide (`learning_course.pdf`) has been attached to the conversation. 
        You have direct access to this document in your context history.
        
        **Your Goal:** Teach the user about Process and Instrumentation Diagrams using the content of that attached guide.
        
        **Teaching Guidelines:**
        - **Source of Truth:** Base your explanations strictly on the provided guide. Do not lecture on general topics unless they are present in the material.
        - **Referencing:** When explaining a symbol or concept, explicitly mention the page number or section title where it is found (e.g., "As shown on slide 4...").
        - **Visual Descriptions:** Since the user might not be looking at the specific page you are, describe the visuals. (e.g., "The gate valve symbol looks like a bow-tie...").
        
        **Tone:**
        - Be patient and educational.
        - Use analogies to simplify complex chemical engineering concepts.
        - If a question is not covered in the guide, politely admit that the current course material does not address it.
        
        **Output Format:**
        - **Strictly use Markdown** for all responses.
        - Use **Bold** for key terms and concepts.
        - Use > Blockquotes for important definitions or rules from the guide.
        - Use Numbered Lists for step-by-step procedures.
        """,
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=16000,
            )
        )
    )

async def setup_artifact_service(app_name, user_id, session_id):
    """
    Initializes the InMemoryArtifactService and pre-loads 
    specific PDF documents from the local assets folder.
    """
    print("--- Bootstrapping Artifact Service ---")
    
    # 1. Initialize the Service
    artifact_service = InMemoryArtifactService()
    
    # 2. Define the files we want to preload
    # We map the local filename to the artifact name we want in the system

    files_to_load = [
        "learning_course.pdf", 
        "pid_sample_1.pdf"
    ]

    # 3. Iterate and Load
    for filename in files_to_load:
        file_path = ASSETS_DIR / filename
        
        if not file_path.exists():
            print(f"⚠️ Warning: {filename} not found in {ASSETS_DIR}")
            continue

        try:
            # Read the raw bytes from the local disk
            pdf_bytes = file_path.read_bytes()
            pdf_mime_type = "application/pdf"
            
            # Create the Gemini Part object
            # This is the format the LLM natively understands
            pdf_artifact_py = types.Part(
                inline_data=types.Blob(data=pdf_bytes, mime_type=pdf_mime_type)
            )
            
            # Save it into the In-Memory Service
            # Note: We use the filename as the key/ID for retrieval later
            await artifact_service.save_artifact(
                filename=filename, 
                artifact=pdf_artifact_py,
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
            
            print(f"✅ Loaded: {filename}")
            
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")

    print("--- Artifact Service Ready ---\n")
    return artifact_service


def create_pid_agent(project_id: str, location: str):
    print(f"project={project_id}, location={location}")
    vertexai.init(project=project_id, location=location)
    
    overseer_instructions = """
        You are the "Overseer," a specialized orchestrator for a Chemical Engineering P&ID Assistant.
        Your goal is to route user requests to the correct specialist sub-agent.

        You have access to three specialists:
        1. **Analyst:** Has access to specific P&ID PDF files. Use this for specific lookup questions (e.g., "What is the pressure on line 101?").
        2. **Instructor:** Has access to the Course Guide. Use this for "How-to" or educational questions (e.g., "What does this symbol mean?" or "Teach me about control loops").
        3. **Drafter:** Has access to the Reference Guide. Use this for visualization requests (e.g., "Draw a simple feed loop").

        **Rules:**
        - Do not attempt to answer technical questions yourself. Always delegate to a specialist.
        - If the user greets you, reply politely and explain your capabilities.
        - If a query is ambiguous, ask for clarification before routing.
        
        **Output Format:**
        - Format all your direct responses in **Markdown**.
        - Use bullet points when listing your available capabilities.
        """
    analyst = create_analyst_agent("gemini-3-pro-preview")
    instructor = create_instructor_agent("gemini-3-pro-preview")

    return Agent(
        model="gemini-3-pro-preview",
        name="overseer_agent",
        instruction=overseer_instructions,
        sub_agents=[analyst, instructor],
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True
            )
        )
    )