# Gemini RCA Agent: Autonomous Root Cause Analysis

Welcome to the Gemini CLI! This project demonstrates a powerful Root Cause Analysis (RCA) agent built with Google's Agent Developer Kit (ADK).

🎯 The Mission
Your company faces complex network incidents. Currently, identifying the root cause requires manual correlation of various logs and data sources. The Vision: We are moving to a model where a Multi-Agent AI System analyzes incident data in real-time to pinpoint root causes and propose actionable solutions.

Your goal today: Utilize this starter kit to automate and enhance the root cause analysis process for network incidents.

🏗 The Architecture
This repository implements a Sequential Agent Pipeline using Google's Agent Developer Kit (ADK). Think of it as an assembly line where each agent specializes in one task:

Agent 1: The NetworkLogResearcher (Gemini 2.5 Pro)
Role: The "Investigator." Analyzes ServiceNow incidents and Versa SD-WAN logs to identify critical events and correlations.
Tool: read_logs() - processes a list of CSV file paths and returns their content as a single string.

Agent 2: The NetworkAnalyst (Gemini 2.5 Pro)
Role: The "Hypothesizer." Evaluates the correlated events and integrates external data (like weather) to form a hypothesis about the root cause.
Tool: get_weather_report() - queries weather data for a given date and location from a CSV file.

Agent 3: The DispatchCoordinator (Gemini 2.5 Pro)
Role: The "Action Planner." Formats the assessment into actionable recommendations for the field operations team.
Tools: send_email(), update_servicenow_case() - mock tools to simulate sending email notifications and updating ServiceNow cases.

🚀 Getting Started
Prerequisites
Python 3.10+
A Google API Key with access to the Gemini models.

Installation
Navigate to the project:

```bash
cd gemini-root-cause
```
Install dependencies:

```bash
pip install -r requirements.txt
```
This installs:
- streamlit - for the web UI
- google-adk - Google's Agent Developer Kit
- python-dotenv - for environment variables
- pandas - for data manipulation

Set your API Key: Create a .env file in the gemini-root-cause directory:

```
GOOGLE_API_KEY="your_api_key_here"
```
Run the App:

```bash
streamlit run app.py
```
The app will open at http://localhost:8501

🎨 The UI
The Streamlit interface has two columns:
- The Data Sources - Displays the ServiceNow incidents, Versa SD-WAN logs, and Weather API data.
- The Agent Analysis - Shows the Researcher's Findings, Hypothesis, and Final Recommendation. It also includes a button to submit the recommendation.

🛠 Hackathon Challenges (Extend this Code!)
This starter kit is just the beginning. Choose a challenge below and use ADK to extend the functionality:

The "Dynamic Data Ingestion" Extension:
Modify the read_logs tool to dynamically ingest data from various sources (e.g., live APIs, databases) instead of static CSV files.
Hint: Update the read_logs tool to connect to external services.

The "Proactive Monitoring" Upgrade:
Enhance the researcher agent to proactively monitor incoming logs and trigger an RCA pipeline when anomalies are detected.
Hint: Implement a monitoring mechanism that feeds new log data to the researcher.

The "Actionable Feedback Loop":
Implement the actual functionality for the send_email and update_servicenow_case tools, connecting them to real email services and ServiceNow instances.
Hint: Replace the mock tool implementations with actual API calls.

The "Multi-Incident Analysis" Boost:
Extend the system to handle multiple concurrent incidents, prioritizing and analyzing them in parallel.
Hint: Explore ParallelAgent or more complex orchestration patterns.

The "Financial Impact Calculator" Extension:
Integrate a tool that estimates the financial impact of an incident based on downtime, affected services, and other relevant metrics.
Hint: Create a new tool function that takes incident parameters and calculates a cost estimate.

📚 Resources
Google ADK Documentation
Google Generative AI SDK
Streamlit Documentation
Pandas Documentation

🔧 Key Technical Details
Framework: Google Agent Developer Kit (ADK)
Pipeline: SequentialAgent chains NetworkLogResearcher → NetworkAnalyst → DispatchCoordinator
Structured Output: Pydantic schemas ensure consistent JSON responses (implicitly, as ADK handles this)
Tools: Function calling for log reading and weather data retrieval, mock tools for email and ServiceNow updates.
Session Management: In-memory sessions for stateful conversations