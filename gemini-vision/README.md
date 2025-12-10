# 🦅 Project SkyGuard: Autonomous ROW Integrity Agent

> **Welcome to the Gemini Vision Hackathon!**
> You have been given the "Starter Kit" for the next generation of pipeline integrity monitoring.

## 🎯 The Mission
Your company monitors thousands of kilometers of Right-of-Way (ROW). Currently, identifying threats (like unauthorized digging) requires manual review of aerial photos.

**The Vision:** We are moving to a model where drone fleets send imagery to the cloud, where a **Multi-Agent AI System** analyzes threats in real-time.

Your goal today: Take this "Starter Kit"—which detects excavators—and make it smarter, safer, and more robust.

## 🏗 The Architecture
This repository implements a **Sequential Agent Pipeline** using Google's Agent Developer Kit (ADK). Think of it as an assembly line where each agent specializes in one task:

1.  **Agent 1: The Scout (Gemini 2.5 Flash)**
    * *Role:* The "Eyes." Uses vision analysis to describe the scene and identify objects (vehicles, livestock, machinery, digging activity).
    * *Tool:* `analyze_aerial_image()` - processes images and returns structured JSON with scene description and detected objects.

2.  **Agent 2: The Risk Officer (Gemini 2.5 Flash)**
    * *Role:* The "Brain." Evaluates the scene intelligently:
      - Assumes typical rural scenes are safe (livestock, farm vehicles, normal weather)
      - Only checks permits for unusual activity (heavy machinery, excavation)
    * *Tool:* `check_permit_database()` - queries active permits when needed.

3.  **Agent 3: The Dispatcher (Gemini 2.5 Flash)**
    * *Role:* The "Voice." Formats the assessment into actionable output:
      - High Risk → Urgent "STOP WORK" SMS alert
      - Low Risk → Standard log entry

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* A Google Cloud Project with Vertex AI API enabled

### Installation
1.  **Navigate to the project:**
    ```bash
    cd gemini-vision
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    
    This installs:
    - `streamlit` - for the web UI
    - `google-adk` - Google's Agent Developer Kit
    - `python-dotenv` - for environment variables

3.  **Configure environment variables:**
    Copy the template file and update with your project details:
    ```bash
    cp .env_template .env
    ```
    
    Edit `.env` with your Google Cloud project settings:
    ```text
    # Required for ADK to use Vertex AI
    GOOGLE_GENAI_USE_VERTEXAI=True
    
    # Your Google Cloud Project ID
    GOOGLE_CLOUD_PROJECT="your-project-id"
    
    # The Vertex AI location/region
    GOOGLE_CLOUD_LOCATION="us-central1"
    ```
    
    > **Note:** Ensure you have authenticated with Google Cloud:
    > ```bash
    > gcloud auth application-default login
    > ```

4.  **Add test images:**
    Place aerial images in `assets/` directory:
    - `clear.jpg` - clear ROW scene
    - `farm.jpg` - farm with livestock
    - `excavator.jpg` - heavy machinery

5.  **Run the App:**
    ```bash
    streamlit run app.py
    ```
    
    The app will open at `http://localhost:8501`

## 🎨 The UI
The Streamlit interface has three columns:

1. **The View** - Displays the aerial image (select scenario or upload custom)
2. **The Brain** - Shows Scout analysis and Risk assessment with expandable sections
3. **The Action** - Displays the final Dispatcher alert (color-coded by risk level)

## 🛠 Hackathon Challenges (Extend this Code!)

This starter kit is just the beginning. Choose a challenge below and use ADK to extend the functionality:

* **The "Weather-Wise" Extension:**
    * Add a 4th agent that checks weather APIs. If Scout sees mud + Weather Agent reports recent rain, flag for "Slope Stability Risk."
    * Hint: Add a new tool function and insert the agent into the `SequentialAgent` chain.

* **The "Forensics" Upgrade:**
    * Enhance the Scout's vision prompt to identify company logos on vehicles.
    * Hint: Modify the `analyze_aerial_image` tool prompt to focus on text/branding detection.

* **The "Human-in-the-Loop" Handover:**
    * Add a confidence score to the Risk Agent's output schema. If < 70%, route to human review instead of auto-dispatch.
    * Hint: Update the `RiskAssessment` Pydantic model and add conditional logic in Dispatcher.

* **The "Multi-Modal" Boost:**
    * Add audio analysis. Create a tool that processes drone audio files to detect machinery sounds.
    * Hint: Use Gemini's audio capabilities with a new analysis function.

## 📚 Resources
* [Google ADK Documentation](https://github.com/google/adk)
* [Google Generative AI SDK](https://ai.google.dev/gemini-api/docs)
* [Streamlit Documentation](https://docs.streamlit.io/)

## 🔧 Key Technical Details
* **Framework:** Google Agent Developer Kit (ADK)
* **Pipeline:** `SequentialAgent` chains Scout → Risk → Dispatcher
* **Structured Output:** Pydantic schemas ensure consistent JSON responses
* **Tools:** Function calling for vision analysis and permit database
* **Session Management:** In-memory sessions for stateful conversations
