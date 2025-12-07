from google.adk.agents import Agent
from google.genai import types
from google.adk.planners import BuiltInPlanner
from google.adk.artifacts import InMemoryArtifactService
from pathlib import Path
from google.adk.tools import ToolContext

from google.adk import Agent
model = "gemini-3-pro-preview"
image_model = "gemini-3-pro-image-preview"
ASSETS_DIR = Path("./assets")

# TOOL for Analyst Sub Agent to get files from Artifact Serivce
def fetch_pid_diagram(tool_context: ToolContext):
    """
    Retrieves the 'pid_sample_1.pdf' document from the artifact store.
    Call this tool immediately when asked questions about line numbers, 
    valves, or equipment in the project documentation.
    """
    # The filename matches what we defined in bootstrap.py
    filename = "pid_sample_1.pdf" 
    
    try:
        print(f"[Analyst] Fetching {filename}...")
        
        # We access the service via the context provided by the Runner
        # This returns the specific version of the artifact we saved earlier
        artifact = tool_context.load_artifact(filename)
        
        # We return the artifact directly. 
        # The ADK Runner automatically injects this 'Part' (PDF bytes) 
        # into the model's context window.
        return artifact
        
    except Exception as e:
        return f"Error: Could not retrieve P&ID file. Details: {e}"
    
def call_pid_analyst(query: str):

    return Agent(
        name="PID_Analyst",
        model=model,
        
        # Register the tool we just created
        tools=[fetch_pid_diagram],
        
        instructions="""
        You are a Senior Process Engineer acting as a P&ID Analyst.
        
        **Your Goal:** Answer technical questions based *strictly* on the provided P&ID diagram.
        
        **Critical Instruction:**
        You cannot answer questions until you see the diagram. 
        ALWAYS call the tool `fetch_pid_diagram` as your first step.
        
        **Analysis Guidelines:**
        - Trace lines carefully from source to destination.
        - Identify components by their tag numbers (e.g., V-101, P-20A).
        - If a symbol is ambiguous, describe its visual appearance and ask the user to clarify.
        - Do not assume standards from external knowledge; look at the diagram first.
        """
    )

def fetch_course_guide(tool_context: ToolContext):
    """
    Retrieves the 'learning_course.pdf' from the artifact store.
    Call this tool when the user asks 'How-to' questions, asks for definitions, 
    or wants to learn about P&ID symbols and standards.
    """
    filename = "learning_course.pdf"
    try:
        print(f"[Instructor] Opening course material: {filename}...")
        artifact = tool_context.load_artifact(filename)
        return artifact
    except Exception as e:
        return f"Error: Could not retrieve Course Guide. Details: {e}"
    
def call_course_instructor(query: str):
    """
    Call this agent when the user wants to learn concepts, 
    understands symbols, or needs a tutorial on P&ID standards.
    """
    # Placeholder: Logic to invoke the Instructor Agent
    return Agent(
        name="PID_Instructor",
        model=model,
        tools=[fetch_course_guide],
        instructions="""
        You are a friendly and knowledgeable P&ID Instructor.
        
        **Your Goal:** Teach the user about Process and Instrumentation Diagrams using the provided Course Guide.
        
        **Workflow:**
        1. Always access the `learning_course.pdf` using your tool before answering.
        2. When explaining a symbol or concept, reference the specific section or page in the guide if possible.
        3. If the user asks about a specific symbol, describe it visually based on the guide.
        
        **Tone:**
        - Be patient and educational.
        - Use analogies if they help explain complex chemical engineering concepts.
        - If the user asks a question not covered in the guide, admit you don't know rather than guessing.
        """
    )

#   generate_content_config = types.GenerateContentConfig(
#     temperature = 1,
#     top_p = 0.95,
#     max_output_tokens = 32768,
#     response_modalities = ["IMAGE"],
#     safety_settings = [types.SafetySetting(
#       category="HARM_CATEGORY_HATE_SPEECH",
#       threshold="OFF"
#     ),types.SafetySetting(
#       category="HARM_CATEGORY_DANGEROUS_CONTENT",
#       threshold="OFF"
#     ),types.SafetySetting(
#       category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
#       threshold="OFF"
#     ),types.SafetySetting(
#       category="HARM_CATEGORY_HARASSMENT",
#       threshold="OFF"
#     )],
#     image_config=types.ImageConfig(
#       aspect_ratio="1:1",
#       image_size="1K",
#       output_mime_type="image/png",
#     ),
#   )
def fetch_reference_guide(tool_context: ToolContext):
    """
    Retrieves the 'reference_guide.pdf' from the artifact store.
    Call this tool when the user asks to draw, sketch, or generate a diagram.
    This guide contains the standard symbols and assembly patterns.
    """
    filename = "reference_guide.pdf"
    try:
        print(f"[Drafter] Consult standards in: {filename}...")
        artifact = tool_context.load_artifact(filename)
        return artifact
    except Exception as e:
        return f"Error: Could not retrieve Reference Guide. Details: {e}"
    
def call_drafter(query: str):
    """
    Call this agent when the user asks to generate, draw, or visualize 
    a P&ID segment or component.
    """
    # Placeholder: Logic to invoke the Drafter Agent
    return Agent(
        name="PID_Drafter",
        model=image_model,
        tools=[fetch_reference_guide],
        instructions="""
        You are a Technical Draftsman specialized in generating P&ID schemas.
        
        **Your Goal:** Convert user requests into valid Mermaid.js flowchart code.
        
        **Workflow:**
        1.  **Consult Standards:** Use `fetch_reference_guide` to check if the requested assembly (e.g., "Bypass Loop") has a standard configuration.
        2.  **Plan the Topology:** Identify the main flow (Left to Right) and the components.
        3.  **Generate Code:** Output a Markdown code block containing the graph.
        
        **Formatting Rules:**
        - Use `mermaid` syntax.
        - Use `flowchart LR` (Left-to-Right) orientation.
        - Represent Tanks/Vessels as subgraphs or cylindrical shapes `[()]`.
        - Represent Valves as specific nodes, e.g., `V101{{Gate Valve}}`.
        - Label lines with the medium if known (e.g., `Tank -->|Water| Pump`).
        
        **Example Output:**
        ```mermaid
        flowchart LR
            A[Tank 1] -->|Feed| B(Pump 101)
            B --> C{Valve 202}
            C -->|Main| D[Mixer]
            C -->|Bypass| E[Drain]
        ```
        """
    )

async def setup_artifact_service():
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
        "reference_guide.pdf", 
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
            file_bytes = file_path.read_bytes()
            
            # Create the Gemini Part object
            # This is the format the LLM natively understands
            artifact_part = types.Part.from_bytes(
                data=file_bytes,
                mime_type="application/pdf"
            )
            
            # Save it into the In-Memory Service
            # Note: We use the filename as the key/ID for retrieval later
            await artifact_service.save_artifact(
                filename=filename, 
                artifact=artifact_part
            )
            
            print(f"✅ Loaded: {filename}")
            
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")

    print("--- Artifact Service Ready ---\n")
    return artifact_service


def get_pandid_agent():
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
        """

    return Agent(
        model=model,
        name="Overseer",
        instructions=overseer_instructions,
        tools=[call_pid_analyst, call_course_instructor, call_drafter],
        planner=BuiltInPlanner(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                # thinking_budget=1024,
                thinking_level="high",
            )
        )
    )