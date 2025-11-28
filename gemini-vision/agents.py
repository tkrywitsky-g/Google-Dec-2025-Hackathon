import os
import json
from google.adk.agents import Agent, SequentialAgent
from google import genai
from google.genai import types

# Mock Permit Database Tool
def check_permit_database(gps_location: str) -> dict:
    """Checks the permit database for a given GPS location.

    Args:
        gps_location (str): The GPS location to check (e.g., "Location A").

    Returns:
        dict: A dictionary containing the permit status and reasoning.
    """
    # Mock database logic
    if "Location A" in gps_location:
        return {"permit_active": True, "details": "Valid permit #12345 found for excavation."}
    elif "Location B" in gps_location:
        return {"permit_active": False, "details": "No active permits found for this location."}
    else:
        return {"permit_active": False, "details": "Location not found in database."}


# Vision Analysis Function Tool - Uses genai client
def analyze_aerial_image(image_path: str, model_name: str = "gemini-2.0-flash-exp") -> dict:
    """Analyzes an aerial image for energy infrastructure monitoring.
    
    Args:
        image_path (str): Path to the image file to analyze.
        model_name (str): The Gemini model to use for analysis.
        
    Returns:
        dict: A dictionary with 'scene_description' (string) and 'detected_objects' (list of strings).
    """
    try:
        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        
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
            
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, types.Part.from_bytes(data=image_bytes, mime_type=mime_type)],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        # Parse the JSON response
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e), "scene_description": "", "detected_objects": []}


# Scout Agent - Uses vision analysis tool
def get_scout_agent(model_name="gemini-2.0-flash-exp"):
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
        output_key="scout_results"
    )


# Risk Agent - Reasoning + Tool with state injection
def get_risk_agent(model_name="gemini-2.0-flash-exp"):
    return Agent(
        name="risk_agent",
        model=model_name,
        description="Risk assessment officer checking compliance.",
        instruction=(
            "You are a risk assessment officer. "
            "Review the scout's analysis: {scout_results}\n\n"
            "Based on the detected objects:\n"
            "- If heavy machinery or digging activity is present, use the 'check_permit_database' tool to verify permits.\n"
            "- Assume the location is 'Location A' if the scene looks like a permitted site, or 'Location B' if it looks unauthorized.\n"
            "- If a permit exists, risk is LOW.\n"
            "- If no permit exists, risk is HIGH.\n"
            "- If only benign objects (cows, pickup trucks on roads) are present, risk is LOW.\n\n"
            "Output a structured assessment with 'risk_level' (High/Low) and 'reasoning' (string explanation)."
        ),
        tools=[check_permit_database],
        output_key="risk_assessment"
    )


# Dispatcher Agent - Action with state injection
def get_dispatcher_agent(model_name="gemini-2.0-flash-exp"):
    return Agent(
        name="dispatcher_agent",
        model=model_name,
        description="Operations dispatcher generating alerts.",
        instruction=(
            "You are an operations dispatcher. "
            "Based on the risk assessment: {risk_assessment}\n\n"
            "Generate the final output:\n"
            "- If Risk is HIGH, draft an urgent 'STOP WORK' SMS alert to the field manager.\n"
            "- If Risk is LOW, generate a standard log entry.\n\n"
            "Return ONLY the final text payload (SMS or log entry)."
        ),
        output_key="final_action"
    )


# Sequential Agent Pipeline
def get_infrastructure_monitoring_pipeline(model_name="gemini-2.0-flash-exp"):
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
def run_scout_agent(image_path, model_name="gemini-2.0-flash-exp"):
    """Legacy function for backward compatibility. Use get_infrastructure_monitoring_pipeline() for new code."""
    result = analyze_aerial_image(image_path, model_name)
    return json.dumps(result)
