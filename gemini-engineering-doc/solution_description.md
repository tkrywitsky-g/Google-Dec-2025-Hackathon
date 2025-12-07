# Project Application Specification: "SkyGuard" ROW Monitor

## 1. Project Overview
Build a Python-based Streamlit application that serves as a "Starter Kit" for a hackathon. The app simulates an automated pipeline Right-of-Way (ROW) inspection workflow using Google Gemini models and an agentic architecture.

## 2. Tech Stack & Dependencies
* **Language:** Python 3.10+
* **Frontend:** Streamlit (`streamlit`)
* **AI/LLM:** `google-genai` (Google Gen AI SDK v2) or `google-cloud-aiplatform` (Vertex AI SDK).
* **Environment:** Managing API keys via `.env` or Streamlit secrets.

## 3. Core Architecture: Sequential Agent Chain
The application must implement a sequential chain of three distinct AI Agents. Data flows from Agent 1 -> Agent 2 -> Agent 3.

### Agent 1: "The Scout" (Multimodal Vision)
* **Model:** Gemini 2.5 Flash (Optimized for speed/vision).
* **Input:** An image (from file upload or pre-loaded selection).
* **System Instruction:** "You are an expert aerial surveyor for energy infrastructure. Analyze the provided image. Provide a detailed scene description (weather, terrain, lighting) and a structured list of potential risks or objects (vehicles, heavy machinery, digging activity, people, livestock)."
* **Output:** A JSON object containing `scene_description` (string) and `detected_objects` (list of strings).

### Agent 2: "The Risk Officer" (Reasoning & Compliance)
* **Model:** Gemini 3.0 Pro (Optimized for complex reasoning).
* **Input:** The JSON output from The Scout.
* **Tools:**
    * `check_permit_database(gps_location)`: A mock python function.
        * *Logic:* It should contain a hardcoded dictionary where 'Location A' returns `True` (Permit Active) and 'Location B' returns `False` (No Permit).
* **System Instruction:** "Review the detected objects. If heavy machinery or digging is present, query the permit database. If a permit exists, risk is LOW. If no permit exists, risk is HIGH. If only benign objects (cows, pickup trucks on roads) are present, risk is LOW."
* **Output:** A structured assessment: `risk_level` (High/Low) and `reasoning` (string explanation).

### Agent 3: "The Dispatcher" (Action/Response)
* **Model:** Gemini 2.5 Flash.
* **Input:** The assessment from The Risk Officer.
* **System Instruction:** "You are an operations dispatcher. Based on the risk level, generate the final output. If Risk is HIGH, draft an urgent 'STOP WORK' SMS alert to the field manager. If Risk is LOW, generate a standard log entry."
* **Output:** The final text payload.

## 4. UI Requirements (Streamlit)
* **Sidebar:**
    * API Key input (optional, if not in env).
    * "Scenario Selector": Buttons to load 3 pre-set images (Clear, Farm/False Alarm, Excavator/Threat).
    * "Custom Upload": File uploader widget.
* **Main Layout (3 Columns):**
    * **Col 1 (The View):** Displays the selected image.
    * **Col 2 (The Brain):** Displays the "Thought Process." Show the raw output from Agent 1 and Agent 2 (e.g., "Scout saw: Excavator... Risk Officer checked DB: No Permit...").
    * **Col 3 (The Action):** Displays the final output from Agent 3 (The SMS or Log entry) in a highlighted box (Red for High risk, Green for Low).

## 5. Mock Data Needed
* Create a dummy `utils.py` with the `check_permit_database` function.
* Assume images are stored in a local `assets/` folder.