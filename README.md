# Google-Dec-2025-Hackathon

This repository contains starter kits for the Google Gemini Hackathon (December 2025).

## 🦅 gemini-vision

A **Sequential Agent Pipeline** demo for infrastructure monitoring using Google's Agent Developer Kit (ADK). 

**Use Case:** Autonomous analysis of aerial drone imagery for Right-of-Way (ROW) monitoring.

**How it works:**
- **Scout Agent** - Uses Gemini vision to analyze aerial images and detect objects
- **Risk Officer Agent** - Evaluates detected objects against permit database
- **Dispatcher Agent** - Generates alerts or log entries based on risk assessment

Built with ADK's `SequentialAgent`, Pydantic schemas for structured outputs, and a Streamlit UI.

👉 [See full documentation](gemini-vision/README.md)

## 🕵️ gemini-root-cause

A **Sequential Agent Pipeline** for autonomous root cause analysis of network incidents.

**Use Case:** Autonomous analysis of network incidents to pinpoint root causes and propose actionable solutions.

**How it works:**
- **NetworkLogResearcher Agent** - Analyzes ServiceNow incidents and Versa SD-WAN logs.
- **NetworkAnalyst Agent** - Evaluates events and integrates external data (like weather) to form a hypothesis.
- **DispatchCoordinator Agent** - Formats the assessment into actionable recommendations.

Built with ADK's `SequentialAgent`, Pydantic schemas, and a Streamlit UI.

👉 [See full documentation](gemini-root-cause/README.md)
