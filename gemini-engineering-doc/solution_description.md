# Project Application Specification: Gemini P&ID Multi-Agent

## 1. Project Overview
Build a Python-based Streamlit application that demonstrates a **Multi-Agent Architecture** for the Oil & Gas/Engineering domain. The app acts as an intelligent assistant that can both analyze technical Piping and Instrumentation Diagrams (P&IDs) and teach users about engineering standards using reference materials.

## 2. Tech Stack & Dependencies
* **Language:** Python 3.10+
* **Frontend:** Streamlit
* **AI Framework:** Google Agent Developer Kit (`google-adk`)
* **LLM:** Google Gemini 3 Pro (via Vertex AI)
* **SDKs:** `google-genai`, `google-cloud-aiplatform` (for Vertex AI init)
* **Key Features:**
    * **Thinking Models:** Sub-agents use `thinking_config` with a budget of 16k tokens for complex visual reasoning and educational planning.
    * **Artifact Service:** In-memory injection of PDF context (Pass-by-value) for agents.
    * **Asynchronous Execution:** Uses `asyncio` for non-blocking agent operations.

## 3. Core Architecture: Hub-and-Spoke
The application implements a hierarchical architecture where a central "Overseer" routes tasks to specialized "Thinking" sub-agents.

### Agent 1: "The Overseer" (Router)
* **Role:** The interface layer. It does not answer technical questions directly.
* **Logic:** Analyzes user intent to delegate work:
    * Specific diagram questions $\rightarrow$ **Analyst**.
    * "How-to" or educational questions $\rightarrow$ **Instructor**.
    * Visualization requests $\rightarrow$ **Drafter** (Stub/Future).
* **Configuration:** `gemini-3-pro-preview` (Standard configuration for fast routing).

### Agent 2: "The Analyst" (Visual & Technical QA)
* **Role:** Senior Process Engineer.
* **Configuration:** `gemini-3-pro-preview` with **Thinking Enabled** (16k budget).
* **Capabilities:**
    * Has direct "visual" access to specific P&ID files (e.g., `pid_sample_1.pdf`) via Artifact Service.
    * Uses "Thinking" to trace lines and resolve ambiguous tags before answering.
* **Callback:** `inject_pid_context` loads the PDF byte stream.

### Agent 3: "The Instructor" (Educational RAG)
* **Role:** P&ID Instructor.
* **Configuration:** `gemini-3-pro-preview` with **Thinking Enabled** (16k budget).
* **Capabilities:**
    * Has access to course material (e.g., `learning_course.pdf`).
    * Uses "Thinking" to plan lesson structures and analogies based on the curriculum.
* **Callback:** `inject_instructor_context` loads the training material.

## 4. UI Requirements (Streamlit)
* **Sidebar:**
    * Configuration for Google Cloud Project ID and Location.
    * Architecture diagram display.
* **Main Layout (Dashboard):**
    * **Agent Profiles:** Visual cards for Overseer, Analyst, and Instructor.
    * **Context Viewers:** Expandable PDF viewers allowing the user to see the same documents the agents are reading.
* **Interaction Flow:**
    * **Query Selection:** Dropdown with pre-set "Golden Path" questions.
    * **Reasoning Log:** An expandable "Glass Box" view showing the Agent's internal thought process (streaming `part.thought` events) and tool calls.
    * **Final Output:** The final answer presented clearly outside the logs.

## 5. Data Requirements
* **Local Assets (`/assets`):**
    * `pid_sample_1.pdf`: A sample engineering diagram.
    * `learning_course.pdf`: A training manual or standard guide.
    * Agent avatars (`overseer.png`, `analyst.png`, `instructor.png`).