import os
import json
import vertexai
from google.adk.agents import Agent, SequentialAgent
from vertexai.preview.generative_models import (
    GenerativeModel,
    Part,
    GenerationConfig,
    Image,
)
from pydantic import BaseModel, Field
from typing import List


# Mock Permit Database Tool
def check_permit_database(gps_location: str) -> dict:
    """Checks the permit database for a given GPS location.

    Args:
        gps_location (str): The GPS location to check (e.g., "Location A").

    Returns:
        dict: A dictionary containing the active permits for the site.
    """
    # Return active permits for vegetation management and ATV based inspection
    return {
        "active_permits": [
            {
                "permit_id": "PM-2025-001",
                "type": "Vegetation Management",
                "status": "Active",
                "details": "Authorized vegetation clearing and maintenance",
            },
            {
                "permit_id": "PM-2025-002",
                "type": "ATV Based Inspection",
                "status": "Active",
                "details": "Authorized ATV use for infrastructure inspection",
            },
        ]
    }


# Vision Analysis Function Tool - Uses genai client
def analyze_aerial_image(image_path: str, model_name: str = "gemini-2.5-flash") -> dict:
    """Analyzes an aerial image for energy infrastructure monitoring.

    Args:
        image_path (str): Path to the image file to analyze.
        model_name (str): The Gemini model to use for analysis.

    Returns:
        dict: A dictionary with 'scene_description' (string) and 'detected_objects' (list of strings).
    """
    try:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION")

        vertexai.init(project=project_id, location=location)

        # Read image
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        prompt = (
            "You are an expert aerial surveyor for energy infrastructure. "
            "Analyze the provided image. "
            "Provide a detailed scene description (weather, terrain, lighting) "
            "and a structured list of potential risks or objects (vehicles, heavy machinery, digging activity, people, livestock). "
            "Output JSON with keys: 'scene_description' (string) and 'detected_objects' (list of strings)."
        )

        # Determine mime type
        mime_type = "image/png"
        if image_path.lower().endswith((".jpg", ".jpeg")):
            mime_type = "image/jpeg"

        model = GenerativeModel(model_name)
        response = model.generate_content(
            [Part.from_data(data=image_bytes, mime_type=mime_type), prompt],
            generation_config=GenerationConfig(response_mime_type="application/json"),
        )

        # Parse the JSON response
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e), "scene_description": "", "detected_objects": []}

# Scout Agent - Uses vision analysis tool
def get_scout_agent(model_name="gemini-2.5-flash"):
    class ScoutOutput(BaseModel):
        scene_description: str = Field(description="Detailed description of the scene including weather, terrain, and lighting conditions.")
        detected_objects: List[str] = Field(description="List of detected objects or potential risks in the image.")
    
    return Agent(
        name="scout_agent",
        model=model_name,
        description="Aerial surveyor analyzing infrastructure images.",
        instruction=(
            "You are an expert aerial surveyor for energy infrastructure. "
            "Use the 'analyze_aerial_image' tool to analyze the provided image path. "
            "The tool will return a scene description and list of detected objects. "
            "Present the analysis results in a clear, structured format."
        ),
        tools=[analyze_aerial_image],
        output_schema=ScoutOutput,
        output_key="scout_results"
    )


# Risk Agent - Reasoning + Tool with state injection
def get_risk_agent(model_name="gemini-2.5-flash"):
    class RiskAssessment(BaseModel):
        risk_level: str = Field(description="Risk level assessment: either 'High' or 'Low'.")
        reasoning: str = Field(description="Detailed explanation of the risk assessment decision.")
    
    return Agent(
        name="risk_agent",
        model=model_name,
        description="Risk assessment officer checking compliance.",
        instruction=(
            "You are a risk assessment officer. "
            "Review the scout's analysis: {scout_results}\n\n"
            "ASSUME BENIGN CONDITIONS for typical rural scenes:\n"
            "- Livestock (cows, horses, etc.) are normal and expected - risk is LOW\n"
            "- Standard vehicles on roads or farm vehicles (pickups, tractors, combines) are normal - risk is LOW\n"
            "- Clear weather and typical terrain features are normal - risk is LOW\n\n"
            "ONLY check permits using 'check_permit_database' if you detect unusual activities such as:\n"
            "- Heavy machinery (excavators, backhoes, bulldozers)\n"
            "- Digging or excavation activity\n"
            "- Unexpected vehicles or equipment out of place for a rural setting\n"
            "- Suspicious or unauthorized activities near infrastructure\n\n"
            "If you need to check permits:\n"
            "- Use the tool to retrieve active permits\n"
            "- Compare detected activities against permitted activities (Vegetation Management, ATV Based Inspection)\n"
            "- If activity matches permits, risk is LOW\n"
            "- If activity does NOT match any permits, risk is HIGH\n\n"
            "Output a structured assessment with 'risk_level' (High/Low) and 'reasoning' (string explanation)."
        ),
        tools=[check_permit_database],
        output_schema=RiskAssessment,
        output_key="risk_assessment"
    )


# Dispatcher Agent - Action with state injection
def get_dispatcher_agent(model_name="gemini-2.5-flash"):
    class DispatcherOutput(BaseModel):
        message: str = Field(description="The final output message - either an urgent SMS alert or a standard log entry.")
    
    return Agent(
        name="dispatcher_agent",
        model=model_name,
        description="Operations dispatcher generating alerts.",
        instruction=(
            "You are an operations dispatcher. "
            "Based on the risk assessment: {risk_assessment}\n\n"
            "Generate the final output:\n"
            "- If Risk is HIGH, draft an urgent 'STOP WORK' SMS alert to the field manager.\n"
            "- If Risk is LOW, generate a standard log entry."
        ),
        output_schema=DispatcherOutput,
        output_key="final_action"
    )


# Sequential Agent Pipeline
def get_infrastructure_monitoring_pipeline(model_name="gemini-2.5-flash"):
    """Creates a sequential agent pipeline for infrastructure monitoring.
    
    Returns:
        SequentialAgent: A pipeline that sequentially executes scout, risk, and dispatcher agents.
    """
    scout_agent = get_scout_agent(model_name)
    risk_agent = get_risk_agent(model_name)
    dispatcher_agent = get_dispatcher_agent(model_name)
    
    return SequentialAgent(
        name="infrastructure_monitoring_pipeline",
        sub_agents=[scout_agent, risk_agent, dispatcher_agent],
        description="Sequential pipeline for infrastructure monitoring: vision analysis, risk assessment, and action dispatch."
    )


# Backward compatibility: keep the old function for existing code
def run_scout_agent(image_path, model_name="gemini-2.5-flash"):
    """Legacy function for backward compatibility. Use get_infrastructure_monitoring_pipeline() for new code."""
    result = analyze_aerial_image(image_path, model_name)
    return json.dumps(result)
