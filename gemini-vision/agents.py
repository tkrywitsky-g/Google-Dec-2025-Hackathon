import os
import json
from google.adk.agents import Agent
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

# Scout Agent (Vision) - Uses genai directly for image support
def run_scout_agent(image_path, model_name="gemini-2.0-flash-exp"):
    """Runs the Scout agent to analyze an image."""
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
        return response.text
    except Exception as e:
        return json.dumps({"error": str(e)})

# Risk Agent (Reasoning + Tool)
def get_risk_agent(model_name="gemini-2.0-flash-exp"):
    return Agent(
        name="risk_agent",
        model=model_name,
        description="Risk assessment officer checking compliance.",
        instruction=(
            "Review the detected objects. "
            "If heavy machinery or digging is present, query the permit database using the 'check_permit_database' tool. "
            "Assume the location is 'Location A' if the scene looks like a permitted site, or 'Location B' if it looks unauthorized, unless specified otherwise. "
            "If a permit exists, risk is LOW. "
            "If no permit exists, risk is HIGH. "
            "If only benign objects (cows, pickup trucks on roads) are present, risk is LOW. "
            "Output a structured assessment: 'risk_level' (High/Low) and 'reasoning' (string explanation)."
        ),
        tools=[check_permit_database]
    )

# Dispatcher Agent (Action)
def get_dispatcher_agent(model_name="gemini-2.0-flash-exp"):
    return Agent(
        name="dispatcher_agent",
        model=model_name,
        description="Operations dispatcher generating alerts.",
        instruction=(
            "You are an operations dispatcher. "
            "Based on the risk level provided by the Risk Officer, generate the final output. "
            "If Risk is HIGH, draft an urgent 'STOP WORK' SMS alert to the field manager. "
            "If Risk is LOW, generate a standard log entry. "
            "Return ONLY the final text payload."
        )
    )
