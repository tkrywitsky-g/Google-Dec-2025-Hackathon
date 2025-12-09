# 🏭 Gemini P&ID Orchestrator

> **An Agentic Workflow for Engineering Document Analysis**
> This demo showcases how to use the Google Agent Developer Kit (ADK) to build a hierarchical AI system that can read complex engineering diagrams (P&IDs) and teach users about them.

## 🎯 The Mission
Processing P&IDs (Piping and Instrumentation Diagrams) usually requires two distinct skill sets:
1.  **Visual Analysis:** Tracing lines, reading tags, and understanding connectivity.
2.  **Domain Knowledge:** Understanding symbols, standards, and engineering rules.

This application solves this by using an **Orchestrator Pattern**. A central "Overseer" agent listens to the user and dynamically routes the request to the correct specialist—either the "Analyst" (who looks at the diagram) or the "Instructor" (who reads the training manual).

## 🏗 The Architecture

This project uses **Google ADK** to manage state, artifacts, and routing.

* **The Overseer (Gemini 2.5 Pro):** The boss. It creates a plan and delegates tasks. It uses `ThinkingConfig` to reason about *which* agent is best suited for the query.
* **The Analyst:** A sub-agent equipped with `pid_sample_1.pdf` in its context window. It answers questions like *"What does this document depict?"*
* **The Instructor:** A sub-agent equipped with `learning_course.pdf`. It answers questions like *"What are the key components of a P&ID?"*

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* A Google Cloud Project with Vertex AI API enabled.
* Access to Gemini 2.5 Pro (or Flash) models.

### Installation

1.  **Clone/Navigate to the project:**
    ```bash
    cd pid-orchestrator
    ```

2.  **Install dependencies:**
    ```bash
    pip install streamlit google-adk google-genai python-dotenv
    ```

3.  **Setup Environment:**
    Create a `.env` file (optional, or use the UI sidebar):
    ```text
    GOOGLE_CLOUD_PROJECT="your-project-id"
    GOOGLE_CLOUD_LOCATION="us-central1"
    ```

4.  **Add Assets:**
    Ensure you have a folder named `assets/` in the root directory containing:
    * `pid_sample_1.pdf` (The diagram to analyze)
    * `learning_course.pdf` (The manual to teach from)
    * `architecture.png`, `overseer.png`, `analyst.png`, `instructor.png` (UI Images)

5.  **Run the App:**
    ```bash
    streamlit run app.py
    ```

## 🧠 Key Features in Code

### 1. "Thinking" Models
We utilize Gemini's thinking capability to improve routing accuracy. You can see this in `agents.py`:
```python
planner=BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        include_thoughts=True,
        thinking_budget=16000, # Allocates token budget for reasoning
    )
)