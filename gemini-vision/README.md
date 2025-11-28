# 🦅 Project SkyGuard: Autonomous ROW Integrity Agent

> **Welcome to the Gemini Vision Hackathon!**
> You have been given the "Starter Kit" for the next generation of pipeline integrity monitoring.

## 🎯 The Mission
Your company monitors thousands of kilometers of Right-of-Way (ROW). Currently, identifying threats (like unauthorized digging) requires manual review of aerial photos.

**The Vision:** We are moving to a model where drone fleets send imagery to the cloud, where a **Multi-Agent AI System** analyzes threats in real-time.

Your goal today: Take this "Starter Kit"—which detects excavators—and make it smarter, safer, and more robust.

## 🏗 The Architecture
This repository implements a **Sequential Agent Chain** using Google's Agent Developer Kit (ADK) patterns.



1.  **Agent 1: The Scout (Gemini 2.5 Flash)**
    * *Role:* The "Eyes." It uses Multimodal capabilities to describe the scene and list every object it sees (trucks, cows, digging, markers).
2.  **Agent 2: The Risk Officer (Gemini 3.0 Pro)**
    * *Role:* The "Brain." It takes the Scout's list and cross-references it with a (mock) Permit Database. It decides if an object is a threat or authorized work.
3.  **Agent 3: The Dispatcher (Gemini 2.5 Flash)**
    * *Role:* The "Voice." It formats the result into a specific action (e.g., an SMS alert, a Work Order, or a Log Entry).

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* A Google Cloud Project with Vertex AI API enabled

### Installation
1.  **Clone the repo:**
    ```bash
    git clone [https://github.com/your-org/skyguard-starter.git](https://github.com/your-org/skyguard-starter.git)
    cd skyguard-starter
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set your API Key:**
    Create a `.env` file and add your key:
    ```text
    GOOGLE_API_KEY="your_api_key_here"
    ```

4.  **Run the App:**
    ```bash
    streamlit run app.py
    ```

## 🛠 Hackathon Challenges (Extend this Code!)

This starter kit is just the beginning. Choose a "Bounty" below and use your ADK skills to extend the functionality:

* **The "Weather-Wise" Extension:**
    * *Challenge:* Add a new Agent that checks weather data. If the Scout sees heavy mud and the Weather Agent reports rain, flag the site for "Slope Stability Risk" even if no vehicles are present.
* **The "Forensics" Upgrade:**
    * *Challenge:* Modify the Scout's prompt to zoom in on machinery. Can you identify the company logo on the side of the truck?
* **The "Human-in-the-Loop" Handover:**
    * *Challenge:* If the Risk Officer is "Unsure" (confidence < 70%), route the alert to a new "Human Review" queue instead of sending an automatic SMS.
* **The "Audio" Input:**
    * *Challenge:* Simulate a drone audio feed. Create an agent that listens for heavy machinery sounds to confirm visual detections.

## 📚 Resources
* [Google Generative AI SDK Documentation](https://ai.google.dev/python/google-generative-ai)
* [Streamlit Documentation](https://docs.streamlit.io/)