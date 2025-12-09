# 🏭 Gemini P&ID Multi-Agent

> **An Agentic Workflow for Engineering Document Analysis**
> This demo showcases how to use the Google Agent Developer Kit (ADK) to build a hierarchical AI system where specialized "Thinking" agents analyze engineering diagrams and teach users about them.

## 🎯 The Mission
Processing P&IDs (Piping and Instrumentation Diagrams) requires two distinct skill sets:
1.  **Visual Analysis:** Tracing lines, reading tags, and understanding connectivity.
2.  **Domain Knowledge:** Understanding symbols, standards, and engineering rules.

This application uses an **Orchestrator Pattern**. A central "Overseer" routes requests to specialized agents—the "Analyst" (for diagrams) and "Instructor" (for manuals)—who utilize **Gemini's Thinking process** to reason through complex tasks.

## 🏗 The Architecture

This project uses **Google ADK** to manage state, artifacts, and routing.

* **The Overseer (Gemini 3 Pro):** The router. It identifies user intent and delegates the conversation to the correct sub-agent.
* **The Analyst (Thinking Enabled):** A specialist equipped with `pid_sample_1.pdf`. It uses a 16k token thinking budget to carefully trace process lines and identify components.
* **The Instructor (Thinking Enabled):** A specialist equipped with `learning_course.pdf`. It uses a 16k token thinking budget to formulate educational explanations based strictly on the provided text.

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* A Google Cloud Project with Vertex AI API enabled.

### Installation

1.  **Clone/Navigate to the project:**
    ```bash
    cd pid-orchestrator
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Environment:**
    [cite_start]Create a `.env` file based on the provided template[cite: 1]:
    ```text
    GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
    GOOGLE_CLOUD_LOCATION="us-central1"
    GOOGLE_GENAI_USE_VERTEXAI="TRUE"
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

### 1. "Thinking" Specialists
We utilize Gemini's thinking capability for the sub-agents to improve accuracy on visual and educational tasks. You can see this in `agents.py`:
```python
planner=BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        include_thoughts=True,
        thinking_budget=16000, # Allocates token budget for reasoning
    )
)